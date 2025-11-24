"""Service for converting files to text."""

import logging
from typing import List
from .base import FileConverter, ConversionResult
from .pdf_converter import PDFConverter
from .docx_converter import DOCXConverter
from .xlsx_converter import XLSXConverter
from .csv_converter import CSVConverter
from .image_converter import ImageConverter
from .video_converter import VideoConverter

logger = logging.getLogger(__name__)


class FileConverterService:
    """Service for converting various file types to text."""
    
    def __init__(self):
        """Initialize converter service with all available converters."""
        self.converters: List[FileConverter] = [
            PDFConverter(),
            DOCXConverter(),
            XLSXConverter(),
            CSVConverter(),
            ImageConverter(),
            VideoConverter(),
        ]
        logger.info(f"📦 FileConverterService initialized with {len(self.converters)} converters")
    
    def find_converter(self, mime_type: str, file_name: str) -> FileConverter:
        """
        Find a converter that can handle the given file.
        
        Args:
            mime_type: MIME type of the file
            file_name: Name of the file
            
        Returns:
            FileConverter instance that can handle the file
            
        Raises:
            ValueError: If no converter is found
        """
        for converter in self.converters:
            if converter.can_convert(mime_type, file_name):
                logger.info(f"✅ Found converter for {file_name}: {converter.__class__.__name__}")
                return converter
        
        raise ValueError(f"No converter available for file type: {mime_type} ({file_name})")
    
    async def convert_to_text(
        self,
        file_content: bytes,
        file_name: str,
        mime_type: str
    ) -> ConversionResult:
        """
        Convert a file to text.
        
        Args:
            file_content: Raw file content as bytes
            file_name: Name of the file
            mime_type: MIME type of the file
            
        Returns:
            ConversionResult with converted text or error
        """
        try:
            converter = self.find_converter(mime_type, file_name)
            result = await converter.convert(file_content, file_name, mime_type)
            return result
        except ValueError as e:
            logger.warning(f"⚠️ {str(e)}")
            return ConversionResult(
                success=False,
                text="",
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Error in FileConverterService: {e}", exc_info=True)
            return ConversionResult(
                success=False,
                text="",
                error=f"Unexpected error: {str(e)}"
            )

