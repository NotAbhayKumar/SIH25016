import cv2
import numpy as np
import os
from datetime import datetime
import json
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class GUIAttendanceSystem:
    def __init__(self):
        self.attendance_data = {}
        self.load_attendance_data()
        self.cap = None
        self.face_cascade = None
        self.running = False
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title("Smart Attendance System")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        self.setup_gui()
        
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
    
    def setup_gui(self):
        """Setup the GUI interface"""
        # Title
        title_label = tk.Label(self.root, text="🎓 Smart Attendance System", 
                              font=('Arial', 20, 'bold'), 
                              bg='#2c3e50', fg='white')
        title_label.pack(pady=20)
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#2c3e50')
        status_frame.pack(pady=10)
        
        self.status_label = tk.Label(status_frame, text="Status: Ready", 
                                   font=('Arial', 12), 
                                   bg='#2c3e50', fg='#27ae60')
        self.status_label.pack()
        
        # Camera frame
        camera_frame = tk.Frame(self.root, bg='#2c3e50')
        camera_frame.pack(pady=10)
        
        self.camera_label = tk.Label(camera_frame, text="Camera: Not Started", 
                                   font=('Arial', 10), 
                                   bg='#2c3e50', fg='white')
        self.camera_label.pack()
        
        # Buttons frame
        buttons_frame = tk.Frame(self.root, bg='#2c3e50')
        buttons_frame.pack(pady=20)
        
        # Start/Stop camera button
        self.camera_btn = tk.Button(buttons_frame, text="📹 Start Camera", 
                                  command=self.toggle_camera,
                                  font=('Arial', 12, 'bold'),
                                  bg='#3498db', fg='white',
                                  padx=20, pady=10)
        self.camera_btn.pack(side=tk.LEFT, padx=10)
        
        # Attendance buttons
        attendance_frame = tk.Frame(self.root, bg='#2c3e50')
        attendance_frame.pack(pady=20)
        
        tk.Label(attendance_frame, text="Mark Attendance:", 
                font=('Arial', 14, 'bold'), 
                bg='#2c3e50', fg='white').pack()
        
        btn_frame = tk.Frame(attendance_frame, bg='#2c3e50')
        btn_frame.pack(pady=10)
        
        # Create attendance buttons
        students = [
            ("1", "Soumyadeep"),
            ("2", "Sundar"),
            ("3", "Elon"),
            ("4", "Sparsh"),
            ("5", "Tannistha")
        ]
        
        for i, (student_id, name) in enumerate(students):
            btn = tk.Button(btn_frame, text=f"{student_id}\n{name}", 
                          command=lambda sid=student_id: self.mark_attendance(sid),
                          font=('Arial', 10, 'bold'),
                          bg='#e74c3c', fg='white',
                          width=8, height=2)
            btn.grid(row=0, column=i, padx=5)
        
        # Display frame
        display_frame = tk.Frame(self.root, bg='#2c3e50')
        display_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        
        # Create treeview for attendance display
        columns = ('ID', 'Name', 'Attendance', 'Last Marked')
        self.tree = ttk.Treeview(display_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Update display
        self.update_display()
        
        # Face detection status
        self.face_status = tk.Label(self.root, text="Face Detection: Inactive", 
                                  font=('Arial', 10), 
                                  bg='#2c3e50', fg='#e74c3c')
        self.face_status.pack(pady=5)
    
    def update_display(self):
        """Update the attendance display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add current data
        for student_id, data in self.attendance_data.items():
            last_attendance = data['last_attendance'] if data['last_attendance'] else "Never"
            self.tree.insert('', 'end', values=(
                student_id, 
                data['name'], 
                data['total_attendance'], 
                last_attendance
            ))
    
    def toggle_camera(self):
        """Start or stop camera"""
        if not self.running:
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        """Start camera and face detection"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Could not open camera!")
                return
            
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.running = True
            
            self.camera_btn.config(text="📹 Stop Camera", bg='#e74c3c')
            self.camera_label.config(text="Camera: Active", fg='#27ae60')
            self.status_label.config(text="Status: Camera Running", fg='#27ae60')
            
            # Start face detection thread
            threading.Thread(target=self.face_detection_loop, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {e}")
    
    def stop_camera(self):
        """Stop camera"""
        self.running = False
        if self.cap:
            self.cap.release()
        
        self.camera_btn.config(text="📹 Start Camera", bg='#3498db')
        self.camera_label.config(text="Camera: Stopped", fg='#e74c3c')
        self.status_label.config(text="Status: Ready", fg='#27ae60')
        self.face_status.config(text="Face Detection: Inactive", fg='#e74c3c')
    
    def face_detection_loop(self):
        """Face detection loop running in background"""
        while self.running and self.cap:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    self.face_status.config(text=f"Face Detection: {len(faces)} face(s) detected", fg='#27ae60')
                else:
                    self.face_status.config(text="Face Detection: No faces detected", fg='#f39c12')
                
                time.sleep(0.5)  # Update every 500ms
                
            except Exception as e:
                print(f"Face detection error: {e}")
                break
    
    def mark_attendance(self, student_id):
        """Mark attendance for a student"""
        if student_id in self.attendance_data:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.attendance_data[student_id]["total_attendance"] += 1
            self.attendance_data[student_id]["last_attendance"] = current_time
            self.save_attendance_data()
            
            student_name = self.attendance_data[student_id]["name"]
            messagebox.showinfo("Attendance Marked", 
                              f"✅ Attendance marked for {student_name}!\n"
                              f"Total attendance: {self.attendance_data[student_id]['total_attendance']}\n"
                              f"Time: {current_time}")
            
            self.update_display()
        else:
            messagebox.showerror("Error", f"Student ID {student_id} not found!")
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        self.running = False
        if self.cap:
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    app = GUIAttendanceSystem()
    app.run()
