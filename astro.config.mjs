// @ts-check
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // IMPORTANT: Update this with your actual domain when deploying to Cloudflare Pages
  // Example: 'https://football-logos.pages.dev' or 'https://yourdomain.com'
  site: 'https://your-domain.com',
  integrations: [sitemap()],
  build: {
    format: 'directory', // Creates /team/arsenal/index.html for cleaner URLs
    inlineStylesheets: 'auto', // Inline CSS for better performance
  },
  image: {
    remotePatterns: [{ protocol: "https" }],
  },
  vite: {
    plugins: [tailwindcss()],
    server: {
      fs: {
        // Allow serving files from football_logos directory
        allow: ['..', './football_logos']
      }
    },
    build: {
      cssMinify: 'lightningcss', // Faster CSS minification
      rollupOptions: {
        output: {
          manualChunks: undefined, // Better code splitting
        }
      }
    }
  },
  // Performance optimizations
  prefetch: {
    prefetchAll: true,
    defaultStrategy: 'viewport'
  },
  compressHTML: true,
});
