#!/usr/bin/env python3
"""
Test the frontend JavaScript logic for grades grouping
"""

def test_grades_grouping():
    """Test the grades grouping logic"""
    
    # Simulate API response data
    mock_results = [
        {
            'exam_title': 'Cat 1',
            'course_title': 'Introduction to Programming',
            'exam_type': 'quiz',
            'total_score': 18.0,
            'total_marks': 30.0,
            'submitted_at': '2026-03-30T20:08:41',
            'submission_status': 'graded'
        },
        {
            'exam_title': 'Cat 2',
            'course_title': 'Introduction to Programming',
            'exam_type': 'midterm',
            'total_score': 15.0,
            'total_marks': 30.0,
            'submitted_at': '2026-03-25T08:55:12',
            'submission_status': 'graded'
        },
        {
            'exam_title': 'cat 1 oop',
            'course_title': 'object oriented programmming',
            'exam_type': 'quiz',
            'total_score': 25.0,
            'total_marks': 30.0,
            'submitted_at': '2026-03-26T11:39:56',
            'submission_status': 'graded'
        },
        {
            'exam_title': 'Cat 2',
            'course_title': 'object oriented programmming',
            'exam_type': 'midterm',
            'total_score': 22.0,
            'total_marks': 30.0,
            'submitted_at': '2026-03-26T15:27:25',
            'submission_status': 'graded'
        },
        {
            'exam_title': 'Final Exam - OOP',
            'course_title': 'object oriented programmming',
            'exam_type': 'final',
            'total_score': 42.0,
            'total_marks': 50.0,
            'submitted_at': '2026-03-31T12:00:00',
            'submission_status': 'graded'
        }
    ]
    
    # Simulate the JavaScript grouping logic
    def letter_grade(pct):
        if pct is None:
            return {'letter': '-', 'color': 'text-neutral-300 bg-white/10'}
        if pct >= 80:
            return {'letter': 'A', 'color': 'text-white bg-green-500'}
        if pct >= 70:
            return {'letter': 'B', 'color': 'text-white bg-blue-500'}
        if pct >= 60:
            return {'letter': 'C', 'color': 'text-white bg-yellow-500'}
        if pct >= 50:
            return {'letter': 'D', 'color': 'text-white bg-orange-500'}
        return {'letter': 'F', 'color': 'text-white bg-red-500'}
    
    # Group results by course and assessment type
    course_groups = {}
    for r in mock_results:
        course_title = r.get('course_title', 'Unknown Course')
        if course_title not in course_groups:
            course_groups[course_title] = {
                'courseTitle': course_title,
                'cat1': None,
                'cat2': None,
                'mainExam': None,
                'assignment': None,
                'latestDate': None
            }
        
        group = course_groups[course_title]
        exam_type = (r.get('exam_type', '')).lower()
        exam_title = (r.get('exam_title', '')).lower()
        
        # Categorize by assessment type
        if 'cat 1' in exam_title or 'cat1' in exam_title or exam_type == 'quiz':
            group['cat1'] = r
        elif 'cat 2' in exam_title or 'cat2' in exam_title or exam_type == 'midterm':
            group['cat2'] = r
        elif 'main exam' in exam_title or 'main_exam' in exam_title or 'final' in exam_title or exam_type == 'final':
            group['mainExam'] = r
        elif exam_type == 'assignment' or 'assignment' in exam_title:
            group['assignment'] = r
        
        # Track latest date
        if r.get('submitted_at'):
            from datetime import datetime
            date = datetime.fromisoformat(r['submitted_at'].replace('T', ' '))
            if not group['latestDate'] or date > datetime.fromisoformat(group['latestDate'].replace('T', ' ')):
                group['latestDate'] = r['submitted_at']
    
    # Calculate overall grade for each course
    course_groups_array = []
    for group in course_groups.values():
        # Check if all required assessments are complete
        has_cat1_score = bool(group['cat1'] and group['cat1']['total_score'] is not None)
        has_cat2_score = bool(group['cat2'] and group['cat2']['total_score'] is not None)
        has_main_score = bool(group['mainExam'] and group['mainExam']['total_score'] is not None)
        all_complete = has_cat1_score and has_cat2_score and has_main_score
        
        # Only calculate grade when all 3 assessments are complete
        percentage = None
        grade_info = {'letter': '-', 'color': 'text-neutral-300 bg-white/10'}
        
        if all_complete:
            scores = [group['cat1']['total_score'], group['cat2']['total_score'], group['mainExam']['total_score']]
            total_marks = [group['cat1']['total_marks'], group['cat2']['total_marks'], group['mainExam']['total_marks']]
            
            total_score = sum(scores)
            total_possible = sum(total_marks)
            percentage = round((total_score / total_possible) * 100)
            grade_info = letter_grade(percentage)
        
        group['percentage'] = percentage
        group['grade_info'] = grade_info
        group['all_complete'] = all_complete
        course_groups_array.append(group)
    
    # Print results
    print("=== GRADES TABLE STRUCTURE ===")
    print("Course | CAT 1 | CAT 2 | Main Exam | Assignment | Grade | Date Released")
    print("-" * 80)
    
    for group in course_groups_array:
        def render_score(assessment):
            if not assessment or assessment.get('total_score') is None:
                return "—"
            return f"{assessment['total_score']}/{assessment['total_marks']}"
        
        course_name = group['courseTitle'][:20]  # Truncate for display
        cat1_score = render_score(group['cat1'])
        cat2_score = render_score(group['cat2'])
        main_score = render_score(group['mainExam'])
        assignment_score = render_score(group['assignment'])
        grade = group['grade_info']['letter']
        date = group['latestDate'].split('T')[0] if group['latestDate'] else "—"
        complete_status = "[COMPLETE]" if group['all_complete'] else "[INCOMPLETE]"
        
        print(f"{course_name:<20} | {cat1_score:>6} | {cat2_score:>6} | {main_score:>10} | {assignment_score:>11} | {grade:>5} | {date} | {complete_status}")
    
    print(f"\nTotal courses: {len(course_groups_array)}")
    complete_courses = [g for g in course_groups_array if g['all_complete']]
    print(f"Complete courses (CAT1+CAT2+Main): {len(complete_courses)}")
    
    if complete_courses:
        avg_score = round(sum(g['percentage'] for g in complete_courses) / len(complete_courses))
        highest_score = max(g['percentage'] for g in complete_courses)
        print(f"Average score (complete only): {avg_score}%")
        print(f"Highest score (complete only): {highest_score}%")
    else:
        print("Average score: Pending")
        print("Highest score: 0")

if __name__ == "__main__":
    test_grades_grouping()
