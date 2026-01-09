# Cloudflare R2 Storage Setup Guide

This guide will help you set up Cloudflare R2 (object storage) to host your football logos efficiently. This approach dramatically reduces your git repository size and speeds up deployments.

## Why Use R2?

- ✅ **Smaller Repository**: Keep only code in git, not thousands of images
- ✅ **Faster Builds**: Cloudflare Pages builds 10-100x faster without large files
- ✅ **Incremental Sync**: Only upload changed files, not everything
- ✅ **Zero Egress Fees**: Free bandwidth when accessed from Cloudflare services
- ✅ **Global CDN**: Automatic edge caching worldwide
- ✅ **Cost Effective**: $0.015/GB storage, first 10GB free monthly

## Architecture

```
┌─────────────────┐
│  Git Repository │  (Only code + metadata.json)
│  (Cloudflare    │
│   Pages)        │
└────────┬────────┘
         │
         │ References
         ▼
┌─────────────────┐
│  Cloudflare R2  │  (All logos: SVG, PNG, coloring pages)
│  Object Storage │  (Synced incrementally)
└─────────────────┘
```

## Prerequisites

- Cloudflare account with R2 enabled
- Node.js installed locally (for sync script)
- Command line access

---

## Step 1: Enable Cloudflare R2

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **R2 Object Storage** in the left sidebar
3. Click **Purchase R2 Plan** (Free tier available - first 10GB storage free)
4. Complete the setup

---

## Step 2: Create R2 Bucket

1. In R2 dashboard, click **Create bucket**
2. Enter bucket name: `football-logos` (or your preferred name)
3. Select location: **Automatic** (recommended for global distribution)
4. Click **Create bucket**

---

## Step 3: Configure Public Access

### Option A: Custom Domain (Recommended)

1. In your bucket settings, go to **Settings** → **Public Access**
2. Click **Connect Domain**
3. Enter your subdomain: `logos.yourdomain.com`
4. Follow DNS setup instructions
5. Enable **Allow Access**

**Benefits:**
- Custom domain
- Automatic HTTPS
- Better caching
- No request limits

### Option B: R2.dev Subdomain (Quick Setup)

1. In bucket settings, go to **Settings** → **Public Access**
2. Click **Allow Access**
3. Enable **R2.dev subdomain**
4. You'll get a URL like: `https://pub-xxxxxxxxxxxxx.r2.dev`

**Note:** R2.dev has rate limits (not suitable for high traffic)

---

## Step 4: Create API Token

1. In R2 dashboard, click **Manage R2 API Tokens**
2. Click **Create API Token**
3. Configure token:
   - **Token name**: `football-logos-sync`
   - **Permissions**:
     - ✅ Object Read & Write
     - ✅ Object List
   - **Buckets**: Select your `football-logos` bucket (or all buckets)
   - **TTL**: Never expire (or set expiration)
4. Click **Create API Token**
5. **IMPORTANT**: Copy the credentials immediately:
   - Access Key ID
   - Secret Access Key
   - Account ID

---

## Step 5: Configure Local Environment

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```bash
   CLOUDFLARE_ACCOUNT_ID=your_account_id_here
   R2_ACCESS_KEY_ID=your_access_key_id_here
   R2_SECRET_ACCESS_KEY=your_secret_access_key_here
   R2_BUCKET_NAME=football-logos
   R2_PUBLIC_URL=https://logos.yourdomain.com
   ```

3. **Security**: The `.env` file is already in `.gitignore` - never commit it!

---

## Step 6: Install Dependencies

```bash
npm install
```

This installs the AWS S3 SDK (R2 is S3-compatible).

---

## Step 7: Sync Logos to R2

### Initial Upload (All Files)

```bash
npm run sync:r2
```

This will:
- Scan all files in `football_logos/`
- Upload SVG, PNG, and JSON files to R2
- Show progress for each file
- Display summary statistics

**Example output:**
```
🚀 Starting sync to Cloudflare R2...

📦 Bucket: football-logos
🔧 Account ID: abc123...

📂 Scanning local files...
   Found 2,847 files

✅ Uploaded: football_logos/england/svg/Arsenal.svg
✅ Uploaded: football_logos/england/svg/Chelsea.svg
...

============================================================
📊 Sync Summary
============================================================
✅ Uploaded: 2,847 files (487.3 MB)
⏭️  Skipped: 0 files (unchanged)
============================================================

🌐 Public URL: https://logos.yourdomain.com
   Example: https://logos.yourdomain.com/football_logos/england/svg/Arsenal.svg

✨ Sync complete!
```

### Incremental Updates (Only Changed Files)

