# PyWinAutoMCP DXT Package

This is a DXT (Desktop Extension) package for PyWinAutoMCP, which provides Windows UI
automation capabilities with advanced security features including face recognition.

## Installation

1. Ensure you have Python 3.8+ installed

2. Install the DXT CLI:

   ```bash
   npm install -g @anthropic-ai/dxt
   ```

3. Install the DXT package:

   ```bash
   dxt install pywinauto-mcp-{version}.dxt
   ```

## Usage

### Starting the Server

```bash
dxt run pywinauto-mcp
```

### Available Tools

#### Face Recognition

- `enroll_face`: Enroll a new face for recognition
- `verify_face_webcam`: Verify identity using webcam face recognition

#### Security Monitoring

- `monitor_sensitive_apps`: Monitor and alert on access to sensitive applications
- `security_sweep`: Perform a security sweep of the system
- `detect_intruder`: Detect intruders using webcam motion detection
- `monitor_workstation_activity`: Monitor workstation for unusual activity patterns

## Configuration

Create a `.env` file in the DXT package directory with the following settings:

```ini
# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Face Recognition
FACE_RECOGNITION_TOLERANCE=0.6
FACE_RECOGNITION_MODEL=hog

# Security Settings
SECURITY_ALERT_EMAIL=your-email@example.com
```

## Building from Source

1. Install build dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Build the DXT package:

   ```bash
   python dxt/build_dxt.py
   ```

3. The package will be created in the `dist` directory.

## License

MIT License - See [LICENSE](LICENSE) for details.
