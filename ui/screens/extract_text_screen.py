"""
Text Extraction tool screen
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QTextEdit, QGroupBox,
    QMessageBox, QProgressDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging
from pathlib import Path

from cyberpdf_core.pdf_tools.operations import PDFOperations

logger = logging.getLogger(__name__)


class ExtractTextScreen(QWidget):
    """Screen for extracting text from PDF"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.input_file = None
        self._setup_ui()
        logger.info("Extract Text screen initialized")
    
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
        
        title = QLabel("Extract Text")
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
        
        # Extracted text display
        text_group = QGroupBox("Extracted Text")
        text_layout = QVBoxLayout(text_group)
        
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setPlaceholderText("Extracted text will appear here...")
        self.text_display.setMinimumHeight(400)
        text_layout.addWidget(self.text_display)
        
        layout.addWidget(text_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.extract_btn = QPushButton("Extract Text")
        self.extract_btn.setEnabled(False)
        self.extract_btn.clicked.connect(self._extract_text)
        self.extract_btn.setMinimumWidth(150)
        self.extract_btn.setMinimumHeight(40)
        button_layout.addWidget(self.extract_btn)
        
        self.save_btn = QPushButton("Save to File...")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_text)
        self.save_btn.setMinimumWidth(150)
        self.save_btn.setMinimumHeight(40)
        button_layout.addWidget(self.save_btn)
        
        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.setEnabled(False)
        self.copy_btn.clicked.connect(self._copy_text)
        self.copy_btn.setMinimumWidth(150)
        self.copy_btn.setMinimumHeight(40)
        button_layout.addWidget(self.copy_btn)
        
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
            self.extract_btn.setEnabled(True)
            self.text_display.clear()
            self.save_btn.setEnabled(False)
            self.copy_btn.setEnabled(False)
            logger.info(f"Selected file: {file_path}")
    
    def _extract_text(self):
        """Extract text from PDF"""
        if not self.input_file:
            return
        
        try:
            # Show progress dialog
            progress = QProgressDialog("Extracting text...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Extract text
            text = PDFOperations.extract_text(self.input_file)
            
            progress.close()
            
            # Display text
            self.text_display.setPlainText(text)
            self.save_btn.setEnabled(True)
            self.copy_btn.setEnabled(True)
            
            # Show info
            word_count = len(text.split())
            char_count = len(text)
            
            QMessageBox.information(
                self,
                "Success",
                f"Text extracted successfully!\n\nWords: {word_count:,}\nCharacters: {char_count:,}"
            )
            
            logger.info(f"Extracted {word_count} words from {self.input_file}")
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to extract text:\n{str(e)}"
            )
    
    def _save_text(self):
        """Save extracted text to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Text File",
            str(Path.home() / "extracted_text.txt"),
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_display.toPlainText())
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Text saved to:\n{file_path}"
                )
                
                logger.info(f"Saved text to {file_path}")
                
            except Exception as e:
                logger.error(f"Error saving text: {e}", exc_info=True)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save text:\n{str(e)}"
                )
    
    def _copy_text(self):
        """Copy text to clipboard"""
        from PySide6.QtWidgets import QApplication
        
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_display.toPlainText())
        
        QMessageBox.information(
            self,
            "Copied",
            "Text copied to clipboard!"
        )
