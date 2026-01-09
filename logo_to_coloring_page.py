#!/usr/bin/env python3
"""
Logo to Coloring Page Converter

Converts colored logos (SVG or PNG) to clean black-and-white line art
suitable for coloring pages.

Usage:
    python logo_to_coloring_page.py input.svg output.svg
    python logo_to_coloring_page.py input.png output.svg
    python logo_to_coloring_page.py input.svg output.svg --padding 50
"""

import cv2
import numpy as np
import subprocess
import argparse
import os
import sys
import re
from pathlib import Path

def svg_to_png(svg_path, png_path, width=1000):
    """Convert SVG to PNG using Inkscape"""
    cmd = [
        'inkscape', svg_path,
        '--export-type=png',
        f'--export-filename={png_path}',
        f'--export-width={width}',
        '--export-background=white'
    ]
    subprocess.run(cmd, capture_output=True)
    return os.path.exists(png_path)

def detect_edges(img, canny_low=50, canny_high=150, dilate_size=2):
    """Apply Canny edge detection"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, canny_low, canny_high)
    
    if dilate_size > 0:
        kernel = np.ones((dilate_size, dilate_size), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
    
    return edges

def add_padding(img, padding, color=(255, 255, 255)):
    """Add white padding around image"""
    return cv2.copyMakeBorder(
        img, padding, padding, padding, padding,
        cv2.BORDER_CONSTANT, value=color
    )

def trace_to_svg(pbm_path, svg_path, turdsize=5, alphamax=0.8):
    """Use potrace to convert bitmap to SVG"""
    cmd = [
        'potrace', pbm_path,
        '-s', '-o', svg_path,
        '--flat',
        f'--turdsize={turdsize}',
        f'--alphamax={alphamax}'
    ]
    subprocess.run(cmd, capture_output=True)
    return os.path.exists(svg_path)

def clean_svg(svg_path, output_path):
    """Clean up the SVG: fix dimensions, add white background"""
    with open(svg_path, 'r') as f:
        svg = f.read()
    
    # Extract dimensions from viewBox
    viewbox_match = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if viewbox_match:
        width = viewbox_match.group(1).replace('.000000', '')
        height = viewbox_match.group(2).replace('.000000', '')
    else:
        width, height = '1000', '1000'
    
    # Fix dimensions (remove 'pt' units)
    svg = re.sub(r'width="[\d.]+pt"', f'width="{width}"', svg)
    svg = re.sub(r'height="[\d.]+pt"', f'height="{height}"', svg)
    
    # Remove DOCTYPE
    svg = re.sub(r'<!DOCTYPE[^>]+>', '', svg)
    
    # Add white background
    svg = re.sub(
        r'(<g transform="[^"]+"\s*fill="#000000" stroke="none">)',
        r'<rect width="100%" height="100%" fill="white"/>\1',
        svg
    )
    
    with open(output_path, 'w') as f:
        f.write(svg)

def convert_logo(input_path, output_path, padding=30, canny_low=50, canny_high=150, 
                 dilate_size=2, turdsize=5, alphamax=0.8, png_width=1000):
    """
    Main conversion function.
    
    Args:
        input_path: Path to input SVG or PNG
        output_path: Path to output SVG
        padding: White padding to add around logo (pixels)
        canny_low: Canny edge detection low threshold
        canny_high: Canny edge detection high threshold  
        dilate_size: Size of dilation kernel (0 to disable)
        turdsize: Potrace turdsize (removes specks smaller than this)
        alphamax: Potrace corner threshold
        png_width: Width to render SVG to PNG
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    # Create temp directory
    temp_dir = Path('/tmp/coloring_page')
    temp_dir.mkdir(exist_ok=True)
    
    # Step 1: Get PNG (convert SVG if needed)
    if input_path.suffix.lower() == '.svg':
        print(f"Converting SVG to PNG...")
        png_path = temp_dir / 'input.png'
        if not svg_to_png(str(input_path), str(png_path), png_width):
            print("Error: Failed to convert SVG to PNG. Is Inkscape installed?")
            return False
    else:
        png_path = input_path
    
    # Step 2: Load image
    print(f"Loading image...")
    img = cv2.imread(str(png_path))
    if img is None:
        print(f"Error: Could not load image {png_path}")
        return False
    
    h, w = img.shape[:2]
    print(f"  Image size: {w}x{h}")
    
    # Step 3: Add padding
    print(f"Adding {padding}px padding...")
    img_padded = add_padding(img, padding)
    
    # Step 4: Edge detection
    print(f"Detecting edges (Canny {canny_low}-{canny_high})...")
    edges = detect_edges(img_padded, canny_low, canny_high, dilate_size)
    
    # Step 5: Invert for potrace (black lines on white)
    edges_inv = cv2.bitwise_not(edges)
    
    # Step 6: Save as PBM for potrace
    pbm_path = temp_dir / 'edges.pbm'
    png_edges_path = temp_dir / 'edges.png'
    cv2.imwrite(str(png_edges_path), edges_inv)
    subprocess.run(['convert', str(png_edges_path), '-threshold', '50%', str(pbm_path)], 
                   capture_output=True)
    
    # Step 7: Trace with potrace
    print(f"Tracing to vector (turdsize={turdsize}, alphamax={alphamax})...")
    temp_svg = temp_dir / 'traced.svg'
    if not trace_to_svg(str(pbm_path), str(temp_svg), turdsize, alphamax):
        print("Error: Potrace failed. Is potrace installed?")
        return False
    
    # Step 8: Clean up SVG
    print(f"Cleaning up SVG...")
    clean_svg(str(temp_svg), str(output_path))
    
    print(f"✓ Created: {output_path}")
    
    # Also create PNG preview
    png_output = output_path.with_suffix('.png')
    subprocess.run([
        'inkscape', str(output_path),
        '--export-type=png',
        f'--export-filename={png_output}',
        f'--export-width={w + 2*padding}'
    ], capture_output=True)
    
    if png_output.exists():
        print(f"✓ Created: {png_output}")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Convert logo to coloring page',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s logo.svg coloring_page.svg
    %(prog)s logo.png coloring_page.svg --padding 50
    %(prog)s logo.svg output.svg --canny-low 30 --canny-high 100
        """
    )
    parser.add_argument('input', help='Input SVG or PNG file')
    parser.add_argument('output', help='Output SVG file')
    parser.add_argument('--padding', type=int, default=30,
                        help='White padding around logo (default: 30)')
    parser.add_argument('--canny-low', type=int, default=50,
                        help='Canny edge detection low threshold (default: 50)')
    parser.add_argument('--canny-high', type=int, default=150,
                        help='Canny edge detection high threshold (default: 150)')
    parser.add_argument('--dilate', type=int, default=2,
                        help='Edge dilation size, 0 to disable (default: 2)')
    parser.add_argument('--turdsize', type=int, default=5,
                        help='Potrace speck removal size (default: 5)')
    parser.add_argument('--alphamax', type=float, default=0.8,
                        help='Potrace corner threshold (default: 0.8)')
    parser.add_argument('--width', type=int, default=1000,
                        help='Width for SVG to PNG conversion (default: 1000)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    success = convert_logo(
        args.input,
        args.output,
        padding=args.padding,
        canny_low=args.canny_low,
        canny_high=args.canny_high,
        dilate_size=args.dilate,
        turdsize=args.turdsize,
        alphamax=args.alphamax,
        png_width=args.width
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
