#!/bin/bash
# Double-click this file to start!

clear
echo ""
echo "🎨 INFO-FRAME CONVERTER"
echo "======================="
echo ""
echo "Ready to convert your files!"
echo ""
echo "DRAG & DROP YOUR FILE HERE (or type the path):"
read -p "> " FILE

if [ ! -f "$FILE" ]; then
    echo ""
    echo "❌ File not found: $FILE"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "Choose format (png/jpg/jpeg/pdf) [default: png]:"
read -p "> " FORMAT
FORMAT=${FORMAT:-png}

echo ""
echo "Choose style (modern/classic/minimalist/bold) [default: modern]:"
read -p "> " STYLE
STYLE=${STYLE:-modern}

echo ""
echo "Converting..."
echo ""

python3 "$(dirname "$0")/convert.py" "$FILE" "$FORMAT" "$STYLE"

echo ""
echo "✨ Done! Files are in Desktop/Convecter"
echo ""
echo "Open folder? (y/n)"
read -p "> " OPEN

if [ "$OPEN" = "y" ] || [ "$OPEN" = "Y" ]; then
    open "$(dirname "$0")"
fi

echo ""
read -p "Press Enter to exit..."
