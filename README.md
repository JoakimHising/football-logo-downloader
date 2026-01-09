# Football Logo Downloader & Coloring Page Converter

Download football club logos from football-logos.cc and convert them to black-and-white coloring pages.

## Features

- Download 2,100+ football logos from 130+ countries
- Automatic rate limiting and retry logic
- Convert logos to clean line art for coloring pages
- Organized folder structure by country

## Setup

### 1. Create a virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# Or on Windows: venv\Scripts\activate
```

### 2. Install Python packages
```bash
pip install -r requirements.txt
```

### 3. Install system dependencies

#### On macOS:
```bash
brew install inkscape potrace imagemagick
```

#### On Ubuntu/Debian:
```bash
sudo apt-get install inkscape potrace imagemagick
```

#### On Windows:
Download and install:
- Inkscape: https://inkscape.org/release/
- Potrace: http://potrace.sourceforge.net/#downloading
- ImageMagick: https://imagemagick.org/script/download.php

---

## Part 1: Download Football Logos

### Quick Start

List available countries:
```bash
source venv/bin/activate
python download_football_logos.py --list-countries
```

Download all logos:
```bash
source venv/bin/activate
python download_football_logos.py
```

### Running the Downloader in the Background

**Option 1: Using `nohup` (Recommended)**
```bash
source venv/bin/activate
nohup python download_football_logos.py > download.log 2>&1 &
echo $! > download.pid
```

Check progress:
```bash
tail -f download.log
```

Stop the download:
```bash
kill $(cat download.pid)
```

**Option 2: Using `screen` (For long-running downloads)**
```bash
# Start a new screen session
screen -S logo_download

# Inside screen, run the download
source venv/bin/activate
python download_football_logos.py

# Detach from screen: Press Ctrl+A, then D

# Reattach later to check progress
screen -r logo_download
```

**Option 3: Using `tmux`**
```bash
# Start a new tmux session
tmux new -s logo_download

# Inside tmux, run the download
source venv/bin/activate
python download_football_logos.py

# Detach from tmux: Press Ctrl+B, then D

# Reattach later
tmux attach -t logo_download
```

### Download Options

```bash
# Download logos from a specific country
python download_football_logos.py --country sweden

# Download only SVG files (faster, no rate limiting issues)
python download_football_logos.py --format svg

# Download with slower rate (more reliable, less likely to hit rate limits)
python download_football_logos.py --delay 1.0 --workers 3

# Download high-resolution PNGs
python download_football_logos.py --format png --size 1500

# Download to a custom directory
python download_football_logos.py --output-dir my_logos
```

### Download Script Options

| Option | Default | Description |
|--------|---------|-------------|
| `--output-dir` | `./football_logos` | Output directory |
| `--format` | `both` | Image format: `png`, `svg`, or `both` |
| `--size` | `512` | PNG size: 64, 128, 256, 512, 700, 1500, 3000 |
| `--country` | All | Download specific country (e.g., "england", "sweden") |
| `--workers` | `5` | Number of parallel downloads |
| `--delay` | `0.5` | Delay between requests (seconds) |
| `--list-countries` | - | List all available countries and exit |

### Examples

```bash
# Download all logos (this may take a while and hit rate limits)
python download_football_logos.py

# Download Swedish clubs only
python download_football_logos.py --country sweden

# Download SVG only (recommended, no rate limits on SVG)
python download_football_logos.py --format svg --delay 0.3

# Download with conservative settings to avoid rate limiting
python download_football_logos.py --delay 1.0 --workers 2

# Download multiple countries sequentially
for country in sweden england spain; do
  python download_football_logos.py --country $country --format svg
  sleep 5
done
```

### Folder Structure

Downloaded logos are organized as:
```
football_logos/
├── metadata.json           # Download metadata
├── england/
│   ├── svg/
│   │   ├── Arsenal.svg
│   │   ├── Chelsea.svg
│   │   └── ...
│   └── png/
│       ├── Arsenal.png
│       └── ...
├── spain/
│   ├── svg/
│   └── png/
└── [130 countries...]
```

### Rate Limiting

The website implements rate limiting. The script includes:
- **Automatic retry** with exponential backoff (2s, 4s, 8s)
- **Delay between requests** (default 0.5s)
- **Reduced workers** to avoid overwhelming the server

If you encounter too many rate limit errors:
```bash
# Use more conservative settings
python download_football_logos.py --delay 2.0 --workers 1 --format svg
```

---

## Part 2: Convert Logos to Coloring Pages

### Convert All Downloaded Logos

```bash
# Convert all SVG logos to coloring pages
./convert_all_to_coloring.sh
```

This script:
- Converts all logos in `football_logos/*/svg/` to coloring pages
- Creates output in `football_logos/*/coloring-pages/`
- Skips already converted files
- Shows progress during conversion

### Convert Individual Logo

```bash
source venv/bin/activate

