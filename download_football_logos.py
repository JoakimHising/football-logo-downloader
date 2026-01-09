#!/usr/bin/env python3
"""
Football Logos Downloader
Downloads all logos from football-logos.cc organized by country

Usage:
    python download_football_logos.py [--output-dir OUTPUT] [--format FORMAT] [--size SIZE]

Options:
    --output-dir    Directory to save logos (default: ./football_logos)
    --format        Image format: png, svg, or both (default: both)
    --size          PNG size: 64, 128, 256, 512, 700, 1500, 3000 (default: 512)
    --country       Download only specific country (use slug like "england", "sweden")
    --workers       Number of parallel downloads (default: 5)
    --list-countries  Just list available countries

Examples:
    python download_football_logos.py                          # Download all logos (PNG + SVG)
    python download_football_logos.py --country sweden         # Only Swedish clubs
    python download_football_logos.py --size 1500 --format png # High-res PNGs only
    python download_football_logos.py --format svg             # SVGs only
"""

import requests
from bs4 import BeautifulSoup
import os
import re
import time
import argparse
from urllib.parse import urljoin
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import sys

BASE_URL = "https://football-logos.cc"
ASSETS_BASE = "https://assets.football-logos.cc/logos"
SVG_BASE = "https://images.football-logos.cc"

# Valid PNG sizes available on the site
VALID_SIZES = [64, 128, 256, 512, 700, 1500, 3000]

