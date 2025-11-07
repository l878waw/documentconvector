#!/usr/bin/env python3
"""
Info-Frame Desktop App - GUI application for creating info-frames
Run with: python3 desktop_infoframe.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageDraw, ImageFont, ImageTk
import textwrap
from pathlib import Path
import PyPDF2
import io

class InfoFrameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Info-Frame Converter")
        self.root.geometry("900x800")
        self.root.configure(bg='#f0f0f0')

        self.selected_style = tk.StringVar(value="modern")
        self.current_image = None
        self.content_text = ""

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg='#667eea', height=100)
        header.pack(fill='x', pady=(0, 20))

        title = tk.Label(
            header,
            text="🎨 Info-Frame Converter",
            font=('Helvetica', 28, 'bold'),
            bg='#667eea',
            fg='white'
        )
        title.pack(pady=20)

        # Main container
        main = tk.Frame(self.root, bg='#f0f0f0')
        main.pack(fill='both', expand=True, padx=20, pady=10)

        # Input section
        input_frame = tk.LabelFrame(
            main,
            text="📄 Input",
            font=('Helvetica', 14, 'bold'),
            bg='#f0f0f0',
            fg='#333'
        )
        input_frame.pack(fill='both', expand=True, pady=(0, 10))

        # File upload button
        btn_frame = tk.Frame(input_frame, bg='#f0f0f0')
        btn_frame.pack(pady=10)

        upload_btn = tk.Button(
            btn_frame,
            text="📎 Upload File (PDF/TXT/HTML)",
            command=self.upload_file,
            font=('Helvetica', 12),
            bg='#667eea',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        upload_btn.pack(side='left', padx=5)

        self.file_label = tk.Label(
            btn_frame,
            text="No file selected",
            font=('Helvetica', 10),
            bg='#f0f0f0',
            fg='#666'
        )
        self.file_label.pack(side='left', padx=10)

        # Text input
        tk.Label(
            input_frame,
            text="Or paste text here:",
            font=('Helvetica', 11),
            bg='#f0f0f0',
            fg='#666'
        ).pack(anchor='w', padx=10, pady=(10, 5))

        self.text_area = scrolledtext.ScrolledText(
            input_frame,
            height=8,
            font=('Courier', 10),
            wrap='word'
        )
        self.text_area.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Style selection
        style_frame = tk.LabelFrame(
            main,
            text="🎨 Style",
            font=('Helvetica', 14, 'bold'),
            bg='#f0f0f0',
            fg='#333'
        )
        style_frame.pack(fill='x', pady=(0, 10))

        styles_container = tk.Frame(style_frame, bg='#f0f0f0')
        styles_container.pack(pady=10)

        styles = [
            ("Modern", "modern", "#e94560"),
            ("Classic", "classic", "#8b4513"),
            ("Minimalist", "minimalist", "#000000"),
            ("Bold", "bold", "#ff0066")
        ]

        for i, (name, value, color) in enumerate(styles):
            rb = tk.Radiobutton(
                styles_container,
                text=name,
                variable=self.selected_style,
                value=value,
                font=('Helvetica', 11, 'bold'),
                bg='#f0f0f0',
                fg=color,
                selectcolor='#e8e8e8',
                activebackground='#f0f0f0',
                cursor='hand2'
            )
            rb.grid(row=0, column=i, padx=15, pady=5)

        # Generate button
        generate_btn = tk.Button(
            main,
            text="✨ Generate Info-Frame",
            command=self.generate,
            font=('Helvetica', 14, 'bold'),
            bg='#667eea',
            fg='white',
            padx=30,
            pady=15,
            cursor='hand2'
        )
        generate_btn.pack(pady=10)

        # Preview section
        preview_frame = tk.LabelFrame(
            main,
            text="👁️ Preview",
            font=('Helvetica', 14, 'bold'),
            bg='#f0f0f0',
            fg='#333'
        )
        preview_frame.pack(fill='both', expand=True, pady=(0, 10))

        self.preview_label = tk.Label(
            preview_frame,
            text="Preview will appear here",
            bg='white',
            fg='#999',
            font=('Helvetica', 12)
        )
        self.preview_label.pack(fill='both', expand=True, padx=10, pady=10)

        # Save button
        self.save_btn = tk.Button(
            main,
            text="💾 Save Image",
            command=self.save_image,
            font=('Helvetica', 12),
            bg='#4caf50',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            state='disabled'
        )
        self.save_btn.pack(pady=(0, 10))

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Select file",
            filetypes=[
                ("All supported", "*.pdf *.txt *.html *.htm"),
                ("PDF files", "*.pdf"),
                ("Text files", "*.txt"),
                ("HTML files", "*.html *.htm"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            if file_path.endswith('.pdf'):
                self.content_text = self.extract_text_from_pdf(file_path)
            elif file_path.endswith(('.html', '.htm')):
                self.content_text = self.extract_text_from_html(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.content_text = f.read()

            filename = Path(file_path).name
            self.file_label.config(text=f"✓ {filename}", fg='#4caf50')
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', self.content_text)

        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{str(e)}")

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"PDF reading error: {str(e)}")

    def extract_text_from_html(self, html_path):
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

            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            parser = HTMLTextExtractor()
            parser.feed(html_content)
            return '\n'.join(parser.text)
        except Exception as e:
            raise Exception(f"HTML reading error: {str(e)}")

    def get_style_colors(self, style):
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

    def create_infoframe(self, text, style):
        """Create info-frame image"""
        colors = self.get_style_colors(style)

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

        return img

    def generate(self):
        # Get text from text area
        text = self.text_area.get('1.0', tk.END).strip()

        if not text:
            messagebox.showwarning("Warning", "Please enter some text or upload a file")
            return

        try:
            # Limit text length
            if len(text) > 2000:
                text = text[:2000] + "..."

            style = self.selected_style.get()

            # Generate image
            self.current_image = self.create_infoframe(text, style)

            # Create thumbnail for preview
            preview_img = self.current_image.copy()
            preview_img.thumbnail((400, 533), Image.Resampling.LANCZOS)

            # Display preview
            photo = ImageTk.PhotoImage(preview_img)
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo  # Keep reference

            # Enable save button
            self.save_btn.config(state='normal')

            messagebox.showinfo("Success", "Info-frame generated successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Generation failed:\n{str(e)}")

    def create_html(self, text, style):
        """Create HTML version of info-frame"""
        colors = self.get_style_colors(style)

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

    def save_image(self):
        if not self.current_image:
            messagebox.showwarning("Warning", "Please generate an image first")
            return

        # Get text content for HTML export
        text = self.text_area.get('1.0', tk.END).strip()
        if len(text) > 2000:
            text = text[:2000] + "..."

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("PDF files", "*.pdf"),
                ("HTML files", "*.html"),
                ("All files", "*.*")
            ],
            initialfile=f"infoframe_{self.selected_style.get()}"
        )

        if file_path:
            try:
                if file_path.endswith('.html'):
                    # Save as HTML
                    html_content = self.create_html(text, self.selected_style.get())
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    messagebox.showinfo("Success", f"HTML file saved to:\n{file_path}")
                elif file_path.endswith('.pdf'):
                    img_rgb = self.current_image.convert('RGB')
                    img_rgb.save(file_path, "PDF", resolution=100.0)
                    messagebox.showinfo("Success", f"PDF saved to:\n{file_path}")
                elif file_path.endswith(('.jpg', '.jpeg')):
                    img_rgb = self.current_image.convert('RGB')
                    img_rgb.save(file_path, "JPEG", quality=95)
                    messagebox.showinfo("Success", f"JPEG saved to:\n{file_path}")
                else:
                    # Default to PNG
                    if not file_path.endswith('.png'):
                        file_path += '.png'
                    self.current_image.save(file_path, "PNG")
                    messagebox.showinfo("Success", f"PNG saved to:\n{file_path}")

            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}")

def main():
    root = tk.Tk()
    app = InfoFrameApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
