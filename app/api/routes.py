"""
API routes for ALIVE Data web application.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import shutil
import os
import socket

from app.models.schemas import (
    SessionCreate,
    SessionResponse,
    ScreenshotUpload,
    OCRRequest,
    OCRResponse,
    DocumentationRequest,
    DocumentationResponse,
    ErrorResponse,
    SessionListResponse
)
from app.services.session_service import SessionService
from app.services.capture_service import extract_text_from_image, extract_terminal_text
from app.services.ai_service import summarize_text, summarize_commands
from app.core.config import settings

router = APIRouter()

# In-memory session storage (in production, use database)
sessions: dict[str, SessionService] = {}


def get_session_service(session_id: str) -> SessionService:
    """Get session service for a given session ID."""
    # Check in-memory first
    if session_id in sessions:
        return sessions[session_id]
    
    # Check filesystem - load session if it exists
    session_info = SessionService.get_session(session_id)
    if session_info:
        session_service = SessionService()
        session_service.current_session_dir = Path(session_info["session_dir"])
        session_service.session_id = session_id
        if session_info.get("start_time"):
            from datetime import datetime
            session_service.session_start_time = datetime.fromisoformat(session_info["start_time"])
        sessions[session_id] = session_service
        return session_service
    
    raise HTTPException(status_code=404, detail="Session not found")


@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(session_data: SessionCreate):
    """Create a new recording session."""
    try:
        session_service = SessionService()
        session_dir = session_service.create_session_folder(
            custom_prefix=session_data.custom_prefix,
            folder_name=session_data.folder_name
        )
        
        sessions[session_service.session_id] = session_service
        
        return SessionResponse(
            session_id=session_service.session_id,
            session_dir=str(session_dir),
            start_time=session_service.session_start_time,
            pc_name=os.getenv("COMPUTERNAME", socket.gethostname() if hasattr(socket, 'gethostname') else None),
            pc_name_abbrev=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions():
    """List all sessions."""
    try:
        session_list = SessionService.list_sessions()
        session_responses = [
            SessionResponse(
                session_id=s.get("session_id", ""),
                session_dir=s.get("session_dir", ""),
                start_time=datetime.fromisoformat(s["start_time"]) if s.get("start_time") else datetime.now(),
                pc_name=s.get("pc_name"),
                pc_name_abbrev=s.get("pc_name_abbrev")
            )
            for s in session_list
        ]
        return SessionListResponse(sessions=session_responses, total=len(session_responses))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session details."""
    session_info = SessionService.get_session(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse(
        session_id=session_info.get("session_id", session_id),
        session_dir=session_info.get("session_dir", ""),
        start_time=datetime.fromisoformat(session_info["start_time"]) if session_info.get("start_time") else datetime.now(),
        pc_name=session_info.get("pc_name"),
        pc_name_abbrev=session_info.get("pc_name_abbrev")
    )


@router.post("/sessions/{session_id}/screenshots", response_model=ScreenshotUpload)
async def upload_screenshot(
    session_id: str,
    file: UploadFile = File(...)
):
    """Upload a screenshot to a session."""
    session_service = get_session_service(session_id)
    
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Save file
    try:
        screenshot_path = session_service.get_screenshot_path()
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(screenshot_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Also copy to static directory for serving
        static_path = settings.STATIC_DIR / screenshot_path.name
        static_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(screenshot_path, static_path)
        
        return ScreenshotUpload(
            screenshot_id=screenshot_path.stem,
            filename=screenshot_path.name,
            path=str(screenshot_path),
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload screenshot: {str(e)}")


@router.post("/sessions/{session_id}/ocr", response_model=OCRResponse)
async def process_ocr(
    session_id: str,
    request: OCRRequest
):
    """Process OCR on an uploaded image."""
    session_service = get_session_service(session_id)
    
    try:
        if request.image_path:
            image_path = request.image_path
            # If it's a relative path with screenshots/, construct full path
            if "screenshots" in image_path and not os.path.isabs(image_path):
                image_path = str(session_service.current_session_dir / image_path)
        elif request.screenshot_id:
            # screenshot_id can be a filename or ID
            screenshots_dir = session_service.current_session_dir / "screenshots"
            # Try as filename first, then as ID
            if os.path.exists(str(screenshots_dir / request.screenshot_id)):
                image_path = str(screenshots_dir / request.screenshot_id)
            else:
                image_path = str(screenshots_dir / f"{request.screenshot_id}.png")
        else:
            raise HTTPException(status_code=400, detail="Either image_path or screenshot_id must be provided")
        
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail=f"Image file not found: {image_path}")
        
        # Extract text
        text = extract_text_from_image(image_path)
        
        return OCRResponse(
            text=text,
            screenshot_path=image_path
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process OCR: {str(e)}")


@router.post("/sessions/{session_id}/generate", response_model=DocumentationResponse)
async def generate_documentation(
    session_id: str,
    request: DocumentationRequest
):
    """Generate documentation from OCR text or command history."""
    session_service = get_session_service(session_id)
    
    try:
        if request.ocr_text:
            # Generate from OCR text
            documentation = summarize_text(request.ocr_text)
        elif request.command_history:
            # Generate from command history
            command_list = [
                (
                    cmd.get("command", ""),
                    datetime.fromisoformat(cmd["timestamp"]) if isinstance(cmd.get("timestamp"), str) else cmd.get("timestamp", datetime.now()),
                    cmd.get("screenshot_path", "")
                )
                for cmd in request.command_history
            ]
            session_base_path = str(session_service.current_session_dir) if session_service.current_session_dir else None
            documentation = summarize_commands(
                command_list,
                include_screenshots=request.include_screenshots,
                session_base_path=session_base_path
            )
        else:
            raise HTTPException(status_code=400, detail="Either ocr_text or command_history must be provided")
        
        # Save documentation
        output_path = session_service.get_documentation_path("documentation.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(documentation)
        
        # Finalize session
        session_service.finalize_session()
        
        return DocumentationResponse(
            documentation=documentation,
            session_id=session_id,
            output_path=str(output_path)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate documentation: {str(e)}")


@router.get("/sessions/{session_id}/documentation")
async def get_documentation(session_id: str):
    """Download documentation file."""
    session_info = SessionService.get_session(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_dir = Path(session_info["session_dir"])
    doc_file = session_dir / "documentation.md"
    
    if not doc_file.exists():
        raise HTTPException(status_code=404, detail="Documentation not found")
    
    return FileResponse(
        path=str(doc_file),
        filename=f"documentation_{session_id}.md",
        media_type="text/markdown"
    )


@router.get("/sessions/{session_id}/screenshots")
async def list_screenshots(session_id: str):
    """List all screenshots in a session."""
    session_info = SessionService.get_session(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_dir = Path(session_info["session_dir"])
    screenshots_dir = session_dir / "screenshots"
    
    if not screenshots_dir.exists():
        return {"screenshots": []}
    
    screenshots = []
    for screenshot_file in screenshots_dir.glob("*.png"):
        screenshots.append({
            "filename": screenshot_file.name,
            "path": f"/static/uploads/{screenshot_file.name}",
            "size": screenshot_file.stat().st_size
        })
    
    return {"screenshots": screenshots}

