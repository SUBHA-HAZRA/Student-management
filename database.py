import sqlite3
import os
import logging
from datetime import datetime

class StudentDatabase:
    def __init__(self, db_name='students.db'):
        # Setup logging
        logging.basicConfig(filename='logs/database.log', level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Database connection
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self):
        """Create students table if not exists"""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    name TEXT NOT NULL,
                    parents TEXT,
                    rollno TEXT PRIMARY KEY,
                    gender TEXT,
                    category TEXT,
                    contact TEXT,
                    Sem1 TEXT,
                    Sem2 TEXT,
                    Sem3 TEXT,
                    Sem4 TEXT,
                    Sem5 TEXT,
                    Sem6 TEXT,
                    Sem7 TEXT,
                    Sem8 TEXT,
                    photo_path TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
            logging.info("Database table created successfully")
        except sqlite3.Error as e:
            logging.error(f"Error creating table: {e}")
    
    def add_student(self, student_data):
        """Add new student to database"""
        try:
            query = '''
                INSERT INTO students 
                (name, parents, rollno, gender, category, contact, Sem1, Sem2, Sem3, Sem4, Sem5, Sem6, Sem7, Sem8, photo_path) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            self.cursor.execute(query, student_data)
            self.conn.commit()
            logging.info(f"Added student: {student_data[0]}")
            return student_data[2]  # Return rollno as ID
        except sqlite3.Error as e:
            logging.error(f"Error adding student: {e}")
            return None

    def search_student(self, search_term):
        """Search students by various attributes"""
        try:
            query = '''
                SELECT * FROM students 
                WHERE name LIKE ? OR rollno LIKE ? OR gender LIKE ? OR category LIKE ?
            '''
            search_pattern = f'%{search_term}%'
            self.cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
            results = self.cursor.fetchall()
            logging.info(f"Search for '{search_term}' returned {len(results)} results")
            return results
        except sqlite3.Error as e:
            logging.error(f"Error searching students: {e}")
            return []
    
    def update_student(self, rollno, updated_data):
        """Update existing student record"""
        try:
            query = '''
                UPDATE students 
                SET name=?, parents=?, rollno=?, gender=?, category=?, 
                    contact=?, Sem1=?, Sem2=?, Sem3=?, Sem4=?, Sem5=?,
                    Sem6=?, Sem7=?, Sem8=?, photo_path=? 
                WHERE rollno=?
            '''
            # The last parameter should be the original rollno (before any changes)
            full_update_data = updated_data + (rollno,)
            self.cursor.execute(query, full_update_data)
            self.conn.commit()
            logging.info(f"Updated student with rollno: {rollno}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Error updating student: {e}")
            return False
    
    def delete_student(self, rollno):
        """Delete student record"""
        try:
            # First, get the photo path to delete the file
            self.cursor.execute('SELECT photo_path FROM students WHERE rollno=?', (rollno,))
            result = self.cursor.fetchone()
            photo_path = result[0] if result else None
            
            # Delete student record
            self.cursor.execute('DELETE FROM students WHERE rollno=?', (rollno,))
            self.conn.commit()
            
            # Remove photo file if it exists
            if photo_path and os.path.exists(photo_path):
                os.remove(photo_path)
            
            logging.info(f"Deleted student with rollno: {rollno}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Error deleting student: {e}")
            return False
    
    def get_all_students(self):
        """Retrieve all student records"""
        try:
            self.cursor.execute('SELECT * FROM students')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error retrieving all students: {e}")
            return []
    
    def get_student_by_rollno(self, rollno):
        """Retrieve a specific student by rollno"""
        try:
            self.cursor.execute('SELECT * FROM students WHERE rollno=?', (rollno,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Error retrieving student with rollno {rollno}: {e}")
            return None
    
    def __del__(self):
        """Close database connection"""
        self.conn.close()