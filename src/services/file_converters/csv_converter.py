"""CSV to text converter."""

import logging
import csv
from io import BytesIO, TextIOWrapper
from .base import FileConverter, ConversionResult

logger = logging.getLogger(__name__)


class CSVConverter(FileConverter):
    """Converter for CSV files to text."""
    
    def can_convert(self, mime_type: str, file_name: str) -> bool:
        """Check if file is a CSV."""
        return (
            mime_type == "text/csv" or
            mime_type == "application/csv" or
            file_name.lower().endswith(".csv")
        )
    
    async def convert(self, file_content: bytes, file_name: str, mime_type: str) -> ConversionResult:
        """Convert CSV to text."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            text = None
            
            for encoding in encodings:
                try:
                    csv_file = BytesIO(file_content)
                    text_wrapper = TextIOWrapper(csv_file, encoding=encoding)
                    reader = csv.reader(text_wrapper)
                    
                    rows = []
                    for row in reader:
                        rows.append(" | ".join(str(cell) for cell in row))
                    
                    text = "\n".join(rows)
                    text_wrapper.detach()  # Prevent closing BytesIO
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
                except Exception as e:
                    logger.warning(f"Error reading CSV with {encoding}: {e}")
                    continue
            
            if text is None:
                return ConversionResult(
                    success=False,
                    text="",
                    error="Could not decode CSV file with any supported encoding"
                )
            
            if text.strip():
                logger.info(f"✅ Converted CSV {file_name} ({len(text)} chars)")
                return ConversionResult(
                    success=True,
                    text=text,
                    metadata={"converter": "csv"}
                )
            else:
                return ConversionResult(
                    success=False,
                    text="",
                    error="CSV file appears to be empty"
                )
                
        except Exception as e:
            logger.error(f"Error converting CSV {file_name}: {e}", exc_info=True)
            return ConversionResult(
                success=False,
                text="",
                error=f"Error extracting text from CSV: {str(e)}"
            )

