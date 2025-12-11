"""
PDF Encryption tool screen
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


class EncryptPDFScreen(QWidget):
    """Screen for encrypting PDF files"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.input_file = None
        self._setup_ui()
        logger.info("Encrypt PDF screen initialized")
    
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
        
        title = QLabel("Encrypt PDF")
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
        
        # Password settings
        password_group = QGroupBox("Password Settings")
        password_layout = QVBoxLayout(password_group)
        
        # User password
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("User Password:"))
        
        self.user_password = QLineEdit()
        self.user_password.setEchoMode(QLineEdit.Password)
        self.user_password.setPlaceholderText("Enter password to open PDF")
        user_layout.addWidget(self.user_password)
        
        self.show_password = QCheckBox("Show")
        self.show_password.toggled.connect(self._toggle_password_visibility)
        user_layout.addWidget(self.show_password)
        
        password_layout.addLayout(user_layout)
        
        # Confirm password
        confirm_layout = QHBoxLayout()
        confirm_layout.addWidget(QLabel("Confirm Password:"))
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Re-enter password")
        confirm_layout.addWidget(self.confirm_password)
        confirm_layout.addWidget(QLabel(""))  # Spacer for alignment
        
        password_layout.addLayout(confirm_layout)
        
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
        
        self.encrypt_btn = QPushButton("Encrypt PDF")
        self.encrypt_btn.setEnabled(False)
        self.encrypt_btn.clicked.connect(self._encrypt_pdf)
        self.encrypt_btn.setMinimumWidth(150)
        self.encrypt_btn.setMinimumHeight(40)
        button_layout.addWidget(self.encrypt_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
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
            output_path = input_path.parent / f"{input_path.stem}_encrypted.pdf"
            self.output_label.setText(str(output_path))
            
            self.encrypt_btn.setEnabled(True)
            logger.info(f"Selected file: {file_path}")
    
    def _browse_output(self):
        """Browse for output file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Encrypted PDF",
            self.output_label.text(),
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.output_label.setText(file_path)
    
    def _toggle_password_visibility(self, checked):
        """Toggle password visibility"""
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.user_password.setEchoMode(mode)
        self.confirm_password.setEchoMode(mode)
    
    def _encrypt_pdf(self):
        """Perform PDF encryption"""
        if not self.input_file:
            QMessageBox.warning(self, "No File", "Please select a PDF file first.")
            return
        
        # Validate passwords
        password = self.user_password.text()
        confirm = self.confirm_password.text()
        
        if not password:
            QMessageBox.warning(self, "No Password", "Please enter a password.")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match.")
            return
        
        if len(password) < 4:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 4 characters long.")
            return
        
        try:
            output_path = self.output_label.text()
            
            # Show progress dialog
            progress = QProgressDialog("Encrypting PDF...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Perform encryption
            result = PDFSecurity.encrypt_pdf(
                self.input_file,
                output_path,
                password
            )
            
            progress.close()
            
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"PDF encrypted successfully!\n\nOutput file:\n{result}\n\nPassword: {password}"
            )
            
            logger.info(f"Successfully encrypted PDF: {result}")
            
            # Clear passwords
            self.user_password.clear()
            self.confirm_password.clear()
            
        except Exception as e:
            logger.error(f"Error encrypting PDF: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to encrypt PDF:\n{str(e)}"
            )
