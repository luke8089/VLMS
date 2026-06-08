
import os
import base64
from flask import Blueprint, request, jsonify, render_template, current_app, redirect
from flask_jwt_extended import jwt_required
from database.models import db, Exam, Submission, Violation, Question, Answer
from utils.security import role_required, get_identity
from datetime import datetime

exam_bp = Blueprint('exam', __name__)

# ──────────────── FACE VERIFICATION PAGE ────────────────

@exam_bp.route('/exam/<int:exam_id>/verify-face')
@jwt_required()
@role_required('student')
def face_verification_page(exam_id):
    """Pre-exam face verification page."""
    from database.models import Exam, Submission
    identity = get_identity()
    exam = Exam.query.get_or_404(exam_id)
    # Get or create submission for this exam
    submission = Submission.query.filter_by(
        exam_id=exam_id,
        student_id=identity['id']
    ).first()
    if not submission:
        submission = Submission(
            exam_id=exam_id,
            student_id=identity['id'],
            status='in_progress'
        )
        db.session.add(submission)
        db.session.commit()
    # If already verified, redirect to exam
    if submission.face_verified:
        return redirect(f'/exam/{exam_id}?submission={submission.id}')
    return render_template('face_verification.html', exam=exam, submission=submission, submission_id=submission.id)


# ──────────────── FACE VERIFICATION PAGE ────────────────



# ──────────────── EXAM INTERFACE PAGE ────────────────

@exam_bp.route('/exam/<int:exam_id>')
@jwt_required()
@role_required('student')
def exam_interface(exam_id):
    from database.models import Exam, Submission

    identity = get_identity()

    # Get or create submission
    submission = Submission.query.filter_by(
        exam_id=exam_id,
        student_id=identity['id']
    ).order_by(Submission.id.desc()).first()

    if not submission:
        submission = Submission(
            exam_id=exam_id,
            student_id=identity['id'],
            status='in_progress'
        )
        db.session.add(submission)
        db.session.commit()

    return render_template('exam_interface.html', exam_id=exam_id, submission=submission)


# ──────────────── PROCTORING ENDPOINTS ────────────────

@exam_bp.route('/api/exam/<int:submission_id>/face-verify', methods=['POST'])
@jwt_required()
@role_required('student')
def face_verify(submission_id):
    """Verify student face before starting exam."""
    identity = get_identity()
    submission = Submission.query.get(submission_id)

    if not submission or submission.student_id != identity['id']:
        return jsonify({'error': 'Submission not found'}), 404

    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({'error': 'No image provided'}), 400

    try:
        from ai_modules.exam_proctoring.face_auth import FaceAuthenticator
        authenticator = FaceAuthenticator()
        result = authenticator.verify_face(identity['id'], image_data)
        is_verified = result.get('verified', False)
    except Exception as e:
        current_app.logger.error(f"Face verification error: {e}")
        return jsonify({'error': 'Face verification system error'}), 500

    if is_verified:
        submission.face_verified = True
        submission.face_verified_at = datetime.utcnow()
        db.session.commit()

    return jsonify({
        'verified': is_verified,
        'message': 'Face verified successfully' if is_verified else 'Face verification failed'
    })


