"""
Command Recorder - Detects terminal windows and captures commands.
"""

import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict

if sys.platform == 'win32':
    try:
        import win32gui
        import win32con
        import win32ui
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
        win32gui = None
        win32con = None
        win32ui = None
    
    try:
        from pynput import keyboard, mouse
        PYNPUT_AVAILABLE = True
    except ImportError:
        PYNPUT_AVAILABLE = False
        keyboard = None
        mouse = None
else:
    # Placeholder for non-Windows (not implemented)
    WIN32_AVAILABLE = False
    PYNPUT_AVAILABLE = False
    win32gui = None
    win32con = None
    win32ui = None
    keyboard = None
    mouse = None


class CommandRecorder:
    """Records commands from terminal windows."""
    
    # Terminal window title patterns to detect
    TERMINAL_PATTERNS = [
        'cmd.exe',
        'powershell',
        'windows terminal',
        'command prompt',
        'terminal',
        'pwsh.exe'
    ]
    
    def __init__(self, on_command_captured=None, session_manager=None):
        """
        Initialize command recorder.
        
        Args:
            on_command_captured: Callback function(command, screenshot_path, timestamp)
            session_manager: Optional SessionManager instance for organizing files
        """
        self.is_recording = False
        self.detected_terminal = None
        # Extended command history: (command, timestamp, screenshot_path, region)
        self.command_history: List[Tuple[str, datetime, str, Optional[Dict]]] = []
        self.on_command_captured = on_command_captured
        self.session_manager = session_manager
        
        # Monitoring threads
        self.window_monitor_thread = None
        self.keyboard_listener = None
        self.mouse_listener = None
        self._stop_monitoring = False
        
        # Interaction tracking
        from .interaction_tracker import InteractionTracker
        self.interaction_tracker = InteractionTracker()
        
        # Event tracking
        from .event_tracker import EventTracker
        self.event_tracker = EventTracker()
        
        # Last capture time for debouncing
        self.last_capture_time = 0
        self.min_capture_interval = 2.0  # Minimum seconds between captures
    
    def start_recording(self):
        """Start recording commands."""
        if self.is_recording:
            return
        
        self.is_recording = True
        self._stop_monitoring = False
        self.command_history = []
        self.detected_terminal = None
        
        # Start monitoring threads
        self.window_monitor_thread = threading.Thread(target=self._monitor_windows, daemon=True)
        self.window_monitor_thread.start()
        
        # Start keyboard listener
        if sys.platform == 'win32' and PYNPUT_AVAILABLE and keyboard:
            try:
                self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
                self.keyboard_listener.start()
            except Exception:
                # Keyboard monitoring not available
                pass
        
        # Start mouse tracking for interaction regions
        try:
            self.interaction_tracker.start_tracking()
        except Exception:
            # Mouse tracking not available
            pass
        
        # Start event tracking
        try:
            self.event_tracker.start_tracking()
        except Exception:
            # Event tracking not available
            pass
    
    def stop_recording(self):
        """
        Stop recording and return command history.
        This should ONLY be called explicitly by the user via button press.
        """
        # Set flags to stop monitoring
        self._stop_monitoring = True
        
        # Stop keyboard listener gracefully
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
            except Exception:
                pass
            self.keyboard_listener = None
        
        # Stop mouse tracking
        try:
            self.interaction_tracker.stop_tracking()
        except Exception:
            pass
        
        # Stop event tracking
        try:
            self.event_tracker.stop_tracking()
        except Exception:
            pass
        
        # Mark recording as stopped
        self.is_recording = False
        
        # Return a copy of the command history
        return self.command_history.copy()
    
    def _monitor_windows(self):
        """Monitor for terminal windows opening."""
        while not self._stop_monitoring and self.is_recording:
            if sys.platform != 'win32' or not WIN32_AVAILABLE:
                time.sleep(1)
                continue
            
            try:
                # Check for terminal windows
                terminal = self._find_terminal_window()
                if terminal and terminal != self.detected_terminal:
                    self.detected_terminal = terminal
                    # Terminal detected - ready to capture commands
                
                time.sleep(0.5)  # Check every 500ms
            except Exception:
                time.sleep(1)
    
    def _is_terminal_window(self, hwnd) -> bool:
        """Check if a window handle is a terminal window."""
        if sys.platform != 'win32' or not WIN32_AVAILABLE:
            return False
        
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return False
            
            window_title = win32gui.GetWindowText(hwnd).lower()
            for pattern in self.TERMINAL_PATTERNS:
                if pattern in window_title:
                    return True
            return False
        except Exception:
            return False
    
    def _find_terminal_window(self) -> Optional[int]:
        """Find active terminal window handle."""
        if sys.platform != 'win32' or not WIN32_AVAILABLE:
            return None
        
        foreground_window = win32gui.GetForegroundWindow()
        terminal_windows = []
        
        def enum_handler(hwnd, ctx):
            try:
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd).lower()
                    for pattern in self.TERMINAL_PATTERNS:
                        if pattern in window_title:
                            ctx.append((hwnd, hwnd == foreground_window))
                            break
            except Exception:
                pass
            return True
        
        try:
            win32gui.EnumWindows(enum_handler, terminal_windows)
            
            # Prefer foreground window, but also accept any visible terminal
            for hwnd, is_foreground in terminal_windows:
                if is_foreground:
                    return hwnd
            
            # If no foreground terminal, return the first visible terminal
            if terminal_windows:
                return terminal_windows[0][0]
            
            return None
        except Exception:
            return None
    
    def _on_key_press(self, key):
        """Handle keyboard press events."""
        # Always return True to keep listener running
        if not self.is_recording or not self.detected_terminal:
            return True
        
        if not PYNPUT_AVAILABLE or not keyboard:
            return True
        
        # Check if Enter key was pressed
        try:
            if key == keyboard.Key.enter:
                # Debounce: don't capture too frequently
                current_time = time.time()
                if current_time - self.last_capture_time < self.min_capture_interval:
                    return True
                
                # Check if terminal is still active
                if sys.platform == 'win32' and WIN32_AVAILABLE:
                    try:
                        active_window = win32gui.GetForegroundWindow()
                        # Check if active window is a terminal (might be different from detected_terminal)
                        if active_window == self.detected_terminal or self._is_terminal_window(active_window):
                            # Update detected terminal if it changed
                            if active_window != self.detected_terminal:
                                self.detected_terminal = active_window
                            
                            # Capture immediately to catch the command before it executes
                            # Use a thread to avoid blocking the keyboard listener
                            def immediate_capture():
                                # CRITICAL: Double-check recording is still active
                                if not self.is_recording or self._stop_monitoring:
                                    return
                                
                                try:
                                    # Re-check terminal window at capture time
                                    current_terminal = self._find_terminal_window()
                                    if current_terminal:
                                        self.detected_terminal = current_terminal
                                    
                                    # Capture the command immediately (before execution)
                                    self._capture_command()
                                except Exception:
                                    # Don't let capture errors stop recording
                                    pass
                            
                            capture_thread = threading.Thread(target=immediate_capture, daemon=True)
                            capture_thread.start()
                    except Exception:
                        pass
        except AttributeError:
            # Key might not have .enter attribute
            pass
        
        # Return True to keep the listener running
        return True
    
    def _capture_command(self):
        """Capture command from terminal window."""
        # Double-check recording is still active
        if not self.is_recording:
            return
            
        if not self.detected_terminal or sys.platform != 'win32' or not WIN32_AVAILABLE:
            return
        
        try:
            # Update last capture time
            self.last_capture_time = time.time()
            
            # Get focus region from interaction tracker
            focus_region = None
            try:
                focus_region = self.interaction_tracker.get_focus_region(
                    window_hwnd=self.detected_terminal,
                    recent_seconds=5.0,
                    min_clicks=1
                )
            except Exception:
                # If region tracking fails, continue without it
                pass
            
            # Capture screenshot of terminal window (just save, don't process yet)
            screenshot_path = self._capture_window_screenshot(self.detected_terminal)
            
            # Don't extract command text here - we'll do OCR later when processing
            # Just store empty command for now
            command = ""
            
            # Store the capture in history (image saved, but not processed)
            # Extended format: (command, timestamp, screenshot_path, region)
            timestamp = datetime.now()
            self.command_history.append((command, timestamp, screenshot_path, focus_region))
            
            # Record command event
            try:
                self.event_tracker.record_command_event(command, screenshot_path, focus_region)
            except Exception:
                pass
            
            # Call callback if provided (but don't do OCR processing here)
            # Just notify that an image was captured
            if self.on_command_captured:
                try:
                    self.on_command_captured(command, screenshot_path, timestamp)
                except Exception:
                    # Don't let callback errors stop recording
                    pass
        except Exception as e:
            # Silently fail - don't interrupt user workflow or stop recording
            # Recording should continue even if one capture fails
            pass
    
    def _capture_window_screenshot(self, hwnd) -> str:
        """Capture screenshot of specific window."""
        if sys.platform != 'win32' or not WIN32_AVAILABLE:
            return ""
        
        try:
            # Use capture module's window capture function
            from .capture import capture_window
            
            # Use session manager if available, otherwise fallback to old location
            if self.session_manager:
                screenshot_path = str(self.session_manager.get_screenshot_path())
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                screenshot_path = f"docs/generated/command_{timestamp}.png"
                Path("docs/generated").mkdir(parents=True, exist_ok=True)
            
            capture_window(hwnd, screenshot_path)
            return screenshot_path
        except Exception:
            # Fallback: use full screen capture
            try:
                from .capture import capture_screen
                
                # Use session manager if available
                if self.session_manager:
                    screenshot_path = str(self.session_manager.get_screenshot_path())
                else:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                    screenshot_path = f"docs/generated/command_{timestamp}.png"
                    Path("docs/generated").mkdir(parents=True, exist_ok=True)
                
                capture_screen(screenshot_path)
                return screenshot_path
            except Exception:
                # Last resort: return empty path
                return ""
    
    def _extract_terminal_command(self, hwnd) -> str:
        """Extract command text from terminal window."""
        if sys.platform != 'win32' or not WIN32_AVAILABLE:
            return ""
        
        try:
            # Try to get window text directly (limited - usually just title)
            window_text = win32gui.GetWindowText(hwnd)
            
            # For terminal windows, we'll rely on OCR from screenshot
            # This is a placeholder - actual implementation would need to:
            # 1. Get terminal buffer content (complex, terminal-specific)
            # 2. Or use OCR on the screenshot (fallback)
            
            # For now, return empty - OCR will extract it from screenshot
            return ""
        except Exception:
            return ""

