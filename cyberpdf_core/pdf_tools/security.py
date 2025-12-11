"""
PDF security operations: encryption, decryption, watermarking
"""
import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PDFSecurity:
    """PDF security and encryption operations"""
    
    @staticmethod
    def encrypt_pdf(
        input_path: str,
        output_path: str,
        user_password: str,
        owner_password: Optional[str] = None,
        permissions: Optional[int] = None
    ) -> str:
        """
        Encrypt PDF with password
        
        Args:
            input_path: Path to input PDF
            output_path: Path for encrypted PDF
            user_password: Password for opening the PDF
            owner_password: Password for changing permissions (defaults to user_password)
            permissions: Permission flags (default: all permissions)
        
        Returns:
            Path to encrypted PDF
        """
        if owner_password is None:
            owner_password = user_password
        
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Copy metadata
        if reader.metadata:
            writer.add_metadata(reader.metadata)
        
        # Encrypt with AES-256
        writer.encrypt(
            user_password=user_password,
            owner_password=owner_password,
            permissions_flag=permissions or -1,  # All permissions
            algorithm="AES-256"
        )
        
        with open(output_path, "wb") as f:
            writer.write(f)
        
        logger.info(f"Encrypted PDF saved to {output_path}")
        return output_path
    
    @staticmethod
    def decrypt_pdf(
        input_path: str,
        output_path: str,
        password: str
    ) -> str:
        """
        Decrypt password-protected PDF
        
        Args:
            input_path: Path to encrypted PDF
            output_path: Path for decrypted PDF
            password: PDF password
        
        Returns:
            Path to decrypted PDF
        """
        reader = PdfReader(input_path)
        
        if reader.is_encrypted:
            if not reader.decrypt(password):
                raise ValueError("Incorrect password")
        
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        if reader.metadata:
            writer.add_metadata(reader.metadata)
        
        with open(output_path, "wb") as f:
            writer.write(f)
        
        logger.info(f"Decrypted PDF saved to {output_path}")
        return output_path
    
    @staticmethod
    def add_watermark(
        input_path: str,
        output_path: str,
        watermark_text: str,
        position: str = "center",
        opacity: float = 0.3,
        font_size: int = 48,
        color: Tuple[float, float, float] = (0.5, 0.5, 0.5),
        rotation: int = 0
    ) -> str:
        """
        Add text watermark to PDF
        
        Args:
            input_path: Path to input PDF
            output_path: Path for watermarked PDF
            watermark_text: Text to use as watermark
            position: Position ('center', 'top', 'bottom', 'diagonal')
            opacity: Watermark opacity (0.0 to 1.0)
            font_size: Font size for watermark
            color: RGB color tuple (0.0 to 1.0 for each channel)
            rotation: Rotation angle in degrees (must be 0, 90, 180, or 270)
        
        Returns:
            Path to watermarked PDF
        """
        doc = fitz.open(input_path)
        
        for page in doc:
            page_rect = page.rect
            
            # Calculate position
            if position == "center":
                x = page_rect.width / 2
                y = page_rect.height / 2
            elif position == "top":
                x = page_rect.width / 2
                y = page_rect.height * 0.1
            elif position == "bottom":
                x = page_rect.width / 2
                y = page_rect.height * 0.9
            else:  # diagonal
                x = page_rect.width / 2
                y = page_rect.height / 2
            
            # Insert watermark text (PyMuPDF doesn't support opacity in insert_text)
            # Use lighter color to simulate opacity
            adjusted_color = tuple(c + (1 - c) * (1 - opacity) for c in color)
            
            page.insert_text(
                (x, y),
                watermark_text,
                fontsize=font_size,
                color=adjusted_color,
                rotate=rotation
            )
        
        doc.save(output_path)
        doc.close()
        
        logger.info(f"Watermarked PDF saved to {output_path}")
        return output_path
    
    @staticmethod
    def remove_metadata(input_path: str, output_path: str) -> str:
        """
        Remove all metadata from PDF for privacy
        
        Args:
            input_path: Path to input PDF
            output_path: Path for cleaned PDF
        
        Returns:
            Path to cleaned PDF
        """
        doc = fitz.open(input_path)
        
        # Clear metadata
        doc.set_metadata({})
        
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()
        
        logger.info(f"Metadata removed, saved to {output_path}")
        return output_path
    
    @staticmethod
    def check_security(input_path: str) -> dict:
        """
        Check PDF security settings
        
        Args:
            input_path: Path to PDF
        
        Returns:
            Dictionary with security information
        """
        reader = PdfReader(input_path)
        
        security_info = {
            "is_encrypted": reader.is_encrypted,
            "has_metadata": bool(reader.metadata),
        }
        
        if reader.is_encrypted:
            # Try to get permissions (if accessible)
            try:
                security_info["permissions"] = {
                    "print": reader.metadata.get("/P", 0) & 4 != 0,
                    "modify": reader.metadata.get("/P", 0) & 8 != 0,
                    "copy": reader.metadata.get("/P", 0) & 16 != 0,
                    "annotate": reader.metadata.get("/P", 0) & 32 != 0,
                }
            except:
                security_info["permissions"] = "Unknown (encrypted)"
        
        # Check for hidden metadata
        doc = fitz.open(input_path)
        metadata = doc.metadata
        
        security_info["metadata_fields"] = list(metadata.keys()) if metadata else []
        security_info["has_javascript"] = False  # Check for embedded JavaScript
        
        # Check for JavaScript
        for page in doc:
            if "/JS" in page.get_text("dict"):
                security_info["has_javascript"] = True
                break
        
        doc.close()
        
        return security_info
