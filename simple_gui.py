import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime
import cv2
import threading
import time

class SimpleAttendanceGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Attendance System")
        self.root.geometry("600x500")
        self.root.configure(bg='lightblue')
        
        # Load data
        self.load_data()
        
        # Create GUI
        self.create_widgets()
        
    def load_data(self):
        try:
            with open('attendance_data.json', 'r') as f:
                self.data = json.load(f)
        except:
            self.data = {
                "1": {"name": "Soumyadeep Mukherjee", "attendance": 0, "last": ""},
                "2": {"name": "Sundar Pichai", "attendance": 0, "last": ""},
                "3": {"name": "Elon Musk", "attendance": 0, "last": ""},
                "4": {"name": "Sparsh Singh", "attendance": 0, "last": ""},
                "5": {"name": "Tannistha Muhuri", "attendance": 0, "last": ""}
            }
            self.save_data()
    
    def save_data(self):
        with open('attendance_data.json', 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="🎓 Smart Attendance System", 
                        font=('Arial', 20, 'bold'), bg='lightblue')
        title.pack(pady=20)
        
        # Status
        self.status = tk.Label(self.root, text="System Ready", 
                              font=('Arial', 12), bg='lightblue', fg='green')
        self.status.pack(pady=10)
        
        # Buttons frame
        btn_frame = tk.Frame(self.root, bg='lightblue')
        btn_frame.pack(pady=20)
        
        tk.Label(btn_frame, text="Mark Attendance:", 
                font=('Arial', 14, 'bold'), bg='lightblue').pack()
        
        # Create buttons
        for i in range(1, 6):
            btn = tk.Button(btn_frame, text=f"Student {i}\n{self.data[str(i)]['name']}", 
                          command=lambda x=i: self.mark_attendance(str(x)),
                          font=('Arial', 10, 'bold'),
                          bg='lightgreen', fg='black',
                          width=12, height=2)
            btn.pack(side=tk.LEFT, padx=5)
        
        # Display frame
        display_frame = tk.Frame(self.root, bg='lightblue')
        display_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        
        # Treeview
        columns = ('ID', 'Name', 'Attendance', 'Last Marked')
        self.tree = ttk.Treeview(display_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Update display
        self.update_display()
        
        # Camera button
        self.camera_btn = tk.Button(self.root, text="📹 Start Camera", 
                                  command=self.toggle_camera,
                                  font=('Arial', 12, 'bold'),
                                  bg='orange', fg='white')
        self.camera_btn.pack(pady=10)
        
        # Face status
        self.face_status = tk.Label(self.root, text="Camera: Off", 
                                  font=('Arial', 10), bg='lightblue')
        self.face_status.pack()
    
    def update_display(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for student_id, info in self.data.items():
            last = info['last'] if info['last'] else "Never"
            self.tree.insert('', 'end', values=(
                student_id, info['name'], info['attendance'], last
            ))
    
    def mark_attendance(self, student_id):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data[student_id]["attendance"] += 1
        self.data[student_id]["last"] = current_time
        self.save_data()
        
        name = self.data[student_id]["name"]
        messagebox.showinfo("Success", f"Attendance marked for {name}!\nTotal: {self.data[student_id]['attendance']}")
        
        self.update_display()
        self.status.config(text=f"Last marked: {name}", fg='blue')
    
    def toggle_camera(self):
        if not hasattr(self, 'camera_running'):
            self.camera_running = False
        
        if not self.camera_running:
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Cannot open camera!")
                return
            
            self.camera_running = True
            self.camera_btn.config(text="📹 Stop Camera", bg='red')
            self.face_status.config(text="Camera: On - Detecting faces...", fg='green')
            
            # Start face detection
            threading.Thread(target=self.detect_faces, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Camera error: {e}")
    
    def stop_camera(self):
        self.camera_running = False
        if hasattr(self, 'cap'):
            self.cap.release()
        
        self.camera_btn.config(text="📹 Start Camera", bg='orange')
        self.face_status.config(text="Camera: Off", fg='black')
    
    def detect_faces(self):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        while self.camera_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    self.face_status.config(text=f"Camera: On - {len(faces)} face(s) detected!", fg='green')
                else:
                    self.face_status.config(text="Camera: On - No faces detected", fg='orange')
                
                time.sleep(0.5)
                
            except:
                break
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleAttendanceGUI()
    app.run()
