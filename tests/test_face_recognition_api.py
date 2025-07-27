"""
Integration tests for face recognition API endpoints.
"""
import os
import pytest
import base64
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Add the parent directory to the Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from pywinauto_mcp.main import app
from pywinauto_mcp.face_recognition import face_recognizer, FaceData

# Test data
TEST_IMAGE_DIR = Path(__file__).parent / "test_images"
KNOWN_FACE_IMAGE = TEST_IMAGE_DIR / "known_face.jpg"
UNKNOWN_FACE_IMAGE = TEST_IMAGE_DIR / "unknown_face.jpg"

# Skip tests if test images don't exist
pytestmark = pytest.mark.skipif(
    not KNOWN_FACE_IMAGE.exists() or not UNKNOWN_FACE_IMAGE.exists(),
    reason="Test images not found"
)

@pytest.fixture(scope="module")
def client():
    """Test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_face_recognizer():
    """Mock the face recognizer for testing."""
    with patch('pywinauto_mcp.face_recognition.face_recognizer') as mock:
        # Setup mock return values
        mock.recognize_face.return_value = (True, "Test User", 0.85)
        mock.capture_and_verify_face.return_value = (True, "Test User", 0.88)
        mock.known_faces = {
            "Test User": FaceData(
                name="Test User",
                encoding=b"test_encoding",
                created_at="2023-01-01T00:00:00",
                last_used="2023-01-01T01:00:00",
                usage_count=5
            )
        }
        yield mock

# Helper function to encode image file to base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Test cases
def test_enroll_face(client, mock_face_recognizer):
    """Test enrolling a new face."""
    # Mock the add_known_face method
    mock_face_recognizer.add_known_face.return_value = True
    
    # Create a test file
    with open(KNOWN_FACE_IMAGE, "rb") as f:
        files = {"image_file": ("test_face.jpg", f, "image/jpeg")}
        
        # Make the request
        response = client.post(
            "/face-recognition/enroll",
            files=files,
            data={"name": "Test User"}
        )
    
    # Check the response
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert response.json()["name"] == "Test User"
    
    # Verify the method was called
    mock_face_recognizer.add_known_face.assert_called_once()
    assert mock_face_recognizer.add_known_face.call_args[1]["name"] == "Test User"

def test_verify_face(client, mock_face_recognizer):
    """Test verifying a face from an image."""
    # Encode test image to base64
    image_base64 = image_to_base64(KNOWN_FACE_IMAGE)
    
    # Make the request
    response = client.post(
        "/face-recognition/verify",
        json={
            "image_data": image_base64,
            "confidence_threshold": 0.7
        }
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["name"] == "Test User"
    assert 0.0 <= data["confidence"] <= 1.0
    
    # Verify the method was called
    mock_face_recognizer.recognize_face.assert_called_once()

@patch('cv2.VideoCapture')
def test_verify_face_webcam(mock_video_capture, client, mock_face_recognizer):
    """Test verifying a face using webcam."""
    # Mock the video capture
    mock_camera = MagicMock()
    mock_video_capture.return_value = mock_camera
    
    # Make the request
    response = client.post(
        "/face-recognition/verify/webcam",
        params={
            "confidence_threshold": 0.7,
            "timeout": 1
        }
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["name"] == "Test User"
    assert 0.0 <= data["confidence"] <= 1.0
    
    # Verify the method was called
    mock_face_recognizer.capture_and_verify_face.assert_called_once()

def test_list_known_faces(client, mock_face_recognizer):
    """Test listing known faces."""
    # Make the request
    response = client.get("/face-recognition/faces")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test User"
    assert data[0]["usage_count"] == 5

def test_remove_known_face(client, mock_face_recognizer):
    """Test removing a known face."""
    # Mock the remove_known_face method
    mock_face_recognizer.remove_known_face.return_value = True
    
    # Make the request
    response = client.delete("/face-recognition/faces/Test%20User")
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Verify the method was called
    mock_face_recognizer.remove_known_face.assert_called_once_with("Test User")

def test_remove_nonexistent_face(client, mock_face_recognizer):
    """Test removing a face that doesn't exist."""
    # Mock the remove_known_face method to return False
    mock_face_recognizer.remove_known_face.return_value = False
    
    # Make the request
    response = client.delete("/face-recognition/faces/Nonexistent%20User")
    
    # Check the response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
