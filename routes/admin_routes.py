from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required
from utils.security import role_required, get_identity
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/dashboard')
@jwt_required()
@role_required('admin')
def dashboard():
    active_page = request.args.get('view', 'overview')
    return render_template('admin_panel.html', admin_active_page=active_page)


# ──────────────── ADMIN OVERVIEW ────────────────

@admin_bp.route('/api/admin/overview', methods=['GET'])
@jwt_required()
@role_required('admin')
def admin_overview():
    from database.models import User, Course, Exam, Submission, Violation, Enrollment, FaceVerificationLog, db
    from sqlalchemy import func

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_students = User.query.filter_by(role='student').count()
    total_lecturers = User.query.filter_by(role='lecturer').count()
    total_courses = Course.query.count()
    total_exams = Exam.query.count()
    total_submissions = Submission.query.count()
    total_enrollments = Enrollment.query.count()
    flagged_submissions = Submission.query.filter_by(is_flagged=True).count()

    # Active exams: currently within window
    active_exams = Exam.query.filter(
        Exam.is_published == True,
        Exam.start_time <= now,
        Exam.end_time >= now
    ).count()

    # Flags today: violations recorded today
    flags_today = Violation.query.filter(Violation.timestamp >= today_start).count()

    # Avg risk score across all submissions
    avg_risk = db.session.query(func.avg(Submission.risk_score)).scalar()
    avg_risk_score = round(float(avg_risk), 1) if avg_risk else 0

    # Face registration
    face_registered = User.query.filter(
        User.role == 'student',
        User.face_encoding.isnot(None)
    ).count()

    # New users last 7 days
    week_ago = now - timedelta(days=7)
    new_users_week = User.query.filter(User.created_at >= week_ago).count()

    # AI response time
    from ai_modules.ollama_service import get_avg_response_time
    avg_ai_response = get_avg_response_time()

    return jsonify({
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'total_courses': total_courses,
        'total_exams': total_exams,
        'total_submissions': total_submissions,
        'total_enrollments': total_enrollments,
        'flagged_submissions': flagged_submissions,
        'active_exams': active_exams,
        'flags_today': flags_today,
        'avg_risk_score': avg_risk_score,
        'face_registered': face_registered,
        'new_users_week': new_users_week,
        'avg_ai_response': avg_ai_response,
    })


# ──────────────── USERS MANAGEMENT ────────────────

@admin_bp.route('/api/admin/users', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_users():
    from database.models import User, Enrollment, db

    role_filter = request.args.get('role', 'all')
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    query = User.query
    if role_filter != 'all':
        query = query.filter_by(role=role_filter)
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    if search:
        query = query.filter(
            db.or_(
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%'),
                User.department.ilike(f'%{search}%')
            )
        )

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = []
    for u in users:
        enrollment_count = Enrollment.query.filter_by(student_id=u.id).count() if u.role == 'student' else 0
        result.append({
            **u.to_dict(),
            'enrollment_count': enrollment_count,
        })

    return jsonify({'users': result, 'total': total, 'page': page, 'per_page': per_page})


@admin_bp.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_user(user_id):
    from database.models import User, db

    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    if 'first_name' in data:
        user.first_name = data['first_name'].strip()
    if 'last_name' in data:
        user.last_name = data['last_name'].strip()
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])
    if 'role' in data and data['role'] in ('admin', 'lecturer', 'student'):
        user.role = data['role']
    if 'department' in data:
        user.department = data['department'].strip() if data['department'] else None

    db.session.commit()
    return jsonify({'message': 'User updated', 'user': user.to_dict()})


@admin_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_user(user_id):
    from database.models import User, db

    identity = get_identity()
    if identity['id'] == user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})


# ──────────────── COURSES MANAGEMENT ────────────────

