import sqlite3
from datetime import datetime

DB_NAME = "academy.db"

def connect():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = connect()
    cursor = conn.cursor()
    
    # Create Students Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            join_date TEXT
        )
    ''')
    
    # Create Attendance Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_student(name, phone):
    conn = connect()
    cursor = conn.cursor()
    date_today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO students (name, phone, join_date) VALUES (?, ?, ?)", 
                   (name, phone, date_today))
    conn.commit()
    conn.close()

def get_all_students():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone FROM students")
    records = cursor.fetchall()
    conn.close()
    return records
