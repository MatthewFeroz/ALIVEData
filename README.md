# ALIVE Data

ALIVE Data is a modern web application for automatically generating documentation from screenshots and terminal commands using OCR and AI.

## Quick Links

- **[📚 Documentation Index](docs/README.md)** - Browse all organized documentation
- **[Main Documentation](docs/readmes/README_MAIN.md)** - Complete project documentation, setup instructions, and usage guide
- **[Convex Documentation](docs/readmes/README_CONVEX.md)** - Convex functions and backend setup guide
- **[Quick Start Guide](docs/quick-start/START_HERE.md)** - Get started quickly

## Quick Start

1. **Backend Setup:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   ```

3. **Run:**
   - Backend: `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
   - Frontend: `cd frontend && npm run dev`

For detailed setup instructions, see [Main Documentation](docs/readmes/README_MAIN.md).

## Documentation

All documentation is organized in the [`docs/`](docs/) directory:

- **[Setup & Configuration](docs/setup/)** - Environment setup, API keys, Convex configuration
- **[Quick Start Guides](docs/quick-start/)** - Getting started guides and quick fixes
- **[Migration Guides](docs/migration/)** - Migration documentation for Convex and TypeScript
- **[Deployment](docs/deployment/)** - Production deployment instructions
- **[Troubleshooting](docs/troubleshooting/)** - Solutions to common problems
- **[Testing](docs/testing/)** - Testing guides and procedures
- **[Project READMEs](docs/readmes/)** - Main project documentation

See the [Documentation Index](docs/README.md) for a complete list of all documentation files.

