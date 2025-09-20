import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime, date
import csv
import cv2
import threading
import time
import hashlib
from PIL import Image, ImageTk
import numpy as np

class FullAttendanceSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Attendance Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage
        self.users_file = 'users.json'
        self.students_file = 'students.json'
        self.attendance_file = 'attendance.json'
        
        # Initialize data
        self.load_data()
        
        # Current user
        self.current_user = None
        
        # Face detection
        self.camera_running = False
        self.cap = None
        
        # Start with login
        self.show_login()
    
    def load_data(self):
        """Load all data from JSON files"""
        # Load users
        try:
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {
                "admin": {
                    "password": self.hash_password("admin123"),
                    "role": "admin",
                    "name": "Administrator"
                },
                "teacher": {
                    "password": self.hash_password("teacher123"),
                    "role": "teacher", 
                    "name": "Teacher"
                }
            }
            self.save_users()
        
        # Load students
        try:
            with open(self.students_file, 'r') as f:
                self.students = json.load(f)
        except FileNotFoundError:
            self.students = {}
            self.save_students()
        
        # Load attendance
        try:
            with open(self.attendance_file, 'r') as f:
                self.attendance = json.load(f)
        except FileNotFoundError:
            self.attendance = {}
            self.save_attendance()
    
    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def save_students(self):
        with open(self.students_file, 'w') as f:
            json.dump(self.students, f, indent=2)
    
    def save_attendance(self):
        with open(self.attendance_file, 'w') as f:
            json.dump(self.attendance, f, indent=2)
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def show_login(self):
        """Show login window"""
        self.clear_window()
        
        # Login frame
        login_frame = tk.Frame(self.root, bg='#f0f0f0')
        login_frame.pack(expand=True)
        
        # Title
        title_label = tk.Label(login_frame, text="🎓 Smart Attendance System", 
                              font=('Arial', 24, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=30)
        
        subtitle_label = tk.Label(login_frame, text="Please login to continue", 
                                 font=('Arial', 14), bg='#f0f0f0', fg='#7f8c8d')
        subtitle_label.pack(pady=10)
        
        # Login form
        form_frame = tk.Frame(login_frame, bg='white', relief='raised', bd=2)
        form_frame.pack(pady=20, padx=50)
        
        tk.Label(form_frame, text="Username:", font=('Arial', 12), bg='white').pack(pady=10)
        self.username_entry = tk.Entry(form_frame, font=('Arial', 12), width=25)
        self.username_entry.pack(pady=5)
        
        tk.Label(form_frame, text="Password:", font=('Arial', 12), bg='white').pack(pady=10)
        self.password_entry = tk.Entry(form_frame, font=('Arial', 12), width=25, show='*')
        self.password_entry.pack(pady=5)
        
        # Login button
        login_btn = tk.Button(form_frame, text="Login", command=self.login,
                             font=('Arial', 12, 'bold'), bg='#3498db', fg='white',
                             width=15, height=2)
        login_btn.pack(pady=20)
        
        # Default credentials
        cred_frame = tk.Frame(login_frame, bg='#f0f0f0')
        cred_frame.pack(pady=10)
        
        tk.Label(cred_frame, text="Default Credentials:", font=('Arial', 10, 'bold'), 
                bg='#f0f0f0').pack()
        tk.Label(cred_frame, text="Admin: admin / admin123", font=('Arial', 10), 
                bg='#f0f0f0').pack()
        tk.Label(cred_frame, text="Teacher: teacher / teacher123", font=('Arial', 10), 
                bg='#f0f0f0').pack()
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.login())
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username in self.users:
            if self.users[username]['password'] == self.hash_password(password):
                self.current_user = username
                messagebox.showinfo("Success", f"Welcome, {self.users[username]['name']}!")
                self.show_dashboard()
            else:
                messagebox.showerror("Error", "Invalid password!")
        else:
            messagebox.showerror("Error", "Invalid username!")
    
    def show_dashboard(self):
        """Show main dashboard"""
        self.clear_window()
        
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Smart Attendance Management System", 
                              font=('Arial', 18, 'bold'), bg='#2c3e50', fg='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        user_label = tk.Label(header_frame, text=f"Welcome, {self.users[self.current_user]['name']}", 
                             font=('Arial', 12), bg='#2c3e50', fg='white')
        user_label.pack(side=tk.RIGHT, padx=20, pady=20)
        
        logout_btn = tk.Button(header_frame, text="Logout", command=self.logout,
                              font=('Arial', 10), bg='#e74c3c', fg='white')
        logout_btn.pack(side=tk.RIGHT, padx=10, pady=20)
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Navigation buttons
        nav_frame = tk.Frame(content_frame, bg='#f0f0f0')
        nav_frame.pack(fill=tk.X, pady=10)
        
        buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("👥 Students", self.show_students),
            ("📝 Attendance", self.show_attendance),
            ("📈 Reports", self.show_reports),
            ("⚙️ Settings", self.show_settings)
        ]
        
        for text, command in buttons:
            btn = tk.Button(nav_frame, text=text, command=command,
                           font=('Arial', 11, 'bold'), bg='#3498db', fg='white',
                           width=15, height=2)
            btn.pack(side=tk.LEFT, padx=5)
        
        # Dashboard content
        dashboard_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=2)
        dashboard_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Statistics
        stats_frame = tk.Frame(dashboard_frame, bg='white')
        stats_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(stats_frame, text="System Overview", font=('Arial', 16, 'bold'), 
                bg='white').pack(pady=10)
        
        # Stats grid
        stats_grid = tk.Frame(stats_frame, bg='white')
        stats_grid.pack(fill=tk.X, pady=10)
        
        total_students = len(self.students)
        today = date.today().strftime("%Y-%m-%d")
        today_attendance = len([a for a in self.attendance.get(today, {}).values() if a])
        
        stats = [
            ("Total Students", total_students, "#3498db"),
            ("Today's Attendance", today_attendance, "#27ae60"),
            ("Attendance Rate", f"{(today_attendance/total_students*100):.1f}%" if total_students > 0 else "0%", "#f39c12"),
            ("Total Records", len(self.attendance), "#e74c3c")
        ]
        
        for i, (label, value, color) in enumerate(stats):
            stat_frame = tk.Frame(stats_grid, bg=color, relief='raised', bd=2)
            stat_frame.grid(row=0, column=i, padx=10, pady=10, sticky='ew')
            
            tk.Label(stat_frame, text=str(value), font=('Arial', 24, 'bold'), 
                    bg=color, fg='white').pack(pady=5)
            tk.Label(stat_frame, text=label, font=('Arial', 12), 
                    bg=color, fg='white').pack(pady=5)
        
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)
        stats_grid.columnconfigure(2, weight=1)
        stats_grid.columnconfigure(3, weight=1)
    
    def show_students(self):
        """Show student management"""
        self.clear_window()
        self.create_header()
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Navigation
        self.create_navigation(content_frame)
        
        # Student management frame
        student_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=2)
        student_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Title and add button
        title_frame = tk.Frame(student_frame, bg='white')
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(title_frame, text="Student Management", font=('Arial', 16, 'bold'), 
                bg='white').pack(side=tk.LEFT)
        
        add_btn = tk.Button(title_frame, text="➕ Add Student", command=self.add_student,
                           font=('Arial', 12, 'bold'), bg='#27ae60', fg='white')
        add_btn.pack(side=tk.RIGHT)
        
        # Students table
        table_frame = tk.Frame(student_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        columns = ('ID', 'Name', 'Email', 'Phone', 'Course', 'Year', 'Face Image', 'Actions')
        self.student_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        
        self.student_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load students
        self.load_students_table()
    
    def add_student(self):
        """Add new student dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Student")
        dialog.geometry("500x600")  # Reduced height
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)  # Prevent resizing
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Create main container with scrollbar
        main_frame = tk.Frame(dialog, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(main_frame, bg='white')
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(scrollable_frame, text="Add New Student", font=('Arial', 16, 'bold'), 
                bg='white').pack(pady=20)
        
        # Form fields
        fields = [
            ("Student ID:", "id"),
            ("Full Name:", "name"),
            ("Email:", "email"),
            ("Phone:", "phone"),
            ("Course:", "course"),
            ("Year:", "year")
        ]
        
        entries = {}
        for label, key in fields:
            frame = tk.Frame(scrollable_frame, bg='white')
            frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(frame, text=label, font=('Arial', 12), bg='white').pack(anchor='w')
            entry = tk.Entry(frame, font=('Arial', 12), width=30)
            entry.pack(fill=tk.X, pady=5)
            entries[key] = entry
        
        # Face image section
        face_frame = tk.Frame(scrollable_frame, bg='white')
        face_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(face_frame, text="Face Image:", font=('Arial', 12, 'bold'), 
                bg='white').pack(anchor='w')
        
        # Image preview frame
        img_preview_frame = tk.Frame(face_frame, bg='lightgray', relief='sunken', bd=2)
        img_preview_frame.pack(fill=tk.X, pady=5)
        img_preview_frame.configure(height=100)  # Reduced height
        
        # Image label for preview
        img_label = tk.Label(img_preview_frame, text="No image selected", 
                            font=('Arial', 10), bg='lightgray', fg='gray')
        img_label.pack(expand=True)
        
        # Image buttons frame
        img_btn_frame = tk.Frame(face_frame, bg='white')
        img_btn_frame.pack(fill=tk.X, pady=5)
        
        selected_image_path = [None]  # Use list to make it mutable in nested function
        
        def select_image():
            file_path = filedialog.askopenfilename(
                title="Select Student Face Image",
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")]
            )
            if file_path:
                selected_image_path[0] = file_path
                try:
                    # Load and resize image for preview
                    from PIL import Image, ImageTk
                    img = Image.open(file_path)
                    img = img.resize((80, 80), Image.Resampling.LANCZOS)  # Smaller preview
                    photo = ImageTk.PhotoImage(img)
                    img_label.configure(image=photo, text="")
                    img_label.image = photo  # Keep a reference
                except Exception as e:
                    messagebox.showerror("Error", f"Could not load image: {e}")
        
        def capture_image():
            """Capture image from camera"""
            try:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    messagebox.showerror("Error", "Cannot open camera!")
                    return
                
                # Create camera capture dialog
                camera_dialog = tk.Toplevel(dialog)
                camera_dialog.title("Capture Face Image")
                camera_dialog.geometry("400x500")
                camera_dialog.configure(bg='white')
                camera_dialog.transient(dialog)
                camera_dialog.grab_set()
                camera_dialog.resizable(False, False)  # Prevent resizing
                
                # Camera preview
                camera_label = tk.Label(camera_dialog, text="Camera Preview", 
                                      font=('Arial', 12), bg='white')
                camera_label.pack(pady=10)
                
                # Capture button
                capture_btn = tk.Button(camera_dialog, text="📷 Capture", 
                                      command=lambda: self.capture_face_image(cap, camera_dialog, selected_image_path, img_label),
                                      font=('Arial', 12, 'bold'), bg='#3498db', fg='white')
                capture_btn.pack(pady=10)
                
                # Close button
                close_btn = tk.Button(camera_dialog, text="Close Camera", 
                                    command=lambda: [cap.release(), camera_dialog.destroy()],
                                    font=('Arial', 12), bg='#e74c3c', fg='white')
                close_btn.pack(pady=5)
                
                # Start camera preview
                self.show_camera_preview(cap, camera_label)
                
            except Exception as e:
                messagebox.showerror("Error", f"Camera error: {e}")
        
        # Image selection buttons
        tk.Button(img_btn_frame, text="📁 Select Image", command=select_image,
                 font=('Arial', 10), bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(img_btn_frame, text="📷 Capture from Camera", command=capture_image,
                 font=('Arial', 10), bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=5)
        
        # Buttons - Fixed at bottom of dialog (outside scrollable area)
        btn_frame = tk.Frame(dialog, bg='white', height=80)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
        btn_frame.pack_propagate(False)  # Maintain fixed height
        
        def save_student():
            student_id = entries['id'].get()
            if student_id in self.students:
                messagebox.showerror("Error", "Student ID already exists!")
                return
            
            # Validate required fields
            if not all([entries[key].get() for key in ['id', 'name', 'email']]):
                messagebox.showerror("Error", "Please fill in all required fields!")
                return
            
            # Save student data
            student_data = {
                'name': entries['name'].get(),
                'email': entries['email'].get(),
                'phone': entries['phone'].get(),
                'course': entries['course'].get(),
                'year': entries['year'].get(),
                'face_image': selected_image_path[0] if selected_image_path[0] else None
            }
            
            # Copy face image to Images folder if provided
            if selected_image_path[0]:
                try:
                    import shutil
                    import os
                    # Create Images folder if it doesn't exist
                    if not os.path.exists('Images'):
                        os.makedirs('Images')
                    
                    # Copy image to Images folder with student ID as filename
                    image_extension = os.path.splitext(selected_image_path[0])[1]
                    new_image_path = f'Images/{student_id}{image_extension}'
                    shutil.copy2(selected_image_path[0], new_image_path)
                    student_data['face_image'] = new_image_path
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save image: {e}")
                    return
            
            self.students[student_id] = student_data
            self.save_students()
            self.load_students_table()
            dialog.destroy()
            messagebox.showinfo("Success", "Student added successfully!")
        
        # Create buttons with better styling
        save_btn = tk.Button(btn_frame, text="💾 Save Student", command=save_student,
                           font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                           width=15, height=2)
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy,
                             font=('Arial', 12, 'bold'), bg='#e74c3c', fg='white',
                             width=15, height=2)
        cancel_btn.pack(side=tk.RIGHT, padx=10)
        
        # Add a separator line above buttons
        separator = tk.Frame(btn_frame, height=2, bg='#bdc3c7')
        separator.pack(fill=tk.X, pady=10)
    
    def load_students_table(self):
        """Load students into table"""
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        for student_id, student in self.students.items():
            face_status = "✅ Yes" if student.get('face_image') else "❌ No"
            self.student_tree.insert('', 'end', values=(
                student_id,
                student['name'],
                student['email'],
                student['phone'],
                student['course'],
                student['year'],
                face_status,
                "Edit | Delete"
            ))
    
    def show_attendance(self):
        """Show attendance marking"""
        self.clear_window()
        self.create_header()
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Navigation
        self.create_navigation(content_frame)
        
        # Attendance frame
        attendance_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=2)
        attendance_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Title
        title_frame = tk.Frame(attendance_frame, bg='white')
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(title_frame, text="Attendance Management", font=('Arial', 16, 'bold'), 
                bg='white').pack(side=tk.LEFT)
        
        # Camera controls
        camera_frame = tk.Frame(title_frame, bg='white')
        camera_frame.pack(side=tk.RIGHT)
        
        self.camera_btn = tk.Button(camera_frame, text="📹 Start Camera", 
                                  command=self.toggle_camera,
                                  font=('Arial', 12, 'bold'), bg='#3498db', fg='white')
        self.camera_btn.pack(side=tk.LEFT, padx=5)
        
        self.face_status = tk.Label(camera_frame, text="Camera: Off", 
                                  font=('Arial', 10), bg='white')
        self.face_status.pack(side=tk.LEFT, padx=10)
        
        # Manual attendance button
        manual_btn = tk.Button(camera_frame, text="✅ Mark All Present", 
                              command=self.mark_all_present,
                              font=('Arial', 10, 'bold'), bg='#27ae60', fg='white')
        manual_btn.pack(side=tk.LEFT, padx=5)
        
        # Face recognition button
        face_rec_btn = tk.Button(camera_frame, text="👤 Recognize Face", 
                                command=self.manual_face_recognition,
                                font=('Arial', 10, 'bold'), bg='#9b59b6', fg='white')
        face_rec_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete attendance button
        delete_btn = tk.Button(camera_frame, text="🗑️ Delete Attendance", 
                              command=self.delete_attendance,
                              font=('Arial', 10, 'bold'), bg='#e74c3c', fg='white')
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Attendance table
        table_frame = tk.Frame(attendance_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        columns = ('Student ID', 'Name', 'Status', 'Time', 'Action')
        self.attendance_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)
        
        self.attendance_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load today's attendance
        self.load_attendance_table()
        
        # Bind double-click event to mark attendance
        self.attendance_tree.bind('<Double-1>', self.mark_attendance_from_table)
        
        # Bind right-click for context menu
        self.attendance_tree.bind('<Button-3>', self.show_context_menu)
    
    def toggle_camera(self):
        """Toggle camera for face detection"""
        if not self.camera_running:
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        """Start camera"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Cannot open camera!")
                return
            
            self.camera_running = True
            self.camera_btn.config(text="📹 Stop Camera", bg='#e74c3c')
            self.face_status.config(text="Camera: On - Detecting faces...", fg='green')
            
            # Start face detection
            threading.Thread(target=self.detect_faces, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Camera error: {e}")
    
    def stop_camera(self):
        """Stop camera"""
        self.camera_running = False
        if self.cap:
            self.cap.release()
        
        self.camera_btn.config(text="📹 Start Camera", bg='#3498db')
        self.face_status.config(text="Camera: Off", fg='black')
    
    def detect_faces(self):
        """Face detection loop with automatic attendance marking"""
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        last_detection_time = 0
        detection_cooldown = 3  # 3 seconds cooldown between detections
        
        while self.camera_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                current_time = time.time()
                
                if len(faces) > 0:
                    self.face_status.config(text=f"Camera: On - {len(faces)} face(s) detected!", fg='green')
                    
                    # Auto-mark attendance when face is detected (with cooldown)
                    if current_time - last_detection_time > detection_cooldown:
                        self.auto_mark_attendance()
                        last_detection_time = current_time
                else:
                    self.face_status.config(text="Camera: On - No faces detected", fg='orange')
                
                time.sleep(0.5)
                
            except:
                break
    
    def auto_mark_attendance(self):
        """Automatically mark attendance when face is detected"""
        today = date.today().strftime("%Y-%m-%d")
        if today not in self.attendance:
            self.attendance[today] = {}
        
        current_time = datetime.now().strftime("%H:%M:%S")
        marked_count = 0
        
        # Try to identify specific student if face images are available
        identified_student = self.identify_student_from_camera()
        
        if identified_student:
            # Mark specific identified student
            student_id = identified_student
            if not self.attendance[today].get(student_id, False):
                self.attendance[today][student_id] = True
                self.attendance[today][f"{student_id}_time"] = current_time
                marked_count = 1
                student_name = self.students[student_id]['name']
                
                # Show prominent notification with student name
                self.show_attendance_notification(student_name, student_id, "Present")
                self.face_status.config(text=f"✅ {student_name} identified and marked present!", fg='green')
        else:
            # Fallback: Mark all students as present when face is detected
            for student_id in self.students.keys():
                if not self.attendance[today].get(student_id, False):
                    self.attendance[today][student_id] = True
                    self.attendance[today][f"{student_id}_time"] = current_time
                    marked_count += 1
            if marked_count > 0:
                self.face_status.config(text=f"✅ Auto-marked {marked_count} students as present!", fg='green')
                # Show general notification
                self.show_attendance_notification("Multiple Students", "All", "Present")
        
        if marked_count > 0:
            self.save_attendance()
            self.load_attendance_table()
            # Reset status after 3 seconds
            self.root.after(3000, lambda: self.face_status.config(text="Camera: On - Face detection active", fg='green'))
    
    def identify_student_from_camera(self):
        """Try to identify specific student from camera feed"""
        try:
            if not self.cap or not self.cap.isOpened():
                return None
            
            ret, frame = self.cap.read()
            if not ret:
                return None
            
            # Simple face matching using template matching
            # This is a basic implementation - for production, use face_recognition library
            for student_id, student in self.students.items():
                if student.get('face_image') and os.path.exists(student['face_image']):
                    # Load student's face image
                    student_img = cv2.imread(student['face_image'])
                    if student_img is not None:
                        # Resize both images to same size for comparison
                        student_img = cv2.resize(student_img, (100, 100))
                        frame_resized = cv2.resize(frame, (100, 100))
                        
                        # Convert to grayscale for comparison
                        student_gray = cv2.cvtColor(student_img, cv2.COLOR_BGR2GRAY)
                        frame_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
                        
                        # Simple template matching
                        result = cv2.matchTemplate(frame_gray, student_gray, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, _ = cv2.minMaxLoc(result)
                        
                        # If similarity is high enough, consider it a match
                        if max_val > 0.6:  # Threshold for face matching
                            return student_id
            
            return None
        except Exception as e:
            print(f"Face identification error: {e}")
            return None
    
    def show_attendance_notification(self, student_name, student_id, status):
        """Show prominent notification when attendance is marked"""
        # Create notification window
        notification = tk.Toplevel(self.root)
        notification.title("Attendance Marked")
        notification.geometry("400x200")
        notification.configure(bg='#2c3e50')
        notification.transient(self.root)
        notification.grab_set()
        
        # Center the notification
        notification.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 200, 
            self.root.winfo_rooty() + 150
        ))
        
        # Make it stay on top
        notification.attributes('-topmost', True)
        
        # Main content
        main_frame = tk.Frame(notification, bg='#2c3e50')
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Icon and status
        if status == "Present":
            icon_text = "✅"
            status_color = "#27ae60"
            status_text = "PRESENT"
        elif status == "Identified":
            icon_text = "👤"
            status_color = "#3498db"
            status_text = "IDENTIFIED"
        else:
            icon_text = "❌"
            status_color = "#e74c3c"
            status_text = "ABSENT"
        
        # Icon
        icon_label = tk.Label(main_frame, text=icon_text, font=('Arial', 48), 
                             bg='#2c3e50', fg=status_color)
        icon_label.pack(pady=10)
        
        # Student name
        name_label = tk.Label(main_frame, text=student_name, 
                             font=('Arial', 20, 'bold'), 
                             bg='#2c3e50', fg='white')
        name_label.pack(pady=5)
        
        # Status
        status_label = tk.Label(main_frame, text=f"Marked as {status_text}", 
                               font=('Arial', 16), 
                               bg='#2c3e50', fg=status_color)
        status_label.pack(pady=5)
        
        # Time
        time_label = tk.Label(main_frame, text=f"Time: {datetime.now().strftime('%H:%M:%S')}", 
                             font=('Arial', 12), 
                             bg='#2c3e50', fg='#bdc3c7')
        time_label.pack(pady=5)
        
        # Auto-close after 3 seconds
        notification.after(3000, notification.destroy)
        
        # Add close button
        close_btn = tk.Button(main_frame, text="Close", 
                             command=notification.destroy,
                             font=('Arial', 10), bg='#34495e', fg='white')
        close_btn.pack(pady=10)
    
    def load_attendance_table(self):
        """Load attendance table"""
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        today = date.today().strftime("%Y-%m-%d")
        today_attendance = self.attendance.get(today, {})
        
        for student_id, student in self.students.items():
            status = "Present" if today_attendance.get(student_id, False) else "Absent"
            time_str = today_attendance.get(f"{student_id}_time", "")
            
            self.attendance_tree.insert('', 'end', values=(
                student_id,
                student['name'],
                status,
                time_str,
                "Mark Present" if status == "Absent" else "Mark Absent"
            ))
    
    def mark_attendance_from_table(self, event):
        """Mark attendance when double-clicking on table row"""
        selection = self.attendance_tree.selection()
        if selection:
            item = self.attendance_tree.item(selection[0])
            values = item['values']
            student_id = values[0]
            student_name = values[1]
            current_status = values[2]
            
            # Toggle attendance status
            new_status = "Absent" if current_status == "Present" else "Present"
            
            # Update attendance data
            today = date.today().strftime("%Y-%m-%d")
            if today not in self.attendance:
                self.attendance[today] = {}
            
            if new_status == "Present":
                self.attendance[today][student_id] = True
                self.attendance[today][f"{student_id}_time"] = datetime.now().strftime("%H:%M:%S")
                # Show notification instead of messagebox
                self.show_attendance_notification(student_name, student_id, "Present")
            else:
                self.attendance[today][student_id] = False
                self.attendance[today][f"{student_id}_time"] = ""
                # Show notification instead of messagebox
                self.show_attendance_notification(student_name, student_id, "Absent")
            
            # Save attendance data
            self.save_attendance()
            
            # Reload table
            self.load_attendance_table()
    
    def mark_all_present(self):
        """Mark all students as present for today"""
        today = date.today().strftime("%Y-%m-%d")
        if today not in self.attendance:
            self.attendance[today] = {}
        
        current_time = datetime.now().strftime("%H:%M:%S")
        marked_count = 0
        
        for student_id in self.students.keys():
            if not self.attendance[today].get(student_id, False):  # Only mark if not already present
                self.attendance[today][student_id] = True
                self.attendance[today][f"{student_id}_time"] = current_time
                marked_count += 1
        
        if marked_count > 0:
            self.save_attendance()
            self.load_attendance_table()
            messagebox.showinfo("Success", f"Marked {marked_count} students as present!")
        else:
            messagebox.showinfo("Info", "All students are already marked as present!")
    
    def manual_face_recognition(self):
        """Manually trigger face recognition"""
        if not self.camera_running:
            messagebox.showwarning("Warning", "Please start the camera first!")
            return
        
        identified_student = self.identify_student_from_camera()
        
        if identified_student:
            student_name = self.students[identified_student]['name']
            
            # Show identification notification
            self.show_attendance_notification(student_name, identified_student, "Identified")
            
            # Ask if user wants to mark attendance
            result = messagebox.askyesno("Mark Attendance", f"Mark {student_name} as present?")
            if result:
                self.mark_single_attendance(identified_student, student_name, "Present")
                # Show attendance marked notification
                self.show_attendance_notification(student_name, identified_student, "Present")
        else:
            messagebox.showinfo("Face Recognition", "No student face recognized. Please ensure:\n- Good lighting\n- Face is clearly visible\n- Student has a face image in the system")
    
    def delete_attendance(self):
        """Delete attendance records with multiple options"""
        # Create delete options dialog
        delete_dialog = tk.Toplevel(self.root)
        delete_dialog.title("Delete Attendance")
        delete_dialog.geometry("400x300")
        delete_dialog.configure(bg='white')
        delete_dialog.transient(self.root)
        delete_dialog.grab_set()
        delete_dialog.resizable(False, False)
        
        # Center dialog
        delete_dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 100, 
            self.root.winfo_rooty() + 100
        ))
        
        # Title
        tk.Label(delete_dialog, text="🗑️ Delete Attendance Records", 
                font=('Arial', 16, 'bold'), bg='white').pack(pady=20)
        
        # Warning message
        warning_frame = tk.Frame(delete_dialog, bg='#fff3cd', relief='raised', bd=2)
        warning_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(warning_frame, text="⚠️ Warning: This action cannot be undone!", 
                font=('Arial', 12, 'bold'), bg='#fff3cd', fg='#856404').pack(pady=10)
        
        # Options frame
        options_frame = tk.Frame(delete_dialog, bg='white')
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Option 1: Delete today's attendance
        today = date.today().strftime("%Y-%m-%d")
        today_count = len([a for a in self.attendance.get(today, {}).values() if a])
        
        today_btn = tk.Button(options_frame, 
                             text=f"📅 Delete Today's Attendance ({today_count} records)",
                             command=lambda: self.confirm_delete_today(delete_dialog),
                             font=('Arial', 12, 'bold'), bg='#f39c12', fg='white',
                             width=35, height=2)
        today_btn.pack(pady=5)
        
        # Option 2: Delete all attendance
        total_records = sum(len([a for a in day_attendance.values() if a]) 
                           for day_attendance in self.attendance.values())
        
        all_btn = tk.Button(options_frame, 
                           text=f"🗂️ Delete All Attendance ({total_records} records)",
                           command=lambda: self.confirm_delete_all(delete_dialog),
                           font=('Arial', 12, 'bold'), bg='#e74c3c', fg='white',
                           width=35, height=2)
        all_btn.pack(pady=5)
        
        # Option 3: Delete specific date
        date_btn = tk.Button(options_frame, 
                            text="📆 Delete Specific Date",
                            command=lambda: self.delete_specific_date(delete_dialog),
                            font=('Arial', 12, 'bold'), bg='#9b59b6', fg='white',
                            width=35, height=2)
        date_btn.pack(pady=5)
        
        # Cancel button
        cancel_btn = tk.Button(delete_dialog, text="❌ Cancel", 
                              command=delete_dialog.destroy,
                              font=('Arial', 12, 'bold'), bg='#95a5a6', fg='white',
                              width=15, height=2)
        cancel_btn.pack(pady=20)
    
    def confirm_delete_today(self, parent_dialog):
        """Confirm deletion of today's attendance"""
        today = date.today().strftime("%Y-%m-%d")
        today_count = len([a for a in self.attendance.get(today, {}).values() if a])
        
        if today_count == 0:
            messagebox.showinfo("Info", "No attendance records found for today!")
            parent_dialog.destroy()
            return
        
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete today's attendance?\n\n"
                                   f"Date: {today}\n"
                                   f"Records: {today_count}\n\n"
                                   f"This action cannot be undone!")
        
        if result:
            # Delete today's attendance
            if today in self.attendance:
                del self.attendance[today]
                self.save_attendance()
                self.load_attendance_table()
                messagebox.showinfo("Success", f"Deleted {today_count} attendance records for today!")
                parent_dialog.destroy()
    
    def confirm_delete_all(self, parent_dialog):
        """Confirm deletion of all attendance"""
        total_records = sum(len([a for a in day_attendance.values() if a]) 
                           for day_attendance in self.attendance.values())
        
        if total_records == 0:
            messagebox.showinfo("Info", "No attendance records found!")
            parent_dialog.destroy()
            return
        
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete ALL attendance records?\n\n"
                                   f"Total Records: {total_records}\n"
                                   f"All Dates: {len(self.attendance)} days\n\n"
                                   f"This action cannot be undone!")
        
        if result:
            # Delete all attendance
            self.attendance = {}
            self.save_attendance()
            self.load_attendance_table()
            messagebox.showinfo("Success", f"Deleted all {total_records} attendance records!")
            parent_dialog.destroy()
    
    def delete_specific_date(self, parent_dialog):
        """Delete attendance for a specific date"""
        parent_dialog.destroy()
        
        # Create date selection dialog
        date_dialog = tk.Toplevel(self.root)
        date_dialog.title("Select Date to Delete")
        date_dialog.geometry("350x200")
        date_dialog.configure(bg='white')
        date_dialog.transient(self.root)
        date_dialog.grab_set()
        date_dialog.resizable(False, False)
        
        # Center dialog
        date_dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 150, 
            self.root.winfo_rooty() + 150
        ))
        
        tk.Label(date_dialog, text="📆 Select Date to Delete", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=20)
        
        # Date selection
        date_frame = tk.Frame(date_dialog, bg='white')
        date_frame.pack(pady=20)
        
        tk.Label(date_frame, text="Date (YYYY-MM-DD):", 
                font=('Arial', 12), bg='white').pack()
        
        date_entry = tk.Entry(date_frame, font=('Arial', 12), width=15)
        date_entry.pack(pady=5)
        date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        # Available dates list
        available_dates = list(self.attendance.keys())
        if available_dates:
            tk.Label(date_dialog, text="Available dates:", 
                    font=('Arial', 10), bg='white').pack(pady=5)
            
            dates_text = ", ".join(sorted(available_dates)[-5:])  # Show last 5 dates
            tk.Label(date_dialog, text=dates_text, 
                    font=('Arial', 9), bg='white', fg='#666').pack()
        
        # Buttons
        btn_frame = tk.Frame(date_dialog, bg='white')
        btn_frame.pack(pady=20)
        
        def delete_selected_date():
            selected_date = date_entry.get().strip()
            
            if not selected_date:
                messagebox.showerror("Error", "Please enter a date!")
                return
            
            if selected_date not in self.attendance:
                messagebox.showerror("Error", f"No attendance records found for {selected_date}!")
                return
            
            # Count records for this date
            date_count = len([a for a in self.attendance[selected_date].values() if a])
            
            result = messagebox.askyesno("Confirm Delete", 
                                       f"Delete attendance for {selected_date}?\n\n"
                                       f"Records: {date_count}\n\n"
                                       f"This action cannot be undone!")
            
            if result:
                del self.attendance[selected_date]
                self.save_attendance()
                self.load_attendance_table()
                messagebox.showinfo("Success", f"Deleted {date_count} records for {selected_date}!")
                date_dialog.destroy()
        
        tk.Button(btn_frame, text="🗑️ Delete", command=delete_selected_date,
                 font=('Arial', 12, 'bold'), bg='#e74c3c', fg='white',
                 width=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="❌ Cancel", command=date_dialog.destroy,
                 font=('Arial', 12), bg='#95a5a6', fg='white',
                 width=10).pack(side=tk.LEFT, padx=5)
    
    def show_context_menu(self, event):
        """Show right-click context menu for attendance marking"""
        selection = self.attendance_tree.selection()
        if selection:
            item = self.attendance_tree.item(selection[0])
            values = item['values']
            student_id = values[0]
            student_name = values[1]
            current_status = values[2]
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            
            if current_status == "Absent":
                context_menu.add_command(label=f"✅ Mark {student_name} as Present", 
                                       command=lambda: self.mark_single_attendance(student_id, student_name, "Present"))
            else:
                context_menu.add_command(label=f"❌ Mark {student_name} as Absent", 
                                       command=lambda: self.mark_single_attendance(student_id, student_name, "Absent"))
            
            context_menu.add_separator()
            context_menu.add_command(label="📊 View Student Details", 
                                   command=lambda: self.view_student_details(student_id))
            
            # Show context menu
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def mark_single_attendance(self, student_id, student_name, status):
        """Mark attendance for a single student"""
        today = date.today().strftime("%Y-%m-%d")
        if today not in self.attendance:
            self.attendance[today] = {}
        
        if status == "Present":
            self.attendance[today][student_id] = True
            self.attendance[today][f"{student_id}_time"] = datetime.now().strftime("%H:%M:%S")
            # Show notification instead of messagebox
            self.show_attendance_notification(student_name, student_id, "Present")
        else:
            self.attendance[today][student_id] = False
            self.attendance[today][f"{student_id}_time"] = ""
            # Show notification instead of messagebox
            self.show_attendance_notification(student_name, student_id, "Absent")
        
        # Save and reload
        self.save_attendance()
        self.load_attendance_table()
    
    def view_student_details(self, student_id):
        """View student details"""
        if student_id in self.students:
            student = self.students[student_id]
            details = f"""
Student Details:
ID: {student_id}
Name: {student['name']}
Email: {student['email']}
Phone: {student['phone']}
Course: {student['course']}
Year: {student['year']}
Face Image: {'Yes' if student.get('face_image') else 'No'}
            """
            messagebox.showinfo("Student Details", details)
    
    def show_reports(self):
        """Show reports section"""
        self.clear_window()
        self.create_header()
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Navigation
        self.create_navigation(content_frame)
        
        # Reports frame
        reports_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=2)
        reports_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Title
        tk.Label(reports_frame, text="Reports & Analytics", font=('Arial', 16, 'bold'), 
                bg='white').pack(pady=20)
        
        # Report options
        options_frame = tk.Frame(reports_frame, bg='white')
        options_frame.pack(pady=20)
        
        report_buttons = [
            ("📊 Daily Report", self.generate_daily_report),
            ("📈 Weekly Report", self.generate_weekly_report),
            ("📋 Monthly Report", self.generate_monthly_report),
            ("👥 Student Report", self.generate_student_report),
            ("📁 Export CSV", self.export_csv)
        ]
        
        for i, (text, command) in enumerate(report_buttons):
            btn = tk.Button(options_frame, text=text, command=command,
                           font=('Arial', 12, 'bold'), bg='#3498db', fg='white',
                           width=20, height=2)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
    
    def generate_daily_report(self):
        """Generate daily attendance report"""
        today = date.today().strftime("%Y-%m-%d")
        filename = f"daily_report_{today}.csv"
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Student ID', 'Name', 'Status', 'Time'])
            
            today_attendance = self.attendance.get(today, {})
            for student_id, student in self.students.items():
                status = "Present" if today_attendance.get(student_id, False) else "Absent"
                time_str = today_attendance.get(f"{student_id}_time", "")
                writer.writerow([student_id, student['name'], status, time_str])
        
        messagebox.showinfo("Success", f"Daily report saved as {filename}")
    
    def generate_weekly_report(self):
        """Generate weekly report"""
        messagebox.showinfo("Info", "Weekly report feature coming soon!")
    
    def generate_monthly_report(self):
        """Generate monthly report"""
        messagebox.showinfo("Info", "Monthly report feature coming soon!")
    
    def generate_student_report(self):
        """Generate individual student report"""
        messagebox.showinfo("Info", "Student report feature coming soon!")
    
    def export_csv(self):
        """Export all data to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Date', 'Student ID', 'Name', 'Status', 'Time'])
                
                for date_str, day_attendance in self.attendance.items():
                    for student_id, student in self.students.items():
                        status = "Present" if day_attendance.get(student_id, False) else "Absent"
                        time_str = day_attendance.get(f"{student_id}_time", "")
                        writer.writerow([date_str, student_id, student['name'], status, time_str])
            
            messagebox.showinfo("Success", f"Data exported to {filename}")
    
    def show_settings(self):
        """Show settings"""
        self.clear_window()
        self.create_header()
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Navigation
        self.create_navigation(content_frame)
        
        # Settings frame
        settings_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=2)
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(settings_frame, text="System Settings", font=('Arial', 16, 'bold'), 
                bg='white').pack(pady=20)
        
        # Settings options
        options_frame = tk.Frame(settings_frame, bg='white')
        options_frame.pack(pady=20)
        
        setting_buttons = [
            ("👤 User Management", self.manage_users),
            ("🔧 System Configuration", self.system_config),
            ("📊 Database Management", self.database_management),
            ("ℹ️ About", self.show_about)
        ]
        
        for i, (text, command) in enumerate(setting_buttons):
            btn = tk.Button(options_frame, text=text, command=command,
                           font=('Arial', 12, 'bold'), bg='#95a5a6', fg='white',
                           width=20, height=2)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
    
    def manage_users(self):
        messagebox.showinfo("Info", "User management feature coming soon!")
    
    def system_config(self):
        messagebox.showinfo("Info", "System configuration feature coming soon!")
    
    def database_management(self):
        messagebox.showinfo("Info", "Database management feature coming soon!")
    
    def show_camera_preview(self, cap, camera_label):
        """Show camera preview in label"""
        def update_preview():
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    # Convert BGR to RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Resize frame
                    frame = cv2.resize(frame, (300, 300))
                    # Convert to PIL Image
                    from PIL import Image, ImageTk
                    img = Image.fromarray(frame)
                    photo = ImageTk.PhotoImage(img)
                    camera_label.configure(image=photo, text="")
                    camera_label.image = photo
                    # Schedule next update
                    camera_label.after(30, update_preview)
        
        update_preview()
    
    def capture_face_image(self, cap, camera_dialog, selected_image_path, img_label):
        """Capture face image from camera"""
        try:
            ret, frame = cap.read()
            if ret:
                # Save captured image
                import tempfile
                import os
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                cv2.imwrite(temp_file.name, frame)
                selected_image_path[0] = temp_file.name
                
                # Update preview
                from PIL import Image, ImageTk
                img = Image.open(temp_file.name)
                img = img.resize((80, 80), Image.Resampling.LANCZOS)  # Smaller preview
                photo = ImageTk.PhotoImage(img)
                img_label.configure(image=photo, text="")
                img_label.image = photo
                
                # Close camera dialog
                cap.release()
                camera_dialog.destroy()
                
                # Show success message
                messagebox.showinfo("Success", "Face image captured successfully!")
                
                # Force dialog to update and maintain layout
                dialog = img_label.master.master.master  # Navigate to main dialog
                dialog.update_idletasks()
                dialog.lift()
                dialog.focus_force()
                
            else:
                messagebox.showerror("Error", "Could not capture image!")
        except Exception as e:
            messagebox.showerror("Error", f"Capture error: {e}")

    def show_about(self):
        about_text = """
