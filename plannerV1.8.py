#!/usr/bin/env python3
"""
Pop!_OS Study Planner - Stable Minimal Version
Improved with stable display and better UI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import time
from datetime import datetime

# Simple default schedule
DEFAULT_SCHEDULE = {
    "Saturday": [
        {"time": "06:00-10:00", "subject": "Electronics 2", "duration": "2h", "completed": False},
        {"time": "14:00-18:00", "subject": "Control Systems", "duration": "1.5h", "completed": False},
        {"time": "19:00-23:00", "subject": "Tests + English", "duration": "1.5h", "completed": False}
    ],
    "Sunday": [
        {"time": "06:00-10:00", "subject": "Circuits", "duration": "2h", "completed": False},
        {"time": "14:00-18:00", "subject": "Electrical Machines", "duration": "1.5h", "completed": False},
        {"time": "19:00-23:00", "subject": "Exercises", "duration": "1.5h", "completed": False}
    ],
    "Monday": [
        {"time": "06:00-10:00", "subject": "Electronics 1", "duration": "2h", "completed": False},
        {"time": "14:00-18:00", "subject": "Mathematics", "duration": "1.5h", "completed": False},
        {"time": "19:00-23:00", "subject": "University Projects", "duration": "1.5h", "completed": False}
    ],
    "Tuesday": [
        {"time": "06:00-10:00", "subject": "Diff. Equations", "duration": "1.5h", "completed": False},
        {"time": "14:00-18:00", "subject": "Control Systems", "duration": "1.5h", "completed": False},
        {"time": "19:00-23:00", "subject": "Mixed Tests", "duration": "1.5h", "completed": False}
    ],
    "Wednesday": [
        {"time": "06:00-10:00", "subject": "Electronics 2", "duration": "2h", "completed": False},
        {"time": "14:00-18:00", "subject": "Digital Logic", "duration": "0.5h", "completed": False},
        {"time": "19:00-23:00", "subject": "English", "duration": "1.5h", "completed": False}
    ],
    "Thursday": [
        {"time": "06:00-10:00", "subject": "Full Mock Exam", "duration": "2.5h", "completed": False},
        {"time": "14:00-18:00", "subject": "Exam Analysis", "duration": "1.5h", "completed": False},
        {"time": "19:00-23:00", "subject": "Catch-up", "duration": "1h", "completed": False}
    ],
    "Friday": [
        {"time": "06:00-10:00", "subject": "Weekly Review", "duration": "2h", "completed": False},
        {"time": "14:00-18:00", "subject": "Rest", "duration": "-", "completed": False},
        {"time": "19:00-23:00", "subject": "Planning", "duration": "1h", "completed": False}
    ]
}

class StudyPlanner:
    def __init__(self):
        # Clean up any existing lock files first
        self.cleanup_lock_files()
        
        self.home_dir = os.path.expanduser("~")
        self.schedule_file = os.path.join(self.home_dir, ".study_planner_schedule.json")
        self.lock_file = "/tmp/study_planner.lock"
        
        # Check if already running
        if self.is_already_running():
            print("Study Planner is already running!")
            return
        
        self.schedule = self.load_schedule()
        self.current_day = None
        self.task_widgets = {}  # Store task widgets to prevent blinking
        self.setup_gui()
        
    def cleanup_lock_files(self):
        """Clean up any existing lock files"""
        lock_files = [
            "/tmp/study_planner.lock",
            "/tmp/study_planner_doom.lock",
            "/tmp/study_planner_v1.6.lock"
        ]
        for lock_file in lock_files:
            try:
                if os.path.exists(lock_file):
                    os.remove(lock_file)
            except:
                pass
    
    def is_already_running(self):
        """Check if another instance is running"""
        try:
            if os.path.exists(self.lock_file):
                # Check if the process is actually running
                with open(self.lock_file, 'r') as f:
                    pid = f.read().strip()
                try:
                    # Check if process exists
                    os.kill(int(pid), 0)
                    return True  # Process is running
                except (OSError, ValueError):
                    # Process doesn't exist, remove stale lock file
                    os.remove(self.lock_file)
                    return False
            return False
        except:
            return False
    
    def create_lock_file(self):
        """Create lock file"""
        try:
            with open(self.lock_file, 'w') as f:
                f.write(str(os.getpid()))
        except:
            pass
    
    def remove_lock_file(self):
        """Remove lock file"""
        try:
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
        except:
            pass
    
    def load_schedule(self):
        """Load schedule from file"""
        try:
            if os.path.exists(self.schedule_file):
                with open(self.schedule_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading schedule: {e}")
        return DEFAULT_SCHEDULE.copy()
    
    def save_schedule(self):
        """Save schedule to file"""
        try:
            with open(self.schedule_file, 'w') as f:
                json.dump(self.schedule, f, indent=2)
        except Exception as e:
            print(f"Error saving schedule: {e}")
    
    def setup_gui(self):
        """Setup the main GUI"""
        self.root = tk.Tk()
        self.root.title("Study Planner")
        self.root.geometry("450x650+100+100")
        self.root.configure(bg='#2b2b2b')
        
        # Make sure we clean up on exit
        self.root.protocol("WM_DELETE_WINDOW", self.safe_exit)
        
        # Create lock file
        self.create_lock_file()
        
        # Configure styles for prettier buttons
        self.configure_styles()
        
        self.create_widgets()
        self.update_display()
        
    def configure_styles(self):
        """Configure ttk styles for better looking buttons"""
        style = ttk.Style()
        
        # Configure button styles
        style.configure('Modern.TButton',
                       background='#4a6baf',
                       foreground='white',
                       borderwidth=1,
                       focusthickness=3,
                       focuscolor='none',
                       font=('Arial', 10, 'bold'),
                       padding=(15, 8))
        
        style.map('Modern.TButton',
                 background=[('active', '#5a7bbf'), ('pressed', '#3a5b9f')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        style.configure('Success.TButton',
                       background='#2e7d32',
                       foreground='white')
        
        style.map('Success.TButton',
                 background=[('active', '#3e8d42'), ('pressed', '#1e6d22')])
        
        style.configure('Danger.TButton',
                       background='#c62828',
                       foreground='white')
        
        style.map('Danger.TButton',
                 background=[('active', '#d63838'), ('pressed', '#b61818')])
        
        # Configure progress bar style
        style.configure("Custom.Horizontal.TProgressbar",
                       background='#4a6baf',
                       troughcolor='#3b3b3b',
                       borderwidth=0,
                       lightcolor='#4a6baf',
                       darkcolor='#4a6baf')
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#2b2b2b')
        header_frame.pack(fill='x', pady=(0, 10))
        
        self.title_label = tk.Label(header_frame, text="📚 Study Planner", 
                                   font=('Arial', 18, 'bold'), 
                                   bg='#2b2b2b', fg='#ffffff')
        self.title_label.pack()
        
        self.day_label = tk.Label(header_frame, font=('Arial', 11), 
                                 bg='#2b2b2b', fg='#cccccc')
        self.day_label.pack()
        
        # Time display
        time_frame = tk.Frame(main_frame, bg='#2b2b2b')
        time_frame.pack(fill='x', pady=5)
        
        self.time_label = tk.Label(time_frame, font=('Arial', 16, 'bold'), 
                                  bg='#2b2b2b', fg='#88ccff')
        self.time_label.pack()
        
        # Progress section
        progress_section = tk.Frame(main_frame, bg='#2b2b2b')
        progress_section.pack(fill='x', pady=15)
        
        # Progress label
        self.progress_label = tk.Label(progress_section, font=('Arial', 11, 'bold'), 
                                      bg='#2b2b2b', fg='#ffffff')
        self.progress_label.pack(anchor='w', pady=(0, 5))
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_section, orient='horizontal', 
                                       length=400, mode='determinate',
                                       style="Custom.Horizontal.TProgressbar")
        self.progress.pack(fill='x', pady=5)
        
        # Tasks section
        tasks_section = tk.Frame(main_frame, bg='#2b2b2b')
        tasks_section.pack(fill='both', expand=True, pady=10)
        
        # Tasks label with nice styling
        tasks_header = tk.Frame(tasks_section, bg='#3b3b3b', relief='raised', bd=1)
        tasks_header.pack(fill='x', pady=(0, 8))
        
        tk.Label(tasks_header, text="Today's Tasks", font=('Arial', 12, 'bold'), 
                bg='#3b3b3b', fg='#ffffff', padx=10, pady=8).pack()
        
        # Tasks container with scrollbar
        tasks_container_frame = tk.Frame(tasks_section, bg='#2b2b2b')
        tasks_container_frame.pack(fill='both', expand=True)
        
        # Create a canvas and scrollbar for tasks
        self.canvas = tk.Canvas(tasks_container_frame, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(tasks_container_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#2b2b2b')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Control buttons frame
        control_frame = tk.Frame(main_frame, bg='#2b2b2b')
        control_frame.pack(fill='x', pady=15)
        
        # Button container for better spacing
        button_container = tk.Frame(control_frame, bg='#2b2b2b')
        button_container.pack(fill='x')
        
        # Edit button
        edit_btn = ttk.Button(button_container, text="✏️ Edit Tasks", 
                             command=self.edit_tasks, style='Modern.TButton')
        edit_btn.pack(side='left', padx=(0, 10), fill='x', expand=True)
        
        # Refresh button
        refresh_btn = ttk.Button(button_container, text="🔄 Refresh", 
                                command=self.update_display, style='Modern.TButton')
        refresh_btn.pack(side='left', padx=(0, 10), fill='x', expand=True)
        
        # Exit button
        exit_btn = ttk.Button(button_container, text="🚪 Exit", 
                             command=self.safe_exit, style='Danger.TButton')
        exit_btn.pack(side='left', fill='x', expand=True)
        
        # Store the tasks container reference
        self.tasks_container = self.scrollable_frame
    
    def update_display(self):
        """Update the display with current information"""
        # Update time
        current_time = datetime.now()
        time_str = current_time.strftime("%H:%M:%S")
        date_str = current_time.strftime("%A, %B %d")
        day_name = current_time.strftime("%A")
        
        self.time_label.config(text=time_str)
        self.day_label.config(text=f"{date_str}")
        
        # Only update tasks if day changed or first run
        if day_name != self.current_day:
            self.current_day = day_name
            self.update_tasks_display(day_name)
        
        # Update progress (always update this)
        self.update_progress(day_name)
        
        # Schedule next update
        self.root.after(1000, self.update_display)
    
    def update_progress(self, day_name):
        """Update progress bar without affecting tasks display"""
        tasks = self.schedule.get(day_name, [])
        completed = sum(1 for task in tasks if task.get('completed', False))
        total = len(tasks)
        
        progress_text = f"Progress: {completed}/{total} tasks completed"
        self.progress_label.config(text=progress_text)
        
        if total > 0:
            progress = (completed / total) * 100
            self.progress['value'] = progress
        else:
            self.progress['value'] = 0
    
    def update_tasks_display(self, day_name):
        """Update the tasks display only when day changes"""
        # Clear existing task widgets
        for widget in self.tasks_container.winfo_children():
            widget.destroy()
        
        self.task_widgets.clear()
        
        tasks = self.schedule.get(day_name, [])
        
        if not tasks:
            no_tasks_label = tk.Label(self.tasks_container, text="🎉 No tasks for today! Enjoy your free time!",
                                     font=('Arial', 11), bg='#2b2b2b', fg='#888888', pady=20)
            no_tasks_label.pack(fill='x', pady=10)
            return
        
        # Create task widgets
        for i, task in enumerate(tasks):
            self.create_task_widget(i, task)
    
    def create_task_widget(self, index, task):
        """Create a stable widget for a single task"""
        task_frame = tk.Frame(self.tasks_container, bg='#3b3b3b', relief='raised', bd=1)
        task_frame.pack(fill='x', pady=3, padx=2)
        
        # Store reference
        self.task_widgets[index] = task_frame
        
        # Completion checkbox with better styling
        is_completed = task.get('completed', False)
        var = tk.BooleanVar(value=is_completed)
        
        # Custom checkbox using Label for better appearance
        check_label = tk.Label(task_frame, text="✓" if is_completed else "○", 
                              font=('Arial', 14), bg='#3b3b3b', 
                              fg='#4CAF50' if is_completed else '#666666',
                              cursor="hand2")
        check_label.pack(side='left', padx=8)
        check_label.var = var
        check_label.task_index = index
        check_label.bind("<Button-1>", lambda e, idx=index: self.toggle_task(idx))
        
        # Task info with better formatting
        task_text = f"{task['time']} - {task['subject']} ({task['duration']})"
        color = '#888888' if is_completed else '#ffffff'
        font_style = ('Arial', 10, 'overstrike' if is_completed else 'normal')
        
        task_label = tk.Label(task_frame, text=task_text, font=font_style,
                             bg='#3b3b3b', fg=color, anchor='w', justify='left')
        task_label.pack(side='left', fill='x', expand=True, padx=5)
        
        # Store references for updating
        task_frame.check_label = check_label
        task_frame.task_label = task_label
    
    def toggle_task(self, task_index):
        """Toggle task completion status with smooth update"""
        day_name = datetime.now().strftime("%A")
        if day_name in self.schedule and 0 <= task_index < len(self.schedule[day_name]):
            # Toggle completion status
            current = self.schedule[day_name][task_index]['completed']
            self.schedule[day_name][task_index]['completed'] = not current
            
            # Update the specific task widget without redrawing everything
            if task_index in self.task_widgets:
                task_frame = self.task_widgets[task_index]
                is_completed = not current
                
                # Update checkbox
                task_frame.check_label.config(
                    text="✓" if is_completed else "○",
                    fg='#4CAF50' if is_completed else '#666666'
                )
                
                # Update task text
                task_text = f"{self.schedule[day_name][task_index]['time']} - {self.schedule[day_name][task_index]['subject']} ({self.schedule[day_name][task_index]['duration']})"
                color = '#888888' if is_completed else '#ffffff'
                font_style = ('Arial', 10, 'overstrike' if is_completed else 'normal')
                
                task_frame.task_label.config(
                    text=task_text,
                    fg=color,
                    font=font_style
                )
            
            self.save_schedule()
            self.update_progress(day_name)  # Only update progress, not entire display
    
    def edit_tasks(self):
        """Open simple task editor"""
        day_name = datetime.now().strftime("%A")
        tasks = self.schedule.get(day_name, [])
        
        # Create simple edit window
        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Edit Tasks for {day_name}")
        edit_win.geometry("500x400")
        edit_win.configure(bg='#2b2b2b')
        edit_win.transient(self.root)
        edit_win.grab_set()
        
        # Center the window
        edit_win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - edit_win.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - edit_win.winfo_height()) // 2
        edit_win.geometry(f"+{x}+{y}")
        
        # Instructions
        header_frame = tk.Frame(edit_win, bg='#3b3b3b', relief='raised', bd=1)
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text=f"✏️ Editing Tasks for {day_name}", 
                font=('Arial', 12, 'bold'), bg='#3b3b3b', fg='white', 
                padx=10, pady=8).pack()
        
        # Text area for editing
        text_frame = tk.Frame(edit_win, bg='#2b2b2b')
        text_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        text_area = tk.Text(text_frame, width=60, height=15, bg='#1b1b1b', fg='white',
                           font=('Arial', 10), insertbackground='white')
        text_area.pack(fill='both', expand=True)
        
        # Populate with current tasks
        for task in tasks:
            status = "[✓]" if task['completed'] else "[○]"
            text_area.insert('end', 
                           f"{status} {task['time']} | {task['subject']} | {task['duration']}\n")
        
        # Button frame
        button_frame = tk.Frame(edit_win, bg='#2b2b2b')
        button_frame.pack(fill='x', pady=10)
        
        def save_changes():
            try:
                # Simple parsing of changes
                content = text_area.get('1.0', 'end-1c')
                new_tasks = []
                
                for line in content.split('\n'):
                    line = line.strip()
                    if line and '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            status_part = parts[0].strip()
                            time_part = parts[1].strip()
                            subject_part = parts[2].strip()
                            duration_part = parts[3].strip() if len(parts) > 3 else "1h"
                            
                            completed = '✓' in status_part
                            
                            new_tasks.append({
                                'time': time_part,
                                'subject': subject_part,
                                'duration': duration_part,
                                'completed': completed
                            })
                
                self.schedule[day_name] = new_tasks
                self.save_schedule()
                self.current_day = None  # Force refresh of tasks display
                self.update_display()
                edit_win.destroy()
                messagebox.showinfo("Success", "Tasks updated successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not save changes: {e}")
        
        # Save button with modern style
        save_btn = ttk.Button(button_frame, text="💾 Save Changes", 
                             command=save_changes, style='Success.TButton')
        save_btn.pack(side='right', padx=5)
        
        # Cancel button
        cancel_btn = ttk.Button(button_frame, text="❌ Cancel", 
                               command=edit_win.destroy, style='Danger.TButton')
        cancel_btn.pack(side='right', padx=5)
    
    def safe_exit(self):
        """Safely exit the application"""
        self.remove_lock_file()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        if hasattr(self, 'root'):
            try:
                self.root.mainloop()
            except Exception as e:
                print(f"Error: {e}")
            finally:
                self.remove_lock_file()

def main():
    """Main function"""
    print("Starting Study Planner...")
    print("Press Ctrl+C in terminal to exit")
    
    planner = StudyPlanner()
    
    # Only run if planner was successfully created
    if hasattr(planner, 'root'):
        planner.run()
    else:
        print("Another instance is already running!")

if __name__ == "__main__":
    main()
