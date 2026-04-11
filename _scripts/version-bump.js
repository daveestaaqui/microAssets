#!/usr/bin/env node
/**
 * SporlyWorks — Auto Version Bump
 *
 * Automatically increments the patch version of all Chrome extension manifests
 * that were modified in the current commit. This prevents CWS upload collisions
 * when re-submitting extensions.
 *
 * Usage:
 *   node _scripts/version-bump.js                   # Bump all extensions
 *   node _scripts/version-bump.js --changed-only     # Bump only git-changed extensions
 *   node _scripts/version-bump.js --extension foo     # Bump a specific extension
 *   node _scripts/version-bump.js --set 2.1.0        # Set exact version for all
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');

// ── Parse CLI Args ─────────────────────────────────────────────────────
const args = process.argv.slice(2);
const changedOnly = args.includes('--changed-only');
const extensionArg = args.includes('--extension') ? args[args.indexOf('--extension') + 1] : null;
const setVersion = args.includes('--set') ? args[args.indexOf('--set') + 1] : null;
const dryRun = args.includes('--dry-run');

// Directories to skip
const SKIP_PREFIXES = ['_', '.', '~', 'node_modules', 'test', 'build', 'dist', 'pack', 'CWS', 'marketing', 'sporlyworks_icons', 'web-ext'];
const SKIP_EXACT = new Set(['__pycache__', 'venv']);

/**
 * Discover all extension directories (Chrome + Firefox)
 */
function discoverAllExtensions() {
  const entries = fs.readdirSync(ROOT, { withFileTypes: true });
  const extensions = [];

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const name = entry.name;
    if (SKIP_PREFIXES.some(prefix => name.startsWith(prefix))) continue;
    if (SKIP_EXACT.has(name)) continue;

    const manifestPath = path.join(ROOT, name, 'manifest.json');
    if (!fs.existsSync(manifestPath)) continue;

    extensions.push({ name, manifestPath });
  }

  return extensions;
}

/**
 * Get list of extension directories changed in the last commit
 */
function getChangedExtensions() {
  try {
    const output = execSync('git diff --name-only HEAD~1 HEAD', { cwd: ROOT, encoding: 'utf-8' });
    const changedDirs = new Set();

    for (const file of output.split('\n').filter(Boolean)) {
      const parts = file.split('/');
      if (parts.length > 1) {
        changedDirs.add(parts[0]);
      }
    }

    return changedDirs;
  } catch {
    console.warn('⚠️  Could not determine changed files — bumping all');
    return null; // Bump all if we can't determine
  }
}

/**
 * Increment patch version: "1.2.3" → "1.2.4"
 */
function bumpPatch(version) {
  const parts = version.split('.');
  if (parts.length < 3) parts.push('0');
  parts[parts.length - 1] = String(parseInt(parts[parts.length - 1], 10) + 1);
  return parts.join('.');
}

// ── Main ───────────────────────────────────────────────────────────────
function main() {
  let extensions = discoverAllExtensions();
  const changedDirs = changedOnly ? getChangedExtensions() : null;

  // Filter to specific extension if requested
  if (extensionArg) {
    extensions = extensions.filter(e => e.name === extensionArg);
    if (extensions.length === 0) {
      console.error(`❌ Extension "${extensionArg}" not found`);
      process.exit(1);
    }
  }

  // Filter to changed-only if requested
  if (changedDirs) {
    extensions = extensions.filter(e => changedDirs.has(e.name));
  }

  console.log(`\n📦 Version bump — ${extensions.length} extensions\n`);

  let updated = 0;
  const results = [];

  for (const ext of extensions) {
    try {
      const manifest = JSON.parse(fs.readFileSync(ext.manifestPath, 'utf-8'));
      const oldVersion = manifest.version || '0.0.0';
      const newVersion = setVersion || bumpPatch(oldVersion);

      if (oldVersion === newVersion) {
        results.push({ name: ext.name, old: oldVersion, new: newVersion, status: 'unchanged' });
        continue;
      }

      manifest.version = newVersion;

      if (!dryRun) {
        fs.writeFileSync(ext.manifestPath, JSON.stringify(manifest, null, 2) + '\n');
      }

      results.push({ name: ext.name, old: oldVersion, new: newVersion, status: dryRun ? 'dry-run' : 'bumped' });
      updated++;
    } catch (err) {
      results.push({ name: ext.name, old: '???', new: '???', status: `error: ${err.message}` });
    }
  }

  // Print results table
  console.log('  Extension'.padEnd(45) + 'Old'.padEnd(12) + 'New'.padEnd(12) + 'Status');
  console.log('  ' + '─'.repeat(70));
  for (const r of results) {
    console.log(`  ${r.name.padEnd(43)} ${r.old.padEnd(12)}${r.new.padEnd(12)}${r.status}`);
  }

  console.log(`\n✅ ${updated} extensions ${dryRun ? 'would be' : ''} updated\n`);

  // Set output for GitHub Actions
  if (process.env.GITHUB_OUTPUT) {
    fs.appendFileSync(process.env.GITHUB_OUTPUT, `bumped_count=${updated}\n`);
    fs.appendFileSync(process.env.GITHUB_OUTPUT, `bumped_extensions=${results.filter(r => r.status === 'bumped').map(r => r.name).join(',')}\n`);
  }

  return updated;
}

main();
