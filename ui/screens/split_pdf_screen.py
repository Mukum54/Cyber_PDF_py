"""
PDF Split tool screen
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QSpinBox, QComboBox, QGroupBox,
    QLineEdit, QMessageBox, QProgressDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging
from pathlib import Path

from cyberpdf_core.pdf_tools.operations import PDFOperations

logger = logging.getLogger(__name__)


class SplitPDFScreen(QWidget):
    """Screen for splitting PDF files"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.input_file = None
        self._setup_ui()
        logger.info("Split PDF screen initialized")
    
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
        
        title = QLabel("Split PDF")
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
        
        # Split options
        options_group = QGroupBox("Split Options")
        options_layout = QVBoxLayout(options_group)
        
        # Split mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Split Mode:"))
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Split into N-page chunks",
            "Split at specific pages",
            "Split by bookmarks",
            "Smart split (auto-detect)"
        ])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        
        options_layout.addLayout(mode_layout)
        
        # Pages per chunk
        self.chunk_layout = QHBoxLayout()
        self.chunk_layout.addWidget(QLabel("Pages per chunk:"))
        
        self.chunk_spin = QSpinBox()
        self.chunk_spin.setMinimum(1)
        self.chunk_spin.setMaximum(1000)
        self.chunk_spin.setValue(10)
        self.chunk_layout.addWidget(self.chunk_spin)
        self.chunk_layout.addStretch()
        
        options_layout.addLayout(self.chunk_layout)
        
        # Page numbers (hidden by default)
        self.pages_layout = QHBoxLayout()
        self.pages_label = QLabel("Page numbers (e.g., 5,10,15):")
        self.pages_layout.addWidget(self.pages_label)
        
        self.pages_input = QLineEdit()
        self.pages_input.setPlaceholderText("5,10,15")
        self.pages_layout.addWidget(self.pages_input)
        
        options_layout.addLayout(self.pages_layout)
        self.pages_label.hide()
        self.pages_input.hide()
        
        layout.addWidget(options_group)
        
        # Output directory
        output_group = QGroupBox("Output Directory")
        output_layout = QHBoxLayout(output_group)
        
        self.output_label = QLabel(str(Path.home() / "Documents"))
        output_layout.addWidget(self.output_label)
        
        output_btn = QPushButton("Change...")
        output_btn.clicked.connect(self._browse_output)
        output_layout.addWidget(output_btn)
        
        layout.addWidget(output_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.split_btn = QPushButton("Split PDF")
        self.split_btn.setEnabled(False)
        self.split_btn.clicked.connect(self._split_pdf)
        self.split_btn.setMinimumWidth(150)
        self.split_btn.setMinimumHeight(40)
        button_layout.addWidget(self.split_btn)
        
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
            self.split_btn.setEnabled(True)
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
            logger.info(f"Selected output directory: {dir_path}")
    
    def _on_mode_changed(self, index):
        """Handle split mode change"""
        # Get the parent widgets
        chunk_widget = self.chunk_spin.parentWidget()
        
        # Hide all mode-specific options
        if chunk_widget:
            for i in range(chunk_widget.layout().count()):
                item = chunk_widget.layout().itemAt(i)
                if item.widget():
                    item.widget().hide()
        
        self.pages_label.hide()
        self.pages_input.hide()
        
        # Show relevant options
        if index == 0:  # N-page chunks
            if chunk_widget:
                for i in range(chunk_widget.layout().count()):
                    item = chunk_widget.layout().itemAt(i)
                    if item.widget():
                        item.widget().show()
        elif index == 1:  # Specific pages
            self.pages_label.show()
            self.pages_input.show()
    
    def _split_pdf(self):
        """Perform PDF split operation"""
        if not self.input_file:
            QMessageBox.warning(self, "No File", "Please select a PDF file first.")
            return
        
        try:
            mode_index = self.mode_combo.currentIndex()
            output_dir = self.output_label.text()
            
            # Determine split mode and parameters
            if mode_index == 0:  # N-page chunks
                mode = "by_count"
                kwargs = {"count": self.chunk_spin.value()}
            elif mode_index == 1:  # Specific pages
                mode = "by_pages"
                pages_text = self.pages_input.text()
                pages = [int(p.strip()) - 1 for p in pages_text.split(",") if p.strip()]
                kwargs = {"pages": pages}
            elif mode_index == 2:  # Bookmarks
                mode = "by_bookmarks"
                kwargs = {}
            else:  # Smart
                mode = "smart"
                kwargs = {}
            
            # Show progress dialog
            progress = QProgressDialog("Splitting PDF...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Perform split
            output_files = PDFOperations.split_pdf(
                self.input_file,
                output_dir,
                split_mode=mode,
                **kwargs
            )
            
            progress.close()
            
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"PDF split into {len(output_files)} files!\n\nOutput directory:\n{output_dir}"
            )
            
            logger.info(f"Successfully split PDF into {len(output_files)} files")
            
        except Exception as e:
            logger.error(f"Error splitting PDF: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to split PDF:\n{str(e)}"
            )
