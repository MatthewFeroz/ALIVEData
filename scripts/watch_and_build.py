"""
Development script that watches for file changes and automatically rebuilds the EXE.
Run this script while developing to have the EXE automatically rebuild when you save changes.

Usage:
    python watch_and_build.py          # Watch and build toolbar
    python watch_and_build.py --gui    # Watch and build GUI
    python watch_and_build.py --run    # Also run the EXE after building
"""

import time
import sys
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from build_exe import build_exe
except ImportError:
    print("Error: Could not import build_exe. Make sure build_exe.py exists in scripts/.")
    sys.exit(1)


class BuildHandler(FileSystemEventHandler):
    """Handler that triggers rebuilds when Python files change."""
    
    def __init__(self, toolbar_mode=True, auto_run=False):
        self.toolbar_mode = toolbar_mode
        self.auto_run = auto_run
        self.last_build_time = 0
        self.build_cooldown = 2  # Minimum seconds between builds
        self.python_files = {'.py'}
        self.exclude_dirs = {'build', 'dist', '__pycache__', '.git', 'venv', '.venv'}
        
    def should_rebuild(self, file_path):
        """Check if we should rebuild based on the changed file."""
        path = Path(file_path)
        
        # Only watch Python files
        if path.suffix not in self.python_files:
            return False
        
        # Skip excluded directories
        for part in path.parts:
            if part in self.exclude_dirs:
                return False
        
        # Skip the build script itself and watch script
        if path.name in ('build_exe.py', 'watch_and_build.py'):
            return False
        
        return True
    
    def on_modified(self, event):
        """Called when a file is modified."""
        if event.is_directory:
            return
        
        if not self.should_rebuild(event.src_path):
            return
        
        # Cooldown to prevent multiple rapid builds
        current_time = time.time()
        if current_time - self.last_build_time < self.build_cooldown:
            return
        
        self.last_build_time = current_time
        
        print(f"\n{'='*60}")
        print(f"📝 File changed: {Path(event.src_path).name}")
        print(f"🔨 Rebuilding {'Toolbar' if self.toolbar_mode else 'GUI'} EXE...")
        print(f"{'='*60}\n")
        
        try:
            # Build the EXE
            build_exe(toolbar=self.toolbar_mode)
            
            print(f"\n✅ Build complete!")
            
            if self.auto_run:
                print("🚀 Launching EXE...")
                exe_name = 'ALIVE_Data_Toolbar' if self.toolbar_mode else 'ALIVE_Data'
                exe_path = Path('dist') / f'{exe_name}.exe'
                
                if exe_path.exists():
                    # Run the EXE in background
                    subprocess.Popen([str(exe_path)], shell=True)
                else:
                    print(f"⚠️  EXE not found at {exe_path}")
            
            print(f"\n👀 Watching for changes... (Press Ctrl+C to stop)\n")
            
        except Exception as e:
            print(f"\n❌ Build failed: {e}\n")
            print("👀 Continuing to watch for changes...\n")


def main():
    """Main function to start the file watcher."""
    # Parse command line arguments
    toolbar_mode = '--gui' not in sys.argv and '-g' not in sys.argv
    auto_run = '--run' in sys.argv or '-r' in sys.argv
    
    print("="*60)
    print("🔍 ALIVE Data - Development Build Watcher")
    print("="*60)
    print(f"📦 Building: {'Toolbar' if toolbar_mode else 'GUI'}")
    print(f"🚀 Auto-run: {'Yes' if auto_run else 'No'}")
    print("="*60)
    print("\n👀 Watching for file changes...")
    print("   (Press Ctrl+C to stop)\n")
    
    # Initial build
    try:
        print("🔨 Performing initial build...\n")
        build_exe(toolbar=toolbar_mode)
        print("\n✅ Initial build complete!\n")
        
        if auto_run:
            exe_name = 'ALIVE_Data_Toolbar' if toolbar_mode else 'ALIVE_Data'
            exe_path = Path('dist') / f'{exe_name}.exe'
            if exe_path.exists():
                print("🚀 Launching EXE...")
                subprocess.Popen([str(exe_path)], shell=True)
    except Exception as e:
        print(f"❌ Initial build failed: {e}")
        print("Continuing to watch for changes...\n")
    
    # Set up file watcher
    event_handler = BuildHandler(toolbar_mode=toolbar_mode, auto_run=auto_run)
    observer = Observer()
    
    # Watch the current directory (where the script is located)
    script_dir = Path(__file__).parent
    observer.schedule(event_handler, str(script_dir), recursive=True)
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping watcher...")
        observer.stop()
    
    observer.join()
    print("👋 Goodbye!")


if __name__ == "__main__":
    main()

