# Quick Guide: Using Your Virtual Environment

## ✅ What Just Happened

I created a **virtual environment (venv)** for your project and installed all the required packages. Here's what you need to know:

## 🔑 Key Concept: Always Activate venv First!

**Before running your app, you MUST activate the venv:**

### Windows (Command Prompt):
```cmd
venv\Scripts\activate
```

### Windows (PowerShell):
```powershell
venv\Scripts\Activate.ps1
```

### How to Know It's Activated:
You'll see `(venv)` at the start of your command prompt:
```
(venv) C:\Users\matth\Desktop\ALIVE Data\ALIVE>
```

## 📋 Daily Workflow

### Every Time You Work on This Project:

1. **Open terminal in project folder**
2. **Activate venv:**
   ```cmd
   venv\Scripts\activate
   ```
3. **Now you can run:**
   ```cmd
   python -m uvicorn app.main:app --reload
   ```

### When You're Done:
```cmd
deactivate
```

## 🎯 Why This Matters

**Without venv activated:**
- Python uses packages from your global installation
- May not have all packages installed
- Can cause "ModuleNotFoundError"

**With venv activated:**
- Python uses packages from `venv/` folder
- All packages are installed and ready
- Everything works correctly!

## 🚀 Quick Start Commands

```cmd
# 1. Activate venv
venv\Scripts\activate

# 2. Start backend
python -m uvicorn app.main:app --reload

# 3. In another terminal, start frontend
cd frontend
npm run dev
```

## ⚠️ Common Mistakes

### ❌ Wrong:
```cmd
python -m uvicorn app.main:app --reload
# (venv not activated - may fail!)
```

### ✅ Correct:
```cmd
venv\Scripts\activate
python -m uvicorn app.main:app --reload
# (venv activated - works!)
```

## 📁 Your Project Structure Now:

```
ALIVE/
├── venv/              ← Virtual environment (NEW!)
│   ├── Scripts/       ← Activation scripts
│   └── Lib/           ← All your packages installed here
├── app/               ← Your code
├── frontend/          ← Frontend code
├── requirements.txt   ← List of packages
└── .env               ← Configuration
```

## 🔍 Verify venv is Working

```cmd
# Activate venv
venv\Scripts\activate

# Check installed packages
pip list

# Should see: fastapi, uvicorn, openai, etc.
```

## 💡 Pro Tips

1. **Always activate venv first** - Make it a habit!
2. **Check for (venv)** in prompt - Confirms it's active
3. **Don't commit venv/** - Already in .gitignore ✓
4. **Recreate if broken** - Delete `venv/` folder and run `python -m venv venv` again

## 🎓 Summary

- **venv** = Isolated Python environment for this project
- **Activate** before running code
- **Deactivate** when done
- **All packages** are now installed in venv ✓

Your venv is ready to use! Just remember to activate it before running your app.

