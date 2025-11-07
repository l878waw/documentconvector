# Document Convector

A universal document conversion tool that transforms PDFs, HTML, DOCX, and text files into beautiful styled images and documents.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Node](https://img.shields.io/badge/node-18%2B-green.svg)

## Features

- **Multiple Input Formats**: PDF, HTML, DOCX, TXT
- **Multiple Output Formats**: PNG, JPG, JPEG, PDF, HTML
- **4 Beautiful Styles**: Modern, Classic, Minimalist, Bold
- **3 Interfaces**:
  - Command-line interface (CLI)
  - Web application (Flask)
  - Desktop GUI (Tkinter)
- **HTML Rendering**: Advanced HTML-to-image conversion using Puppeteer

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/l878waw/documentconvector.git
cd documentconvector
```

2. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

3. Install Node dependencies (for HTML rendering):
```bash
npm install
```

### Basic Usage

**Command Line:**
```bash
python3 convert.py input.pdf png modern
python3 convert.py document.html jpg classic
python3 convert.py notes.txt png minimalist
```

**Web App:**
```bash
python3 webapp.py
# Open http://localhost:8000
```

**Desktop GUI:**
```bash
python3 desktop_infoframe.py
```

## Styles

### Modern
Dark blue background with vibrant pink accents
- Perfect for contemporary documents

### Classic
Warm beige background with brown tones
- Ideal for traditional documents

### Minimalist
Clean white background with black text
- Best for simple, elegant output

### Bold
Bright yellow background with vibrant colors
- Great for eye-catching content

## Command Line Reference

### Syntax
```bash
python3 convert.py <input_file> [output_format] [style]
```

### Examples
```bash
# PDF to PNG with modern style
python3 convert.py report.pdf png modern

# HTML to JPG with classic style
python3 convert.py page.html jpg classic

# Text to JPEG with bold style
python3 convert.py notes.txt jpeg bold

# DOCX to PNG with minimalist style
python3 convert.py document.docx png minimalist
```

### Arguments
- `input_file`: Path to your input file (PDF, HTML, DOCX, or TXT)
- `output_format`: Desired output format (png, jpg, jpeg, pdf)
- `style`: Visual style (modern, classic, minimalist, bold)

## Web Application

The web interface provides an intuitive way to convert documents:

1. **Upload or Paste**: Choose a file or paste text directly
2. **Select Style**: Pick from 4 visual themes
3. **Generate**: Create your info-frame
4. **Download**: Save as PNG or HTML

### Running the Web App

**Standard Web App:**
```bash
python3 webapp.py
# Visit http://localhost:8000
```

**InfoFrame Web App:**
```bash
python3 webapp_infoframe.py
# Visit http://localhost:5001
```

## Desktop Application

A native GUI application built with Tkinter:

```bash
python3 desktop_infoframe.py
```

**Features:**
- File browser for easy selection
- Real-time preview
- Multiple export formats
- Drag-and-drop support

## HTML to Image Conversion

For advanced HTML rendering using Puppeteer:

```bash
node snap.js input.html output.png
```

**Options:**
```bash
node snap.js input.html -o output.png -w 1200 -H 1600 -d 500
```

- `-o, --output`: Output file path
- `-w, --width`: Viewport width in pixels (default: 1200)
- `-H, --height`: Viewport height in pixels (default: 1600)
- `-d, --delay`: Delay before screenshot in ms (default: 500)
- `--jpeg`: Save as JPEG instead of PNG

## Project Structure

```
documentconvector/
├── convert.py              # Main CLI converter
├── webapp.py               # Flask web application (port 8000)
├── webapp_infoframe.py     # Alternative web app (port 5001)
├── desktop_infoframe.py    # Tkinter desktop GUI
├── snap.js                 # Puppeteer HTML renderer
├── render.js               # Render utility
├── package.json            # Node dependencies
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Requirements

### Python Dependencies
- `Pillow` - Image processing
- `PyPDF2` - PDF text extraction
- `python-docx` - DOCX file support
- `Flask` - Web framework

### Node Dependencies
- `puppeteer` - HTML rendering

### System Requirements
- Python 3.8 or higher
- Node.js 18 or higher
- macOS, Linux, or Windows

## Output

All converted files are saved in the project directory with the format:
```
<filename>_<style>.<format>
```

Examples:
- `report_modern.png`
- `document_classic.jpg`
- `notes_bold.jpeg`

## Troubleshooting

### "Module not found" Error
Install missing Python dependencies:
```bash
pip3 install Pillow PyPDF2 python-docx Flask
```

### HTML Rendering Not Working
Install Node dependencies:
```bash
npm install
```

### Font Issues on Windows/Linux
The tool uses system fonts. If fonts are not found, it falls back to default fonts.

### Web App Port Already in Use
Change the port in the Python file:
```python
app.run(host='0.0.0.0', port=8001)  # Use different port
```

## Development

### Running Tests
```bash
# Test CLI converter
python3 convert.py test.txt png modern

# Test web app locally
python3 webapp.py

# Test HTML rendering
node snap.js test.html test_output.png
```

### Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Created by [l878waw](https://github.com/l878waw)

## Acknowledgments

- Built with [Pillow](https://python-pillow.org/) for image processing
- Uses [Flask](https://flask.palletsprojects.com/) for web interface
- Powered by [Puppeteer](https://pptr.dev/) for HTML rendering
- PDF support via [PyPDF2](https://pypdf2.readthedocs.io/)

## Support

For issues, questions, or suggestions:
- Open an issue on [GitHub](https://github.com/l878waw/documentconvector/issues)
- Check existing issues for solutions

---

**Made with Python, Node.js, and creativity**
