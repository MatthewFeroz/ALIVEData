"""
Window Selector - UI tool for selecting which windows/applications to track.
"""

import sys
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Optional, Set

if sys.platform == 'win32':
    try:
        import win32gui
        import win32process
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
        win32gui = None
        win32process = None
else:
    WIN32_AVAILABLE = False
    win32gui = None
    win32process = None


def get_all_windows() -> List[Dict]:
    """
    Get list of all visible windows with their information.
    
    Returns:
        List of dicts with keys: hwnd, title, process_name, executable_path
    """
    windows = []
    
    if not WIN32_AVAILABLE or sys.platform != 'win32':
        return windows
    
    def enum_handler(hwnd, ctx):
        try:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                # Skip empty titles (usually system windows)
                if not title:
                    return True
                
                # Get process info
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    try:
                        import psutil
                        proc = psutil.Process(pid)
                        process_name = proc.name()
                        executable_path = proc.exe() if proc.exe() else ''
                    except Exception:
                        process_name = ''
                        executable_path = ''
                except Exception:
                    process_name = ''
                    executable_path = ''
                
                windows.append({
                    'hwnd': hwnd,
                    'title': title,
                    'process_name': process_name,
                    'executable_path': executable_path
                })
        except Exception:
            pass
        return True
    
    try:
        win32gui.EnumWindows(enum_handler, None)
    except Exception:
        pass
    
    # Sort by process name, then title
    windows.sort(key=lambda w: (w['process_name'], w['title']))
    
    return windows


