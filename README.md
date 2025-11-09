# ALIVE Data MVP

A local MVP skeleton that captures screenshots, extracts text with OCR, and summarizes it into step-by-step documentation using an LLM.

## Features

1. **Screenshot Capture** - Takes a screenshot of your screen
2. **OCR Text Extraction** - Extracts text from the screenshot using Tesseract
3. **LLM Summarization** - Converts OCR text into step-by-step documentation

## Setup

### Prerequisites

- Python 3.8+
- Tesseract OCR installed on your system

#### Installing Tesseract

- **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki) or use `choco install tesseract`
- **macOS**: `brew install tesseract`
- **Ubuntu/Debian**: `sudo apt install tesseract-ocr`

### Installation

1. Create and activate a virtual environment:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:

Create a `.env` file in the project root with:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

## Usage

### Floating Toolbar (Recommended)

Launch the minimal floating toolbar (similar to Zoom's toolbar):

```bash
python toolbar.py
```

Or use the launcher:
```bash
run_toolbar.bat
```

The toolbar:
- Stays at the bottom center of your screen
- Always on top, unobtrusive design
- One-click capture and documentation generation
- Step counter and status indicator
- Minimal footprint - you'll barely notice it's there

### Full GUI Application

Launch the full graphical interface:

```bash
python gui.py
```

Or use the launcher:
```bash
run_gui.bat
```

The GUI provides:
- Easy API key configuration
- One-click screenshot capture and documentation generation
- Real-time status updates
- View and save generated documentation
- Open docs folder directly

### Command Line Interface

Run the main script:

```bash
python main.py
```

The script will:
1. Take a screenshot of your screen
2. Extract text using OCR
3. Generate step-by-step documentation using GPT-4o-mini
4. Save the documentation to `docs/generated_doc.md`

## Building an Executable

To create a standalone `.exe` file for distribution:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   # Build floating toolbar (recommended)
   python build_exe.py --toolbar
   
   # Or build full GUI
   python build_exe.py
   ```

The executable will be created in the `dist/` folder. See `BUILD_INSTRUCTIONS.md` for detailed instructions.

**Note**: Users will need to install Tesseract OCR separately. See `TESSERACT_INSTALL.txt` for instructions.

## Project Structure

```
ALIVE/
├── capture.py           # Screenshot capture and OCR
├── summarize.py         # LLM summarization
├── main.py              # CLI orchestration script
├── toolbar.py           # Floating toolbar (recommended)
├── gui.py               # Full GUI application
├── build_exe.py         # Script to build executable
├── test_setup.py        # Setup verification script
├── run_toolbar.bat      # Toolbar launcher
├── run_gui.bat          # GUI launcher
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore rules
├── BUILD_INSTRUCTIONS.md # Executable building guide
├── TESSERACT_INSTALL.txt # Tesseract installation guide
├── SETUP.md             # Setup instructions
└── docs/                # Generated screenshots and documentation
```

## Next Steps

Once the MVP is working, consider adding:

- **Multiple steps**: Capture every N seconds, group into sequence
- **Privacy**: Local redaction regex for names/emails
- **Backend API**: FastAPI endpoint to store and fetch docs
- **Frontend UI**: Streamlit or Flask template to view past docs
- **Config**: Frequency, region, and data retention settings

## Development Tip

Iterate in notebooks first if needed:

```bash
jupyter notebook
```

Paste the OCR + LLM loop so you can visualize the captured text and tune prompts before coding automation.
