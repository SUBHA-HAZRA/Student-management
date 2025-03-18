import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QFileDialog, QMessageBox, 
                             QDialog, QFormLayout)
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from PIL import Image
from database import StudentDatabase

class StudentManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = StudentDatabase()
        self.selected_photo_path = None
        self.initUI()
    
    def initUI(self):
        """Initialize the main user interface"""
        self.setWindowTitle('Student Management System')
        self.setGeometry(100, 100, 1200, 800)
        
        # Set a modern, dark color scheme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
                color: #ECF0F1;
            }
            QLabel, QLineEdit, QPushButton {
                font-size: 14px;
                padding: 8px;
                border-radius: 5px;
            }
            QLineEdit {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #2980B9;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QTableWidget {
                background-color: #34495E;
                color: #ECF0F1;
                alternate-background-color: #2C3E50;
            }
        """)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Search section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search by Name, Roll Number, Gender or Category')
        search_button = QPushButton('Search')
        search_button.clicked.connect(self.search_students)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        main_layout.addLayout(search_layout)
        
        # Student table
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(7)
        self.student_table.setHorizontalHeaderLabels(['Name','Son/Daughter Of','Roll Number','Gender',
                                                      'Category','Contact','Actions'])
        self.student_table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.student_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        add_button = QPushButton('Add Student')
        add_button.clicked.connect(self.open_add_student_dialog)
        action_layout.addWidget(add_button)
        main_layout.addLayout(action_layout)
        
        # Load initial data
        self.load_students()
    
    def load_students(self, students=None):
        """Load students into the table"""
        if students is None:
            students = self.db.get_all_students()
        
        self.student_table.setRowCount(len(students))
        for row, student in enumerate(students):
            # Display only first 6 columns (name, parents, rollno, gender, category, contact)
            for col in range(6):
                item = QTableWidgetItem(str(student[col]))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.student_table.setItem(row, col, item)
            
            # Add action buttons
            edit_btn = QPushButton('Edit')
            delete_btn = QPushButton('Delete')
            view_btn = QPushButton('View')
            
            # Use rollno (index 2) as the unique identifier
            rollno = student[2]
            edit_btn.clicked.connect(lambda _, r=rollno: self.edit_student(r))
            delete_btn.clicked.connect(lambda _, r=rollno: self.delete_student(r))
            view_btn.clicked.connect(lambda _, s=student: self.view_student(s))
            
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addWidget(view_btn)
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            self.student_table.setCellWidget(row, 6, action_widget)
    
    def search_students(self):
        """Search and filter students"""
        search_term = self.search_input.text()
        results = self.db.search_student(search_term)
        self.load_students(results)
    
    def open_add_student_dialog(self):
        """Open dialog to add new student"""
        dialog = StudentDialog(self)
        dialog.exec_()
        self.load_students()  # Refresh table
    
    def edit_student(self, rollno):
        """Open dialog to edit existing student"""
        student = self.db.get_student_by_rollno(rollno)
        if student:
            dialog = StudentDialog(self, rollno)
            dialog.exec_()
            self.load_students()
        else:
            QMessageBox.warning(self, "Error", f"Student with Roll No {rollno} not found.")
    
    def delete_student(self, rollno):
        """Delete a student record"""
        reply = QMessageBox.question(self, 'Delete Student', 
                                     'Are you sure you want to delete this student?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.delete_student(rollno):
                QMessageBox.information(self, "Success", "Student deleted successfully.")
                self.load_students()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete student.")
    
    def view_student(self, student_data):
        """View full student details"""
        dialog = QDialog(self)
        dialog.setWindowTitle('Student Details')
        layout = QFormLayout()
        
        # Display student photo
        photo_label = QLabel()
        photo_path = student_data[14]  # photo_path is at index 14
        if photo_path and os.path.exists(photo_path):
            try:
                pixmap = QPixmap(photo_path)
                photo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            except Exception as e:
                print(f"Error loading photo: {e}")
                photo_label.setText("Error loading photo")
        else:
            photo_label.setText("No Photo Available")
        
        # Add details to layout
        details = ['Name','Son/Daughter Of','Roll Number','Gender','Category','Contact','1st Sem SGPA',
                   '2nd Sem SGPA','3rd Sem SGPA','4th Sem SGPA','5th Sem SGPA','6th Sem SGPA','7th Sem SGPA','8th Sem SGPA']
        for i, detail in enumerate(details):
            layout.addRow(f'{detail}:', QLabel(str(student_data[i])))
        
        layout.addRow('Photo:', photo_label)
        dialog.setLayout(layout)
        dialog.exec_()

class StudentDialog(QDialog):
    def __init__(self, parent=None, rollno=None):
        super().__init__(parent)
        self.parent = parent
        self.rollno = rollno
        self.selected_photo_path = None
        self.initUI()
        
        # If editing existing student, populate fields
        if self.rollno:
            self.load_student_data()
    
    def initUI(self):
        """Initialize student dialog UI"""
        self.setWindowTitle('Add/Edit Student')
        layout = QFormLayout()
        
        # Input fields
        self.name_input = QLineEdit()
        self.parents_input = QLineEdit()
        self.rollno_input = QLineEdit()
        self.gender_input = QLineEdit()
        self.category_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.Sem1_input = QLineEdit()
        self.Sem2_input = QLineEdit()
        self.Sem3_input = QLineEdit()
        self.Sem4_input = QLineEdit()
        self.Sem5_input = QLineEdit()
        self.Sem6_input = QLineEdit()
        self.Sem7_input = QLineEdit()
        self.Sem8_input = QLineEdit()
        
        # Photo selection
        self.photo_label = QLabel('No Photo Selected')
        photo_button = QPushButton('Select Photo')
        photo_button.clicked.connect(self.select_photo)
        
        # Add to layout
        layout.addRow('Name:', self.name_input)
        layout.addRow('Son/Daughter Of:', self.parents_input)
        layout.addRow('Roll Number:', self.rollno_input)
        layout.addRow('Gender:', self.gender_input)
        layout.addRow('Category:', self.category_input)
        layout.addRow('Contact:', self.contact_input)
        layout.addRow('1st Sem SGPA:', self.Sem1_input)
        layout.addRow('2nd Sem SGPA:', self.Sem2_input)
        layout.addRow('3rd Sem SGPA:', self.Sem3_input)
        layout.addRow('4th Sem SGPA:', self.Sem4_input)
        layout.addRow('5th Sem SGPA:', self.Sem5_input)
        layout.addRow('6th Sem SGPA:', self.Sem6_input)
        layout.addRow('7th Sem SGPA:', self.Sem7_input)
        layout.addRow('8th Sem SGPA:', self.Sem8_input)
        layout.addRow('Photo:', self.photo_label)
        layout.addRow('', photo_button)
        
        # Save button
        save_button = QPushButton('Save Student')
        save_button.clicked.connect(self.save_student)
        layout.addRow('', save_button)
        
        self.setLayout(layout)
    
    def select_photo(self):
        """Select and display student photo"""
        file_name, _ = QFileDialog.getOpenFileName(self, 'Select Photo', 
                                                   '', 'Image Files (*.png *.jpg *.jpeg)')
        if file_name:
            # Create directory if it doesn't exist
            os.makedirs('student_photos', exist_ok=True)
            
            # Save photo to project directory
            filename = os.path.basename(file_name)
            dest_path = os.path.join('student_photos', f'{filename}')
            
            # Resize and save image
            try:
                img = Image.open(file_name)
                img.thumbnail((300, 300))
                img.save(dest_path)
                
                self.selected_photo_path = dest_path
                self.photo_label.setText(filename)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to process image: {e}")
    
    def load_student_data(self):
        """Load existing student data for editing"""
        student = self.parent.db.get_student_by_rollno(self.rollno)
        if student:
            self.name_input.setText(student[0])
            self.parents_input.setText(student[1])
            self.rollno_input.setText(student[2])
            self.gender_input.setText(student[3])
            self.category_input.setText(student[4])
            self.contact_input.setText(student[5])
            self.Sem1_input.setText(student[6])
            self.Sem2_input.setText(student[7])
            self.Sem3_input.setText(student[8])
            self.Sem4_input.setText(student[9])
            self.Sem5_input.setText(student[10])
            self.Sem6_input.setText(student[11])
            self.Sem7_input.setText(student[12])
            self.Sem8_input.setText(student[13])
            self.selected_photo_path = student[14]
            
            # Display photo filename if available
            if self.selected_photo_path:
                self.photo_label.setText(os.path.basename(self.selected_photo_path))
    
    def save_student(self):
        """Save student data to database"""
        # Validate inputs
        if not self.validate_inputs():
            return

        # Collect input data
        student_data = (
            self.name_input.text(),
            self.parents_input.text(),
            self.rollno_input.text(),
            self.gender_input.text(),
            self.category_input.text(),
            self.contact_input.text(),
            self.Sem1_input.text(),
            self.Sem2_input.text(),
            self.Sem3_input.text(),
            self.Sem4_input.text(),
            self.Sem5_input.text(),
            self.Sem6_input.text(),
            self.Sem7_input.text(),
            self.Sem8_input.text(),
            self.selected_photo_path or ''
        )
        
        # Save or update student
        if self.rollno:
            success = self.parent.db.update_student(self.rollno, student_data)
            message = "Student updated successfully!" if success else "Failed to update student."
        else:
            new_id = self.parent.db.add_student(student_data)
            success = new_id is not None
            message = "Student added successfully!" if success else "Failed to add student."
        
        # Show result message
        if success:
            QMessageBox.information(self, 'Success', message)
            self.close()
        else:
            QMessageBox.warning(self, 'Error', message)
    
    def validate_inputs(self):
        """Validate user inputs before saving"""
        # Check required fields
        required_fields = [
            (self.name_input, 'Name'),
            (self.rollno_input, 'Roll Number'),
            (self.gender_input, 'Gender')
        ]
        
        for field, name in required_fields:
            if not field.text().strip():
                QMessageBox.warning(self, 'Validation Error', f'{name} cannot be empty')
                return False
        
        return True