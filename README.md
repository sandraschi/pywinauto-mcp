# PyWinAuto MCP

A modular, FastMCP 2.10+ compliant server for Windows UI automation using PyWinAuto. Features a plugin-based architecture for extensibility and maintainability.

## 🚀 Features

### Dual Interface Architecture

PyWinAuto MCP is designed with a powerful dual-interface architecture that supports both MCP tools for Claude/LLM integration and REST API endpoints for direct testing and integration:

- **MCP Tools**: Optimized for Claude and other LLM agents via the MCP protocol
- **REST API**: Standard HTTP endpoints for testing, debugging, and direct integration
- **Feature Parity**: Both interfaces provide access to the same core functionality
- **Plugin Support**: All plugins are automatically exposed through both interfaces

### Example: Finding a Window

#### Using MCP Tools (Claude/LLM)

```python
# Claude can call this directly as an MCP tool
window = find_window(
    title="Untitled - Notepad",
    class_name="Notepad"
)
```

#### Using REST API

```http
GET /api/v1/windows/find?title=Untitled%20-%20Notepad&class_name=Notepad
```

#### Response (both interfaces)

```json
{
  "window_handle": 123456,
  "title": "Untitled - Notepad",
  "class_name": "Notepad",
  "process_id": 9876,
  "is_visible": true,
  "is_enabled": true,
  "rectangle": {
    "left": 100,
    "top": 100,
    "right": 800,
    "bottom": 600,
    "width": 700,
    "height": 500
  },
  "process_name": "notepad.exe"
}
```

### Core Features

- **Window Management**: Find, activate, and manipulate windows
- **UI Automation**: Interact with controls, type text, click elements
- **Element Inspection**: Get detailed information about UI elements
- **Screenshots**: Capture window or element screenshots
- **Robust Error Handling**: Built-in retry mechanisms and timeouts
- **MCP Integration**: Seamless integration with the MCP ecosystem

### Plugin System

- **Modular Architecture**: Extend functionality through plugins
- **Built-in Plugins**:
  - **OCR**: Text extraction from images and windows
  - **Security**: Application monitoring and access control
- **Easy to Extend**: Create custom plugins for specialized automation needs

## 🛠 Installation

1. **Prerequisites**:
   - Windows 10/11
   - Python 3.10+
   - Microsoft UI Automation (UIA) support

2. **Install from source**:

   ```powershell
   # Clone the repository
   git clone https://github.com/sandraschi/pywinauto-mcp.git
   cd pywinauto-mcp
   
   # Create and activate a virtual environment
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # Install with all dependencies (including OCR and security plugins)
   pip install -e ".[all]"

   # Or install only core dependencies
   # pip install -e .
   ```

3. **Install Tesseract OCR** (required for OCR plugin):

   - Download and install Tesseract from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - Add Tesseract to your system PATH

## 🚀 Quick Start

### Option 1: DXT Package (Recommended)

1. **Install the DXT CLI**:

   ```bash
   npm install -g @anthropic-ai/dxt
   ```

