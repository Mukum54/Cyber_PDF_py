"""
PDF to Word conversion screen
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QGroupBox, QMessageBox,
    QProgressDialog, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging
from pathlib import Path

from cyberpdf_core.converters.pdf_word import PDFWordConverter

logger = logging.getLogger(__name__)


class PDFToWordScreen(QWidget):
    """Screen for converting PDF to Word"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.input_file = None
        self._setup_ui()
        self._check_dependencies()
        logger.info("PDF to Word screen initialized")
    
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
        
        title = QLabel("PDF to Word")
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
        
        # Conversion options
        options_group = QGroupBox("Conversion Options")
        options_layout = QVBoxLayout(options_group)
        
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Conversion Method:"))
        
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Text Extraction (Fast & Reliable)",
            "LibreOffice (Best Quality - Slower)",
        ])
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()
        
        options_layout.addLayout(method_layout)
        
        # Info label
        info_label = QLabel("💡 Text extraction is recommended for most PDFs. Use LibreOffice only if you need to preserve complex formatting.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #718096; font-size: 11px; padding: 10px;")
        options_layout.addWidget(info_label)
        
        # Dependency status
        self.status_label = QLabel()
        options_layout.addWidget(self.status_label)
        
        layout.addWidget(options_group)
        
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
        
        self.convert_btn = QPushButton("Convert to Word")
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self._convert_pdf)
        self.convert_btn.setMinimumWidth(150)
        self.convert_btn.setMinimumHeight(40)
        button_layout.addWidget(self.convert_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def _check_dependencies(self):
        """Check for required dependencies"""
        deps = PDFWordConverter.check_dependencies()
        
        status_parts = []
        if deps['libreoffice']:
            status_parts.append("✓ LibreOffice available")
        else:
            status_parts.append("✗ LibreOffice not found (install for best quality)")
        
        if deps['unoconv']:
            status_parts.append("✓ unoconv available")
        
        self.status_label.setText("\n".join(status_parts))
    
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
            
            # Set default output path
            input_path = Path(file_path)
            output_path = input_path.with_suffix('.docx')
            self.output_label.setText(str(output_path))
            
            self.convert_btn.setEnabled(True)
            logger.info(f"Selected file: {file_path}")
    
    def _browse_output(self):
        """Browse for output file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Word Document",
            self.output_label.text(),
            "Word Documents (*.docx)"
        )
        
        if file_path:
            self.output_label.setText(file_path)
    
    def _convert_pdf(self):
        """Convert PDF to Word"""
        if not self.input_file:
            return
        
        try:
            output_path = self.output_label.text()
            
            # Determine method
            method_index = self.method_combo.currentIndex()
            if method_index == 0:
                method = "text"  # Text extraction (default)
            else:
                method = "libreoffice"  # LibreOffice
            
            # Show progress dialog
            progress = QProgressDialog("Converting PDF to Word...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Perform conversion
            result = PDFWordConverter.pdf_to_word(
                self.input_file,
                output_path,
                method=method
            )
            
            progress.close()
            
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"PDF converted to Word successfully!\n\nOutput file:\n{result}"
            )
            
            logger.info(f"Successfully converted PDF to Word: {result}")
            
        except Exception as e:
            logger.error(f"Error converting PDF: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to convert PDF:\n{str(e)}\n\nTip: Install LibreOffice for better conversion quality."
            )
