# Cloudflare Pages Deployment Guide

This guide will help you deploy your Football Logo Downloader Astro site to Cloudflare Pages.

> **⚡ Recommended:** For optimal performance, use **Cloudflare R2** to store logos instead of committing them to git. See [R2_DEPLOYMENT.md](./R2_DEPLOYMENT.md) for the optimized setup that offers:
> - 🚀 100x faster builds (30 seconds vs 10+ minutes)
> - 📦 100x smaller repository (5 MB vs 500+ MB)
> - 💰 Zero bandwidth costs
> - ⚡ Incremental updates (only sync changed files)

## Prerequisites

- A Cloudflare account (https://dash.cloudflare.com/sign-up)
- Your code pushed to a GitHub repository
- Your football logos and coloring pages generated locally

## Deployment Steps

### 1. Connect Your GitHub Repository to Cloudflare Pages

1. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **Workers & Pages** in the left sidebar
3. Click **Create application** (or **Create** button)
4. Select the **Pages** tab
5. Click **Connect to Git**

### 2. Select Your Repository

1. Click **Connect GitHub** and authorize Cloudflare to access your repositories
2. Find and select your `football-logo-downloader` repository
3. Click **Begin setup**

### 3. Configure Build Settings

Use these settings for your Astro project:

```
Production branch: main
Build command: npm run build
Build output directory: dist
Root directory: (leave empty)
```

**Environment variables:** (none required for basic deployment)

### 4. Advanced Build Settings (Optional)

If needed, you can add these environment variables:
- `NODE_VERSION`: 22 (already set via .node-version file)

### 5. Deploy

1. Click **Save and Deploy**
2. Wait for the build to complete (usually 1-3 minutes)
3. Your site will be live at `https://your-project-name.pages.dev`

## Post-Deployment Configuration

### Update Your Domain in astro.config.mjs

After deployment, update the `site` field in `astro.config.mjs`:

```javascript
export default defineConfig({
  site: 'https://your-project-name.pages.dev', // or your custom domain
  // ...
});
```

Then commit and push the change to trigger a new deployment.

### Add a Custom Domain (Optional)

1. In your Cloudflare Pages project, go to **Custom domains**
2. Click **Set up a custom domain**
3. Enter your domain name (e.g., `football-logos.com`)
4. Follow the instructions to:
   - Add your domain to Cloudflare (if not already added)
   - Update DNS settings
   - Enable automatic HTTPS

## Important Notes About Large Files

### Football Logos Directory

Your `football_logos` directory contains many large SVG and PNG files. Consider these options:

**Option 1: Deploy with Logos (Recommended for Personal Use)**
- Keep all logos in the repository
- Note: Initial builds may be slower due to large file count
- Cloudflare Pages has a 25 MB per file limit and 20,000 file limit

**Option 2: Use External Storage (For Production)**
- Upload logos to Cloudflare R2 (object storage)
- Update image paths to reference R2 URLs
- Keeps repository smaller and builds faster

### .gitignore Considerations

If your `football_logos` directory is getting too large, consider:

```gitignore
# Optionally ignore logos in git (not recommended for Cloudflare Pages)
# football_logos/**/*.png
# football_logos/**/*.svg

# Keep metadata
!football_logos/metadata.json
```

Note: If you ignore these files, you'll need to use Option 2 above (external storage).

## Build Optimization

Your project is already optimized with:
- ✅ CSS minification with Lightning CSS
- ✅ Automatic HTML compression
- ✅ Smart prefetching
- ✅ Image optimization
- ✅ Directory-based URLs for cleaner paths

### Security Headers

The project includes security headers in `public/_headers`:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin

These are automatically applied by Cloudflare Pages.

### Caching Strategy

Static assets and logos are cached for 1 year:
- `/assets/*` - Immutable build assets
- `/football_logos/*` - Logo files

## Continuous Deployment

Cloudflare Pages automatically deploys when you:
1. Push to your `main` branch (production)
2. Create a pull request (preview deployment)

Preview deployments are available at:
`https://[commit-hash].[project-name].pages.dev`

## Monitoring and Analytics

1. Go to your Cloudflare Pages project
2. Check the **Analytics** tab for:
   - Page views
   - Unique visitors
   - Bandwidth usage
   - Top pages

## Troubleshooting

### Build Fails

**Issue:** Build times out or fails
- **Solution:** Check the build logs in Cloudflare Dashboard
- Common causes: Large file count, missing dependencies

**Issue:** "Command not found: npm"
- **Solution:** Ensure `.node-version` file exists (already created)

### Site Shows 404

**Issue:** Pages return 404 errors
- **Solution:** Verify `Build output directory` is set to `dist`
- Check that `npm run build` completes successfully locally

### Images Not Loading

**Issue:** Football logos don't display
- **Solution 1:** Ensure `football_logos` directory is committed to git
- **Solution 2:** Check file paths are correct (relative to `public/`)
- **Solution 3:** Verify files are under 25 MB each

### Coloring Page Viewer Not Working

**Issue:** Viewer page is blank
- **Solution:** Check browser console for errors
- Verify `football_logos/metadata.json` exists
- Ensure CORS headers allow file access (already configured in `_headers`)

## Performance Tips

1. **Enable Cloudflare CDN** (automatic with Pages)
2. **Use Custom Domain** for better caching
3. **Enable HTTP/3** in Cloudflare settings
4. **Monitor Core Web Vitals** in Analytics

## Costs

Cloudflare Pages Free Tier includes:
- ✅ Unlimited bandwidth
- ✅ Unlimited requests
- ✅ 500 builds per month
- ✅ 1 build at a time
- ✅ Automatic HTTPS

This is more than sufficient for personal projects and most production use cases.

## Next Steps

After deployment:
1. ✅ Test your site at the `.pages.dev` URL
2. ✅ Update `astro.config.mjs` with your actual domain
3. ✅ Set up a custom domain (optional)
4. ✅ Configure DNS settings if using custom domain
5. ✅ Test all coloring page functionality
6. ✅ Share your site!

## Useful Links

- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Astro Deployment Guide](https://docs.astro.build/en/guides/deploy/cloudflare/)
- [Cloudflare Dashboard](https://dash.cloudflare.com/)
- [Your GitHub Repository](https://github.com/JoakimHising/football-logo-downloader)

## Support

If you encounter issues:
1. Check [Cloudflare Community](https://community.cloudflare.com/)
2. Review [Astro Discord](https://astro.build/chat)
3. Check build logs in Cloudflare Dashboard
