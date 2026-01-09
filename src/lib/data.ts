import fs from 'fs';
import path from 'path';

export interface Logo {
  team_name: string;
  team_slug: string;
  base_name: string;
  png_hash: string | null;
  svg_hash: string | null;
  country_slug: string;
  team_url: string;
}

export interface Metadata {
  total_logos: number;
  countries: string[];
  settings: {
    format: string;
    size: number;
  };
  logos: Logo[];
}

// Load metadata from the football_logos directory
export function loadMetadata(): Metadata {
  const metadataPath = path.join(process.cwd(), 'football_logos', 'metadata.json');
  const data = fs.readFileSync(metadataPath, 'utf-8');
  return JSON.parse(data) as Metadata;
}

// Get all countries with their logo counts (only count teams with coloring pages)
export function getCountriesWithCounts(metadata: Metadata): { slug: string; count: number }[] {
  const countryCounts = new Map<string, number>();

  metadata.logos.forEach(logo => {
    // Only count if coloring page exists
    const coloringPagePath = path.join(
      process.cwd(),
      'football_logos',
      logo.country_slug,
      'coloring-pages',
      `${logo.base_name}_coloring.svg`
    );
    if (fs.existsSync(coloringPagePath)) {
      countryCounts.set(logo.country_slug, (countryCounts.get(logo.country_slug) || 0) + 1);
    }
  });

  return Array.from(countryCounts.entries())
    .map(([slug, count]) => ({ slug, count }))
    .filter(item => item.count > 0) // Only show countries with at least one logo
    .sort((a, b) => a.slug.localeCompare(b.slug));
}

// Get logos for a specific country (only those with coloring pages)
export function getLogosByCountry(metadata: Metadata, countrySlug: string): Logo[] {
  return metadata.logos.filter(logo => {
    if (logo.country_slug !== countrySlug) return false;

    // Check if coloring page exists
    const coloringPagePath = path.join(
      process.cwd(),
      'football_logos',
      logo.country_slug,
      'coloring-pages',
      `${logo.base_name}_coloring.svg`
    );
    return fs.existsSync(coloringPagePath);
  });
}

// Get a specific logo by team slug and country
export function getLogoByTeam(metadata: Metadata, countrySlug: string, teamSlug: string): Logo | undefined {
  return metadata.logos.find(
    logo => logo.country_slug === countrySlug && logo.team_slug === teamSlug
  );
}

// Get logo file paths
// Files use base_name convention: lowercase, hyphenated (e.g., "arsenal", "afc-wimbledon")
export function getLogoPath(logo: Logo, type: 'original' | 'coloring', format: 'svg' | 'png' = 'svg'): string {
  const baseDir = `/football_logos/${logo.country_slug}`;
  const fileName = logo.base_name; // Use base_name for web-friendly filenames

  if (type === 'original') {
    // Return path regardless of hash (metadata hash values are unreliable)
    if (format === 'svg') {
      return `${baseDir}/svg/${fileName}.svg`;
    } else {
      return `${baseDir}/png/${fileName}.png`;
    }
  } else {
    // Coloring page
    return `${baseDir}/coloring-pages/${fileName}_coloring.${format}`;
  }
}

// Format country name for display
export function formatCountryName(slug: string): string {
  return slug
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
