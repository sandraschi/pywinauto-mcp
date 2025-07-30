"""
Security monitoring tools for PyWinAutoMCP.

This module provides security-focused monitoring capabilities for Windows systems,
including application monitoring, security sweeps, and intruder detection.
"""
import logging
import time
import os
import json
import smtplib
from datetime import datetime, time as dt_time
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

import cv2
import numpy as np
import psutil
import win32gui
import win32process
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from pywinauto_mcp.config import settings

logger = logging.getLogger(__name__)

# Constants
DEFAULT_ALERT_EMAIL = "security@example.com"
SECURITY_LOG_DIR = Path("logs/security")
SECURITY_LOG_DIR.mkdir(parents=True, exist_ok=True)

class SecurityLevel(str, Enum):
    """Security alert levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityEvent:
    """Represents a security-related event."""
    timestamp: str
    event_type: str
    level: SecurityLevel
    message: str
    details: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "level": self.level.value,
            "message": self.message,
            "details": self.details or {}
        }

class SecurityMonitor:
    """Base class for security monitoring functionality."""
    
    def __init__(self):
        self.running = False
        self.events: List[SecurityEvent] = []
        self._load_known_devices()
    
    def log_event(self, event_type: str, level: SecurityLevel, message: str, details: Dict = None) -> None:
        """Log a security event."""
        event = SecurityEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            level=level,
            message=message,
            details=details or {}
        )
        self.events.append(event)
        self._write_to_log(event)
        
        # Send alert if needed
        if level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            self._send_alert(event)
    
    def _write_to_log(self, event: SecurityEvent) -> None:
        """Write event to log file."""
        log_file = SECURITY_LOG_DIR / f"security_{datetime.now().strftime('%Y%m%d')}.log"
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{json.dumps(event.to_dict())}\n")
        except Exception as e:
            logger.error(f"Failed to write to security log: {e}")
    
    def _send_alert(self, event: SecurityEvent) -> None:
        """Send security alert via configured method (email, etc.)."""
        # TODO: Implement actual alerting (email, SMS, etc.)
        logger.warning(f"SECURITY ALERT ({event.level}): {event.message}")
    
    def _load_known_devices(self) -> None:
        """Load known devices from configuration."""
        self.known_devices = set()  # TODO: Load from persistent storage
    
    def _is_work_hours(self, time_windows: List[Dict] = None) -> bool:
        """Check if current time is within work hours."""
        if not time_windows:
            # Default work hours: Mon-Fri 9AM-5PM
            now = datetime.now()
            if now.weekday() >= 5:  # Saturday or Sunday
                return False
            return dt_time(9, 0) <= now.time() <= dt_time(17, 0)
        
        # Check against custom time windows
        now = datetime.now()
        current_time = now.time()
        
        for window in time_windows:
            start = dt_time.fromisoformat(window["start"])
            end = dt_time.fromisoformat(window["end"])
            
            # Handle overnight windows
            if start < end:
                if start <= current_time <= end:
                    return True
            else:  # Overnight window (e.g., 22:00-06:00)
                if current_time >= start or current_time <= end:
                    return True
        
        return False

class ApplicationMonitor(SecurityMonitor):
    """Monitors application usage and access patterns."""
    
    def monitor_sensitive_apps(
        self,
        app_names: List[str],
        webcam_required: bool = True,
        alert_email: str = None,
        monitor_duration_minutes: int = 60,
        time_windows: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Monitor sensitive applications and enforce security policies.
        
        Args:
            app_names: List of application names to monitor
            webcam_required: Whether to require webcam verification
            alert_email: Email address to send alerts to
            monitor_duration_minutes: Duration to monitor (in minutes)
            time_windows: Time windows when monitoring should be active
            
        Returns:
            Dict with monitoring results
        """
        self.running = True
        start_time = time.time()
        end_time = start_time + (monitor_duration_minutes * 60)
        
        try:
            while self.running and time.time() < end_time:
                if not self._is_work_hours(time_windows):
                    # Check for sensitive apps outside work hours
                    for proc in psutil.process_iter(['name', 'exe', 'pid']):
                        try:
                            proc_name = proc.info['name'].lower()
                            if any(app.lower() in proc_name for app in app_names):
                                self._handle_sensitive_app_access(
                                    proc_name=proc_name,
                                    pid=proc.info['pid'],
                                    webcam_required=webcam_required,
                                    alert_email=alert_email
                                )
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            continue
                
                time.sleep(5)  # Check every 5 seconds
                
        except Exception as e:
            logger.error(f"Error in application monitoring: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Application monitoring failed: {str(e)}"
            )
        finally:
            self.running = False
        
        return {
            "status": "completed",
            "monitored_duration_seconds": time.time() - start_time,
            "events_logged": len(self.events),
            "alerts_generated": sum(1 for e in self.events if e.level in ["high", "critical"])
        }
    
    def _handle_sensitive_app_access(
        self,
        proc_name: str,
        pid: int,
        webcam_required: bool,
        alert_email: str
    ) -> None:
        """Handle access to a sensitive application."""
        try:
            # Get window title for more context
            window_title = ""
            try:
                def callback(hwnd, _):
                    nonlocal window_title
                    _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if found_pid == pid:
                        window_title = win32gui.GetWindowText(hwnd)
                        return False
                    return True
                
                win32gui.EnumWindows(callback, None)
            except Exception:
                pass
            
            event_details = {
                "process_name": proc_name,
                "pid": pid,
                "window_title": window_title,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if webcam_required and not self._verify_webcam():
                self.log_event(
                    event_type="unauthorized_app_access",
                    level=SecurityLevel.HIGH,
                    message=f"Unauthorized access to sensitive application: {proc_name}",
                    details=event_details
                )
                
                # TODO: Take action (lock workstation, log out user, etc.)
                
            else:
                self.log_event(
                    event_type="authorized_app_access",
                    level=SecurityLevel.LOW,
                    message=f"Authorized access to sensitive application: {proc_name}",
                    details=event_details
                )
                
        except Exception as e:
            logger.error(f"Error handling sensitive app access: {e}")
    
    def _verify_webcam(self) -> bool:
        """Verify user identity via webcam (placeholder implementation)."""
        # TODO: Implement actual webcam verification
        # This is a placeholder that would normally:
        # 1. Capture an image from the webcam
        # 2. Perform face detection/recognition
        # 3. Return True if authorized, False otherwise
        return False

class IntruderDetector(SecurityMonitor):
    """Detects potential intruders using available cameras."""
    
    def detect_intruder(
        self,
        sensitivity: float = 0.7,
        duration_minutes: int = 5,
        alert_contacts: List[str] = None,
        record_video: bool = True
    ) -> Dict[str, Any]:
        """
        Monitor for intruders using available cameras.
        
        Args:
            sensitivity: Motion detection sensitivity (0.1-1.0)
            duration_minutes: Duration to monitor (in minutes)
            alert_contacts: List of email addresses to alert
            record_video: Whether to record video when motion is detected
            
        Returns:
            Dict with detection results
        """
        self.running = True
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        motion_detected = False
        
        # Initialize video capture
        cap = cv2.VideoCapture(0)  # Default camera
        if not cap.isOpened():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not access camera"
            )
        
        # Initialize video writer if recording
        video_writer = None
        if record_video:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = SECURITY_LOG_DIR / f"intruder_{timestamp}.avi"
            frame_width = int(cap.get(3))
            frame_height = int(cap.get(4))
            video_writer = cv2.VideoWriter(
                str(video_path),
                fourcc,
                20.0,
                (frame_width, frame_height)
            )
        
        try:
            # Read first frame for motion detection
            ret, prev_frame = cap.read()
            if not ret:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to capture video frame"
                )
            
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)
            
            while self.running and time.time() < end_time:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to grayscale and blur
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                
                # Compute difference between frames
                frame_delta = cv2.absdiff(prev_gray, gray)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                
                # Find contours of moving objects
                contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Check for significant motion
                motion_detected = False
                for contour in contours:
                    if cv2.contourArea(contour) < 500:  # Minimum contour area
                        continue
                    motion_detected = True
                    break
                
                if motion_detected:
                    self.log_event(
                        event_type="motion_detected",
                        level=SecurityLevel.HIGH,
                        message="Motion detected in camera view",
                        details={
                            "timestamp": datetime.utcnow().isoformat(),
                            "sensitivity": sensitivity,
                            "contours_found": len(contours)
                        }
                    )
                    
                    if record_video and video_writer is not None:
                        # Draw timestamp on frame
                        cv2.putText(
                            frame,
                            datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                            (10, frame.shape[0] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.35,
                            (0, 0, 255),
                            1
                        )
                        video_writer.write(frame)
                
                # Update previous frame
                prev_gray = gray
                
                # Add small delay
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                time.sleep(0.1)  # Reduce CPU usage
                
        except Exception as e:
            logger.error(f"Error in intruder detection: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Intruder detection failed: {str(e)}"
            )
            
        finally:
            if video_writer is not None:
                video_writer.release()
            cap.release()
            cv2.destroyAllWindows()
            self.running = False
        
        return {
            "status": "completed",
            "monitored_duration_seconds": time.time() - start_time,
            "motion_detected": motion_detected,
            "events_logged": len(self.events)
        }

# Create singleton instances
app_monitor = ApplicationMonitor()
intruder_detector = IntruderDetector()
