import cv2
import numpy as np
import os
from datetime import datetime
import json
import threading
import time

class ConsoleAttendanceSystem:
    def __init__(self):
        self.attendance_data = {}
        self.load_attendance_data()
        self.running = True
        
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
    
    def display_attendance(self):
        """Display current attendance status"""
        print("\n" + "="*60)
        print("           SMART ATTENDANCE SYSTEM")
        print("="*60)
        print(f"{'ID':<3} {'Name':<20} {'Attendance':<10} {'Last Marked':<20}")
        print("-"*60)
        
        for student_id, data in self.attendance_data.items():
            last_attendance = data['last_attendance'] if data['last_attendance'] else "Never"
            print(f"{student_id:<3} {data['name']:<20} {data['total_attendance']:<10} {last_attendance:<20}")
        
        print("="*60)
        print("Commands:")
        print("  1-5: Mark attendance for student ID 1-5")
        print("  s: Show attendance status")
        print("  q: Quit")
        print("="*60)
    
    def face_detection_thread(self):
        """Background thread for face detection"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Warning: Could not open webcam. Face detection disabled.")
                return
                
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    print(f"\n[FACE DETECTED] {len(faces)} face(s) found in camera!")
                
                time.sleep(1)  # Check every second
                
            cap.release()
        except Exception as e:
            print(f"Face detection error: {e}")
    
    def run(self):
        """Main application loop"""
        print("Smart Attendance System Starting...")
        print("Initializing face detection...")
        
        # Start face detection in background thread
        face_thread = threading.Thread(target=self.face_detection_thread, daemon=True)
        face_thread.start()
        
        time.sleep(2)  # Give time for camera initialization
        
        self.display_attendance()
        
        while self.running:
            try:
                command = input("\nEnter command (1-5, s, q): ").strip().lower()
                
                if command == 'q':
                    print("Shutting down attendance system...")
                    self.running = False
                    break
                elif command == 's':
                    self.display_attendance()
                elif command in ['1', '2', '3', '4', '5']:
                    student_id = command
                    if self.mark_attendance(student_id):
                        student_name = self.attendance_data[student_id]["name"]
                        print(f"\n✅ Attendance marked for {student_name} (ID: {student_id})")
                        print(f"   Total attendance: {self.attendance_data[student_id]['total_attendance']}")
                        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    else:
                        print(f"❌ Student ID {student_id} not found!")
                else:
                    print("❌ Invalid command. Use 1-5, s, or q")
                    
            except KeyboardInterrupt:
                print("\nShutting down attendance system...")
                self.running = False
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("Attendance System Closed!")
        print("Final attendance data saved to attendance_data.json")

if __name__ == "__main__":
    system = ConsoleAttendanceSystem()
    system.run()