# Basic usage
python logo_to_coloring_page.py input.svg output.svg

# Example with downloaded logo
python logo_to_coloring_page.py \
  football_logos/england/svg/Arsenal.svg \
  football_logos/england/coloring-pages/Arsenal_coloring.svg
```

### Advanced Coloring Page Options

```bash
# With more white padding around logo
python logo_to_coloring_page.py input.svg output.svg --padding 50

# Adjust edge detection (lower values = more edges detected)
python logo_to_coloring_page.py input.svg output.svg --canny-low 30 --canny-high 100

# Thicker lines
python logo_to_coloring_page.py input.svg output.svg --dilate 3

# Remove more small specks
python logo_to_coloring_page.py input.svg output.svg --turdsize 10
```

### Coloring Page Options

| Option | Default | Description |
|--------|---------|-------------|
| `--padding` | 30 | White padding around logo (pixels) |
| `--canny-low` | 50 | Edge detection low threshold |
| `--canny-high` | 150 | Edge detection high threshold |
| `--dilate` | 2 | Line thickness (0 to disable) |
| `--turdsize` | 5 | Remove specks smaller than this |
| `--alphamax` | 0.8 | Corner smoothing (0-1.34) |
| `--width` | 1000 | Render width for SVG input |

### Tuning Tips

- **Lines too thin?** Increase `--dilate` (try 3-4)
- **Too much noise?** Increase `--turdsize` (try 10-15)
- **Missing edges?** Lower `--canny-low` (try 30-40)
- **Unwanted edges?** Raise `--canny-high` (try 200-250)

---

## Part 3: View and Print Coloring Pages

### Open the Viewer

**Option 1: Double-click to open (easiest)**
```bash
open coloring_page_viewer.html
# Or just double-click the file in Finder
```

**Option 2: If you get CORS errors, use a local web server**
```bash
python -m http.server 8000
# Then visit: http://localhost:8000/coloring_page_viewer.html
```

### Using the Viewer

The HTML viewer provides an intuitive interface to browse, select, and print your coloring pages:

**Navigation:**
- 🌍 **Sidebar**: Click any country to filter logos (e.g., England, Spain, Italy)
- 🔍 **Search**: Type in the search box to filter countries
- 📂 **All Countries**: Click to view all logos at once

**Selection:**
- ✅ **Click logo card** or checkbox to select individual logos
- ⬜ **Select All**: Select all visible logos (respects country filter)
- ❌ **Deselect All**: Clear all selections
- 📊 **Counter**: Shows how many logos you've selected

**Printing:**
1. Select your desired logos (click cards or use Select All)
2. Click the **🖨️ Print Selected** button
3. In the print dialog, adjust "Pages per sheet" setting:
   - **1 page per sheet** - One logo per page, full size (default, best for coloring)
   - **2 pages per sheet** - Two logos per page
   - **4 pages per sheet** - Four logos per page
   - **6 pages per sheet** - Six logos per page
4. Choose orientation and margins:
   - Portrait for 1 per page
   - Landscape for 2+ per page
   - Adjust margins if needed
5. Print or save as PDF

### Keyboard Shortcuts

- `Ctrl/Cmd + P` - Print selected logos
- `Ctrl/Cmd + A` - Select all visible logos
- `Escape` - Deselect all

### Features

✨ **Smart Loading**: Automatically detects which coloring pages exist
📱 **Responsive**: Works on desktop, tablet, and mobile
🖨️ **Print-Optimized**: Clean, full-page print layout
🔄 **Auto-Update**: New coloring pages appear automatically
💾 **No Installation**: Pure HTML, runs in any browser

### Printing Tips

**For best results:**
- Select logos before printing (only selected logos will print)
- **Use your browser's "Pages per sheet" setting** to control layout:
  - **1 per page**: Full size, best for coloring
  - **2 per page**: Perfect balance of size and paper efficiency
  - **4-6 per page**: Great for variety sheets or smaller projects

**Recommended print settings:**
```
Pages per sheet: 1 (for full-size coloring pages)
Orientation: Portrait (1 per page) or Landscape (2+ per page)
Margins: Minimum or None
Quality: Best
```

**How to adjust "Pages per sheet":**
- **macOS**: In print dialog, look for "Layout" section → "Pages per Sheet"
- **Windows**: In print dialog, look for "Multiple" or "Pages per sheet" option
- **Chrome/Edge**: Click "More settings" → "Pages per sheet"

### Troubleshooting

**Logos not appearing:**
- Make sure you've run `./convert_all_to_coloring.sh` to generate coloring pages
- Check that `football_logos/` folder exists with coloring-pages subdirectories

**Page is blank:**
- Open browser console (F12) to check for errors
- If you see CORS errors, use Option 2 (local web server)

**Print shows all logos:**
- Make sure you selected logos before clicking Print Selected
- Check that selected logos have blue borders

**Country list is empty:**
- Verify `football_logos/metadata.json` exists
- Make sure you're opening from the project directory

---

## Complete Folder Structure

After downloading and converting:
```
football_logos/
├── metadata.json
├── england/
│   ├── svg/                    # Original SVG logos
│   │   ├── Arsenal.svg
│   │   ├── Chelsea.svg
│   │   └── ...
│   ├── png/                    # Original PNG logos (if downloaded)
│   │   ├── Arsenal.png
│   │   └── ...
│   └── coloring-pages/         # Converted coloring pages
│       ├── Arsenal_coloring.svg
│       ├── Arsenal_coloring.png
│       ├── Chelsea_coloring.svg
│       ├── Chelsea_coloring.png
│       └── ...
├── spain/
│   ├── svg/
│   ├── png/
│   └── coloring-pages/
└── [130 countries...]
```

---

## Complete Workflow Example

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Download logos in the background
nohup python download_football_logos.py --format svg --delay 1.0 > download.log 2>&1 &

# 3. Check progress (in another terminal)
tail -f download.log

# 4. Once download completes, convert to coloring pages
./convert_all_to_coloring.sh

# 5. Open the viewer to browse and print
open coloring_page_viewer.html

# 6. Your coloring pages are ready!
ls football_logos/*/coloring-pages/
```

