import sqlite3
import os

# Check if database exists
db_path = 'lms.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute('PRAGMA table_info(submissions)')
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'approval_status' not in columns:
        print('Adding approval_status column...')
        cursor.execute('ALTER TABLE submissions ADD COLUMN approval_status TEXT DEFAULT "pending"')
        conn.commit()
        print('Column added successfully')
    else:
        print('Column already exists')
    
    conn.close()
else:
    print('Database not found')
