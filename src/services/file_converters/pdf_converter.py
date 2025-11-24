"""PDF to text converter."""

import logging
from typing import Optional
from .base import FileConverter, ConversionResult

logger = logging.getLogger(__name__)


class PDFConverter(FileConverter):
    """Converter for PDF files to text."""
    
    def can_convert(self, mime_type: str, file_name: str) -> bool:
        """Check if file is a PDF."""
        return (
            mime_type == "application/pdf" or
            file_name.lower().endswith(".pdf")
        )
    
    async def convert(self, file_content: bytes, file_name: str, mime_type: str) -> ConversionResult:
        """Convert PDF to text."""
        try:
            # Try pdfplumber first (better for tables and structured content)
            try:
                import pdfplumber
                from io import BytesIO
                
                text_parts = []
                pdf_file = BytesIO(file_content)
                with pdfplumber.open(pdf_file) as pdf:
                    for page_num, page in enumerate(pdf.pages, 1):
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(f"[Page {page_num}]\n{page_text}")
                
                if text_parts:
                    text = "\n\n".join(text_parts)
                    logger.info(f"✅ Converted PDF {file_name} using pdfplumber ({len(text)} chars)")
                    return ConversionResult(
                        success=True,
                        text=text,
                        metadata={"pages": len(text_parts), "converter": "pdfplumber"}
                    )
            except ImportError:
                logger.warning("pdfplumber not available, trying PyPDF2")
            except Exception as e:
                logger.warning(f"pdfplumber failed: {e}, trying PyPDF2")
            
            # Fallback to PyPDF2
            try:
                import PyPDF2
                from io import BytesIO
                
                pdf_file = BytesIO(file_content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                text_parts = []
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"[Page {page_num}]\n{page_text}")
                
                if text_parts:
                    text = "\n\n".join(text_parts)
                    logger.info(f"✅ Converted PDF {file_name} using PyPDF2 ({len(text)} chars)")
                    return ConversionResult(
                        success=True,
                        text=text,
                        metadata={"pages": len(text_parts), "converter": "PyPDF2"}
                    )
                else:
                    return ConversionResult(
                        success=False,
                        text="",
                        error="PDF appears to be empty or image-based (no extractable text)"
                    )
            except ImportError:
                return ConversionResult(
                    success=False,
                    text="",
                    error="No PDF library available. Install pdfplumber or PyPDF2"
                )
            except Exception as e:
                logger.error(f"Error converting PDF {file_name}: {e}", exc_info=True)
                return ConversionResult(
                    success=False,
                    text="",
                    error=f"Error extracting text from PDF: {str(e)}"
                )
                
        except Exception as e:
            logger.error(f"Unexpected error converting PDF {file_name}: {e}", exc_info=True)
            return ConversionResult(
                success=False,
                text="",
                error=f"Unexpected error: {str(e)}"
            )

