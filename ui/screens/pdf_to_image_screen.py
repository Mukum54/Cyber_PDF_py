"""
PDF to Image conversion screen
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QGroupBox, QMessageBox,
    QProgressDialog, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging
from pathlib import Path
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class PDFToImageScreen(QWidget):
    """Screen for converting PDF to images"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.input_file = None
        self._setup_ui()
        logger.info("PDF to Image screen initialized")
    
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
        
        title = QLabel("PDF to Image")
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
        
        # Format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Image Format:"))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG", "TIFF"])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        
        options_layout.addLayout(format_layout)
        
        # DPI/Quality
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("DPI (Quality):"))
        
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setMinimum(72)
        self.dpi_spin.setMaximum(600)
        self.dpi_spin.setValue(150)
        self.dpi_spin.setSuffix(" dpi")
        dpi_layout.addWidget(self.dpi_spin)
        dpi_layout.addStretch()
        
        options_layout.addLayout(dpi_layout)
        
        layout.addWidget(options_group)
        
        # Output directory
        output_group = QGroupBox("Output Directory")
        output_layout = QHBoxLayout(output_group)
        
        self.output_label = QLabel(str(Path.home() / "Documents" / "pdf_images"))
        output_layout.addWidget(self.output_label)
        
        output_btn = QPushButton("Change...")
        output_btn.clicked.connect(self._browse_output)
        output_layout.addWidget(output_btn)
        
        layout.addWidget(output_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.convert_btn = QPushButton("Convert to Images")
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self._convert_pdf)
        self.convert_btn.setMinimumWidth(150)
        self.convert_btn.setMinimumHeight(40)
        button_layout.addWidget(self.convert_btn)
        
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
            self.convert_btn.setEnabled(True)
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
    
    def _convert_pdf(self):
        """Convert PDF to images"""
        if not self.input_file:
            return
        
        try:
            output_dir = Path(self.output_label.text())
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Get options
            image_format = self.format_combo.currentText().lower()
            dpi = self.dpi_spin.value()
            
            # Show progress dialog
            progress = QProgressDialog("Converting PDF to images...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Open PDF
            doc = fitz.open(self.input_file)
            
            # Convert each page
            output_files = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Render page to image
                zoom = dpi / 72  # 72 is default DPI
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Save image
                output_file = output_dir / f"page_{page_num + 1:03d}.{image_format}"
                pix.save(str(output_file))
                output_files.append(str(output_file))
            
            doc.close()
            progress.close()
            
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Converted {len(output_files)} pages to images!\n\nOutput directory:\n{output_dir}"
            )
            
            logger.info(f"Converted {len(output_files)} pages to images")
            
        except Exception as e:
            logger.error(f"Error converting PDF: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to convert PDF:\n{str(e)}"
            )
