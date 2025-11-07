#!/usr/bin/env bash
set -euo pipefail

# Simple wrapper for converting HTML files into PNG info-frames.

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
    echo "Usage: $(basename "$0") <file.html> [style]"
    echo "Styles: modern (default), classic, minimalist, bold"
    exit 1
fi

input_file="$1"
style="${2:-}"

if [ ! -f "$input_file" ]; then
    echo "❌ File not found: $input_file"
    exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
converter="$script_dir/convert.py"

if [ ! -f "$converter" ]; then
    echo "❌ Missing converter script at $converter"
    exit 1
fi

if [ -z "$style" ]; then
    python3 "$converter" "$input_file" png
else
    python3 "$converter" "$input_file" png "$style"
fi
