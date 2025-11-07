#!/bin/bash
# Info-Frame Setup Script
# Installs all dependencies and makes scripts executable

echo "🎨 INFO-FRAME SETUP"
echo "=" | awk '{s=sprintf("%50s",""); gsub(/ /,"=",$0); print}'

echo ""
echo "📦 Installing Python dependencies..."
echo ""

pip3 install --upgrade pip --quiet
pip3 install PyPDF2 Pillow Flask --quiet

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "⚠️  Some dependencies may have failed to install"
    echo "   You can try manually: pip3 install PyPDF2 Pillow Flask"
fi

echo ""
echo "🔧 Making scripts executable..."
echo ""

chmod +x pdf_to_frames.py 2>/dev/null
chmod +x webapp_infoframe.py 2>/dev/null
chmod +x desktop_infoframe.py 2>/dev/null
chmod +x launch_webapp.sh 2>/dev/null
chmod +x launch_desktop.sh 2>/dev/null

echo "✓ Scripts are now executable"

echo ""
echo "✨ Setup complete!"
echo ""
echo "You can now run:"
echo "  1. Command line: python3 pdf_to_frames.py <file> [format] [style]"
echo "  2. Web app:      ./launch_webapp.sh  (or python3 webapp_infoframe.py)"
echo "  3. Desktop app:  ./launch_desktop.sh (or python3 desktop_infoframe.py)"
echo ""
