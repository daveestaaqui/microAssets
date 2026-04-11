/**
 * Extension Loader — Shared test helpers for SporlyWorks extension testing
 *
 * Discovers extension directories, launches Chromium with extensions loaded,
 * and provides utilities for interacting with extension pages.
 */

const fs = require('fs');
const path = require('path');
const { chromium } = require('@playwright/test');

const ROOT = path.resolve(__dirname, '..', '..');

// Directories to skip when discovering extensions
const SKIP_PREFIXES = ['_', '.', '~', 'node_modules', 'test', 'build', 'dist', 'pack', 'CWS', 'marketing', 'sporlyworks_icons', 'web-ext'];
const SKIP_EXACT = new Set(['__pycache__', 'venv']);

/**
 * Discover all Chrome extension directories in the repo root.
 * An extension directory is defined as one that:
 *   1. Contains a manifest.json
 *   2. Is not a Firefox variant (no `-firefox` suffix)
 *   3. Is not in the skip list
 *
 * @returns {Array<{name: string, path: string, manifest: object}>}
 */
function discoverExtensions() {
  const entries = fs.readdirSync(ROOT, { withFileTypes: true });
  const extensions = [];

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const name = entry.name;

    // Skip non-extension directories
    if (SKIP_PREFIXES.some(prefix => name.startsWith(prefix))) continue;
    if (SKIP_EXACT.has(name)) continue;
    if (name.endsWith('-firefox')) continue;

    const manifestPath = path.join(ROOT, name, 'manifest.json');
    if (!fs.existsSync(manifestPath)) continue;

    try {
      const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
      extensions.push({
        name,
        path: path.join(ROOT, name),
        manifest,
      });
    } catch (e) {
      // Invalid JSON — will be caught by manifest lint tests
      extensions.push({
        name,
        path: path.join(ROOT, name),
        manifest: null,
      });
    }
  }

  return extensions.sort((a, b) => a.name.localeCompare(b.name));
}

/**
 * Launch a Chromium browser with a single extension loaded.
 *
 * @param {string} extensionDir — Absolute path to the extension directory
 * @param {object} [options]
 * @param {boolean} [options.headless=true] — Whether to run headless
 * @returns {Promise<{context: import('@playwright/test').BrowserContext, extensionId: string}>}
 */
async function launchWithExtension(extensionDir, options = {}) {
  const headless = options.headless ?? !process.env.DEBUG;

  const context = await chromium.launchPersistentContext('', {
    headless,
    args: [
      `--disable-extensions-except=${extensionDir}`,
      `--load-extension=${extensionDir}`,
      '--no-first-run',
      '--disable-default-apps',
      '--disable-popup-blocking',
      '--disable-translate',
      '--disable-sync',
      '--disable-background-networking',
    ],
  });

  // Wait for the service worker to register and get the extension ID
  let extensionId = '';

  // Try to get the extension ID from the service worker
  let serviceWorker;
  try {
    serviceWorker = context.serviceWorkers()[0] ||
      await context.waitForEvent('serviceworker', { timeout: 5000 });
    const swUrl = serviceWorker.url();
    const match = swUrl.match(/chrome-extension:\/\/([a-z]+)\//);
    if (match) extensionId = match[1];
  } catch {
    // Extension may not have a service worker — that's OK
    // Try to find it via the extensions page
    const extPage = await context.newPage();
    await extPage.goto('chrome://extensions/', { waitUntil: 'domcontentloaded' });

    // Extract extension ID from the extensions management page
    extensionId = await extPage.evaluate(() => {
      const manager = document.querySelector('extensions-manager');
      if (!manager || !manager.shadowRoot) return '';
      const itemList = manager.shadowRoot.querySelector('extensions-item-list');
      if (!itemList || !itemList.shadowRoot) return '';
      const item = itemList.shadowRoot.querySelector('extensions-item');
      if (!item) return '';
      return item.id || '';
    }).catch(() => '');

    await extPage.close();
  }

  return { context, extensionId };
}

/**
 * Get the popup URL for an extension.
 *
 * @param {string} extensionId
 * @param {object} manifest — The parsed manifest.json
 * @returns {string|null}
 */
function getPopupUrl(extensionId, manifest) {
  const popupPath = manifest?.action?.default_popup
    || manifest?.browser_action?.default_popup;

  if (!popupPath || !extensionId) return null;
  return `chrome-extension://${extensionId}/${popupPath}`;
}

/**
 * Scan JS files in a directory for forbidden patterns.
 *
 * @param {string} dir — Directory to scan
 * @returns {Array<{file: string, line: number, pattern: string, content: string}>}
 */
function scanForbiddenPatterns(dir) {
  const FORBIDDEN = [
    { pattern: /\beval\s*\(/, name: 'eval()' },
    { pattern: /new\s+Function\s*\(/, name: 'new Function()' },
    { pattern: /document\.write\s*\(/, name: 'document.write()' },
    { pattern: /["']http:\/\/(?!localhost)/, name: 'hardcoded http:// URL' },
    { pattern: /(['"])(sk|pk)_(live|test)_[A-Za-z0-9]{20,}\1/, name: 'possible API key' },
    { pattern: /(['"])AIza[A-Za-z0-9_-]{35}\1/, name: 'Google API key' },
    { pattern: /(['"])[A-Za-z0-9]{40}\1.*(?:token|key|secret|api)/i, name: 'possible secret token' },
  ];

  const issues = [];
  const jsFiles = findFilesRecursive(dir, /\.(js|mjs|ts)$/);

  for (const file of jsFiles) {
    const content = fs.readFileSync(file, 'utf-8');
    const lines = content.split('\n');

    for (let i = 0; i < lines.length; i++) {
      for (const { pattern, name } of FORBIDDEN) {
        if (pattern.test(lines[i])) {
          issues.push({
            file: path.relative(dir, file),
            line: i + 1,
            pattern: name,
            content: lines[i].trim().substring(0, 120),
          });
        }
      }
    }
  }

  return issues;
}

/**
 * Recursively find files matching a regex pattern.
 */
function findFilesRecursive(dir, pattern) {
  const results = [];
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== 'node_modules') {
        results.push(...findFilesRecursive(fullPath, pattern));
      } else if (entry.isFile() && pattern.test(entry.name)) {
        results.push(fullPath);
      }
    }
  } catch { /* permission denied or broken symlink */ }
  return results;
}

module.exports = {
  ROOT,
  discoverExtensions,
  launchWithExtension,
  getPopupUrl,
  scanForbiddenPatterns,
  findFilesRecursive,
};