Smart Attendance Management System
Version 1.0

Features:
• User Authentication
• Student Management
• Attendance Tracking
• Face Detection
• Report Generation
• Data Export
• Face Image Upload/Capture

Developed with Python & Tkinter
        """
        messagebox.showinfo("About", about_text)
    
    def create_header(self):
        """Create header with navigation"""
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Smart Attendance Management System", 
                              font=('Arial', 18, 'bold'), bg='#2c3e50', fg='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        user_label = tk.Label(header_frame, text=f"Welcome, {self.users[self.current_user]['name']}", 
                             font=('Arial', 12), bg='#2c3e50', fg='white')
        user_label.pack(side=tk.RIGHT, padx=20, pady=20)
        
        logout_btn = tk.Button(header_frame, text="Logout", command=self.logout,
                              font=('Arial', 10), bg='#e74c3c', fg='white')
        logout_btn.pack(side=tk.RIGHT, padx=10, pady=20)
    
    def create_navigation(self, parent):
        """Create navigation buttons"""
        nav_frame = tk.Frame(parent, bg='#f0f0f0')
        nav_frame.pack(fill=tk.X, pady=10)
        
        buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("👥 Students", self.show_students),
            ("📝 Attendance", self.show_attendance),
            ("📈 Reports", self.show_reports),
            ("⚙️ Settings", self.show_settings)
        ]
        
        for text, command in buttons:
            btn = tk.Button(nav_frame, text=text, command=command,
                           font=('Arial', 11, 'bold'), bg='#3498db', fg='white',
                           width=15, height=2)
            btn.pack(side=tk.LEFT, padx=5)
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def logout(self):
        """Logout user"""
        self.current_user = None
        self.show_login()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = FullAttendanceSystem()
    app.run()
image.png