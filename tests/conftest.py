"""Pytest configuration and shared fixtures for PyWinAuto MCP tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Environment-aware CI vs local (mcp-central-docs: standards/testing-environment-aware.md)
from tests.conftest_env import (  # noqa: E402
    environment_report,
    pytest_configure,
    pytest_runtest_setup,
    skip_if_device_unreachable,
)


@pytest.fixture(scope="session")
def app_instance():
    """Get the FastMCP app instance."""
    from pywinauto_mcp.app import app

    return app


@pytest.fixture
def mock_window():
    """Create a mock window object."""
    window = MagicMock()
    window.title = "Test Window"
    window.handle = 12345
    window.isVisible = True
    window.isEnabled = True
    window.rectangle = MagicMock()
    window.rectangle.left = 100
    window.rectangle.top = 100
    window.rectangle.right = 800
    window.rectangle.bottom = 600
    window.rectangle.width = 700
    window.rectangle.height = 500
    window.class_name = "TestWindowClass"
    window.process_id = 1234
    window.process_name = "test.exe"
    return window


@pytest.fixture
def mock_element():
    """Create a mock UI element."""
    element = MagicMock()
    element.automation_id = "btnOK"
    element.name = "OK Button"
    element.control_type = "Button"
    element.is_visible = True
    element.is_enabled = True
    element.rectangle = MagicMock()
    element.rectangle.left = 200
    element.rectangle.top = 300
    element.rectangle.right = 300
    element.rectangle.bottom = 350
    element.rectangle.width = 100
    element.rectangle.height = 50
    element.text = "OK"
    return element


@pytest.fixture
def mock_desktop():
    """Create a mock Desktop object."""
    desktop = MagicMock()
    return desktop


@pytest.fixture
def mock_application():
    """Create a mock Application object."""
    app = MagicMock()
    app.window.return_value = MagicMock()
    return app


@pytest.fixture
def mock_pyautogui():
    """Mock pyautogui for testing."""
    with patch("pywinauto_mcp.tools.basic_tools.pyautogui") as mock:
        mock.position.return_value = (500, 500)
        mock.size.return_value = (1920, 1080)
        mock.click.return_value = None
        mock.moveTo.return_value = None
        mock.scroll.return_value = None
        mock.typewrite.return_value = None
        mock.press.return_value = None
        mock.hotkey.return_value = None
        yield mock


@pytest.fixture
def mock_pywinauto():
    """Mock pywinauto for testing."""
    with (
        patch("pywinauto_mcp.tools.window.Application") as mock_app,
        patch("pywinauto_mcp.tools.window.findwindows") as mock_find,
        patch("pywinauto_mcp.tools.window.Desktop") as mock_desktop,
    ):
        mock_window = MagicMock()
        mock_window.wrapper_object.return_value = MagicMock()
        mock_app.return_value = mock_window

        yield {"Application": mock_app, "findwindows": mock_find, "Desktop": mock_desktop}


@pytest.fixture
def mock_pygetwindow():
    """Mock pygetwindow for testing."""
    with patch("pywinauto_mcp.tools.system_tools.gw") as mock:
        mock_window = MagicMock()
        mock_window.title = "Test Window"
        mock_window.isActive = True
        mock.getWindowsWithTitle.return_value = [mock_window]
        mock.getAllWindows.return_value = [mock_window]
        yield mock


@pytest.fixture
def mock_psutil():
    """Mock psutil for testing."""
    with patch("pywinauto_mcp.tools.system_tools.psutil") as mock:
        mock_process = MagicMock()
        mock_process.name.return_value = "test.exe"
        mock_process.pid = 1234
        mock.process_iter.return_value = [mock_process]
        yield mock


@pytest.fixture
def temp_test_dir(tmp_path):
    """Create a temporary directory for test files."""
    return tmp_path


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks before each test."""
    yield
    # Cleanup after test if needed


@pytest.fixture
def sample_image_path(tmp_path):
    """Create a sample image file for testing."""
    from PIL import Image

    img = Image.new("RGB", (100, 100), color="red")
    img_path = tmp_path / "test_image.png"
    img.save(img_path)
    return str(img_path)


@pytest.fixture
def mock_ocr():
    """Mock OCR functionality."""
    with patch("pywinauto_mcp.tools.visual_tools.pytesseract") as mock:
        mock.image_to_string.return_value = "Sample OCR Text"
        mock.image_to_data.return_value = []
        yield mock


@pytest.fixture
def mock_face_recognition():
    """Mock face recognition functionality."""
    with patch("pywinauto_mcp.tools.face_recognition.face_recognition") as mock:
        mock.face_locations.return_value = [(100, 200, 300, 400)]
        mock.face_encodings.return_value = [[0.1] * 128]
        mock.compare_faces.return_value = [True]
        mock.face_distance.return_value = [0.3]
        yield mock


@pytest.fixture
def mock_cv2():
    """Mock OpenCV for testing."""
    with patch("pywinauto_mcp.tools.visual_tools.cv2") as mock:
        mock.imread.return_value = None
        mock.imwrite.return_value = True
        mock.VideoCapture.return_value = MagicMock()
        yield mock


@pytest.fixture
def mock_pil():
    """Mock PIL/Pillow for testing."""
    with (
        patch("pywinauto_mcp.tools.visual_tools.Image") as mock_image,
        patch("pywinauto_mcp.tools.visual_tools.ImageGrab") as mock_grab,
    ):
        mock_img = MagicMock()
        mock_img.size = (1920, 1080)
        mock_img.save.return_value = None
        mock_image.open.return_value = mock_img
        mock_image.new.return_value = mock_img
        mock_grab.grab.return_value = mock_img

        yield {"Image": mock_image, "ImageGrab": mock_grab}
