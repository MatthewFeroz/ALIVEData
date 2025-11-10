# Fixing Build Errors with ffi-napi

## Problem

The build is failing because:
1. **Path with spaces**: Your project path contains spaces (`C:\Users\Matthew Feroz\Desktop\...`), which causes node-gyp to fail when building native modules
2. **ffi-napi build failure**: The `ffi-napi` package (used for Windows API calls) fails to compile during the build process

## Solutions

### Option 1: Skip Native Module Rebuild (Quick Fix) ✅

I've already configured your `package.json` to skip rebuilding native modules during the build process. This works because:
- Your code already handles missing native modules gracefully (see `windowTracker.js`)
- The app will use fallback methods if native modules aren't available

**Try building now:**
```bash
cd electron-app
npm run build
```

### Option 2: Move Project to Path Without Spaces (Best Solution) ⭐

The most reliable solution is to move your project to a path without spaces:

1. **Create a new directory without spaces:**
   ```powershell
   mkdir C:\Projects\ALIVEData
   ```

2. **Move your project:**
   ```powershell
   robocopy "C:\Users\Matthew Feroz\Desktop\ALIVEOCR\ALIVEData" "C:\Projects\ALIVEData" /E /MOVE
   ```

3. **Navigate to new location:**
   ```powershell
   cd C:\Projects\ALIVEData\electron-app
   ```

4. **Rebuild native modules:**
   ```bash
   npm install
   npm run rebuild
   ```

5. **Build the app:**
   ```bash
   npm run build
   ```

### Option 3: Build Native Modules Manually Before Building

If you want to keep the current path, you can try building native modules manually:

1. **Install Windows Build Tools** (if not already installed):
   ```bash
   npm install --global windows-build-tools
   ```
   Or install Visual Studio Build Tools manually from Microsoft.

2. **Build native modules in development:**
   ```bash
   cd electron-app
   npm run rebuild
   ```

3. **Then build the app:**
   ```bash
   npm run build
   ```

### Option 4: Use Prebuilt Binaries

If the above don't work, you can try using prebuilt binaries:

1. **Remove the problematic packages:**
   ```bash
   npm uninstall ffi-napi ref-napi
   ```

2. **Install prebuilt versions** (if available):
   ```bash
   npm install ffi-napi@latest ref-napi@latest --build-from-source=false
   ```

## What Changed

I've updated your `package.json` with:
- `"electronRebuild": false` - Skips rebuilding native modules during build
- Updated `postinstall` script to skip automatic rebuild
- Added `ffi-napi` and `ref-napi` to `asarUnpack` so they're included if available

## Testing

After applying the fix, test that the app still works:

```bash
npm run dev
```

The app should work even without native modules - it will use fallback methods for window tracking.

## Notes

- The `windowTracker.js` file already handles missing native modules gracefully
- Window tracking will use alternative methods if `ffi-napi` isn't available
- For production, consider moving to a path without spaces for reliability

