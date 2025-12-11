"""
Page arrangement system for visual PDF manipulation
"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import hashlib
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)


class PageArranger:
    """Backend for visual page manipulation and reordering"""
    
    def __init__(self, pdf_path: str, cache_dir: Optional[str] = None):
        """
        Initialize page arranger
        
        Args:
            pdf_path: Path to PDF file
            cache_dir: Directory for thumbnail cache (default: /tmp/cyberpdf)
        """
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.page_count = len(self.doc)
        self.page_order = list(range(self.page_count))
        
        # Set up cache directory
        if cache_dir is None:
            cache_dir = Path("/tmp/cyberpdf")
        self.cache_dir = Path(cache_dir)
        
        # Create session-specific cache directory
        pdf_hash = hashlib.md5(pdf_path.encode()).hexdigest()[:8]
        self.session_cache = self.cache_dir / pdf_hash
        self.session_cache.mkdir(parents=True, exist_ok=True)
        
        self.thumbnail_cache: Dict[int, str] = {}
        self.undo_stack: List[List[int]] = []
        self.redo_stack: List[List[int]] = []
        
        logger.info(f"Initialized PageArranger for {pdf_path} ({self.page_count} pages)")
    
    def generate_thumbnails(
        self,
        max_size: int = 200,
        quality: int = 85,
        force_regenerate: bool = False
    ) -> Dict[int, str]:
        """
        Generate thumbnails for all pages
        
        Args:
            max_size: Maximum dimension (width or height) in pixels
            quality: JPEG quality (0-100)
            force_regenerate: Force regeneration even if cached
        
        Returns:
            Dictionary mapping page numbers to thumbnail paths
        """
        for page_num in range(self.page_count):
            thumbnail_path = self.session_cache / f"page_{page_num}.jpg"
            
            # Use cached thumbnail if exists
            if thumbnail_path.exists() and not force_regenerate:
                self.thumbnail_cache[page_num] = str(thumbnail_path)
                continue
            
            # Generate thumbnail
            page = self.doc[page_num]
            
            # Calculate zoom to fit max_size
            page_rect = page.rect
            zoom = max_size / max(page_rect.width, page_rect.height)
            mat = fitz.Matrix(zoom, zoom)
            
            # Render page to pixmap
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to PIL Image for better compression
            img_data = pix.tobytes("jpeg", quality)
            img = Image.open(io.BytesIO(img_data))
            
            # Save thumbnail
            img.save(thumbnail_path, "JPEG", quality=quality, optimize=True)
            
            self.thumbnail_cache[page_num] = str(thumbnail_path)
            logger.debug(f"Generated thumbnail for page {page_num + 1}")
        
        logger.info(f"Generated {len(self.thumbnail_cache)} thumbnails")
        return self.thumbnail_cache
    
    def get_thumbnail(self, page_num: int) -> Optional[str]:
        """
        Get thumbnail path for a specific page
        
        Args:
            page_num: Page number (0-indexed)
        
        Returns:
            Path to thumbnail image or None
        """
        if page_num not in self.thumbnail_cache:
            # Generate on demand
            self.generate_thumbnails()
        
        return self.thumbnail_cache.get(page_num)
    
    def reorder_pages(self, new_order: List[int]) -> None:
        """
        Update page order
        
        Args:
            new_order: New list of page indices
        """
        if len(new_order) != len(self.page_order):
            raise ValueError("New order must contain all pages")
        
        # Save current state for undo
        self.undo_stack.append(self.page_order.copy())
        self.redo_stack.clear()
        
        self.page_order = new_order
        logger.info(f"Reordered pages: {new_order}")
    
    def move_page(self, from_index: int, to_index: int) -> None:
        """
        Move a page from one position to another
        
        Args:
            from_index: Current position
            to_index: Target position
        """
        # Save current state for undo
        self.undo_stack.append(self.page_order.copy())
        self.redo_stack.clear()
        
        page = self.page_order.pop(from_index)
        self.page_order.insert(to_index, page)
        
        logger.info(f"Moved page from {from_index} to {to_index}")
    
    def delete_pages(self, page_indices: List[int]) -> None:
        """
        Remove pages from document
        
        Args:
            page_indices: List of page indices to delete
        """
        # Save current state for undo
        self.undo_stack.append(self.page_order.copy())
        self.redo_stack.clear()
        
        # Remove pages (sort in reverse to maintain indices)
        for idx in sorted(page_indices, reverse=True):
            if 0 <= idx < len(self.page_order):
                del self.page_order[idx]
        
        logger.info(f"Deleted {len(page_indices)} pages")
    
    def duplicate_pages(self, page_indices: List[int]) -> None:
        """
        Duplicate specified pages
        
        Args:
            page_indices: List of page indices to duplicate
        """
        # Save current state for undo
        self.undo_stack.append(self.page_order.copy())
        self.redo_stack.clear()
        
        # Duplicate pages (insert after original)
        offset = 0
        for idx in sorted(page_indices):
            page_num = self.page_order[idx + offset]
            self.page_order.insert(idx + offset + 1, page_num)
            offset += 1
        
        logger.info(f"Duplicated {len(page_indices)} pages")
    
    def rotate_page(self, page_index: int, angle: int) -> None:
        """
        Rotate a specific page
        
        Args:
            page_index: Index in current page order
            angle: Rotation angle (90, 180, 270)
        """
        if angle not in [90, 180, 270, -90, -180, -270]:
            raise ValueError("Angle must be 90, 180, or 270 degrees")
        
        page_num = self.page_order[page_index]
        page = self.doc[page_num]
        page.set_rotation(angle)
        
        # Regenerate thumbnail for this page
        thumbnail_path = self.session_cache / f"page_{page_num}.jpg"
        if thumbnail_path.exists():
            thumbnail_path.unlink()
        
        self.generate_thumbnails(force_regenerate=False)
        
        logger.info(f"Rotated page {page_index} by {angle} degrees")
    
    def undo(self) -> bool:
        """
        Undo last operation
        
        Returns:
            True if undo was successful
        """
        if not self.undo_stack:
            return False
        
        self.redo_stack.append(self.page_order.copy())
        self.page_order = self.undo_stack.pop()
        
        logger.info("Undo operation")
        return True
    
    def redo(self) -> bool:
        """
        Redo last undone operation
        
        Returns:
            True if redo was successful
        """
        if not self.redo_stack:
            return False
        
        self.undo_stack.append(self.page_order.copy())
        self.page_order = self.redo_stack.pop()
        
        logger.info("Redo operation")
        return True
    
    def save_arranged(self, output_path: str) -> str:
        """
        Save PDF with new page arrangement
        
        Args:
            output_path: Path for output PDF
        
        Returns:
            Path to saved PDF
        """
        new_doc = fitz.open()
        
        for page_idx in self.page_order:
            new_doc.insert_pdf(
                self.doc,
                from_page=page_idx,
                to_page=page_idx
            )
        
        # Preserve metadata
        new_doc.set_metadata(self.doc.metadata)
        
        new_doc.save(output_path)
        new_doc.close()
        
        logger.info(f"Saved arranged PDF to {output_path} ({len(self.page_order)} pages)")
        return output_path
    
    def get_page_info(self, page_index: int) -> Dict:
        """
        Get information about a specific page
        
        Args:
            page_index: Index in current page order
        
        Returns:
            Dictionary with page information
        """
        page_num = self.page_order[page_index]
        page = self.doc[page_num]
        
        return {
            "original_page_num": page_num + 1,
            "current_index": page_index,
            "width": page.rect.width,
            "height": page.rect.height,
            "rotation": page.rotation,
            "has_images": len(page.get_images()) > 0,
            "has_text": bool(page.get_text().strip()),
        }
    
    def cleanup(self) -> None:
        """Clean up resources and cache"""
        self.doc.close()
        
        # Optionally remove cache
        # for file in self.session_cache.glob("*.jpg"):
        #     file.unlink()
        
        logger.info("Cleaned up PageArranger resources")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