@exam_bp.route('/api/exam/<int:submission_id>/face-verify-enhanced', methods=['POST'])
@jwt_required()
@role_required('student')
def face_verify_enhanced(submission_id):
    """
    Enhanced face verification with liveness detection.
    Required before starting proctored exams.
    """
    identity = get_identity()
    submission = Submission.query.get(submission_id)

    if not submission or submission.student_id != identity['id']:
        return jsonify({'error': 'Submission not found'}), 404
    
    exam = Exam.query.get(submission.exam_id)
    if not exam:
        return jsonify({'error': 'Exam not found'}), 404

    data = request.get_json()
    image_data = data.get('image')
    previous_frames = data.get('previous_frames', [])

    if not image_data:
        return jsonify({'error': 'No image provided'}), 400

    # Check if user has face registered
    from database.models import User
    user = User.query.get(identity['id'])
    if not user or not user.face_encoding:
        return jsonify({
            'verified': False,
            'message': 'No face registered. Please register your face first.',
            'needs_registration': True
        }), 400

    try:
        from ai_modules.exam_proctoring.face_auth import FaceAuthenticator
        authenticator = FaceAuthenticator()
        
        result = authenticator.verify_face(
            identity['id'], 
            image_data,
            exam_id=submission.exam_id,
            submission_id=submission_id,
            previous_frames=previous_frames
        )
        
        if result['verified']:
            submission.face_verified = True
            submission.face_verified_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Face verification error: {e}")
        return jsonify({
            'verified': False,
            'message': 'Verification system error. Please try again.'
        }), 500


@exam_bp.route('/api/exam/<int:submission_id>/proctor-frame', methods=['POST'])
@jwt_required()
@role_required('student')
def process_proctor_frame(submission_id):
    """Process a webcam frame for proctoring analysis."""
    identity = get_identity()
    submission = Submission.query.get(submission_id)

    if not submission or submission.student_id != identity['id']:
        return jsonify({'error': 'Submission not found'}), 404
    if submission.status != 'in_progress':
        return jsonify({'error': 'Exam not in progress'}), 400

    data = request.get_json()
    image_data = data.get('image')  # Base64 encoded frame

    if not image_data:
        return jsonify({'error': 'No image provided'}), 400

    violations = []
    try:
        from ai_modules.exam_proctoring.risk_scoring import RiskScorer
        scorer = RiskScorer()
        violations = scorer.analyze_frame(image_data)
    except ImportError:
        pass

    # Record violations
    created_violations = []
    for v in violations:
        severity = v.get('severity', 5)
        screenshot = _save_screenshot(image_data, 'v', submission_id, current_app) if severity >= 20 else None
        violation = Violation(
            submission_id=submission_id,
            violation_type=v['type'],
            severity=severity,
            description=v.get('description', ''),
            screenshot_path=screenshot,
        )
        db.session.add(violation)
        submission.risk_score = (submission.risk_score or 0) + severity
        created_violations.append({'vobj': violation, 'type': v.get('type'), 'severity': severity})

    # Check threshold
    exam = Exam.query.get(submission.exam_id)
    if (submission.risk_score or 0) >= (exam.risk_threshold or 100):
        submission.is_flagged = True

    db.session.commit()

    violations_payload = [
        {'id': item['vobj'].id, 'type': item['type'], 'severity': item['severity']}
        for item in created_violations
    ]

    return jsonify({
        'risk_score': submission.risk_score,
        'is_flagged': submission.is_flagged,
        'violations': violations_payload,
    })


