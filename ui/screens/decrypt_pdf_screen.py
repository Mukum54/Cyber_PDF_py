"""
PDF Decryption tool screen
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QLineEdit, QGroupBox,
    QMessageBox, QProgressDialog, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging
from pathlib import Path

from cyberpdf_core.pdf_tools.security import PDFSecurity

logger = logging.getLogger(__name__)


class DecryptPDFScreen(QWidget):
    """Screen for decrypting PDF files"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.input_file = None
        self._setup_ui()
        logger.info("Decrypt PDF screen initialized")
    
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
        
        title = QLabel("Decrypt PDF")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # File selection
        file_group = QGroupBox("Select Encrypted PDF File")
        file_layout = QHBoxLayout(file_group)
        
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(browse_btn)
        
        layout.addWidget(file_group)
        
        # Password input
        password_group = QGroupBox("Enter Password")
        password_layout = QVBoxLayout(password_group)
        
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Password:"))
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter PDF password")
        pass_layout.addWidget(self.password_input)
        
        self.show_password = QCheckBox("Show")
        self.show_password.toggled.connect(self._toggle_password_visibility)
        pass_layout.addWidget(self.show_password)
        
        password_layout.addLayout(pass_layout)
        layout.addWidget(password_group)
        
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
        
        self.decrypt_btn = QPushButton("Decrypt PDF")
        self.decrypt_btn.setEnabled(False)
        self.decrypt_btn.clicked.connect(self._decrypt_pdf)
        self.decrypt_btn.setMinimumWidth(150)
        self.decrypt_btn.setMinimumHeight(40)
        button_layout.addWidget(self.decrypt_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def _browse_file(self):
        """Browse for input PDF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Encrypted PDF File",
            str(Path.home()),
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.input_file = file_path
            self.file_label.setText(Path(file_path).name)
            
            # Set default output path
            input_path = Path(file_path)
            output_path = input_path.parent / f"{input_path.stem}_decrypted.pdf"
            self.output_label.setText(str(output_path))
            
            self.decrypt_btn.setEnabled(True)
            logger.info(f"Selected file: {file_path}")
    
    def _browse_output(self):
        """Browse for output file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Decrypted PDF",
            self.output_label.text(),
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.output_label.setText(file_path)
    
    def _toggle_password_visibility(self, checked):
        """Toggle password visibility"""
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.password_input.setEchoMode(mode)
    
    def _decrypt_pdf(self):
        """Perform PDF decryption"""
        if not self.input_file:
            QMessageBox.warning(self, "No File", "Please select a PDF file first.")
            return
        
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "No Password", "Please enter the PDF password.")
            return
        
        try:
            output_path = self.output_label.text()
            
            # Show progress dialog
            progress = QProgressDialog("Decrypting PDF...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Perform decryption
            result = PDFSecurity.decrypt_pdf(
                self.input_file,
                output_path,
                password
            )
            
            progress.close()
            
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"PDF decrypted successfully!\n\nOutput file:\n{result}"
            )
            
            logger.info(f"Successfully decrypted PDF: {result}")
            
            # Clear password
            self.password_input.clear()
            
        except Exception as e:
            logger.error(f"Error decrypting PDF: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to decrypt PDF:\n{str(e)}\n\nPlease check if the password is correct."
            )
