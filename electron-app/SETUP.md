# ALIVE Data Electron - Setup Guide

## Prerequisites

1. **Node.js** 18+ installed
2. **npm** or **yarn** package manager
3. **Windows SDK** (for native module compilation on Windows)

## Installation

```bash
cd electron-app
npm install
```

## Development

```bash
# Run in development mode (starts Vite dev server + Electron)
npm run dev

# Build for production
npm run build

# Build only renderer (frontend)
npm run build:vite

# Build only Electron app
npm run build:electron
```

## Environment Variables

Create a `.env` file in the `electron-app` directory:

```env
# WorkOS Configuration (AuthKit)
WORKOS_CLIENT_ID=your_workos_client_id

# Note: AuthKit uses hosted authentication, so no API key or connection/provider
# configuration is needed in the .env file. Configure these in the WorkOS dashboard.

# Convex Configuration
CONVEX_URL=https://your-deployment.convex.cloud
CONVEX_DEPLOYMENT_KEY=your_convex_deployment_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

## Project Structure

```
electron-app/
├── src/
│   ├── main/              # Electron main process
│   │   ├── main.js        # Entry point
│   │   ├── windows/       # Window tracking
│   │   ├── processes/     # Process monitoring
│   │   ├── capture/       # Screenshot capture
│   │   └── ocr/           # OCR service
│   ├── preload/           # Preload scripts
│   └── renderer/          # React frontend
│       ├── components/    # React components
│       └── services/      # Services (auth, convex)
├── build/                 # Build assets (icons)
├── dist/                  # Build output
└── package.json
```

## Building Executables

```bash
# Build for current platform
npm run build

# Output will be in dist/ directory
```

## Troubleshooting

### Native Module Compilation Issues

If you encounter errors with `ffi-napi` or `ref-napi`:

1. Install Windows Build Tools:
   ```bash
   npm install --global windows-build-tools
   ```

2. Or install Visual Studio Build Tools manually

### Tesseract.js Issues

Tesseract.js requires its core files. They should be automatically included, but if OCR fails:

1. Check that `node_modules/tesseract.js-core` exists
2. Reinstall: `npm install tesseract.js --force`

### Windows API Access

The app requires Windows API access. On Windows, this should work automatically. For testing on other platforms, the Windows-specific features will be disabled.

## Next Steps

1. Set up WorkOS account and configure OAuth
2. Create Convex project and get deployment URL
3. Add application icons to `build/` directory
4. Test the application: `npm run dev`
5. Port remaining features from Python version

