"""
Main application entry point
"""
import sys
import logging
from pathlib import Path

# Ensure log directory exists
log_dir = Path.home() / ".config/cyberpdf"
log_dir.mkdir(parents=True, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_dir / "cyberpdf.log")
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point"""
    try:
        from PySide6.QtWidgets import QApplication
        from ui.main_window import CyberPDFMainWindow
        
        logger.info("Starting CYBER PDF application")
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("CYBER PDF")
        app.setOrganizationName("CYBER PDF Team")
        app.setApplicationVersion("1.0.0")
        
        # Create and show main window
        window = CyberPDFMainWindow()
        window.show()
        
        # Run application
        sys.exit(app.exec())
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        print("Error: PySide6 is required. Install with: pip install PySide6")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
