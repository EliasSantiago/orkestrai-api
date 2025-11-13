"""
File Search File Manager.

Manages file uploads and imports to File Search Stores.
"""

import logging
import time
import mimetypes
from typing import Dict, Any, Optional, BinaryIO, List
from google import genai
from src.config import Config

logger = logging.getLogger(__name__)

# Maximum file size: 100 MB (as per Google documentation)
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB

# Supported file types by Google Gemini File Search
# Based on: https://ai.google.dev/gemini-api/docs/file-search
SUPPORTED_MIME_TYPES = {
    # Documents
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # .pptx
    'application/rtf',
    'text/plain',
    'text/markdown',
    'text/html',
    'text/csv',
    # Images
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/webp',
    'image/heif',
    # Audio
    'audio/mpeg',
    'audio/mp3',
    'audio/mp4',
    'audio/m4a',
    'audio/wav',
    # Video
    'video/mp4',
    'video/mpeg',
    'video/quicktime',
    'video/x-msvideo',
    'video/x-flv',
    'video/webm',
    'video/x-ms-wmv',
    'video/3gpp',
    # Code files
    'text/x-python',
    'text/x-java',
    'text/x-c',
    'text/x-c++',
    'text/x-php',
    'text/x-sql',
    'text/javascript',
    'text/css',
    # Other
    'application/json',
    'application/xml',
    'text/xml',
}


