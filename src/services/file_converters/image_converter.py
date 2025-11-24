"""Image to text converter using OCR."""

import logging
from io import BytesIO
from .base import FileConverter, ConversionResult

logger = logging.getLogger(__name__)


class ImageConverter(FileConverter):
    """Converter for images to text using OCR."""
    
    def can_convert(self, mime_type: str, file_name: str) -> bool:
        """Check if file is an image."""
        image_types = [
            "image/png",
            "image/jpeg",
            "image/jpg",
            "image/gif",
            "image/bmp",
            "image/tiff",
            "image/webp"
        ]
        return (
            mime_type in image_types or
            any(file_name.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"])
        )
    
    async def convert(self, file_content: bytes, file_name: str, mime_type: str) -> ConversionResult:
        """Convert image to text using OCR."""
        try:
            from PIL import Image
            import pytesseract
            
            # Load image
            image = Image.open(BytesIO(file_content))
            
            # Perform OCR
            # Try Portuguese first, then English
            try:
                text = pytesseract.image_to_string(image, lang='por+eng')
            except Exception as lang_error:
                logger.warning(f"Portuguese+English OCR failed: {lang_error}, trying English only")
                try:
                    # Fallback to English only
                    text = pytesseract.image_to_string(image, lang='eng')
                except Exception as eng_error:
                    logger.warning(f"English OCR failed: {eng_error}, trying without language")
                    # Last resort: no language specified
                    text = pytesseract.image_to_string(image)
            
            if text.strip():
                logger.info(f"✅ Converted image {file_name} using OCR ({len(text)} chars)")
                return ConversionResult(
                    success=True,
                    text=text,
                    metadata={"converter": "pytesseract", "image_size": image.size}
                )
            else:
                return ConversionResult(
                    success=False,
                    text="",
                    error="No text detected in image (image may not contain readable text)"
                )
                
        except ImportError as e:
            missing_lib = "pytesseract" if "pytesseract" in str(e) else "PIL"
            return ConversionResult(
                success=False,
                text="",
                error=f"{missing_lib} library not installed. Install with: pip install pytesseract pillow"
            )
        except Exception as e:
            logger.error(f"Error converting image {file_name}: {e}", exc_info=True)
            # Check if it's a tesseract not found error
            if "tesseract" in str(e).lower() or "TesseractNotFoundError" in str(type(e).__name__):
                return ConversionResult(
                    success=False,
                    text="",
                    error="Tesseract OCR engine not found. Install Tesseract: https://github.com/tesseract-ocr/tesseract"
                )
            return ConversionResult(
                success=False,
                text="",
                error=f"Error performing OCR on image: {str(e)}"
            )

