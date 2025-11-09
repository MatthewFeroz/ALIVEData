# Building ALIVE Data MVP as an Executable

This guide explains how to package the ALIVE Data MVP into a standalone executable (.exe) file.

## Prerequisites

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Install all dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Building the Executable

### Option 1: Using the build script (Recommended)

```bash
python build_exe.py
```

### Option 2: Manual PyInstaller command

```bash
pyinstaller --name=ALIVE_Data --onefile --windowed gui.py
```

## What Gets Created

After building, you'll find:
- `dist/ALIVE_Data.exe` - The standalone executable
- `build/` - Temporary build files (can be deleted)
- `ALIVE_Data.spec` - PyInstaller spec file (can be reused)

## Important Notes

### Tesseract OCR Dependency

⚠️ **Important**: The executable does NOT include Tesseract OCR. Users must install Tesseract separately:

- **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- The executable will look for Tesseract in standard locations:
  - `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`

### API Key Configuration

Users will need to:
1. Run the executable
2. Enter their OpenAI API key in the GUI
3. Click "Save Key" to store it locally

The API key is saved in a `.env` file in the same directory as the executable.

## Distribution

To distribute the application:

1. **Include the executable**: `dist/ALIVE_Data.exe`
2. **Include installation instructions** for Tesseract OCR
3. **Include README.md** with usage instructions

### Creating a Distribution Package

You can create a zip file with:
```
ALIVE_Data_Distribution/
├── ALIVE_Data.exe
├── README.md
├── TESSERACT_INSTALL.txt (instructions for installing Tesseract)
└── LICENSE (if applicable)
```

## Advanced: Including Tesseract

If you want to bundle Tesseract with your executable (larger file size):

1. Download Tesseract portable version
2. Include it in the PyInstaller build using `--add-data`
3. Modify `capture.py` to use the bundled Tesseract path

This is more complex but creates a truly standalone application.

## Troubleshooting

### "Failed to execute script"
- Ensure all dependencies are installed
- Check that hidden imports are included
- Try building with `--debug=all` for more information

### "Tesseract not found"
- Users must install Tesseract OCR separately
- Or bundle Tesseract with the executable (see Advanced section)

### Large file size
- The executable includes Python and all dependencies
- Consider using `--onedir` instead of `--onefile` for faster startup
- Use UPX compression: `--upx-dir=path/to/upx`

## Testing the Executable

Before distributing:

1. Test on a clean Windows machine (without Python installed)
2. Verify Tesseract detection works
3. Test API key saving and loading
4. Test screenshot capture and OCR
5. Test documentation generation

