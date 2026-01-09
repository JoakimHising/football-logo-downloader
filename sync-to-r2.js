#!/usr/bin/env node

/**
 * Sync football logos to Cloudflare R2 (incremental upload)
 * Only uploads new or modified files based on file hash comparison
 */

import { S3Client, PutObjectCommand, HeadObjectCommand, ListObjectsV2Command } from '@aws-sdk/client-s3';
import { createReadStream, statSync } from 'fs';
import { readdir, readFile } from 'fs/promises';
import { join, relative } from 'path';
import { createHash } from 'crypto';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Configuration from environment variables
const config = {
  accountId: process.env.CLOUDFLARE_ACCOUNT_ID,
  accessKeyId: process.env.R2_ACCESS_KEY_ID,
  secretAccessKey: process.env.R2_SECRET_ACCESS_KEY,
  bucketName: process.env.R2_BUCKET_NAME || 'football-logos',
  publicUrl: process.env.R2_PUBLIC_URL, // e.g., https://logos.yourdomain.com
};

// Validate configuration
function validateConfig() {
  const required = ['accountId', 'accessKeyId', 'secretAccessKey', 'bucketName'];
  const missing = required.filter(key => !config[key]);

  if (missing.length > 0) {
    console.error('❌ Missing required environment variables:');
    missing.forEach(key => {
      const envVar = key === 'accountId' ? 'CLOUDFLARE_ACCOUNT_ID' :
                      key === 'accessKeyId' ? 'R2_ACCESS_KEY_ID' :
                      key === 'secretAccessKey' ? 'R2_SECRET_ACCESS_KEY' :
                      'R2_BUCKET_NAME';
      console.error(`   - ${envVar}`);
    });
    console.error('\nPlease set these environment variables or add them to a .env file.');
    console.error('See R2_DEPLOYMENT.md for setup instructions.');
    process.exit(1);
  }
}

validateConfig();

// Initialize R2 client (S3-compatible)
const r2Client = new S3Client({
  region: 'auto',
  endpoint: `https://${config.accountId}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId: config.accessKeyId,
    secretAccessKey: config.secretAccessKey,
  },
});

// Calculate MD5 hash of a file
async function getFileHash(filePath) {
  const fileBuffer = await readFile(filePath);
  return createHash('md5').update(fileBuffer).digest('hex');
}

// Get ETag (hash) of a file in R2
async function getR2FileETag(key) {
  try {
    const command = new HeadObjectCommand({
      Bucket: config.bucketName,
      Key: key,
    });
    const response = await r2Client.send(command);
    // Remove quotes from ETag
    return response.ETag?.replace(/"/g, '');
  } catch (error) {
    if (error.name === 'NotFound') {
      return null; // File doesn't exist in R2
    }
    throw error;
  }
}

// Get all files recursively from a directory
async function getFiles(dir, fileList = []) {
  const files = await readdir(dir, { withFileTypes: true });

  for (const file of files) {
    const filePath = join(dir, file.name);

    if (file.isDirectory()) {
      await getFiles(filePath, fileList);
    } else {
      // Only include SVG, PNG, and JSON files
      if (file.name.match(/\.(svg|png|json)$/i)) {
        fileList.push(filePath);
      }
    }
  }

  return fileList;
}

// Upload a file to R2
async function uploadFile(localPath, r2Key) {
  const fileStream = createReadStream(localPath);
  const stats = statSync(localPath);

  // Determine content type
  const contentType = localPath.endsWith('.svg') ? 'image/svg+xml' :
                      localPath.endsWith('.png') ? 'image/png' :
                      localPath.endsWith('.json') ? 'application/json' :
                      'application/octet-stream';

  const command = new PutObjectCommand({
    Bucket: config.bucketName,
    Key: r2Key,
    Body: fileStream,
    ContentType: contentType,
    CacheControl: 'public, max-age=31536000, immutable', // Cache for 1 year
  });

  await r2Client.send(command);
  return stats.size;
}

// Main sync function
async function syncToR2() {
  console.log('🚀 Starting sync to Cloudflare R2...\n');
  console.log(`📦 Bucket: ${config.bucketName}`);
  console.log(`🔧 Account ID: ${config.accountId}\n`);

  const logosDir = join(__dirname, 'football_logos');

  try {
    // Get all local files
    console.log('📂 Scanning local files...');
    const localFiles = await getFiles(logosDir);
    console.log(`   Found ${localFiles.length} files\n`);

    let uploaded = 0;
    let skipped = 0;
    let totalBytes = 0;
    const errors = [];

    // Process each file
    for (const localPath of localFiles) {
      const relativePath = relative(logosDir, localPath);
      const r2Key = `football_logos/${relativePath}`;

      try {
        // Calculate local file hash
        const localHash = await getFileHash(localPath);

        // Get R2 file hash (ETag)
        const r2Hash = await getR2FileETag(r2Key);

        // Compare hashes
        if (r2Hash === localHash) {
          skipped++;
          process.stdout.write(`⏭️  Skip: ${relativePath}\r`);
        } else {
          // Upload file (new or modified)
          const bytes = await uploadFile(localPath, r2Key);
          totalBytes += bytes;
          uploaded++;
          console.log(`✅ ${r2Hash ? 'Updated' : 'Uploaded'}: ${relativePath}`);
        }
      } catch (error) {
        errors.push({ file: relativePath, error: error.message });
        console.error(`❌ Error: ${relativePath} - ${error.message}`);
      }
    }

    // Summary
    console.log('\n' + '='.repeat(60));
    console.log('📊 Sync Summary');
    console.log('='.repeat(60));
    console.log(`✅ Uploaded: ${uploaded} files (${formatBytes(totalBytes)})`);
    console.log(`⏭️  Skipped: ${skipped} files (unchanged)`);

    if (errors.length > 0) {
      console.log(`❌ Errors: ${errors.length} files`);
      errors.forEach(({ file, error }) => {
        console.log(`   - ${file}: ${error}`);
      });
    }

    console.log('='.repeat(60));

    if (config.publicUrl) {
      console.log(`\n🌐 Public URL: ${config.publicUrl}`);
      console.log(`   Example: ${config.publicUrl}/football_logos/england/svg/Arsenal.svg`);
    } else {
      console.log('\n💡 Tip: Set R2_PUBLIC_URL to see example URLs');
    }

    console.log('\n✨ Sync complete!');

  } catch (error) {
    console.error('\n❌ Sync failed:', error.message);
    process.exit(1);
  }
}

// Format bytes to human-readable
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Run sync
syncToR2().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