2. **Download the latest DXT package** from the [releases page](https://github.com/sandraschi/pywinauto-mcp/releases)

3. **Install the DXT package**:

   ```bash
   dxt install dxt/pywinauto-mcp-0.1.0.dxt
   ```

4. **Start the server**:

   ```bash
   dxt run pywinauto-mcp
   ```

### Option 2: From Source

1. **Start the MCP server**:

   ```powershell
   uvicorn pywinauto_mcp.main:app --reload
   ```

2. **Example: Find and interact with Notepad**

   ```powershell
   # Find Notepad window
   $window = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/windows/find" -Method Post -Body (@{title="Untitled - Notepad"; timeout=5} | ConvertTo-Json) -ContentType "application/json"
   
   # Type some text
   Invoke-RestMethod -Uri "http://localhost:8000/api/v1/element/type" -Method Post -Body (@{
       window_id = $window.window_handle
       control_id = "Edit"
       text = "Hello from PyWinAuto MCP!"
   } | ConvertTo-Json) -ContentType "application/json"
   ```

## 🧩 Plugin System

PyWinAuto MCP uses a modular plugin system to extend its functionality. Plugins can be enabled/disabled via configuration.

### Available Plugins

#### OCR Plugin

Extract text from windows and images using Tesseract OCR.

**Features**:

- Extract text from any window or image
- Find text positions within images
- Support for multiple languages
- Region-based text extraction

**Example**:

```python
# Extract text from a window region
text = await mcp.extract_text(
    window_handle=window_handle,
    x=100, y=100, width=200, height=50,
    lang="eng"
)
```

#### Security Plugin

Monitor applications and detect unauthorized access.

**Features**:

- Application whitelisting/blacklisting
- Unauthorized access detection
- Activity logging
- Configurable alerts

### Creating Custom Plugins

1. Create a new Python module in `src/pywinauto_mcp/plugins/`
2. Create a class that inherits from `PyWinAutoPlugin`
3. Implement the required methods
4. Register your plugin using the `@register_plugin` decorator

**Example Plugin**:

```python
from pywinauto_mcp.core.plugin import PyWinAutoPlugin, register_plugin

@register_plugin
class MyCustomPlugin(PyWinAutoPlugin):
    @classmethod
    def get_name(cls) -> str:
        return "my_plugin"

    def register_tools(self):
        @self.app.mcp.tool("my_tool")
        async def my_tool(param: str):
            return {"result": f"Processed: {param}"}
```

## 📚 API Documentation

### Windows

- `POST /api/v1/windows/find` - Find a window by attributes
- `GET /api/v1/windows` - List all top-level windows
- `GET /api/v1/windows/{handle}` - Get window details
- `POST /api/v1/windows/{handle}/activate` - Activate a window
- `POST /api/v1/windows/{handle}/close` - Close a window

### Elements

- `POST /api/v1/element/click` - Click an element
- `POST /api/v1/element/type` - Type text into an element
- `POST /api/v1/element/get` - Get element information
- `POST /api/v1/element/screenshot` - Take a screenshot of an element

## 🔧 Configuration

### DXT Configuration

When using the DXT package, create a `.env` file in the DXT package directory (typically in `~/.dxt/packages/pywinauto-mcp/.env` on Linux/macOS or `%USERPROFILE%\.dxt\packages\pywinauto-mcp\.env` on Windows).

### Local Development

For local development, create a `.env` file in the project root:

```ini
# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# PyWinAuto Settings
TIMEOUT=10.0
RETRY_ATTEMPTS=3
RETRY_DELAY=1.0

# Face Recognition Settings
FACE_RECOGNITION_TOLERANCE=0.6
FACE_RECOGNITION_MODEL=hog

# Security Settings
SECURITY_ALERT_EMAIL=alerts@example.com
SECURITY_WEBHOOK_URL=

# Screenshot Settings
SCREENSHOT_DIR=./screenshots
SCREENSHOT_FORMAT=png
```

## 🔒 Security Features

### Face Recognition

```python
# Enroll a new face
curl -X POST "http://localhost:8000/face-recognition/enroll" \
     -H "Content-Type: multipart/form-data" \
     -F "name=John Doe" \
     -F "image_file=@john.jpg"

# Verify face using webcam
curl -X POST "http://localhost:8000/face-recognition/verify/webcam?confidence_threshold=0.7"

# List known faces
curl "http://localhost:8000/face-recognition/faces"
```

### Security Monitoring

```python
# Monitor sensitive applications
curl -X POST "http://localhost:8000/security/monitor/apps/start" \
     -H "Content-Type: application/json" \
     -d '{"app_names": ["banking_app.exe"], "webcam_required": true}'

# Start intruder detection
curl -X POST "http://localhost:8000/security/monitor/intruder/start" \
     -H "Content-Type: application/json" \
     -d '{"sensitivity": 0.8, "alert_contacts": ["security@example.com"]}'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PyWinAuto](https://pywinauto.github.io/) for the excellent Windows automation library
- [FastMCP](https://github.com/wandb/fastmcp) for the MCP server framework
