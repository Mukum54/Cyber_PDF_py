"""
Word to PDF conversion screen
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QGroupBox, QMessageBox,
    QProgressDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging
from pathlib import Path

from cyberpdf_core.converters.pdf_word import PDFWordConverter

logger = logging.getLogger(__name__)


class WordToPDFScreen(QWidget):
    """Screen for converting Word to PDF"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.input_file = None
        self._setup_ui()
        self._check_dependencies()
        logger.info("Word to PDF screen initialized")
    
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
        
        title = QLabel("Word to PDF")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # File selection
        file_group = QGroupBox("Select Word Document")
        file_layout = QHBoxLayout(file_group)
        
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(browse_btn)
        
        layout.addWidget(file_group)
        
        # Dependency status
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel()
        status_layout.addWidget(self.status_label)
        
        layout.addWidget(status_group)
        
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
        
        self.convert_btn = QPushButton("Convert to PDF")
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self._convert_word)
        self.convert_btn.setMinimumWidth(150)
        self.convert_btn.setMinimumHeight(40)
        button_layout.addWidget(self.convert_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def _check_dependencies(self):
        """Check for required dependencies"""
        deps = PDFWordConverter.check_dependencies()
        
        if deps['libreoffice']:
            self.status_label.setText("✓ LibreOffice is installed and ready")
            self.status_label.setStyleSheet("color: #48BB78;")
        else:
            self.status_label.setText("✗ LibreOffice is required for Word to PDF conversion\n\nInstall: sudo apt install libreoffice")
            self.status_label.setStyleSheet("color: #F56565;")
    
    def _browse_file(self):
        """Browse for input Word file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Word Document",
            str(Path.home()),
            "Word Documents (*.docx *.doc)"
        )
        
        if file_path:
            self.input_file = file_path
            self.file_label.setText(Path(file_path).name)
            
            # Set default output path
            input_path = Path(file_path)
            output_path = input_path.with_suffix('.pdf')
            self.output_label.setText(str(output_path))
            
            self.convert_btn.setEnabled(True)
            logger.info(f"Selected file: {file_path}")
    
    def _browse_output(self):
        """Browse for output file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF File",
            self.output_label.text(),
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.output_label.setText(file_path)
    
    def _convert_word(self):
        """Convert Word to PDF"""
        if not self.input_file:
            return
        
        try:
            output_path = self.output_label.text()
            
            # Show progress dialog
            progress = QProgressDialog("Converting Word to PDF...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Perform conversion
            result = PDFWordConverter.word_to_pdf(
                self.input_file,
                output_path
            )
            
            progress.close()
            
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Word document converted to PDF successfully!\n\nOutput file:\n{result}"
            )
            
            logger.info(f"Successfully converted Word to PDF: {result}")
            
        except Exception as e:
            logger.error(f"Error converting Word: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to convert Word document:\n{str(e)}\n\nMake sure LibreOffice is installed:\nsudo apt install libreoffice"
            )
