# Quick Start Guide

## Run Downloader in Background

### Simple Background Run (Recommended)
```bash
source venv/bin/activate
nohup python download_football_logos.py --format svg --delay 1.0 > download.log 2>&1 &
echo $! > download.pid
```

**Check progress:**
```bash
tail -f download.log
```

**Stop the download:**
```bash
kill $(cat download.pid)
```

### Using screen
```bash
screen -S logo_download
source venv/bin/activate
python download_football_logos.py --format svg
# Press Ctrl+A, then D to detach
# Later: screen -r logo_download to reattach
```

## Common Commands

### Download All Logos
```bash
source venv/bin/activate
python download_football_logos.py --format svg --delay 1.0
```

### Download Specific Country
```bash
source venv/bin/activate
python download_football_logos.py --country sweden --format svg
```

### Convert All to Coloring Pages
```bash
./convert_all_to_coloring.sh
```

### View and Print Coloring Pages
```bash
# Open the viewer
open coloring_page_viewer.html

# Or with a web server (if CORS issues)
python -m http.server 8000
# Visit: http://localhost:8000/coloring_page_viewer.html
```

**In the viewer:**
1. Click a country in the sidebar to filter
2. Click logos to select them (or use "Select All")
3. Click "Print Selected" button
4. In print dialog, choose "2 pages per sheet" for 2 per page

### Check What's Downloaded
```bash
# Count SVG files
find football_logos -name "*.svg" -path "*/svg/*" | wc -l

# Count coloring pages
find football_logos -name "*.svg" -path "*/coloring-pages/*" | wc -l

# List all countries with logos
ls football_logos/
```

## Recommended Settings

For reliable downloads without rate limiting:
```bash
python download_football_logos.py \
  --format svg \
  --delay 1.0 \
  --workers 2
```

For maximum speed (may hit rate limits):
```bash
python download_football_logos.py \
  --format svg \
  --delay 0.3 \
  --workers 5
```

## File Locations

- **Downloaded logos:** `football_logos/[country]/svg/`
- **Coloring pages:** `football_logos/[country]/coloring-pages/`
- **Download log:** `download.log` (if running with nohup)
- **Process ID:** `download.pid` (if running with nohup)