The sync script is smart - it only uploads files that have changed:

```bash
# Add new logos or modify existing ones
./convert_all_to_coloring.sh

# Sync only changes
npm run sync:r2
```

**Example output:**
```
📂 Scanning local files...
   Found 2,847 files

⏭️  Skip: football_logos/england/svg/Arsenal.svg
⏭️  Skip: football_logos/england/svg/Chelsea.svg
✅ Uploaded: football_logos/spain/svg/Barcelona.svg (new)
✅ Updated: football_logos/italy/svg/Juventus.svg (modified)

============================================================
📊 Sync Summary
============================================================
✅ Uploaded: 2 files (143.2 KB)
⏭️  Skipped: 2,845 files (unchanged)
============================================================
```

---

## Step 8: Update Your Application

### Option A: Update Astro Config (for Astro sites)

Update `astro.config.mjs`:

```javascript
export default defineConfig({
  image: {
    domains: ['logos.yourdomain.com'], // Your R2 domain
    remotePatterns: [
      { protocol: "https", hostname: "logos.yourdomain.com" }
    ],
  },
  // ... rest of config
});
```

### Option B: Update Image Paths in Code

Replace local paths with R2 URLs:

**Before:**
```html
<img src="/football_logos/england/svg/Arsenal.svg" />
```

**After:**
```html
<img src="https://logos.yourdomain.com/football_logos/england/svg/Arsenal.svg" />
```

### Option C: Use Environment Variable

Create a helper for dynamic URLs:

```javascript
// src/config.js
export const LOGOS_BASE_URL = import.meta.env.PUBLIC_R2_URL || '/football_logos';

// Usage
import { LOGOS_BASE_URL } from './config';
const logoUrl = `${LOGOS_BASE_URL}/england/svg/Arsenal.svg`;
```

---

## Step 9: Update Git Repository

After setting up R2, clean up your git repository:

1. **Uncomment the exclusions in `.gitignore`:**
   ```gitignore
   # Uncomment these lines:
   football_logos/**/*.svg
   football_logos/**/*.png
   football_logos/**/coloring-pages/
   ```

2. **Remove large files from git:**
   ```bash
   git rm --cached -r football_logos/**/*.svg
   git rm --cached -r football_logos/**/*.png
   git rm --cached -r football_logos/**/coloring-pages/

   # Keep metadata.json
   git add football_logos/metadata.json

   git commit -m "Move logos to R2, remove from git"
   git push
   ```

3. **Your repository is now lightweight!** 🎉

---

## Step 10: Automate with GitHub Actions (Optional)

See **GitHub Actions Setup** section below for automatic syncing on every push.

---

## GitHub Actions Setup

Automate R2 syncing with GitHub Actions:

### 1. Add Secrets to GitHub

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:
   - `CLOUDFLARE_ACCOUNT_ID`
   - `R2_ACCESS_KEY_ID`
   - `R2_SECRET_ACCESS_KEY`
   - `R2_BUCKET_NAME`
   - `R2_PUBLIC_URL`

### 2. Create Workflow File

The workflow file is already created at `.github/workflows/sync-r2.yml`. It will:
- ✅ Run on every push to `main` branch
- ✅ Only sync when logo files change
- ✅ Upload only modified files
- ✅ Show detailed logs

### 3. Trigger Workflow

```bash
# Push changes
git add .
git commit -m "Add new logos"
git push

# GitHub Actions will automatically sync to R2
```

**View progress:**
- Go to **Actions** tab in your GitHub repository
- Click on the latest workflow run
- Watch the sync in real-time

---

## Usage Examples

### Access Logos from R2

```javascript
// Direct URL
const arsenalLogo = 'https://logos.yourdomain.com/football_logos/england/svg/Arsenal.svg';

// In HTML
<img src="https://logos.yourdomain.com/football_logos/england/svg/Arsenal.svg"
     alt="Arsenal FC" />

// In Astro component
---
const logoBaseUrl = import.meta.env.PUBLIC_R2_URL;
const team = 'Arsenal';
const logoUrl = `${logoBaseUrl}/football_logos/england/svg/${team}.svg`;
---
<img src={logoUrl} alt={`${team} logo`} />
```

### Update Coloring Page Viewer

Update `coloring_page_viewer.html` to use R2 URLs:

```javascript
// Add at the top
const LOGOS_BASE_URL = 'https://logos.yourdomain.com';

// Update image sources
imgElement.src = `${LOGOS_BASE_URL}/football_logos/${country}/coloring-pages/${filename}`;
```

---

## Cost Estimation

### R2 Pricing (as of 2024)

