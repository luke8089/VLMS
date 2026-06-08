import threading
from flask import Blueprint, request, jsonify, render_template, current_app
from flask_jwt_extended import jwt_required
from database.models import (
    db, User, Course, Enrollment, Material, Lecture, Exam, Submission,
    Question, Answer, LearningProgress, LiveClass
)
from utils.security import role_required, get_identity
from utils.helpers import paginate_query, save_uploaded_file, allowed_file
from datetime import datetime, timedelta

student_bp = Blueprint('student', __name__)


# ──────────────── PAGE ROUTES ────────────────

@student_bp.route('/student/dashboard')
@jwt_required()
@role_required('student')
def dashboard():
    return render_template('student_panel.html')


@student_bp.route('/student/materials/<int:material_id>/read')
@jwt_required()
@role_required('student')
def read_material(material_id):
    identity = get_identity()
    material = Material.query.get(material_id)
    if not material:
        return render_template('student_panel.html')

    enrollment = Enrollment.query.filter_by(
        student_id=identity['id'], course_id=material.course_id, status='active'
    ).first()
    if not enrollment:
        return render_template('student_panel.html')

    if material.file_type != 'pdf':
        return render_template('student_panel.html')

    progress = LearningProgress.query.filter_by(
        student_id=identity['id'], material_id=material_id
    ).first()

    material_data = material.to_dict()
    material_data['file_url'] = f"/uploads/{material.file_path}"
    material_data['course_title'] = material.course.title if material.course else None

    return render_template(
        'material_reader.html',
        material_data=material_data,
        progress_data=progress.to_dict() if progress else None,
        show_ai_summary=False,
    )


# ──────────────── COURSE ROUTES ────────────────

@student_bp.route('/api/student/courses', methods=['GET'])
@jwt_required()
@role_required('student')
def get_enrolled_courses():
    identity = get_identity()
    page = request.args.get('page', 1, type=int)
    enrollment_list = Enrollment.query.filter_by(
        student_id=identity['id'], status='active'
    ).all()
    course_ids = [e.course_id for e in enrollment_list]
    if not course_ids:
        return jsonify({'items': [], 'total': 0, 'page': 1, 'pages': 0, 'has_next': False})
    courses = Course.query.filter(Course.id.in_(course_ids), Course.is_published == True, Course.is_active == True)
    return jsonify(paginate_query(courses, page))


@student_bp.route('/api/student/courses/available', methods=['GET'])
@jwt_required()
@role_required('student')
def get_available_courses():
    identity = get_identity()
    
    # Get student's department
    student = User.query.get(identity['id'])
    student_department = student.department if student else None
    
    enrolled_ids = [e.course_id for e in
                    Enrollment.query.filter_by(student_id=identity['id']).all()]
    
    # Build query filtering by department if set
    if student_department:
        query = Course.query.filter(
            Course.is_published == True,
            Course.is_active == True,
            db.func.lower(Course.category) == db.func.lower(student_department)
        )
    else:
        query = Course.query.filter(Course.is_published == True, Course.is_active == True)
    
    # Exclude already enrolled courses
    if enrolled_ids:
        query = query.filter(~Course.id.in_(enrolled_ids))
    
    page = request.args.get('page', 1, type=int)
    return jsonify(paginate_query(query, page))


@student_bp.route('/api/student/courses/all', methods=['GET'])
@jwt_required()
@role_required('student')
def get_all_courses():
    """Return all published courses matching student's department with an enrolled flag."""
    identity = get_identity()
    
    # Get student's department
    student = User.query.get(identity['id'])
    student_department = student.department if student else None
    
    enrolled_ids = set(
        e.course_id for e in
        Enrollment.query.filter_by(student_id=identity['id'], status='active').all()
    )
    
    # Filter courses by student's department (or show all if no department set)
    if student_department:
        courses = Course.query.filter(
            Course.is_published == True,
            Course.is_active == True,
            db.func.lower(Course.category) == db.func.lower(student_department)
        ).order_by(Course.title).all()
    else:
        courses = Course.query.filter(
            Course.is_published == True,
            Course.is_active == True,
        ).order_by(Course.title).all()
    
    items = []
    for c in courses:
        d = c.to_dict()
        d['enrolled'] = c.id in enrolled_ids
        items.append(d)
    return jsonify({'items': items, 'total': len(items)})


