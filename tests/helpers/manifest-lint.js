/**
 * Manifest Lint — Fast static validation for all extension manifests
 *
 * Run standalone: node tests/helpers/manifest-lint.js
 * Also used by the test suite for manifest integrity checks.
 */

const { discoverExtensions } = require('./extension-loader');

const REQUIRED_FIELDS = ['name', 'version', 'description', 'manifest_version'];
const REQUIRED_ICON_SIZES = ['16', '48', '128'];
const MAX_DESCRIPTION_LENGTH = 132; // Chrome Web Store limit
const SEMVER_REGEX = /^\d+\.\d+\.\d+$/;

/**
 * Validate a single extension's manifest.
 *
 * @param {{name: string, path: string, manifest: object|null}} ext
 * @returns {{errors: string[], warnings: string[]}}
 */
function lintManifest(ext) {
  const errors = [];
  const warnings = [];

  if (!ext.manifest) {
    errors.push('manifest.json is not valid JSON');
    return { errors, warnings };
  }

  const m = ext.manifest;

  // Required fields
  for (const field of REQUIRED_FIELDS) {
    if (!m[field]) {
      errors.push(`Missing required field: "${field}"`);
    }
  }

  // Manifest version must be 3
  if (m.manifest_version && m.manifest_version !== 3) {
    errors.push(`manifest_version is ${m.manifest_version}, must be 3 (MV3)`);
  }

  // Version format
  if (m.version && !SEMVER_REGEX.test(m.version)) {
    warnings.push(`Version "${m.version}" is not strict semver (x.y.z)`);
  }

  // Description length
  if (m.description && m.description.length > MAX_DESCRIPTION_LENGTH) {
    errors.push(`Description is ${m.description.length} chars, max is ${MAX_DESCRIPTION_LENGTH}`);
  }

  // Icons
  if (m.icons) {
    for (const size of REQUIRED_ICON_SIZES) {
      if (!m.icons[size]) {
        warnings.push(`Missing icon size: ${size}px`);
      }
    }
  } else {
    errors.push('Missing "icons" object in manifest');
  }

  // Permissions audit (warnings, not errors)
  const allPerms = [...(m.permissions || []), ...(m.host_permissions || [])];
  if (allPerms.includes('<all_urls>')) {
    warnings.push('Uses <all_urls> — consider using activeTab + specific host_permissions');
  }
  if (allPerms.includes('webRequestBlocking')) {
    errors.push('webRequestBlocking is not available in MV3 — use declarativeNetRequest');
  }
  if (allPerms.includes('nativeMessaging')) {
    warnings.push('Uses nativeMessaging — ensure this is intentional');
  }

  // Background script check
  if (m.background) {
    if (m.background.scripts) {
      errors.push('background.scripts (MV2) detected — use background.service_worker for MV3');
    }
  }

  return { errors, warnings };
}

/**
 * Run lint on all extensions and return results.
 */
function lintAll() {
  const extensions = discoverExtensions();
  const results = [];

  for (const ext of extensions) {
    const { errors, warnings } = lintManifest(ext);
    results.push({ name: ext.name, errors, warnings });
  }

  return results;
}

// If run directly (not imported), print results and exit
if (require.main === module) {
  const results = lintAll();
  let hasErrors = false;

  for (const { name, errors, warnings } of results) {
    if (errors.length === 0 && warnings.length === 0) continue;

    console.log(`\n📦 ${name}`);
    for (const err of errors) {
      console.log(`  ❌ ${err}`);
      hasErrors = true;
    }
    for (const warn of warnings) {
      console.log(`  ⚠️  ${warn}`);
    }
  }

  const total = results.length;
  const errCount = results.filter(r => r.errors.length > 0).length;
  const warnCount = results.filter(r => r.warnings.length > 0).length;
  const passCount = total - errCount;

  console.log(`\n${'═'.repeat(50)}`);
  console.log(`📊 ${total} extensions scanned`);
  console.log(`   ✅ ${passCount} passed | ❌ ${errCount} with errors | ⚠️  ${warnCount} with warnings`);
  console.log(`${'═'.repeat(50)}\n`);

  process.exit(hasErrors ? 1 : 0);
}

module.exports = { lintManifest, lintAll };