@exam_bp.route('/api/exam/<int:submission_id>/face-identity-check', methods=['POST'])
@jwt_required()
@role_required('student')
def face_identity_check(submission_id):
    """Periodic face identity check during exam — compares live frame to registered encoding."""
    identity = get_identity()
    submission = Submission.query.get(submission_id)

    if not submission or submission.student_id != identity['id']:
        return jsonify({'error': 'Submission not found'}), 404
    if submission.status != 'in_progress':
        return jsonify({'error': 'Exam not in progress'}), 400

    data = request.get_json()
    image_data = data.get('image')
    if not image_data:
        return jsonify({'error': 'No image provided'}), 400

    try:
        from ai_modules.exam_proctoring.face_auth import FaceAuthenticator
        from database.models import User
        authenticator = FaceAuthenticator()

        user = User.query.get(identity['id'])
        if not user or not user.face_encoding:
            # No face registered — skip silently
            return jsonify({'verified': True, 'skipped': True, 'reason': 'no_registration'})

        result = authenticator.verify_face(
            user_id=identity['id'],
            base64_image=image_data,
            exam_id=submission.exam_id,
            submission_id=submission_id,
        )

        confidence = result.get('confidence', 0.0)
        verified   = result.get('verified', False)
        match_pct  = round(confidence * 100)
        mismatch_pct = 100 - match_pct

        if not verified:
            severity = 45
            description = (
                f"Face identity mismatch detected during exam. "
                f"Match confidence: {match_pct}% — Mismatch: {mismatch_pct}%. "
                f"The person in front of the camera does not match the registered student."
            )

            violation = Violation(
                submission_id=submission_id,
                violation_type='face_mismatch',
                severity=severity,
                description=description,
            )

            # Always save a screenshot for face mismatches
            try:
                screenshot_dir = current_app.config.get('SCREENSHOT_FOLDER', 'screenshots')
                os.makedirs(screenshot_dir, exist_ok=True)
                filename = f"facemismatch_{submission_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
                filepath = os.path.join(screenshot_dir, filename)
                img_bytes = base64.b64decode(image_data.split(',')[-1])
                with open(filepath, 'wb') as f:
                    f.write(img_bytes)
                violation.screenshot_path = filename
            except Exception:
                pass

            db.session.add(violation)
            submission.risk_score = (submission.risk_score or 0) + severity

            exam = Exam.query.get(submission.exam_id)
            if submission.risk_score >= (exam.risk_threshold or 100):
                submission.is_flagged = True

            db.session.commit()

            return jsonify({
                'verified': False,
                'match_pct': match_pct,
                'mismatch_pct': mismatch_pct,
                'risk_score': submission.risk_score,
                'is_flagged': submission.is_flagged,
                'violation_id': violation.id,
            })

        return jsonify({
            'verified': True,
            'match_pct': match_pct,
            'mismatch_pct': mismatch_pct,
            'risk_score': submission.risk_score,
            'is_flagged': submission.is_flagged,
        })

    except Exception as e:
        current_app.logger.error(f'Face identity check error: {e}')
        return jsonify({'verified': True, 'skipped': True, 'reason': 'system_error'})


@exam_bp.route('/api/exam/violations/<int:violation_id>/clip', methods=['POST'])
@jwt_required()
@role_required('student')
def upload_violation_clip(violation_id):
    identity = get_identity()
    violation = Violation.query.get(violation_id)
    if not violation:
        return jsonify({'error': 'Violation not found'}), 404

    submission = Submission.query.get(violation.submission_id)
    if not submission or submission.student_id != identity['id']:
        return jsonify({'error': 'Unauthorized'}), 403

    clip = request.files.get('clip')
    if not clip:
        return jsonify({'error': 'No clip uploaded'}), 400

    recording_dir = current_app.config.get('RECORDING_FOLDER', 'recordings')
    os.makedirs(recording_dir, exist_ok=True)
    ext = os.path.splitext(clip.filename or '')[1].lower() or '.webm'
    filename = f"clip_{violation_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{ext}"
    filepath = os.path.join(recording_dir, filename)
    clip.save(filepath)

    violation.video_path = filename
    violation.video_format = (clip.mimetype or 'video/webm')
    violation.video_duration = request.form.get('duration', type=float)
    db.session.commit()

    return jsonify({'message': 'Clip uploaded', 'video_path': filename})


@exam_bp.route('/api/exam/<int:submission_id>/tab-switch', methods=['POST'])
@jwt_required()
@role_required('student')
def record_tab_switch(submission_id):
    """Record a tab switch violation."""
    identity = get_identity()
    submission = Submission.query.get(submission_id)

    if not submission or submission.student_id != identity['id']:
        return jsonify({'error': 'Submission not found'}), 404

    violation = Violation(
        submission_id=submission_id,
        violation_type='tab_switch',
        severity=10,
        description='Student switched browser tab/window',
    )
    db.session.add(violation)
    submission.risk_score = (submission.risk_score or 0) + 10

    exam = Exam.query.get(submission.exam_id)
    if (submission.risk_score or 0) >= (exam.risk_threshold or 100):
        submission.is_flagged = True

    db.session.commit()
    return jsonify({'risk_score': submission.risk_score, 'is_flagged': submission.is_flagged})


