"""Face recognition portmanteau tool for PyWinAuto MCP.

Loaded only when the operator sets **PYWINAUTO_MCP_ENABLE_FACE=1** (and face deps are installed).
See **docs/SAFETY.md** §5.

PORTMANTEAU PATTERN RATIONALE:
Instead of creating 5+ separate tools (one per face recognition operation), this tool consolidates
related face recognition operations into a single interface. This design:
- Prevents tool explosion (5+ tools → 1 tool) while maintaining full functionality
- Improves discoverability by grouping related operations together
- Follows FastMCP 2.13+ best practices for feature-rich MCP servers

SUPPORTED OPERATIONS:
- add: Add a new face to the recognition database
- recognize: Recognize faces in an image
- list: List all known faces
- delete: Delete a known face
- capture: Capture from a local camera (OpenCV index) and recognize — use built-in or USB UVC webcam; not Tapo/IP cameras
"""

import base64
import logging
import os
import pickle
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import cv2
import numpy as np

# Import the FastMCP app instance
try:
    from pywinauto_mcp.app import app

    logger = logging.getLogger(__name__)
    logger.info("Successfully imported FastMCP app instance in portmanteau_face")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import FastMCP app in portmanteau_face: {e}")
    app = None

# Try to import face_recognition
try:
    import face_recognition

    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning("face_recognition library not available")

# Try to import encryption
try:
    from cryptography.fernet import Fernet, InvalidToken

    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False

# Constants
DEFAULT_KNOWN_FACES_DIR = Path("data/known_faces")
DEFAULT_ENCRYPTION_KEY = b"your-32-byte-encryption-key-here"


@dataclass
class FaceData:
    """Stores face encoding and metadata."""

    name: str
    encoding: bytes
    created_at: str
    last_used: str | None = None
    usage_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class FaceRecognitionManager:
    """Manages face recognition operations."""

    def __init__(
        self,
        known_faces_dir: Path = DEFAULT_KNOWN_FACES_DIR,
        tolerance: float = 0.6,
        model: str = "hog",
    ):
        self.known_faces_dir = Path(known_faces_dir)
        self.known_faces_dir.mkdir(parents=True, exist_ok=True)
        self.tolerance = tolerance
        self.model = model
        self.known_faces: dict[str, FaceData] = {}

        if ENCRYPTION_AVAILABLE:
            self.cipher_suite = Fernet(base64.urlsafe_b64encode(DEFAULT_ENCRYPTION_KEY))
        else:
            self.cipher_suite = None

        self.load_known_faces()

    def load_known_faces(self):
        """Load known faces from disk."""
        self.known_faces = {}
        if not self.known_faces_dir.exists():
            return

        for file_path in self.known_faces_dir.glob("*.pkl"):
            try:
                with open(file_path, "rb") as f:
                    data = f.read()

                if self.cipher_suite:
                    try:
                        data = self.cipher_suite.decrypt(data)
                    except InvalidToken:
                        logger.debug("Decryption failed - possibly unencrypted legacy file.")

                face_data = pickle.loads(data)
                if isinstance(face_data, dict):
                    face_data = FaceData(**face_data)

                self.known_faces[face_data.name] = face_data
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")

    def save_face(self, name: str) -> bool:
        """Save face data to disk."""
        if name not in self.known_faces:
            return False

        face_data = self.known_faces[name]
        try:
            from datetime import datetime

            face_data.last_used = datetime.now().isoformat()
            face_data.usage_count += 1

            data = pickle.dumps(face_data)
            if self.cipher_suite:
                data = self.cipher_suite.encrypt(data)

            file_path = self.known_faces_dir / f"{name.lower().replace(' ', '_')}.pkl"
            with open(file_path, "wb") as f:
                f.write(data)

            return True
        except Exception as e:
            logger.error(f"Error saving face {name}: {e}")
            return False


# Create global instance if available
face_manager = None
if FACE_RECOGNITION_AVAILABLE:
    try:
        face_manager = FaceRecognitionManager()
    except Exception as e:
        logger.error(f"Failed to initialize face manager: {e}")


