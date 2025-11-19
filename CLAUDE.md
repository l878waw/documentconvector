# CLAUDE.md - AI Assistant Guide for Document Convector

## Project Overview

**Document Convector** is a universal document conversion tool that transforms various document formats (PDF, HTML, DOCX, TXT) into beautifully styled images and documents. The project provides three interfaces: CLI, Web App, and Desktop GUI.

**Primary Language**: Python 3.8+
**Secondary Language**: JavaScript (Node.js 18+)
**Framework**: Flask (web), Tkinter (desktop), Puppeteer (HTML rendering)

## Repository Structure

```
documentconvector/
├── convert.py              # Main CLI converter (core logic)
├── webapp.py               # Flask web app (port 8000)
├── webapp_infoframe.py     # Alternative Flask app (port 5001)
├── desktop_infoframe.py    # Tkinter desktop GUI
├── snap.js                 # Puppeteer HTML-to-image renderer (main)
├── render.js               # Wrapper for snap.js
├── test.html               # Test file for HTML conversion
├── package.json            # Node.js dependencies
├── requirements.txt        # Python dependencies
├── README.md              # User documentation
└── *.sh                   # Shell scripts for various tasks
```

## Core Components

### 1. CLI Converter (`convert.py`)
**Location**: `convert.py:1-360`

**Key Functions**:
- `read_file(file_path)` - Universal file reader (PDF/HTML/DOCX/TXT) at `convert.py:113`
- `read_pdf(file_path)` - PDF text extraction using PyPDF2 at `convert.py:33`
- `read_html(file_path)` - HTML text extraction with formatting at `convert.py:50`
- `read_docx(file_path)` - DOCX text extraction at `convert.py:16`
- `get_colors(style)` - Color scheme definitions at `convert.py:164`
- `create_image(text, style)` - Image generation logic at `convert.py:194`
- `convert_html_with_snap(input_path, output_path)` - HTML rendering via Node.js at `convert.py:131`

**Usage Pattern**:
```bash
python3 convert.py <input_file> [output_format] [style]
```

**Supported Formats**:
- Input: PDF, HTML, DOCX, TXT
- Output: PNG, JPG, JPEG, PDF
- Styles: modern, classic, minimalist, bold

### 2. Web Applications

#### Main Web App (`webapp.py`)
**Port**: 8000
**Location**: `webapp.py:1-622`

**Key Routes**:
- `/` - Main interface at `webapp.py:515`
- `/generate` - Image generation endpoint at `webapp.py:525`
- `/convert_html` - HTML-to-PNG conversion via npm at `webapp.py:559`
- `/setup` - HTML converter setup page at `webapp.py:519`

**Key Functions**:
- `read_file_content(file)` - Uploaded file reader at `webapp.py:23`
- `get_colors(style)` - Color scheme at `webapp.py:66`
- `create_image(text, style)` - Image generator at `webapp.py:76`

#### InfoFrame Web App (`webapp_infoframe.py`)
**Port**: 5001
**Location**: `webapp_infoframe.py:1-742`

**Differences from main webapp**:
- HTML output support via `/generate?format=html`
- `create_html(text, style)` function at `webapp_infoframe.py:583`
- Drag-and-drop file upload
- Both PNG and HTML generation buttons

### 3. Desktop GUI (`desktop_infoframe.py`)
**Framework**: Tkinter
**Location**: `desktop_infoframe.py:1-519`

**Key Class**: `InfoFrameApp` at `desktop_infoframe.py:15`

**Key Methods**:
- `upload_file()` - File upload handler at `desktop_infoframe.py:182`
- `generate()` - Image generation at `desktop_infoframe.py:336`
- `save_image()` - Multi-format save at `desktop_infoframe.py:464`
- `create_infoframe(text, style)` - Image creation at `desktop_infoframe.py:278`
- `create_html(text, style)` - HTML export at `desktop_infoframe.py:371`

### 4. HTML Renderer (`snap.js`)
**Purpose**: Convert HTML files/URLs to PNG/JPEG using Puppeteer
**Location**: `snap.js:1-271`

**Key Functions**:
- `convertHtml(options)` - Main conversion function at `snap.js:45`
- `resolveInputPath(input)` - Path resolution at `snap.js:12`
- `parseArgs(argv)` - CLI argument parser at `snap.js:131`
- `runSnap(argv, options)` - CLI runner at `snap.js:214`

**Default Settings**:
- Viewport: 1200x1600
- Delay: 500ms
- Output: `~/Desktop/Donepng/<filename>.png`
- Full page screenshot enabled

## Style System

All components share the same 4 color schemes defined identically across files:

### Style Definitions
Located in multiple files with identical values:
- `convert.py:164-192`
- `webapp.py:66-74`
- `webapp_infoframe.py:50-77`
- `desktop_infoframe.py:249-276`

### Color Schemes

**Modern**:
- Background: `(26, 26, 46)` - Dark blue
- Accent: `(233, 69, 96)` - Pink
- Text: `(238, 238, 238)` - Light gray
- Secondary: `(78, 204, 163)` - Teal