# Pre-populated country list (extracted from the website)
# Format: slug -> (display_name, logo_count)
KNOWN_COUNTRIES = {
    "england": ("England", 150),
    "spain": ("Spain", 68),
    "italy": ("Italy", 70),
    "germany": ("Germany", 57),
    "france": ("France", 46),
    "portugal": ("Portugal", 86),
    "netherlands": ("Netherlands", 37),
    "brazil": ("Brazil", 44),
    "turkey": ("Turkey", 32),
    "scotland": ("Scotland", 65),
    "belgium": ("Belgium", 27),
    "argentina": ("Argentina", 51),
    "afghanistan": ("Afghanistan", 1),
    "albania": ("Albania", 21),
    "algeria": ("Algeria", 1),
    "andorra": ("Andorra", 9),
    "angola": ("Angola", 1),
    "armenia": ("Armenia", 10),
    "australia": ("Australia", 17),
    "austria": ("Austria", 27),
    "azerbaijan": ("Azerbaijan", 15),
    "bahrain": ("Bahrain", 1),
    "bangladesh": ("Bangladesh", 1),
    "belarus": ("Belarus", 22),
    "benin": ("Benin", 1),
    "bolivia": ("Bolivia", 1),
    "bosnia-and-herzegovina": ("Bosnia and Herzegovina", 16),
    "botswana": ("Botswana", 1),
    "bulgaria": ("Bulgaria", 24),
    "burkina-faso": ("Burkina Faso", 1),
    "cabo-verde": ("Cabo Verde", 1),
    "cameroon": ("Cameroon", 2),
    "canada": ("Canada", 10),
    "chile": ("Chile", 17),
    "china": ("China", 19),
    "colombia": ("Colombia", 21),
    "comoros": ("Comoros", 1),
    "croatia": ("Croatia", 15),
    "cuba": ("Cuba", 1),
    "congo-dr": ("Democratic Republic of the Congo", 1),
    "costa-rica": ("Costa Rica", 1),
    "cote-d-ivoire": ("Côte d'Ivoire", 1),
    "cyprus": ("Cyprus", 23),
    "czech-republic": ("Czech Republic", 33),
    "curacao": ("Curacao", 1),
    "denmark": ("Denmark", 29),
    "ecuador": ("Ecuador", 16),
    "egypt": ("Egypt", 14),
    "equatorial-guinea": ("Equatorial Guinea", 1),
    "estonia": ("Estonia", 10),
    "faroe-islands": ("Faroe Islands", 14),
    "finland": ("Finland", 24),
    "gabon": ("Gabon", 1),
    "georgia": ("Georgia", 17),
    "guatemala": ("Guatemala", 1),
    "gibraltar": ("Gibraltar", 12),
    "ghana": ("Ghana", 1),
    "greece": ("Greece", 23),
    "haiti": ("Haiti", 1),
    "honduras": ("Honduras", 1),
    "hungary": ("Hungary", 30),
    "iceland": ("Iceland", 20),
    "india": ("India", 15),
    "indonesia": ("Indonesia", 20),
    "iran": ("Iran", 1),
    "iraq": ("Iraq", 1),
    "israel": ("Israel", 25),
    "jamaica": ("Jamaica", 1),
    "japan": ("Japan", 24),
    "jordan": ("Jordan", 1),
    "kazakhstan": ("Kazakhstan", 16),
    "kenya": ("Kenya", 1),
    "kosovo": ("Kosovo", 17),
    "latvia": ("Latvia", 10),
    "liechtenstein": ("Liechtenstein", 3),
    "lithuania": ("Lithuania", 14),
    "luxembourg": ("Luxembourg", 18),
    "malaysia": ("Malaysia", 11),
    "mali": ("Mali", 1),
    "malta": ("Malta", 19),
    "mexico": ("Mexico", 21),
    "moldova": ("Moldova", 7),
    "montenegro": ("Montenegro", 12),
    "morocco": ("Morocco", 18),
    "mozambique": ("Mozambique", 1),
    "nigeria": ("Nigeria", 1),
    "north-macedonia": ("North Macedonia", 14),
    "northern-ireland": ("Northern Ireland", 16),
    "norway": ("Norway", 30),
    "nepal": ("Nepal", 1),
    "new-zealand": ("New Zealand", 1),
    "nicaragua": ("Nicaragua", 1),
    "oman": ("Oman", 1),
    "peru": ("Peru", 19),
    "poland": ("Poland", 33),
    "panama": ("Panama", 1),
    "paraguay": ("Paraguay", 11),
    "palestine": ("Palestine", 1),
    "qatar": ("Qatar", 1),
    "republic-of-ireland": ("Republic of Ireland", 18),
    "romania": ("Romania", 25),
    "russia": ("Russia", 33),
    "san-marino": ("San Marino", 14),
    "saudi-arabia": ("Saudi Arabia", 33),
    "senegal": ("Senegal", 1),
    "singapore": ("Singapore", 1),
    "serbia": ("Serbia", 23),
    "slovakia": ("Slovakia", 17),
    "slovenia": ("Slovenia", 17),
    "somalia": ("Somalia", 1),
    "south-africa": ("South Africa", 9),
    "south-korea": ("South Korea", 14),
    "sudan": ("Sudan", 1),
    "suriname": ("Suriname", 1),
    "sweden": ("Sweden", 29),
    "switzerland": ("Switzerland", 18),
    "syria": ("Syria", 1),
    "thailand": ("Thailand", 7),
    "tunisia": ("Tunisia", 1),
    "uae": ("United Arab Emirates", 1),
    "uganda": ("Uganda", 1),
    "ukraine": ("Ukraine", 23),
    "uruguay": ("Uruguay", 17),
    "usa": ("USA", 55),
    "uzbekistan": ("Uzbekistan", 17),
    "venezuela": ("Venezuela", 1),
    "vietnam": ("Vietnam", 2),
    "wales": ("Wales", 42),
    "zambia": ("Zambia", 1),
    "tournaments": ("Tournaments", 37),  # International tournaments
}