class WindowSelector:
    """Dialog for selecting which windows/applications to track."""
    
    def __init__(self, parent=None):
        """
        Initialize window selector.
        
        Args:
            parent: Parent tkinter window (optional)
        """
        self.parent = parent
        self.selected_windows: Set[int] = set()
        self.selected_processes: Set[str] = set()
        self.result = None  # None = cancelled, (windows, processes) = selected
        
        self.window = None
        self.tree = None
        self.windows_data = []
        self.item_to_window_data = {}  # Map tree item IDs to window data
    
    def show(self) -> Optional[tuple]:
        """
        Show the window selector dialog.
        
        Returns:
            None if cancelled, or tuple (list of window handles, list of process names)
        """
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Select Windows to Track - ALIVE Data")
        self.window.geometry("700x500")
        self.window.attributes('-topmost', True)
        
        if self.parent:
            # Center on parent
            self.parent.update_idletasks()
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            x = parent_x + (parent_width - 700) // 2
            y = parent_y + (parent_height - 500) // 2
            self.window.geometry(f"700x500+{x}+{y}")
        
        # Configure style
        self.window.configure(bg='#1A1A1A')
        
        # Header
        header_frame = tk.Frame(self.window, bg='#2D2D2D', height=50)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(
            header_frame,
            text="Select Windows/Applications to Track",
            bg='#2D2D2D',
            fg='#FFFFFF',
            font=('Segoe UI', 12, 'bold'),
            anchor='w',
            padx=20,
            pady=15
        )
        header_label.pack(fill=tk.X)
        
        # Instructions
        instructions = tk.Label(
            self.window,
            text="Select the windows/applications you want to track events from. Only events from selected windows will be recorded.",
            bg='#1A1A1A',
            fg='#CCCCCC',
            font=('Segoe UI', 9),
            anchor='w',
            padx=20,
            pady=10,
            wraplength=660
        )
        instructions.pack(fill=tk.X)
        
        # Filter frame
        filter_frame = tk.Frame(self.window, bg='#1A1A1A')
        filter_frame.pack(fill=tk.X, padx=20, pady=5)
        
        filter_label = tk.Label(
            filter_frame,
            text="Filter:",
            bg='#1A1A1A',
            fg='#FFFFFF',
            font=('Segoe UI', 9)
        )
        filter_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self._on_filter_change)
        filter_entry = tk.Entry(
            filter_frame,
            textvariable=self.filter_var,
            bg='#2D2D2D',
            fg='#FFFFFF',
            font=('Segoe UI', 9),
            insertbackground='#FFFFFF',
            width=30
        )
        filter_entry.pack(side=tk.LEFT)
        
        # Treeview with scrollbar
        tree_frame = tk.Frame(self.window, bg='#1A1A1A')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('Process', 'Window Title'),
            show='tree headings',
            yscrollcommand=scrollbar.set,
            selectmode='extended'
        )
        scrollbar.config(command=self.tree.yview)
        
        # Configure columns
        self.tree.heading('#0', text='✓', anchor='w')
        self.tree.heading('Process', text='Process Name', anchor='w')
        self.tree.heading('Window Title', text='Window Title', anchor='w')
        
        self.tree.column('#0', width=30, minwidth=30)
        self.tree.column('Process', width=200, minwidth=150)
        self.tree.column('Window Title', width=400, minwidth=200)
        
        # Configure tags for checked/unchecked with proper colors
        self.tree.tag_configure('checked', background='#E8F5E9', foreground='#000000')
        self.tree.tag_configure('unchecked', background='#FFFFFF', foreground='#000000')
        self.tree.tag_configure('process', foreground='#000000', background='#F5F5F5')
        self.tree.tag_configure('window', foreground='#000000', background='#FFFFFF')
        
        # Configure style for better visibility - use lighter background
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background='#FFFFFF', foreground='#000000', fieldbackground='#FFFFFF', rowheight=25)
        style.configure('Treeview.Heading', background='#E0E0E0', foreground='#000000', font=('Segoe UI', 9, 'bold'))
        style.map('Treeview', background=[('selected', '#B3D9FF')], foreground=[('selected', '#000000')])
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind double-click to toggle selection
        self.tree.bind('<Double-1>', self._on_item_double_click)
        self.tree.bind('<Button-1>', self._on_item_click)
        
        # Buttons frame
        button_frame = tk.Frame(self.window, bg='#1A1A1A')
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Select All / Deselect All buttons
        select_all_btn = tk.Button(
            button_frame,
            text="Select All",
            command=self._select_all,
            bg='#2D2D2D',
            fg='#FFFFFF',
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        select_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        deselect_all_btn = tk.Button(
            button_frame,
            text="Deselect All",
            command=self._deselect_all,
            bg='#2D2D2D',
            fg='#FFFFFF',
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        deselect_all_btn.pack(side=tk.LEFT)
        
        # Right side buttons
        right_buttons = tk.Frame(button_frame, bg='#1A1A1A')
        right_buttons.pack(side=tk.RIGHT)
        
        cancel_btn = tk.Button(
            right_buttons,
            text="Cancel",
            command=self._cancel,
            bg='#404040',
            fg='#FFFFFF',
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor='hand2'
        )
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ok_btn = tk.Button(
            right_buttons,
            text="OK",
            command=self._ok,
            bg='#0078D4',
            fg='#FFFFFF',
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor='hand2'
        )
        ok_btn.pack(side=tk.LEFT)
        
        # Load windows
        self._load_windows()
        
        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Wait for window to close
        self.window.wait_window()
        
        return self.result
    
    def _load_windows(self):
        """Load all windows into the treeview."""
        self.windows_data = get_all_windows()
        self._refresh_tree()
    
    def _refresh_tree(self):
        """Refresh the treeview with current filter."""
        # Clear tree and data
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.item_to_window_data.clear()
        
        # Filter windows
        filter_text = self.filter_var.get().lower()
        filtered_windows = self.windows_data
        
        if filter_text:
            filtered_windows = [
                w for w in self.windows_data
                if filter_text in w['title'].lower() or filter_text in w['process_name'].lower()
            ]
        
        # Group by process name
        processes = {}
        for window in filtered_windows:
            process_name = window['process_name'] or 'Unknown'
            if process_name not in processes:
                processes[process_name] = []
            processes[process_name].append(window)
        
        # Add to tree
        for process_name in sorted(processes.keys()):
            process_id = self.tree.insert('', 'end', text='', values=(process_name, ''), tags=('process', 'unchecked'))
            # Store process data
            self.item_to_window_data[process_id] = {'type': 'process', 'process_name': process_name}
            
            for window in processes[process_name]:
                window_id = self.tree.insert(
                    process_id,
                    'end',
                    text='',
                    values=('', window['title']),
                    tags=('window', 'unchecked')
                )
                # Store window data in dictionary
                self.item_to_window_data[window_id] = {
                    'type': 'window',
                    'hwnd': window['hwnd'],
                    'process_name': window['process_name'],
                    'title': window['title']
                }
        
        # Update checkboxes
        self._update_checkboxes()
    
    def _update_checkboxes(self):
        """Update checkbox states based on selections."""
        for item in self.tree.get_children():
            self._update_item_checkbox(item)
            for child in self.tree.get_children(item):
                self._update_item_checkbox(child)
    
    def _update_item_checkbox(self, item):
        """Update checkbox for a single item."""
        tags = list(self.tree.item(item, 'tags'))
        
        # Remove old checked/unchecked tags
        if 'checked' in tags:
            tags.remove('checked')
        if 'unchecked' in tags:
            tags.remove('unchecked')
        
        # Get window data from dictionary
        window_data = self.item_to_window_data.get(item, {})
        item_type = window_data.get('type', '')
        
        is_checked = False
        if item_type == 'window':
            hwnd = window_data.get('hwnd')
            if hwnd and hwnd in self.selected_windows:
                is_checked = True
        elif item_type == 'process':
            process_name = window_data.get('process_name', '')
            if process_name and process_name.lower() in {p.lower() for p in self.selected_processes}:
                is_checked = True
        
        # Add appropriate tag
        if is_checked:
            tags.append('checked')
            # Update checkbox text
            self.tree.item(item, text='✓')
        else:
            tags.append('unchecked')
            self.tree.item(item, text='')
        
        self.tree.item(item, tags=tags)
    
    def _on_filter_change(self, *args):
        """Handle filter text change."""
        self._refresh_tree()
    
    def _on_item_click(self, event):
        """Handle single click on item."""
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        # Toggle selection on click
        self._toggle_item_selection(item)
    
    def _on_item_double_click(self, event):
        """Handle double-click on item to toggle selection."""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
        
        self._toggle_item_selection(item)
    
    def _toggle_item_selection(self, item):
        """Toggle selection of an item."""
        # Get window data from dictionary
        window_data = self.item_to_window_data.get(item, {})
        item_type = window_data.get('type', '')
        
        if item_type == 'window':
            # Toggle individual window
            hwnd = window_data.get('hwnd')
            if hwnd:
                if hwnd in self.selected_windows:
                    self.selected_windows.remove(hwnd)
                else:
                    self.selected_windows.add(hwnd)
        elif item_type == 'process':
            # Toggle entire process (select/deselect all child windows)
            process_name = window_data.get('process_name', '')
            if not process_name:
                return
            
            is_selected = process_name.lower() in {p.lower() for p in self.selected_processes}
            
            if is_selected:
                # Deselect process and all its windows
                self.selected_processes = {p for p in self.selected_processes if p.lower() != process_name.lower()}
                # Also remove individual windows from this process
                for child in self.tree.get_children(item):
                    child_data = self.item_to_window_data.get(child, {})
                    if child_data.get('type') == 'window':
                        child_hwnd = child_data.get('hwnd')
                        if child_hwnd:
                            self.selected_windows.discard(child_hwnd)
            else:
                # Select process and all its windows
                self.selected_processes.add(process_name)
                # Also select all child windows
                for child in self.tree.get_children(item):
                    child_data = self.item_to_window_data.get(child, {})
                    if child_data.get('type') == 'window':
                        child_hwnd = child_data.get('hwnd')
                        if child_hwnd:
                            self.selected_windows.add(child_hwnd)
        
        self._update_checkboxes()
    
    def _select_all(self):
        """Select all windows."""
        for window in self.windows_data:
            self.selected_windows.add(window['hwnd'])
            if window['process_name']:
                self.selected_processes.add(window['process_name'])
        self._update_checkboxes()
    
    def _deselect_all(self):
        """Deselect all windows."""
        self.selected_windows.clear()
        self.selected_processes.clear()
        self._update_checkboxes()
    
    def _ok(self):
        """Handle OK button click."""
        # Collect all selected windows from tree
        selected_windows = set(self.selected_windows)
        selected_processes = set(self.selected_processes)
        
        # Also check tree items for selections
        for item in self.tree.get_children():
            # Check if process is selected
            window_data = self.item_to_window_data.get(item, {})
            if window_data.get('type') == 'process':
                process_name = window_data.get('process_name', '')
                tags = self.tree.item(item, 'tags')
                
                if 'checked' in tags and process_name:
                    selected_processes.add(process_name)
            
            # Check child windows
            for child in self.tree.get_children(item):
                child_data = self.item_to_window_data.get(child, {})
                if child_data.get('type') == 'window':
                    hwnd = child_data.get('hwnd')
                    tags = self.tree.item(child, 'tags')
                    if hwnd and 'checked' in tags:
                        selected_windows.add(hwnd)
        
        self.result = (list(selected_windows), list(selected_processes))
        self.window.destroy()
    
    def _cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.window.destroy()

