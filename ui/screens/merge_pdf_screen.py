"""
PDF Merge tool screen
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QListWidget, QGroupBox,
    QMessageBox, QProgressDialog, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging
from pathlib import Path

from cyberpdf_core.pdf_tools.operations import PDFOperations

logger = logging.getLogger(__name__)


class MergePDFScreen(QWidget):
    """Screen for merging PDF files"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.pdf_files = []
        self._setup_ui()
        logger.info("Merge PDF screen initialized")
    
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
        
        title = QLabel("Merge PDFs")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # File list
        files_group = QGroupBox("PDF Files to Merge")
        files_layout = QVBoxLayout(files_group)
        
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(300)
        files_layout.addWidget(self.file_list)
        
        # File buttons
        file_buttons = QHBoxLayout()
        
        add_btn = QPushButton("Add Files...")
        add_btn.clicked.connect(self._add_files)
        file_buttons.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_selected)
        file_buttons.addWidget(remove_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_all)
        file_buttons.addWidget(clear_btn)
        
        file_buttons.addStretch()
        
        move_up_btn = QPushButton("Move Up")
        move_up_btn.clicked.connect(self._move_up)
        file_buttons.addWidget(move_up_btn)
        
        move_down_btn = QPushButton("Move Down")
        move_down_btn.clicked.connect(self._move_down)
        file_buttons.addWidget(move_down_btn)
        
        files_layout.addLayout(file_buttons)
        layout.addWidget(files_group)
        
        # Output file
        output_group = QGroupBox("Output File")
        output_layout = QHBoxLayout(output_group)
        
        self.output_label = QLabel(str(Path.home() / "Documents" / "merged.pdf"))
        output_layout.addWidget(self.output_label)
        
        output_btn = QPushButton("Change...")
        output_btn.clicked.connect(self._browse_output)
        output_layout.addWidget(output_btn)
        
        layout.addWidget(output_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.merge_btn = QPushButton("Merge PDFs")
        self.merge_btn.setEnabled(False)
        self.merge_btn.clicked.connect(self._merge_pdfs)
        self.merge_btn.setMinimumWidth(150)
        self.merge_btn.setMinimumHeight(40)
        button_layout.addWidget(self.merge_btn)
        
        layout.addLayout(button_layout)
    
    def _add_files(self):
        """Add PDF files to merge"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files",
            str(Path.home()),
            "PDF Files (*.pdf)"
        )
        
        for file_path in file_paths:
            if file_path not in self.pdf_files:
                self.pdf_files.append(file_path)
                self.file_list.addItem(Path(file_path).name)
        
        self.merge_btn.setEnabled(len(self.pdf_files) >= 2)
        logger.info(f"Added {len(file_paths)} files, total: {len(self.pdf_files)}")
    
    def _remove_selected(self):
        """Remove selected files"""
        selected_items = self.file_list.selectedItems()
        for item in selected_items:
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
            del self.pdf_files[row]
        
        self.merge_btn.setEnabled(len(self.pdf_files) >= 2)
    
    def _clear_all(self):
        """Clear all files"""
        self.file_list.clear()
        self.pdf_files.clear()
        self.merge_btn.setEnabled(False)
    
    def _move_up(self):
        """Move selected file up"""
        current_row = self.file_list.currentRow()
        if current_row > 0:
            item = self.file_list.takeItem(current_row)
            self.file_list.insertItem(current_row - 1, item)
            self.file_list.setCurrentRow(current_row - 1)
            
            self.pdf_files[current_row], self.pdf_files[current_row - 1] = \
                self.pdf_files[current_row - 1], self.pdf_files[current_row]
    
    def _move_down(self):
        """Move selected file down"""
        current_row = self.file_list.currentRow()
        if current_row < self.file_list.count() - 1:
            item = self.file_list.takeItem(current_row)
            self.file_list.insertItem(current_row + 1, item)
            self.file_list.setCurrentRow(current_row + 1)
            
            self.pdf_files[current_row], self.pdf_files[current_row + 1] = \
                self.pdf_files[current_row + 1], self.pdf_files[current_row]
    
    def _browse_output(self):
        """Browse for output file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged PDF",
            str(Path.home() / "Documents" / "merged.pdf"),
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.output_label.setText(file_path)
    
    def _merge_pdfs(self):
        """Perform PDF merge operation"""
        if len(self.pdf_files) < 2:
            QMessageBox.warning(self, "Not Enough Files", "Please add at least 2 PDF files to merge.")
            return
        
        try:
            output_path = self.output_label.text()
            
            # Show progress dialog
            progress = QProgressDialog("Merging PDFs...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Perform merge
            result = PDFOperations.merge_pdfs(self.pdf_files, output_path)
            
            progress.close()
            
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Successfully merged {len(self.pdf_files)} PDFs!\n\nOutput file:\n{result}"
            )
            
            logger.info(f"Successfully merged {len(self.pdf_files)} PDFs to {result}")
            
            # Clear the list
            self._clear_all()
            
        except Exception as e:
            logger.error(f"Error merging PDFs: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to merge PDFs:\n{str(e)}"
            )
