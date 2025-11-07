#!/usr/bin/env python3
"""
Info-Frame Web App - Upload and convert PDFs/Text to styled images
Run with: python3 webapp_infoframe.py
Then open: http://localhost:5001
"""

from flask import Flask, render_template_string, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io
import base64
from pathlib import Path
import PyPDF2

app = Flask(__name__)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_html(html_file):
    """Extract text content from HTML file"""
    try:
        from html.parser import HTMLParser

        class HTMLTextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []

            def handle_data(self, data):
                if data.strip():
                    self.text.append(data.strip())

        html_content = html_file.read().decode('utf-8')
        parser = HTMLTextExtractor()
        parser.feed(html_content)
        return '\n'.join(parser.text)
    except Exception as e:
        return f"Error reading HTML: {str(e)}"

def get_style_colors(style):
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
    return styles.get(style, styles["modern"])

def create_infoframe(text, style):
    """Create info-frame image and return as bytes"""
    colors = get_style_colors(style)

    width, height = 1200, 1600
    img = Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    except:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    # Header
    draw.rectangle([0, 0, width, 150], fill=colors["accent"])
    draw.text(
        (width // 2, 75),
        "INFO FRAME",
        fill=colors["bg"],
        font=title_font,
        anchor="mm"
    )

    # Accent line
    draw.rectangle([50, 180, width - 50, 185], fill=colors["secondary"])

    # Content
    margin = 80
    lines = text.split('\n')
    wrapped_lines = []
    for line in lines:
        if line.strip():
            wrapped = textwrap.wrap(line, width=40)
            wrapped_lines.extend(wrapped)
        else:
            wrapped_lines.append('')

    y_position = 240
    line_height = 45

    for line in wrapped_lines[:25]:
        if y_position > height - 100:
            break
        draw.text(
            (margin, y_position),
            line,
            fill=colors["text"],
            font=body_font
        )
        y_position += line_height

    # Footer decoration
    draw.rectangle([50, height - 50, width - 50, height - 45], fill=colors["secondary"])

    # Convert to bytes
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Info-Frame Converter</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            background: #f8f9ff;
            margin-bottom: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .upload-area:hover {
            background: #f0f2ff;
            border-color: #764ba2;
        }
        .upload-area.dragover {
            background: #e8ebff;
            border-color: #764ba2;
            transform: scale(1.02);
        }
        input[type="file"] {
            display: none;
        }
        .file-label {
            cursor: pointer;
            color: #667eea;
            font-weight: bold;
            font-size: 1.1em;
        }
        .text-input {
            width: 100%;
            min-height: 200px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-family: monospace;
            font-size: 14px;
            margin-bottom: 20px;
            resize: vertical;
        }
        .style-selector {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .style-btn {
            padding: 15px;
            border: 3px solid #ddd;
            border-radius: 10px;
            background: white;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
        }
        .style-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .style-btn.selected {
            border-color: #667eea;
            background: #f8f9ff;
        }
        .style-btn.modern { color: #e94560; }
        .style-btn.classic { color: #8b4513; }
        .style-btn.minimalist { color: #000; }
        .style-btn.bold { color: #ff0066; }
        .generate-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.2em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102,126,234,0.4);
        }
        .generate-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .preview {
            margin-top: 30px;
            text-align: center;
        }
        .preview img {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .download-btn {
            margin-top: 15px;
            padding: 12px 30px;
            background: #4caf50;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
        }
        .download-btn:hover {
            background: #45a049;
            transform: translateY(-2px);
        }
        .loading {
            text-align: center;
            margin-top: 20px;
            color: #667eea;
            font-weight: bold;
        }
        .error {
            background: #ff4444;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            flex: 1;
            padding: 12px;
            background: #f0f0f0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        .tab.active {
            background: #667eea;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Info-Frame Converter</h1>
        <p class="subtitle">Transform PDFs and text into beautiful styled images</p>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('upload')">📄 Upload File</button>
            <button class="tab" onclick="switchTab('text')">✍️ Paste Text</button>
        </div>

        <div id="upload-tab" class="tab-content active">
            <div class="upload-area" id="uploadArea">
                <label for="fileInput" class="file-label">
                    📎 Click or drag & drop a file here
                </label>
                <input type="file" id="fileInput" accept=".pdf,.txt,.html,.htm" onchange="handleFile()">
                <p style="margin-top: 10px; color: #999;">Supports: PDF, TXT, HTML</p>
            </div>
        </div>

        <div id="text-tab" class="tab-content">
            <textarea
                id="textInput"
                class="text-input"
                placeholder="Paste your text here..."></textarea>
        </div>

        <h3 style="margin-bottom: 15px; color: #333;">Choose Style:</h3>
        <div class="style-selector">
            <button class="style-btn modern selected" data-style="modern" onclick="selectStyle('modern')">
                Modern
            </button>
            <button class="style-btn classic" data-style="classic" onclick="selectStyle('classic')">
                Classic
            </button>
            <button class="style-btn minimalist" data-style="minimalist" onclick="selectStyle('minimalist')">
                Minimalist
            </button>
            <button class="style-btn bold" data-style="bold" onclick="selectStyle('bold')">
                Bold
            </button>
        </div>

        <button class="generate-btn" onclick="generate()">
            ✨ Generate Info-Frame
        </button>

        <div style="margin-top: 20px; text-align: center;">
            <button class="generate-btn" onclick="generateHTML()" style="background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);">
                🌐 Generate HTML Version
            </button>
        </div>

        <div id="loading" class="loading" style="display: none;">
            Generating your info-frame...
        </div>

        <div id="error" class="error" style="display: none;"></div>

        <div id="preview" class="preview" style="display: none;">
            <h3 style="color: #333; margin-bottom: 15px;">Your Info-Frame:</h3>
            <img id="previewImg" src="" alt="Preview">
            <br>
            <a id="downloadBtn" class="download-btn" download="infoframe.png">
                ⬇️ Download PNG
            </a>
        </div>
    </div>

    <script>
        let selectedStyle = 'modern';
        let currentTab = 'upload';

        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            if (tab === 'upload') {
                document.getElementById('upload-tab').classList.add('active');
                document.querySelector('.tab:nth-child(1)').classList.add('active');
            } else {
                document.getElementById('text-tab').classList.add('active');
                document.querySelector('.tab:nth-child(2)').classList.add('active');
            }
        }

        function selectStyle(style) {
            selectedStyle = style;
            document.querySelectorAll('.style-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            document.querySelector(`[data-style="${style}"]`).classList.add('selected');
        }

        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('dragover');
            });
        });

        uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length) {
                fileInput.files = files;
                handleFile();
            }
        });

        function handleFile() {
            const file = fileInput.files[0];
            if (file) {
                document.querySelector('.file-label').textContent = `✓ ${file.name}`;
            }
        }

        async function generate() {
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const preview = document.getElementById('preview');

            loading.style.display = 'block';
            error.style.display = 'none';
            preview.style.display = 'none';

            try {
                const formData = new FormData();
                formData.append('style', selectedStyle);

                if (currentTab === 'upload') {
                    const file = fileInput.files[0];
                    if (!file) {
                        throw new Error('Please select a file');
                    }
                    formData.append('file', file);
                } else {
                    const text = document.getElementById('textInput').value;
                    if (!text.trim()) {
                        throw new Error('Please enter some text');
                    }
                    formData.append('text', text);
                }

                const response = await fetch('/generate', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.error || 'Generation failed');
                }

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);

                document.getElementById('previewImg').src = url;
                document.getElementById('downloadBtn').href = url;

                loading.style.display = 'none';
                preview.style.display = 'block';

            } catch (err) {
                loading.style.display = 'none';
                error.textContent = err.message;
                error.style.display = 'block';
            }
        }

        async function generateHTML() {
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');

            loading.style.display = 'block';
            loading.textContent = 'Generating HTML file...';
            error.style.display = 'none';

            try {
                const formData = new FormData();
                formData.append('style', selectedStyle);
                formData.append('format', 'html');

                if (currentTab === 'upload') {
                    const file = fileInput.files[0];
                    if (!file) {
                        throw new Error('Please select a file');
                    }
                    formData.append('file', file);
                } else {
                    const text = document.getElementById('textInput').value;
                    if (!text.trim()) {
                        throw new Error('Please enter some text');
                    }
                    formData.append('text', text);
                }

                const response = await fetch('/generate', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.error || 'Generation failed');
                }

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);

                // Download HTML file
                const a = document.createElement('a');
                a.href = url;
                a.download = `infoframe_${selectedStyle}.html`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);

                loading.style.display = 'none';
                loading.textContent = 'Generating your info-frame...';
                alert('✅ HTML file downloaded successfully!');

            } catch (err) {
                loading.style.display = 'none';
                loading.textContent = 'Generating your info-frame...';
                error.textContent = err.message;
                error.style.display = 'block';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

def create_html(text, style):
    """Create HTML version of info-frame"""
    colors = get_style_colors(style)

    # Convert RGB tuples to hex
    bg_hex = '#{:02x}{:02x}{:02x}'.format(*colors["bg"])
    accent_hex = '#{:02x}{:02x}{:02x}'.format(*colors["accent"])
    text_hex = '#{:02x}{:02x}{:02x}'.format(*colors["text"])
    secondary_hex = '#{:02x}{:02x}{:02x}'.format(*colors["secondary"])

    # Process text
    lines = text.split('\n')
    content_html = ""
    for line in lines:
        if line.strip():
            content_html += f"<p>{line}</p>\n"
        else:
            content_html += "<br>\n"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Info Frame - {style.capitalize()}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Helvetica', Arial, sans-serif;
            background: {bg_hex};
            color: {text_hex};
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            width: 100%;
            background: {bg_hex};
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .header {{
            background: {accent_hex};
            padding: 50px;
            text-align: center;
        }}
        .header h1 {{
            color: {bg_hex};
            font-size: 3.5em;
            font-weight: bold;
            letter-spacing: 2px;
        }}
        .accent-line {{
            height: 5px;
            background: {secondary_hex};
            margin: 30px 50px;
        }}
        .content {{
            padding: 40px 80px;
            font-size: 1.3em;
            line-height: 1.8;
        }}
        .content p {{
            margin-bottom: 15px;
        }}
        .footer-line {{
            height: 5px;
            background: {secondary_hex};
            margin: 30px 50px 50px 50px;
        }}
        @media print {{
            body {{
                padding: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>INFO FRAME</h1>
        </div>
        <div class="accent-line"></div>
        <div class="content">
{content_html}
        </div>
        <div class="footer-line"></div>
    </div>
</body>
</html>"""
    return html

@app.route('/generate', methods=['POST'])
def generate():
    try:
        style = request.form.get('style', 'modern')
        output_format = request.form.get('format', 'png')

        # Check if file or text was provided
        if 'file' in request.files:
            file = request.files['file']
            if file.filename.endswith('.pdf'):
                text = extract_text_from_pdf(file)
            elif file.filename.endswith(('.html', '.htm')):
                text = extract_text_from_html(file)
            else:
                text = file.read().decode('utf-8')
        elif 'text' in request.form:
            text = request.form.get('text')
        else:
            return jsonify({'error': 'No file or text provided'}), 400

        if not text or not text.strip():
            return jsonify({'error': 'No content to convert'}), 400

        # Limit text length
        if len(text) > 2000:
            text = text[:2000] + "..."

        # Generate HTML if requested
        if output_format == 'html':
            html_content = create_html(text, style)
            html_io = io.BytesIO(html_content.encode('utf-8'))
            html_io.seek(0)
            return send_file(
                html_io,
                mimetype='text/html',
                as_attachment=True,
                download_name=f'infoframe_{style}.html'
            )

        # Generate image
        img_io = create_infoframe(text, style)

        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=False,
            download_name=f'infoframe_{style}.png'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🎨 INFO-FRAME WEB APP")
    print("=" * 60)
    print("\n✨ Server starting...")
    print("🌐 Open your browser and go to: http://localhost:5001")
    print("📱 Or from another device: http://YOUR_IP:5001")
    print("\n⌨️  Press Ctrl+C to stop the server\n")
    app.run(debug=True, host='0.0.0.0', port=5001)
