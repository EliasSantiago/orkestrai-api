"""Video to text converter using speech-to-text."""

import logging
import tempfile
import os
from .base import FileConverter, ConversionResult

logger = logging.getLogger(__name__)


class VideoConverter(FileConverter):
    """Converter for video files (MP4) to text using speech-to-text."""
    
    def can_convert(self, mime_type: str, file_name: str) -> bool:
        """Check if file is a video."""
        video_types = [
            "video/mp4",
            "video/mpeg",
            "video/quicktime",
            "video/x-msvideo",
            "video/webm"
        ]
        return (
            mime_type in video_types or
            any(file_name.lower().endswith(ext) for ext in [".mp4", ".mpeg", ".mov", ".avi", ".webm"])
        )
    
    async def convert(self, file_content: bytes, file_name: str, mime_type: str) -> ConversionResult:
        """Convert video to text using speech-to-text."""
        try:
            import whisper
            
            # Save video to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # Load Whisper model (use base model for speed, can be configured)
                model = whisper.load_model("base")
                
                # Transcribe audio
                result = model.transcribe(temp_file_path, language="pt", task="transcribe")
                
                text = result["text"]
                
                if text.strip():
                    logger.info(f"✅ Converted video {file_name} using Whisper ({len(text)} chars)")
                    return ConversionResult(
                        success=True,
                        text=text,
                        metadata={
                            "converter": "whisper",
                            "language": result.get("language", "unknown"),
                            "segments": len(result.get("segments", []))
                        }
                    )
                else:
                    return ConversionResult(
                        success=False,
                        text="",
                        error="No speech detected in video"
                    )
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                
        except ImportError:
            return ConversionResult(
                success=False,
                text="",
                error="openai-whisper library not installed. Install with: pip install openai-whisper"
            )
        except Exception as e:
            logger.error(f"Error converting video {file_name}: {e}", exc_info=True)
            return ConversionResult(
                success=False,
                text="",
                error=f"Error transcribing video: {str(e)}"
            )