- **Storage**: $0.015 per GB per month (first 10 GB free)
- **Class A Operations** (writes): $4.50 per million requests
- **Class B Operations** (reads): $0.36 per million requests
- **Egress**: FREE to Cloudflare services (Pages, Workers, etc.)

### Example Costs

**Scenario 1: Personal Project**
- Storage: 500 MB of logos = FREE (under 10 GB)
- Reads: 10,000 page views/month = ~$0.004
- **Total: ~$0.00/month** ✅

**Scenario 2: Popular Site**
- Storage: 2 GB of logos = FREE (under 10 GB)
- Reads: 1 million page views/month = ~$0.36
- **Total: ~$0.36/month** ✅

**Scenario 3: Very Popular Site**
- Storage: 15 GB of logos = ~$0.08
- Reads: 10 million page views/month = ~$3.60
- **Total: ~$3.68/month** ✅

Compare to traditional CDN: Often $50-200/month for similar usage! 🎉

---

## Troubleshooting

### Error: "Missing required environment variables"

**Solution:** Ensure `.env` file exists with all required variables:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### Error: "Access Denied" or "401 Unauthorized"

**Solutions:**
1. Verify API token has correct permissions (Read & Write)
2. Check token hasn't expired
3. Ensure bucket name matches in `.env`
4. Verify account ID is correct

### Error: "Bucket not found"

**Solutions:**
1. Create the R2 bucket in Cloudflare Dashboard
2. Ensure bucket name in `.env` matches exactly
3. Check bucket is in correct account

### Sync is Very Slow

**Solutions:**
1. First sync uploads ALL files - this is normal
2. Subsequent syncs are much faster (only changes)
3. Check your internet upload speed
4. Consider reducing file sizes if needed

### Images Not Loading from R2

**Solutions:**
1. Verify public access is enabled on bucket
2. Check CORS settings (should allow all origins)
3. Verify URL format: `https://your-domain/football_logos/...`
4. Test URL directly in browser
5. Check browser console for CORS errors

### GitHub Actions Failing

**Solutions:**
1. Verify all secrets are set correctly in GitHub
2. Check workflow file syntax
3. Review Actions logs for specific error
4. Ensure repository has Actions enabled

---

## Maintenance

### Regular Tasks

**Weekly: Sync New Logos**
```bash
# Download new logos
python download_football_logos.py --country [country]

# Convert to coloring pages
./convert_all_to_coloring.sh

# Sync to R2
npm run sync:r2
```

**Monthly: Review Storage**
```bash
# Check R2 storage usage in Cloudflare Dashboard
# R2 > Your Bucket > Metrics
```

**As Needed: Rotate API Keys**
```bash
# Create new API token in Cloudflare Dashboard
# Update .env and GitHub Secrets
# Delete old token
```

---

## Migration Back to Local (if needed)

If you want to move logos back to git:

```bash
# 1. Comment out .gitignore exclusions
# 2. Add files back to git
git add football_logos/
git commit -m "Move logos back to repository"
git push

# 3. Update image URLs back to local paths
# 4. Keep R2 as backup if desired
```

---

## Benefits Summary

| Aspect | Before (Git) | After (R2) |
|--------|-------------|-----------|
| Repository Size | ~500 MB | ~5 MB |
| Clone Time | 2-5 minutes | 10 seconds |
| Build Time | 5-10 minutes | 30-60 seconds |
| Deploy Time | 10-15 minutes | 1-2 minutes |
| Bandwidth Cost | Included in Pages | FREE (R2→Pages) |
| Incremental Updates | Full rebuild | Only changed files |
| Global Distribution | ✅ Yes | ✅ Yes (faster) |

---

## Next Steps

After R2 setup:
1. ✅ Sync logos to R2
2. ✅ Update image paths in code
3. ✅ Remove large files from git
4. ✅ Set up GitHub Actions (optional)
5. ✅ Deploy to Cloudflare Pages
6. ✅ Test all functionality
7. ✅ Monitor R2 usage

---

## Useful Links

- [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/)
- [R2 Pricing](https://developers.cloudflare.com/r2/pricing/)
- [R2 Public Buckets Guide](https://developers.cloudflare.com/r2/buckets/public-buckets/)
- [AWS S3 SDK (used for R2)](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/clients/client-s3/)
- [Cloudflare Dashboard](https://dash.cloudflare.com/)

---

## Support

If you need help:
1. Check [Cloudflare Community](https://community.cloudflare.com/c/developers/workers/40)
2. Review [R2 Discord](https://discord.gg/cloudflaredev)
3. Open an issue in this repository
