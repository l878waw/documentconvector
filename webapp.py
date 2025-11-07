#!/usr/bin/env python3
"""
Info-Frame Web App - Simple & Fast
Run this and open http://localhost:8000
"""

from flask import Flask, render_template_string, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io
from pathlib import Path
import subprocess
import tempfile

app = Flask(__name__)

# Import our converter functions
import sys
BASE_DIR = Path(__file__).parent
NODE_CONVERTER = BASE_DIR / "render.js"
sys.path.insert(0, str(BASE_DIR))

def read_file_content(file):
    """Read uploaded file content"""
    filename = file.filename.lower()

    try:
        if filename.endswith('.pdf'):
            import PyPDF2
            reader = PyPDF2.PdfReader(file)
            text = []
            for page in reader.pages:
                text.append(page.extract_text())
            return '\n'.join(text)

        elif filename.endswith(('.html', '.htm')):
            from html.parser import HTMLParser
            class TextExtractor(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text = []
                def handle_data(self, data):
                    if data.strip():
                        self.text.append(data.strip())

            content = file.read().decode('utf-8')
            parser = TextExtractor()
            parser.feed(content)
            return '\n'.join(parser.text)

        elif filename.endswith('.docx'):
            import docx
            doc = docx.Document(file)
            text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text.append(para.text)
            return '\n'.join(text)

        else:  # Plain text
            return file.read().decode('utf-8')

    except Exception as e:
        return f"Error reading file: {str(e)}"

def get_colors(style):
    """Get color scheme"""
    styles = {
        "modern": {"bg": (26, 26, 46), "accent": (233, 69, 96), "text": (238, 238, 238), "secondary": (78, 204, 163)},
        "classic": {"bg": (240, 235, 220), "accent": (139, 69, 19), "text": (40, 40, 40), "secondary": (184, 134, 11)},
        "minimalist": {"bg": (255, 255, 255), "accent": (0, 0, 0), "text": (60, 60, 60), "secondary": (150, 150, 150)},
        "bold": {"bg": (255, 215, 0), "accent": (255, 0, 102), "text": (0, 0, 0), "secondary": (102, 0, 204)}
    }
    return styles.get(style.lower(), styles["modern"])

def create_image(text, style):
    """Create info-frame image"""
    colors = get_colors(style)

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

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Info-Frame Converter</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            background: #f8f9ff;
            margin-bottom: 20px;
            cursor: pointer;
        }
        .upload-area:hover { background: #f0f2ff; }
        input[type="file"] { display: none; }
        .file-label {
            cursor: pointer;
            color: #667eea;
            font-weight: bold;
            font-size: 1.1em;
        }
        .text-area {
            width: 100%;
            min-height: 150px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-family: monospace;
            margin-bottom: 20px;
        }
        .styles {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }
        .style-btn {
            padding: 12px;
            border: 3px solid #ddd;
            border-radius: 8px;
            background: white;
            cursor: pointer;
            font-weight: bold;
        }
        .style-btn.selected { border-color: #667eea; background: #f8f9ff; }
        .gen-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.2em;
            font-weight: bold;
            cursor: pointer;
        }
        .gen-btn:hover { transform: translateY(-2px); }
        .preview { margin-top: 20px; text-align: center; }
        .preview img {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .download {
            margin-top: 15px;
            padding: 12px 30px;
            background: #4caf50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            flex: 1;
            padding: 10px;
            background: #f0f0f0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }
        .tab.active { background: #667eea; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Info-Frame Converter</h1>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('upload')">📤 Upload</button>
            <button class="tab" onclick="switchTab('text')">✍️ Text</button>
        </div>

        <div id="upload-tab" class="tab-content active">
            <div class="upload-area" onclick="document.getElementById('file').click()">
                <label class="file-label">
                    📎 Click to upload PDF, HTML, DOCX, or TXT
                </label>
                <input type="file" id="file" accept=".pdf,.html,.htm,.docx,.txt">
            </div>
        </div>

        <div id="text-tab" class="tab-content">
            <textarea id="text" class="text-area" placeholder="Or paste your text here..."></textarea>
        </div>

        <h3 style="margin-bottom: 10px;">Choose Style:</h3>
        <div class="styles">
            <button class="style-btn selected" data-style="modern" onclick="selectStyle('modern')">Modern</button>
            <button class="style-btn" data-style="classic" onclick="selectStyle('classic')">Classic</button>
            <button class="style-btn" data-style="minimalist" onclick="selectStyle('minimalist')">Minimal</button>
            <button class="style-btn" data-style="bold" onclick="selectStyle('bold')">Bold</button>
        </div>

        <button class="gen-btn" onclick="generate()">✨ Generate</button>

        <div id="preview" class="preview" style="display:none;">
            <h3>Your Info-Frame:</h3>
            <img id="img" src="">
            <br>
            <a id="download" class="download" download="infoframe.png">⬇️ Download PNG</a>
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
                document.querySelector('.tab:nth-child(1)').classList.add('active');
                document.getElementById('upload-tab').classList.add('active');
            } else {
                document.querySelector('.tab:nth-child(2)').classList.add('active');
                document.getElementById('text-tab').classList.add('active');
            }
        }

        function selectStyle(style) {
            selectedStyle = style;
            document.querySelectorAll('.style-btn').forEach(b => b.classList.remove('selected'));
            document.querySelector(`[data-style="${style}"]`).classList.add('selected');
        }

        async function generate() {
            const formData = new FormData();
            formData.append('style', selectedStyle);

            if (currentTab === 'upload') {
                const file = document.getElementById('file').files[0];
                if (!file) {
                    alert('Please select a file');
                    return;
                }
                formData.append('file', file);
            } else {
                const text = document.getElementById('text').value;
                if (!text.trim()) {
                    alert('Please enter some text');
                    return;
                }
                formData.append('text', text);
            }

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error('Generation failed');

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);

                document.getElementById('img').src = url;
                document.getElementById('download').href = url;
                document.getElementById('preview').style.display = 'block';
            } catch (err) {
                alert('Error: ' + err.message);
            }
        }
    </script>
