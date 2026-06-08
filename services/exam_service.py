from database.models import db, Exam, Question, Submission, Answer, Violation
from datetime import datetime


class ExamService:
    """Business logic for exam operations."""

    @staticmethod
    def auto_grade_submission(submission_id):
        """Auto-grade all MCQ questions and optionally use AI for short answers."""
        submission = Submission.query.get(submission_id)
        if not submission:
            return None, 'Submission not found'

        answers = Answer.query.filter_by(submission_id=submission_id).all()
        total_score = 0
        all_graded = True

        for answer in answers:
            question = Question.query.get(answer.question_id)
            if not question:
                continue

            if question.question_type == 'mcq':
                answer.is_correct = str(answer.selected_option) == str(question.correct_answer)
                answer.score = question.marks if answer.is_correct else 0
                total_score += answer.score

            elif question.question_type in ('short_answer', 'essay'):
                try:
                    from ai_modules.gemini_service import grade_answer
                    score, feedback = grade_answer(
                        question_text=question.question_text,
                        question_type=question.question_type,
                        student_answer=answer.answer_text or '',
                        correct_answer=question.correct_answer or '',
                        max_marks=question.marks,
                    )
                    answer.score = score
                    answer.ai_feedback = feedback
                    answer.is_correct = score >= (question.marks * 0.5)
                    total_score += score
                except Exception:
                    all_graded = False

        submission.total_score = total_score
        if all_graded:
            submission.is_graded = True
            submission.status = 'graded'

        db.session.commit()
        return submission, None

    @staticmethod
    def get_risk_report(submission_id):
        """Generate a risk report for a submission."""
        submission = Submission.query.get(submission_id)
        if not submission:
            return None

        violations = Violation.query.filter_by(submission_id=submission_id).order_by(Violation.timestamp).all()

        # Severity breakdown
        severity_map = {
            'multiple_faces': 40,
            'no_face': 15,
            'eye_gaze': 5,
            'head_pose': 5,
            'lip_movement': 20,
            'phone_detected': 50,
            'tab_switch': 10,
            'background_person': 40,
        }

        type_counts = {}
        for v in violations:
            vtype = v.violation_type
            if vtype not in type_counts:
                type_counts[vtype] = 0
            type_counts[vtype] += 1

        return {
            'submission_id': submission_id,
            'risk_score': submission.risk_score,
            'is_flagged': submission.is_flagged,
            'total_violations': len(violations),
            'violation_breakdown': type_counts,
            'severity_reference': severity_map,
            'timeline': [v.to_dict() for v in violations],
        }

    @staticmethod
    def generate_exam_from_material(material_id, num_questions=10, difficulty='understand'):
        """Use AI to generate quiz questions from course material."""
        try:
            from ai_modules.assessment_ai.quiz_generator import QuizGenerator
            generator = QuizGenerator()
            return generator.generate_from_material(material_id, num_questions, difficulty)
        except ImportError:
            return None, 'Quiz generation AI module not available'
