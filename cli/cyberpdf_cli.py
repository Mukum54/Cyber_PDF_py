"""
Command-line interface for CYBER PDF
"""
import click
import logging
from pathlib import Path
from typing import List

from cyberpdf_core.pdf_tools.operations import PDFOperations
from cyberpdf_core.pdf_tools.security import PDFSecurity
from cyberpdf_core.converters.pdf_word import PDFWordConverter

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="1.0.0", prog_name="CYBER PDF CLI")
def cli():
    """CYBER PDF - Professional PDF operations suite"""
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--pages", help="Page range (e.g., 1-5,7,9-12)")
@click.option("--count", type=int, help="Pages per file")
@click.option("--mode", type=click.Choice(["by_pages", "by_count", "by_bookmarks", "smart"]), 
              default="by_count", help="Split mode")
@click.option("--output-dir", "-o", default="./output", help="Output directory")
def split(input_file, pages, count, mode, output_dir):
    """Split PDF into multiple files"""
    try:
        kwargs = {}
        
        if mode == "by_pages" and pages:
            # Parse page ranges
            page_list = []
            for part in pages.split(","):
                if "-" in part:
                    start, end = map(int, part.split("-"))
                    page_list.extend(range(start - 1, end))
                else:
                    page_list.append(int(part) - 1)
            kwargs["pages"] = page_list
        elif mode == "by_count":
            kwargs["count"] = count or 10
        
        output_files = PDFOperations.split_pdf(
            input_file,
            output_dir,
            split_mode=mode,
            **kwargs
        )
        
        click.echo(f"✓ Split into {len(output_files)} files:")
        for file in output_files:
            click.echo(f"  - {file}")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("input_files", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--output", "-o", required=True, help="Output PDF file")
def merge(input_files, output):
    """Merge multiple PDFs into one"""
    try:
        result = PDFOperations.merge_pdfs(list(input_files), output)
        click.echo(f"✓ Merged {len(input_files)} files into {result}")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--to", "target_format", type=click.Choice(["pdf", "docx", "word"]), 
              required=True, help="Target format")
@click.option("--output", "-o", help="Output file path")
def convert(input_file, target_format, output):
    """Convert between PDF and Word formats"""
    try:
        input_path = Path(input_file)
        
        # Determine output path
        if not output:
            if target_format in ["docx", "word"]:
                output = input_path.with_suffix(".docx")
            else:
                output = input_path.with_suffix(".pdf")
        
        # Perform conversion
        if target_format in ["docx", "word"]:
            result = PDFWordConverter.pdf_to_word(str(input_path), str(output))
            click.echo(f"✓ Converted PDF to Word: {result}")
        else:
            result = PDFWordConverter.word_to_pdf(str(input_path), str(output))
            click.echo(f"✓ Converted Word to PDF: {result}")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--password", prompt=True, hide_input=True, 
              confirmation_prompt=True, help="Encryption password")
@click.option("--output", "-o", help="Output PDF file")
def encrypt(input_file, password, output):
    """Encrypt PDF with password"""
    try:
        input_path = Path(input_file)
        
        if not output:
            output = input_path.with_stem(f"{input_path.stem}_encrypted")
        
        result = PDFSecurity.encrypt_pdf(str(input_path), str(output), password)
        click.echo(f"✓ Encrypted PDF saved to: {result}")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--password", prompt=True, hide_input=True, help="PDF password")
@click.option("--output", "-o", help="Output PDF file")
def decrypt(input_file, password, output):
    """Decrypt password-protected PDF"""
    try:
        input_path = Path(input_file)
        
        if not output:
            output = input_path.with_stem(f"{input_path.stem}_decrypted")
        
        result = PDFSecurity.decrypt_pdf(str(input_path), str(output), password)
        click.echo(f"✓ Decrypted PDF saved to: {result}")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--text", required=True, help="Watermark text")
@click.option("--position", type=click.Choice(["center", "top", "bottom", "diagonal"]), 
              default="center", help="Watermark position")
@click.option("--opacity", type=float, default=0.3, help="Opacity (0.0-1.0)")
@click.option("--output", "-o", help="Output PDF file")
def watermark(input_file, text, position, opacity, output):
    """Add text watermark to PDF"""
    try:
        input_path = Path(input_file)
        
        if not output:
            output = input_path.with_stem(f"{input_path.stem}_watermarked")
        
        result = PDFSecurity.add_watermark(
            str(input_path), 
            str(output), 
            text,
            position=position,
            opacity=opacity
        )
        click.echo(f"✓ Watermarked PDF saved to: {result}")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output", "-o", help="Output text file")
def extract_text(input_file, output):
    """Extract text from PDF"""
    try:
        text = PDFOperations.extract_text(input_file)
        
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(text)
            click.echo(f"✓ Text extracted to: {output}")
        else:
            click.echo(text)
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output-dir", "-o", default="./images", help="Output directory for images")
def extract_images(input_file, output_dir):
    """Extract all images from PDF"""
    try:
        images = PDFOperations.extract_images(input_file, output_dir)
        click.echo(f"✓ Extracted {len(images)} images to: {output_dir}")
        for img in images:
            click.echo(f"  - {img}")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
def info(input_file):
    """Display PDF metadata and information"""
    try:
        metadata = PDFOperations.get_metadata(input_file)
        
        click.echo(f"\n📄 PDF Information: {input_file}\n")
        click.echo(f"Pages: {metadata.get('page_count', 'N/A')}")
        click.echo(f"File Size: {metadata.get('file_size', 0) / 1024 / 1024:.2f} MB")
        click.echo(f"Title: {metadata.get('title', 'N/A')}")
        click.echo(f"Author: {metadata.get('author', 'N/A')}")
        click.echo(f"Subject: {metadata.get('subject', 'N/A')}")
        click.echo(f"Creator: {metadata.get('creator', 'N/A')}")
        click.echo(f"Producer: {metadata.get('producer', 'N/A')}")
        click.echo(f"Images: {metadata.get('image_count', 0)}")
        
        if metadata.get('fonts'):
            click.echo(f"\nFonts ({len(metadata['fonts'])}):")
            for font in metadata['fonts'][:10]:  # Show first 10
                click.echo(f"  - {font}")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.group()
def batch():
    """Batch operations on multiple files"""
    pass


@batch.command()
@click.argument("pattern", default="*.docx")
@click.option("--to", "target_format", type=click.Choice(["pdf"]), default="pdf")
@click.option("--output-dir", "-o", default="./output", help="Output directory")
def convert_batch(pattern, target_format, output_dir):
    """Batch convert files"""
    try:
        from glob import glob
        
        files = glob(pattern)
        if not files:
            click.echo(f"No files found matching: {pattern}")
            return
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        with click.progressbar(files, label="Converting files") as bar:
            for file in bar:
                output_path = Path(output_dir) / f"{Path(file).stem}.pdf"
                PDFWordConverter.word_to_pdf(file, str(output_path))
        
        click.echo(f"✓ Converted {len(files)} files to {output_dir}")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    cli()
