import sys
import os
from PyQt5.QtWidgets import QApplication
from gui import StudentManagementApp

def main():
    # Ensure project directories exist
    os.makedirs('student_photos', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Create logs directory with proper permissions
    try:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        # Ensure the log file is writable or can be created
        log_file = 'logs/database.log'
        if not os.path.exists(log_file):
            with open(log_file, 'w') as f:
                pass  # Just create the file
        # Make sure it's writable
        os.chmod(log_file, 0o666)  # Read/write for everyone
    except Exception as e:
        print(f"Warning: Could not set up log file: {e}")
        
    # Initialize the application
    app = QApplication(sys.argv)
    window = StudentManagementApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()