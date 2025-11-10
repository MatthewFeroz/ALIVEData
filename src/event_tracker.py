"""
Event Tracker - Monitors system events like window focus changes, application launches, etc.
Provides comprehensive event tracking for recording sessions.
"""

import sys
import threading
import time
from datetime import datetime
from typing import List, Dict, Optional, Callable

if sys.platform == 'win32':
    try:
        import win32gui
        import win32con
        import win32process
        import win32api
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
        win32gui = None
        win32con = None
        win32process = None
        win32api = None
    
    try:
        import psutil
        PSUTIL_AVAILABLE = True
    except ImportError:
        PSUTIL_AVAILABLE = False
        psutil = None
else:
    WIN32_AVAILABLE = False
    PSUTIL_AVAILABLE = False
    win32gui = None
    win32con = None
    win32process = None
    win32api = None
    psutil = None


class Event:
    """Represents a system event."""
    
    def __init__(self, event_type: str, event_data: Dict, timestamp: Optional[datetime] = None):
        self.event_type = event_type
        self.event_data = event_data
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'event_data': self.event_data
        }
    
    def __repr__(self):
        return f"Event(type={self.event_type}, time={self.timestamp}, data={self.event_data})"


class EventTracker:
    """
    Tracks system events like window focus changes, application launches, etc.
    """
    
    def __init__(self, on_event: Optional[Callable] = None, debounce_window_focus: float = 0.5, 
                 tracked_windows: Optional[List[int]] = None, tracked_processes: Optional[List[str]] = None):
        """
        Initialize event tracker.
        
        Args:
            on_event: Optional callback function(event) called when event occurs
            debounce_window_focus: Seconds to debounce window focus changes
            tracked_windows: Optional list of window handles (hwnd) to track. If None, tracks all.
            tracked_processes: Optional list of process names to track. If None, tracks all.
        """
        self.on_event = on_event
        self.debounce_window_focus = debounce_window_focus
        
        # Window/process filtering
        self.tracked_windows = set(tracked_windows) if tracked_windows else None
        self.tracked_processes = set(p.lower() for p in tracked_processes) if tracked_processes else None
        
        # Pending windows tracking
        self.pending_windows: List[Dict] = []  # Windows detected but not yet tracked
        self.pending_windows_lock = threading.Lock()  # Lock for pending windows
        self.on_new_window_callback: Optional[Callable] = None  # Callback when new window detected
        self.notified_windows: Set[int] = set()  # Windows we've already notified about
        self.notified_windows_lock = threading.Lock()  # Lock for notified windows
        self.last_notification_time: Dict[int, float] = {}  # Track last notification time per window
        self.notification_cooldown = 10.0  # Don't notify about same window within 10 seconds
        
        # Event storage
        self.events: List[Event] = []
        self._events_lock = threading.Lock()
        
        # Tracking state
        self.is_tracking = False
        self._stop_tracking = False
        
        # Monitoring threads
        self.window_monitor_thread = None
        self.process_monitor_thread = None
        
        # Window tracking
        self.last_foreground_window = None
        self.last_focus_change_time = 0
        self.known_windows: Dict[int, Dict] = {}  # hwnd -> window info
        self.known_processes: Dict[int, Dict] = {}  # pid -> process info
        
        # Process tracking (for psutil)
        self.last_process_check_time = 0
        self.process_check_interval = 2.0  # Check every 2 seconds
    
    def start_tracking(self):
        """Start tracking system events."""
        if self.is_tracking:
            return
        
        self.is_tracking = True
        self._stop_tracking = False
        self.events = []
        self.last_foreground_window = None
        
        # Initialize current foreground window
        if WIN32_AVAILABLE and sys.platform == 'win32':
            try:
                self.last_foreground_window = win32gui.GetForegroundWindow()
                self._update_window_info(self.last_foreground_window)
            except Exception:
                pass
        
        # Start monitoring threads
        if WIN32_AVAILABLE and sys.platform == 'win32':
            self.window_monitor_thread = threading.Thread(target=self._monitor_windows, daemon=True)
            self.window_monitor_thread.start()
        
        if PSUTIL_AVAILABLE:
            self.process_monitor_thread = threading.Thread(target=self._monitor_processes, daemon=True)
            self.process_monitor_thread.start()
    
    def stop_tracking(self):
        """Stop tracking system events."""
        self._stop_tracking = True
        self.is_tracking = False
        
        # Wait for threads to finish (with timeout)
        if self.window_monitor_thread:
            self.window_monitor_thread.join(timeout=1.0)
        if self.process_monitor_thread:
            self.process_monitor_thread.join(timeout=1.0)
    
    def _monitor_windows(self):
        """Monitor window focus changes."""
        while not self._stop_tracking and self.is_tracking:
            if not WIN32_AVAILABLE or sys.platform != 'win32':
                time.sleep(1)
                continue
            
            try:
                current_window = win32gui.GetForegroundWindow()
                
                if current_window != self.last_foreground_window:
                    current_time = time.time()
                    
                    # Debounce rapid focus changes
                    if current_time - self.last_focus_change_time >= self.debounce_window_focus:
                        self._handle_window_focus_change(current_window)
                        self.last_foreground_window = current_window
                        self.last_focus_change_time = current_time
                
                # Check for new windows
                self._check_for_new_windows()
                
                time.sleep(0.1)  # Check every 100ms
            except Exception:
                time.sleep(0.5)
    
    def _monitor_processes(self):
        """Monitor process launches and terminations."""
        if not PSUTIL_AVAILABLE:
            return
        
        while not self._stop_tracking and self.is_tracking:
            try:
                current_time = time.time()
                
                # Check processes periodically
                if current_time - self.last_process_check_time >= self.process_check_interval:
                    self._check_processes()
                    self.last_process_check_time = current_time
                
                time.sleep(1.0)
            except Exception:
                time.sleep(2.0)
    
    def _handle_window_focus_change(self, hwnd: int):
        """Handle window focus change event."""
        if not hwnd or hwnd == 0:
            return
        
        try:
            window_info = self._get_window_info(hwnd)
            if not window_info:
                return
            
            # Check if window should be tracked
            if not self._should_track_window(hwnd, window_info):
                return
            
            # Check if this is a new window (application launch)
            if hwnd not in self.known_windows:
                self._record_app_launch(hwnd, window_info)
            
            # Record focus change
            self._record_window_focus(hwnd, window_info)
            
            # Update known windows
            self.known_windows[hwnd] = window_info
            
        except Exception:
            pass
    
    def _check_for_new_windows(self):
        """Check for newly created windows."""
        if not WIN32_AVAILABLE or sys.platform != 'win32':
            return
        
        try:
            def enum_handler(hwnd, ctx):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        if hwnd not in self.known_windows:
                            window_info = self._get_window_info(hwnd)
                            if window_info and window_info.get('process_name'):
                                process_name = window_info.get('process_name', '').lower()
                                
                                # Smart auto-add: If process is already tracked, auto-add this window
                                if self.tracked_processes and process_name in self.tracked_processes:
                                    # Auto-add window from tracked process
                                    if self.tracked_windows is None:
                                        self.tracked_windows = set()
                                    self.tracked_windows.add(hwnd)
                                    # Record as app launch
                                    self._record_app_launch(hwnd, window_info)
                                    self.known_windows[hwnd] = window_info
                                    return True
                                
                                # Check if should track this window
                                if self._should_track_window(hwnd, window_info):
                                    # New window detected and should be tracked
                                    self._record_app_launch(hwnd, window_info)
                                    self.known_windows[hwnd] = window_info
                                else:
                                    # Window detected but doesn't match filters - add to pending
                                    with self.pending_windows_lock:
                                        # Check if already in pending (avoid duplicates)
                                        if not any(p.get('window_hwnd') == hwnd for p in self.pending_windows):
                                            # Check if we've already notified about this window recently
                                            current_time = time.time()
                                            last_notified = self.last_notification_time.get(hwnd, 0)
                                            
                                            # Only add to pending and notify if not recently notified
                                            if current_time - last_notified >= self.notification_cooldown:
                                                self.pending_windows.append({
                                                    'window_hwnd': hwnd,
                                                    'window_title': window_info.get('window_title', ''),
                                                    'process_name': window_info.get('process_name', ''),
                                                    'executable_path': window_info.get('executable_path', ''),
                                                    'timestamp': current_time
                                                })
                                                
                                                # Mark as notified and record time
                                                with self.notified_windows_lock:
                                                    self.notified_windows.add(hwnd)
                                                self.last_notification_time[hwnd] = current_time
                                                
                                                # Call callback if set
                                                if self.on_new_window_callback:
                                                    try:
                                                        self.on_new_window_callback(hwnd, window_info)
                                                    except Exception:
                                                        pass
                except Exception:
                    pass
                return True
            
            win32gui.EnumWindows(enum_handler, None)
        except Exception:
            pass
    
    def _check_processes(self):
        """Check for new and terminated processes."""
        if not PSUTIL_AVAILABLE:
            return
        
        try:
            current_pids = set()
            
            # Get all current processes
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
                try:
                    pid = proc.info['pid']
                    current_pids.add(pid)
                    
                    # Check if this is a new process
                    if pid not in self.known_processes:
                        # Filter out system processes and check if should track
                        if self._should_track_process(proc.info):
                            self._record_process_launch(proc.info)
                            self.known_processes[pid] = proc.info
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Check for terminated processes
            terminated_pids = set(self.known_processes.keys()) - current_pids
            for pid in terminated_pids:
                process_info = self.known_processes.pop(pid, None)
                if process_info:
                    self._record_process_termination(process_info)
                    
        except Exception:
            pass
    
    def add_window(self, hwnd: int):
        """
        Dynamically add a window to tracking.
        
        Args:
            hwnd: Window handle to add
        """
        if self.tracked_windows is None:
            self.tracked_windows = set()
        self.tracked_windows.add(hwnd)
        
        # Remove from pending and notified lists
        with self.pending_windows_lock:
            self.pending_windows = [w for w in self.pending_windows if w.get('window_hwnd') != hwnd]
        with self.notified_windows_lock:
            self.notified_windows.discard(hwnd)
        
        # If window is in known_windows, ensure it's tracked
        if hwnd in self.known_windows:
            window_info = self.known_windows[hwnd]
            if self._should_track_window(hwnd, window_info):
                # Record as app launch if not already recorded
                if hwnd not in [e.event_data.get('window_hwnd') for e in self.events if e.event_type == 'app_launch']:
                    self._record_app_launch(hwnd, window_info)
    
    def add_process(self, process_name: str):
        """
        Dynamically add a process to tracking.
        
        Args:
            process_name: Process name to add (will be lowercased)
        """
        if self.tracked_processes is None:
            self.tracked_processes = set()
        self.tracked_processes.add(process_name.lower())
        
        # Auto-add all existing windows from this process
        for hwnd, window_info in self.known_windows.items():
            if window_info.get('process_name', '').lower() == process_name.lower():
                if self.tracked_windows is None:
                    self.tracked_windows = set()
                self.tracked_windows.add(hwnd)
                # Remove from pending and notified lists
                with self.pending_windows_lock:
                    self.pending_windows = [w for w in self.pending_windows if w.get('window_hwnd') != hwnd]
                with self.notified_windows_lock:
                    self.notified_windows.discard(hwnd)
    
    def get_pending_windows(self) -> List[Dict]:
        """
        Get list of windows that were detected but don't match current filters.
        
        Returns:
            List of window info dictionaries
        """
        with self.pending_windows_lock:
            return self.pending_windows.copy()
    
    def clear_pending_windows(self):
        """Clear the pending windows list."""
        with self.pending_windows_lock:
            self.pending_windows.clear()
    
    def set_new_window_callback(self, callback: Callable):
        """
        Set callback function to be called when new window is detected.
        
        Args:
            callback: Function that takes (hwnd, window_info) as arguments
        """
        self.on_new_window_callback = callback
    
    def _should_track_window(self, hwnd: int, window_info: Dict) -> bool:
        """
        Check if a window should be tracked based on filters.
        
        Args:
            hwnd: Window handle
            window_info: Window information dict
        
        Returns:
            True if window should be tracked, False otherwise
        """
        # If no filters set, track all (backward compatibility)
        if self.tracked_windows is None and self.tracked_processes is None:
            return self._is_user_process(window_info)
        
        # Check window handle filter
        if self.tracked_windows is not None:
            if hwnd in self.tracked_windows:
                return True
        
        # Check process name filter
        if self.tracked_processes is not None:
            process_name = window_info.get('process_name', '').lower()
            if process_name in self.tracked_processes:
                return True
        
        # If filters are set but window doesn't match, don't track
        return False
    
    def _should_track_process(self, process_info: Dict) -> bool:
        """
        Check if a process should be tracked based on filters.
        
        Args:
            process_info: Process information dict
        
        Returns:
            True if process should be tracked, False otherwise
        """
        # If no filters set, track user processes (backward compatibility)
        if self.tracked_processes is None:
            return self._is_user_process(process_info)
        
        # Check process name filter
        process_name = process_info.get('name', '').lower()
        return process_name in self.tracked_processes
    
    def _is_user_process(self, process_info: Dict) -> bool:
        """Check if process is a user application (not system process)."""
        if not process_info:
            return False
        
        process_name = process_info.get('name', '').lower()
        exe_path = process_info.get('exe', '').lower()
        
        # Filter out system processes
        system_processes = [
            'svchost.exe', 'dwm.exe', 'winlogon.exe', 'csrss.exe',
            'services.exe', 'lsass.exe', 'smss.exe', 'explorer.exe',
            'system', 'dllhost.exe', 'conhost.exe', 'audiodg.exe'
        ]
        
        if process_name in system_processes:
            return False
        
        # Filter out processes in system directories
        system_dirs = [
            r'c:\windows\system32',
            r'c:\windows\syswow64',
            r'c:\program files\windows'
        ]
        
        if exe_path:
            for sys_dir in system_dirs:
                if sys_dir in exe_path:
                    return False
        
        return True
    
    def _get_window_info(self, hwnd: int) -> Optional[Dict]:
        """Get information about a window."""
        if not WIN32_AVAILABLE or sys.platform != 'win32' or not hwnd:
            return None
        
        try:
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get process info
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process_info = self._get_process_info(pid)
            except Exception:
                process_info = {}
            
            return {
                'window_hwnd': hwnd,
                'window_title': window_title,
                'process_id': pid if 'pid' in locals() else None,
                'process_name': process_info.get('name', ''),
                'executable_path': process_info.get('exe', '')
            }
        except Exception:
            return None
    
    def _get_process_info(self, pid: int) -> Dict:
        """Get process information."""
        info = {}
        
        # Try psutil first
        if PSUTIL_AVAILABLE:
            try:
                proc = psutil.Process(pid)
                info = {
                    'pid': pid,
                    'name': proc.name(),
                    'exe': proc.exe() if proc.exe() else '',
                    'create_time': proc.create_time()
                }
                return info
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Fallback to Windows API
        if WIN32_AVAILABLE and sys.platform == 'win32':
            try:
                handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
                exe_path = win32process.GetModuleFileNameEx(handle, 0)
                info = {
                    'pid': pid,
                    'exe': exe_path
                }
                win32api.CloseHandle(handle)
            except Exception:
                pass
        
        return info
    
    def _update_window_info(self, hwnd: int):
        """Update cached window information."""
        if hwnd:
            window_info = self._get_window_info(hwnd)
            if window_info:
                self.known_windows[hwnd] = window_info
    
    def _record_window_focus(self, hwnd: int, window_info: Dict):
        """Record a window focus change event."""
        event = Event(
            event_type='window_focus',
            event_data={
                'window_title': window_info.get('window_title', ''),
                'process_name': window_info.get('process_name', ''),
                'executable_path': window_info.get('executable_path', ''),
                'window_hwnd': hwnd
            }
        )
        self._add_event(event)
    
    def _record_app_launch(self, hwnd: int, window_info: Dict):
        """Record an application launch event."""
        event = Event(
            event_type='app_launch',
            event_data={
                'window_title': window_info.get('window_title', ''),
                'process_name': window_info.get('process_name', ''),
                'executable_path': window_info.get('executable_path', ''),
                'window_hwnd': hwnd
            }
        )
        self._add_event(event)
    
    def _record_process_launch(self, process_info: Dict):
        """Record a process launch event."""
        event = Event(
            event_type='process_launch',
            event_data={
                'process_name': process_info.get('name', ''),
                'executable_path': process_info.get('exe', ''),
                'process_id': process_info.get('pid')
            }
        )
        self._add_event(event)
    
    def _record_process_termination(self, process_info: Dict):
        """Record a process termination event."""
        event = Event(
            event_type='process_termination',
            event_data={
                'process_name': process_info.get('name', ''),
                'executable_path': process_info.get('exe', ''),
                'process_id': process_info.get('pid')
            }
        )
        self._add_event(event)
    
    def record_command_event(self, command: str, screenshot_path: str, region: Optional[Dict] = None):
        """Record a command execution event."""
        event_data = {
            'command': command,
            'screenshot_path': screenshot_path
        }
        
        # Add current foreground window info
        if WIN32_AVAILABLE and sys.platform == 'win32':
            try:
                current_window = win32gui.GetForegroundWindow()
                window_info = self._get_window_info(current_window)
                if window_info:
                    event_data['active_window_title'] = window_info.get('window_title', '')
                    event_data['active_process_name'] = window_info.get('process_name', '')
            except Exception:
                pass
        
        if region:
            event_data['focus_region'] = region
        
        event = Event(
            event_type='command',
            event_data=event_data
        )
        self._add_event(event)
    
    def _add_event(self, event: Event):
        """Add an event to the event list and call callback."""
        with self._events_lock:
            self.events.append(event)
        
        # Call callback if provided
        if self.on_event:
            try:
                self.on_event(event)
            except Exception:
                pass
    
    def get_events(self) -> List[Event]:
        """Get all tracked events."""
        with self._events_lock:
            return self.events.copy()
    
    def get_event_summary(self) -> Dict:
        """Get summary statistics of tracked events."""
        with self._events_lock:
            event_types = {}
            applications_used = set()
            processes_launched = set()
            window_focus_changes = 0
            
            for event in self.events:
                # Count event types
                event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
                
                # Track applications
                if 'process_name' in event.event_data:
                    process_name = event.event_data['process_name']
                    if process_name:
                        applications_used.add(process_name)
                
                # Track processes launched
                if event.event_type == 'process_launch':
                    if 'process_name' in event.event_data:
                        processes_launched.add(event.event_data['process_name'])
                
                # Count focus changes
                if event.event_type == 'window_focus':
                    window_focus_changes += 1
            
            return {
                'total_events': len(self.events),
                'event_types': event_types,
                'applications_used': sorted(list(applications_used)),
                'processes_launched': sorted(list(processes_launched)),
                'window_focus_changes': window_focus_changes
            }