def get_headers():
    """Return headers that mimic a browser request."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": BASE_URL,
    }

def sanitize_filename(name):
    """Sanitize a string to be used as a filename."""
    # Remove or replace problematic characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = name.strip()
    return name

def get_countries_list(session):
    """Fetch the main page and extract all country links, or use fallback."""
    print("Fetching country list...")
    
    try:
        response = session.get(BASE_URL, headers=get_headers(), timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        countries = {}
        
        # Find all country links - they follow pattern like /england/, /spain/, etc.
        exclude_paths = {'/', '/all/', '/collections/', '/map/', '/new/', '/countries/'}
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            # Match country paths (single segment paths)
            if re.match(r'^/[a-z-]+/$', href) and href not in exclude_paths:
                country_slug = href.strip('/')
                
                # Try to get the country name from the link text
                text = link.get_text(strip=True)
                # Clean up emoji flags and numbers
                country_name = re.sub(r'[\U0001F1E0-\U0001F1FF\U0001F3F4\U000E0067-\U000E007F]+', '', text)
                country_name = re.sub(r'\d+', '', country_name).strip()
                
                if country_name and country_slug not in countries:
                    countries[country_slug] = country_name
        
        if countries:
            print(f"Found {len(countries)} countries from website")
            return countries
            
    except Exception as e:
        print(f"Could not fetch from website: {e}")
    
    # Use fallback list
    print(f"Using pre-populated list of {len(KNOWN_COUNTRIES)} countries")
    return {slug: info[0] for slug, info in KNOWN_COUNTRIES.items()}

def get_country_logos(session, country_slug, country_name):
    """Fetch all logos for a specific country."""
    logos = []
    page = 1
    
    while True:
        if page == 1:
            url = f"{BASE_URL}/{country_slug}/"
        else:
            url = f"{BASE_URL}/{country_slug}/page/{page}/"
        
        try:
            response = session.get(url, headers=get_headers())
            
            if response.status_code == 404:
                break
                
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all logo cards/links
            # Looking for links to individual team pages and extracting logo info
            found_logos = False
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                
                # Match team pages like /england/liverpool/
                if re.match(rf'^/{country_slug}/[a-z0-9-]+/$', href):
                    team_slug = href.strip('/').split('/')[-1]
                    
                    # Try to find the team name
                    h3 = link.find('h3')
                    if h3:
                        team_name = h3.get_text(strip=True)
                    else:
                        team_name = team_slug.replace('-', ' ').title()
                    
                    # Find the logo image in this link
                    img = link.find('img')
                    if img and img.get('src'):
                        img_src = img.get('src', '')
                        
                        # Extract the hash from the image URL for constructing download URLs
                        # Pattern: https://assets.football-logos.cc/logos/england/256x256/liverpool.99c48ae3.png
                        match = re.search(rf'{country_slug}/\d+x\d+/([^/]+)\.([a-f0-9]+)\.png', img_src)
                        if match:
                            base_name = match.group(1)
                            png_hash = match.group(2)
                            
                            logo_info = {
                                'team_name': team_name,
                                'team_slug': team_slug,
                                'base_name': base_name,
                                'png_hash': png_hash,
                                'svg_hash': None,  # Will be fetched from team page
                                'country_slug': country_slug,
                                'team_url': f"{BASE_URL}{href}",
                            }
                            
                            # Avoid duplicates
                            if not any(l['team_slug'] == team_slug for l in logos):
                                logos.append(logo_info)
                                found_logos = True
            
            if not found_logos:
                break
                
            page += 1
            time.sleep(0.3)  # Be polite to the server
            
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching page {page} for {country_name}: {e}")
            break
    
    return logos


def get_svg_hash_from_team_page(session, logo_info):
    """Fetch team page to get SVG hash."""
    try:
        response = session.get(logo_info['team_url'], headers=get_headers(), timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for SVG link on the page
        # Pattern: https://images.football-logos.cc/england/liverpool.b130c6a1.svg
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if '.svg' in href:
                match = re.search(rf'{logo_info["country_slug"]}/([^/]+)\.([a-f0-9]+)\.svg', href)
                if match:
                    return match.group(2)  # Return the SVG hash
        
        return None
    except Exception:
        return None

def download_logo_png(session, logo_info, output_dir, size=512, max_retries=3):
    """Download PNG logo with retry logic for rate limiting."""
    country_slug = logo_info['country_slug']
    base_name = logo_info['base_name']
    png_hash = logo_info['png_hash']
    team_name = sanitize_filename(logo_info['team_name'])

    # Create country/png directory
    country_dir = Path(output_dir) / sanitize_filename(country_slug) / "png"
    country_dir.mkdir(parents=True, exist_ok=True)

    url = f"{ASSETS_BASE}/{country_slug}/{size}x{size}/{base_name}.{png_hash}.png"
    filename = f"{team_name}.png"
    filepath = country_dir / filename

    # Skip if already downloaded
    if filepath.exists():
        return True, f"Skipped (exists): {filepath}"

    # Retry logic with exponential backoff for rate limiting
    for attempt in range(max_retries):
        try:
            response = session.get(url, headers=get_headers(), timeout=30)

            # Handle rate limiting
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2  # 2, 4, 8 seconds
                    time.sleep(wait_time)
                    continue
                else:
                    return False, f"Rate limited PNG {team_name}: Too Many Requests (429)"

            response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(response.content)

            return True, f"Downloaded: {filepath}"

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 2
                time.sleep(wait_time)
                continue
            return False, f"Failed PNG {team_name}: {e}"
        except requests.exceptions.RequestException as e:
            return False, f"Failed PNG {team_name}: {e}"

    return False, f"Failed PNG {team_name}: Max retries exceeded"


def download_logo_svg(session, logo_info, output_dir, max_retries=3):
    """Download SVG logo with retry logic for rate limiting."""
    country_slug = logo_info['country_slug']
    base_name = logo_info['base_name']
    svg_hash = logo_info.get('svg_hash')
    team_name = sanitize_filename(logo_info['team_name'])

    # Create country/svg directory
    country_dir = Path(output_dir) / sanitize_filename(country_slug) / "svg"
    country_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{team_name}.svg"
    filepath = country_dir / filename

    # Skip if already downloaded
    if filepath.exists():
        return True, f"Skipped (exists): {filepath}"

    # If we don't have SVG hash, we need to fetch it from team page
    if not svg_hash:
        svg_hash = get_svg_hash_from_team_page(session, logo_info)
        if not svg_hash:
            return False, f"No SVG available for {team_name}"

    url = f"{SVG_BASE}/{country_slug}/{base_name}.{svg_hash}.svg"

    # Retry logic with exponential backoff for rate limiting
    for attempt in range(max_retries):
        try:
            response = session.get(url, headers=get_headers(), timeout=30)

            # Handle rate limiting
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2  # 2, 4, 8 seconds
                    time.sleep(wait_time)
                    continue
                else:
                    return False, f"Rate limited SVG {team_name}: Too Many Requests (429)"

            response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(response.content)

            return True, f"Downloaded: {filepath}"

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 2
                time.sleep(wait_time)
                continue
            return False, f"Failed SVG {team_name}: {e}"
        except requests.exceptions.RequestException as e:
            return False, f"Failed SVG {team_name}: {e}"

    return False, f"Failed SVG {team_name}: Max retries exceeded"


def download_logo(session, logo_info, output_dir, img_format='both', size=512, delay=0.5):
    """Download logo in specified format(s)."""
    results = []

    if img_format in ('png', 'both'):
        results.append(('png', download_logo_png(session, logo_info, output_dir, size)))
        time.sleep(delay)  # Add delay between requests

    if img_format in ('svg', 'both'):
        results.append(('svg', download_logo_svg(session, logo_info, output_dir)))
        time.sleep(delay)  # Add delay between requests

    return results

def main():
    parser = argparse.ArgumentParser(
        description='Download football logos from football-logos.cc',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s                          # Download all logos (PNG + SVG)
    %(prog)s --country sweden         # Only Swedish clubs  
    %(prog)s --country sweden --size 1500  # Swedish clubs at 1500x1500
    %(prog)s --format png             # PNG only
    %(prog)s --format svg             # SVG only
    %(prog)s --list-countries         # Show all available countries
        """
    )
    parser.add_argument('--output-dir', '-o', default='./football_logos',
                        help='Output directory (default: ./football_logos)')
    parser.add_argument('--format', '-f', choices=['png', 'svg', 'both'], default='both',
                        help='Image format: png, svg, or both (default: both)')
    parser.add_argument('--size', '-s', type=int, choices=VALID_SIZES, default=512,
                        help='PNG size in pixels (default: 512)')
    parser.add_argument('--country', '-c', default=None,
                        help='Download only specific country (use slug like "england", "sweden")')
    parser.add_argument('--workers', '-w', type=int, default=5,
                        help='Number of parallel download workers (default: 5)')
    parser.add_argument('--list-countries', action='store_true',
                        help='Just list available countries and exit')
    parser.add_argument('--delay', '-d', type=float, default=0.5,
                        help='Delay between requests in seconds (default: 0.5)')
    
    args = parser.parse_args()
    
    # Quick list-countries mode using pre-populated data
    if args.list_countries:
        print("\nAvailable countries/categories:")
        print("-" * 50)
        for slug, (name, count) in sorted(KNOWN_COUNTRIES.items(), key=lambda x: x[1][0]):
            print(f"  {slug:25} {name:30} ({count} logos)")
        print("-" * 50)
        print(f"Total: {sum(c[1] for c in KNOWN_COUNTRIES.values())} logos across {len(KNOWN_COUNTRIES)} categories")
        return
    
    # Create session for connection pooling
    session = requests.Session()
    
    # Get list of countries
    countries = get_countries_list(session)
    
    # Filter to specific country if requested
    if args.country:
        if args.country in countries:
            countries = {args.country: countries[args.country]}
        else:
            print(f"Country '{args.country}' not found.")
            print("Use --list-countries to see available options.")
            sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Collect all logos from all countries
    all_logos = []
    total_countries = len(countries)
    
    print(f"\nScanning {total_countries} countries for logos...")
    print("=" * 50)
    
    for i, (country_slug, country_name) in enumerate(sorted(countries.items()), 1):
        print(f"[{i}/{total_countries}] {country_name} ({country_slug})...", end=" ", flush=True)
        
        logos = get_country_logos(session, country_slug, country_name)
        all_logos.extend(logos)
        
        print(f"found {len(logos)} logos")
        time.sleep(args.delay)
    
    print("=" * 50)
    print(f"Total logos found: {len(all_logos)}")
    
    if not all_logos:
        print("No logos found to download.")
        return
    
    # Save metadata
    metadata_file = output_dir / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_logos': len(all_logos),
            'countries': list(countries.keys()),
            'settings': {
                'format': args.format,
                'size': args.size
            },
            'logos': all_logos
        }, f, indent=2, ensure_ascii=False)
    print(f"\nSaved metadata to {metadata_file}")
    
    # Calculate expected downloads
    format_str = args.format.upper()
    if args.format == 'both':
        format_str = f"PNG ({args.size}x{args.size}) + SVG"
        expected = len(all_logos) * 2
    else:
        if args.format == 'png':
            format_str = f"PNG ({args.size}x{args.size})"
        expected = len(all_logos)
    
    print(f"\nDownloading {len(all_logos)} logos ({format_str})...")
    print("-" * 50)
    
    # Counters
    png_success = 0
    png_skipped = 0
    png_failed = 0
    svg_success = 0
    svg_skipped = 0
    svg_failed = 0
    
    processed = 0
    
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(download_logo, session, logo, output_dir, args.format, args.size, args.delay): logo
            for logo in all_logos
        }
        
        for future in as_completed(futures):
            processed += 1
            results = future.result()
            
            for fmt, (success, message) in results:
                if fmt == 'png':
                    if success:
                        if "Skipped" in message:
                            png_skipped += 1
                        else:
                            png_success += 1
                    else:
                        png_failed += 1
                        if "Failed" in message:
                            print(f"  ✗ {message}")
                elif fmt == 'svg':
                    if success:
                        if "Skipped" in message:
                            svg_skipped += 1
                        else:
                            svg_success += 1
                    else:
                        svg_failed += 1
                        # Only print SVG errors if not "No SVG available" (common)
                        if "Failed" in message and "No SVG" not in message:
                            print(f"  ✗ {message}")
            
            # Progress update every 50 logos
            if processed % 50 == 0 or processed == len(all_logos):
                if args.format == 'both':
                    print(f"  Progress: {processed}/{len(all_logos)} logos | PNG: {png_success} new, {png_skipped} exist, {png_failed} fail | SVG: {svg_success} new, {svg_skipped} exist, {svg_failed} fail")
                elif args.format == 'png':
                    print(f"  Progress: {processed}/{len(all_logos)} | {png_success} new, {png_skipped} exist, {png_failed} failed")
                else:
                    print(f"  Progress: {processed}/{len(all_logos)} | {svg_success} new, {svg_skipped} exist, {svg_failed} failed")
    
    print("-" * 50)
    print(f"\n✓ Download complete!")
    
    if args.format in ('png', 'both'):
        print(f"  PNG: {png_success} new, {png_skipped} existed, {png_failed} failed")
    if args.format in ('svg', 'both'):
        print(f"  SVG: {svg_success} new, {svg_skipped} existed, {svg_failed} failed")
    
    print(f"\n  Output directory: {output_dir.absolute()}")
    print(f"  Structure: {output_dir}/[country]/png/ and {output_dir}/[country]/svg/")

if __name__ == "__main__":
    main()
