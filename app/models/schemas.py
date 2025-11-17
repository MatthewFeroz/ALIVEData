"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SessionCreate(BaseModel):
    """Schema for creating a new session."""
    custom_prefix: Optional[str] = None
    folder_name: Optional[str] = None


class SessionResponse(BaseModel):
    """Schema for session response."""
    session_id: str
    session_dir: str
    start_time: datetime
    pc_name: Optional[str] = None
    pc_name_abbrev: Optional[str] = None


class ScreenshotUpload(BaseModel):
    """Schema for screenshot upload response."""
    screenshot_id: str
    filename: str
    path: str
    timestamp: datetime


class OCRRequest(BaseModel):
    """Schema for OCR processing request."""
    screenshot_id: Optional[str] = None
    image_path: Optional[str] = None


class OCRResponse(BaseModel):
    """Schema for OCR response."""
    text: str
    screenshot_path: Optional[str] = None


class DocumentationRequest(BaseModel):
    """Schema for documentation generation request."""
    ocr_text: Optional[str] = None
    command_history: Optional[List[dict]] = None
    include_screenshots: bool = True


class DocumentationResponse(BaseModel):
    """Schema for documentation response."""
    documentation: str
    session_id: str
    output_path: str


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None


class SessionListResponse(BaseModel):
    """Schema for listing sessions."""
    sessions: List[SessionResponse]
    total: int

