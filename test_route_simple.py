#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import and test the route
try:
    from app import create_app
    from database.models import db, Submission, Answer
    
    print("Creating app...")
    app = create_app('development')
    
    with app.app_context():
        print("Testing database connection...")
        # Test if we can query submissions
        submissions = Submission.query.limit(1).all()
        print(f"Found {len(submissions)} submissions")
        
        # Test if we can query answers
        answers = Answer.query.limit(1).all()
        print(f"Found {len(answers)} answers")
        
        print("Database connection working")
        print("Models imported successfully")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
