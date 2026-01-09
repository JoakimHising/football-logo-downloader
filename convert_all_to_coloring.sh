#!/bin/bash
# Convert all downloaded SVG logos to coloring pages
# Output structure: football_logos/[country]/coloring-pages/[name]_coloring.svg

set -e

LOGOS_DIR="football_logos"
PYTHON_SCRIPT="logo_to_coloring_page.py"

# Activate virtual environment
source venv/bin/activate

# Count total SVG files
TOTAL=$(find "$LOGOS_DIR" -name "*.svg" -path "*/svg/*" | wc -l | tr -d ' ')
echo "Found $TOTAL logos to convert"
echo "================================"

CONVERTED=0
FAILED=0

# Find all SVG files in country/svg/ folders
while IFS= read -r svg_file; do
    # Extract country name from path
    # Example: football_logos/england/svg/Arsenal.svg -> england
    country=$(echo "$svg_file" | cut -d'/' -f2)

    # Extract filename without extension
    filename=$(basename "$svg_file" .svg)

    # Create output directory
    output_dir="$LOGOS_DIR/$country/coloring-pages"
    mkdir -p "$output_dir"

    # Set output file path
    output_file="$output_dir/${filename}_coloring.svg"

    # Skip if already exists
    if [ -f "$output_file" ]; then
        echo "[$((CONVERTED + FAILED + 1))/$TOTAL] Skipped (exists): $country/$filename"
        ((CONVERTED++))
        continue
    fi

    # Convert the logo
    echo "[$((CONVERTED + FAILED + 1))/$TOTAL] Converting: $country/$filename"
    if python "$PYTHON_SCRIPT" "$svg_file" "$output_file" > /dev/null 2>&1; then
        ((CONVERTED++))
    else
        ((FAILED++))
        echo "  ERROR: Failed to convert $svg_file"
    fi

done < <(find "$LOGOS_DIR" -name "*.svg" -path "*/svg/*")

echo "================================"
echo "Conversion complete!"
echo "  Converted: $CONVERTED"
echo "  Failed: $FAILED"
echo "  Total: $TOTAL"
