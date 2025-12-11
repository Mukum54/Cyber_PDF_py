"""
Extract Images tool screen
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QGroupBox, QMessageBox,
    QProgressDialog, QListWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging
from pathlib import Path

from cyberpdf_core.pdf_tools.operations import PDFOperations

logger = logging.getLogger(__name__)


class ExtractImagesScreen(QWidget):
    """Screen for extracting images from PDF"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.input_file = None
        self.extracted_images = []
        self._setup_ui()
        logger.info("Extract Images screen initialized")
    
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
        
        title = QLabel("Extract Images")
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
        
        # Extracted images list
        images_group = QGroupBox("Extracted Images")
        images_layout = QVBoxLayout(images_group)
        
        self.images_list = QListWidget()
        self.images_list.setMinimumHeight(300)
        images_layout.addWidget(self.images_list)
        
        layout.addWidget(images_group)
        
        # Output directory
        output_group = QGroupBox("Output Directory")
        output_layout = QHBoxLayout(output_group)
        
        self.output_label = QLabel(str(Path.home() / "Documents" / "extracted_images"))
        output_layout.addWidget(self.output_label)
        
        output_btn = QPushButton("Change...")
        output_btn.clicked.connect(self._browse_output)
        output_layout.addWidget(output_btn)
        
        layout.addWidget(output_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.extract_btn = QPushButton("Extract Images")
        self.extract_btn.setEnabled(False)
        self.extract_btn.clicked.connect(self._extract_images)
        self.extract_btn.setMinimumWidth(150)
        self.extract_btn.setMinimumHeight(40)
        button_layout.addWidget(self.extract_btn)
        
        self.open_folder_btn = QPushButton("Open Folder")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self._open_folder)
        self.open_folder_btn.setMinimumWidth(150)
        self.open_folder_btn.setMinimumHeight(40)
        button_layout.addWidget(self.open_folder_btn)
        
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
            self.images_list.clear()
            self.extracted_images = []
            self.open_folder_btn.setEnabled(False)
            logger.info(f"Selected file: {file_path}")
    
    def _browse_output(self):
        """Browse for output directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            str(Path.home())
        )
        
        if dir_path:
            self.output_label.setText(dir_path)
    
    def _extract_images(self):
        """Extract images from PDF"""
        if not self.input_file:
            return
        
        try:
            output_dir = self.output_label.text()
            
            # Show progress dialog
            progress = QProgressDialog("Extracting images...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Extract images
            self.extracted_images = PDFOperations.extract_images(self.input_file, output_dir)
            
            progress.close()
            
            # Display images in list
            self.images_list.clear()
            for img_path in self.extracted_images:
                self.images_list.addItem(Path(img_path).name)
            
            self.open_folder_btn.setEnabled(True)
            
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Extracted {len(self.extracted_images)} images!\n\nOutput directory:\n{output_dir}"
            )
            
            logger.info(f"Extracted {len(self.extracted_images)} images from {self.input_file}")
            
        except Exception as e:
            logger.error(f"Error extracting images: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to extract images:\n{str(e)}"
            )
    
    def _open_folder(self):
        """Open output folder"""
        import subprocess
        import platform
        
        output_dir = self.output_label.text()
        
        try:
            if platform.system() == "Linux":
                subprocess.run(["xdg-open", output_dir])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", output_dir])
            elif platform.system() == "Windows":
                subprocess.run(["explorer", output_dir])
        except Exception as e:
            logger.error(f"Error opening folder: {e}")
            QMessageBox.warning(self, "Error", f"Could not open folder:\n{str(e)}")
