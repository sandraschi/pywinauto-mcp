# 📋 Changelog

All notable changes to PyWinAuto MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive DXT manifest with 22+ automation tools
- Extensive prompt templates for conversational AI interaction
- GitHub Actions CI/CD pipeline with automated testing
- Issue and pull request templates for better contributions
- Contributing guidelines and development documentation

### Changed
- Reorganized repository structure with dedicated `dxt/` directory
- Updated pywin32 dependency to version 311
- Enhanced package metadata and descriptions

## [0.2.0] - 2025-01-23

### Added
- **Complete DXT Package**: Comprehensive Windows UI automation with face recognition
- **22 Automation Tools**: Window management, element interaction, OCR, mouse/keyboard control
- **Dual Interface Architecture**: MCP tools + REST API with feature parity
- **Face Recognition Security**: Webcam authentication and intruder detection
- **OCR Integration**: Text extraction from windows and images
- **Advanced Element Interaction**: Click, type, hover, and drag operations

### Changed
- Major architecture overhaul with modular plugin system
- Enhanced error handling and retry mechanisms
- Improved configuration management

## [0.1.0] - 2025-07-30

### Added
- Initial PyWinAuto MCP server implementation
- Basic window management tools
- Face recognition API endpoints
- Security monitoring features
- DXT packaging support

### Changed
- Initial release with core automation functionality

---

## 📊 Version Information

- **Current Version**: 0.2.0
- **Python Support**: 3.10, 3.11, 3.12
- **Platform**: Windows 10/11
- **License**: MIT

## 🔄 Release Process

Releases are automated through GitHub Actions:
1. Push to `master` branch triggers CI
2. Tests run on Windows with multiple Python versions
3. DXT package is built and uploaded as artifact
4. Release creation triggers final package distribution

## 🤝 Contributing to Changelog

When contributing to this project, please:
- Add entries to the "Unreleased" section above
- Use present tense for changes ("Add feature" not "Added feature")
- Group changes under appropriate headings (Added, Changed, Fixed, etc.)
- Reference issue numbers when applicable

---

*For more detailed information about each release, see the [GitHub Releases](https://github.com/yourusername/pywinauto-mcp/releases) page.*
