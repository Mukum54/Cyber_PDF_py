"""
Arrange Pages screen - Reorder, delete, and duplicate PDF pages
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QGroupBox, QMessageBox,
    QProgressDialog, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging
from pathlib import Path

from cyberpdf_core.pdf_tools.operations import PDFOperations

logger = logging.getLogger(__name__)


class ArrangePagesScreen(QWidget):
    """Screen for arranging PDF pages"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.input_file = None
        self.page_count = 0
        self._setup_ui()
        logger.info("Arrange Pages screen initialized")
    
    def _setup_ui(self):
        """Set up UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(back_btn)
        
        header_layout.addStretch()
        
        title = QLabel("Arrange Pages")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # File selection
        file_group = QGroupBox("Select PDF File")
        file_layout = QHBoxLayout(file_group)
        
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(browse_btn)
        
        layout.addWidget(file_group)
        
        # Page list and controls
        pages_group = QGroupBox("Page Order")
        pages_layout = QHBoxLayout(pages_group)
        
        # Page list
        list_layout = QVBoxLayout()
        
        self.page_info_label = QLabel("Load a PDF to see pages")
        self.page_info_label.setStyleSheet("color: #718096; font-size: 12px;")
        list_layout.addWidget(self.page_info_label)
        
        self.page_list = QListWidget()
        self.page_list.setMinimumHeight(300)
        self.page_list.currentRowChanged.connect(self._on_selection_changed)
        list_layout.addWidget(self.page_list)
        
        pages_layout.addLayout(list_layout, 3)
        
        # Control buttons
        controls_layout = QVBoxLayout()
        
        self.move_up_btn = QPushButton("↑ Move Up")
        self.move_up_btn.setEnabled(False)
        self.move_up_btn.clicked.connect(self._move_up)
        controls_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("↓ Move Down")
        self.move_down_btn.setEnabled(False)
        self.move_down_btn.clicked.connect(self._move_down)
        controls_layout.addWidget(self.move_down_btn)
        
        controls_layout.addSpacing(20)
        
        self.duplicate_btn = QPushButton("📄 Duplicate")
        self.duplicate_btn.setEnabled(False)
        self.duplicate_btn.clicked.connect(self._duplicate_page)
        controls_layout.addWidget(self.duplicate_btn)
        
        self.delete_btn = QPushButton("🗑 Delete")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self._delete_page)
        controls_layout.addWidget(self.delete_btn)
        
        controls_layout.addStretch()
        
        pages_layout.addLayout(controls_layout, 1)
        
        layout.addWidget(pages_group)
        
        # Output file
        output_group = QGroupBox("Output File")
        output_layout = QHBoxLayout(output_group)
        
        self.output_label = QLabel("Will be set after selecting input file")
        output_layout.addWidget(self.output_label)
        
        output_btn = QPushButton("Change...")
        output_btn.clicked.connect(self._browse_output)
        output_layout.addWidget(output_btn)
        
        layout.addWidget(output_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save Arranged PDF")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_arranged_pdf)
        self.save_btn.setMinimumWidth(180)
        self.save_btn.setMinimumHeight(40)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def _browse_file(self):
        """Browse for input PDF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF File",
            str(Path.home()),
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.input_file = file_path
            self.file_label.setText(Path(file_path).name)
            
            # Load PDF pages
            self._load_pages()
            
            # Set default output path
            input_path = Path(file_path)
            output_path = input_path.parent / f"{input_path.stem}_arranged.pdf"
            self.output_label.setText(str(output_path))
            
            self.save_btn.setEnabled(True)
            logger.info(f"Selected file: {file_path}")
    
    def _load_pages(self):
        """Load pages from PDF"""
        try:
            from pypdf import PdfReader
            reader = PdfReader(self.input_file)
            self.page_count = len(reader.pages)
            
            # Clear and populate list
            self.page_list.clear()
            for i in range(self.page_count):
                item = QListWidgetItem(f"Page {i + 1}")
                item.setData(Qt.UserRole, i)  # Store original page index
                self.page_list.addItem(item)
            
            self.page_info_label.setText(f"Total pages: {self.page_count}")
            logger.info(f"Loaded {self.page_count} pages")
            
        except Exception as e:
            logger.error(f"Error loading pages: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load PDF pages:\n{str(e)}")
    
    def _browse_output(self):
        """Browse for output file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Arranged PDF",
            self.output_label.text(),
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.output_label.setText(file_path)
    
    def _on_selection_changed(self, current_row):
        """Handle page selection change"""
        has_selection = current_row >= 0
        self.move_up_btn.setEnabled(has_selection and current_row > 0)
        self.move_down_btn.setEnabled(has_selection and current_row < self.page_list.count() - 1)
        self.duplicate_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection and self.page_list.count() > 1)
    
    def _move_up(self):
        """Move selected page up"""
        current_row = self.page_list.currentRow()
        if current_row > 0:
            item = self.page_list.takeItem(current_row)
            self.page_list.insertItem(current_row - 1, item)
            self.page_list.setCurrentRow(current_row - 1)
            logger.info(f"Moved page from position {current_row + 1} to {current_row}")
    
    def _move_down(self):
        """Move selected page down"""
        current_row = self.page_list.currentRow()
        if current_row < self.page_list.count() - 1:
            item = self.page_list.takeItem(current_row)
            self.page_list.insertItem(current_row + 1, item)
            self.page_list.setCurrentRow(current_row + 1)
            logger.info(f"Moved page from position {current_row + 1} to {current_row + 2}")
    
    def _duplicate_page(self):
        """Duplicate selected page"""
        current_row = self.page_list.currentRow()
        if current_row >= 0:
            current_item = self.page_list.item(current_row)
            page_idx = current_item.data(Qt.UserRole)
            
            # Create duplicate
            new_item = QListWidgetItem(f"Page {page_idx + 1} (copy)")
            new_item.setData(Qt.UserRole, page_idx)
            self.page_list.insertItem(current_row + 1, new_item)
            
            logger.info(f"Duplicated page {page_idx + 1}")
    
    def _delete_page(self):
        """Delete selected page"""
        current_row = self.page_list.currentRow()
        if current_row >= 0 and self.page_list.count() > 1:
            item = self.page_list.takeItem(current_row)
            page_idx = item.data(Qt.UserRole)
            logger.info(f"Deleted page {page_idx + 1} from arrangement")
    
    def _save_arranged_pdf(self):
        """Save the arranged PDF"""
        if not self.input_file or self.page_list.count() == 0:
            QMessageBox.warning(self, "No Pages", "No pages to arrange.")
            return
        
        try:
            output_path = self.output_label.text()
            
            # Get page order from list
            page_order = []
            for i in range(self.page_list.count()):
                item = self.page_list.item(i)
                page_idx = item.data(Qt.UserRole)
                page_order.append(page_idx)
            
            # Show progress dialog
            progress = QProgressDialog("Arranging pages...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Perform arrangement
            result = PDFOperations.arrange_pages(
                self.input_file,
                output_path,
                page_order
            )
            
            progress.close()
            
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Pages arranged successfully!\\n\\n"
                f"Original pages: {self.page_count}\\n"
                f"Arranged pages: {len(page_order)}\\n\\n"
                f"Output file:\\n{result}"
            )
            
            logger.info(f"Successfully arranged PDF: {result}")
            
        except Exception as e:
            logger.error(f"Error arranging pages: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to arrange pages:\\n{str(e)}"
            )