if app is not None:
    logger.info("Registering portmanteau_face tool with FastMCP")

    @app.tool(
        name="automation_face",
        description="""Optional face enrollment and matching (local). Requires PYWINAUTO_MCP_ENABLE_FACE=1 and the face extra.

Capture uses OpenCV VideoCapture: built-in laptop camera or USB UVC webcam (camera_index 0, 1, …). Not Tapo/IP/RTSP.

SUPPORTED OPERATIONS:
- add: Register a face from an image file.
- recognize: Match faces in an image.
- list: List registered names.
- delete: Remove a profile.
- capture: Webcam capture then recognize.

Examples:
    automation_face("add", name="John Doe", image_path="john.jpg")
    automation_face("recognize", image_path="unknown.jpg")

""",
    )
    def automation_face(
        operation: Literal["add", "recognize", "list", "delete", "capture"],
        name: str | None = None,
        image_path: str | None = None,
        camera_index: int = 0,
        save_capture_path: str | None = None,
        tolerance: float = 0.6,
    ) -> dict[str, Any]:
        """Face recognition operations.

        Args:
            operation: The operation to perform
            name: Person's name for add/delete operations
            image_path: Path to image file for add/recognize operations
            camera_index: OpenCV device index (0, 1, …) for built-in or USB UVC webcam — not Tapo/RTSP
            save_capture_path: Path to save captured image
            tolerance: Face matching tolerance (lower = stricter)

        Returns:
            Operation-specific result with face recognition data

        """
        try:
            timestamp = time.time()

            if not FACE_RECOGNITION_AVAILABLE:
                return {
                    "status": "error",
                    "operation": operation,
                    "error": "face_recognition library not installed. Install with: pip install face_recognition",
                }

            if face_manager is None:
                return {
                    "status": "error",
                    "operation": operation,
                    "error": "Face recognition manager not initialized",
                }

            biometric_metadata = {
                "timestamp": timestamp,
                "model": face_manager.model,
                "tolerance": tolerance,
                "encryption": ENCRYPTION_AVAILABLE,
            }

            # === ADD OPERATION ===
            if operation == "add":
                if not name:
                    return {
                        "status": "error",
                        "operation": "add",
                        "error": "name parameter is required",
                    }
                if not image_path:
                    return {
                        "status": "error",
                        "operation": "add",
                        "error": "image_path parameter is required",
                    }
                if not os.path.exists(image_path):
                    return {
                        "status": "error",
                        "operation": "add",
                        "error": f"Image file not found: {image_path}",
                    }

                # Load image and find face
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)

                if not encodings:
                    return {
                        "status": "error",
                        "operation": "add",
                        "error": "No faces found in the image",
                    }

                if len(encodings) > 1:
                    return {
                        "status": "error",
                        "operation": "add",
                        "error": "Multiple faces found. Please provide image with single face.",
                    }

                from datetime import datetime

                now = datetime.now().isoformat()

                face_data = FaceData(
                    name=name,
                    encoding=encodings[0].tobytes(),
                    created_at=now,
                    last_used=now,
                    usage_count=1,
                )

                face_manager.known_faces[name] = face_data

                if face_manager.save_face(name):
                    return {
                        "status": "success",
                        "operation": "add",
                        "name": name,
                        "message": "Face added successfully",
                        "timestamp": timestamp,
                        "biometric_metadata": biometric_metadata,
                    }
                else:
                    return {
                        "status": "error",
                        "operation": "add",
                        "error": "Failed to save face data",
                    }

            # === RECOGNIZE OPERATION ===
            elif operation == "recognize":
                if not image_path:
                    return {
                        "status": "error",
                        "operation": "recognize",
                        "error": "image_path parameter is required",
                    }
                if not os.path.exists(image_path):
                    return {
                        "status": "error",
                        "operation": "recognize",
                        "error": f"Image file not found: {image_path}",
                    }

                image = face_recognition.load_image_file(image_path)
                face_locations = face_recognition.face_locations(image, model=face_manager.model)
                face_encodings = face_recognition.face_encodings(image, face_locations)

                if not face_encodings:
                    return {
                        "status": "success",
                        "operation": "recognize",
                        "faces_found": 0,
                        "matches": [],
                        "timestamp": timestamp,
                        "biometric_metadata": biometric_metadata,
                    }

                matches = []
                for encoding in face_encodings:
                    match_found = False

                    for known_name, known_face in face_manager.known_faces.items():
                        known_encoding = np.frombuffer(known_face.encoding, dtype=np.float64)

                        match = face_recognition.compare_faces(
                            [known_encoding], encoding, tolerance=tolerance
                        )

                        if match[0]:
                            distance = float(
                                face_recognition.face_distance([known_encoding], encoding)[0]
                            )

                            matches.append(
                                {
                                    "name": known_name,
                                    "confidence": 1.0 - distance,
                                    "face_distance": distance,
                                }
                            )
                            match_found = True
                            break

                    if not match_found:
                        matches.append({"name": "unknown", "confidence": 0.0, "face_distance": 1.0})

                return {
                    "status": "success",
                    "operation": "recognize",
                    "faces_found": len(face_encodings),
                    "matches": matches,
                    "timestamp": timestamp,
                    "biometric_metadata": biometric_metadata,
                }

            # === LIST OPERATION ===
            elif operation == "list":
                faces = []
                for name, face_data in face_manager.known_faces.items():
                    faces.append(
                        {
                            "name": name,
                            "created_at": face_data.created_at,
                            "last_used": face_data.last_used,
                            "usage_count": face_data.usage_count,
                        }
                    )

                return {
                    "status": "success",
                    "operation": "list",
                    "count": len(faces),
                    "faces": faces,
                    "timestamp": timestamp,
                    "biometric_metadata": biometric_metadata,
                }

            # === DELETE OPERATION ===
            elif operation == "delete":
                if not name:
                    return {
                        "status": "error",
                        "operation": "delete",
                        "error": "name parameter is required",
                    }

                if name not in face_manager.known_faces:
                    return {
                        "status": "error",
                        "operation": "delete",
                        "error": f"No face found for '{name}'",
                    }

                del face_manager.known_faces[name]

                file_path = face_manager.known_faces_dir / f"{name.lower().replace(' ', '_')}.pkl"
                if file_path.exists():
                    file_path.unlink()

                return {
                    "status": "success",
                    "operation": "delete",
                    "name": name,
                    "message": "Face deleted successfully",
                    "timestamp": timestamp,
                    "biometric_metadata": biometric_metadata,
                }

            # === CAPTURE OPERATION ===
            elif operation == "capture":
                cap = cv2.VideoCapture(camera_index)

                if not cap.isOpened():
                    return {
                        "status": "error",
                        "operation": "capture",
                        "error": f"Could not open camera at index {camera_index}",
                    }

                ret, frame = cap.read()
                cap.release()

                if not ret:
                    return {
                        "status": "error",
                        "operation": "capture",
                        "error": "Failed to capture image from camera",
                    }

                # Save captured image
                if save_capture_path:
                    cv2.imwrite(save_capture_path, frame)
                    captured_path = save_capture_path
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
                        cv2.imwrite(f.name, frame)
                        captured_path = f.name

                # Recognize faces in captured image
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(
                    rgb_frame, model=face_manager.model
                )
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                matches = []
                for encoding in face_encodings:
                    match_found = False

                    for known_name, known_face in face_manager.known_faces.items():
                        known_encoding = np.frombuffer(known_face.encoding, dtype=np.float64)

                        match = face_recognition.compare_faces(
                            [known_encoding], encoding, tolerance=tolerance
                        )

                        if match[0]:
                            distance = float(
                                face_recognition.face_distance([known_encoding], encoding)[0]
                            )

                            matches.append(
                                {
                                    "name": known_name,
                                    "confidence": 1.0 - distance,
                                    "face_distance": distance,
                                }
                            )
                            match_found = True
                            break

                    if not match_found:
                        matches.append({"name": "unknown", "confidence": 0.0, "face_distance": 1.0})

                return {
                    "status": "success",
                    "operation": "capture",
                    "image_path": captured_path,
                    "faces_found": len(face_encodings),
                    "matches": matches,
                    "timestamp": timestamp,
                    "biometric_metadata": biometric_metadata,
                }

            else:
                return {
                    "status": "error",
                    "error": f"Unknown operation: {operation}",
                    "valid_operations": ["add", "recognize", "list", "delete", "capture"],
                }

        except Exception as e:
            return {
                "status": "error",
                "operation": operation,
                "error": str(e),
                "error_type": type(e).__name__,
            }


__all__ = ["automation_face"]
