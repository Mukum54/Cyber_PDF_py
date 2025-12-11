"""
Rotate Pages tool screen
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

from cyberpdf_core.pdf_tools.operations import PDFOperations

logger = logging.getLogger(__name__)


class RotatePagesScreen(QWidget):
    """Screen for rotating PDF pages"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.input_file = None
        self._setup_ui()
        logger.info("Rotate Pages screen initialized")
    
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
        
        title = QLabel("Rotate Pages")
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
        
        # Rotation options
        options_group = QGroupBox("Rotation Options")
        options_layout = QVBoxLayout(options_group)
        
        # Angle
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("Rotation Angle:"))
        
        self.angle_combo = QComboBox()
        self.angle_combo.addItems(["90° Clockwise", "180°", "270° Clockwise (90° Counter)"])
        angle_layout.addWidget(self.angle_combo)
        angle_layout.addStretch()
        
        options_layout.addLayout(angle_layout)
        
        # Pages
        pages_layout = QHBoxLayout()
        pages_layout.addWidget(QLabel("Apply to:"))
        
        self.pages_combo = QComboBox()
        self.pages_combo.addItems(["All Pages", "Specific Pages"])
        self.pages_combo.currentIndexChanged.connect(self._on_pages_changed)
        pages_layout.addWidget(self.pages_combo)
        pages_layout.addStretch()
        
        options_layout.addLayout(pages_layout)
        
        # Specific pages input (hidden by default)
        self.specific_pages_layout = QHBoxLayout()
        self.specific_pages_layout.addWidget(QLabel("Page numbers (e.g., 1,3,5-10):"))
        
        self.pages_input = QLineEdit()
        self.pages_input.setPlaceholderText("1,3,5-10")
        self.specific_pages_layout.addWidget(self.pages_input)
        
        options_layout.addLayout(self.specific_pages_layout)
        self.pages_input.hide()
        self.specific_pages_layout.itemAt(0).widget().hide()
        
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
        
        self.rotate_btn = QPushButton("Rotate Pages")
        self.rotate_btn.setEnabled(False)
        self.rotate_btn.clicked.connect(self._rotate_pages)
        self.rotate_btn.setMinimumWidth(150)
        self.rotate_btn.setMinimumHeight(40)
        button_layout.addWidget(self.rotate_btn)
        
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
            output_path = input_path.parent / f"{input_path.stem}_rotated.pdf"
            self.output_label.setText(str(output_path))
            
            self.rotate_btn.setEnabled(True)
            logger.info(f"Selected file: {file_path}")
    
    def _browse_output(self):
        """Browse for output file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Rotated PDF",
            self.output_label.text(),
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.output_label.setText(file_path)
    
    def _on_pages_changed(self, index):
        """Handle pages selection change"""
        if index == 1:  # Specific pages
            self.pages_input.show()
            self.specific_pages_layout.itemAt(0).widget().show()
        else:
            self.pages_input.hide()
            self.specific_pages_layout.itemAt(0).widget().hide()
    
    def _rotate_pages(self):
        """Rotate PDF pages"""
        if not self.input_file:
            return
        
        try:
            output_path = self.output_label.text()
            
            # Get rotation angle
            angle_index = self.angle_combo.currentIndex()
            angles = [90, 180, 270]
            angle = angles[angle_index]
            
            # Get pages to rotate
            pages = None
            if self.pages_combo.currentIndex() == 1:  # Specific pages
                pages_text = self.pages_input.text()
                if not pages_text:
                    QMessageBox.warning(self, "No Pages", "Please enter page numbers.")
                    return
                
                # Parse page numbers
                pages = []
                for part in pages_text.split(","):
                    if "-" in part:
                        start, end = map(int, part.split("-"))
                        pages.extend(range(start - 1, end))
                    else:
                        pages.append(int(part) - 1)
            
            # Show progress dialog
            progress = QProgressDialog("Rotating pages...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Perform rotation
            result = PDFOperations.rotate_pages(
                self.input_file,
                output_path,
                angle,
                pages
            )
            
            progress.close()
            
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Pages rotated successfully!\n\nOutput file:\n{result}"
            )
            
            logger.info(f"Successfully rotated pages: {result}")
            
        except Exception as e:
            logger.error(f"Error rotating pages: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to rotate pages:\n{str(e)}"
            )


# Import QLineEdit
from PySide6.QtWidgets import QLineEdit
