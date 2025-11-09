"""
ALIVE Data MVP - GUI Application
A user-friendly interface for capturing screenshots and generating documentation.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from pathlib import Path
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from capture import capture_and_ocr
from summarize import summarize_text


class ALIVEGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ALIVE Data - Automatic Documentation Generator")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Load environment variables
        load_dotenv()
        
        # Variables
        self.api_key = tk.StringVar(value=os.getenv("OPENAI_API_KEY", ""))
        self.is_processing = False
        
        self.setup_ui()
        self.check_api_key()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="ALIVE Data - Automatic Documentation Generator",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # API Key section
        api_frame = ttk.LabelFrame(main_frame, text="OpenAI API Configuration", padding="10")
        api_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        api_frame.columnconfigure(1, weight=1)
        
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        api_entry = ttk.Entry(api_frame, textvariable=self.api_key, width=50, show="*")
        api_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        save_key_btn = ttk.Button(api_frame, text="Save Key", command=self.save_api_key)
        save_key_btn.grid(row=0, column=2)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        self.capture_btn = ttk.Button(
            control_frame,
            text="📸 Capture & Generate Documentation",
            command=self.start_capture_process,
            state=tk.NORMAL
        )
        self.capture_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_folder_btn = ttk.Button(
            control_frame,
            text="📁 Open Docs Folder",
            command=self.open_docs_folder
        )
        self.open_folder_btn.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Generated Documentation", padding="10")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=("Consolas", 10)
        )
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Output buttons
        output_btn_frame = ttk.Frame(output_frame)
        output_btn_frame.grid(row=1, column=0, pady=(10, 0))
        
        ttk.Button(
            output_btn_frame,
            text="💾 Save Documentation",
            command=self.save_documentation
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            output_btn_frame,
            text="🗑️ Clear",
            command=self.clear_output
        ).pack(side=tk.LEFT)
        
    def check_api_key(self):
        """Check if API key is set."""
        if not self.api_key.get() or self.api_key.get() == "":
            self.status_var.set("⚠️ Warning: API key not set. Please enter your OpenAI API key.")
        else:
            self.status_var.set("Ready - API key configured")
            
    def save_api_key(self):
        """Save API key to .env file."""
        key = self.api_key.get().strip()
        if not key:
            messagebox.showwarning("Warning", "Please enter an API key.")
            return
        
        try:
            env_path = Path(".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"OPENAI_API_KEY={key}\n")
            
            # Update environment variable
            os.environ["OPENAI_API_KEY"] = key
            
            messagebox.showinfo("Success", "API key saved successfully!")
            self.status_var.set("Ready - API key saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API key: {e}")
            
    def start_capture_process(self):
        """Start the capture and documentation generation process in a separate thread."""
        if self.is_processing:
            messagebox.showinfo("Info", "Processing already in progress. Please wait.")
            return
        
        # Check API key
        if not self.api_key.get() or self.api_key.get().strip() == "":
            messagebox.showwarning("Warning", "Please set your OpenAI API key first.")
            return
        
        # Disable button and start processing
        self.capture_btn.config(state=tk.DISABLED)
        self.is_processing = True
        self.status_var.set("Processing... Taking screenshot...")
        
        # Run in separate thread to keep UI responsive
        thread = threading.Thread(target=self.capture_process, daemon=True)
        thread.start()
        
    def capture_process(self):
        """Perform the capture and documentation generation."""
        try:
            # Ensure docs directory exists
            Path("docs").mkdir(exist_ok=True)
            
            # Update status
            self.root.after(0, lambda: self.status_var.set("Capturing screenshot..."))
            
            # Capture and OCR
            ocr_result = capture_and_ocr()
            
            self.root.after(0, lambda: self.status_var.set("Extracting text with OCR..."))
            self.root.after(0, lambda: self.output_text.insert(tk.END, "=== OCR Extracted Text ===\n\n"))
            self.root.after(0, lambda: self.output_text.insert(tk.END, ocr_result[:500] + "...\n\n"))
            self.root.after(0, lambda: self.output_text.see(tk.END))
            
            # Generate summary
            self.root.after(0, lambda: self.status_var.set("Generating documentation with AI..."))
            
            # Update API key in environment if changed
            if self.api_key.get():
                os.environ["OPENAI_API_KEY"] = self.api_key.get()
            
            summary = summarize_text(ocr_result)
            
            # Save to file
            output_path = Path("docs") / f"generated_doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(summary)
            
            # Update UI
            self.root.after(0, lambda: self.output_text.insert(tk.END, "\n=== Generated Documentation ===\n\n"))
            self.root.after(0, lambda: self.output_text.insert(tk.END, summary))
            self.root.after(0, lambda: self.output_text.see(tk.END))
            self.root.after(0, lambda: self.status_var.set(f"✓ Complete! Saved to {output_path.name}"))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.status_var.set(error_msg))
            self.root.after(0, lambda: self.output_text.insert(tk.END, f"\n\n❌ Error: {error_msg}\n"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{error_msg}"))
        finally:
            # Re-enable button
            self.is_processing = False
            self.root.after(0, lambda: self.capture_btn.config(state=tk.NORMAL))
            
    def save_documentation(self):
        """Save the current documentation to a file."""
        content = self.output_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("Info", "No documentation to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=Path("docs").absolute()
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Documentation saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
                
    def clear_output(self):
        """Clear the output text area."""
        self.output_text.delete("1.0", tk.END)
        self.status_var.set("Ready")
        
    def open_docs_folder(self):
        """Open the docs folder in file explorer."""
        docs_path = Path("docs").absolute()
        docs_path.mkdir(exist_ok=True)
        
        if os.name == 'nt':  # Windows
            os.startfile(docs_path)
        elif os.name == 'posix':  # macOS/Linux
            import subprocess
            subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', str(docs_path)])


def main():
    root = tk.Tk()
    app = ALIVEGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

