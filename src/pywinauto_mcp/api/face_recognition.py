"""
Face recognition API endpoints for PyWinAutoMCP.

This module provides FastAPI routes for face recognition functionality.
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastmcp import mcp
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
import base64
import io

from ...face_recognition import face_recognizer, FaceData
from ...security import SecurityLevel

router = APIRouter(
    prefix="/face-recognition",
    tags=["face-recognition"],
    responses={404: {"description": "Not found"}},
)

# Request/Response Models
class FaceEnrollmentRequest(BaseModel):
    """Request model for enrolling a new face."""
    name: str = Field(..., description="Name or identifier for the person")
    image_data: Optional[str] = Field(
        None,
        description="Base64-encoded image data (alternative to image_file)"
    )

class FaceVerificationRequest(BaseModel):
    """Request model for verifying a face."""
    image_data: str = Field(..., description="Base64-encoded image data")
    confidence_threshold: float = Field(
        0.7,
        description="Minimum confidence score to accept a match (0-1)",
        ge=0.0,
        le=1.0
    )

class FaceVerificationResponse(BaseModel):
    """Response model for face verification."""
    success: bool
    name: Optional[str] = None
    confidence: Optional[float] = None
    message: str

class FaceInfo(BaseModel):
    """Information about a known face."""
    name: str
    created_at: str
    last_used: Optional[str] = None
    usage_count: int = 0

# API Endpoints
@mcp.tool("Enroll a new face")
@router.post("/enroll", status_code=status.HTTP_201_CREATED)
async def enroll_face(
    name: str = Form(...),
    image_file: UploadFile = File(..., description="Image file containing the face"),
):
    """
    Enroll a new face for recognition.
    
    This endpoint allows you to register a new face by providing an image.
    The face will be extracted and stored for future recognition.
    """
    try:
        # Read image data
        image_data = await image_file.read()
        
        # Add the face
        success = face_recognizer.add_known_face(
            name=name,
            image_data=image_data
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not detect a face in the provided image"
            )
            
        return {
            "status": "success",
            "message": f"Successfully enrolled face for {name}",
            "name": name
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enrolling face: {str(e)}"
        )

@mcp.tool("Verify a face")
@router.post("/verify", response_model=FaceVerificationResponse)
async def verify_face(
    request: FaceVerificationRequest
) -> FaceVerificationResponse:
    """
    Verify a face against known faces.
    
    This endpoint takes an image and checks if it matches any known faces.
    Returns the name and confidence score if a match is found.
    """
    try:
        # Decode base64 image data
        image_data = base64.b64decode(request.image_data)
        
        # Verify the face
        success, name, confidence = face_recognizer.recognize_face(image_data)
        
        if success and confidence >= request.confidence_threshold:
            return FaceVerificationResponse(
                success=True,
                name=name,
                confidence=confidence,
                message=f"Face recognized as {name} with {confidence*100:.1f}% confidence"
            )
        else:
            return FaceVerificationResponse(
                success=False,
                message="No matching face found" if success else "Face not recognized",
                confidence=confidence if success else 0.0
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying face: {str(e)}"
        )

@mcp.tool("Verify face with webcam")
@router.post("/verify/webcam", response_model=FaceVerificationResponse)
async def verify_face_webcam(
    confidence_threshold: float = 0.7,
    timeout: int = 30
) -> FaceVerificationResponse:
    """
    Verify a face using the webcam.
    
    This endpoint activates the webcam and attempts to recognize a face.
    It will continue trying until a match is found or the timeout is reached.
    """
    try:
        success, name, confidence = face_recognizer.capture_and_verify_face(
            timeout=timeout,
            confidence_threshold=confidence_threshold
        )
        
        if success:
            return FaceVerificationResponse(
                success=True,
                name=name,
                confidence=confidence,
                message=f"Face recognized as {name} with {confidence*100:.1f}% confidence"
            )
        else:
            return FaceVerificationResponse(
                success=False,
                message="No matching face found within the timeout period",
                confidence=0.0
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during face verification: {str(e)}"
        )

@mcp.tool("List known faces")
@router.get("/faces", response_model=List[FaceInfo])
async def list_known_faces():
    """
    List all known faces.
    
    Returns a list of all enrolled faces with their metadata.
    """
    try:
        faces = []
        for name, face_data in face_recognizer.known_faces.items():
            faces.append(FaceInfo(
                name=face_data.name,
                created_at=face_data.created_at,
                last_used=face_data.last_used,
                usage_count=face_data.usage_count
            ))
        return faces
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing known faces: {str(e)}"
        )

@mcp.tool("Remove a known face")
@router.delete("/faces/{name}")
async def remove_known_face(name: str):
    """
    Remove a known face by name.
    
    This will delete the face data from the system.
    """
    try:
        success = face_recognizer.remove_known_face(name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No face found with name '{name}'"
            )
            
        return {
            "status": "success",
            "message": f"Successfully removed face '{name}'"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing face: {str(e)}"
        )

# Register cleanup handler
@router.on_event("shutdown")
async def cleanup():
    """Clean up resources on shutdown."""
    face_recognizer.save_known_faces()
