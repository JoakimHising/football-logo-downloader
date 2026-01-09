#!/bin/bash
# Quick script to open the terms of service pages

echo "Opening football-logos.cc license information..."
echo ""
echo "Main license page:"
echo "https://football-logos.cc/license/"
echo ""
echo "Main website:"
echo "https://football-logos.cc"
echo ""
echo "Robots.txt (automated access policy):"
echo "https://football-logos.cc/robots.txt"
echo ""

# Automatically open in browser (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    read -p "Open these pages in your browser? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "https://football-logos.cc/license/"
        sleep 1
        open "https://football-logos.cc"
        sleep 1
        open "https://football-logos.cc/robots.txt"
    fi
fi
