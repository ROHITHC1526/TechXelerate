"""
QR Code Scanner Service for Attendance Verification

Handles:
- Image file validation and reading
- QR code detection and decoding using multiple methods
- QR data extraction and parsing
- Proper error handling and logging
"""

import logging
import json
try:
    import numpy as np
    _HAS_NUMPY = True
except Exception:
    np = None
    _HAS_NUMPY = False
try:
    import cv2
    _HAS_CV2 = True
except Exception:
    cv2 = None
    _HAS_CV2 = False
from io import BytesIO
from typing import Dict, Optional, Tuple
from PIL import Image
try:
    import pyzbar.pyzbar as pyzbar
    _HAS_PYZBAR = True
except Exception:
    pyzbar = None
    _HAS_PYZBAR = False

logger = logging.getLogger(__name__)

# Max file size: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# Supported image formats
ALLOWED_FORMATS = {'jpeg', 'jpg', 'png', 'bmp', 'gif'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/bmp', 'image/gif'}


class QRScannerError(Exception):
    """Base exception for QR scanner errors."""
    pass


class InvalidImageError(QRScannerError):
    """Raised when image cannot be read or is invalid."""
    pass


class QRNotDetectedError(QRScannerError):
    """Raised when no QR code is detected in the image."""
    pass


class InvalidQRDataError(QRScannerError):
    """Raised when QR data is invalid or cannot be parsed."""
    pass


class QRScanner:
    """
    Professional QR code scanner for attendance verification.
    
    Supports multiple QR detection methods:
    1. pyzbar (primary, most reliable)
    2. OpenCV QRCodeDetector (fallback)
    3. Image preprocessing for difficult conditions
    """
    
    def __init__(self):
        """Initialize QR scanner."""
        logger.debug("✓ QRScanner initialized")
    
    @staticmethod
    def validate_file(file_content: bytes, file_name: str, content_type: str) -> bool:
        """
        Validate uploaded file.
        
        Args:
            file_content: Raw file bytes
            file_name: Original filename
            content_type: MIME type
            
        Returns:
            True if valid
            
        Raises:
            InvalidImageError: If file is invalid
        """
        # Check file size
        if len(file_content) > MAX_FILE_SIZE:
            raise InvalidImageError(
                f"File too large: {len(file_content) / 1024 / 1024:.2f}MB (max 5MB)"
            )
        
        # Check file extension
        file_ext = file_name.split('.')[-1].lower()
        if file_ext not in ALLOWED_FORMATS:
            raise InvalidImageError(
                f"Invalid file format: .{file_ext} (allowed: {', '.join(ALLOWED_FORMATS)})"
            )
        
        # Check MIME type
        if content_type not in ALLOWED_MIME_TYPES:
            raise InvalidImageError(
                f"Invalid MIME type: {content_type} (allowed: {', '.join(ALLOWED_MIME_TYPES)})"
            )
        
        logger.debug(f"✓ File validation passed: {file_name}")
        return True
    
    @staticmethod
    def read_image_from_bytes(file_content: bytes) -> Tuple[Optional['np.ndarray'], 'Image.Image']:
        """
        Read image from raw bytes using multiple methods.
        
        Args:
            file_content: Raw image bytes
            
        Returns:
            Tuple of (cv2_image numpy array, PIL Image)
            
        Raises:
            InvalidImageError: If image cannot be read
        """
        try:
            # Method 1: Read with PIL first (validation)
            pil_image = Image.open(BytesIO(file_content))
            logger.debug(f"✓ PIL Image opened: {pil_image.format} {pil_image.size}")
            
            # If numpy not available, return PIL image only
            if not _HAS_NUMPY:
                logger.warning("⚠️  numpy not available - returning PIL image only")
                return None, pil_image

            # Convert PIL to numpy array
            image_array = np.array(pil_image)

            # If OpenCV available, convert RGB->BGR for cv2 processing
            if _HAS_CV2 and len(image_array.shape) == 3 and image_array.shape[2] == 3:
                try:
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                except Exception:
                    # Fall back to raw array
                    pass

            logger.debug(f"✓ Image converted to numpy array: shape={image_array.shape}")

            return image_array, pil_image
        
        except Exception as e:
            logger.error(f"❌ Failed to read image from bytes: {e}")
            raise InvalidImageError(f"Could not read image: {str(e)}")
    
    @staticmethod
    def preprocess_image(image: 'np.ndarray') -> 'np.ndarray':
        """
        Preprocess image for better QR code detection.
        
        Args:
            image: OpenCV image (numpy array)
            
        Returns:
            Preprocessed image
        """
        try:
            if not _HAS_CV2:
                logger.warning("⚠️  OpenCV not available - skipping advanced preprocessing")
                return image

            # Convert to grayscale if color
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            # Apply bilateral filter to reduce noise while preserving edges
            filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            logger.debug("✓ Image preprocessing completed")
            return filtered
        
        except Exception as e:
            logger.warning(f"⚠️  Image preprocessing failed, continuing with original: {e}")
            return image
    
    @staticmethod
    def detect_qr_pyzbar(image: 'np.ndarray') -> Optional[str]:
        """
        Detect and decode QR code using pyzbar (primary method).
        
        Args:
            image: Image as numpy array or PIL Image
            
        Returns:
            Decoded QR data string or None if not found
        """
        try:
            # Convert numpy array to PIL Image if needed
            if image is None:
                logger.debug("ℹ️ detect_qr_pyzbar received None image")
                return None

            if isinstance(image, np.ndarray):
                if len(image.shape) == 3:
                    # If image is BGR (from OpenCV), convert to RGB; otherwise assume RGB
                    if _HAS_CV2:
                        try:
                            pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                        except Exception:
                            pil_img = Image.fromarray(image)
                    else:
                        pil_img = Image.fromarray(image)
                else:
                    pil_img = Image.fromarray(image)
            else:
                pil_img = image
            
            if not _HAS_PYZBAR:
                logger.warning("⚠️  pyzbar not available - skipping pyzbar detection")
                return None

            # Detect QR codes
            decoded_objects = pyzbar.decode(pil_img)

            if decoded_objects:
                logger.info(f"✅ pyzbar detected {len(decoded_objects)} QR code(s)")
                
                # Return first QR code data
                qr_data = decoded_objects[0].data.decode('utf-8')
                logger.debug(f"✓ QR data extracted: {qr_data[:100]}")
                return qr_data
            
            logger.warning("⚠️  pyzbar: No QR code detected")
            return None
        
        except Exception as e:
            logger.error(f"❌ pyzbar detection failed: {e}")
            return None
    
    @staticmethod
    def detect_qr_opencv(image: 'np.ndarray') -> Optional[str]:
        """
        Detect and decode QR code using OpenCV (fallback method).
        
        Args:
            image: Image as numpy array (grayscale or color)
            
        Returns:
            Decoded QR data string or None if not found
        """
        try:
            if not _HAS_CV2:
                logger.warning("⚠️  OpenCV not available - skipping OpenCV QR detection")
                return None

            qr_detector = cv2.QRCodeDetector()

            # Try to detect and decode
            retval, decoded_info, points, straight_qr = qr_detector.detectAndDecodeMulti(image)
            
            if retval and decoded_info:
                logger.info(f"✅ OpenCV detected {len(decoded_info)} QR code(s)")
                
                # Return first QR code data
                qr_data = decoded_info[0]
                if qr_data:
                    logger.debug(f"✓ QR data extracted: {qr_data[:100]}")
                    return qr_data
            
            logger.warning("⚠️  OpenCV: No QR code detected")
            return None
        
        except Exception as e:
            logger.error(f"❌ OpenCV detection failed: {e}")
            return None
    
    @staticmethod
    def scan_image_for_qr(image: 'np.ndarray') -> str:
        """
        Scan image for QR code using multiple methods.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Decoded QR data string
            
        Raises:
            QRNotDetectedError: If no QR code found
        """
        logger.info("🔍 Starting QR code detection...")
        
        # Method 1: Try pyzbar on original image
        logger.debug("  Attempting pyzbar detection on original image...")
        qr_data = QRScanner.detect_qr_pyzbar(image)
        if qr_data:
            logger.info("✅ QR detected with pyzbar (original)")
            return qr_data
        
        # Method 2: Try OpenCV on original image
        logger.debug("  Attempting OpenCV detection on original image...")
        qr_data = QRScanner.detect_qr_opencv(image)
        if qr_data:
            logger.info("✅ QR detected with OpenCV (original)")
            return qr_data
        
        # Method 3: Preprocess and try pyzbar again
        logger.debug("  Preprocessing image for better detection...")
        preprocessed = QRScanner.preprocess_image(image)
        
        qr_data = QRScanner.detect_qr_pyzbar(preprocessed)
        if qr_data:
            logger.info("✅ QR detected with pyzbar (preprocessed)")
            return qr_data
        
        # Method 4: Try OpenCV on preprocessed image
        qr_data = QRScanner.detect_qr_opencv(preprocessed)
        if qr_data:
            logger.info("✅ QR detected with OpenCV (preprocessed)")
            return qr_data
        
        # No QR code detected
        logger.error("❌ No QR code detected in image")
        raise QRNotDetectedError(
            "No QR code found in image. Please ensure:"
            "\n  • QR code is clearly visible"  
            "\n  • Image is well-lit"
            "\n  • QR code is not damaged"
            "\n  • Camera is in focus"
        )
    
    @staticmethod
    def parse_qr_data(qr_data: str) -> Dict:
        """
        Parse QR code data and extract attendance information.
        
        Args:
            qr_data: Raw QR code data string
            
        Returns:
            Dictionary with extracted data:
            {
                "team_id": str,
                "access_key": str
            }
            
        Raises:
            InvalidQRDataError: If data cannot be parsed
        """
        try:
            # Try to parse as JSON (most common case)
            data = json.loads(qr_data)
            logger.debug("✓ QR data parsed as JSON")
        except json.JSONDecodeError:
            # Try a few tolerant fallbacks: single quotes -> double quotes,
            # or strip surrounding quotes and retry.
            try:
                alt = qr_data.strip()
                if (alt.startswith("'") and alt.endswith("'")) or (alt.startswith('"') and alt.endswith('"')):
                    alt = alt[1:-1]
                alt = alt.replace("'", '"')
                data = json.loads(alt)
                logger.debug("✓ QR data parsed after fallback JSON normalization")
            except Exception:
                # Last resort: regex extract common keys
                try:
                    import re
                    team_match = re.search(r'"?team_id"?\s*[:=]\s*"?([A-Za-z0-9\-_]+)"?', qr_data)
                    key_match = re.search(r'"?access_key"?\s*[:=]\s*"?([A-Za-z0-9\-_=+%\\\./:@!#$%^&*(),]+)"?', qr_data)
                    member_match = re.search(r'"?member_id"?\s*[:=]\s*"?([A-Za-z0-9\-_]+)"?', qr_data)
                    data = {}
                    if team_match:
                        data['team_id'] = team_match.group(1)
                    if key_match:
                        data['access_key'] = key_match.group(1)
                    if member_match:
                        data['member_id'] = member_match.group(1)
                    if not data:
                        raise InvalidQRDataError("Unable to extract QR fields via fallback regex")
                    logger.debug("✓ QR data extracted via regex fallback")
                except InvalidQRDataError:
                    logger.error("❌ QR data is not valid JSON and regex fallback failed")
                    raise InvalidQRDataError("Invalid QR data format")

        # At this point `data` should be a dict. Accept alternative key names and nested structures.
        if not isinstance(data, dict):
            logger.error("❌ Parsed QR payload is not a JSON object")
            raise InvalidQRDataError("Invalid QR payload structure")

        # Normalize keys: accept team/team_id/teamId and access_key/accessKey/key
        def find_key(d, candidates):
            for k in candidates:
                if k in d and d[k] is not None:
                    return d[k]
            # support nested under 'data' or similar
            for k in ('data', 'payload', 'p'):
                if k in d and isinstance(d[k], dict):
                    for c in candidates:
                        if c in d[k] and d[k][c] is not None:
                            return d[k][c]
            return None

        team_id = find_key(data, ['team_id', 'team', 'teamId'])
        access_key = find_key(data, ['access_key', 'accessKey', 'key', 'access'])
        member_id = find_key(data, ['member_id', 'memberId', 'participant_id', 'participantId'])

        if not team_id or not access_key:
            logger.error(f"❌ QR missing required fields after normalization: team_id={team_id}, access_key={access_key}")
            raise InvalidQRDataError("Missing required field: team_id or access_key")

        result = {
            'team_id': str(team_id).strip(),
            'access_key': str(access_key).strip()
        }
        if member_id:
            result['member_id'] = str(member_id).strip()

        logger.info(f"✅ QR data validated - Team ID: {result['team_id']}")
        return result
    
    @classmethod
    async def scan_file(cls, file_content: bytes, file_name: str, content_type: str) -> Dict:
        """
        Complete QR scanning workflow: validate → read → detect → parse.
        
        Args:
            file_content: Raw image bytes
            file_name: Original filename
            content_type: MIME type
            
        Returns:
            Parsed QR data dictionary
            
        Raises:
            InvalidImageError: If image is invalid
            QRNotDetectedError: If QR code not found
            InvalidQRDataError: If QR data cannot be parsed
        """
        # Step 1: Validate file
        logger.info(f"📥 Starting QR scan: {file_name}")
        cls.validate_file(file_content, file_name, content_type)
        
        # Step 2: Read image
        logger.debug("  Reading image file...")
        cv_image, pil_image = cls.read_image_from_bytes(file_content)
        
        # Step 3: Detect QR code
        logger.debug("  Detecting QR code...")
        qr_data_string = cls.scan_image_for_qr(cv_image)
        
        # Step 4: Parse QR data
        logger.debug("  Parsing QR data...")
        qr_data = cls.parse_qr_data(qr_data_string)
        
        logger.info("✅ QR code successfully scanned and parsed")
        return qr_data


def get_qr_scanner() -> QRScanner:
    """Dependency injection for QR scanner."""
    return QRScanner()
