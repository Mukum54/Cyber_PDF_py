"""
Main application window
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QToolBar, QStatusBar, QLabel
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon
import logging

from ui.screens.home_dashboard import HomeDashboard
from cyberpdf_core.config import config

logger = logging.getLogger(__name__)


class CyberPDFMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("CYBER PDF")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Initialize UI
        self._setup_ui()
        self._setup_menubar()
        self._setup_toolbar()
        self._setup_statusbar()
        self._apply_theme()
        
        logger.info("Main window initialized")
    
    def _setup_ui(self):
        """Set up main window UI"""
        # Central widget with stacked layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Footer
        footer = QWidget()
        footer.setMaximumHeight(30)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(10, 5, 10, 5)
        
        footer_label = QLabel("CYBER PDF v1.0.0 | Open Source PDF Suite")
        footer_label.setStyleSheet("color: #718096; font-size: 11px;")
        footer_layout.addWidget(footer_label)
        
        footer_layout.addStretch()
        
        github_label = QLabel('<a href="https://github.com/Mukum54/Cyber_PDF_py" style="color: #00D9FF; text-decoration: none;">GitHub</a>')
        github_label.setOpenExternalLinks(True)
        github_label.setStyleSheet("font-size: 11px;")
        footer_layout.addWidget(github_label)
        
        main_layout.addWidget(footer)
        
        # Add home dashboard
        self.home_screen = HomeDashboard(self)
        self.stacked_widget.addWidget(self.home_screen)
        
        # Connect signals
        self.home_screen.tool_selected.connect(self._on_tool_selected)
    
    def _setup_menubar(self):
        """Set up menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open PDF...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        toggle_theme_action = QAction("Toggle &Theme", self)
        toggle_theme_action.setShortcut("Ctrl+T")
        toggle_theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(toggle_theme_action)
        
        fullscreen_action = QAction("&Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self):
        """Set up toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Home button
        home_action = QAction("Home", self)
        home_action.setShortcut("Ctrl+H")
        home_action.triggered.connect(self._go_home)
        toolbar.addAction(home_action)
        
        toolbar.addSeparator()
    
    def _setup_statusbar(self):
        """Set up status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.statusbar.addWidget(self.status_label)
    
    def _apply_theme(self):
        """Apply current theme"""
        theme = config.get("general.theme", "dark")
        
        if theme == "dark":
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
    
    def _apply_dark_theme(self):
        """Apply dark theme stylesheet"""
        stylesheet = """
        QMainWindow {
            background-color: #0F1419;
            color: #FFFFFF;
        }
        
        QMenuBar {
            background-color: #1A1F26;
            color: #FFFFFF;
            border-bottom: 1px solid #2D3748;
        }
        
        QMenuBar::item:selected {
            background-color: #242B34;
        }
        
        QMenu {
            background-color: #1A1F26;
            color: #FFFFFF;
            border: 1px solid #2D3748;
        }
        
        QMenu::item:selected {
            background-color: #00D9FF;
        }
        
        QToolBar {
            background-color: #1A1F26;
            border-bottom: 1px solid #2D3748;
            spacing: 8px;
            padding: 4px;
        }
        
        QStatusBar {
            background-color: #1A1F26;
            color: #A0AEC0;
            border-top: 1px solid #2D3748;
        }
        
        QPushButton {
            background-color: #00D9FF;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
        }
        
        QPushButton:hover {
            background-color: #00B8E6;
        }
        
        QPushButton:pressed {
            background-color: #0097C2;
        }
        """
        
        self.setStyleSheet(stylesheet)
    
    def _apply_light_theme(self):
        """Apply light theme stylesheet"""
        stylesheet = """
        QMainWindow {
            background-color: #FFFFFF;
            color: #1A202C;
        }
        
        QMenuBar {
            background-color: #F7FAFC;
            color: #1A202C;
            border-bottom: 1px solid #E2E8F0;
        }
        
        QMenuBar::item:selected {
            background-color: #EDF2F7;
        }
        
        QMenu {
            background-color: #FFFFFF;
            color: #1A202C;
            border: 1px solid #E2E8F0;
        }
        
        QMenu::item:selected {
            background-color: #0088CC;
            color: #FFFFFF;
        }
        
        QToolBar {
            background-color: #F7FAFC;
            border-bottom: 1px solid #E2E8F0;
        }
        
        QStatusBar {
            background-color: #F7FAFC;
            color: #4A5568;
            border-top: 1px solid #E2E8F0;
        }
        """
        
        self.setStyleSheet(stylesheet)
    
    def _on_open_file(self):
        """Handle open file action"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            logger.info(f"Opening file: {file_path}")
            self.status_label.setText(f"Opened: {file_path}")
    
    def _on_tool_selected(self, tool_name: str):
        """Handle tool selection from home screen"""
        logger.info(f"Tool selected: {tool_name}")
        self.status_label.setText(f"Selected tool: {tool_name}")
        
        # Navigate to appropriate tool screen
        if tool_name == "Split PDF":
            from ui.screens.split_pdf_screen import SplitPDFScreen
            if not hasattr(self, 'split_screen'):
                self.split_screen = SplitPDFScreen(self)
                self.split_screen.back_requested.connect(self._go_home)
                self.stacked_widget.addWidget(self.split_screen)
            self.stacked_widget.setCurrentWidget(self.split_screen)
            
        elif tool_name == "Merge PDFs":
            from ui.screens.merge_pdf_screen import MergePDFScreen
            if not hasattr(self, 'merge_screen'):
                self.merge_screen = MergePDFScreen(self)
                self.merge_screen.back_requested.connect(self._go_home)
                self.stacked_widget.addWidget(self.merge_screen)
            self.stacked_widget.setCurrentWidget(self.merge_screen)
            
        elif tool_name == "Encrypt PDF":
            from ui.screens.encrypt_pdf_screen import EncryptPDFScreen
            if not hasattr(self, 'encrypt_screen'):
                self.encrypt_screen = EncryptPDFScreen(self)
                self.encrypt_screen.back_requested.connect(self._go_home)
                self.stacked_widget.addWidget(self.encrypt_screen)
            self.stacked_widget.setCurrentWidget(self.encrypt_screen)
            
        elif tool_name == "Decrypt PDF":
            from ui.screens.decrypt_pdf_screen import DecryptPDFScreen
            if not hasattr(self, 'decrypt_screen'):
                self.decrypt_screen = DecryptPDFScreen(self)
                self.decrypt_screen.back_requested.connect(self._go_home)
                self.stacked_widget.addWidget(self.decrypt_screen)
            self.stacked_widget.setCurrentWidget(self.decrypt_screen)
            
        elif tool_name == "Watermark":
            from ui.screens.watermark_pdf_screen import WatermarkPDFScreen
            if not hasattr(self, 'watermark_screen'):
                self.watermark_screen = WatermarkPDFScreen(self)
                self.watermark_screen.back_requested.connect(self._go_home)
                self.stacked_widget.addWidget(self.watermark_screen)
            self.stacked_widget.setCurrentWidget(self.watermark_screen)
            
        elif tool_name == "Extract Text":
            from ui.screens.extract_text_screen import ExtractTextScreen
            if not hasattr(self, 'extract_text_screen'):
                self.extract_text_screen = ExtractTextScreen(self)
                self.extract_text_screen.back_requested.connect(self._go_home)
                self.stacked_widget.addWidget(self.extract_text_screen)
            self.stacked_widget.setCurrentWidget(self.extract_text_screen)
            
        elif tool_name == "Extract Images":
            from ui.screens.extract_images_screen import ExtractImagesScreen
            if not hasattr(self, 'extract_images_screen'):
                self.extract_images_screen = ExtractImagesScreen(self)
                self.extract_images_screen.back_requested.connect(self._go_home)
                self.stacked_widget.addWidget(self.extract_images_screen)
            self.stacked_widget.setCurrentWidget(self.extract_images_screen)
            
        elif tool_name == "Metadata":
            from ui.screens.metadata_screen import MetadataScreen
            if not hasattr(self, 'metadata_screen'):
                self.metadata_screen = MetadataScreen(self)
                self.metadata_screen.back_requested.connect(self._go_home)
                self.stacked_widget.addWidget(self.metadata_screen)
            self.stacked_widget.setCurrentWidget(self.metadata_screen)
            
        elif tool_name == "PDF to Word":
            from ui.screens.pdf_to_word_screen import PDFToWordScreen
            if not hasattr(self, 'pdf_to_word_screen'):
                self.pdf_to_word_screen = PDFToWordScreen(self)
                self.pdf_to_word_screen.back_requested.connect(self._go_home)
                self.stacked_widget.addWidget(self.pdf_to_word_screen)
            self.stacked_widget.setCurrentWidget(self.pdf_to_word_screen)
            
        elif tool_name == "Word to PDF":
            from ui.screens.word_to_pdf_screen import WordToPDFScreen
            if not hasattr(self, 'word_to_pdf_screen'):
                self.word_to_pdf_screen = WordToPDFScreen(self)
                self.word_to_pdf_screen.back_requested.connect(self._go_home)
                self.stacked_widget.addWidget(self.word_to_pdf_screen)
            self.stacked_widget.setCurrentWidget(self.word_to_pdf_screen)
            
        elif tool_name == "Rotate Pages":
            from ui.screens.rotate_pages_screen import RotatePagesScreen
            if not hasattr(self, 'rotate_screen'):
                self.rotate_screen = RotatePagesScreen(self)
                self.rotate_screen.back_requested.connect(self._go_home)
                self.stacked_widget.addWidget(self.rotate_screen)
            self.stacked_widget.setCurrentWidget(self.rotate_screen)
            
        elif tool_name == "PDF to Image":
            from ui.screens.pdf_to_image_screen import PDFToImageScreen
            if not hasattr(self, 'pdf_to_image_screen'):
                self.pdf_to_image_screen = PDFToImageScreen(self)
                self.pdf_to_image_screen.back_requested.connect(self._go_home)
                self.stacked_widget.addWidget(self.pdf_to_image_screen)
            self.stacked_widget.setCurrentWidget(self.pdf_to_image_screen)
            
        elif tool_name == "Arrange Pages":
            from ui.screens.arrange_pages_screen import ArrangePagesScreen
            if not hasattr(self, 'arrange_screen'):
                self.arrange_screen = ArrangePagesScreen(self)
                self.arrange_screen.back_requested.connect(self._go_home)
                self.stacked_widget.addWidget(self.arrange_screen)
            self.stacked_widget.setCurrentWidget(self.arrange_screen)
            
        else:
            # For other tools, show a message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                tool_name,
                f"{tool_name} screen coming soon!\n\nThis feature is being implemented."
            )
    
    def _go_home(self):
        """Navigate to home screen"""
        self.stacked_widget.setCurrentWidget(self.home_screen)
        self.status_label.setText("Ready")
    
    def _toggle_theme(self):
        """Toggle between dark and light theme"""
        current_theme = config.get("general.theme", "dark")
        new_theme = "light" if current_theme == "dark" else "dark"
        
        config.set("general.theme", new_theme)
        self._apply_theme()
        
        # Update home dashboard theme
        if hasattr(self, 'home_screen'):
            self.home_screen.apply_theme()
        
        logger.info(f"Theme changed to: {new_theme}")
    
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def _show_about(self):
        """Show about dialog"""
        from PySide6.QtWidgets import QMessageBox
        
        QMessageBox.about(
            self,
            "About CYBER PDF",
            "<h2>CYBER PDF</h2>"
            "<p>Version 1.0.0</p>"
            "<p>Professional PDF Operations Suite for Linux</p>"
            "<p>Copyright © 2024 CYBER PDF Team</p>"
            "<p>Licensed under GPL v3</p>"
        )
