# Quick Start Guide

## Running the App

### Development Mode (Recommended)
```bash
cd electron-app
npm run dev
```

This will:
1. Start the Vite dev server (frontend)
2. Start the Electron app
3. Enable hot reload for changes

### Production Mode
```bash
# First, build the app
cd electron-app
npm run build

# Then run it
npm start
```

## What Each Command Does

| Command | What It Does |
|---------|-------------|
| `npm run dev` | **Starts the app** in development mode with hot reload |
| `npm run build` | **Builds/packages** the app (creates installer), doesn't run it |
| `npm start` | **Runs** the Electron app (after building) |
| `npm run build:vite` | Builds only the React frontend |
| `npm run build:electron` | Packages only the Electron app |

## Troubleshooting

### "App won't start"
- Make sure you're using `npm run dev` (not `npm run build`)
- Check that port 5173 is not already in use
- Try closing other Electron apps

### "Build failed"
- See `BUILD_STATUS.md` for build-related issues
- Make sure you've run `npm install` first

### "Can't log in"
- Set `VITE_SKIP_AUTH=true` in `.env` for testing without WorkOS
- Or configure `VITE_WORKOS_CLIENT_ID` in `.env` for real authentication

## Environment Variables

Create a `.env` file in `electron-app/`:

```env
# For development (skip authentication)
VITE_SKIP_AUTH=true

# OR for real authentication
VITE_WORKOS_CLIENT_ID=your_client_id_here
```
