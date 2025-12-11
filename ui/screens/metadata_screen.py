"""
PDF Metadata viewer screen
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QGroupBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging
from pathlib import Path

from cyberpdf_core.pdf_tools.operations import PDFOperations

logger = logging.getLogger(__name__)


class MetadataScreen(QWidget):
    """Screen for viewing PDF metadata"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.input_file = None
        self._setup_ui()
        logger.info("Metadata screen initialized")
    
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
        
        title = QLabel("PDF Metadata")
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
        
        # Metadata table
        metadata_group = QGroupBox("Metadata Information")
        metadata_layout = QVBoxLayout(metadata_group)
        
        self.metadata_table = QTableWidget()
        self.metadata_table.setColumnCount(2)
        self.metadata_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.metadata_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.metadata_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.metadata_table.setMinimumHeight(400)
        metadata_layout.addWidget(self.metadata_table)
        
        layout.addWidget(metadata_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.view_btn = QPushButton("View Metadata")
        self.view_btn.setEnabled(False)
        self.view_btn.clicked.connect(self._view_metadata)
        self.view_btn.setMinimumWidth(150)
        self.view_btn.setMinimumHeight(40)
        button_layout.addWidget(self.view_btn)
        
        button_layout.addStretch()
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
            self.view_btn.setEnabled(True)
            self.metadata_table.setRowCount(0)
            logger.info(f"Selected file: {file_path}")
    
    def _view_metadata(self):
        """View PDF metadata"""
        if not self.input_file:
            return
        
        try:
            # Get metadata
            metadata = PDFOperations.get_metadata(self.input_file)
            
            # Clear table
            self.metadata_table.setRowCount(0)
            
            # Add metadata to table
            row = 0
            
            # File info
            self._add_row(row, "File Name", Path(self.input_file).name)
            row += 1
            
            self._add_row(row, "File Size", f"{metadata.get('file_size', 0) / 1024 / 1024:.2f} MB")
            row += 1
            
            self._add_row(row, "Page Count", str(metadata.get('page_count', 'N/A')))
            row += 1
            
            # Document properties
            properties = [
                ('Title', 'title'),
                ('Author', 'author'),
                ('Subject', 'subject'),
                ('Creator', 'creator'),
                ('Producer', 'producer'),
                ('Creation Date', 'creation_date'),
                ('Modification Date', 'mod_date'),
            ]
            
            for label, key in properties:
                value = metadata.get(key, 'N/A')
                if value and value != 'N/A':
                    self._add_row(row, label, str(value))
                    row += 1
            
            # Statistics
            self._add_row(row, "Image Count", str(metadata.get('image_count', 0)))
            row += 1
            
            if metadata.get('fonts'):
                fonts_str = ', '.join(metadata['fonts'][:5])
                if len(metadata['fonts']) > 5:
                    fonts_str += f" ... ({len(metadata['fonts'])} total)"
                self._add_row(row, "Fonts", fonts_str)
                row += 1
            
            logger.info(f"Displayed metadata for {self.input_file}")
            
        except Exception as e:
            logger.error(f"Error viewing metadata: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to view metadata:\n{str(e)}"
            )
    
    def _add_row(self, row, property_name, value):
        """Add a row to the metadata table"""
        self.metadata_table.insertRow(row)
        
        property_item = QTableWidgetItem(property_name)
        property_item.setFlags(property_item.flags() & ~Qt.ItemIsEditable)
        property_item.setFont(QFont("", -1, QFont.Bold))
        self.metadata_table.setItem(row, 0, property_item)
        
        value_item = QTableWidgetItem(str(value))
        value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)
        self.metadata_table.setItem(row, 1, value_item)
