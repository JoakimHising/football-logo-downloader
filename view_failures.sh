#!/bin/bash
# View failure analysis after download completes

echo "=== Failure Analysis ==="
echo ""

if [ ! -f "download.log" ]; then
    echo "No download.log found."
    echo ""
    echo "The download is running in your terminal without logging."
    echo "Failures are printed with '✗' but scrolling by."
    echo ""
    echo "Common failure reasons:"
    echo "  • 404 errors: PNG files don't exist on server (this is normal)"
    echo "  • 429 errors: Rate limiting (the script retries automatically)"
    echo "  • No SVG available: Some logos only have PNG versions"
    echo ""
    echo "To capture failures for analysis:"
    echo "  1. Let current download finish OR stop it: kill $(pgrep -f download_football_logos.py)"
    echo "  2. Restart with logging: python download_football_logos.py --format svg 2>&1 | tee download.log"
    echo "  3. Run this script again: ./view_failures.sh"
else
    echo "Total failures: $(grep -c '✗' download.log)"
    echo ""
    echo "=== Failure Breakdown ==="
    echo "404 errors (not found): $(grep -c '404' download.log)"
    echo "429 errors (rate limit): $(grep -c '429' download.log)"
    echo "Other errors: $(grep '✗' download.log | grep -v '404' | grep -v '429' | wc -l | tr -d ' ')"
    echo ""
    echo "=== Last 10 Failures ==="
    grep '✗' download.log | tail -10
    echo ""
    echo "To see all failures: grep '✗' download.log"
fi