@exam_bp.route('/api/exam/<int:submission_id>/copy-attempt', methods=['POST'])
@jwt_required()
@role_required('student')
def record_copy_attempt(submission_id):
    identity = get_identity()
    submission = Submission.query.get(submission_id)

    if not submission or submission.student_id != identity['id']:
        return jsonify({'error': 'Submission not found'}), 404

    violation = Violation(
        submission_id=submission_id,
        violation_type='other',
        severity=5,
        description='Student attempted to copy or cut exam content',
    )
    db.session.add(violation)
    submission.risk_score = (submission.risk_score or 0) + 5

    exam = Exam.query.get(submission.exam_id)
    if (submission.risk_score or 0) >= (exam.risk_threshold or 100):
        submission.is_flagged = True

    db.session.commit()
    return jsonify({'risk_score': submission.risk_score, 'is_flagged': submission.is_flagged})


# ──────────────── ENHANCED PROCTORING ENDPOINTS ────────────────

def _save_screenshot(image_data, prefix, submission_id, app):
    """Save a base64 image and return the filename, or None on failure."""
    try:
        screenshot_dir = app.config.get('SCREENSHOT_FOLDER', 'screenshots')
        os.makedirs(screenshot_dir, exist_ok=True)
        filename = f"{prefix}_{submission_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(screenshot_dir, filename)
        img_bytes = base64.b64decode(image_data.split(',')[-1])
        with open(filepath, 'wb') as f:
            f.write(img_bytes)
        return filename
    except Exception:
        return None


def _record_violation(submission, violation_type, severity, description, screenshot_filename=None):
    """Create a Violation record and bump the submission risk score."""
    violation = Violation(
        submission_id=submission.id,
        violation_type=violation_type,
        severity=severity,
        description=description,
        screenshot_path=screenshot_filename,
    )
    db.session.add(violation)
    submission.risk_score = (submission.risk_score or 0) + severity
    exam = Exam.query.get(submission.exam_id)
    if submission.risk_score >= (exam.risk_threshold or 100):
        submission.is_flagged = True
    return violation


@exam_bp.route('/api/exam/<int:submission_id>/fullscreen-exit', methods=['POST'])
@jwt_required()
@role_required('student')
def record_fullscreen_exit(submission_id):
    """Record when a student exits fullscreen during the exam."""
    identity = get_identity()
    submission = Submission.query.get(submission_id)
    if not submission or submission.student_id != identity['id']:
        return jsonify({'error': 'Submission not found'}), 404
    if submission.status != 'in_progress':
        return jsonify({'error': 'Exam not in progress'}), 400

    data = request.get_json(silent=True) or {}
    image_data = data.get('image')
    screenshot = _save_screenshot(image_data, 'fs', submission_id, current_app) if image_data else None

    violation = _record_violation(
        submission, 'fullscreen_exit', 15,
        'Student exited fullscreen mode during exam',
        screenshot,
    )
    db.session.commit()
    return jsonify({'risk_score': submission.risk_score, 'is_flagged': submission.is_flagged,
                    'violation_id': violation.id})


@exam_bp.route('/api/exam/<int:submission_id>/noise-detected', methods=['POST'])
@jwt_required()
@role_required('student')
def record_noise(submission_id):
    """Record a noise / voice detection event during the exam."""
    identity = get_identity()
    submission = Submission.query.get(submission_id)
    if not submission or submission.student_id != identity['id']:
        return jsonify({'error': 'Submission not found'}), 404
    if submission.status != 'in_progress':
        return jsonify({'error': 'Exam not in progress'}), 400

    data = request.get_json(silent=True) or {}
    noise_level = data.get('noise_level', 0)

    # No screenshot saved here — the client uploads an audio+video clip via
    # POST /api/exam/violations/<violation_id>/clip immediately after this call.
    violation = _record_violation(
        submission, 'noise_detected', 10,
        f'Noise/voice detected during exam (audio level: {noise_level})',
    )
    db.session.commit()
    return jsonify({'risk_score': submission.risk_score, 'is_flagged': submission.is_flagged,
                    'violation_id': violation.id})


