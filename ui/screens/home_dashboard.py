"""
Home dashboard screen with tool cards
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QPalette, QColor
import logging

from cyberpdf_core.config import config

logger = logging.getLogger(__name__)


class ToolCard(QFrame):
    """Interactive tool card widget"""
    
    clicked = Signal(str)  # Emits tool name when clicked
    
    def __init__(self, tool_name: str, icon: str, description: str, parent=None):
        super().__init__(parent)
        
        self.tool_name = tool_name
        self.setFixedSize(220, 200)
        self.setCursor(Qt.PointingHandCursor)
        
        # Set up UI
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon label
        self.icon_label = QLabel(icon)
        icon_font = QFont()
        icon_font.setPointSize(56)
        self.icon_label.setFont(icon_font)
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)
        
        # Tool name
        self.name_label = QLabel(tool_name)
        name_font = QFont()
        name_font.setPointSize(15)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        self.name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.name_label)
        
        # Description
        self.desc_label = QLabel(description)
        desc_font = QFont()
        desc_font.setPointSize(11)
        self.desc_label.setFont(desc_font)
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)
        
        # Apply theme
        self.apply_theme()
        
        # Animation for hover effect
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        
        self.original_geometry = None
    
    def apply_theme(self):
        """Apply theme-aware styling"""
        theme = config.get("general.theme", "dark")
        
        if theme == "dark":
            self.setStyleSheet("""
                ToolCard {
                    background-color: #1A1F26;
                    border: 2px solid #2D3748;
                    border-radius: 16px;
                }
                ToolCard:hover {
                    border: 2px solid #00D9FF;
                    background-color: #242B34;
                }
                QLabel {
                    color: #FFFFFF;
                }
            """)
            self.desc_label.setStyleSheet("color: #A0AEC0;")
        else:
            self.setStyleSheet("""
                ToolCard {
                    background-color: #FFFFFF;
                    border: 2px solid #E2E8F0;
                    border-radius: 16px;
                }
                ToolCard:hover {
                    border: 2px solid #0088CC;
                    background-color: #F7FAFC;
                }
                QLabel {
                    color: #1A202C;
                }
            """)
            self.desc_label.setStyleSheet("color: #718096;")
    
    def enterEvent(self, event):
        """Handle mouse enter (hover)"""
        if self.original_geometry is None:
            self.original_geometry = self.geometry()
        
        # Lift effect
        lifted_geometry = QRect(
            self.original_geometry.x(),
            self.original_geometry.y() - 6,
            self.original_geometry.width(),
            self.original_geometry.height()
        )
        
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(lifted_geometry)
        self.animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave"""
        if self.original_geometry:
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(self.original_geometry)
            self.animation.start()
        
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.tool_name)
        super().mousePressEvent(event)


class HomeDashboard(QWidget):
    """Home dashboard with tool cards"""
    
    tool_selected = Signal(str)  # Emits tool name when selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.tool_cards = []
        self._setup_ui()
        logger.info("Home dashboard initialized")
    
    def _setup_ui(self):
        """Set up UI layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Title
        self.title_label = QLabel("CYBER PDF")
        title_font = QFont()
        title_font.setPointSize(36)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)
        
        # Subtitle
        self.subtitle_label = QLabel("Professional PDF Operations Suite for Linux")
        subtitle_font = QFont()
        subtitle_font.setPointSize(15)
        self.subtitle_label.setFont(subtitle_font)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.subtitle_label)
        
        # Scroll area for tool cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(40)
        
        # CONVERT section
        self._add_section(scroll_layout, "CONVERT", [
            ("PDF to Word", "📄→📝", "Convert PDF to DOCX"),
            ("Word to PDF", "📝→📄", "Convert DOCX to PDF"),
            ("PDF to Image", "📄→🖼️", "Export pages as images"),
        ])
        
        # EDIT section
        self._add_section(scroll_layout, "EDIT", [
            ("Split PDF", "✂️", "Split PDF into parts"),
            ("Merge PDFs", "🔗", "Combine multiple PDFs"),
            ("Arrange Pages", "🔄", "Reorder and organize pages"),
            ("Rotate Pages", "↻", "Rotate PDF pages"),
        ])
        
        # SECURE section
        self._add_section(scroll_layout, "SECURE", [
            ("Encrypt PDF", "🔒", "Password protect PDF"),
            ("Decrypt PDF", "🔓", "Remove password"),
            ("Watermark", "💧", "Add text watermark"),
        ])
        
        # ANALYZE section
        self._add_section(scroll_layout, "ANALYZE", [
            ("Extract Text", "📝", "Extract text content"),
            ("Extract Images", "🖼️", "Extract all images"),
            ("Metadata", "📊", "View and edit metadata"),
        ])
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Apply theme
        self.apply_theme()
    
    def _add_section(self, layout, section_name: str, tools: list):
        """Add a section with tool cards"""
        # Section header
        section_label = QLabel(section_name)
        section_font = QFont()
        section_font.setPointSize(18)
        section_font.setBold(True)
        section_label.setFont(section_font)
        section_label.setObjectName("section_header")
        layout.addWidget(section_label)
        
        # Tool cards grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(25)
        
        for i, (name, icon, desc) in enumerate(tools):
            card = ToolCard(name, icon, desc)
            card.clicked.connect(self.tool_selected.emit)
            self.tool_cards.append(card)
            
            row = i // 3
            col = i % 3
            grid_layout.addWidget(card, row, col)
        
        layout.addLayout(grid_layout)
    
    def apply_theme(self):
        """Apply theme to all elements"""
        theme = config.get("general.theme", "dark")
        
        if theme == "dark":
            self.title_label.setStyleSheet("color: #FFFFFF;")
            self.subtitle_label.setStyleSheet("color: #A0AEC0;")
            
            # Update section headers
            for label in self.findChildren(QLabel):
                if label.objectName() == "section_header":
                    label.setStyleSheet("color: #00D9FF; margin-top: 20px;")
        else:
            self.title_label.setStyleSheet("color: #1A202C;")
            self.subtitle_label.setStyleSheet("color: #4A5568;")
            
            # Update section headers
            for label in self.findChildren(QLabel):
                if label.objectName() == "section_header":
                    label.setStyleSheet("color: #0088CC; margin-top: 20px;")
        
        # Update all tool cards
        for card in self.tool_cards:
            card.apply_theme()
