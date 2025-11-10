"""
Interaction Tracker - Tracks mouse clicks and builds interaction regions.
Provides desktop application equivalent of DOM tracking for web apps.
"""

import sys
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import deque

if sys.platform == 'win32':
    try:
        import win32gui
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
        win32gui = None
    
    try:
        from pynput import mouse
        PYNPUT_AVAILABLE = True
    except ImportError:
        PYNPUT_AVAILABLE = False
        mouse = None
else:
    WIN32_AVAILABLE = False
    PYNPUT_AVAILABLE = False
    win32gui = None
    mouse = None


class ClickEvent:
    """Represents a mouse click event."""
    
    def __init__(self, x: int, y: int, window_hwnd: Optional[int] = None, 
                 relative_x: Optional[int] = None, relative_y: Optional[int] = None,
                 timestamp: Optional[float] = None):
        self.x = x  # Screen coordinates
        self.y = y
        self.window_hwnd = window_hwnd
        self.relative_x = relative_x  # Coordinates relative to window
        self.relative_y = relative_y
        self.timestamp = timestamp or time.time()
    
    def __repr__(self):
        return f"ClickEvent(x={self.x}, y={self.y}, hwnd={self.window_hwnd}, rel=({self.relative_x}, {self.relative_y}))"


class InteractionTracker:
    """
    Tracks mouse clicks and calculates interaction regions.
    Similar to DOM tracking in web apps, but for desktop applications.
    """
    
    def __init__(self, max_clicks_per_window: int = 50, click_timeout: float = 10.0):
        """
        Initialize interaction tracker.
        
        Args:
            max_clicks_per_window: Maximum number of clicks to store per window
            click_timeout: Seconds after which old clicks are considered stale
        """
        self.max_clicks_per_window = max_clicks_per_window
        self.click_timeout = click_timeout
        
        # Store clicks per window: {window_hwnd: deque of ClickEvent}
        self.clicks_by_window: Dict[int, deque] = {}
        
        # Mouse listener
        self.mouse_listener = None
        self.is_tracking = False
    
    def start_tracking(self):
        """Start tracking mouse clicks globally."""
        if self.is_tracking:
            return
        
        if not PYNPUT_AVAILABLE or not mouse:
            return
        
        try:
            self.mouse_listener = mouse.Listener(on_click=self._on_click)
            self.mouse_listener.start()
            self.is_tracking = True
        except Exception:
            # Mouse tracking not available
            pass
    
    def stop_tracking(self):
        """Stop tracking mouse clicks."""
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except Exception:
                pass
            self.mouse_listener = None
        self.is_tracking = False
    
    def _on_click(self, x: int, y: int, button, pressed: bool):
        """Handle mouse click event."""
        if not pressed:  # Only track on button release
            return True
        
        if not WIN32_AVAILABLE or sys.platform != 'win32':
            return True
        
        try:
            # Get window under cursor
            window_hwnd = win32gui.WindowFromPoint((x, y))
            if not window_hwnd:
                return True
            
            # Get window rectangle
            try:
                left, top, right, bottom = win32gui.GetWindowRect(window_hwnd)
                relative_x = x - left
                relative_y = y - top
            except Exception:
                relative_x = None
                relative_y = None
            
            # Create click event
            click_event = ClickEvent(
                x=x,
                y=y,
                window_hwnd=window_hwnd,
                relative_x=relative_x,
                relative_y=relative_y
            )
            
            # Store click
            if window_hwnd not in self.clicks_by_window:
                self.clicks_by_window[window_hwnd] = deque(maxlen=self.max_clicks_per_window)
            
            self.clicks_by_window[window_hwnd].append(click_event)
            
            # Clean up old clicks
            self._cleanup_old_clicks()
            
        except Exception:
            # Silently fail - don't interrupt user workflow
            pass
        
        return True  # Keep listener running
    
    def _cleanup_old_clicks(self):
        """Remove clicks older than timeout."""
        current_time = time.time()
        windows_to_remove = []
        
        for window_hwnd, clicks in self.clicks_by_window.items():
            # Remove clicks older than timeout
            while clicks and (current_time - clicks[0].timestamp) > self.click_timeout:
                clicks.popleft()
            
            # Remove empty windows
            if not clicks:
                windows_to_remove.append(window_hwnd)
        
        for window_hwnd in windows_to_remove:
            del self.clicks_by_window[window_hwnd]
    
    def get_recent_clicks(self, window_hwnd: Optional[int] = None, 
                         max_clicks: Optional[int] = None) -> List[ClickEvent]:
        """
        Get recent clicks for a window.
        
        Args:
            window_hwnd: Window handle (None for all windows)
            max_clicks: Maximum number of clicks to return
        
        Returns:
            List of ClickEvent objects
        """
        self._cleanup_old_clicks()
        
        if window_hwnd is None:
            # Return clicks from all windows
            all_clicks = []
            for clicks in self.clicks_by_window.values():
                all_clicks.extend(clicks)
            # Sort by timestamp (most recent first)
            all_clicks.sort(key=lambda c: c.timestamp, reverse=True)
            if max_clicks:
                return all_clicks[:max_clicks]
            return all_clicks
        
        if window_hwnd not in self.clicks_by_window:
            return []
        
        clicks = list(self.clicks_by_window[window_hwnd])
        clicks.sort(key=lambda c: c.timestamp, reverse=True)
        if max_clicks:
            return clicks[:max_clicks]
        return clicks
    
    def get_focus_region(self, window_hwnd: Optional[int] = None, 
                        recent_seconds: float = 5.0,
                        min_clicks: int = 1) -> Optional[Dict]:
        """
        Calculate focus region from recent clicks.
        Returns bounding box of recent clicks within the specified time window.
        
        Args:
            window_hwnd: Window handle (None uses foreground window)
            recent_seconds: How many seconds back to look for clicks
            min_clicks: Minimum clicks needed to calculate a region
        
        Returns:
            Region dict with keys: x, y, width, height, window_hwnd, confidence
            Returns None if insufficient clicks
        """
        if not WIN32_AVAILABLE or sys.platform != 'win32':
            return None
        
        # Get window handle
        if window_hwnd is None:
            try:
                window_hwnd = win32gui.GetForegroundWindow()
            except Exception:
                return None
        
        if not window_hwnd:
            return None
        
        # Get recent clicks
        current_time = time.time()
        recent_clicks = [
            click for click in self.get_recent_clicks(window_hwnd)
            if (current_time - click.timestamp) <= recent_seconds
        ]
        
        if len(recent_clicks) < min_clicks:
            return None
        
        # Filter clicks that have relative coordinates
        clicks_with_rel = [c for c in recent_clicks if c.relative_x is not None and c.relative_y is not None]
        
        if not clicks_with_rel:
            return None
        
        # Calculate bounding box
        min_x = min(c.relative_x for c in clicks_with_rel)
        max_x = max(c.relative_x for c in clicks_with_rel)
        min_y = min(c.relative_y for c in clicks_with_rel)
        max_y = max(c.relative_y for c in clicks_with_rel)
        
        # Add padding (10% of dimensions, minimum 20px)
        width = max_x - min_x
        height = max_y - min_y
        padding_x = max(20, int(width * 0.1))
        padding_y = max(20, int(height * 0.1))
        
        region_x = max(0, min_x - padding_x)
        region_y = max(0, min_y - padding_y)
        region_width = width + (2 * padding_x)
        region_height = height + (2 * padding_y)
        
        # Get window dimensions to ensure region is within bounds
        try:
            left, top, right, bottom = win32gui.GetWindowRect(window_hwnd)
            window_width = right - left
            window_height = bottom - top
            
            # Clamp region to window bounds
            region_x = max(0, min(region_x, window_width - 1))
            region_y = max(0, min(region_y, window_height - 1))
            region_width = min(region_width, window_width - region_x)
            region_height = min(region_height, window_height - region_y)
        except Exception:
            pass
        
        # Calculate confidence based on click count and recency
        click_count = len(clicks_with_rel)
        avg_age = sum(current_time - c.timestamp for c in clicks_with_rel) / click_count
        recency_score = max(0, 1.0 - (avg_age / recent_seconds))
        click_score = min(1.0, click_count / 5.0)  # Normalize to 5 clicks = max
        confidence = (recency_score * 0.6 + click_score * 0.4)
        
        return {
            'x': region_x,
            'y': region_y,
            'width': region_width,
            'height': region_height,
            'window_hwnd': window_hwnd,
            'confidence': confidence
        }
    
    def clear_clicks(self, window_hwnd: Optional[int] = None):
        """Clear stored clicks for a window (or all windows if None)."""
        if window_hwnd is None:
            self.clicks_by_window.clear()
        elif window_hwnd in self.clicks_by_window:
            del self.clicks_by_window[window_hwnd]

