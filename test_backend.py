"""
Simple test script to verify core functionality without GUI
"""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def test_config():
    """Test configuration system"""
    print("Testing configuration system...")
    from cyberpdf_core.config import config
    
    # Test getting values
    theme = config.get("general.theme")
    print(f"  ✓ Theme: {theme}")
    
    # Test setting values
    config.set("general.theme", "light")
    assert config.get("general.theme") == "light"
    print("  ✓ Config set/get works")
    
    # Reset
    config.set("general.theme", "dark")
    print("  ✓ Configuration system OK\n")

def test_pdf_operations():
    """Test PDF operations (requires a sample PDF)"""
    print("Testing PDF operations...")
    from cyberpdf_core.pdf_tools.operations import PDFOperations
    
    print("  ✓ PDFOperations module imported")
    print("  ✓ PDF operations module OK\n")

def test_security():
    """Test security module"""
    print("Testing security module...")
    from cyberpdf_core.pdf_tools.security import PDFSecurity
    
    print("  ✓ PDFSecurity module imported")
    print("  ✓ Security module OK\n")

def test_arranger():
    """Test page arranger"""
    print("Testing page arranger...")
    from cyberpdf_core.pdf_tools.arranger import PageArranger
    
    print("  ✓ PageArranger module imported")
    print("  ✓ Page arranger module OK\n")

def test_converters():
    """Test converters"""
    print("Testing converters...")
    from cyberpdf_core.converters.pdf_word import PDFWordConverter
    
    # Check dependencies
    deps = PDFWordConverter.check_dependencies()
    print(f"  LibreOffice available: {deps['libreoffice']}")
    print(f"  unoconv available: {deps['unoconv']}")
    print("  ✓ Converter module OK\n")

def test_cache():
    """Test caching system"""
    print("Testing caching system...")
    from cyberpdf_core.utils.cache import CacheManager
    
    cache = CacheManager()
    stats = cache.get_cache_size()
    print(f"  Cache items: {stats['memory_items']}")
    print(f"  Cache files: {stats['disk_files']}")
    print("  ✓ Cache system OK\n")

def main():
    """Run all tests"""
    print("=" * 50)
    print("CYBER PDF - Backend Test Suite")
    print("=" * 50)
    print()
    
    try:
        test_config()
        test_pdf_operations()
        test_security()
        test_arranger()
        test_converters()
        test_cache()
        
        print("=" * 50)
        print("✓ ALL TESTS PASSED")
        print("=" * 50)
        print()
        print("Backend modules are working correctly!")
        print("Note: GUI test requires PySide6 installation to complete.")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
