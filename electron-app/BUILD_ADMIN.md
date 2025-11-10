# Running Build Commands as Administrator

## Option 1: PowerShell as Administrator

1. **Open PowerShell as Administrator:**
   - Press `Windows Key + X`
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"
   - Or search for "PowerShell" in Start Menu, right-click, and select "Run as administrator"

2. **Navigate to your project:**
   ```powershell
   cd "C:\Users\Matthew Feroz\Desktop\ALIVEOCR\ALIVEData\electron-app"
   ```

3. **Run the build:**
   ```powershell
   npm run build
   ```

## Option 2: Command Prompt as Administrator

1. **Open Command Prompt as Administrator:**
   - Press `Windows Key + X`
   - Select "Command Prompt (Admin)" or "Terminal (Admin)"
   - Or search for "cmd" in Start Menu, right-click, and select "Run as administrator"

2. **Navigate to your project:**
   ```cmd
   cd "C:\Users\Matthew Feroz\Desktop\ALIVEOCR\ALIVEData\electron-app"
   ```

3. **Run the build:**
   ```cmd
   npm run build
   ```

## Option 3: Enable Developer Mode (Recommended)

Instead of running as admin every time, you can enable Developer Mode in Windows, which allows creating symbolic links without admin privileges:

1. **Open Windows Settings:**
   - Press `Windows Key + I`
   - Go to **Privacy & Security** → **For developers**

2. **Enable Developer Mode:**
   - Toggle "Developer Mode" to **On**
   - Windows will download and install some components (may take a few minutes)

3. **Restart your terminal** and run the build normally:
   ```powershell
   cd "C:\Users\Matthew Feroz\Desktop\ALIVEOCR\ALIVEData\electron-app"
   npm run build
   ```

## Re-enabling Code Signing (if needed)

If you want to enable code signing after running as admin, you can:

1. **Remove the `sign: false` from package.json:**
   ```json
   "win": {
     "target": [...],
     "icon": "build/icon.ico",
     "artifactName": "${productName}-${version}-${arch}.${ext}"
     // Remove: "sign": false
   }
   ```

2. **Remove the environment variable from build scripts:**
   ```json
   "build": "vite build && electron-builder",
   "build:electron": "electron-builder",
   ```

3. **Run the build as administrator** (or with Developer Mode enabled)

## Note

For **development builds**, code signing is not required. The current configuration (with code signing disabled) will work fine for testing your app. Code signing is mainly needed for:
- Production releases
- Windows Store distribution
- Avoiding "Unknown Publisher" warnings

You can keep code signing disabled for now and only enable it when you're ready to distribute the app.