**Classic**:
- Background: `(240, 235, 220)` - Beige
- Accent: `(139, 69, 19)` - Brown
- Text: `(40, 40, 40)` - Dark gray
- Secondary: `(184, 134, 11)` - Gold

**Minimalist**:
- Background: `(255, 255, 255)` - White
- Accent: `(0, 0, 0)` - Black
- Text: `(60, 60, 60)` - Gray
- Secondary: `(150, 150, 150)` - Light gray

**Bold**:
- Background: `(255, 215, 0)` - Yellow
- Accent: `(255, 0, 102)` - Bright pink
- Text: `(0, 0, 0)` - Black
- Secondary: `(102, 0, 204)` - Purple

## Image Generation Logic

### Standard Layout (used in all image outputs)
**Canvas**: 1200x1600 pixels

**Layout Structure**:
1. Header: `[0, 0, 1200, 150]` - Filled with accent color
2. Title: "INFO FRAME" centered at `(600, 75)`
3. Accent line: `[50, 180, 1150, 185]` - Secondary color
4. Content area: Starts at y=240, 40-char line wrapping, max 25 lines
5. Footer line: `[50, 1550, 1150, 1555]` - Secondary color

### Font Loading
**Primary font path**: `/System/Library/Fonts/Helvetica.ttc`
**Fallback**: `ImageFont.load_default()`
- Title font: 60pt
- Body font: 32pt
- Line height: 45px

## Dependencies

### Python Dependencies (`requirements.txt`)
```
Pillow>=10.0.0      # Image processing
PyPDF2>=3.0.0       # PDF text extraction
python-docx>=0.8.11 # DOCX file support
Flask>=2.3.0        # Web framework
```

**Installation**: `pip3 install -r requirements.txt`

### Node Dependencies (`package.json`)
```json
{
  "dependencies": {
    "puppeteer": "^24.15.0"
  },
  "scripts": {
    "convert": "node render.js",
    "snap": "node snap.js"
  }
}
```

**Installation**: `npm install`

## Development Workflows

### Adding a New Style

1. Update `get_colors()` / `get_style_colors()` in ALL files:
   - `convert.py:164`
   - `webapp.py:66`
   - `webapp_infoframe.py:50`
   - `desktop_infoframe.py:249`

2. Add color definition with keys: `bg`, `accent`, `text`, `secondary`

3. Update style validation in `convert.py:268` (valid_styles set)

4. Update UI elements:
   - Web apps: Add button in HTML templates
   - Desktop: Add radiobutton in `desktop_infoframe.py:112-132`

### Adding a New Input Format

1. Add reader function in `convert.py` (follow pattern of `read_pdf`, `read_html`, etc.)

2. Update `read_file()` at `convert.py:113` to handle new extension

3. Update web apps:
   - Add to `read_file_content()` in `webapp.py:23`
   - Add to file upload accept list in HTML templates

4. Update desktop app:
   - Add to `upload_file()` filetypes at `desktop_infoframe.py:183`
   - Add extraction method if needed

### Adding a New Output Format

1. Update `convert.py` main function around line 349-355

2. Add format to `valid_formats` set at `convert.py:258`

3. Add save logic using PIL's `img.save()` method

4. Update desktop app's `save_image()` at `desktop_infoframe.py:464`

### Testing HTML Conversion

Use the test file:
```bash
node snap.js test.html output.png
# or
npm run snap -- test.html output.png
```

## Shell Scripts Reference

### Quick Start Scripts
- `START_NOW.sh` - Interactive CLI converter with prompts
- `launch_webapp.sh` - Start Flask web app (port 8000)
- `launch_desktop.sh` - Start desktop GUI

### Installation Scripts
- `install_deps.sh` - Install Python dependencies only
- `install_infoframe.sh` - Full setup (Python + Node)
- `setup_infoframe.sh` - Complete project setup

### Conversion Scripts
- `convert_file.sh` - Convert single file
- `quick_convert.sh` - Fast conversion with defaults
- `html_to_png.sh` - HTML-specific conversion

## Key Conventions

### Code Style
1. **Docstrings**: Triple-quoted strings at function start
2. **Error Handling**: Try-except with user-friendly messages
3. **File Paths**: Use `pathlib.Path` for cross-platform compatibility
4. **Text Limiting**: Max 2000 characters for image generation
5. **Line Wrapping**: 40 characters for image text, 25 lines max

### Naming Conventions
- **Functions**: `snake_case` (e.g., `read_file`, `create_image`)
- **Classes**: `PascalCase` (e.g., `InfoFrameApp`)
- **Variables**: `snake_case` (e.g., `selected_style`, `output_path`)
- **Constants**: Uppercase in some cases (e.g., `HTML_TEMPLATE`)

### File Naming
- Output files: `{input_name}_{style}.{format}`
- Example: `document_modern.png`

### Error Messages
- Use emoji prefixes: `❌` for errors, `⚠️` for warnings, `✅` for success
- Provide actionable guidance in error messages

## Common Development Tasks

### 1. Run the CLI Converter
```bash
python3 convert.py input.pdf png modern
```

### 2. Start Web App for Testing
```bash
# Main web app
python3 webapp.py  # http://localhost:8000

# InfoFrame web app
python3 webapp_infoframe.py  # http://localhost:5001
```