</body>
</html>
"""

SETUP_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>HTML to PNG Setup</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f4f6fb;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .box {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 100%;
            padding: 40px 35px;
            text-align: center;
        }
        h1 {
            font-size: 2.1em;
            margin-bottom: 10px;
            color: #333;
        }
        p {
            color: #666;
            margin-bottom: 25px;
        }
        input[type="file"] {
            display: none;
        }
        label {
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
        }
        button {
            margin-top: 20px;
            padding: 14px 24px;
            border: none;
            border-radius: 10px;
            background: #4caf50;
            color: white;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
        }
        button:disabled {
            background: #a5d6a7;
            cursor: not-allowed;
        }
        #status {
            margin-top: 18px;
            min-height: 20px;
            color: #764ba2;
        }
        .preview {
            margin-top: 25px;
            display: none;
        }
        .preview img {
            max-width: 100%;
            border-radius: 12px;
            box-shadow: 0 12px 32px rgba(0,0,0,0.18);
        }
        .preview a {
            display: inline-block;
            margin-top: 12px;
            padding: 10px 20px;
            border-radius: 8px;
            background: #667eea;
            color: white;
            text-decoration: none;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="box">
        <h1>HTML → PNG</h1>
        <p>Upload a HTML file and we’ll render it to PNG using the Node converter.</p>
        <form id="convertForm">
            <input type="file" id="htmlFile" name="file" accept=".html,.htm">
            <label for="htmlFile">📎 Choose HTML file</label>
            <button type="submit" disabled id="convertBtn">Run npm convert</button>
        </form>
        <div id="status"></div>
        <div class="preview" id="preview">
            <h3 style="margin-bottom: 12px; color: #333;">Preview</h3>
            <img id="previewImg" alt="Rendered preview">
            <a id="downloadLink" download="rendered.png">⬇️ Download PNG</a>
        </div>
    </div>

    <script>
        const fileInput = document.getElementById('htmlFile');
        const convertBtn = document.getElementById('convertBtn');
        const statusEl = document.getElementById('status');
        const preview = document.getElementById('preview');
        const previewImg = document.getElementById('previewImg');
        const downloadLink = document.getElementById('downloadLink');

        fileInput.addEventListener('change', () => {
            statusEl.textContent = '';
            statusEl.style.color = '#764ba2';
            preview.style.display = 'none';
            if (fileInput.files.length) {
                convertBtn.disabled = false;
                convertBtn.textContent = 'Run npm convert';
            } else {
                convertBtn.disabled = true;
            }
        });

        document.getElementById('convertForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!fileInput.files.length) {
                statusEl.style.color = '#e74c3c';
                statusEl.textContent = 'Select a HTML file first.';
                return;
            }

            convertBtn.disabled = true;
            convertBtn.textContent = 'Converting...';
            statusEl.style.color = '#764ba2';
            statusEl.textContent = 'Running npm convert...';
            preview.style.display = 'none';

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            try {
                const response = await fetch('/convert_html', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const data = await response.json().catch(() => ({}));
                    throw new Error(data.error || 'Conversion failed');
                }

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);

                previewImg.src = url;
                downloadLink.href = url;
                preview.style.display = 'block';
                statusEl.style.color = '#4caf50';
                statusEl.textContent = 'Success! Preview ready below.';
            } catch (err) {
                statusEl.style.color = '#e74c3c';
                statusEl.textContent = err.message;
            } finally {
                convertBtn.disabled = false;
                convertBtn.textContent = 'Run npm convert';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/setup')
def setup_page():
    if not NODE_CONVERTER.exists():
        return "Node converter (render.js) not found in project directory.", 500
    return render_template_string(SETUP_HTML)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        style = request.form.get('style', 'modern')

        # Get content
        if 'file' in request.files:
            file = request.files['file']
            text = read_file_content(file)
        elif 'text' in request.form:
            text = request.form.get('text')
        else:
            return jsonify({'error': 'No input provided'}), 400

        if not text or not text.strip():
            return jsonify({'error': 'No content'}), 400

        # Trim
        if len(text) > 2000:
            text = text[:2000] + "..."

        # Generate
        img = create_image(text, style)

        # Return
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png', download_name=f'infoframe_{style}.png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/convert_html', methods=['POST'])
def convert_html_to_png():
    if not NODE_CONVERTER.exists():
        return jsonify({'error': 'render.js not found. Please ensure the Node converter is present.'}), 500

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    uploaded = request.files['file']
    filename = uploaded.filename or ''
    if not filename.lower().endswith(('.html', '.htm')):
        return jsonify({'error': 'Please upload a HTML file (.html or .htm)'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', dir=BASE_DIR) as tmp_in:
            uploaded.save(tmp_in.name)
            input_path = Path(tmp_in.name)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png', dir=BASE_DIR) as tmp_out:
            output_path = Path(tmp_out.name)

        try:
            result = subprocess.run(
                ["npm", "run", "convert", "--", str(input_path), str(output_path)],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True
            )

            if result.returncode != 0 or not output_path.exists():
                error_msg = result.stderr.strip() or result.stdout.strip() or "Conversion failed"
                return jsonify({'error': error_msg}), 500

            with output_path.open('rb') as f:
                data = io.BytesIO(f.read())
            data.seek(0)
            return send_file(
                data,
                mimetype='image/png',
                as_attachment=True,
                download_name=f"{Path(filename).stem or 'rendered'}.png"
            )
        finally:
            try:
                input_path.unlink()
            except OSError:
                pass
            try:
                output_path.unlink()
            except OSError:
                pass
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🌐 INFO-FRAME WEB APP")
    print("=" * 60)
    print("\n✨ Starting server...")
    print("🌐 Open: http://localhost:8000")
    print("📱 Or from phone: http://YOUR_IP:8000")
    print("\n⌨️  Press Ctrl+C to stop\n")
    app.run(host='0.0.0.0', port=8000, debug=False)
