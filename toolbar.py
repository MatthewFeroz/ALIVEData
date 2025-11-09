"""
ALIVE Data MVP - Floating Toolbar
A minimal, unobtrusive toolbar that stays at the bottom of the screen.
"""

import tkinter as tk
from tkinter import messagebox
import threading
from pathlib import Path
import os
from datetime import datetime
from dotenv import load_dotenv

from capture import capture_and_ocr
from summarize import summarize_text


class FloatingToolbar:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', 0.95)  # Slight transparency
        
        # Make window click-through when not hovering (optional)
        # self.root.attributes('-transparentcolor', 'gray15')
        
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        
        # State
        self.is_processing = False
        self.step_count = 0
        
        # Drag state
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.setup_toolbar()
        self.position_toolbar()
        self.setup_hover_effects()
        self.setup_drag_functionality()
        
    def setup_toolbar(self):
        """Create the minimal toolbar interface."""
        # Drag bar at the top
        self.drag_bar = tk.Frame(
            self.root,
            bg='#1A1A1A',  # Slightly darker for the drag bar
            height=4,
            cursor='hand2'
        )
        self.drag_bar.pack(fill=tk.X, side=tk.TOP)
        
        # Main frame with rounded appearance
        self.toolbar_frame = tk.Frame(
            self.root,
            bg='#2D2D2D',  # Dark gray background
            relief=tk.FLAT,
            bd=0
        )
        self.toolbar_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Logo/Branding
        logo_frame = tk.Frame(self.toolbar_frame, bg='#2D2D2D')
        logo_frame.pack(side=tk.LEFT, padx=(12, 8), pady=8)
        
        logo_label = tk.Label(
            logo_frame,
            text="ALIVE",
            bg='#2D2D2D',
            fg='#FF4444',  # Red accent
            font=('Segoe UI', 10, 'bold')
        )
        logo_label.pack()
        
        # Center - Step counter
        self.step_label = tk.Label(
            self.toolbar_frame,
            text=f"{self.step_count} Steps",
            bg='#2D2D2D',
            fg='#CCCCCC',
            font=('Segoe UI', 9)
        )
        self.step_label.pack(side=tk.LEFT, padx=8)
        
        # Center - Capture button
        self.capture_btn = tk.Button(
            self.toolbar_frame,
            text="Done",
            bg='#0078D4',  # Blue button
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=6,
            cursor='hand2',
            command=self.start_capture_process,
            activebackground='#005A9E',
            activeforeground='white'
        )
        self.capture_btn.pack(side=tk.LEFT, padx=8)
        
        # Right side - Status indicator
        self.status_indicator = tk.Canvas(
            self.toolbar_frame,
            width=12,
            height=12,
            bg='#2D2D2D',
            highlightthickness=0
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(8, 12), pady=8)
        self.draw_status_indicator('idle')
        
        # Right side - Settings button (gear icon)
        settings_btn = tk.Button(
            self.toolbar_frame,
            text="⚙",
            bg='#2D2D2D',
            fg='#CCCCCC',
            font=('Segoe UI', 12),
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=4,
            cursor='hand2',
            command=self.show_settings,
            activebackground='#404040',
            activeforeground='white'
        )
        settings_btn.pack(side=tk.RIGHT, padx=4)
        
        # Right side - Close button
        close_btn = tk.Button(
            self.toolbar_frame,
            text="✕",
            bg='#2D2D2D',
            fg='#CCCCCC',
            font=('Segoe UI', 12),
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=4,
            cursor='hand2',
            command=self.on_closing,
            activebackground='#E81123',
            activeforeground='white'
        )
        close_btn.pack(side=tk.RIGHT, padx=4)
        
    def draw_status_indicator(self, status):
        """Draw status indicator circle."""
        self.status_indicator.delete("all")
        if status == 'idle':
            color = '#666666'  # Gray
        elif status == 'processing':
            color = '#FF4444'  # Red (recording)
        elif status == 'success':
            color = '#00FF00'  # Green
        else:
            color = '#FFAA00'  # Orange (error)
        
        self.status_indicator.create_oval(
            2, 2, 10, 10,
            fill=color,
            outline='',
            tags='indicator'
        )
        
    def position_toolbar(self):
        """Position toolbar at bottom center of screen."""
        self.root.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Toolbar dimensions (added 4px for drag bar)
        toolbar_width = 320
        toolbar_height = 54  # 50 + 4 for drag bar
        
        # Position at bottom center with some margin
        x = (screen_width - toolbar_width) // 2
        y = screen_height - toolbar_height - 20  # 20px from bottom
        
        self.root.geometry(f'{toolbar_width}x{toolbar_height}+{x}+{y}')
        
    def setup_hover_effects(self):
        """Add hover effects to make toolbar more visible on hover."""
        def on_enter(event):
            self.root.attributes('-alpha', 1.0)
            
        def on_leave(event):
            if not self.is_processing:
                self.root.attributes('-alpha', 0.95)
        
        self.toolbar_frame.bind('<Enter>', on_enter)
        self.toolbar_frame.bind('<Leave>', on_leave)
        self.drag_bar.bind('<Enter>', on_enter)
        self.drag_bar.bind('<Leave>', on_leave)
        
    def setup_drag_functionality(self):
        """Set up drag functionality for the toolbar."""
        def start_drag(event):
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            
        def on_drag(event):
            x = self.root.winfo_x() + event.x - self.drag_start_x
            y = self.root.winfo_y() + event.y - self.drag_start_y
            self.root.geometry(f'+{x}+{y}')
            
        # Bind drag events to drag bar and toolbar frame
        self.drag_bar.bind('<Button-1>', start_drag)
        self.drag_bar.bind('<B1-Motion>', on_drag)
        self.toolbar_frame.bind('<Button-1>', start_drag)
        self.toolbar_frame.bind('<B1-Motion>', on_drag)
        
    def start_capture_process(self):
        """Start the capture and documentation generation."""
        if self.is_processing:
            return
        
        if not self.api_key or self.api_key.strip() == "":
            self.show_settings()
            messagebox.showwarning(
                "API Key Required",
                "Please set your OpenAI API key in settings."
            )
            return
        
        self.is_processing = True
        self.capture_btn.config(state=tk.DISABLED, text="Processing...")
        self.draw_status_indicator('processing')
        self.step_count += 1
        self.step_label.config(text=f"{self.step_count} Steps")
        
        # Run in separate thread
        thread = threading.Thread(target=self.capture_process, daemon=True)
        thread.start()
        
    def capture_process(self):
        """Perform capture and documentation generation."""
        try:
            Path("docs").mkdir(exist_ok=True)
            
            # Update API key if needed
            if self.api_key:
                os.environ["OPENAI_API_KEY"] = self.api_key
            
            # Capture and OCR
            ocr_result = capture_and_ocr()
            
            # Generate summary
            summary = summarize_text(ocr_result)
            
            # Save to file
            output_path = Path("docs") / f"generated_doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(summary)
            
            # Update UI
            self.root.after(0, lambda: self.capture_btn.config(state=tk.NORMAL, text="Done"))
            self.root.after(0, lambda: self.draw_status_indicator('success'))
            self.root.after(0, lambda: self.show_notification(f"Documentation saved!\n{output_path.name}"))
            
            # Reset status after 2 seconds
            self.root.after(2000, lambda: self.draw_status_indicator('idle'))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.capture_btn.config(state=tk.NORMAL, text="Done"))
            self.root.after(0, lambda: self.draw_status_indicator('error'))
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{error_msg}"))
            self.root.after(2000, lambda: self.draw_status_indicator('idle'))
        finally:
            self.is_processing = False
            
    def show_notification(self, message):
        """Show a brief notification."""
        # Simple notification - could be enhanced with a toast-style popup
        self.step_label.config(text=message[:20] + "...")
        self.root.after(3000, lambda: self.step_label.config(text=f"{self.step_count} Steps"))
        
    def show_settings(self):
        """Show settings window for API key configuration."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("ALIVE Data Settings")
        settings_window.geometry("400x150")
        settings_window.attributes('-topmost', True)
        settings_window.resizable(False, False)
        
        # Center the settings window
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (settings_window.winfo_screenheight() // 2) - (150 // 2)
        settings_window.geometry(f"400x150+{x}+{y}")
        
        frame = tk.Frame(settings_window, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="OpenAI API Key:", font=('Segoe UI', 9)).pack(anchor=tk.W, pady=(0, 5))
        
        api_key_var = tk.StringVar(value=self.api_key)
        api_entry = tk.Entry(frame, textvariable=api_key_var, show="*", width=45, font=('Consolas', 9))
        api_entry.pack(fill=tk.X, pady=(0, 15))
        
        def save_settings():
            key = api_key_var.get().strip()
            if not key:
                messagebox.showwarning("Warning", "Please enter an API key.")
                return
            
            try:
                env_path = Path(".env")
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(f"OPENAI_API_KEY={key}\n")
                
                self.api_key = key
                os.environ["OPENAI_API_KEY"] = key
                messagebox.showinfo("Success", "API key saved successfully!")
                settings_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(
            btn_frame,
            text="Save",
            command=save_settings,
            bg='#0078D4',
            fg='white',
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=settings_window.destroy,
            bg='#404040',
            fg='white',
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.RIGHT)
        
    def on_closing(self):
        """Handle toolbar close."""
        if messagebox.askokcancel("Quit", "Close ALIVE Data toolbar?"):
            self.root.quit()
            self.root.destroy()
            
    def run(self):
        """Start the toolbar."""
        self.root.mainloop()


def main():
    app = FloatingToolbar()
    app.run()


if __name__ == "__main__":
    main()

