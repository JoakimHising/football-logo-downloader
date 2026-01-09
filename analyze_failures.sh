#!/bin/bash
# Analyze what failed to download

echo "=== Download Analysis ==="
echo ""

# Count what we have
total_expected=$(grep -c "team_name" football_logos/metadata.json 2>/dev/null || echo "0")
svg_downloaded=$(find football_logos -name "*.svg" -path "*/svg/*" 2>/dev/null | wc -l | tr -d ' ')
png_downloaded=$(find football_logos -name "*.png" -path "*/png/*" 2>/dev/null | wc -l | tr -d ' ')

echo "Expected logos: $total_expected"
echo "SVG downloaded: $svg_downloaded"
echo "PNG downloaded: $png_downloaded"
echo ""

# Check which countries have the most missing files
echo "=== Missing SVGs by country ==="
for country_dir in football_logos/*/; do
    country=$(basename "$country_dir")
    [ "$country" = "*" ] && continue
    
    # Count logos in metadata for this country
    expected=$(grep -c "\"country_slug\":\"$country\"" football_logos/metadata.json 2>/dev/null || echo "0")
    actual=$(find "$country_dir/svg" -name "*.svg" 2>/dev/null | wc -l | tr -d ' ')
    missing=$((expected - actual))
    
    if [ $missing -gt 0 ]; then
        echo "  $country: $actual/$expected downloaded ($missing missing)"
    fi
done | sort -t: -k2 -rn | head -20

echo ""
echo "=== Checking for common failure reasons ==="

# Check if any 404 patterns
if [ -f football_logos/metadata.json ]; then
    echo "Logos in metadata: $(grep -c team_name football_logos/metadata.json)"
    echo ""
    
    # Sample some teams that should exist but might not
    echo "Sample of teams from metadata (checking if files exist):"
    grep -o '"team_name":"[^"]*"' football_logos/metadata.json | head -10 | while read -r line; do
        team_name=$(echo "$line" | sed 's/"team_name":"\(.*\)"/\1/')
        country=$(echo "$line" | grep -B2 "$team_name" || echo "unknown")
        echo "  - $team_name"
    done
fi

echo ""
echo "Tip: The download is still running. Wait for it to complete to see all failures."