@admin_bp.route('/api/admin/courses', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_courses():
    from database.models import Course, User, Enrollment, Exam, db

    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all')

    query = Course.query
    if status_filter == 'published':
        query = query.filter_by(is_published=True)
    elif status_filter == 'unpublished':
        query = query.filter_by(is_published=False)
    if search:
        query = query.filter(
            db.or_(
                Course.title.ilike(f'%{search}%'),
                Course.code.ilike(f'%{search}%'),
                Course.category.ilike(f'%{search}%')
            )
        )

    courses = query.order_by(Course.created_at.desc()).all()
    result = []
    for c in courses:
        lecturer = User.query.get(c.lecturer_id)
        enrollment_count = Enrollment.query.filter_by(course_id=c.id).count()
        exam_count = Exam.query.filter_by(course_id=c.id).count()
        result.append({
            **c.to_dict(),
            'lecturer_name': f"{lecturer.first_name} {lecturer.last_name}" if lecturer else 'Unknown',
            'enrollment_count': enrollment_count,
            'exam_count': exam_count,
        })

    return jsonify({'courses': result, 'total': len(result)})


@admin_bp.route('/api/admin/courses/<int:course_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_course(course_id):
    from database.models import Course, db

    course = Course.query.get_or_404(course_id)
    data = request.get_json() or {}

    if 'is_published' in data:
        course.is_published = bool(data['is_published'])

    db.session.commit()
    return jsonify({'message': 'Course updated', 'course': course.to_dict()})


@admin_bp.route('/api/admin/courses/<int:course_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_course(course_id):
    from database.models import Course, db

    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return jsonify({'message': 'Course deleted'})


# ──────────────── EXAMS OVERVIEW ────────────────

@admin_bp.route('/api/admin/exams', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_exams():
    from database.models import Exam, Course, User, Submission, Violation, db

    search = request.args.get('search', '').strip()
    query = Exam.query
    if search:
        query = query.filter(Exam.title.ilike(f'%{search}%'))

    exams = query.order_by(Exam.created_at.desc()).all()
    now = datetime.utcnow()
    result = []

    for e in exams:
        course = Course.query.get(e.course_id)
        lecturer = User.query.get(course.lecturer_id) if course else None
        sub_count = Submission.query.filter_by(exam_id=e.id).count()
        flagged_count = Submission.query.filter_by(exam_id=e.id, is_flagged=True).count()
        viol_count = Violation.query.join(Submission).filter(Submission.exam_id == e.id).count()

        if e.start_time and e.end_time:
            if now < e.start_time:
                exam_status = 'upcoming'
            elif e.start_time <= now <= e.end_time:
                exam_status = 'active'
            else:
                exam_status = 'ended'
        else:
            exam_status = 'draft'

        result.append({
            **e.to_dict(),
            'course_title': course.title if course else 'Unknown',
            'course_code': course.code if course else '',
            'lecturer_name': f"{lecturer.first_name} {lecturer.last_name}" if lecturer else 'Unknown',
            'submission_count': sub_count,
            'flagged_count': flagged_count,
            'violation_count': viol_count,
            'exam_status': exam_status,
        })

    return jsonify({'exams': result, 'total': len(result)})


# ──────────────── EXAMS MANAGEMENT ────────────────

@admin_bp.route('/api/admin/exams/<int:exam_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_exam(exam_id):
    from database.models import Exam, db
    exam = Exam.query.get_or_404(exam_id)
    db.session.delete(exam)
    db.session.commit()
    return jsonify({'message': 'Exam deleted'})


@admin_bp.route('/api/admin/exams/<int:exam_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_exam_detail(exam_id):
    from database.models import Exam, Course, User, Submission, Violation, Answer, Question, db
    from sqlalchemy import func

    exam = Exam.query.get_or_404(exam_id)
    course = Course.query.get(exam.course_id)
    lecturer = User.query.get(course.lecturer_id) if course else None

    submissions = Submission.query.filter_by(exam_id=exam_id).all()
    sub_list = []
    for s in submissions:
        student = User.query.get(s.student_id)
        viol_count = Violation.query.filter_by(submission_id=s.id).count()
        sub_list.append({
            **s.to_dict(),
            'student_name': f"{student.first_name} {student.last_name}" if student else 'Unknown',
            'student_email': student.email if student else '',
            'violation_count': viol_count,
        })

    question_count = Question.query.filter_by(exam_id=exam_id).count()
    flagged_count = sum(1 for s in sub_list if s['is_flagged'])
    avg_score = None
    graded = [s['total_score'] for s in sub_list if s['total_score'] is not None]
    if graded:
        avg_score = round(sum(graded) / len(graded), 1)

    now = datetime.utcnow()
    if exam.start_time and exam.end_time:
        if now < exam.start_time:
            status = 'upcoming'
        elif exam.start_time <= now <= exam.end_time:
            status = 'active'
        else:
            status = 'ended'
    else:
        status = 'draft'

    return jsonify({
        **exam.to_dict(),
        'course_title': course.title if course else 'Unknown',
        'course_code': course.code if course else '',
        'lecturer_name': f"{lecturer.first_name} {lecturer.last_name}" if lecturer else 'Unknown',
        'question_count': question_count,
        'submission_count': len(sub_list),
        'flagged_count': flagged_count,
        'avg_score': avg_score,
        'exam_status': status,
        'submissions': sub_list,
    })


# ──────────────── COURSES DETAIL ────────────────

@admin_bp.route('/api/admin/courses/<int:course_id>/detail', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_course_detail(course_id):
    from database.models import Course, User, Enrollment, Exam, db

    course = Course.query.get_or_404(course_id)
    lecturer = User.query.get(course.lecturer_id)
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    exams = Exam.query.filter_by(course_id=course_id).all()

    enrolled_students = []
    for e in enrollments:
        student = User.query.get(e.student_id)
        if student:
            enrolled_students.append({
                'id': student.id,
                'name': f"{student.first_name} {student.last_name}",
                'email': student.email,
                'department': student.department,
                'enrolled_at': e.enrolled_at.isoformat() if e.enrolled_at else None,
                'progress': e.progress,
                'status': e.status,
            })

    return jsonify({
        **course.to_dict(),
        'lecturer_name': f"{lecturer.first_name} {lecturer.last_name}" if lecturer else 'Unknown',
        'lecturer_email': lecturer.email if lecturer else '',
        'enrollment_count': len(enrollments),
        'exam_count': len(exams),
        'enrolled_students': enrolled_students,
        'exams': [e.to_dict() for e in exams],
    })


# ──────────────── SYSTEM HEALTH ────────────────

@admin_bp.route('/api/admin/system', methods=['GET'])
@jwt_required()
@role_required('admin')
def system_health():
    from database.models import (User, Course, Exam, Submission, Violation,
                                  Enrollment, Material, LearningProgress,
                                  FaceVerificationLog, LiveClass, db)
    import sys
    import platform
    import os
    import flask

    def _folder_size_mb(path):
        total = 0
        try:
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total += os.path.getsize(fp)
        except Exception:
            pass
        return round(total / (1024 * 1024), 2)

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uploads_mb     = _folder_size_mb(os.path.join(base, 'uploads'))
    screenshots_mb = _folder_size_mb(os.path.join(base, 'screenshots'))
    recordings_mb  = _folder_size_mb(os.path.join(base, 'recordings'))

    table_counts = {
        'users':            User.query.count(),
        'courses':          Course.query.count(),
        'exams':            Exam.query.count(),
        'submissions':      Submission.query.count(),
        'violations':       Violation.query.count(),
        'enrollments':      Enrollment.query.count(),
        'materials':        Material.query.count(),
        'learning_progress':LearningProgress.query.count(),
        'face_logs':        FaceVerificationLog.query.count(),
        'live_classes':     LiveClass.query.count(),
    }

    total_records = sum(table_counts.values())

    # Role breakdown
    students  = User.query.filter_by(role='student').count()
    lecturers = User.query.filter_by(role='lecturer').count()
    admins    = User.query.filter_by(role='admin').count()

    # Exam health
    now = datetime.utcnow()
    active_exams  = Exam.query.filter(Exam.is_published==True, Exam.start_time<=now, Exam.end_time>=now).count()
    flagged_subs  = Submission.query.filter_by(is_flagged=True).count()
    unverified    = User.query.filter_by(role='student', email_verified=False).count()

    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'table_counts': table_counts,
        'total_records': total_records,
        'python_version': sys.version.split(' ')[0],
        'flask_version': flask.__version__,
        'platform': platform.system() + ' ' + platform.release(),
        'server_time': datetime.utcnow().isoformat(),
        'storage': {
            'uploads_mb': uploads_mb,
            'screenshots_mb': screenshots_mb,
            'recordings_mb': recordings_mb,
            'total_mb': round(uploads_mb + screenshots_mb + recordings_mb, 2),
        },
        'user_breakdown': {
            'students': students,
            'lecturers': lecturers,
            'admins': admins,
        },
        'platform_health': {
            'active_exams': active_exams,
            'flagged_submissions': flagged_subs,
            'unverified_students': unverified,
        },
    })


# ──────────────── ANALYTICS PAGE ────────────────

@admin_bp.route('/admin/analytics')
@jwt_required()
@role_required('admin')
def analytics_page():
    return render_template('admin_analytics.html')


@admin_bp.route('/api/admin/analytics', methods=['GET'])
@jwt_required()
@role_required('admin')
def admin_analytics():
    from database.models import (User, Course, Exam, Submission, Violation,
                                  Enrollment, Material, LearningProgress, db)
    from sqlalchemy import func

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # ── Totals ──
    total_students  = User.query.filter_by(role='student').count()
    total_lecturers = User.query.filter_by(role='lecturer').count()
    total_admins    = User.query.filter_by(role='admin').count()
    total_courses   = Course.query.count()
    total_exams     = Exam.query.count()
    total_submissions = Submission.query.count()
    total_enrollments = Enrollment.query.count()
    total_materials   = Material.query.count()

    # ── Integrity ──
    flagged_submissions = Submission.query.filter_by(is_flagged=True).count()
    flags_today = Violation.query.filter(Violation.timestamp >= today_start).count()
    avg_risk = db.session.query(func.avg(Submission.risk_score)).scalar()
    avg_risk_score = round(float(avg_risk), 1) if avg_risk else 0
    face_registered = User.query.filter(
        User.role == 'student', User.face_encoding.isnot(None)
    ).count()

    # ── Growth: new users per day for last 30 days ──
    thirty_ago = now - timedelta(days=29)
    new_users_raw = db.session.query(
        func.date(User.created_at).label('day'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= thirty_ago).group_by(func.date(User.created_at)).all()
    new_users_by_day = {str(r.day): r.count for r in new_users_raw}

    # Fill all 30 days
    growth_series = []
    for i in range(29, -1, -1):
        d = (now - timedelta(days=i)).strftime('%Y-%m-%d')
        growth_series.append({'date': d, 'count': new_users_by_day.get(d, 0)})

    # ── Exam status breakdown ──
    active_exams   = Exam.query.filter(Exam.is_published==True, Exam.start_time<=now, Exam.end_time>=now).count()
    upcoming_exams = Exam.query.filter(Exam.is_published==True, Exam.start_time>now).count()
    ended_exams    = Exam.query.filter(Exam.end_time<now).count()
    draft_exams    = total_exams - active_exams - upcoming_exams - ended_exams

    # ── Top courses by enrollment ──
    top_courses_raw = db.session.query(
        Course.id, Course.title, Course.code,
        func.count(Enrollment.id).label('enrollments')
    ).outerjoin(Enrollment, Enrollment.course_id == Course.id
    ).group_by(Course.id).order_by(func.count(Enrollment.id).desc()).limit(8).all()

    top_courses = [{'id': r.id, 'title': r.title, 'code': r.code or '', 'enrollments': r.enrollments}
                   for r in top_courses_raw]
    max_enroll = max((c['enrollments'] for c in top_courses), default=1) or 1

    # ── Submission pass/fail ratio ──
    graded_subs = Submission.query.filter(Submission.total_score.isnot(None)).all()
    passed = sum(1 for s in graded_subs if s.total_score and s.total_score >= 50)
    failed = len(graded_subs) - passed

    # ── Recent violations ──
    recent_violations = Violation.query.order_by(Violation.timestamp.desc()).limit(10).all()
    violation_types = {}
    for v in Violation.query.all():
        t = v.violation_type or 'unknown'
        violation_types[t] = violation_types.get(t, 0) + 1

    # ── Submissions per exam type ──
    exam_type_stats = db.session.query(
        Exam.exam_type,
        func.count(Submission.id).label('submissions')
    ).outerjoin(Submission, Submission.exam_id == Exam.id
    ).group_by(Exam.exam_type).all()
    exam_type_breakdown = [{'type': r.exam_type or 'unknown', 'submissions': r.submissions}
                            for r in exam_type_stats]

    return jsonify({
        'totals': {
            'students': total_students,
            'lecturers': total_lecturers,
            'admins': total_admins,
            'courses': total_courses,
            'exams': total_exams,
            'submissions': total_submissions,
            'enrollments': total_enrollments,
            'materials': total_materials,
        },
        'integrity': {
            'flagged': flagged_submissions,
            'flags_today': flags_today,
            'avg_risk_score': avg_risk_score,
            'face_registered': face_registered,
            'face_rate': round(face_registered / total_students * 100, 1) if total_students else 0,
        },
        'growth_series': growth_series,
        'exam_status': {
            'active': active_exams,
            'upcoming': upcoming_exams,
            'ended': ended_exams,
            'draft': draft_exams,
        },
        'top_courses': top_courses,
        'max_enroll': max_enroll,
        'submission_outcomes': {'passed': passed, 'failed': failed, 'total': len(graded_subs)},
        'violation_types': violation_types,
        'exam_type_breakdown': exam_type_breakdown,
    })


# ──────────────── FACE VERIFICATION ADMIN ────────────────

@admin_bp.route('/admin/face-verification')
@jwt_required()
@role_required('admin')
def face_verification_admin():
    """Admin page for managing student face verification."""
    return render_template('admin_panel.html', admin_active_page='face_verification')


@admin_bp.route('/api/admin/face-verification/students', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_student_face_status():
    """Get list of students with their face verification status."""
    from database.models import User, Submission, db
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    department = request.args.get('department', None)
    search = request.args.get('search', '').strip().lower()
    
    # Base query
    query = User.query.filter_by(role='student')
    
    if department:
        query = query.filter_by(department=department)
    
    if search:
        query = query.filter(
            db.or_(
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )
    
    students = query.all()
    
    result = []
    for student in students:
        # Count exams and verified exams
        total_exams = Submission.query.filter_by(student_id=student.id).count()
        verified_exams = Submission.query.filter_by(
            student_id=student.id, 
            face_verified=True
        ).count()
        
        face_status = 'registered' if student.face_encoding else 'not_registered'
        
        # Apply status filter
        if status_filter != 'all' and face_status != status_filter:
            continue
        
        result.append({
            'id': student.id,
            'email': student.email,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'department': student.department,
            'face_status': face_status,
            'total_exams': total_exams,
            'verified_exams': verified_exams,
            'created_at': student.created_at.isoformat() if student.created_at else None
        })
    
    return jsonify({
        'students': result,
        'total': len(result),
        'registered': sum(1 for s in result if s['face_status'] == 'registered'),
        'not_registered': sum(1 for s in result if s['face_status'] == 'not_registered')
    })


@admin_bp.route('/api/admin/face-verification/<int:student_id>/reset', methods=['POST'])
@jwt_required()
@role_required('admin')
def reset_student_face(student_id):
    """Reset/delete a student's face registration."""
    from database.models import User
    from ai_modules.exam_proctoring.face_auth import FaceAuthenticator
    
    identity = get_identity()
    data = request.get_json() or {}
    reason = data.get('reason', 'No reason provided')
    
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    if not student.face_encoding:
        return jsonify({'error': 'Student has no face registered'}), 400
    
    # Reset face using the authenticator
    authenticator = FaceAuthenticator()
    success, message = authenticator.reset_face(student_id, identity['id'], reason)
    
    if success:
        return jsonify({
            'message': 'Face registration reset successfully',
            'student_id': student_id
        })
    else:
        return jsonify({'error': message}), 500


@admin_bp.route('/api/admin/face-verification/<int:student_id>/register', methods=['POST'])
@jwt_required()
@role_required('admin')
def admin_register_student_face(student_id):
    """Admin registers face for a student."""
    from database.models import User
    from ai_modules.exam_proctoring.face_auth import FaceAuthenticator
    
    identity = get_identity()
    data = request.get_json()
    
    if not data or not data.get('images'):
        return jsonify({'error': 'No face images provided'}), 400
    
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    reason = data.get('reason', 'Admin registration')
    images = data.get('images', [])
    
    if len(images) < 3:
        return jsonify({'error': 'At least 3 face samples required'}), 400
    
    authenticator = FaceAuthenticator()
    success, message = authenticator.admin_register_face(
        student_id, identity['id'], images, reason
    )
    
    if success:
        return jsonify({
            'message': message,
            'student_id': student_id,
            'face_registered': True
        })
    else:
        return jsonify({'error': message}), 400


@admin_bp.route('/api/admin/face-verification/logs/<int:student_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_student_face_logs(student_id):
    """Get face verification logs for a student."""
    from database.models import FaceVerificationLog, User
    
    # Verify student exists
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    logs = FaceVerificationLog.query.filter_by(user_id=student_id).order_by(
        FaceVerificationLog.created_at.desc()
    ).limit(50).all()
    
    return jsonify({
        'student_id': student_id,
        'student_name': f"{student.first_name} {student.last_name}",
        'logs': [log.to_dict() for log in logs]
    })


@admin_bp.route('/api/admin/face-verification/stats', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_face_verification_stats():
    """Get overall face verification statistics."""
    from database.models import User, Submission, FaceVerificationLog, db
    from sqlalchemy import func
    
    # Total students
    total_students = User.query.filter_by(role='student').count()
    
    # Students with face registered
    registered_count = User.query.filter(
        User.role == 'student',
        User.face_encoding.isnot(None)
    ).count()
    
    # Students without face
    not_registered_count = total_students - registered_count
    
    # Total verification attempts
    total_verifications = FaceVerificationLog.query.count()
    
    # Successful verifications
    successful_verifications = FaceVerificationLog.query.filter_by(status='success').count()
    
    # Failed verifications
    failed_verifications = FaceVerificationLog.query.filter_by(status='failed').count()
    
    # Recent activity (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    recent_verifications = FaceVerificationLog.query.filter(
        FaceVerificationLog.created_at >= week_ago
    ).count()
    
    recent_successful = FaceVerificationLog.query.filter(
        FaceVerificationLog.created_at >= week_ago,
        FaceVerificationLog.status == 'success'
    ).count()
    
    # By department
    dept_stats = db.session.query(
        User.department,
        func.count(User.id).label('total'),
        func.sum(db.case([(User.face_encoding.isnot(None), 1)], else_=0)).label('registered')
    ).filter(User.role == 'student').group_by(User.department).all()
    
    department_breakdown = [
        {
            'department': dept[0] or 'Unspecified',
            'total': dept[1],
            'registered': dept[2] or 0,
            'percentage': round((dept[2] or 0) / dept[1] * 100, 1) if dept[1] > 0 else 0
        }
        for dept in dept_stats
    ]
    
    return jsonify({
        'overview': {
            'total_students': total_students,
            'registered_faces': registered_count,
            'not_registered': not_registered_count,
            'registration_rate': round(registered_count / total_students * 100, 1) if total_students > 0 else 0
        },
        'verifications': {
            'total_attempts': total_verifications,
            'successful': successful_verifications,
            'failed': failed_verifications,
            'success_rate': round(successful_verifications / total_verifications * 100, 1) if total_verifications > 0 else 0
        },
        'recent_activity': {
            'last_7_days_attempts': recent_verifications,
            'last_7_days_successful': recent_successful
        },
        'department_breakdown': department_breakdown
    })
