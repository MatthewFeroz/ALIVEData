"""
Development mode: Run GUI directly with auto-reload on file changes.
This is MUCH faster than rebuilding the EXE every time.

Usage:
    python dev_gui.py
"""

import sys
import subprocess
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ReloadHandler(FileSystemEventHandler):
    """Handler that restarts the script when Python files change."""
    
    def __init__(self, script_path):
        self.script_path = script_path
        self.process = None
        self.last_reload_time = 0
        self.reload_cooldown = 1  # Minimum seconds between reloads
        self.python_files = {'.py'}
        self.exclude_dirs = {'build', 'dist', '__pycache__', '.git', 'venv', '.venv'}
        
    def should_reload(self, file_path):
        """Check if we should reload based on the changed file."""
        path = Path(file_path)
        
        # Only watch Python files
        if path.suffix not in self.python_files:
            return False
        
        # Skip excluded directories
        for part in path.parts:
            if part in self.exclude_dirs:
                return False
        
        # Skip the dev script itself
        if path.name in ('dev_toolbar.py', 'dev_gui.py'):
            return False
        
        return True
    
    def start_process(self):
        """Start the GUI process."""
        if self.process and self.process.poll() is None:
            # Process still running, kill it
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        print(f"\n🚀 Starting GUI...")
        self.process = subprocess.Popen(
            [sys.executable, str(self.script_path)],
            stdout=sys.stdout,
            stderr=sys.stderr
        )
    
    def on_modified(self, event):
        """Called when a file is modified."""
        if event.is_directory:
            return
        
        if not self.should_reload(event.src_path):
            return
        
        # Cooldown to prevent rapid reloads
        current_time = time.time()
        if current_time - self.last_reload_time < self.reload_cooldown:
            return
        
        self.last_reload_time = current_time
        
        print(f"\n{'='*60}")
        print(f"📝 File changed: {Path(event.src_path).name}")
        print(f"🔄 Reloading GUI...")
        print(f"{'='*60}\n")
        
        self.start_process()


def main():
    """Main function to start the development server."""
    script_dir = Path(__file__).parent.parent
    gui_script = script_dir / 'src' / 'gui.py'
    
    if not gui_script.exists():
        print(f"❌ Error: {gui_script} not found!")
        sys.exit(1)
    
    print("="*60)
    print("🔧 ALIVE Data - Development Mode (Hot Reload)")
    print("="*60)
    print("📝 Running gui.py directly (no EXE rebuild needed)")
    print("🔄 Auto-reloads when you save changes")
    print("="*60)
    print("\n👀 Watching for file changes...")
    print("   (Press Ctrl+C to stop)\n")
    
    # Set up file watcher
    event_handler = ReloadHandler(gui_script)
    observer = Observer()
    observer.schedule(event_handler, str(script_dir), recursive=True)
    
    # Start initial process
    event_handler.start_process()
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
            # Check if process died
            if event_handler.process and event_handler.process.poll() is not None:
                print("\n⚠️  Process exited. Waiting for file changes to restart...")
                # Don't restart automatically, wait for file change
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping...")
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
            try:
                event_handler.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                event_handler.process.kill()
    
    observer.join()
    print("👋 Goodbye!")


if __name__ == "__main__":
    main()

