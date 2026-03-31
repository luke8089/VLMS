#!/usr/bin/env python3
"""
Test script to check the grades API endpoint
"""

import requests
import json

# Base URL
BASE_URL = "http://127.0.0.1:5000"

def test_grades_api():
    """Test the grades API endpoint"""
    
    # First, try to login as a student
    print("=== Testing Login ===")
    login_data = {
        "email": "test@student.com",
        "password": "password123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access_token')
            print("Login successful!")
            
            # Now test the grades endpoint
            print("\n=== Testing Grades API ===")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            grades_response = requests.get(f"{BASE_URL}/api/student/results", headers=headers)
            print(f"Grades API Status: {grades_response.status_code}")
            
            if grades_response.status_code == 200:
                grades_data = grades_response.json()
                results = grades_data.get('results', [])
                print(f"Number of results: {len(results)}")
                
                for result in results:
                    print(f"  - Exam: {result.get('exam_title', 'Unknown')}")
                    print(f"    Score: {result.get('total_score', 'N/A')}")
                    print(f"    Course: {result.get('course_title', 'N/A')}")
                    print(f"    Status: {result.get('submission_status', 'N/A')}")
                    print()
            else:
                print(f"Grades API Error: {grades_response.text}")
                
        else:
            print(f"Login failed: {login_response.text}")
            
            # Try different credentials
            print("\n=== Trying Different Credentials ===")
            test_creds = [
                {"email": "jane123@gmail.com", "password": "password123"},
                {"email": "Jane@gmail.com", "password": "password123"},
                {"email": "wahbih837@gmail.com", "password": "password123"}
            ]
            
            for creds in test_creds:
                print(f"Trying: {creds['email']}")
                try:
                    resp = requests.post(f"{BASE_URL}/api/auth/login", json=creds)
                    if resp.status_code == 200:
                        token = resp.json().get('access_token')
                        headers = {"Authorization": f"Bearer {token}"}
                        grades_resp = requests.get(f"{BASE_URL}/api/student/results", headers=headers)
                        print(f"  -> Grades API Status: {grades_resp.status_code}")
                        if grades_resp.status_code == 200:
                            data = grades_resp.json()
                            print(f"  -> Results count: {len(data.get('results', []))}")
                        break
                except Exception as e:
                    print(f"  -> Error: {e}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_grades_api()
