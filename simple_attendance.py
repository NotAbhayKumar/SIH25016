import cv2
import numpy as np
import os
from datetime import datetime
import json

class SimpleAttendanceSystem:
    def __init__(self):
        self.attendance_data = {}
        self.load_attendance_data()
        
    def load_attendance_data(self):
        """Load attendance data from JSON file"""
        try:
            with open('attendance_data.json', 'r') as f:
                self.attendance_data = json.load(f)
        except FileNotFoundError:
            # Initialize with sample data
            self.attendance_data = {
                "1": {"name": "Soumyadeep Mukherjee", "total_attendance": 0, "last_attendance": ""},
                "2": {"name": "Sundar Pichai", "total_attendance": 0, "last_attendance": ""},
                "3": {"name": "Elon Musk", "total_attendance": 0, "last_attendance": ""},
                "4": {"name": "Sparsh Singh", "total_attendance": 0, "last_attendance": ""},
                "5": {"name": "Tannistha Muhuri", "total_attendance": 0, "last_attendance": ""}
            }
            self.save_attendance_data()
    
    def save_attendance_data(self):
        """Save attendance data to JSON file"""
        with open('attendance_data.json', 'w') as f:
            json.dump(self.attendance_data, f, indent=2)
    
    def mark_attendance(self, student_id):
        """Mark attendance for a student"""
        if student_id in self.attendance_data:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.attendance_data[student_id]["total_attendance"] += 1
            self.attendance_data[student_id]["last_attendance"] = current_time
            self.save_attendance_data()
            return True
        return False
    
    def run(self):
        """Main application loop"""
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        cap.set(3, 640)
        cap.set(4, 480)
        
        # Load background image
        try:
            img_background = cv2.imread('Resources/background.png')
            if img_background is None:
                print("Background image not found. Using plain background.")
                img_background = np.zeros((480, 640, 3), dtype=np.uint8)
        except:
            img_background = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Initialize face cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        print("Simple Attendance System Started!")
        print("Press 'q' to quit, '1-5' to mark attendance for students 1-5")
        print("Student IDs: 1-Soumyadeep, 2-Sundar, 3-Elon, 4-Sparsh, 5-Tannistha")
        
        while True:
            success, img = cap.read()
            if not success:
                break
            
            # Flip image horizontally for mirror effect
            img = cv2.flip(img, 1)
            
            # Detect faces
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(img, "Face Detected", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # Display attendance information
            y_offset = 30
            cv2.putText(img, "Simple Attendance System", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            y_offset += 30
            
            for student_id, data in self.attendance_data.items():
                text = f"ID {student_id}: {data['name']} - Attendance: {data['total_attendance']}"
                cv2.putText(img, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_offset += 20
            
            # Display instructions
            cv2.putText(img, "Press 1-5 to mark attendance, 'q' to quit", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            cv2.imshow("Simple Attendance System", img)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key >= ord('1') and key <= ord('5'):
                student_id = str(key - ord('0'))
                if self.mark_attendance(student_id):
                    student_name = self.attendance_data[student_id]["name"]
                    print(f"Attendance marked for {student_name} (ID: {student_id})")
                    print(f"Total attendance: {self.attendance_data[student_id]['total_attendance']}")
                else:
                    print(f"Student ID {student_id} not found!")
        
        cap.release()
        cv2.destroyAllWindows()
        print("Attendance System Closed!")

if __name__ == "__main__":
    system = SimpleAttendanceSystem()
    system.run()
