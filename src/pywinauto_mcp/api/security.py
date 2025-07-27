"""
Security API endpoints for PyWinAutoMCP.

This module provides FastAPI routes for security-related functionality.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime, time

from ...security import app_monitor, intruder_detector, SecurityLevel, SecurityEvent

router = APIRouter(
    prefix="/security",
    tags=["security"],
    responses={404: {"description": "Not found"}},
)

# Request/Response Models
class TimeWindow(BaseModel):
    """Time window for monitoring."""
    start: str = Field(..., description="Start time in HH:MM format")
    end: str = Field(..., description="End time in HH:MM format")
    days: Optional[List[int]] = Field(
        None,
        description="List of weekdays (0=Monday, 6=Sunday). If None, applies to all days.",
        ge=0,
        le=6
    )

class MonitorSensitiveAppsRequest(BaseModel):
    """Request model for monitoring sensitive applications."""
    app_names: List[str] = Field(
        ...,
        description="List of application names to monitor (e.g., ['notepad.exe', 'chrome.exe'])",
        min_items=1
    )
    webcam_required: bool = Field(
        True,
        description="Whether to require webcam verification for access"
    )
    alert_email: Optional[EmailStr] = Field(
        None,
        description="Email address to send alerts to"
    )
    monitor_duration_minutes: int = Field(
        60,
        description="Duration to monitor for (in minutes)",
        gt=0
    )
    time_windows: Optional[List[TimeWindow]] = Field(
        None,
        description="Time windows when monitoring should be active"
    )

class IntruderDetectionRequest(BaseModel):
    """Request model for intruder detection."""
    sensitivity: float = Field(
        0.7,
        description="Motion detection sensitivity (0.1-1.0)",
        ge=0.1,
        le=1.0
    )
    duration_minutes: int = Field(
        5,
        description="Duration to monitor (in minutes)",
        gt=0
    )
    alert_contacts: Optional[List[EmailStr]] = Field(
        None,
        description="List of email addresses to alert"
    )
    record_video: bool = Field(
        True,
        description="Whether to record video when motion is detected"
    )

class SecurityEventResponse(BaseModel):
    """Response model for security events."""
    timestamp: str
    event_type: str
    level: str
    message: str
    details: Dict[str, Any]

    @classmethod
    def from_event(cls, event: SecurityEvent) -> 'SecurityEventResponse':
        return cls(
            timestamp=event.timestamp,
            event_type=event.event_type,
            level=event.level.value,
            message=event.message,
            details=event.details or {}
        )

class MonitoringStatusResponse(BaseModel):
    """Response model for monitoring status."""
    running: bool
    start_time: Optional[datetime]
    events_logged: int
    last_event: Optional[SecurityEventResponse]

# Background Tasks
monitoring_tasks = {}

# Helper Functions
def get_monitoring_status(monitor) -> MonitoringStatusResponse:
    """Get the status of a monitoring task."""
    return MonitoringStatusResponse(
        running=monitor.running,
        start_time=getattr(monitor, 'start_time', None),
        events_logged=len(monitor.events),
        last_event=SecurityEventResponse.from_event(monitor.events[-1]) if monitor.events else None
    )

# API Endpoints
@router.post("/monitor/apps/start", response_model=MonitoringStatusResponse)
async def start_app_monitoring(
    request: MonitorSensitiveAppsRequest,
    background_tasks: BackgroundTasks
):
    """
    Start monitoring sensitive applications.
    
    This endpoint starts a background task that monitors specified applications
    and enforces security policies like webcam verification.
    """
    if app_monitor.running:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application monitoring is already running"
        )
    
    # Convert time windows to dict for the security module
    time_windows = None
    if request.time_windows:
        time_windows = [tw.dict() for tw in request.time_windows]
    
    # Start monitoring in background
    background_tasks.add_task(
        app_monitor.monitor_sensitive_apps,
        app_names=request.app_names,
        webcam_required=request.webcam_required,
        alert_email=request.alert_email,
        monitor_duration_minutes=request.monitor_duration_minutes,
        time_windows=time_windows
    )
    
    return get_monitoring_status(app_monitor)

@router.post("/monitor/intruder/start", response_model=MonitoringStatusResponse)
async def start_intruder_detection(
    request: IntruderDetectionRequest,
    background_tasks: BackgroundTasks
):
    """
    Start intruder detection.
    
    This endpoint starts a background task that monitors for motion using
    available cameras and alerts when potential intruders are detected.
    """
    if intruder_detector.running:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Intruder detection is already running"
        )
    
    # Start detection in background
    background_tasks.add_task(
        intruder_detector.detect_intruder,
        sensitivity=request.sensitivity,
        duration_minutes=request.duration_minutes,
        alert_contacts=request.alert_contacts,
        record_video=request.record_video
    )
    
    return get_monitoring_status(intruder_detector)

@router.get("/monitor/apps/status", response_model=MonitoringStatusResponse)
async def get_app_monitoring_status():
    """Get the current status of application monitoring."""
    return get_monitoring_status(app_monitor)

@router.get("/monitor/intruder/status", response_model=MonitoringStatusResponse)
async def get_intruder_detection_status():
    """Get the current status of intruder detection."""
    return get_monitoring_status(intruder_detector)

@router.post("/monitor/apps/stop")
async def stop_app_monitoring():
    """Stop application monitoring."""
    app_monitor.running = False
    return {"status": "stopped", "message": "Application monitoring stopped"}

@router.post("/monitor/intruder/stop")
async def stop_intruder_detection():
    """Stop intruder detection."""
    intruder_detector.running = False
    return {"status": "stopped", "message": "Intruder detection stopped"}

@router.get("/events", response_model=List[SecurityEventResponse])
async def get_security_events(
    limit: int = 100,
    level: Optional[SecurityLevel] = None,
    event_type: Optional[str] = None
):
    """
    Get security events.
    
    Args:
        limit: Maximum number of events to return
        level: Filter by security level (low, medium, high, critical)
        event_type: Filter by event type
    """
    events = app_monitor.events + intruder_detector.events
    
    # Sort by timestamp (newest first)
    events.sort(key=lambda e: e.timestamp, reverse=True)
    
    # Apply filters
    if level:
        events = [e for e in events if e.level == level]
    if event_type:
        events = [e for e in events if e.event_type == event_type]
    
    # Apply limit
    events = events[:limit]
    
    return [SecurityEventResponse.from_event(e) for e in events]

# Register cleanup handlers
@router.on_event("shutdown")
async def cleanup():
    """Clean up resources on shutdown."""
    app_monitor.running = False
    intruder_detector.running = False
