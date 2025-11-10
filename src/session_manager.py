"""
Session Manager - Organizes recording sessions into structured folders.
Each recording session gets its own folder with date, PC name, and session ID.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import socket


def get_pc_name_abbreviation() -> str:
    """
    Get abbreviated PC name for folder naming.
    Returns first 8 characters of hostname, uppercase, sanitized.
    """
    try:
        hostname = socket.gethostname()
        # Take first 8 chars, uppercase, remove invalid chars
        abbrev = hostname[:8].upper()
        # Remove invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            abbrev = abbrev.replace(char, '')
        return abbrev if abbrev else "PC"
    except Exception:
        return "PC"


def generate_session_folder_name(
    date_format: str = "%Y%m%d",
    include_time: bool = True,
    include_pc_name: bool = True,
    include_session_id: bool = True,
    custom_prefix: Optional[str] = None
) -> str:
    """
    Generate a session folder name with date, PC name, and session ID.
    
    Format: [PREFIX_]YYYYMMDD_HHMMSS_PCNAME_SESSIONID
    
    Args:
        date_format: Date format string (default: YYYYMMDD)
        include_time: Include time in folder name
        include_pc_name: Include PC name abbreviation
        include_session_id: Include unique session ID (timestamp-based)
        custom_prefix: Optional custom prefix (e.g., "REC", "DEMO")
    
    Returns:
        Folder name string (e.g., "20251109_224512_MATTHEWF_001")
    """
    parts = []
    
    # Add custom prefix if provided
    if custom_prefix:
        parts.append(custom_prefix.upper())
    
    # Add date
    now = datetime.now()
    date_str = now.strftime(date_format)
    parts.append(date_str)
    
    # Add time if requested
    if include_time:
        time_str = now.strftime("%H%M%S")
        parts.append(time_str)
    
    # Add PC name abbreviation
    if include_pc_name:
        pc_name = get_pc_name_abbreviation()
        parts.append(pc_name)
    
    # Add session ID (milliseconds for uniqueness)
    if include_session_id:
        session_id = now.strftime("%f")[:3]  # First 3 digits of microseconds
        parts.append(session_id)
    
    return "_".join(parts)


class SessionManager:
    """Manages recording session folders and file organization."""
    
    def __init__(self, base_dir: str = "docs/sessions"):
        """
        Initialize session manager.
        
        Args:
            base_dir: Base directory for all sessions (default: docs/sessions)
        """
        self.base_dir = Path(base_dir)
        self.current_session_dir: Optional[Path] = None
        self.session_id: Optional[str] = None
        self.session_start_time: Optional[datetime] = None
    
    def create_session_folder(
        self,
        custom_prefix: Optional[str] = None,
        folder_name: Optional[str] = None
    ) -> Path:
        """
        Create a new session folder.
        
        Args:
            custom_prefix: Optional prefix for folder name (e.g., "REC", "DEMO")
            folder_name: Optional custom folder name (if None, auto-generates)
        
        Returns:
            Path to the created session folder
        """
        # Generate folder name if not provided
        if folder_name is None:
            folder_name = generate_session_folder_name(custom_prefix=custom_prefix)
        
        # Create session directory
        session_dir = self.base_dir / folder_name
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for organization
        (session_dir / "screenshots").mkdir(exist_ok=True)
        (session_dir / "metadata").mkdir(exist_ok=True)
        (session_dir / "events").mkdir(exist_ok=True)
        
        self.current_session_dir = session_dir
        self.session_id = folder_name
        self.session_start_time = datetime.now()
        
        # Create session metadata file
        self._create_session_metadata()
        
        return session_dir
    
    def _create_session_metadata(self):
        """Create a metadata file for the session."""
        if not self.current_session_dir:
            return
        
        metadata = {
            "session_id": self.session_id,
            "start_time": self.session_start_time.isoformat() if self.session_start_time else None,
            "pc_name": socket.gethostname(),
            "pc_name_abbrev": get_pc_name_abbreviation(),
            "base_dir": str(self.base_dir),
            "session_dir": str(self.current_session_dir)
        }
        
        metadata_file = self.current_session_dir / "metadata" / "session_info.json"
        try:
            import json
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
        except Exception:
            # If JSON fails, create a simple text file
            metadata_file = self.current_session_dir / "metadata" / "session_info.txt"
            with open(metadata_file, "w", encoding="utf-8") as f:
                f.write(f"Session ID: {self.session_id}\n")
                f.write(f"Start Time: {self.session_start_time}\n")
                f.write(f"PC Name: {socket.gethostname()}\n")
                f.write(f"PC Abbreviation: {get_pc_name_abbreviation()}\n")
    
    def get_events_path(self) -> Path:
        """
        Get path for events.json file in the current session.
        
        Returns:
            Path object for the events.json file
        """
        if not self.current_session_dir:
            raise RuntimeError("No active session. Call create_session_folder() first.")
        
        return self.current_session_dir / "events" / "events.json"
    
    def save_events(self, events: List[Dict]) -> Path:
        """
        Save events to events.json file.
        
        Args:
            events: List of event dictionaries (from Event.to_dict())
        
        Returns:
            Path to the saved events file
        """
        events_path = self.get_events_path()
        
        try:
            import json
            with open(events_path, "w", encoding="utf-8") as f:
                json.dump(events, f, indent=2)
        except Exception:
            # If JSON fails, create a simple text file
            events_path = self.current_session_dir / "events" / "events.txt"
            with open(events_path, "w", encoding="utf-8") as f:
                for event in events:
                    f.write(f"{event.get('timestamp', '')} - {event.get('event_type', '')}\n")
        
        return events_path
    
    def get_screenshot_path(self, filename: Optional[str] = None) -> Path:
        """
        Get path for saving a screenshot in the current session.
        
        Args:
            filename: Optional custom filename (if None, auto-generates)
        
        Returns:
            Path object for the screenshot file
        """
        if not self.current_session_dir:
            raise RuntimeError("No active session. Call create_session_folder() first.")
        
        screenshots_dir = self.current_session_dir / "screenshots"
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            filename = f"command_{timestamp}.png"
        
        return screenshots_dir / filename
    
    def get_documentation_path(self, filename: Optional[str] = None) -> Path:
        """
        Get path for saving documentation in the current session.
        
        Args:
            filename: Optional custom filename (if None, auto-generates)
        
        Returns:
            Path object for the documentation file
        """
        if not self.current_session_dir:
            raise RuntimeError("No active session. Call create_session_folder() first.")
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"documentation_{timestamp}.md"
        
        return self.current_session_dir / filename
    
    def finalize_session(self) -> dict:
        """
        Finalize the current session and return session summary.
        
        Returns:
            Dictionary with session summary information
        """
        if not self.current_session_dir:
            return {}
        
        end_time = datetime.now()
        duration = None
        if self.session_start_time:
            duration = (end_time - self.session_start_time).total_seconds()
        
        # Count files
        screenshot_count = len(list((self.current_session_dir / "screenshots").glob("*.png")))
        
        # Load events if available
        events_summary = {}
        events_path = self.current_session_dir / "events" / "events.json"
        if events_path.exists():
            try:
                import json
                with open(events_path, "r", encoding="utf-8") as f:
                    events = json.load(f)
                    # Calculate summary
                    event_types = {}
                    applications_used = set()
                    processes_launched = set()
                    window_focus_changes = 0
                    
                    for event in events:
                        event_type = event.get('event_type', '')
                        event_types[event_type] = event_types.get(event_type, 0) + 1
                        
                        event_data = event.get('event_data', {})
                        if 'process_name' in event_data:
                            process_name = event_data['process_name']
                            if process_name:
                                applications_used.add(process_name)
                        
                        if event_type == 'process_launch' and 'process_name' in event_data:
                            processes_launched.add(event_data['process_name'])
                        
                        if event_type == 'window_focus':
                            window_focus_changes += 1
                    
                    events_summary = {
                        'event_count': len(events),
                        'event_types': event_types,
                        'applications_used': sorted(list(applications_used)),
                        'processes_launched': sorted(list(processes_launched)),
                        'window_focus_changes': window_focus_changes
                    }
            except Exception:
                pass
        
        summary = {
            "session_id": self.session_id,
            "session_dir": str(self.current_session_dir),
            "start_time": self.session_start_time.isoformat() if self.session_start_time else None,
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "screenshot_count": screenshot_count
        }
        
        # Add event summary if available
        if events_summary:
            summary.update(events_summary)
        
        # Update metadata file with end time
        metadata_file = self.current_session_dir / "metadata" / "session_info.json"
        if metadata_file.exists():
            try:
                import json
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                metadata["end_time"] = end_time.isoformat()
                metadata["duration_seconds"] = duration
                metadata["screenshot_count"] = screenshot_count
                
                # Add event summary if available
                if events_summary:
                    metadata.update(events_summary)
                
                with open(metadata_file, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2)
            except Exception:
                pass
        
        return summary
    
    def get_session_path(self, relative_path: str) -> Path:
        """
        Get a path relative to the current session directory.
        
        Args:
            relative_path: Relative path within session folder
        
        Returns:
            Full path within session directory
        """
        if not self.current_session_dir:
            raise RuntimeError("No active session. Call create_session_folder() first.")
        
        return self.current_session_dir / relative_path


# Convenience function for quick session folder creation
def create_session_folder(custom_prefix: Optional[str] = None) -> Path:
    """
    Quick function to create a session folder.
    
    Args:
        custom_prefix: Optional prefix (e.g., "REC", "DEMO")
    
    Returns:
        Path to created session folder
    """
    manager = SessionManager()
    return manager.create_session_folder(custom_prefix=custom_prefix)


