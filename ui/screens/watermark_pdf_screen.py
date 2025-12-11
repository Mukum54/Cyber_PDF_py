"""
PDF Watermark tool screen
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QLineEdit, QGroupBox,
    QMessageBox, QProgressDialog, QComboBox, QSlider
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging
from pathlib import Path

from cyberpdf_core.pdf_tools.security import PDFSecurity

logger = logging.getLogger(__name__)


class WatermarkPDFScreen(QWidget):
    """Screen for adding watermarks to PDF"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.input_file = None
        self._setup_ui()
        logger.info("Watermark PDF screen initialized")
    
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
        
        title = QLabel("Add Watermark")
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
        
        # Watermark settings
        settings_group = QGroupBox("Watermark Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Watermark text
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Watermark Text:"))
        
        self.watermark_text = QLineEdit()
        self.watermark_text.setPlaceholderText("Enter watermark text (e.g., CONFIDENTIAL)")
        text_layout.addWidget(self.watermark_text)
        
        settings_layout.addLayout(text_layout)
        
        # Position
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("Position:"))
        
        self.position_combo = QComboBox()
        self.position_combo.addItems(["Center", "Diagonal", "Top", "Bottom"])
        position_layout.addWidget(self.position_combo)
        position_layout.addStretch()
        
        settings_layout.addLayout(position_layout)
        
        # Opacity
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(10)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(30)
        self.opacity_slider.valueChanged.connect(self._update_opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        
        self.opacity_label = QLabel("30%")
        opacity_layout.addWidget(self.opacity_label)
        
        settings_layout.addLayout(opacity_layout)
        
        # Rotation
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(QLabel("Rotation:"))
        
        self.rotation_combo = QComboBox()
        self.rotation_combo.addItems(["0°", "90°", "180°", "270°"])
        rotation_layout.addWidget(self.rotation_combo)
        rotation_layout.addStretch()
        
        settings_layout.addLayout(rotation_layout)
        
        layout.addWidget(settings_group)
        
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
        
        self.watermark_btn = QPushButton("Add Watermark")
        self.watermark_btn.setEnabled(False)
        self.watermark_btn.clicked.connect(self._add_watermark)
        self.watermark_btn.setMinimumWidth(150)
        self.watermark_btn.setMinimumHeight(40)
        button_layout.addWidget(self.watermark_btn)
        
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
            output_path = input_path.parent / f"{input_path.stem}_watermarked.pdf"
            self.output_label.setText(str(output_path))
            
            self.watermark_btn.setEnabled(True)
            logger.info(f"Selected file: {file_path}")
    
    def _browse_output(self):
        """Browse for output file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Watermarked PDF",
            self.output_label.text(),
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.output_label.setText(file_path)
    
    def _update_opacity_label(self, value):
        """Update opacity label"""
        self.opacity_label.setText(f"{value}%")
    
    def _add_watermark(self):
        """Add watermark to PDF"""
        if not self.input_file:
            QMessageBox.warning(self, "No File", "Please select a PDF file first.")
            return
        
        watermark_text = self.watermark_text.text()
        if not watermark_text:
            QMessageBox.warning(self, "No Text", "Please enter watermark text.")
            return
        
        try:
            output_path = self.output_label.text()
            position = self.position_combo.currentText().lower()
            opacity = self.opacity_slider.value() / 100.0
            
            # Show progress dialog
            progress = QProgressDialog("Adding watermark...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Get rotation value
            rotation_text = self.rotation_combo.currentText()
            rotation = int(rotation_text.replace("°", ""))
            
            # Add watermark
            result = PDFSecurity.add_watermark(
                self.input_file,
                output_path,
                watermark_text,
                position=position,
                opacity=opacity,
                rotation=rotation
            )
            
            progress.close()
            
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Watermark added successfully!\n\nOutput file:\n{result}"
            )
            
            logger.info(f"Successfully added watermark to PDF: {result}")
            
        except Exception as e:
            logger.error(f"Error adding watermark: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to add watermark:\n{str(e)}"
            )
