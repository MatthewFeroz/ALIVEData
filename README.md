# ALIVE Data

ALIVE Data is a modern web application for automatically generating documentation from screenshots using OCR and AI. Built with React, Convex, and OpenAI.

## Quick Links

- **[📚 Documentation Index](docs/README.md)** - Browse all organized documentation
- **[Convex Documentation](docs/readmes/README_CONVEX.md)** - Convex functions and backend setup guide
- **[Quick Start Guide](docs/quick-start/START_HERE.md)** - Get started quickly
- **[Architecture Overview](ARCHITECTURE.md)** - Application architecture and structure

## Quick Start

1. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure Environment:**
   - Create `.env.local` in `frontend/` directory
   - Add: `VITE_CONVEX_URL=your_convex_url`
   - Set `OPENAI_API_KEY` in Convex dashboard

3. **Run:**
   ```bash
   cd frontend
   npm run dev
   ```

4. **Convex Backend:**
   - Run `npx convex dev` in the `frontend/convex/` directory
   - Set `OPENAI_API_KEY` in Convex dashboard environment variables

For detailed setup instructions, see [Convex Documentation](docs/readmes/README_CONVEX.md).

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

