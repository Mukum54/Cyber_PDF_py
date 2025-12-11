"""
Core PDF operations: split, merge, rotate, extract
"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from pypdf import PdfReader, PdfWriter
import logging

logger = logging.getLogger(__name__)


class PDFOperations:
    """Core PDF manipulation operations"""
    
    @staticmethod
    def split_pdf(
        input_path: str,
        output_dir: str,
        split_mode: str = "by_pages",
        **kwargs
    ) -> List[str]:
        """
        Split PDF into multiple files
        
        Args:
            input_path: Path to input PDF
            output_dir: Directory for output files
            split_mode: One of 'by_pages', 'by_count', 'by_size', 'by_bookmarks', 'smart'
            **kwargs: Additional parameters based on split_mode
                - pages: List of page numbers for 'by_pages' mode
                - count: Number of pages per file for 'by_count' mode
                - size_mb: Max file size in MB for 'by_size' mode
        
        Returns:
            List of output file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        output_files = []
        
        if split_mode == "by_pages":
            # Split at specific page numbers
            pages = kwargs.get("pages", [])
            if not pages:
                raise ValueError("'pages' parameter required for by_pages mode")
            
            # Convert page ranges to list of split points
            split_points = [0] + sorted(pages) + [total_pages]
            
            for i in range(len(split_points) - 1):
                start = split_points[i]
                end = split_points[i + 1]
                
                writer = PdfWriter()
                for page_num in range(start, end):
                    writer.add_page(reader.pages[page_num])
                
                output_path = output_dir / f"part_{i+1}.pdf"
                with open(output_path, "wb") as f:
                    writer.write(f)
                
                output_files.append(str(output_path))
                logger.info(f"Created {output_path} (pages {start+1}-{end})")
        
        elif split_mode == "by_count":
            # Split into N-page chunks
            count = kwargs.get("count", 10)
            
            for i in range(0, total_pages, count):
                writer = PdfWriter()
                end = min(i + count, total_pages)
                
                for page_num in range(i, end):
                    writer.add_page(reader.pages[page_num])
                
                output_path = output_dir / f"part_{i//count + 1}.pdf"
                with open(output_path, "wb") as f:
                    writer.write(f)
                
                output_files.append(str(output_path))
                logger.info(f"Created {output_path} (pages {i+1}-{end})")
        
        elif split_mode == "by_bookmarks":
            # Split at bookmark boundaries
            doc = fitz.open(input_path)
            toc = doc.get_toc()
            
            if not toc:
                raise ValueError("PDF has no bookmarks")
            
            # Get bookmark page numbers
            bookmark_pages = [item[2] - 1 for item in toc if item[1] == 1]  # Level 1 bookmarks
            bookmark_pages.append(total_pages)
            
            for i in range(len(bookmark_pages) - 1):
                start = bookmark_pages[i]
                end = bookmark_pages[i + 1]
                
                writer = PdfWriter()
                for page_num in range(start, end):
                    writer.add_page(reader.pages[page_num])
                
                # Use bookmark title as filename
                title = toc[i][1] if i < len(toc) else f"section_{i+1}"
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
                output_path = output_dir / f"{safe_title}.pdf"
                
                with open(output_path, "wb") as f:
                    writer.write(f)
                
                output_files.append(str(output_path))
                logger.info(f"Created {output_path} (pages {start+1}-{end})")
        
        elif split_mode == "smart":
            # Auto-detect chapter breaks using blank pages or content analysis
            doc = fitz.open(input_path)
            split_points = [0]
            
            for page_num in range(total_pages):
                page = doc[page_num]
                text = page.get_text().strip()
                
                # Detect blank or nearly blank pages
                if len(text) < 50:
                    split_points.append(page_num + 1)
            
            split_points.append(total_pages)
            
            # Remove consecutive split points
            split_points = sorted(set(split_points))
            
            for i in range(len(split_points) - 1):
                start = split_points[i]
                end = split_points[i + 1]
                
                if end - start < 1:  # Skip empty sections
                    continue
                
                writer = PdfWriter()
                for page_num in range(start, end):
                    writer.add_page(reader.pages[page_num])
                
                output_path = output_dir / f"chapter_{i+1}.pdf"
                with open(output_path, "wb") as f:
                    writer.write(f)
                
                output_files.append(str(output_path))
                logger.info(f"Created {output_path} (pages {start+1}-{end})")
        
        else:
            raise ValueError(f"Unknown split mode: {split_mode}")
        
        return output_files
    
    @staticmethod
    def merge_pdfs(
        input_files: List[str],
        output_path: str,
        page_order: Optional[List[Tuple[int, int]]] = None
    ) -> str:
        """
        Merge multiple PDFs into one
        
        Args:
            input_files: List of PDF file paths to merge
            output_path: Path for output PDF
            page_order: Optional list of (file_index, page_index) tuples for custom ordering
        
        Returns:
            Path to merged PDF
        """
        writer = PdfWriter()
        
        if page_order:
            # Custom page ordering
            for file_idx, page_idx in page_order:
                reader = PdfReader(input_files[file_idx])
                writer.add_page(reader.pages[page_idx])
        else:
            # Sequential merge
            for input_file in input_files:
                reader = PdfReader(input_file)
                for page in reader.pages:
                    writer.add_page(page)
                logger.info(f"Added {len(reader.pages)} pages from {input_file}")
        
        with open(output_path, "wb") as f:
            writer.write(f)
        
        logger.info(f"Merged PDF saved to {output_path}")
        return output_path
    
    @staticmethod
    def rotate_pages(
        input_path: str,
        output_path: str,
        rotations: Dict[int, int]
    ) -> str:
        """
        Rotate specific pages
        
        Args:
            input_path: Path to input PDF
            output_path: Path for output PDF
            rotations: Dictionary mapping page numbers to rotation angles (90, 180, 270)
        
        Returns:
            Path to rotated PDF
        """
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page_num, page in enumerate(reader.pages):
            if page_num in rotations:
                angle = rotations[page_num]
                page.rotate(angle)
                logger.info(f"Rotated page {page_num + 1} by {angle} degrees")
            
            writer.add_page(page)
        
        with open(output_path, "wb") as f:
            writer.write(f)
        
        logger.info(f"Rotated PDF saved to {output_path}")
        return output_path
    
    @staticmethod
    def arrange_pages(
        input_path: str,
        output_path: str,
        page_order: List[int]
    ) -> str:
        """
        Arrange PDF pages in custom order (supports reordering, deletion, and duplication)
        
        Args:
            input_path: Path to input PDF
            output_path: Path for output PDF
            page_order: List of page indices (0-based) in desired order
                       - Omit indices to delete pages
                       - Repeat indices to duplicate pages
        
        Returns:
            Path to arranged PDF
        """
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        total_pages = len(reader.pages)
        
        # Validate page indices
        for idx in page_order:
            if idx < 0 or idx >= total_pages:
                raise ValueError(f"Invalid page index: {idx}. PDF has {total_pages} pages (0-{total_pages-1})")
        
        # Add pages in specified order
        for idx in page_order:
            writer.add_page(reader.pages[idx])
            logger.info(f"Added page {idx + 1} to output")
        
        with open(output_path, "wb") as f:
            writer.write(f)
        
        logger.info(f"Arranged PDF saved to {output_path} ({len(page_order)} pages)")
        return output_path

    
    @staticmethod
    def extract_text(input_path: str, page_range: Optional[Tuple[int, int]] = None) -> str:
        """
        Extract text from PDF
        
        Args:
            input_path: Path to input PDF
            page_range: Optional (start, end) page range
        
        Returns:
            Extracted text
        """
        doc = fitz.open(input_path)
        text_parts = []
        
        start = page_range[0] if page_range else 0
        end = page_range[1] if page_range else len(doc)
        
        for page_num in range(start, end):
            page = doc[page_num]
            text = page.get_text()
            text_parts.append(text)
            logger.info(f"Extracted text from page {page_num + 1}")
        
        return "\n\n".join(text_parts)
    
    @staticmethod
    def extract_images(input_path: str, output_dir: str) -> List[str]:
        """
        Extract all images from PDF
        
        Args:
            input_path: Path to input PDF
            output_dir: Directory for output images
        
        Returns:
            List of extracted image paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        doc = fitz.open(input_path)
        image_paths = []
        image_count = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                image_path = output_dir / f"image_{image_count + 1}.{image_ext}"
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                
                image_paths.append(str(image_path))
                image_count += 1
                logger.info(f"Extracted image {image_count} from page {page_num + 1}")
        
        return image_paths
    
    @staticmethod
    def get_metadata(input_path: str) -> Dict[str, any]:
        """
        Extract PDF metadata
        
        Args:
            input_path: Path to input PDF
        
        Returns:
            Dictionary containing metadata
        """
        doc = fitz.open(input_path)
        metadata = doc.metadata
        
        # Add additional statistics
        metadata["page_count"] = len(doc)
        metadata["file_size"] = Path(input_path).stat().st_size
        
        # Analyze fonts and images
        fonts = set()
        image_count = 0
        
        for page in doc:
            # Get fonts
            for font in page.get_fonts():
                fonts.add(font[3])  # Font name
            
            # Count images
            image_count += len(page.get_images())
        
        metadata["fonts"] = list(fonts)
        metadata["image_count"] = image_count
        
        logger.info(f"Extracted metadata from {input_path}")
        return metadata
