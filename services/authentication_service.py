from database.models import db, User
from utils.security import hash_password, check_password
from flask_jwt_extended import create_access_token, create_refresh_token
import re
import secrets
from datetime import datetime, timedelta


class AuthenticationService:
    """Handles user registration, login, and token management."""

    @staticmethod
    def register(email, password, first_name, last_name, role='student'):
        """Register a new user."""
        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return None, 'Invalid email format.'

        # Check password strength
        if len(password) < 8:
            return None, 'Password must be at least 8 characters.'

        # Check if user exists
        if User.query.filter_by(email=email).first():
            return None, 'Email already registered.'

        # Validate role
        if role not in ('admin', 'lecturer', 'student'):
            return None, 'Invalid role.'

        verification_token = secrets.token_urlsafe(48)
        user = User(
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
            email_verified=False,
            email_verification_token=verification_token,
            email_verification_token_expires=datetime.utcnow() + timedelta(hours=24),
        )
        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def login(email, password):
        """Authenticate user and return tokens."""
        user_row = db.session.query(
            User.id,
            User.email,
            User.password_hash,
            User.first_name,
            User.last_name,
            User.role,
            User.department,
            User.profile_image,
            User.phone_number,
            User.bio,
            User.is_active,
            User.share_contact,
            User.created_at,
            User.email_verified,
            User.face_encoding.isnot(None).label('face_registered'),
        ).filter(
            User.email == email,
            User.is_active == True,
        ).first()

        if not user_row or not check_password(password, user_row.password_hash):
            return None, 'Invalid email or password.'

        if not user_row.email_verified:
            return None, 'EMAIL_NOT_VERIFIED'

        profile_steps = [
            bool(user_row.profile_image),
            bool(user_row.phone_number),
            bool(user_row.bio),
            bool(user_row.face_registered),
        ]
        profile_complete = int(sum(profile_steps) / len(profile_steps) * 100)

        user_payload = {
            'id': user_row.id,
            'email': user_row.email,
            'first_name': user_row.first_name,
            'last_name': user_row.last_name,
            'role': user_row.role,
            'department': user_row.department,
            'profile_image': user_row.profile_image,
            'phone_number': user_row.phone_number,
            'bio': user_row.bio,
            'is_active': user_row.is_active,
            'email_verified': bool(user_row.email_verified),
            'share_contact': user_row.share_contact,
            'profile_complete': profile_complete,
            'face_registered': bool(user_row.face_registered),
            'created_at': user_row.created_at.isoformat() if user_row.created_at else None,
        }

        claims = {'email': user_row.email, 'role': user_row.role}
        access_token = create_access_token(identity=str(user_row.id), additional_claims=claims)
        refresh_token = create_refresh_token(identity=str(user_row.id), additional_claims=claims)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user_payload,
        }, None

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID."""
        return User.query.get(user_id)

    @staticmethod
    def update_profile(user_id, **kwargs):
        """Update user profile fields."""
        user = User.query.get(user_id)
        if not user:
            return None, 'User not found.'

        allowed = ['first_name', 'last_name', 'profile_image', 'phone_number', 'bio', 'share_contact']
        for key, value in kwargs.items():
            if key in allowed and value is not None:
                setattr(user, key, value)

        # Department can only be set once by the student; after that only admin can change it
        if 'department' in kwargs and kwargs['department'] and not user.department:
            user.department = kwargs['department']

        db.session.commit()
        return user, None

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Change user password."""
        user = User.query.get(user_id)
        if not user:
            return False, 'User not found.'
        if not check_password(old_password, user.password_hash):
            return False, 'Current password is incorrect.'
        if len(new_password) < 8:
            return False, 'New password must be at least 8 characters.'

        user.password_hash = hash_password(new_password)
        db.session.commit()
        return True, None

    @staticmethod
    def verify_email(token: str):
        """Mark a user's email as verified using the verification token."""
        user = User.query.filter_by(email_verification_token=token).first()
        if not user:
            return None, 'Invalid verification link.'
        if user.email_verified:
            return user, 'already_verified'
        if user.email_verification_token_expires and \
                user.email_verification_token_expires < datetime.utcnow():
            return None, 'Verification link has expired. Please request a new one.'

        user.email_verified = True
        user.email_verification_token = None
        user.email_verification_token_expires = None
        db.session.commit()
        return user, 'verified'

    @staticmethod
    def regenerate_verification_token(email: str):
        """Issue a fresh verification token for an unverified account."""
        user = User.query.filter_by(email=email).first()
        if not user:
            return None, 'No account found with that email.'
        if user.email_verified:
            return None, 'This account is already verified.'

        token = secrets.token_urlsafe(48)
        user.email_verification_token = token
        user.email_verification_token_expires = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
        return user, token
