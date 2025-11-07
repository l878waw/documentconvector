#!/bin/bash
# Info-Frame Quick Converter
# Drag your text file here or run with file path

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📄 INFO-FRAME CONVERTER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $# -eq 0 ]; then
    echo "📂 Select your text file:"
    echo ""
    
    # List text files on Desktop
    cd ~/Desktop
    select file in *.txt; do
        if [ -n "$file" ]; then
            python3 ~/Desktop/quick_convert.py "$file"
            break
        else
            echo "Invalid selection"
        fi
    done
else
    # File was dragged onto script
    python3 ~/Desktop/quick_convert.py "$1"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Press Enter to close..."
