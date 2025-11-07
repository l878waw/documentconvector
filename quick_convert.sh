#!/bin/bash
# Quick Converter - Drag & Drop Your File Here!

clear
echo "🎨 QUICK CONVERTER"
echo "================="
echo ""

# Check if file provided
if [ $# -eq 0 ]; then
    echo "Usage: Drag and drop a file onto this script"
    echo "Or: ./quick_convert.sh <file> [format] [style]"
    echo ""
    echo "Formats: png, jpg, jpeg, pdf"
    echo "Styles: modern, classic, minimalist, bold"
    echo ""
    exit 1
fi

FILE="$1"
FORMAT="${2:-png}"
STYLE="${3:-modern}"

cd "$(dirname "$0")"

echo "📄 Input: $FILE"
echo "📦 Format: $FORMAT"
echo "🎨 Style: $STYLE"
echo ""

python3 convert.py "$FILE" "$FORMAT" "$STYLE"

echo ""
echo "✨ Done! Check Desktop/Convecter folder"
echo ""
