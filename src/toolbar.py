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

from .capture import capture_and_ocr, extract_terminal_text
from .summarize import summarize_text, summarize_commands
from .command_recorder import CommandRecorder
from .session_manager import SessionManager


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
        # If tooltip already exists, destroy it first to refresh with new text
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
        
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
                text=self.text,  # Read current text value
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
    
    def update_text(self, new_text):
        """Update the tooltip text and refresh if currently showing."""
        self.text = new_text
        # If tooltip is currently showing, destroy it so it will refresh on next hover
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
        self.is_recording = False  # Command recording mode
        self.step_count = 0
        self.is_hidden = False
        self.is_dragging = False
        
        # Command recorder
        self.command_recorder = None
        
        # Session manager for organizing recordings
        self.session_manager = None
        
        # Recording log window for visual feedback
        self.log_window = None
        self.log_text = None
        self.captured_commands = []  # Store recent captures for display
        
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
        # This button toggles between start/stop recording
        self.capture_btn = self.create_icon_button(
            button_container,
            "🔴",  # Record icon
            self.button_active,
            self.toggle_recording,
            "Start Recording"
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
            'processing': 'Status: Processing...',
            'success': 'Status: Success',
            'error': 'Status: Error'
        }
        
        if hasattr(self, 'status_indicator'):
            self.status_indicator.config(fg=colors.get(status, '#666666'))
        
        if hasattr(self, 'status_tooltip'):
            # Use update_text method to properly refresh tooltip
            new_tooltip_text = tooltips.get(status, 'Status: Unknown')
            self.status_tooltip.update_text(new_tooltip_text)
    
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
        
    def toggle_recording(self):
        """Toggle recording on/off - ONLY way to stop recording."""
        if self.is_recording:
            # Stop recording (ONLY called via button press)
            self.stop_recording()
        else:
            # Start recording mode
            self.start_recording()
    
    def toggle_capture_or_record(self):
        """Toggle between manual capture and command recording mode."""
        if self.is_recording:
            # Stop recording
            self.stop_recording()
        else:
            # Check if we should start recording or do manual capture
            # For now, start recording mode
            self.start_recording()
    
    def start_recording(self):
        """Start command recording mode."""
        if self.is_processing or self.is_recording:
            return
        
        if not self.api_key or self.api_key.strip() == "":
            self.show_settings()
            messagebox.showwarning(
                "API Key Required",
                "Please set your OpenAI API key in settings."
            )
            return
        
        # Show window selector to choose which windows to track
        from .window_selector import WindowSelector
        selector = WindowSelector(self.root)
        selection = selector.show()
        
        # If user cancelled, don't start recording
        if selection is None:
            return
        
        tracked_windows, tracked_processes = selection
        
        # Create session folder for this recording
        self.session_manager = SessionManager()
        self.session_manager.create_session_folder()
        
        # Initialize command recorder with session manager and event filters
        self.is_recording = True
        self.command_recorder = CommandRecorder(
            on_command_captured=self.on_command_captured,
            session_manager=self.session_manager
        )
        
        # Set event tracker filters
        if self.command_recorder.event_tracker:
            self.command_recorder.event_tracker.tracked_windows = set(tracked_windows) if tracked_windows else None
            self.command_recorder.event_tracker.tracked_processes = set(p.lower() for p in tracked_processes) if tracked_processes else None
            # Don't set callback - we don't want automatic notifications
            # User can manually refresh if they want to add new windows
        
        self.command_recorder.start_recording()
        
        # Update UI
        self.capture_btn.config(text="⏹", bg='#CC0000')  # Stop icon, darker red
        self.update_status_indicator('processing')
        self.logo_label.config(fg='#FF4444')  # Red logo when recording
        self.step_label.config(text="Recording...")
        
        # Update tooltip
        ToolTip(self.capture_btn, "Stop Recording")
        
        # Show recording log window
        self.show_recording_log()
    
    def stop_recording(self):
        """Stop command recording and generate documentation."""
        if not self.is_recording or not self.command_recorder:
            return
        
        # Stop recording
        command_history = self.command_recorder.stop_recording()
        self.is_recording = False
        
        # Save events if available
        if self.command_recorder and self.command_recorder.event_tracker and self.session_manager:
            try:
                events = self.command_recorder.event_tracker.get_events()
                if events:
                    events_dict = [event.to_dict() for event in events]
                    self.session_manager.save_events(events_dict)
            except Exception:
                pass
        
        # Update UI
        self.capture_btn.config(text="🔴", bg=self.button_active, activebackground='#CC0000')  # Back to record icon
        self.update_status_indicator('processing')
        self.step_label.config(text="Processing...")
        
        # Remove old tooltip and add new one
        for widget in [self.capture_btn]:
            try:
                widget.unbind('<Enter>')
                widget.unbind('<Leave>')
            except Exception:
                pass
        ToolTip(self.capture_btn, "Start Recording")
        
        # Hide recording log window
        self.hide_recording_log()
        
        # Generate documentation from commands
        if command_history:
            thread = threading.Thread(target=self.process_command_session, args=(command_history,), daemon=True)
            thread.start()
        else:
            self.root.after(0, lambda: messagebox.showinfo("Recording", "No commands were captured."))
            self.root.after(0, lambda: self.capture_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.update_status_indicator('idle'))
            self.root.after(0, lambda: self.logo_label.config(fg='#FFFFFF'))
            self.root.after(0, lambda: self.step_label.config(text=f"{self.step_count}"))
    
    def on_command_captured(self, command, screenshot_path, timestamp):
        """Callback when a command is captured."""
        # Don't process OCR here - just update UI
        # Images will be processed later when stop_recording is called
        try:
            # Update step count (just count captures, don't process images)
            self.step_count += 1
            self.root.after(0, lambda: self.step_label.config(text=f"{self.step_count} commands"))
            
            # Add to captured commands list for display
            time_str = timestamp.strftime("%H:%M:%S")
            self.captured_commands.append((time_str, screenshot_path))
            
            # Update log window if it exists
            self.root.after(0, lambda: self.update_recording_log(time_str, screenshot_path))
        except Exception:
            # Don't let UI updates stop recording
            pass
    
    def show_recording_log(self):
        """Show a log window displaying captured commands during recording."""
        if self.log_window:
            return
        
        # Create log window
        self.log_window = tk.Toplevel(self.root)
        self.log_window.title("Recording Log - ALIVE Data")
        self.log_window.geometry("500x300")
        self.log_window.attributes('-topmost', True)
        self.log_window.configure(bg='#1A1A1A')
        
        # Position window near toolbar
        self.root.update_idletasks()
        toolbar_x = self.root.winfo_x()
        toolbar_y = self.root.winfo_y()
        
        # Position above toolbar
        log_x = toolbar_x
        log_y = toolbar_y - 320  # Above toolbar
        self.log_window.geometry(f"500x300+{log_x}+{log_y}")
        
        # Header
        header_frame = tk.Frame(self.log_window, bg='#2D2D2D', height=40)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(
            header_frame,
            text="🔴 Recording...",
            bg='#2D2D2D',
            fg='#FF4444',
            font=('Segoe UI', 10, 'bold'),
            anchor='w',
            padx=15,
            pady=10
        )
        header_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Refresh button
        refresh_btn = tk.Button(
            header_frame,
            text="🔄 Refresh Windows",
            bg='#4A4A4A',
            fg='#FFFFFF',
            font=('Segoe UI', 8),
            padx=10,
            pady=5,
            relief=tk.FLAT,
            cursor='hand2',
            command=self._show_new_windows_dialog
        )
        refresh_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Log text area with scrollbar
        log_frame = tk.Frame(self.log_window, bg='#1A1A1A')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            log_frame,
            bg='#1A1A1A',
            fg='#FFFFFF',
            font=('Consolas', 9),
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            padx=10,
            pady=10,
            insertbackground='#FFFFFF'
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Initial message
        self.log_text.insert(tk.END, "Waiting for commands...\n", "info")
        self.log_text.tag_config("info", foreground="#CCCCCC")
        self.log_text.tag_config("command", foreground="#FFFFFF", font=('Consolas', 9, 'bold'))
        self.log_text.tag_config("time", foreground="#888888")
        self.log_text.tag_config("file", foreground="#4A9EFF")
        
        self.log_text.config(state=tk.DISABLED)  # Make read-only
        
        # Handle window close
        def on_log_close():
            # Don't actually close during recording, just minimize
            if self.is_recording:
                self.log_window.iconify()
            else:
                self.log_window.destroy()
                self.log_window = None
                self.log_text = None
        
        self.log_window.protocol("WM_DELETE_WINDOW", on_log_close)
        
        # Clear captured commands list
        self.captured_commands = []
    
    def update_recording_log(self, time_str, screenshot_path):
        """Update the recording log with a new capture."""
        if not self.log_window or not self.log_text:
            return
        
        try:
            self.log_text.config(state=tk.NORMAL)
            
            # Get filename from path
            filename = Path(screenshot_path).name if screenshot_path else "Unknown"
            
            # Add entry
            self.log_text.insert(tk.END, f"[{time_str}] ", "time")
            self.log_text.insert(tk.END, "Captured: ", "info")
            self.log_text.insert(tk.END, f"{filename}\n", "file")
            
            # Auto-scroll to bottom
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
            
            # Keep only last 50 entries visible
            lines = self.log_text.get("1.0", tk.END).split('\n')
            if len(lines) > 50:
                self.log_text.config(state=tk.NORMAL)
                self.log_text.delete("1.0", f"{len(lines) - 50}.0")
                self.log_text.config(state=tk.DISABLED)
        except Exception:
            # Don't let log updates break recording
            pass
    
    def hide_recording_log(self):
        """Hide or close the recording log window."""
        if self.log_window:
            try:
                self.log_window.destroy()
            except Exception:
                pass
            self.log_window = None
            self.log_text = None
        self.captured_commands = []
    
    def _show_new_windows_dialog(self):
        """Show dialog with newly detected windows that can be added to tracking."""
        if not self.is_recording or not self.command_recorder or not self.command_recorder.event_tracker:
            return
        
        # Get pending windows
        pending_windows = self.command_recorder.event_tracker.get_pending_windows()
        
        if not pending_windows:
            messagebox.showinfo("No New Windows", "No new windows detected. All windows are already being tracked.")
            return
        
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("New Windows Detected")
        dialog.geometry("600x400")
        dialog.attributes('-topmost', True)
        dialog.configure(bg='#1A1A1A')
        
        # Center on parent
        self.root.update_idletasks()
        parent_x = self.root.winfo_x()
        parent_y = self.root.winfo_y()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()
        
        x = parent_x + (parent_width - 600) // 2
        y = parent_y + (parent_height - 400) // 2
        dialog.geometry(f"600x400+{x}+{y}")
        
        # Header
        header_label = tk.Label(
            dialog,
            text=f"Found {len(pending_windows)} new window(s). Select which to track:",
            bg='#2D2D2D',
            fg='#FFFFFF',
            font=('Segoe UI', 10),
            padx=15,
            pady=10,
            anchor='w'
        )
        header_label.pack(fill=tk.X)
        
        # Listbox with scrollbar
        list_frame = tk.Frame(dialog, bg='#1A1A1A')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(
            list_frame,
            bg='#2D2D2D',
            fg='#FFFFFF',
            font=('Consolas', 9),
            selectmode=tk.EXTENDED,
            yscrollcommand=scrollbar.set
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Store window data with listbox indices
        window_data_map = {}
        for idx, window in enumerate(pending_windows):
            display_text = f"{window.get('process_name', 'Unknown')} - {window.get('window_title', 'Untitled')}"
            listbox.insert(tk.END, display_text)
            window_data_map[idx] = window
        
        # Select all by default
        listbox.selection_set(0, tk.END)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#1A1A1A')
        button_frame.pack(fill=tk.X, padx=15, pady=10)
        
        def add_selected():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select at least one window to add.")
                return
            
            event_tracker = self.command_recorder.event_tracker
            
            for idx in selected_indices:
                window = window_data_map[idx]
                hwnd = window.get('window_hwnd')
                process_name = window.get('process_name', '')
                
                if hwnd:
                    event_tracker.add_window(hwnd)
                
                # Also add process if not already tracked
                if process_name and event_tracker.tracked_processes:
                    if process_name.lower() not in event_tracker.tracked_processes:
                        event_tracker.add_process(process_name)
            
            # Remove added windows from pending
            for idx in reversed(selected_indices):
                window = window_data_map[idx]
                hwnd = window.get('window_hwnd')
                with event_tracker.pending_windows_lock:
                    event_tracker.pending_windows = [
                        w for w in event_tracker.pending_windows
                        if w.get('window_hwnd') != hwnd
                    ]
            
            messagebox.showinfo("Windows Added", f"Added {len(selected_indices)} window(s) to tracking.")
            dialog.destroy()
        
        def add_all_process():
            # Group by process and add all windows from selected processes
            process_groups = {}
            for idx, window in window_data_map.items():
                process_name = window.get('process_name', '')
                if process_name not in process_groups:
                    process_groups[process_name] = []
                process_groups[process_name].append(window)
            
            event_tracker = self.command_recorder.event_tracker
            
            for process_name, windows in process_groups.items():
                if process_name:
                    event_tracker.add_process(process_name)
                    # All windows from this process will be auto-added by add_process
            
            # Clear pending windows
            event_tracker.clear_pending_windows()
            
            messagebox.showinfo("Processes Added", f"Added {len(process_groups)} process(es) to tracking.")
            dialog.destroy()
        
        add_btn = tk.Button(
            button_frame,
            text="Add Selected",
            bg='#4A9EFF',
            fg='#FFFFFF',
            font=('Segoe UI', 9),
            padx=20,
            pady=5,
            command=add_selected
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        add_all_btn = tk.Button(
            button_frame,
            text="Add All Processes",
            bg='#2D7A2D',
            fg='#FFFFFF',
            font=('Segoe UI', 9),
            padx=20,
            pady=5,
            command=add_all_process
        )
        add_all_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            bg='#4A4A4A',
            fg='#FFFFFF',
            font=('Segoe UI', 9),
            padx=20,
            pady=5,
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        dialog.grab_set()
    
    def _on_new_window_detected(self, hwnd, window_info):
        """Callback when EventTracker detects a new window."""
        if not self.is_recording:
            return
        
        # Check if this is a notification window itself (avoid recursive notifications)
        try:
            window_title = window_info.get('window_title', '')
            if 'New Window Detected' in window_title or 'New Windows Detected' in window_title:
                return
        except Exception:
            pass
        
        # Show notification (only if not already showing one for this window)
        # Use root.after to ensure this runs on the main thread
        self.root.after(0, lambda: self._show_window_notification(hwnd, window_info))
    
    def _show_window_notification(self, hwnd, window_info):
        """Show a toast notification for a newly detected window."""
        # Check if we already have a notification for this window
        if hwnd in getattr(self, '_active_notifications', set()):
            return
        
        # Track active notifications
        if not hasattr(self, '_active_notifications'):
            self._active_notifications = set()
        self._active_notifications.add(hwnd)
        
        process_name = window_info.get('process_name', 'Unknown')
        
        # Create notification window
        notif = tk.Toplevel(self.root)
        notif.title("New Window Detected")
        notif.overrideredirect(True)  # Remove window decorations
        notif.configure(bg='#2D2D2D')
        
        # Position near toolbar (top-right)
        self.root.update_idletasks()
        toolbar_x = self.root.winfo_x()
        toolbar_y = self.root.winfo_y()
        toolbar_width = self.root.winfo_width()
        
        notif_width = 350
        notif_height = 100
        notif_x = toolbar_x + toolbar_width - notif_width - 10
        notif_y = toolbar_y - notif_height - 10
        
        notif.geometry(f"{notif_width}x{notif_height}+{notif_x}+{notif_y}")
        
        # Content
        content_frame = tk.Frame(notif, bg='#2D2D2D')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        message_label = tk.Label(
            content_frame,
            text=f"New application detected:\n{process_name}",
            bg='#2D2D2D',
            fg='#FFFFFF',
            font=('Segoe UI', 9),
            anchor='w',
            justify=tk.LEFT
        )
        message_label.pack(fill=tk.X, pady=(0, 5))
        
        # Buttons frame
        btn_frame = tk.Frame(content_frame, bg='#2D2D2D')
        btn_frame.pack(fill=tk.X)
        
        def cleanup():
            """Remove from active notifications when notification is dismissed."""
            if hasattr(self, '_active_notifications'):
                self._active_notifications.discard(hwnd)
            try:
                notif.destroy()
            except Exception:
                pass
        
        def add_window():
            if self.command_recorder and self.command_recorder.event_tracker:
                self.command_recorder.event_tracker.add_window(hwnd)
            cleanup()
        
        def add_process():
            if self.command_recorder and self.command_recorder.event_tracker:
                self.command_recorder.event_tracker.add_process(process_name)
            cleanup()
        
        def ignore():
            cleanup()
        
        add_btn = tk.Button(
            btn_frame,
            text="Add",
            bg='#4A9EFF',
            fg='#FFFFFF',
            font=('Segoe UI', 8),
            padx=15,
            pady=3,
            command=add_window
        )
        add_btn.pack(side=tk.LEFT, padx=2)
        
        add_process_btn = tk.Button(
            btn_frame,
            text=f"Add All {process_name}",
            bg='#2D7A2D',
            fg='#FFFFFF',
            font=('Segoe UI', 8),
            padx=10,
            pady=3,
            command=add_process
        )
        add_process_btn.pack(side=tk.LEFT, padx=2)
        
        ignore_btn = tk.Button(
            btn_frame,
            text="Ignore",
            bg='#4A4A4A',
            fg='#FFFFFF',
            font=('Segoe UI', 8),
            padx=15,
            pady=3,
            command=ignore
        )
        ignore_btn.pack(side=tk.RIGHT, padx=2)
        
        # Auto-dismiss after 5 seconds
        def auto_dismiss():
            cleanup()
        
        notif.after(5000, auto_dismiss)
        
        # Make it clickable
        notif.attributes('-topmost', True)
    
    def process_command_session(self, command_history):
        """Process recorded commands and generate documentation."""
        try:
            Path("docs/generated").mkdir(parents=True, exist_ok=True)
            
            # Update API key if needed
            if self.api_key:
                os.environ["OPENAI_API_KEY"] = self.api_key
            
            # NOW process all screenshots - extract commands using OCR
            # This is where we do the image processing, not during capture
            processed_history = []
            for item in command_history:
                # Handle both old format (command, timestamp, screenshot_path) 
                # and new format (command, timestamp, screenshot_path, region)
                if len(item) == 4:
                    command, timestamp, screenshot_path, region = item
                else:
                    # Backward compatibility: old format without region
                    command, timestamp, screenshot_path = item
                    region = None
                
                # Process each screenshot to extract command text
                if not command or command.strip() == "":
                    # Extract from screenshot using OCR with focus region
                    try:
                        # Get window handle from region if available, otherwise from command_recorder
                        window_hwnd = None
                        if region and 'window_hwnd' in region:
                            window_hwnd = region.get('window_hwnd')
                        elif self.command_recorder and self.command_recorder.detected_terminal:
                            window_hwnd = self.command_recorder.detected_terminal
                        
                        # Extract text with region support
                        extracted = extract_terminal_text(
                            screenshot_path, 
                            region=region,
                            window_hwnd=window_hwnd
                        )
                        if extracted and extracted.strip():
                            command = extracted
                        else:
                            command = "Command captured"
                    except Exception:
                        # If OCR fails, just mark as captured
                        command = "Command captured"
                
                processed_history.append((command, timestamp, screenshot_path))
            
            # Generate documentation from processed commands
            # Pass session base path to use relative paths for screenshots
            session_base_path = None
            if self.session_manager and self.session_manager.current_session_dir:
                session_base_path = str(self.session_manager.current_session_dir)
            
            # Load events if available
            events = None
            if self.session_manager:
                try:
                    events_path = self.session_manager.get_events_path()
                    if events_path.exists():
                        import json
                        with open(events_path, "r", encoding="utf-8") as f:
                            events = json.load(f)
                except Exception:
                    pass
            
            summary = summarize_commands(
                processed_history, 
                include_screenshots=True,
                session_base_path=session_base_path,
                events=events
            )
            
            # Save to file in session folder
            if self.session_manager:
                output_path = self.session_manager.get_documentation_path("documentation.md")
            else:
                # Fallback to old location if no session manager
                output_path = Path("docs/generated") / f"command_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(summary)
            
            # Finalize session and add session info to documentation
            if self.session_manager:
                session_summary = self.session_manager.finalize_session()
                # Append session info to documentation
                session_info = "\n\n---\n\n## Session Information\n\n"
                session_info += f"- **Session ID:** `{session_summary.get('session_id', 'N/A')}`\n"
                session_info += f"- **Duration:** {session_summary.get('duration_seconds', 0):.1f} seconds\n"
                session_info += f"- **Screenshots:** {session_summary.get('screenshot_count', 0)}\n"
                
                # Add event summary if available
                if 'event_count' in session_summary:
                    session_info += f"- **Events Captured:** {session_summary.get('event_count', 0)}\n"
                if 'applications_used' in session_summary and session_summary['applications_used']:
                    session_info += f"- **Applications Used:** {', '.join(session_summary['applications_used'])}\n"
                
                session_info += f"- **Session Folder:** `{session_summary.get('session_dir', 'N/A')}`\n"
                
                with open(output_path, "a", encoding="utf-8") as f:
                    f.write(session_info)
            
            # Update UI
            self.root.after(0, lambda: self.capture_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.update_status_indicator('success'))
            self.root.after(0, lambda: self.show_notification(f"Documentation saved!\n{output_path.name}"))
            self.root.after(0, lambda: self.step_label.config(text=f"{len(processed_history)}"))
            
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
    
    def start_capture_process(self):
        """Start manual capture and documentation generation (legacy method)."""
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