---

## Troubleshooting

### Rate Limiting Issues
If you see many "429 Too Many Requests" errors:
```bash
# Use slower, more conservative settings
python download_football_logos.py --delay 2.0 --workers 1 --format svg
```

### Conversion Errors
If coloring page conversion fails:
- Check that Inkscape, Potrace, and ImageMagick are installed
- Try running: `inkscape --version`, `potrace --version`, `magick --version`

### Virtual Environment Issues
If packages aren't found:
```bash
# Make sure you activated the virtual environment
source venv/bin/activate
# Reinstall packages
pip install -r requirements.txt
```

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `download_football_logos.py` | Download logos from football-logos.cc |
| `logo_to_coloring_page.py` | Convert single logo to coloring page |
| `convert_all_to_coloring.sh` | Batch convert all downloaded logos |
| `coloring_page_viewer.html` | Browse, select, and print coloring pages |

---

## License & Terms of Service

### Football-Logos.cc License

According to football-logos.cc license terms:

**✅ Allowed Uses:**
- Informational, editorial, and educational purposes
- Fan-based projects and personal use
- Non-commercial design work

**❌ Prohibited Uses:**
- Commercial products or merchandise
- Branding or promotional materials
- Implying affiliation or endorsement

**Ownership:**
- All logos are intellectual property of their respective clubs, leagues, and associations
- Football-logos.cc is a curated reference resource
- Rights holders can request removal at any time

### Usage Guidelines

**For Coloring Pages:**
- ✅ Personal use and educational purposes
- ✅ Free distribution for non-commercial purposes
- ✅ Fan projects and hobby use
- ❌ Selling coloring books or commercial products
- ❌ Using in business/promotional materials

**Recommended Attribution:**
Include in your coloring pages:
- "Logos courtesy of [Club Name]"
- "All trademarks belong to their respective owners"

### Automated Download Policy

- The site allows automated access (robots.txt: `Allow: /`)
- Rate limiting is implemented to prevent server overload
- Use respectful delays (0.5-2.0 seconds) between requests
- Limit concurrent workers (2-5 maximum)

### This Project

This tool is provided for educational and personal use. Users are responsible for ensuring their usage complies with football-logos.cc terms and applicable copyright laws.
