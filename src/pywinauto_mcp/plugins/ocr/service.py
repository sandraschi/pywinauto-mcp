"""
OCR Service for PyWinAutoMCP.

This module provides OCR (Optical Character Recognition) functionality
for extracting text from images and windows.
"""
import os
import sys
from pathlib import Path
import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple, Union, List
from fastapi import UploadFile, HTTPException
from fastmcp.tools import tool as mcp

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from pywinauto_mcp.core.plugin import PyWinAutoPlugin


class OCRService:
    """Service for performing OCR operations."""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """Initialize the OCR service.
        
        Args:
            tesseract_cmd: Path to the Tesseract OCR executable
        """
        self.tesseract_cmd = tesseract_cmd
        self._import_tesseract()
    
    def _import_tesseract(self) -> None:
        """Import Tesseract OCR with proper error handling."""
        try:
            import pytesseract
            
            if self.tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
                
            self.pytesseract = pytesseract
            self._check_tesseract_available()
            
        except ImportError:
            raise ImportError(
                "pytesseract is required for OCR functionality. "
                "Install with: pip install pytesseract"
            )
    
    def _check_tesseract_available(self) -> None:
        """Check if Tesseract OCR is properly installed and accessible."""
        try:
            self.pytesseract.get_tesseract_version()
        except self.pytesseract.TesseractNotFoundError as e:
            raise RuntimeError(
                "Tesseract is not installed or it's not in your PATH. "
                "Please install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki"
            ) from e
    
    def extract_text(
        self,
        image: Union[np.ndarray, str],
        preprocess: bool = True,
        lang: str = "eng",
        config: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract text from an image.
        
        Args:
            image: Input image as numpy array or file path
            preprocess: Whether to preprocess the image for better OCR
            lang: Language code for OCR (e.g., 'eng', 'deu', 'fra')
            config: Additional Tesseract config parameters
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Load image if path is provided
            if isinstance(image, str):
                if not os.path.isfile(image):
                    raise ValueError(f"Image file not found: {image}")
                image = cv2.imread(image)
                if image is None:
                    raise ValueError(f"Could not read image: {image}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing if enabled
            if preprocess:
                gray = self._preprocess_image(gray)
            
            # Configure Tesseract
            tess_config = config or "--oem 3 --psm 6"
            
            # Perform OCR
            data = self.pytesseract.image_to_data(
                gray,
                output_type=self.pytesseract.Output.DICT,
                lang=lang,
                config=tess_config
            )
            
            # Extract text and confidence
            text = self.pytesseract.image_to_string(gray, lang=lang, config=tess_config)
            confidences = [float(x) for x in data['conf'] if float(x) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                "text": text.strip(),
                "confidence": avg_confidence,
                "language": lang,
                "data": data
            }
            
        except Exception as e:
            raise RuntimeError(f"OCR processing failed: {str(e)}")
    
    def extract_text_from_region(
        self,
        image: Union[np.ndarray, str],
        x: int,
        y: int,
        width: int,
        height: int,
        preprocess: bool = True,
        lang: str = "eng",
        config: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract text from a specific region of an image.
        
        Args:
            image: Input image as numpy array or file path
            x: X coordinate of the top-left corner
            y: Y coordinate of the top-left corner
            width: Width of the region
            height: Height of the region
            preprocess: Whether to preprocess the image for better OCR
            lang: Language code for OCR
            config: Additional Tesseract config parameters
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Load image if path is provided
            if isinstance(image, str):
                if not os.path.isfile(image):
                    raise ValueError(f"Image file not found: {image}")
                image = cv2.imread(image)
                if image is None:
                    raise ValueError(f"Could not read image: {image}")
            
            # Extract the region of interest
            h, w = image.shape[:2]
            x1, y1 = max(0, x), max(0, y)
            x2, y2 = min(w, x + width), min(h, y + height)
            
            if x1 >= x2 or y1 >= y2:
                raise ValueError("Invalid region coordinates")
                
            roi = image[y1:y2, x1:x2]
            
            # Extract text from the region
            result = self.extract_text(roi, preprocess, lang, config)
            result["region"] = {"x": x1, "y": y1, "width": x2-x1, "height": y2-y1}
            return result
            
        except Exception as e:
            raise RuntimeError(f"Region-based OCR failed: {str(e)}")
    
    def find_text_position(
        self,
        image: Union[np.ndarray, str],
        search_text: str,
        lang: str = "eng",
        case_sensitive: bool = False,
        config: Optional[str] = None
    ) -> Optional[Tuple[int, int, int, int]]:
        """Find the position of specific text in an image.
        
        Args:
            image: Input image as numpy array or file path
            search_text: Text to search for
            lang: Language code for OCR
            case_sensitive: Whether the search should be case-sensitive
            config: Additional Tesseract config parameters
            
        Returns:
            Tuple of (x, y, width, height) if found, None otherwise
        """
        try:
            # Load image if path is provided
            if isinstance(image, str):
                if not os.path.isfile(image):
                    raise ValueError(f"Image file not found: {image}")
                image = cv2.imread(image)
                if image is None:
                    raise ValueError(f"Could not read image: {image}")
            
            # Get OCR data with character-level bounding boxes
            tess_config = (config or "--oem 3 --psm 6") + " -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            data = self.pytesseract.image_to_data(
                image,
                output_type=self.pytesseract.Output.DICT,
                lang=lang,
                config=tess_config
            )
            
            # Find the text in the OCR results
            search_text = search_text if case_sensitive else search_text.lower()
            
            for i in range(len(data['text'])):
                text = data['text'][i] if case_sensitive else data['text'][i].lower()
                if search_text in text:
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    return (x, y, w, h)
            
            return None
            
        except Exception as e:
            raise RuntimeError(f"Text search failed: {str(e)}")
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image to improve OCR accuracy.
        
        Args:
            image: Input grayscale image
            
        Returns:
            Preprocessed grayscale image
        """
        # Apply adaptive thresholding
        processed = cv2.adaptiveThreshold(
            image, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        
        # Apply dilation and erosion to remove noise
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.dilate(processed, kernel, iterations=1)
        processed = cv2.erode(processed, kernel, iterations=1)
        
        return processed


class OCRPlugin(PyWinAutoPlugin):
    """OCR Plugin for PyWinAutoMCP."""
    
    def __init__(self, app, config: Optional[Dict[str, Any]] = None):
        """Initialize the OCR plugin.
        
        Args:
            app: The FastMCP application instance
            config: Optional configuration dictionary
        """
        super().__init__(app, config)
        self.service = OCRService(
            tesseract_cmd=config.get("tesseract_cmd") if config else None
        )
    
    @classmethod
    def get_name(cls) -> str:
        """Return the plugin's unique name."""
        return "ocr"
    
    def register_tools(self) -> None:
        """Register OCR tools with the MCP server."""
        @mcp.tool("Extract text from an image")
        async def extract_text(
            file: UploadFile,
            preprocess: bool = True,
            lang: str = "eng"
        ) -> Dict[str, Any]:
            """Extract text from an uploaded image.
            
            Args:
                file: The image file to process
                preprocess: Whether to preprocess the image for better OCR
                lang: Language code for OCR (e.g., 'eng', 'deu', 'fra')
                
            Returns:
                Dictionary containing extracted text and metadata
            """
            try:
                contents = await file.read()
                nparr = np.frombuffer(contents, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is None:
                    raise HTTPException(
                        status_code=400,
                        detail="Could not decode the image file"
                    )
                
                result = self.service.extract_text(
                    image=image,
                    preprocess=preprocess,
                    lang=lang,
                    config=self.config.get("tesseract_config")
                )
                
                return {
                    "success": True,
                    "text": result["text"],
                    "confidence": result["confidence"],
                    "language": lang
                }
                
            except Exception as e:
                self._logger.error(f"OCR extraction failed: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"OCR processing failed: {str(e)}"
                )
        
        @mcp.tool("Extract text from a region of an image")
        async def extract_region(
            file: UploadFile,
            x: int,
            y: int,
            width: int,
            height: int,
            preprocess: bool = True,
            lang: str = "eng"
        ) -> Dict[str, Any]:
            """Extract text from a specific region of an image.
            
            Args:
                file: The image file to process
                x: X coordinate of the top-left corner
                y: Y coordinate of the top-left corner
                width: Width of the region
                height: Height of the region
                preprocess: Whether to preprocess the image for better OCR
                lang: Language code for OCR (e.g., 'eng', 'deu', 'fra')
                
            Returns:
                Dictionary containing extracted text and region info
            """
            try:
                contents = await file.read()
                nparr = np.frombuffer(contents, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is None:
                    raise HTTPException(
                        status_code=400,
                        detail="Could not decode the image file"
                    )
                
                result = self.service.extract_text_from_region(
                    image=image,
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    preprocess=preprocess,
                    lang=lang,
                    config=self.config.get("tesseract_config")
                )
                
                return {
                    "success": True,
                    "text": result["text"],
                    "confidence": result["confidence"],
                    "language": lang,
                    "region": result["region"]
                }
                
            except Exception as e:
                self._logger.error(f"Region-based OCR failed: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Region-based OCR failed: {str(e)}"
                )
        
        @mcp.tool("Find text position in an image")
        async def find_text(
            file: UploadFile,
            search_text: str,
            lang: str = "eng",
            case_sensitive: bool = False
        ) -> Dict[str, Any]:
            """Find the position of specific text in an image.
            
            Args:
                file: The image file to search in
                search_text: The text to search for
                lang: Language code for OCR (e.g., 'eng', 'deu', 'fra')
                case_sensitive: Whether the search should be case-sensitive
                
            Returns:
                Dictionary with position information if found
            """
            try:
                if not search_text.strip():
                    raise HTTPException(
                        status_code=400,
                        detail="Search text cannot be empty"
                    )
                
                contents = await file.read()
                nparr = np.frombuffer(contents, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is None:
                    raise HTTPException(
                        status_code=400,
                        detail="Could not decode the image file"
                    )
                
                position = self.service.find_text_position(
                    image=image,
                    search_text=search_text,
                    lang=lang,
                    case_sensitive=case_sensitive,
                    config=self.config.get("tesseract_config")
                )
                
                if position:
                    x, y, w, h = position
                    return {
                        "success": True,
                        "found": True,
                        "search_text": search_text,
                        "position": {
                            "x": x,
                            "y": y,
                            "width": w,
                            "height": h
                        }
                    }
                else:
                    return {
                        "success": True,
                        "found": False,
                        "search_text": search_text,
                        "message": "Text not found in the image"
                    }
                    
            except Exception as e:
                self._logger.error(f"Text search failed: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Text search failed: {str(e)}"
                )