@student_bp.route('/api/student/courses/<int:course_id>/enroll', methods=['POST'])
@jwt_required()
@role_required('student')
def enroll_in_course(course_id):
    identity = get_identity()
    
    # Get student and course
    student = User.query.get(identity['id'])
    course = Course.query.get(course_id)
    
    if not course or not course.is_published or not course.is_active:
        return jsonify({'error': 'Course not found'}), 404

    # Check department match (case-insensitive)
    if course.category and student.department:
        if course.category.strip().lower() != student.department.strip().lower():
            return jsonify({
                'error': 'Cannot enroll - this course belongs to "' + course.category + '" department. You are registered under "' + student.department + '" department.'
            }), 403

    existing = Enrollment.query.filter_by(
        student_id=identity['id'], course_id=course_id
    ).first()
    if existing:
        return jsonify({'error': 'Already enrolled'}), 400

    enrollment = Enrollment(student_id=identity['id'], course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    return jsonify({'message': 'Enrolled successfully', 'enrollment': enrollment.to_dict()}), 201


# ──────────────── MATERIALS ROUTES ────────────────

@student_bp.route('/api/student/courses/<int:course_id>/materials', methods=['GET'])
@jwt_required()
@role_required('student')
def get_course_materials(course_id):
    identity = get_identity()
    course = Course.query.get(course_id)
    if not course or not course.is_active:
        return jsonify({'error': 'Course not available'}), 404

    enrollment = Enrollment.query.filter_by(
        student_id=identity['id'], course_id=course_id, status='active'
    ).first()
    if not enrollment:
        return jsonify({'error': 'Not enrolled in this course'}), 403

    materials = Material.query.filter_by(course_id=course_id).all()
    return jsonify({'materials': [m.to_dict() for m in materials]})


@student_bp.route('/api/student/courses/<int:course_id>/lectures', methods=['GET'])
@jwt_required()
@role_required('student')
def get_course_lectures(course_id):
    identity = get_identity()
    course = Course.query.get(course_id)
    if not course or not course.is_active:
        return jsonify({'error': 'Course not available'}), 404

    enrollment = Enrollment.query.filter_by(
        student_id=identity['id'], course_id=course_id, status='active'
    ).first()
    if not enrollment:
        return jsonify({'error': 'Not enrolled in this course'}), 403
    lectures = Lecture.query.filter_by(
        course_id=course_id, is_published=True
    ).order_by(Lecture.order_index).all()

    lecturer_info = None
    if course and course.lecturer:
        lec = course.lecturer
        lecturer_info = {
            'name': f"{lec.first_name} {lec.last_name}",
            'profile_image': lec.profile_image,
        }
        if lec.share_contact:
            lecturer_info['email'] = lec.email
            lecturer_info['phone_number'] = lec.phone_number
            lecturer_info['bio'] = lec.bio
            lecturer_info['contact_shared'] = True
        else:
            lecturer_info['contact_shared'] = False

    return jsonify({
        'lectures': [l.to_dict() for l in lectures],
        'course_title': course.title if course else None,
        'course_code': course.code if course else None,
        'lecturer': lecturer_info,
    })


# ──────────────── LEARNING PROGRESS ────────────────

@student_bp.route('/api/student/progress/<int:material_id>', methods=['POST'])
@jwt_required()
@role_required('student')
def update_progress(material_id):
    identity = get_identity()
    data = request.get_json() or {}

    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': 'Material not found'}), 404

    enrollment = Enrollment.query.filter_by(
        student_id=identity['id'], course_id=material.course_id, status='active'
    ).first()
    if not enrollment:
        return jsonify({'error': 'Not enrolled in this course'}), 403

    progress = LearningProgress.query.filter_by(
        student_id=identity['id'], material_id=material_id
    ).first()

    if not progress:
        progress = LearningProgress(
            student_id=identity['id'],
            material_id=material_id
        )
        db.session.add(progress)

    progress.has_opened = True
    if not progress.first_opened_at:
        progress.first_opened_at = datetime.utcnow()

    if data.get('last_page') is not None:
        progress.last_page = max(0, int(data['last_page']))
    if data.get('total_pages') is not None:
        progress.total_pages = max(0, int(data['total_pages']))

    if data.get('progress_percent') is not None:
        progress.progress_percent = min(100, max(0, data['progress_percent']))

    if progress.total_pages > 0 and progress.last_page > 0:
        computed_percent = min(100, (progress.last_page / progress.total_pages) * 100)
        progress.progress_percent = max(progress.progress_percent or 0, computed_percent)

    if data.get('time_spent_seconds') is not None:
        progress.time_spent_seconds += max(0, int(data['time_spent_seconds']))

    if progress.progress_percent >= 100 or (
        progress.total_pages > 0 and progress.last_page >= progress.total_pages
    ):
        progress.completed = True

    db.session.commit()
    return jsonify({'progress': progress.to_dict()})


@student_bp.route('/api/student/materials/<int:material_id>/progress', methods=['GET'])
@jwt_required()
@role_required('student')
def get_material_progress(material_id):
    identity = get_identity()
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': 'Material not found'}), 404

    enrollment = Enrollment.query.filter_by(
        student_id=identity['id'], course_id=material.course_id, status='active'
    ).first()
    if not enrollment:
        return jsonify({'error': 'Not enrolled in this course'}), 403

    progress = LearningProgress.query.filter_by(
        student_id=identity['id'], material_id=material_id
    ).first()

    return jsonify({
        'material': material.to_dict(),
        'progress': progress.to_dict() if progress else None,
    })


@student_bp.route('/api/student/materials/<int:material_id>/progress', methods=['POST'])
@jwt_required()
@role_required('student')
def update_material_progress(material_id):
    return update_progress(material_id)


# ──────────────── EXAM ROUTES ────────────────

def _submission_remaining_seconds(submission, exam):
    duration_seconds = int((exam.duration_minutes or 0) * 60)
    if duration_seconds <= 0:
        return 0
    started_at = submission.started_at or datetime.utcnow()
    elapsed = int((datetime.utcnow() - started_at).total_seconds())
    remaining = duration_seconds - elapsed

    if exam.end_time:
        remaining_until_close = int((exam.end_time - datetime.now()).total_seconds())
        remaining = min(remaining, remaining_until_close)

    return max(0, remaining)


def _finalize_submission(submission):
    """Mark submission as submitted immediately, then grade non-MCQ answers in background."""
    submission.submitted_at = datetime.utcnow()
    submission.status = 'submitted'

    # Tally MCQ scores (already stored per-answer) so total_score is not zero
    mcq_total = 0
    has_open_questions = False
    answers = Answer.query.filter_by(submission_id=submission.id).all()
    for ans in answers:
        q = Question.query.get(ans.question_id)
        if not q:
            continue
        if q.question_type == 'mcq':
            mcq_total += ans.score or 0
        else:
            has_open_questions = True

    submission.total_score = mcq_total
    if not has_open_questions:
        submission.is_graded = True
        submission.status = 'graded'

    db.session.commit()

    # Grade short_answer / essay in background so the HTTP response is instant
    if has_open_questions:
        app = current_app._get_current_object()
        submission_id = submission.id
        threading.Thread(
            target=_background_grade,
            args=(app, submission_id),
            daemon=True,
        ).start()

    return submission


def _background_grade(app, submission_id):
    """Grade open-ended answers with Gemini in a background thread."""
    from ai_modules.gemini_service import grade_answer
    with app.app_context():
        try:
            submission = Submission.query.get(submission_id)
            if not submission:
                return

            answers = Answer.query.filter_by(submission_id=submission_id).all()
            total_score = 0
            all_graded = True

            for ans in answers:
                q = Question.query.get(ans.question_id)
                if not q:
                    continue
                if q.question_type == 'mcq':
                    total_score += ans.score or 0
                    continue
                try:
                    score, feedback = grade_answer(
                        question_text=q.question_text,
                        question_type=q.question_type,
                        student_answer=ans.answer_text or '',
                        correct_answer=q.correct_answer or '',
                        max_marks=q.marks,
                    )
                    ans.score = score
                    ans.ai_feedback = feedback
                    ans.is_correct = score >= (q.marks * 0.5)
                    total_score += score
                except Exception as exc:
                    import logging
                    logging.getLogger(__name__).error("Background grading error for answer %s: %s", ans.id, exc)
                    all_graded = False

            submission.total_score = total_score
            if all_graded:
                submission.is_graded = True
                submission.status = 'graded'

            db.session.commit()
        except Exception as exc:
            import logging
            logging.getLogger(__name__).error("Background grading thread error for submission %s: %s", submission_id, exc)
            db.session.rollback()

@student_bp.route('/api/student/exams', methods=['GET'])
@jwt_required()
@role_required('student')
def get_available_exams():
    identity = get_identity()
    print(f"Loading exams for student {identity['id']}")

    enrolled_ids = [e.course_id for e in
                    Enrollment.query.filter_by(student_id=identity['id'], status='active').all()]

    if not enrolled_ids:
        return jsonify({'exams': []})

    # Only include exams from active courses
    active_course_ids = [
        c.id for c in Course.query.filter(
            Course.id.in_(enrolled_ids), Course.is_active == True
        ).all()
    ]

    now = datetime.now()

    # Return ALL published exams for enrolled active courses (upcoming + open + closed)
    exams = Exam.query.filter(
        Exam.course_id.in_(active_course_ids),
        Exam.is_published == True,
    ).order_by(Exam.start_time.asc()).all()

    exam_data = []
    for exam in exams:
        sub = Submission.query.filter_by(
            exam_id=exam.id, student_id=identity['id']
        ).first()
        ed = exam.to_dict()
        ed['submission_status'] = sub.status if sub else None
        # Scores are visible only when the individual submission's grades_released flag is set
        if sub and sub.grades_released and sub.is_graded:
            ed['total_score'] = sub.total_score
        else:
            ed['total_score'] = None
            # Mark as awaiting release so the student knows they've submitted but results aren't visible yet
            if sub and sub.status in ('submitted', 'graded'):
                ed['submission_status'] = 'awaiting_release' if not sub.grades_released else sub.status

        # Compute exam availability status
        if exam.start_time and now < exam.start_time:
            ed['availability'] = 'upcoming'
        elif exam.end_time and now > exam.end_time:
            ed['availability'] = 'closed'
        else:
            # Exam is open if within time window, regardless of submission status
            ed['availability'] = 'open'

        # Include course name for display
        course = Course.query.get(exam.course_id)
        ed['course_title'] = course.title if course else ''
        ed['course_code'] = course.code if course else ''

        exam_data.append(ed)

    return jsonify({'exams': exam_data})


@student_bp.route('/api/student/exams/<int:exam_id>/start', methods=['POST'])
@jwt_required()
@role_required('student')
def start_exam(exam_id):
    identity = get_identity()
    exam = Exam.query.get(exam_id)
    if not exam or not exam.is_published:
        return jsonify({'error': 'Exam not found'}), 404

    course = Course.query.get(exam.course_id)
    if not course or not course.is_active:
        return jsonify({'error': 'This course is currently unavailable'}), 403

    # Verify enrollment
    enrollment = Enrollment.query.filter_by(
        student_id=identity['id'], course_id=exam.course_id, status='active'
    ).first()
    if not enrollment:
        return jsonify({'error': 'Not enrolled in this course'}), 403

    # Check existing submission
    existing = Submission.query.filter_by(
        exam_id=exam_id, student_id=identity['id']
    ).first()
    if existing and existing.status != 'in_progress':
        return jsonify({'error': 'Exam already submitted'}), 400

    # Check time window for new attempts
    now = datetime.now()
    if not existing:
        if exam.start_time and now < exam.start_time:
            return jsonify({
                'error': 'This exam has not opened yet.',
                'opens_at': exam.start_time.isoformat()
            }), 403
        if exam.end_time and now > exam.end_time:
            return jsonify({'error': 'This exam has already closed.'}), 403

    if not existing:
        existing = Submission(
            exam_id=exam_id,
            student_id=identity['id'],
            status='in_progress',
            started_at=datetime.utcnow(),
        )
        db.session.add(existing)
        db.session.commit()
    else:
        remaining_seconds = _submission_remaining_seconds(existing, exam)
        if remaining_seconds <= 0:
            _finalize_submission(existing)
            return jsonify({
                'error': 'Time is up. Your exam was auto-submitted.',
                'auto_submitted': True,
                'submission': existing.to_dict(),
            }), 403

    # Get questions (without correct answers)
    questions = Question.query.filter_by(exam_id=exam_id).order_by(Question.order_index).all()
    remaining_seconds = _submission_remaining_seconds(existing, exam)
    answers = Answer.query.filter_by(submission_id=existing.id).all()
    return jsonify({
        'submission_id': existing.id,
        'exam': exam.to_dict(),
        'remaining_seconds': remaining_seconds,
        'questions': [q.to_dict(include_answer=False) for q in questions],
        'answers': [a.to_dict() for a in answers],
    })


@student_bp.route('/api/student/exams/<int:submission_id>/answer', methods=['POST'])
@jwt_required()
@role_required('student')
def submit_answer(submission_id):
    identity = get_identity()
    submission = Submission.query.get(submission_id)
    if not submission or submission.student_id != identity['id']:
        return jsonify({'error': 'Submission not found'}), 404
    if submission.status != 'in_progress':
        return jsonify({'error': 'Exam already submitted'}), 400

    exam = Exam.query.get(submission.exam_id)
    if not exam:
        return jsonify({'error': 'Exam not found'}), 404

    remaining_seconds = _submission_remaining_seconds(submission, exam)
    if remaining_seconds <= 0:
        _finalize_submission(submission)
        return jsonify({
            'error': 'Time is up. Your exam was auto-submitted.',
            'auto_submitted': True,
            'submission': submission.to_dict(),
        }), 403

    data = request.get_json()
    question_id = data.get('question_id')
    question = Question.query.get(question_id)
    if not question or question.exam_id != submission.exam_id:
        return jsonify({'error': 'Invalid question'}), 400

    # Upsert answer
    answer = Answer.query.filter_by(
        submission_id=submission_id, question_id=question_id
    ).first()
    if not answer:
        answer = Answer(submission_id=submission_id, question_id=question_id)
        db.session.add(answer)

    if question.question_type == 'mcq':
        answer.selected_option = data.get('selected_option')
        # Auto-grade MCQ
        if question.correct_answer is not None:
            answer.is_correct = str(answer.selected_option) == str(question.correct_answer)
            answer.score = question.marks if answer.is_correct else 0
    else:
        answer.answer_text = data.get('answer_text', '')

    db.session.commit()
    return jsonify({'message': 'Answer saved', 'answer': answer.to_dict()})


@student_bp.route('/api/student/exams/<int:submission_id>/submit', methods=['POST'])
@jwt_required()
@role_required('student')
def submit_exam(submission_id):
    identity = get_identity()
    submission = Submission.query.get(submission_id)
    if not submission or submission.student_id != identity['id']:
        return jsonify({'error': 'Submission not found'}), 404
    if submission.status != 'in_progress':
        return jsonify({'error': 'Already submitted'}), 400

    exam = Exam.query.get(submission.exam_id)
    if not exam:
        return jsonify({'error': 'Exam not found'}), 404

    _finalize_submission(submission)
    return jsonify({
        'message': 'Exam submitted successfully',
        'submission': submission.to_dict(),
    })


@student_bp.route('/api/student/results', methods=['GET'])
@jwt_required()
@role_required('student')
def get_results():
    identity = get_identity()
    submissions = Submission.query.filter_by(student_id=identity['id']).all()
    results = []
    for sub in submissions:
        exam = Exam.query.get(sub.exam_id)
        if not exam:
            continue
        # Show results only when this individual submission's grades have been released
        if not sub.grades_released or not sub.is_graded:
            continue
        course = Course.query.get(exam.course_id) if exam else None
        entry = {
            **sub.to_dict(),
            'exam_title': exam.title,
            'exam_type': exam.exam_type,
            'total_marks': exam.total_marks,
            'course_title': course.title if course else None,
        }
        print(f"Including result: score {sub.total_score}")
        results.append(entry)
    return jsonify({'results': results})


# ──────────────── LIVE CLASSES ROUTES ────────────────

def purge_expired_live_classes():
    """Delete live classes that have already ended."""
    now = datetime.now()
    classes = LiveClass.query.all()
    deleted = False

    for live_class in classes:
        duration = int(live_class.duration_minutes or 60)
        class_end = live_class.scheduled_at + timedelta(minutes=duration)
        if class_end <= now:
            db.session.delete(live_class)
            deleted = True

    if deleted:
        db.session.commit()

@student_bp.route('/api/student/classes', methods=['GET'])
@jwt_required()
@role_required('student')
def get_live_classes():
    purge_expired_live_classes()
    identity = get_identity()
    enrolled = Enrollment.query.filter_by(student_id=identity['id']).all()
    course_ids = [e.course_id for e in enrolled]

    if not course_ids:
        return jsonify({'classes': []})

    classes = LiveClass.query.filter(
        LiveClass.course_id.in_(course_ids)
    ).order_by(LiveClass.scheduled_at.asc()).all()

    now = datetime.now()
    result = []
    for c in classes:
        is_accessible = c.is_unlocked or (c.scheduled_at and c.scheduled_at <= now)
        course = Course.query.get(c.course_id)
        data = c.to_dict()
        data['course_title'] = course.title if course else None
        data['course_code'] = course.code if course else None
        data['access_status'] = 'unlocked' if is_accessible else 'locked'
        if not is_accessible:
            data['meeting_link'] = None  # hide link when locked
        result.append(data)

    return jsonify({'classes': result})
