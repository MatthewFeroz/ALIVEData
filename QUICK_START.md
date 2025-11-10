# ALIVE Data - Quick Start Guide

## 🚀 How to Run the Project

### Option 1: Floating Toolbar (Recommended) ⭐

**Easiest way - Double-click:**
```
scripts\batch\run_toolbar.bat
```

**Or from command line:**
```bash
python -m src.toolbar
```

### Option 2: Full GUI Application

**Double-click:**
```
scripts\batch\dev_gui.bat
```

**Or from command line:**
```bash
python -m src.gui
```

### Option 3: Command Line Interface

```bash
python main.py
```

### Option 4: Development Mode (Hot Reload)

For development with instant updates when you change code:

**Toolbar:**
```bash
scripts\batch\dev_toolbar.bat
```

**GUI:**
```bash
scripts\batch\dev_gui.bat
```

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Tesseract OCR** installed (see `config/TESSERACT_INSTALL.txt`)
3. **Dependencies installed:**
   ```bash
   pip install -r requirements.txt
   ```
4. **API Key configured:**
   - Create `.env` file in project root
   - Add: `OPENAI_API_KEY=sk-your-key-here`

## ✅ Verify Setup

Run the test script to verify everything is configured:

```bash
python tests\test_setup.py
```

## 📁 Project Structure

- **`src/`** - Core application code
- **`scripts/`** - Development and build tools
- **`scripts/batch/`** - Windows launchers
- **`docs/`** - Documentation
- **`docs/generated/`** - Generated outputs

## 🛠️ Building Executables

```bash
# Build toolbar EXE
python scripts\build_exe.py --toolbar

# Build GUI EXE
python scripts\build_exe.py
```

## 💡 Tips

- **First time?** Use `scripts\batch\run_toolbar.bat` - it's the simplest
- **Developing?** Use `scripts\batch\dev_toolbar.bat` for hot-reload
- **Need help?** Check `docs/SETUP.md` for detailed setup instructions

