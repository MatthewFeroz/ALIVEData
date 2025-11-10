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
try:
    from dotenv import load_dotenv
except ImportError:
    # Fallback if dotenv is not available
    def load_dotenv():
        pass
import sys

# Windows API for monitor detection
if sys.platform == 'win32':
    import ctypes

from .capture import capture_and_ocr
from .summarize import summarize_text


class ToolTip:
    """Custom tooltip class for hover tooltips."""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind('<Enter>', self.on_enter)
        self.widget.bind('<Leave>', self.on_leave)
        self.widget.bind('<ButtonPress>', self.on_leave)
    
    def on_enter(self, event=None):
        """Show tooltip on hover."""
        # Don't show if tooltip already exists
        if self.tooltip_window:
            return
        
        try:
            # Get widget position
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + 20
            
            self.tooltip_window = tk.Toplevel(self.widget)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_geometry(f"+{x}+{y}")
            self.tooltip_window.attributes('-topmost', True)
            
            label = tk.Label(
                self.tooltip_window,
                text=self.text,
                background='#2D2D2D',
                foreground='white',
                font=('Segoe UI', 9),
                relief=tk.FLAT,
                padx=8,
                pady=4,
                borderwidth=0
            )
            label.pack()
        except (tk.TclError, RuntimeError):
            # Widget might be destroyed, ignore
            pass
    
    def on_leave(self, event=None):
        """Hide tooltip when mouse leaves."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class FloatingToolbar:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', 0.95)  # Slight transparency
        
        # Enable DPI awareness on Windows
        if sys.platform == 'win32':
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except (AttributeError, OSError):
                # DPI awareness not available or failed
                pass
        
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        
        # State
        self.is_processing = False
        self.step_count = 0
        self.is_hidden = False
        self.is_dragging = False
        
        # Auto-hide settings
        self.hide_delay = 3000  # Hide after 3 seconds of inactivity
        self.hide_timer = None
        self.fade_steps = 10  # Steps for fade animation
        self.fade_duration = 200  # ms per fade step
        
        # Drag state
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Monitor detection
        self.base_toolbar_width = 320  # Base width for 1920px monitor
        self.base_monitor_width = 1920  # Reference monitor width
        self.toolbar_height = 56  # Slightly taller for better appearance
        self.corner_radius = 12  # Rounded corner radius
        
        # Colors (Zoom-inspired dark theme)
        self.bg_color = '#1A1A1A'  # Very dark background
        self.button_bg = '#2D2D2D'  # Button background
        self.button_hover = '#404040'  # Button hover
        self.button_active = '#FF4444'  # Red active/primary button
        self.text_color = '#FFFFFF'  # White text
        self.text_secondary = '#CCCCCC'  # Secondary text
        
        self.setup_toolbar()
        self.position_toolbar()
        self.setup_hover_effects()
        self.setup_drag_functionality()
        self.setup_auto_hide()
        self.setup_global_mouse_tracking()
        
    def setup_toolbar(self):
        """Create the Zoom-style toolbar interface with rounded corners."""
        # Main canvas for rounded corners and custom drawing
        self.canvas = tk.Canvas(
            self.root,
            bg=self.bg_color,
            highlightthickness=0,
            borderwidth=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw rounded rectangle background
        self.draw_rounded_rect()
        
        # Container frame for buttons (transparent, sits on canvas)
        self.toolbar_frame = tk.Frame(
            self.canvas,
            bg=self.bg_color
        )
        
        # Update canvas window to fill
        def update_canvas_window(event):
            if hasattr(self, 'canvas_window_id'):
                self.canvas.itemconfig(self.canvas_window_id, width=event.width, height=event.height)
            self.draw_rounded_rect()
        
        self.canvas_window_id = self.canvas.create_window(0, 0, window=self.toolbar_frame, anchor='nw')
        self.canvas.bind('<Configure>', update_canvas_window)
        self.toolbar_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        
        # Button container
        button_container = tk.Frame(self.toolbar_frame, bg=self.bg_color)
        button_container.pack(side=tk.LEFT, padx=12, pady=8)
        
        # Left side - Logo/Branding
        logo_frame = tk.Frame(button_container, bg=self.bg_color)
        logo_frame.pack(side=tk.LEFT, padx=4)
        
        self.logo_label = tk.Label(
            logo_frame,
            text="ALIVE",
            bg=self.bg_color,
            fg='#FFFFFF',  # White initially, turns red when capturing
            font=('Segoe UI', 10, 'bold'),
            cursor='arrow'
        )
        self.logo_label.pack()
        
        # Separator
        separator1 = tk.Frame(button_container, bg='#404040', width=1)
        separator1.pack(side=tk.LEFT, padx=8, fill=tk.Y, pady=4)
        
        # Step counter (icon + text) - horizontally aligned
        step_frame = tk.Frame(button_container, bg=self.bg_color)
        step_frame.pack(side=tk.LEFT, padx=4)
        
        # Use grid for better alignment control - horizontally aligned
        step_icon = tk.Label(
            step_frame,
            text="📊",
            bg=self.bg_color,
            fg=self.text_secondary,
            font=('Segoe UI', 11),  # Match text size for alignment
            cursor='arrow'
        )
        step_icon.grid(row=0, column=0, padx=(0, 4), sticky='ns')  # Vertically centered
        
        self.step_label = tk.Label(
            step_frame,
            text=f"{self.step_count}",
            bg=self.bg_color,
            fg=self.text_color,
            font=('Segoe UI', 11, 'bold'),  # Match icon size
            cursor='arrow'
        )
        self.step_label.grid(row=0, column=1, padx=0, sticky='ns')  # Vertically centered
        
        # Configure grid for proper vertical centering
        step_frame.grid_rowconfigure(0, weight=1)
        step_frame.grid_columnconfigure(0, weight=0)
        step_frame.grid_columnconfigure(1, weight=0)
        
        # Add tooltip to frame and all child widgets
        ToolTip(step_frame, "Steps captured")
        ToolTip(step_icon, "Steps captured")
        ToolTip(self.step_label, "Steps captured")
        
        # Separator
        separator2 = tk.Frame(button_container, bg='#404040', width=1)
        separator2.pack(side=tk.LEFT, padx=8, fill=tk.Y, pady=4)
        
        # Center - Capture button (icon style)
        self.capture_btn = self.create_icon_button(
            button_container,
            "🔴",  # Record icon
            self.button_active,
            self.start_capture_process,
            "Start Capture"
        )
        self.capture_btn.pack(side=tk.LEFT, padx=4)
        
        # Status indicator (icon style)
        status_frame = tk.Frame(button_container, bg=self.bg_color)
        status_frame.pack(side=tk.LEFT, padx=4)
        
        self.status_indicator = tk.Label(
            status_frame,
            text="●",
            bg=self.bg_color,
            fg='#666666',
            font=('Segoe UI', 12),
            cursor='arrow'
        )
        self.status_indicator.pack()
        self.status_tooltip = ToolTip(status_frame, "Status: Idle")
        
        # Right side buttons
        right_container = tk.Frame(self.toolbar_frame, bg=self.bg_color)
        right_container.pack(side=tk.RIGHT, padx=8, pady=8)
        
        # Settings button
        settings_btn = self.create_icon_button(
            right_container,
            "⚙",
            self.button_bg,
            self.show_settings,
            "Settings"
        )
        settings_btn.pack(side=tk.LEFT, padx=4)
        
        # Close button
        close_btn = self.create_icon_button(
            right_container,
            "✕",
            self.button_bg,
            self.on_closing,
            "Close"
        )
        close_btn.pack(side=tk.LEFT, padx=4)
    
    def create_icon_button(self, parent, icon, bg_color, command, tooltip_text):
        """Create an icon-only button with hover effects and tooltip."""
        btn = tk.Button(
            parent,
            text=icon,
            bg=bg_color,
            fg=self.text_color,
            font=('Segoe UI', 16),
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=8,
            cursor='hand2',
            command=command,
            activebackground=self.button_hover,
            activeforeground=self.text_color,
            width=3,
            height=1
        )
        
        # Add hover effect
        def on_enter(event):
            if btn['state'] != 'disabled':
                # Use darker red for capture button hover, normal hover for others
                if bg_color == self.button_active:
                    btn.config(bg='#CC0000')  # Darker red for capture button
                else:
                    btn.config(bg=self.button_hover)
        
        def on_leave(event):
            if btn['state'] != 'disabled':
                btn.config(bg=bg_color)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        # Add tooltip
        ToolTip(btn, tooltip_text)
        
        return btn
    
    def draw_rounded_rect(self):
        """Draw a rounded rectangle on the canvas (simulated rounded corners)."""
        self.canvas.delete('rounded_bg')
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Create rounded rectangle (simplified - Tkinter doesn't support true rounded corners)
        # We'll use a filled rectangle with border for depth
        self.canvas.create_rectangle(
            0, 0, width, height,
            fill=self.bg_color,
            outline='',
            tags='rounded_bg'
        )
        
        # Add subtle border for depth
        self.canvas.create_rectangle(
            1, 1, width - 1, height - 1,
            fill='',
            outline='#333333',
            width=1,
            tags='rounded_bg'
        )
    
    def update_status_indicator(self, status):
        """Update status indicator color and tooltip."""
        colors = {
            'idle': '#666666',
            'processing': '#FF4444',
            'success': '#00FF00',
            'error': '#FFAA00'
        }
        tooltips = {
            'idle': 'Status: Idle',
            'processing': 'Status: Processing',
            'success': 'Status: Success',
            'error': 'Status: Error'
        }
        
        if hasattr(self, 'status_indicator'):
            self.status_indicator.config(fg=colors.get(status, '#666666'))
        
        if hasattr(self, 'status_tooltip'):
            self.status_tooltip.text = tooltips.get(status, 'Status: Unknown')
    
    def draw_status_indicator(self, status):
        """Draw status indicator (legacy method for compatibility)."""
        self.update_status_indicator(status)
    
    def get_monitor_info(self, x=None, y=None):
        """
        Get monitor information for a given position.
        Returns (monitor_x, monitor_y, monitor_width, monitor_height) for the monitor containing the point.
        If x/y not provided, uses the current window position.
        """
        if sys.platform != 'win32':
            # Fallback for non-Windows: use tkinter's screen info
            if x is None or y is None:
                x = self.root.winfo_x()
                y = self.root.winfo_y()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            return (0, 0, screen_width, screen_height)
        
        # Windows: Use Windows API to enumerate monitors
        try:
            user32 = ctypes.windll.user32
            
            # If no position provided, get current window position
            if x is None or y is None:
                x = self.root.winfo_x()
                y = self.root.winfo_y()
            
            # Define RECT structure
            class RECT(ctypes.Structure):
                _fields_ = [
                    ("left", ctypes.c_long),
                    ("top", ctypes.c_long),
                    ("right", ctypes.c_long),
                    ("bottom", ctypes.c_long),
                ]
            
            # Define POINT structure
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            
            # Get monitor handle for the point
            point = POINT(x, y)
            monitor_handle = user32.MonitorFromPoint(point, 2)  # MONITOR_DEFAULTTONEAREST
            
            # Get monitor info
            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", ctypes.c_uint),
                    ("rcMonitor", RECT),
                    ("rcWork", RECT),
                    ("dwFlags", ctypes.c_uint),
                ]
            
            monitor_info = MONITORINFO()
            monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
            
            if user32.GetMonitorInfoW(monitor_handle, ctypes.byref(monitor_info)):
                rect = monitor_info.rcMonitor
                return (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)
        except Exception:
            pass
        
        # Fallback: use tkinter screen info
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        return (0, 0, screen_width, screen_height)
    
    def get_current_monitor_info(self):
        """Get info for the monitor containing the current window position."""
        return self.get_monitor_info()
    
    def calculate_toolbar_width(self, monitor_width):
        """
        Calculate toolbar width based on monitor width.
        Scales proportionally from base width.
        """
        # Scale toolbar width based on monitor width
        # Minimum width: 280px, Maximum width: 600px
        scale_factor = monitor_width / self.base_monitor_width
        calculated_width = int(self.base_toolbar_width * scale_factor)
        
        # Clamp to reasonable bounds
        min_width = 280
        max_width = 600
        return max(min_width, min(max_width, calculated_width))
    
    def position_toolbar(self, x=None, y=None):
        """
        Position toolbar at bottom center of the current monitor.
        If x/y provided, positions relative to that monitor.
        """
        self.root.update_idletasks()
        
        # Get monitor info for the position (or current position if not provided)
        if x is None or y is None:
            # On first load, try to center on primary monitor
            monitor_x, monitor_y, monitor_width, monitor_height = self.get_monitor_info(0, 0)
        else:
            monitor_x, monitor_y, monitor_width, monitor_height = self.get_monitor_info(x, y)
        
        # Calculate toolbar width based on monitor width
        toolbar_width = self.calculate_toolbar_width(monitor_width)
        
        # Position at bottom center of the monitor with some margin
        if x is None or y is None:
            x = monitor_x + (monitor_width - toolbar_width) // 2
            y = monitor_y + monitor_height - self.toolbar_height - 20  # 20px from bottom
        else:
            # If position provided, ensure it's within monitor bounds
            x = max(monitor_x, min(x, monitor_x + monitor_width - toolbar_width))
            y = max(monitor_y, min(y, monitor_y + monitor_height - self.toolbar_height))
        
        self.root.geometry(f'{toolbar_width}x{self.toolbar_height}+{x}+{y}')
        
    def setup_hover_effects(self):
        """Add hover effects to make toolbar more visible on hover."""
        def on_enter(event):
            if not self.is_hidden:
                self.root.attributes('-alpha', 1.0)
            self.reset_hide_timer()
            
        def on_leave(event):
            if not self.is_processing and not self.is_dragging:
                self.root.attributes('-alpha', 0.95)
        
        self.toolbar_frame.bind('<Enter>', on_enter)
        self.toolbar_frame.bind('<Leave>', on_leave)
        if hasattr(self, 'canvas'):
            self.canvas.bind('<Enter>', on_enter)
            self.canvas.bind('<Leave>', on_leave)
    
    def setup_auto_hide(self):
        """Set up auto-hide functionality with fade animation."""
        def reset_hide_timer():
            """Reset the auto-hide timer."""
            if self.hide_timer:
                self.root.after_cancel(self.hide_timer)
            
            if not self.is_hidden and not self.is_dragging:
                self.show_toolbar()
                self.hide_timer = self.root.after(self.hide_delay, self.hide_toolbar)
        
        # Bind mouse movement to reset timer
        self.root.bind('<Motion>', lambda e: reset_hide_timer())
        if hasattr(self, 'canvas'):
            self.canvas.bind('<Motion>', lambda e: reset_hide_timer())
        self.toolbar_frame.bind('<Motion>', lambda e: reset_hide_timer())
        
        # Start initial timer
        self.hide_timer = self.root.after(self.hide_delay, self.hide_toolbar)
    
    def reset_hide_timer(self):
        """Reset the auto-hide timer."""
        if self.hide_timer:
            self.root.after_cancel(self.hide_timer)
        
        if not self.is_hidden and not self.is_dragging:
            self.show_toolbar()
            self.hide_timer = self.root.after(self.hide_delay, self.hide_toolbar)
    
    def hide_toolbar(self):
        """Hide toolbar with fade animation."""
        if self.is_hidden or self.is_dragging:
            return
        
        self.is_hidden = True
        
        # Fade out animation
        def fade_out(step=0):
            if step <= self.fade_steps:
                alpha = 1.0 - (step / self.fade_steps) * 0.85  # Fade to 15% opacity
                try:
                    self.root.attributes('-alpha', alpha)
                    self.root.after(self.fade_duration // self.fade_steps, lambda: fade_out(step + 1))
                except (tk.TclError, RuntimeError):
                    # Window might be destroyed during fade
                    pass
        
        fade_out()
    
    def show_toolbar(self):
        """Show toolbar with fade animation."""
        if not self.is_hidden:
            return
        
        self.is_hidden = False
        
        # Fade in animation
        def fade_in(step=0):
            if step <= self.fade_steps:
                alpha = 0.15 + (step / self.fade_steps) * 0.85  # Fade from 15% to 100%
                try:
                    self.root.attributes('-alpha', alpha)
                    self.root.after(self.fade_duration // self.fade_steps, lambda: fade_in(step + 1))
                except (tk.TclError, RuntimeError):
                    # Window might be destroyed during fade
                    pass
        
        fade_in()
    
    def setup_global_mouse_tracking(self):
        """Track mouse movement globally to show toolbar when mouse moves."""
        if sys.platform == 'win32':
            def check_mouse():
                try:
                    # Get cursor position
                    class POINT(ctypes.Structure):
                        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
                    
                    point = POINT()
                    ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
                    
                    # Get toolbar position
                    toolbar_x = self.root.winfo_x()
                    toolbar_y = self.root.winfo_y()
                    toolbar_w = self.root.winfo_width()
                    toolbar_h = self.root.winfo_height()
                    
                    # Check if mouse is near toolbar (within 50px)
                    margin = 50
                    if (toolbar_x - margin <= point.x <= toolbar_x + toolbar_w + margin and
                        toolbar_y - margin <= point.y <= toolbar_y + toolbar_h + margin):
                        if self.is_hidden:
                            self.show_toolbar()
                    else:
                        # Mouse is away, start hide timer
                        if not self.is_hidden and not self.is_dragging:
                            if self.hide_timer:
                                self.root.after_cancel(self.hide_timer)
                            self.hide_timer = self.root.after(self.hide_delay, self.hide_toolbar)
                    
                    self.root.after(100, check_mouse)  # Check every 100ms
                except (AttributeError, RuntimeError, tk.TclError):
                    # Window might be destroyed or API call failed
                    pass
            
            self.root.after(100, check_mouse)
        
    def setup_drag_functionality(self):
        """Set up drag functionality for the toolbar with monitor-aware resizing."""
        def start_drag(event):
            self.is_dragging = True
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            # Store initial monitor info
            self.drag_start_monitor = self.get_current_monitor_info()
            
            # Cancel hide timer while dragging
            if self.hide_timer:
                self.root.after_cancel(self.hide_timer)
            
            # Show toolbar while dragging
            if self.is_hidden:
                self.show_toolbar()
            
        def on_drag(event):
            # Calculate new position
            new_x = self.root.winfo_x() + event.x - self.drag_start_x
            new_y = self.root.winfo_y() + event.y - self.drag_start_y
            
            # Get monitor info for new position
            monitor_x, monitor_y, monitor_width, monitor_height = self.get_monitor_info(new_x, new_y)
            
            # Check if we've moved to a different monitor
            current_monitor = (monitor_x, monitor_y, monitor_width, monitor_height)
            if hasattr(self, 'drag_start_monitor') and current_monitor != self.drag_start_monitor:
                # Different monitor detected - adjust toolbar width
                new_width = self.calculate_toolbar_width(monitor_width)
                # Re-center horizontally on new monitor
                new_x = monitor_x + (monitor_width - new_width) // 2
                # Keep vertical position but ensure it's within bounds
                new_y = max(monitor_y, min(new_y, monitor_y + monitor_height - self.toolbar_height))
                self.root.geometry(f'{new_width}x{self.toolbar_height}+{new_x}+{new_y}')
                self.drag_start_monitor = current_monitor
            else:
                # Same monitor - just update position, but keep within bounds
                new_x = max(monitor_x, min(new_x, monitor_x + monitor_width - self.root.winfo_width()))
                new_y = max(monitor_y, min(new_y, monitor_y + monitor_height - self.toolbar_height))
                self.root.geometry(f'+{new_x}+{new_y}')
            
        def end_drag(event):
            self.is_dragging = False
            
            # When drag ends, snap to bottom center of current monitor if near bottom
            current_x = self.root.winfo_x()
            current_y = self.root.winfo_y()
            monitor_x, monitor_y, monitor_width, monitor_height = self.get_monitor_info(current_x, current_y)
            
            # If toolbar is near bottom of monitor (within 50px), snap to bottom center
            bottom_y = monitor_y + monitor_height - self.toolbar_height - 20
            if abs(current_y - bottom_y) < 50:
                toolbar_width = self.calculate_toolbar_width(monitor_width)
                center_x = monitor_x + (monitor_width - toolbar_width) // 2
                self.root.geometry(f'{toolbar_width}x{self.toolbar_height}+{center_x}+{bottom_y}')
            
            # Restart hide timer
            self.reset_hide_timer()
            
        # Bind drag events to canvas and toolbar frame
        if hasattr(self, 'canvas'):
            self.canvas.bind('<Button-1>', start_drag)
            self.canvas.bind('<B1-Motion>', on_drag)
            self.canvas.bind('<ButtonRelease-1>', end_drag)
        self.toolbar_frame.bind('<Button-1>', start_drag)
        self.toolbar_frame.bind('<B1-Motion>', on_drag)
        self.toolbar_frame.bind('<ButtonRelease-1>', end_drag)
        
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
        self.capture_btn.config(state=tk.DISABLED)
        self.update_status_indicator('processing')
        # Change logo to red when capturing
        self.logo_label.config(fg='#FF4444')
        self.step_count += 1
        self.step_label.config(text=f"{self.step_count}")
        
        # Run in separate thread
        thread = threading.Thread(target=self.capture_process, daemon=True)
        thread.start()
        
    def capture_process(self):
        """Perform capture and documentation generation."""
        try:
            Path("docs/generated").mkdir(parents=True, exist_ok=True)
            
            # Update API key if needed
            if self.api_key:
                os.environ["OPENAI_API_KEY"] = self.api_key
            
            # Capture and OCR
            ocr_result = capture_and_ocr()
            
            # Generate summary
            summary = summarize_text(ocr_result)
            
            # Save to file
            output_path = Path("docs/generated") / f"generated_doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(summary)
            
            # Update UI
            self.root.after(0, lambda: self.capture_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.update_status_indicator('success'))
            self.root.after(0, lambda: self.show_notification(f"Documentation saved!\n{output_path.name}"))
            
            # Reset status after 2 seconds
            self.root.after(2000, lambda: self.draw_status_indicator('idle'))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.capture_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.update_status_indicator('error'))
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{error_msg}"))
            self.root.after(2000, lambda: self.update_status_indicator('idle'))
        finally:
            self.is_processing = False
            # Change logo back to white when done
            self.root.after(0, lambda: self.logo_label.config(fg='#FFFFFF'))
            
    def show_notification(self, message):
        """Show a brief notification."""
        # Simple notification - could be enhanced with a toast-style popup
        self.step_label.config(text=message[:20] + "...")
        self.root.after(3000, lambda: self.step_label.config(text=f"{self.step_count} Steps"))
        
    def format_api_key_display(self, key):
        """Format API key for display (show first 7 chars + ...)."""
        if not key or len(key) < 7:
            return ""
        return f"{key[:7]}...{key[-4:]}" if len(key) > 11 else f"{key[:7]}..."
    
    def validate_api_key_format(self, key):
        """Validate OpenAI API key format."""
        if not key:
            return False, "API key cannot be empty"
        key = key.strip()
        if len(key) < 20:
            return False, "API key appears too short (minimum 20 characters)"
        if not (key.startswith("sk-") or key.startswith("sk-proj-")):
            return False, "API key should start with 'sk-' or 'sk-proj-'"
        return True, "Valid format"
    
    def show_settings(self):
        """Show settings window for API key configuration."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("ALIVE Data Settings")
        settings_window.geometry("400x180")
        settings_window.attributes('-topmost', True)
        settings_window.resizable(False, False)
        
        # Center the settings window on the same monitor as the toolbar
        settings_window.update_idletasks()
        toolbar_x = self.root.winfo_x()
        toolbar_y = self.root.winfo_y()
        monitor_x, monitor_y, monitor_width, monitor_height = self.get_monitor_info(toolbar_x, toolbar_y)
        x = monitor_x + (monitor_width - 400) // 2
        y = monitor_y + (monitor_height - 180) // 2
        settings_window.geometry(f"400x180+{x}+{y}")
        
        frame = tk.Frame(settings_window, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="OpenAI API Key:", font=('Segoe UI', 9)).pack(anchor=tk.W, pady=(0, 5))
        
        api_key_var = tk.StringVar(value=self.api_key)
        api_entry = tk.Entry(frame, textvariable=api_key_var, show="*", width=45, font=('Consolas', 9))
        api_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Format display label
        display_label = tk.Label(frame, text="", font=('Consolas', 8), fg='gray', anchor=tk.W)
        display_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Update display when key changes
        def update_display(*args):
            key = api_key_var.get()
            if key:
                formatted = self.format_api_key_display(key)
                display_label.config(text=f"Preview: {formatted}")
            else:
                display_label.config(text="")
        api_key_var.trace_add("write", update_display)
        update_display()
        
        def save_settings():
            key = api_key_var.get().strip()
            if not key:
                messagebox.showwarning("Warning", "Please enter an API key.")
                return
            
            # Validate format
            is_valid, message = self.validate_api_key_format(key)
            if not is_valid:
                result = messagebox.askyesno(
                    "Invalid API Key Format",
                    f"{message}\n\nDo you want to save it anyway?"
                )
                if not result:
                    return
            
            try:
                env_path = Path(".env")
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(f"OPENAI_API_KEY={key}\n")
                
                self.api_key = key
                os.environ["OPENAI_API_KEY"] = key
                formatted = self.format_api_key_display(key)
                messagebox.showinfo("Success", f"API key saved successfully!\n({formatted})")
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