class FileSearchFileManager:
    """Manages files in File Search Stores."""
    
    def __init__(self):
        """Initialize the File Search File Manager."""
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not configured in environment")
        
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        logger.debug(f"Initialized FileSearchFileManager with API key (length: {len(Config.GOOGLE_API_KEY) if Config.GOOGLE_API_KEY else 0})")
    
    def validate_file_size(self, file_size: int) -> bool:
        """
        Validate that file size is within limits.
        
        Args:
            file_size: File size in bytes
            
        Returns:
            True if file size is valid (<= 100 MB)
        """
        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed size "
                f"({MAX_FILE_SIZE_BYTES / (1024 * 1024)} MB)"
            )
        return True
    
    def detect_mime_type(self, file_name: str, content_type: Optional[str] = None) -> str:
        """
        Detect MIME type from file name or content type.
        
        Args:
            file_name: File name with extension
            content_type: Optional content type from request
            
        Returns:
            MIME type string
            
        Raises:
            ValueError: If MIME type cannot be determined or is not supported
        """
        # First, try to use provided content_type
        # Accept any provided content_type - let Google API validate it
        if content_type:
            # Normalize content_type
            content_type = content_type.strip()
            
            # Handle common aliases
            content_type_aliases = {
                'image/jpg': 'image/jpeg',
                'application/x-pdf': 'application/pdf',
            }
            content_type = content_type_aliases.get(content_type.lower(), content_type)
            
            # Use provided content_type - don't validate against our list
            # Google API will validate the format
            logger.debug(f"Using provided content_type: {content_type}")
            return content_type
        
        # Clean file name (remove query parameters, etc.)
        clean_file_name = file_name.split('?')[0].split(';')[0].strip()
        
        # Try to detect from file extension
        mime_type, _ = mimetypes.guess_type(clean_file_name)
        
        if mime_type:
            # Normalize some common variations
            mime_type_lower = mime_type.lower()
            
            # Handle common aliases
            mime_type_aliases = {
                'image/jpg': 'image/jpeg',
                'application/x-pdf': 'application/pdf',
            }
            # Use alias if available, otherwise use original (preserve case)
            mime_type = mime_type_aliases.get(mime_type_lower, mime_type)
            
            # Return detected MIME type - don't validate against our list
            # Google API will validate the format
            logger.debug(f"Detected MIME type from extension '{clean_file_name}': {mime_type}")
            return mime_type
        
        # Manual fallback for common extensions if mimetypes fails
        extension = clean_file_name.lower().split('.')[-1] if '.' in clean_file_name else ''
        extension_mime_map = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'txt': 'text/plain',
            'md': 'text/markdown',
            'html': 'text/html',
            'csv': 'text/csv',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'webp': 'image/webp',
            'mp3': 'audio/mpeg',
            'mp4': 'video/mp4',
            'wav': 'audio/wav',
            'py': 'text/x-python',
            'java': 'text/x-java',
            'c': 'text/x-c',
            'cpp': 'text/x-c++',
            'php': 'text/x-php',
            'sql': 'text/x-sql',
            'js': 'text/javascript',
            'css': 'text/css',
            'json': 'application/json',
            'xml': 'application/xml',
        }
        
        if extension in extension_mime_map:
            mime_type = extension_mime_map[extension]
            logger.debug(f"Detected MIME type from extension fallback '{extension}': {mime_type}")
            return mime_type
        
        # If we still don't have a valid MIME type, raise error
        raise ValueError(
            f"Could not determine MIME type for file '{file_name}'. "
            f"Please ensure the file has a valid extension or provide the content_type. "
            f"Supported types: PDF, DOC, DOCX, TXT, MD, HTML, CSV, XLS, XLSX, PPTX, "
            f"PNG, JPG, JPEG, WEBP, MP3, MP4, WAV, and code files."
        )
    
    def validate_mime_type(self, mime_type: str) -> bool:
        """
        Validate that MIME type is supported.
        
        Args:
            mime_type: MIME type to validate
            
        Returns:
            True if MIME type is supported
            
        Raises:
            ValueError: If MIME type is not supported
        """
        if mime_type not in SUPPORTED_MIME_TYPES:
            raise ValueError(
                f"MIME type '{mime_type}' is not supported. "
                f"Supported types include: PDF, DOC, DOCX, TXT, MD, HTML, CSV, XLS, XLSX, PPTX, "
                f"PNG, JPG, JPEG, WEBP, MP3, MP4, WAV, and code files."
            )
        return True
    
    async def upload_and_import(
        self,
        file_content: BinaryIO,
        file_name: str,
        store_name: str,
        display_name: Optional[str] = None,
        mime_type: Optional[str] = None,
        chunking_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload a file directly to a File Search Store and import it.
        
        This is the recommended approach as it uploads and imports in one step.
        
        Args:
            file_content: File content (file-like object)
            file_name: Original file name
            store_name: Full Google store name (projects/.../fileSearchStores/...)
            display_name: Optional display name for the file
            mime_type: Optional MIME type (will be detected from file_name if not provided)
            chunking_config: Optional chunking configuration
            
        Returns:
            Dictionary with file information:
            - name: Full Google file name (projects/.../files/...)
            - display_name: Display name
            - size_bytes: File size in bytes
        """
        try:
            # Read file content to get size
            file_content.seek(0, 2)  # Seek to end
            file_size = file_content.tell()
            file_content.seek(0)  # Reset to beginning
            
            # Validate file size
            self.validate_file_size(file_size)
            
            # Detect MIME type if not provided
            detected_mime_type = None
            if not mime_type:
                try:
                    detected_mime_type = self.detect_mime_type(file_name)
                except ValueError as e:
                    # If detection fails, try to extract from filename anyway
                    logger.warning(f"Could not detect MIME type: {e}. Trying fallback...")
                    extension = file_name.lower().split('.')[-1] if '.' in file_name else ''
                    if extension:
                        # Try common extensions
                        fallback_map = {
                            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                            'doc': 'application/msword',
                            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            'xls': 'application/vnd.ms-excel',
                            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                            'pdf': 'application/pdf',
                            'txt': 'text/plain',
                        }
                        detected_mime_type = fallback_map.get(extension)
                        if detected_mime_type:
                            logger.info(f"Using fallback MIME type '{detected_mime_type}' for extension '{extension}'")
                    else:
                        raise ValueError(
                            "Could not determine MIME type for file. "
                            "Please ensure the file has a valid extension or provide the content_type."
                        )
            else:
                detected_mime_type = mime_type
            
            logger.info(f"Uploading file '{file_name}' ({file_size} bytes, detected type: {detected_mime_type}) to store {store_name}")
            
            # Google API requires mime_type to be provided
            # However, it may reject complex Office MIME types with strict validation
            # We'll use simplified MIME types for Office documents that Google API accepts
            if not detected_mime_type:
                raise ValueError(
                    "Could not determine MIME type for file. "
                    "Please ensure the file has a valid extension or provide the content_type."
                )
            
            # Map complex Office MIME types to simpler alternatives that Google API accepts
            # Based on documentation and testing, Google API may accept simpler formats
            mime_type_mapping = {
                # Office OpenXML formats - use simpler alternatives
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'application/msword',  # .docx -> .doc format
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'application/vnd.ms-excel',  # .xlsx -> .xls format
                'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'application/vnd.ms-powerpoint',  # .pptx -> .ppt format
            }
            
            # Use mapped MIME type if available, otherwise use detected
            final_mime_type = mime_type_mapping.get(detected_mime_type, detected_mime_type)
            
            # Validate MIME type format (must be type/subtype)
            if '/' not in final_mime_type or final_mime_type.count('/') != 1:
                raise ValueError(
                    f"Invalid MIME type format: '{final_mime_type}'. "
                    "MIME type must be in format 'type/subtype' (e.g., 'application/pdf')"
                )
            
            # Prepare config - try without mime_type first for Office documents
            # Google API may auto-detect from file content
            # If that fails, we'll try with mime_type
            config = {
                'display_name': display_name or file_name,
            }
            
            # For Office documents, don't pass mime_type - let Google auto-detect
            # For other files, pass mime_type explicitly
            office_extensions = {'.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt'}
            video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.mpeg', '.mpg'}
            audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac'}
            
            file_extension = file_name.lower()
            is_office_file = any(file_extension.endswith(ext) for ext in office_extensions)
            is_video_file = any(file_extension.endswith(ext) for ext in video_extensions)
            is_audio_file = any(file_extension.endswith(ext) for ext in audio_extensions)
            
            # Warn about potentially unsupported file types
            if is_video_file:
                logger.warning(
                    f"Uploading video file '{file_name}'. "
                    f"Note: Google Gemini File Search may not support video files. "
                    f"If upload fails with 500 error, video files may not be supported."
                )
            elif is_audio_file:
                logger.warning(
                    f"Uploading audio file '{file_name}'. "
                    f"Note: Google Gemini File Search may have limited support for audio files."
                )
            
            if not is_office_file:
                # For non-Office files, pass mime_type explicitly
                config['mime_type'] = final_mime_type
                logger.debug(f"Passing MIME type for non-Office file: {final_mime_type}")
            else:
                # For Office files, don't pass mime_type - let Google auto-detect
                logger.info(
                    f"Not passing MIME type for Office file '{file_name}' - "
                    f"Google API will auto-detect from file content"
                )
            
            if chunking_config:
                config['chunking_config'] = chunking_config
            
            # Upload and import directly to file search store
            logger.info(f"Calling upload_to_file_search_store with store_name='{store_name}', config keys: {list(config.keys())}")
            logger.debug(f"Config content: {config}")
            logger.debug(f"File type: {type(file_content)}, file size: {file_size} bytes")
            
            # Ensure file_content is at the beginning
            file_content.seek(0)
            
            # Google API may return store names in short format (fileSearchStores/...)
            # or full format (projects/.../fileSearchStores/...)
            # Both formats should work, but let's log which one we're using
            if store_name.startswith('projects/'):
                logger.debug(f"Using full store_name format: {store_name}")
            elif store_name.startswith('fileSearchStores/'):
                logger.debug(f"Using short store_name format: {store_name}")
                # The API should accept the short format, but if it doesn't work,
                # we may need to construct the full format
                # For now, try with the short format as-is
            else:
                logger.warning(f"Unexpected store_name format: {store_name}")
            
            try:
                # Try to upload
                # Google API SDK should handle BytesIO objects directly
                logger.debug(f"Attempting upload with file type: {type(file_content)}")
                operation = self.client.file_search_stores.upload_to_file_search_store(
                    file=file_content,
                    file_search_store_name=store_name,
                    config=config
                )
                logger.info("Upload request sent successfully, waiting for operation to complete...")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Upload failed: {error_msg}")
                
                # Check for specific error types
                if '500' in error_msg or 'INTERNAL' in error_msg:
                    # 500 errors can be caused by:
                    # 1. File too large (even if under 100MB, Google may have stricter limits for videos)
                    # 2. Unsupported file type
                    # 3. Corrupted file
                    # 4. Server-side issue
                    raise RuntimeError(
                        f"Google API returned internal server error (500). "
                        f"This may be caused by: "
                        f"1. File size too large (videos may have stricter limits), "
                        f"2. Unsupported file type for File Search, "
                        f"3. Corrupted file, or "
                        f"4. Temporary server issue. "
                        f"File: '{file_name}' ({file_size} bytes), MIME type: '{final_mime_type}'. "
                        f"Original error: {error_msg}"
                    )
                elif 'mime_type' in error_msg.lower() or 'mime type' in error_msg.lower():
                    raise ValueError(
                        f"Upload failed due to MIME type issue. "
                        f"Detected MIME type: '{detected_mime_type}', "
                        f"Mapped to: '{final_mime_type}'. "
                        f"Error from Google API: {error_msg}. "
                        f"Please check Google Gemini File Search documentation for supported MIME types."
                    )
                else:
                    # Re-raise other errors as-is
                    raise
            
            # Wait for import to complete
            # According to Google documentation: https://ai.google.dev/gemini-api/docs/file-search
            # We should pass the operation object directly to operations.get()
            logger.info(f"Waiting for file import to complete...")
            logger.debug(f"Operation type: {type(operation)}, has 'done': {hasattr(operation, 'done')}")
            
            # Poll operation until complete
            # Following Google's documentation pattern:
            # while not operation.done:
            #     time.sleep(5)
            #     operation = client.operations.get(operation)
            max_attempts = 120  # Maximum 10 minutes (120 * 5 seconds) for large files
            attempt = 0
            
            while attempt < max_attempts:
                # Check if operation is done
                if hasattr(operation, 'done') and operation.done:
                    logger.info(f"Operation completed after {attempt * 5} seconds")
                    break
                
                # Wait before checking again (5 seconds as per Google docs)
                time.sleep(5)
                attempt += 1
                
                # Refresh operation status
                # According to docs, pass operation object directly, not operation.name
                try:
                    operation = self.client.operations.get(operation)
                    logger.debug(f"Operation status check {attempt}/{max_attempts}, done: {getattr(operation, 'done', False)}")
                except Exception as e:
                    logger.warning(f"Error checking operation status (attempt {attempt}): {e}")
                    # Continue trying - might be a transient error
                    continue
            
            # Final check
            if attempt >= max_attempts:
                raise RuntimeError(
                    f"Operation timed out after {max_attempts * 5} seconds ({max_attempts * 5 / 60:.1f} minutes). "
                    f"Large files may take longer to process. Please try again or use a smaller file."
                )
            
            # Verify operation completed successfully
            if not hasattr(operation, 'done') or not operation.done:
                raise RuntimeError("Operation did not complete successfully")
            
            # Check for errors
            if hasattr(operation, 'error') and operation.error:
                error_msg = str(operation.error)
                logger.error(f"File import failed: {error_msg}")
                raise RuntimeError(f"File import failed: {error_msg}")
            
            # Get file information from operation result
            # Handle different response structures
            file_name_from_response = None
            
            # Debug: Log operation structure
            logger.debug(f"Operation type: {type(operation)}")
            logger.debug(f"Operation attributes: {dir(operation)}")
            
            # Based on log: Operation type is UploadToFileSearchStoreOperation
            # Has response: True, Has metadata: True, Has file: False
            # Try to access response and metadata directly
            if hasattr(operation, 'response'):
                response = operation.response
                logger.debug(f"Operation.response type: {type(response)}")
                logger.debug(f"Operation.response: {response}")
                
                # Try to get file name from response
                # Response might be a protobuf message or dict-like object
                try:
                    # Try accessing as object attributes
                    if hasattr(response, 'file'):
                        file_obj = response.file
                        if hasattr(file_obj, 'name'):
                            file_name_from_response = file_obj.name
                            logger.info(f"✅ Got file name from response.file.name: {file_name_from_response}")
                        elif isinstance(file_obj, str):
                            file_name_from_response = file_obj
                            logger.info(f"✅ Got file name from response.file (string): {file_name_from_response}")
                    # Try accessing as dict
                    elif isinstance(response, dict):
                        file_obj = response.get('file', {})
                        if isinstance(file_obj, dict):
                            file_name_from_response = file_obj.get('name')
                            logger.info(f"✅ Got file name from response['file']['name']: {file_name_from_response}")
                        elif isinstance(file_obj, str):
                            file_name_from_response = file_obj
                            logger.info(f"✅ Got file name from response['file'] (string): {file_name_from_response}")
                    # Try direct name attribute
                    elif hasattr(response, 'name'):
                        file_name_from_response = response.name
                        logger.info(f"✅ Got file name from response.name: {file_name_from_response}")
                except Exception as e:
                    logger.debug(f"Error accessing response attributes: {e}")
            
            # Try metadata (based on log: Has metadata: True)
            if not file_name_from_response and hasattr(operation, 'metadata'):
                metadata = operation.metadata
                logger.debug(f"Operation.metadata type: {type(metadata)}")
                logger.debug(f"Operation.metadata: {metadata}")
                
                try:
                    # Try accessing metadata as object
                    if hasattr(metadata, 'file'):
                        file_obj = metadata.file
                        if hasattr(file_obj, 'name'):
                            file_name_from_response = file_obj.name
                            logger.info(f"✅ Got file name from metadata.file.name: {file_name_from_response}")
                        elif isinstance(file_obj, str):
                            file_name_from_response = file_obj
                            logger.info(f"✅ Got file name from metadata.file (string): {file_name_from_response}")
                    # Try as dict
                    elif isinstance(metadata, dict):
                        file_name_from_response = metadata.get('file') or metadata.get('file_name') or metadata.get('file_name_path')
                        if file_name_from_response:
                            logger.info(f"✅ Got file name from metadata dict: {file_name_from_response}")
                except Exception as e:
                    logger.debug(f"Error accessing metadata attributes: {e}")
            
            # Try to get from operation directly (fallback)
            if not file_name_from_response and hasattr(operation, 'file'):
                file_obj = operation.file
                if hasattr(file_obj, 'name'):
                    file_name_from_response = file_obj.name
                    logger.info(f"✅ Got file name from operation.file.name: {file_name_from_response}")
                elif isinstance(file_obj, dict):
                    file_name_from_response = file_obj.get('name')
                    logger.info(f"✅ Got file name from operation.file['name']: {file_name_from_response}")
            
            # Try to get from operation.name if it's a file name (not operation name)
            if not file_name_from_response and hasattr(operation, 'name'):
                op_name = operation.name
                # Check if it looks like a file name (contains 'files/')
                if isinstance(op_name, str) and 'files/' in op_name:
                    file_name_from_response = op_name
                    logger.info(f"✅ Got file name from operation.name (looks like file path): {file_name_from_response}")
            
            # Build file info
            file_info = {
                'name': file_name_from_response or '',
                'display_name': display_name or file_name,
                'size_bytes': file_size
            }
            
            # Log warning if we couldn't extract the file name
            if not file_info['name']:
                logger.warning(
                    f"Could not extract file name from operation response. "
                    f"Operation type: {type(operation)}, "
                    f"Has response: {hasattr(operation, 'response')}, "
                    f"Has metadata: {hasattr(operation, 'metadata')}, "
                    f"Has file: {hasattr(operation, 'file')}, "
                    f"Operation name: {getattr(operation, 'name', 'N/A')}"
                )
                # Try to inspect the operation object more deeply
                try:
                    import json
                    operation_dict = {}
                    for attr in dir(operation):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(operation, attr)
                                if not callable(value):
                                    operation_dict[attr] = str(value)[:100]  # Limit length
                            except:
                                pass
                    logger.debug(f"Operation object summary: {json.dumps(operation_dict, indent=2)}")
                except Exception as e:
                    logger.debug(f"Could not serialize operation object: {e}")
                
                # Fallback: Try to find the file by listing files in the store
                # This is a workaround if the operation response doesn't contain the file name
                try:
                    logger.info(f"Attempting to find file by listing files in store {store_name}")
                    # List files in the store to find the newly uploaded file
                    # We'll look for files with matching display_name or recent upload
                    files_in_store = self._list_files_in_store_fallback(store_name)
                    if files_in_store:
                        # Try to find by display_name or get the most recent file
                        matching_file = None
                        for file_item in files_in_store:
                            file_display_name = file_item.get('display_name') or file_item.get('name', '')
                            if file_display_name == (display_name or file_name):
                                matching_file = file_item
                                break
                        
                        # If no match by name, get the most recent file (likely the one we just uploaded)
                        if not matching_file and files_in_store:
                            matching_file = files_in_store[-1]  # Most recent
                        
                        if matching_file:
                            file_name_from_response = matching_file.get('name') or matching_file.get('file_name')
                            if file_name_from_response:
                                file_info['name'] = file_name_from_response
                                logger.info(f"Found file name via fallback method: {file_name_from_response}")
                except Exception as e:
                    logger.warning(f"Fallback method to find file name failed: {e}")
                    # This is not fatal - the file was uploaded successfully
                    # We just don't have the Google file name to store
            
            logger.info(f"Successfully uploaded and imported file: {file_info.get('name', 'unknown')}")
            return file_info
            
        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error uploading file to file search store: {e}")
            raise RuntimeError(f"Failed to upload file: {str(e)}")
    
    async def upload_file_separately(
        self,
        file_content: BinaryIO,
        file_name: str,
        display_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file using the Files API (separate from import).
        
        Use this if you want to upload first, then import later.
        
        Args:
            file_content: File content (file-like object)
            file_name: Original file name
            display_name: Optional display name for the file
            
        Returns:
            Dictionary with file information:
            - name: Full Google file name (projects/.../files/...)
            - display_name: Display name
            - size_bytes: File size in bytes
        """
        try:
            # Read file content to get size
            file_content.seek(0, 2)  # Seek to end
            file_size = file_content.tell()
            file_content.seek(0)  # Reset to beginning
            
            # Validate file size
            self.validate_file_size(file_size)
            
            logger.info(f"Uploading file '{file_name}' ({file_size} bytes)")
            
            # Upload file using Files API
            uploaded_file = self.client.files.upload(
                file=file_content,
                config={'name': display_name or file_name}
            )
            
            logger.info(f"Successfully uploaded file: {uploaded_file.name}")
            return {
                'name': uploaded_file.name,
                'display_name': display_name or file_name,
                'size_bytes': file_size
            }
            
        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise RuntimeError(f"Failed to upload file: {str(e)}")
    
    async def import_file(
        self,
        file_name: str,
        store_name: str,
        chunking_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Import an already uploaded file into a File Search Store.
        
        Args:
            file_name: Full Google file name (projects/.../files/...)
            store_name: Full Google store name (projects/.../fileSearchStores/...)
            chunking_config: Optional chunking configuration
            
        Returns:
            Dictionary with operation information
        """
        try:
            logger.info(f"Importing file {file_name} into store {store_name}")
            
            config = {}
            if chunking_config:
                config['chunking_config'] = chunking_config
            
            # Import file into file search store
            operation = self.client.file_search_stores.import_file(
                file_search_store_name=store_name,
                file_name=file_name,
                config=config if config else None
            )
            
            # Wait for import to complete
            # Following Google's documentation pattern
            logger.info(f"Waiting for file import to complete...")
            max_attempts = 120  # Maximum 10 minutes (120 * 5 seconds) for large files
            attempt = 0
            
            while attempt < max_attempts:
                # Check if operation is done
                if hasattr(operation, 'done') and operation.done:
                    logger.info(f"Import operation completed after {attempt * 5} seconds")
                    break
                
                # Wait before checking again (5 seconds as per Google docs)
                time.sleep(5)
                attempt += 1
                
                # Refresh operation status
                # According to docs, pass operation object directly, not operation.name
                try:
                    operation = self.client.operations.get(operation)
                    logger.debug(f"Import operation status check {attempt}/{max_attempts}, done: {getattr(operation, 'done', False)}")
                except Exception as e:
                    logger.warning(f"Error checking import operation status (attempt {attempt}): {e}")
                    # Continue trying - might be a transient error
                    continue
            
            # Final check
            if attempt >= max_attempts:
                raise RuntimeError(
                    f"Import operation timed out after {max_attempts * 5} seconds ({max_attempts * 5 / 60:.1f} minutes). "
                    f"Large files may take longer to process. Please try again or use a smaller file."
                )
            
            # Verify operation completed successfully
            if not hasattr(operation, 'done') or not operation.done:
                raise RuntimeError("Import operation did not complete successfully")
            
            if hasattr(operation, 'error') and operation.error:
                error_msg = str(operation.error)
                logger.error(f"File import failed: {error_msg}")
                raise RuntimeError(f"File import failed: {error_msg}")
            
            logger.info(f"Successfully imported file: {file_name}")
            return {
                'operation_name': operation.name,
                'done': operation.done
            }
            
        except Exception as e:
            logger.error(f"Error importing file: {e}")
            raise RuntimeError(f"Failed to import file: {str(e)}")
    
    def _list_files_in_store_fallback(self, store_name: str) -> List[Dict[str, Any]]:
        """
        Fallback method to list files in a store.
        Used when we can't extract file name from operation response.
        
        Note: This is a workaround. The Google API might not provide
        a direct way to list files in a File Search Store.
        
        Args:
            store_name: Full Google store name
            
        Returns:
            List of file dictionaries with 'name' and 'display_name'
        """
        try:
            # The Google File Search API might not support listing files directly
            # This is a placeholder for future implementation
            # For now, return empty list - the file was uploaded successfully
            # even if we can't get its name from the operation response
            logger.debug("File listing fallback not fully implemented - Google API limitation")
            return []
        except Exception as e:
            logger.warning(f"Fallback file listing failed: {e}")
            return []
    
    def get_file(self, file_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a file.
        
        Args:
            file_name: Full Google file name (projects/.../files/...)
            
        Returns:
            Dictionary with file information or None if not found
        """
        try:
            file = self.client.files.get(file_name)
            return {
                'name': file.name,
                'display_name': getattr(file, 'display_name', None),
                'mime_type': getattr(file, 'mime_type', None)
            }
        except Exception as e:
            logger.error(f"Error getting file {file_name}: {e}")
            return None
    
    def delete_file(self, file_name: str) -> bool:
        """
        Delete a file.
        
        Args:
            file_name: Full Google file name (projects/.../files/...)
            
        Returns:
            True if deleted successfully
        """
        try:
            logger.info(f"Deleting file: {file_name}")
            self.client.files.delete(file_name)
            logger.info(f"Successfully deleted file: {file_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file {file_name}: {e}")
            raise RuntimeError(f"Failed to delete file: {str(e)}")

