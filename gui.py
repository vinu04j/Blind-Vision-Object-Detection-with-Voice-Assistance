import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import threading

class BlindVisionGUI:
    def __init__(self, app):
        """Initialize GUI"""
        self.app = app
        self.root = tk.Tk()
        self.root.title("Blind Vision Guide - Object Detection with Voice Navigation")
        self.root.geometry("1000x700")
        
        # Configure style
        self.root.configure(bg='#f0f0f0')
        
        # Store current frame for camera display
        self.current_frame = None
        self.photo = None
        
        # Create main frame
        self.create_widgets()
        
    def create_widgets(self):
        """Create GUI widgets"""
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="Blind Vision Guide",
            font=("Arial", 20, "bold"),
            bg='#f0f0f0',
            fg='#333'
        )
        title_label.pack(pady=10)
        
        # Subtitle
        subtitle_label = tk.Label(
            main_container,
            text="Object Detection with Voice Navigation",
            font=("Arial", 12),
            bg='#f0f0f0',
            fg='#666'
        )
        subtitle_label.pack()
        
        # Create horizontal layout for camera and controls
        content_frame = tk.Frame(main_container, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # ===== LEFT SIDE: CAMERA FEED =====
        camera_frame = ttk.LabelFrame(content_frame, text="📹 Live Camera Feed", padding=10)
        camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Camera display label
        self.camera_label = tk.Label(
            camera_frame,
            bg='#000000',
            width=40,
            height=20,
            fg='#ffffff'
        )
        self.camera_label.pack(fill=tk.BOTH, expand=True)
        
        # ===== RIGHT SIDE: CONTROLS AND INFO =====
        control_frame = tk.Frame(content_frame, bg='#f0f0f0')
        control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        # Language Selection Frame
        lang_frame = ttk.LabelFrame(control_frame, text="Select Language", padding=10)
        lang_frame.pack(padx=10, pady=10, fill="x")
        
        self.language_var = tk.StringVar(value="en")
        
        ttk.Radiobutton(
            lang_frame,
            text="English 🇬🇧",
            variable=self.language_var,
            value="en"
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Radiobutton(
            lang_frame,
            text="Tamil தமிழ் 🇮🇳",
            variable=self.language_var,
            value="ta"
        ).pack(anchor=tk.W, pady=5)
        
        # Control Buttons Frame
        button_frame = tk.Frame(control_frame, bg='#f0f0f0')
        button_frame.pack(pady=10, fill="x")
        
        self.start_btn = ttk.Button(
            button_frame,
            text="▶ Start Detection",
            command=self.start_detection,
            width=20
        )
        self.start_btn.pack(pady=5, fill="x")
        
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹ Stop Detection",
            command=self.stop_detection,
            state=tk.DISABLED,
            width=20
        )
        self.stop_btn.pack(pady=5, fill="x")
        
        # Status Label
        self.status_label = tk.Label(
            control_frame,
            text="Status: Ready",
            font=("Arial", 10, "bold"),
            bg='#f0f0f0',
            fg='#008000'
        )
        self.status_label.pack(pady=10, fill="x")
        
        # Objects Display Frame
        objects_frame = ttk.LabelFrame(control_frame, text="🎯 Detected Objects", padding=10)
        objects_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.objects_text = tk.Text(
            objects_frame,
            height=12,
            width=30,
            font=("Courier", 9),
            bg='#f5f5f5',
            fg='#333'
        )
        self.objects_text.pack(fill="both", expand=True)
        
        # Scrollbar for text
        scrollbar = ttk.Scrollbar(objects_frame, orient=tk.VERTICAL, command=self.objects_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.objects_text.config(yscrollcommand=scrollbar.set)
        
    def start_detection(self):
        """Start object detection"""
        language = self.language_var.get()
        self.app.start_detection(language)
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Detection Running...", fg='#008000')
        self.update_camera_display()
        
    def stop_detection(self):
        """Stop object detection"""
        self.app.stop_detection()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped", fg='#FF0000')
        self.camera_label.config(image='', text="Camera Stopped")
        
    def update_objects_display(self, objects):
        """Update detected objects display"""
        self.objects_text.config(state=tk.NORMAL)
        self.objects_text.delete(1.0, tk.END)
        
        if objects:
            for i, obj in enumerate(objects, 1):
                confidence = obj['confidence']
                # Color code by confidence
                if confidence > 80:
                    emoji = "🟢"  # High confidence
                elif confidence > 50:
                    emoji = "🟡"  # Medium confidence
                else:
                    emoji = "🔴"  # Low confidence
                
                text = f"{emoji} {obj['name']}\n   Confidence: {confidence:.1f}%\n\n"
                self.objects_text.insert(tk.END, text)
        else:
            self.objects_text.insert(tk.END, "No objects detected")
        
        self.objects_text.config(state=tk.DISABLED)
    
    def display_frame(self, frame):
        """Display frame in camera feed"""
        self.current_frame = frame
    
    def update_camera_display(self):
        """Update camera display label with current frame"""
        if self.current_frame is not None and self.app.running:
            # Resize frame to fit label
            frame = cv2.resize(self.current_frame, (500, 400))
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            image = Image.fromarray(frame_rgb)
            
            # Convert to PhotoImage
            self.photo = ImageTk.PhotoImage(image)
            
            # Update label
            self.camera_label.config(image=self.photo)
            self.camera_label.image = self.photo
        
        # Schedule next update
        if self.app.running:
            self.root.after(100, self.update_camera_display)
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()