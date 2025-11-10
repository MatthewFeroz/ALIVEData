# ALIVE Data - Electron App

Electron-based version of ALIVE Data with modern web UI.

## Quick Start

```bash
# Install dependencies
npm install

# Run in development mode (starts the app)
npm run dev

# Build for production (creates installer, doesn't run the app)
npm run build

# Run the built app (after building)
npm start
```

## Available Scripts

- `npm run dev` - Start development server and Electron app (hot reload enabled)
- `npm run build` - Build the app and create installer/package
- `npm start` - Run the Electron app (requires build first)
- `npm run build:vite` - Build only the React frontend
- `npm run build:electron` - Package only the Electron app

## Project Structure

```
electron-app/
├── src/
│   ├── main/           # Electron main process
│   │   ├── main.js     # Main entry point
│   │   ├── windows/    # Window tracking
│   │   ├── processes/  # Process monitoring
│   │   └── capture/    # Screenshot capture
│   ├── preload/        # Preload scripts
│   └── renderer/       # React frontend
├── package.json
└── vite.config.js
```

## Features

- Window tracking using Windows API
- Process monitoring
- Screenshot capture
- Modern React UI
- Electron-based desktop app

