# What is a Virtual Environment (venv)?

## Simple Explanation

A **virtual environment (venv)** is like a **separate, isolated workspace** for your Python project. Think of it like this:

- **Without venv**: All Python packages are installed globally on your computer. Every project shares the same packages, which can cause conflicts.
- **With venv**: Each project has its own isolated set of packages. Projects don't interfere with each other.

## Why Use a Virtual Environment?

### Problem Without venv:
```
Project A needs FastAPI version 0.100
Project B needs FastAPI version 0.120
→ Conflict! Can't have both versions installed globally
```

### Solution With venv:
```
Project A/venv → FastAPI 0.100 ✓
Project B/venv → FastAPI 0.120 ✓
→ No conflict! Each project has its own version
```

## Benefits

1. **Isolation**: Packages in one project don't affect others
2. **Clean System**: Keeps your main Python installation clean
3. **Reproducibility**: Easy to recreate the exact environment
4. **Version Control**: Each project can use different package versions
5. **Dependency Management**: Clear list of what each project needs

## How It Works

```
Your Computer
├── Python (system-wide)
│   └── Global packages
│
└── ALIVE Project/
    ├── venv/                    ← Virtual environment (isolated)
    │   ├── bin/ (or Scripts/ on Windows)
    │   └── lib/                 ← Packages installed HERE
    │
    ├── app/                     ← Your code
    ├── requirements.txt         ← List of needed packages
    └── .env                     ← Configuration
```

When you **activate** the venv:
- Python uses packages from `venv/lib/` instead of global packages
- Commands like `pip install` install to the venv, not globally

## Creating and Using a venv

### Step 1: Create the venv
```bash
python -m venv venv
```
This creates a `venv/` folder in your project.

### Step 2: Activate the venv

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

**How to know it's activated:**
- You'll see `(venv)` at the start of your command prompt:
```
(venv) C:\Users\matth\Desktop\ALIVE Data\ALIVE>
```

### Step 3: Install packages (while venv is activated)
```bash
pip install -r requirements.txt
```
Now packages install into `venv/`, not globally!

### Step 4: Deactivate (when done)
```bash
deactivate
```

## Common Issues

### "venv doesn't have everything installed"
**Problem**: You installed packages before activating venv, or venv wasn't activated.

**Solution**:
1. Activate venv first
2. Then install packages: `pip install -r requirements.txt`

### "Command not found" after activating venv
**Problem**: venv might be corrupted or incomplete.

**Solution**: Delete `venv/` folder and recreate it:
```bash
# Deactivate first
deactivate

# Delete venv folder
rmdir /s venv    # Windows
rm -rf venv      # macOS/Linux

# Recreate
python -m venv venv

# Activate and install
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### "I don't see (venv) in my prompt"
**Problem**: venv is not activated.

**Solution**: Activate it! The prompt should show `(venv)` when active.

## Best Practices

1. **Always activate venv** before working on the project
2. **Create venv** in the project root (same folder as `requirements.txt`)
3. **Don't commit venv** to git (add `venv/` to `.gitignore` - already done!)
4. **Recreate venv** if it gets corrupted
5. **Use requirements.txt** to track dependencies

## For Your ALIVE Project

Your project structure should look like:
```
ALIVE/
├── venv/              ← Virtual environment (create this)
├── app/               ← Your code
├── frontend/          ← Frontend code
├── requirements.txt   ← List of packages needed
└── .env               ← Configuration
```

## Quick Checklist

- [ ] Create venv: `python -m venv venv`
- [ ] Activate venv: `venv\Scripts\activate` (Windows)
- [ ] Verify activation: See `(venv)` in prompt
- [ ] Install packages: `pip install -r requirements.txt`
- [ ] Verify installation: `pip list` shows your packages
- [ ] Run app: `python -m uvicorn app.main:app --reload`

## Summary

**venv = Isolated Python environment for your project**

- Keeps packages separate from other projects
- Prevents conflicts between different package versions
- Makes your project portable and reproducible
- **Always activate before installing packages or running code!**

