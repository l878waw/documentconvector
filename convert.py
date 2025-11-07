#!/usr/bin/env python3
"""
Universal Info-Frame Converter
Converts: TXT, HTML, PDF, DOCX → PNG, JPG, JPEG, PDF

Usage: python3 convert.py <input_file> [output_format] [style]
Example: python3 convert.py document.pdf png modern
"""

from PIL import Image, ImageDraw, ImageFont
import textwrap
import sys
import subprocess
from pathlib import Path

def read_docx(file_path):
    """Read text from DOCX file"""
    try:
        import docx
        doc = docx.Document(file_path)
        text = []
        for para in doc.paragraphs:
            if para.text.strip():
                text.append(para.text)
        return '\n'.join(text)
    except ImportError:
        print("⚠️  DOCX support requires python-docx: pip3 install python-docx")
        return None
    except Exception as e:
        print(f"⚠️  Could not read DOCX: {e}")
        return None

def read_pdf(file_path):
    """Read text from PDF file"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = []
            for page in reader.pages:
                text.append(page.extract_text())
            return '\n'.join(text)
    except ImportError:
        print("⚠️  PDF support requires PyPDF2: pip3 install PyPDF2")
        return None
    except Exception as e:
        print(f"⚠️  Could not read PDF: {e}")
        return None

def read_html(file_path):
    """Read text from HTML file with better formatting"""
    try:
        from html.parser import HTMLParser

        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
                self.in_title = False
                self.in_heading = False

            def handle_starttag(self, tag, attrs):
                if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    self.in_heading = True
                    self.text.append('')  # Add blank line before heading
                elif tag == 'title':
                    self.in_title = True
                elif tag in ['p', 'div', 'section', 'li']:
                    pass
                elif tag == 'br':
                    self.text.append('')

            def handle_endtag(self, tag):
                if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    self.in_heading = False
                    self.text.append('')  # Add blank line after heading
                elif tag == 'title':
                    self.in_title = False
                    self.text.append('')
                elif tag in ['p', 'li']:
                    self.text.append('')

            def handle_data(self, data):
                cleaned = data.strip()
                if cleaned:
                    if self.in_heading:
                        self.text.append('=== ' + cleaned.upper() + ' ===')
                    elif self.in_title:
                        self.text.append('*** ' + cleaned + ' ***')
                    else:
                        self.text.append(cleaned)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            parser = TextExtractor()
            parser.feed(content)
            # Clean up multiple blank lines
            result = []
            prev_blank = False
            for line in parser.text:
                if not line:
                    if not prev_blank:
                        result.append(line)
                    prev_blank = True
                else:
                    result.append(line)
                    prev_blank = False
            return '\n'.join(result)
    except Exception as e:
        print(f"⚠️  Could not read HTML: {e}")
        return None

def read_file(file_path):
    """Read any supported file type"""
    ext = Path(file_path).suffix.lower()

    if ext == '.pdf':
        return read_pdf(file_path)
    elif ext in ['.html', '.htm']:
        return read_html(file_path)
    elif ext in ['.docx', '.doc']:
        return read_docx(file_path)
    else:  # TXT or plain text
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Could not read file: {e}")
            return None

def convert_html_with_snap(input_path, output_path):
    """Render HTML file to image using snap.js"""
    snap_script = Path(__file__).parent / "snap.js"

    if not snap_script.exists():
        print(f"❌ Missing snap.js at {snap_script}")
        return False

    try:
        result = subprocess.run(
            ["node", str(snap_script), str(input_path), str(output_path)],
            capture_output=True,
            text=True
        )
    except FileNotFoundError:
        print("❌ Node.js is required for HTML rendering but was not found.")
        return False

    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()

    if result.returncode != 0:
        if stderr:
            print(stderr)
        if stdout and stdout != stderr:
            print(stdout)
        print("❌ HTML rendering failed via snap.js")
        return False

    if stdout:
        print(stdout)
    return True

def get_colors(style):
    """Get color scheme for style"""
    styles = {
        "modern": {
            "bg": (26, 26, 46),
            "accent": (233, 69, 96),
            "text": (238, 238, 238),
            "secondary": (78, 204, 163)
        },
        "classic": {
            "bg": (240, 235, 220),
            "accent": (139, 69, 19),
            "text": (40, 40, 40),
            "secondary": (184, 134, 11)
        },
        "minimalist": {
            "bg": (255, 255, 255),
            "accent": (0, 0, 0),
            "text": (60, 60, 60),
            "secondary": (150, 150, 150)
        },
        "bold": {
            "bg": (255, 215, 0),
            "accent": (255, 0, 102),
            "text": (0, 0, 0),
            "secondary": (102, 0, 204)
        }
    }
    return styles.get(style.lower(), styles["modern"])

def create_image(text, style):
    """Create info-frame image"""
    colors = get_colors(style)

    width, height = 1200, 1600
    img = Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    except:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    # Header
    draw.rectangle([0, 0, width, 150], fill=colors["accent"])
    draw.text((width//2, 75), "INFO FRAME", fill=colors["bg"], font=title_font, anchor="mm")

    # Accent line
    draw.rectangle([50, 180, width-50, 185], fill=colors["secondary"])

    # Content
    lines = []
    for line in text.split('\n'):
        if line.strip():
            lines.extend(textwrap.wrap(line, width=40))
        else:
            lines.append('')

    y = 240
    for line in lines[:25]:
        if y > height - 100:
            break
        draw.text((80, y), line, fill=colors["text"], font=body_font)
        y += 45

    # Footer
    draw.rectangle([50, height-50, width-50, height-45], fill=colors["secondary"])

    return img

def main():
    print("\n🎨 UNIVERSAL CONVERTER")
    print("=" * 50)

    if len(sys.argv) < 2:
        print("\nUsage: python3 convert.py <file> [format] [style]")
        print("\nInput:  TXT, HTML, PDF, DOCX")
        print("Output: PNG, JPG, JPEG, PDF")
        print("Styles: modern, classic, minimalist, bold")
        print("\nExamples:")
        print("  python3 convert.py document.pdf png modern")
        print("  python3 convert.py notes.txt jpg")
        print("  python3 convert.py page.html png classic\n")
        return

    input_file = sys.argv[1]
    output_format = sys.argv[2].lower() if len(sys.argv) > 2 else "png"
    style = sys.argv[3].lower() if len(sys.argv) > 3 else "modern"
    style_arg_raw = style
    input_path = Path(input_file)

    valid_formats = {"png", "jpg", "jpeg", "pdf"}
    style_aliases = {
        "minimal": "minimalist",
        "minimalistic": "minimalist",
        "classic": "classic",
        "classical": "classic",
        "bold": "bold",
        "modern": "modern",
        "minimalist": "minimalist"
    }
    valid_styles = {"modern", "classic", "minimalist", "bold"}

    def normalize_style(value):
        return style_aliases.get(value, value)

    swap_message = ""
    output_format = output_format.lower()
    style = normalize_style(style.lower())
    format_as_style = normalize_style(output_format)
    style_arg_is_format = style_arg_raw in valid_formats
    style_arg_is_style = style in valid_styles
    style_arg_provided = len(sys.argv) > 3

    if output_format not in valid_formats:
        if format_as_style in valid_styles and style_arg_is_format:
            # Format and style positions were swapped.
            style = format_as_style
            output_format = style_arg_raw
            swap_message = f"🔄 Detected swapped arguments. Using format '{output_format}' and style '{style}'."
        elif format_as_style in valid_styles and (not style_arg_provided or not style_arg_is_style):
            # Only style provided; fall back to default format.
            style = format_as_style
            output_format = "png"
            swap_message = f"🔄 Detected style only. Using format 'png' and style '{style}'."
        else:
            print(f"❌ Unknown format: {output_format}")
            print("   Supported formats: png, jpg, jpeg, pdf\n")
            return
    else:
        if style_arg_is_format and format_as_style in valid_styles:
            # Third argument is a format; swap with style.
            style = format_as_style
            output_format = style_arg_raw
            swap_message = f"🔄 Detected swapped arguments. Using format '{output_format}' and style '{style}'."

    if style not in valid_styles:
        print(f"❌ Unknown style: {style}")
        print("   Supported styles: modern, classic, minimalist, bold\n")
        return

    if not input_path.exists():
        print(f"❌ File not found: {input_file}\n")
        return

    input_ext = input_path.suffix.lower()
    output_name = f"{input_path.stem}_{style}.{output_format}"
    output_path = Path(__file__).parent / output_name

    print(f"\n📄 Reading: {input_path.name}")
    if swap_message:
        print(swap_message)

    image_formats = {"png", "jpg", "jpeg"}

    if input_ext in ['.html', '.htm'] and output_format in image_formats:
        print(f"📦 Format: {output_format}")
        print(f"🎨 Style: {style} (ignored for HTML screenshot)")
        print("📸 Rendering HTML with snap.js...")
        if convert_html_with_snap(input_path, output_path):
            print(f"\n✅ Saved: {output_name}")
            print(f"📁 Location: {output_path.parent}\n")
            return
        print("⚠️  snap.js rendering failed; falling back to styled text rendering.")

    text = read_file(input_file)

    if not text:
        print("❌ Could not read file\n")
        return

    # Trim if too long
    if len(text) > 2000:
        text = text[:2000] + "..."
        print("✂️  Content trimmed to 2000 chars")

    # Generate image
    print(f"🎨 Style: {style}")
    print(f"📦 Format: {output_format}")

    img = create_image(text, style)

    if output_format in ['jpg', 'jpeg']:
        img.convert('RGB').save(output_path, 'JPEG', quality=95)
    elif output_format == 'pdf':
        img.convert('RGB').save(output_path, 'PDF', resolution=100.0)
    else:
        img.save(output_path, 'PNG')

    print(f"\n✅ Saved: {output_name}")
    print(f"📁 Location: {output_path.parent}\n")

if __name__ == "__main__":
    main()
