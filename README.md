# PyWinAuto MCP

**Version 0.2.0** | **22 Comprehensive Automation Tools** | **Enterprise-Grade Windows UI Automation**

A sophisticated, FastMCP 2.10+ compliant server for Windows UI automation using PyWinAuto. Features a comprehensive tool ecosystem, face recognition security, and professional DXT packaging with extensive prompt templates for conversational AI interaction.

## 🚀 Features

### 🏆 **22 Comprehensive Automation Tools**
PyWinAuto MCP provides the most complete Windows automation toolkit available:

- **🔍 Window Management** (6 tools): Find, activate, maximize, minimize, position, and close windows
- **🖱️ Mouse Control** (7 tools): Click, move, scroll, drag-and-drop with precision coordinates
- **⌨️ Keyboard Input** (3 tools): Type text, send key combinations, special shortcuts
- **🎯 UI Elements** (6 tools): Click, type, inspect, verify text, get info, check states
- **📸 Visual Intelligence** (3 tools): Screenshots, OCR text extraction, image recognition
- **🔒 Face Recognition** (4 tools): Add faces, recognize, list known faces, webcam verification

### 🤖 **Conversational AI Integration**
- **Extensive Prompt Templates**: 100+ detailed prompts for natural language interaction
- **Contextual Examples**: Real-world usage scenarios for each tool
- **Smart Defaults**: Intelligent parameter handling and error recovery
- **Desktop State Capture**: Complete UI element discovery with visual annotations

### 🏗️ **Enterprise Architecture**
- **Dual Interface Design**: MCP tools + REST API with complete feature parity
- **Security-First**: Face recognition authentication and access controls
- **Professional Packaging**: Complete DXT distribution with all dependencies
- **Plugin System**: Extensible architecture for custom automation tools

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
   dxt install dist/pywinauto-mcp-0.2.0.dxt
   ```

   **Package Features:**
   - **281KB comprehensive package** with all dependencies
   - **23 automation tools** across 7 categories (including Desktop State Capture)
   - **100+ prompt templates** for conversational AI
   - **Face recognition security** and webcam integration
   - **OCR and visual intelligence** capabilities
   - **Complete desktop UI analysis** with element discovery

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

## 🛠️ **Tool Discovery & Help**

PyWinAuto MCP includes a comprehensive help system to discover and understand all available tools:

#### Get Help Tool
```python
# Get overview of all tools
help_info = get_help()

# Get tools by category
window_tools = get_help(category="windows")

# Get detailed tool information
click_details = get_help(tool_name="click_element")
```

#### Tool Categories
- **System Tools** (4): Health checks, clipboard, timing
- **Window Management** (6): Find, manipulate, and control windows
- **UI Elements** (6): Click, type, inspect, and interact with controls
- **Mouse Control** (7): Precise cursor movement and clicking
- **Keyboard Input** (3): Text input and key combinations
- **Visual Intelligence** (3): Screenshots, OCR, image recognition
- **Face Recognition** (4): Security authentication features
- **Desktop State** (1): Complete UI analysis and discovery

### 📊 **Desktop State Capture**

The `get_desktop_state` tool provides comprehensive UI element discovery with optional visual annotations and OCR text extraction.

**Key Features**:
- **Complete UI Analysis**: Discovers all interactive and informative elements
- **Visual Annotations**: Color-coded element boundaries on screenshots
- **OCR Enhancement**: Extracts text from visual elements
- **Structured Output**: JSON-formatted results for programmatic use

**Usage Examples**:
```python
# Basic UI discovery
state = get_desktop_state()
print(f"Found {state['element_count']} elements")

# With visual annotations
state = get_desktop_state(use_vision=True)
# Includes base64-encoded annotated screenshot

# Complete analysis with OCR
state = get_desktop_state(use_vision=True, use_ocr=True, max_depth=15)
```

📖 **[Complete Desktop State Tool Documentation](docs/desktop-state-tool.md)**

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

### Desktop State

- `POST /api/v1/desktop_state/capture` - Capture complete desktop state with UI elements
  - Optional: `use_vision=true` for annotated screenshots
  - Optional: `use_ocr=true` for text extraction from elements
  - Optional: `max_depth=10` for UI tree traversal depth

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

We welcome contributions! PyWinAuto MCP has comprehensive contribution guidelines and a structured process:

### 📋 **Getting Started**
- 📖 **[Contributing Guide](CONTRIBUTING.md)**: Complete development workflow and guidelines
- 🐛 **[Issue Templates](.github/ISSUE_TEMPLATE/)**: Structured bug reports and feature requests
- 🔄 **CI/CD Pipeline**: Automated testing and quality assurance

### 🛠️ **Development Workflow**
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/your-feature`)
3. **Develop** following our coding standards
4. **Test** your changes thoroughly
5. **Submit** a pull request with detailed description

### 📚 **Documentation**
- 📋 **[Status Report](docs/STATUS_REPORT.md)**: Comprehensive project assessment and roadmap
- 📝 **[API Documentation](docs/)**: Technical documentation and guides
- 🔄 **[Changelog](CHANGELOG.md)**: Version history and release notes

### 🤝 **Community Standards**
- 📜 **[Code of Conduct](CODE_OF_CONDUCT.md)**: Community guidelines and expectations
- 🔒 **[Security Policy](SECURITY.md)**: Vulnerability reporting and security features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PyWinAuto](https://pywinauto.github.io/) for the excellent Windows automation library
- [FastMCP](https://github.com/wandb/fastmcp) for the MCP server framework
