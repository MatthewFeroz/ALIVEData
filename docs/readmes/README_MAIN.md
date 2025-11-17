# ALIVE Data - Web Application

ALIVE Data is a modern web application for automatically generating documentation from screenshots and terminal commands using OCR and AI.

## Features

- 📸 **Screenshot Upload**: Upload screenshots via drag-and-drop or file selection
- 🔍 **OCR Processing**: Extract text from images using Tesseract OCR
- 🤖 **AI Documentation**: Generate step-by-step documentation using OpenAI
- 📁 **Session Management**: Organize recordings into structured sessions
- 🎨 **Modern UI**: Responsive dark-themed interface built with React

## Architecture

- **Backend**: FastAPI (Python) - RESTful API with automatic documentation
- **Frontend**: React + Vite - Modern single-page application
- **OCR**: Tesseract OCR for text extraction
- **AI**: OpenAI GPT models for documentation generation

## Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- Tesseract OCR installed on your system
  - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd ALIVE
```

### 2. Backend Setup

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 4. Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-api-key-here
```

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
# Activate virtual environment if not already active
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Run FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Interactive API Docs: http://localhost:8000/redoc

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:3000

### Production Mode

**Build Frontend:**
```bash
cd frontend
npm run build
```

**Run Backend:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Usage

1. **Start the application** (both backend and frontend)
2. **Create a new session** from the Sessions page
3. **Upload screenshots** using drag-and-drop or file selection
4. **Process OCR** on uploaded screenshots to extract text
5. **Generate documentation** using AI to create step-by-step guides
6. **View and download** the generated documentation

## API Endpoints

### Sessions

- `POST /api/sessions` - Create a new session
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{session_id}` - Get session details

### Screenshots

- `POST /api/sessions/{session_id}/screenshots` - Upload a screenshot
- `GET /api/sessions/{session_id}/screenshots` - List screenshots in a session

### OCR & Documentation

- `POST /api/sessions/{session_id}/ocr` - Process OCR on an image
- `POST /api/sessions/{session_id}/generate` - Generate documentation
- `GET /api/sessions/{session_id}/documentation` - Download documentation

Full API documentation is available at http://localhost:8000/docs when the backend is running.

## Project Structure

```
ALIVE/
├── app/                    # Backend FastAPI application
│   ├── api/               # API route handlers
│   ├── core/              # Configuration and utilities
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic services
│   └── main.py            # FastAPI app entry point
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API client
│   │   └── App.jsx        # Main app component
│   └── package.json
├── src/                   # Original desktop app code (preserved)
├── docs/                  # Generated documentation and sessions
├── uploads/               # Uploaded files
├── static/                # Static files served by backend
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Development

### Backend Development

The backend uses FastAPI with automatic API documentation. Code changes will hot-reload when using `--reload` flag.

### Frontend Development

The frontend uses Vite for fast development with hot module replacement. Changes will automatically reload in the browser.

### Adding New Features

1. **Backend**: Add new routes in `app/api/routes.py` and corresponding services in `app/services/`
2. **Frontend**: Add new components in `frontend/src/components/` and pages in `frontend/src/pages/`

## Troubleshooting

### Tesseract OCR Not Found

Ensure Tesseract is installed and in your system PATH, or set `TESSERACT_CMD` in `.env`:

```
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### CORS Errors

If you encounter CORS errors, ensure the frontend URL is in the `CORS_ORIGINS` list in `app/core/config.py`.

### OpenAI API Errors

- Verify your API key is correct in `.env`
- Check your OpenAI account has sufficient credits
- Ensure the API key has proper permissions

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