@exam_bp.route('/api/exam/<int:submission_id>/window-blur', methods=['POST'])
@jwt_required()
@role_required('student')
def record_window_blur(submission_id):
    """Record when the exam window loses focus (student switched away)."""
    identity = get_identity()
    submission = Submission.query.get(submission_id)
    if not submission or submission.student_id != identity['id']:
        return jsonify({'error': 'Submission not found'}), 404
    if submission.status != 'in_progress':
        return jsonify({'error': 'Exam not in progress'}), 400

    data = request.get_json(silent=True) or {}
    image_data = data.get('image')
    blur_type = data.get('type', 'window_blur')
    screenshot = _save_screenshot(image_data, 'blur', submission_id, current_app) if image_data else None

    violation = _record_violation(
        submission, 'window_blur', 10,
        f'Exam window lost focus ({blur_type})',
        screenshot,
    )
    db.session.commit()
    return jsonify({'risk_score': submission.risk_score, 'is_flagged': submission.is_flagged,
                    'violation_id': violation.id})


@exam_bp.route('/api/exam/<int:submission_id>/keyboard-shortcut', methods=['POST'])
@jwt_required()
@role_required('student')
def record_keyboard_shortcut(submission_id):
    """Record a suspicious keyboard shortcut used during the exam."""
    identity = get_identity()
    submission = Submission.query.get(submission_id)
    if not submission or submission.student_id != identity['id']:
        return jsonify({'error': 'Submission not found'}), 404
    if submission.status != 'in_progress':
        return jsonify({'error': 'Exam not in progress'}), 400

    data = request.get_json(silent=True) or {}
    key = data.get('key', 'unknown')
    combo = ' + '.join(filter(None, [
        'Ctrl' if data.get('ctrl') else '',
        'Alt' if data.get('alt') else '',
        'Meta' if data.get('meta') else '',
        key,
    ]))

    violation = _record_violation(
        submission, 'keyboard_shortcut', 8,
        f'Suspicious keyboard shortcut detected: {combo}',
    )
    db.session.commit()
    return jsonify({'risk_score': submission.risk_score, 'is_flagged': submission.is_flagged,
                    'violation_id': violation.id})


@exam_bp.route('/api/exam/<int:submission_id>/periodic-screenshot', methods=['POST'])
@jwt_required()
@role_required('student')
def save_periodic_screenshot(submission_id):
    """Save a periodic proctoring screenshot (no violation, evidence only)."""
    identity = get_identity()
    submission = Submission.query.get(submission_id)
    if not submission or submission.student_id != identity['id']:
        return jsonify({'error': 'Submission not found'}), 404
    if submission.status != 'in_progress':
        return jsonify({'error': 'Exam not in progress'}), 400

    data = request.get_json(silent=True) or {}
    image_data = data.get('image')
    if not image_data:
        return jsonify({'error': 'No image provided'}), 400

    filename = _save_screenshot(image_data, 'snap', submission_id, current_app)
    return jsonify({'saved': bool(filename), 'filename': filename})


# ──────────────── VIOLATION REPORTS ────────────────

@exam_bp.route('/api/exam/<int:submission_id>/violations', methods=['GET'])
@jwt_required()
def get_violations(submission_id):
    identity = get_identity()
    submission = Submission.query.get(submission_id)
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    # Only the student themselves or lecturers/admins can view
    if identity['role'] == 'student' and submission.student_id != identity['id']:
        return jsonify({'error': 'Unauthorized'}), 403

    violations = Violation.query.filter_by(submission_id=submission_id).order_by(Violation.timestamp).all()
    return jsonify({'violations': [v.to_dict() for v in violations]})
