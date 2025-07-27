"""
Tests for face recognition functionality.
"""
import os
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the parent directory to the Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from pywinauto_mcp.face_recognition import FaceRecognition, FaceData

# Test data
TEST_IMAGE_DIR = Path(__file__).parent / "test_images"
KNOWN_FACE_IMAGE = TEST_IMAGE_DIR / "known_face.jpg"
UNKNOWN_FACE_IMAGE = TEST_IMAGE_DIR / "unknown_face.jpg"

# Skip face recognition tests if test images don't exist
pytestmark = pytest.mark.skipif(
    not KNOWN_FACE_IMAGE.exists() or not UNKNOWN_FACE_IMAGE.exists(),
    reason="Test images not found"
)

@pytest.fixture
def face_rec():
    """Fixture that provides a FaceRecognition instance for testing."""
    # Use a temporary directory for test data
    with patch('pywinauto_mcp.face_recognition.KNOWN_FACES_DIR', 
               Path("tests/test_data/known_faces")):
        # Create the test directory if it doesn't exist
        os.makedirs("tests/test_data/known_faces", exist_ok=True)
        
        # Initialize with a test encryption key
        with patch('pywinauto_mcp.face_recognition.ENCRYPTION_KEY', 
                  b'test-key-1234567890123456789012'):
            yield FaceRecognition(tolerance=0.6, model='hog')
    
    # Cleanup: Remove test data after tests
    import shutil
    if os.path.exists("tests/test_data"):
        shutil.rmtree("tests/test_data")

def test_add_known_face(face_rec):
    """Test adding a known face."""
    # Test with image path
    success = face_rec.add_known_face("Test User", str(KNOWN_FACE_IMAGE))
    assert success
    assert "Test User" in face_rec.known_faces
    
    # Test with image data
    with open(KNOWN_FACE_IMAGE, 'rb') as f:
        image_data = f.read()
    success = face_rec.add_known_face("Test User 2", image_data=image_data)
    assert success
    assert "Test User 2" in face_rec.known_faces

def test_remove_known_face(face_rec):
    """Test removing a known face."""
    # First add a face
    face_rec.add_known_face("Test User", str(KNOWN_FACE_IMAGE))
    assert "Test User" in face_rec.known_faces
    
    # Then remove it
    success = face_rec.remove_known_face("Test User")
    assert success
    assert "Test User" not in face_rec.known_faces
    
    # Try removing non-existent face
    success = face_rec.remove_known_face("Non-existent User")
    assert not success

def test_recognize_face(face_rec):
    """Test recognizing a face."""
    # Add a known face
    face_rec.add_known_face("Test User", str(KNOWN_FACE_IMAGE))
    
    # Test with known face
    with open(KNOWN_FACE_IMAGE, 'rb') as f:
        image_data = f.read()
    success, name, confidence = face_rec.recognize_face(image_data)
    assert success
    assert name == "Test User"
    assert 0.0 <= confidence <= 1.0
    
    # Test with unknown face
    with open(UNKNOWN_FACE_IMAGE, 'rb') as f:
        unknown_image_data = f.read()
    success, name, confidence = face_rec.recognize_face(unknown_image_data)
    assert not success
    assert name is None
    assert confidence == 0.0

@patch('cv2.VideoCapture')
def test_capture_and_verify_face(mock_video_capture, face_rec):
    """Test face verification with webcam."""
    # Mock the video capture
    mock_camera = MagicMock()
    mock_video_capture.return_value = mock_camera
    
    # Mock frame data
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    mock_camera.read.return_value = (True, test_frame)
    
    # Mock face detection
    with patch('face_recognition.face_locations') as mock_face_locations, \
         patch('face_recognition.face_encodings') as mock_face_encodings:
        
        # Setup mock for no face detected
        mock_face_locations.return_value = []
        
        # Test with no face in frame (should return False)
        success, name, confidence = face_rec.capture_and_verify_face(timeout=1)
        assert not success
        assert name is None
        assert confidence == 0.0
        
        # Setup mock for face detected but not recognized
        mock_face_locations.return_value = [(100, 200, 300, 400)]
        mock_face_encodings.return_value = [np.zeros(128)]
        
        # Add a known face with a different encoding
        face_rec.add_known_face("Test User", str(KNOWN_FACE_IMAGE))
        
        # Test with face detected but not recognized (different encoding)
        success, name, confidence = face_rec.capture_and_verify_face(timeout=1)
        assert not success
        assert name is None
        assert confidence == 0.0

def test_face_encryption(face_rec):
    """Test that face encodings are properly encrypted/decrypted."""
    # Create a test encoding
    test_encoding = np.random.rand(128)
    
    # Encrypt and decrypt
    encrypted = face_rec.encrypt_encoding(test_encoding)
    decrypted = face_rec.decrypt_encoding(encrypted)
    
    # Check that decrypted data matches original
    assert np.allclose(test_encoding, decrypted)
    
    # Check that encrypted data is different from original
    assert not np.array_equal(test_encoding.tobytes(), encrypted)