### 3. Test Desktop GUI
```bash
python3 desktop_infoframe.py
```

### 4. Test HTML Rendering
```bash
node snap.js test.html -o output.png -w 1200 -H 1600
```

### 5. Install All Dependencies
```bash
pip3 install -r requirements.txt
npm install
```

## Important Notes for AI Assistants

### 1. Code Duplication
The color scheme logic and image creation functions are **intentionally duplicated** across files (`convert.py`, `webapp.py`, `webapp_infoframe.py`, `desktop_infoframe.py`) to keep each component independent. When updating styles or image generation logic, update ALL files.

### 2. Font Paths
The current font path `/System/Library/Fonts/Helvetica.ttc` is **macOS-specific**. On Linux/Windows, the code falls back to default fonts. When suggesting font improvements, consider cross-platform paths.

### 3. HTML Rendering
HTML files can be processed two ways:
1. **Text extraction**: Extract text content and create styled image (fallback)
2. **Screenshot**: Render actual HTML using Puppeteer (preferred for HTML files)

The CLI (`convert.py:322`) tries Puppeteer first, falls back to text extraction.

### 4. Argument Swapping
The CLI includes smart argument detection (`convert.py:273-305`) that handles cases where users swap format and style arguments.

### 5. Two Web Apps
- `webapp.py` (port 8000): Simpler, PNG-only output, includes `/setup` page for HTML conversion
- `webapp_infoframe.py` (port 5001): Full-featured, supports both PNG and HTML output, drag-and-drop

### 6. Output Locations
- CLI: Saves to same directory as script
- Snap.js: Saves to `~/Desktop/Donepng/` by default
- Web apps: Streams directly to browser (no file saved on server)
- Desktop GUI: User chooses save location

### 7. Text Processing
All components trim text to 2000 characters and wrap at 40 characters per line, displaying max 25 lines. This is consistent across all implementations.

### 8. Development Branch
Current branch: `claude/claude-md-mi61so68s992dwf3-01YSFY7tUV695xEHR2mfHW8e`
Main branch: Not specified (appears to be using detached or feature branch)

## Testing Guidelines

### Manual Testing Checklist
1. **CLI Tests**:
   - Test each input format (PDF, HTML, DOCX, TXT)
   - Test each output format (PNG, JPG, PDF)
   - Test all 4 styles
   - Test argument swapping detection

2. **Web App Tests**:
   - Test file upload
   - Test text paste
   - Test each style
   - Test download functionality

3. **Desktop GUI Tests**:
   - Test file selection
   - Test text paste
   - Test preview generation
   - Test save as PNG/JPG/PDF/HTML

4. **HTML Rendering Tests**:
   - Test with `test.html`
   - Test with URL
   - Test custom viewport sizes
   - Test JPEG output

### Edge Cases to Consider
- Empty files
- Very large files (>2000 chars)
- Special characters in text
- Missing dependencies
- Invalid file paths
- Unsupported formats

## Quick Reference Commands

```bash
# Install dependencies
pip3 install -r requirements.txt && npm install

# CLI conversion
python3 convert.py document.pdf png modern

# Start web apps
python3 webapp.py              # Port 8000
python3 webapp_infoframe.py    # Port 5001

# Start desktop GUI
python3 desktop_infoframe.py

# HTML to PNG
node snap.js input.html output.png
npm run snap -- input.html output.png

# Run with custom options
node snap.js page.html -o result.png -w 800 -H 600 -d 1000
```

## Git Workflow

### Commit Messages
Follow the existing pattern:
- Use descriptive commit messages
- Examples from history:
  - "Add test HTML file for converter testing"
  - "Initial commit: Document Convector"

### Branch Strategy
- Development happens on feature branches starting with `claude/`
- Branch format includes session ID suffix
- Always push to the designated feature branch

## Extension Points

Areas where the codebase can be easily extended:

1. **New Styles**: Add to `get_colors()` functions
2. **New Input Formats**: Add reader function and update `read_file()`
3. **New Output Formats**: Add save logic in main functions
4. **Custom Layouts**: Modify `create_image()` / `create_infoframe()`
5. **Additional Web Routes**: Add Flask routes in web apps
6. **GUI Features**: Extend `InfoFrameApp` class

## Performance Considerations

1. **Image Generation**: Fast (< 1 second for typical text)
2. **PDF Extraction**: Can be slow for large PDFs
3. **HTML Rendering**: Requires launching Puppeteer browser (2-5 seconds)
4. **Web Apps**: Use threading for production deployment
5. **Memory**: PIL keeps images in memory; consider for batch processing

## Security Considerations

1. **File Upload**: Web apps should validate file types and sizes
2. **Text Input**: Currently no sanitization for HTML output
3. **Command Injection**: Be careful with subprocess calls (snap.js usage)
4. **Path Traversal**: Use Path objects, not string concatenation
5. **Flask Debug Mode**: Disabled in production (`webapp.py:621`)

---

**Last Updated**: 2025-11-19
**Maintained By**: AI Assistant (Claude)
**Project Owner**: l878waw
**License**: MIT
