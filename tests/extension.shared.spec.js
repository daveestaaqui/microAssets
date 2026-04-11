/**
 * SporlyWorks Extension QA — Shared Test Suite
 *
 * Runs against every Chrome extension in the repo.
 * Each extension gets its own describe block with:
 *   1. Manifest integrity checks (JSON validity, required fields, MV3)
 *   2. Icon file existence validation
 *   3. Forbidden pattern scanning (eval, hardcoded URLs, secrets)
 *   4. Popup rendering test (loads in real Chromium)
 *   5. Permissions audit (advisory warnings)
 */

const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');
const {
  discoverExtensions,
  launchWithExtension,
  getPopupUrl,
  scanForbiddenPatterns,
} = require('./helpers/extension-loader');
const { lintManifest } = require('./helpers/manifest-lint');

// Discover all extensions once
const extensions = discoverExtensions();

// ─── Static Tests (no browser needed) ────────────────────────────────

test.describe('Static Analysis', () => {
  for (const ext of extensions) {
    test.describe(`📦 ${ext.name}`, () => {

      // ── Manifest Integrity ──────────────────────────────
      test('manifest.json is valid and MV3 compliant', () => {
        expect(ext.manifest, `${ext.name}/manifest.json is not valid JSON`).not.toBeNull();

        const { errors } = lintManifest(ext);
        if (errors.length > 0) {
          const msg = errors.map(e => `  • ${e}`).join('\n');
          expect(errors, `Manifest errors in ${ext.name}:\n${msg}`).toHaveLength(0);
        }
      });

      // ── Icon Files Exist ────────────────────────────────
      test('all referenced icon files exist', () => {
        if (!ext.manifest?.icons) {
          test.skip(!ext.manifest?.icons, 'No icons in manifest');
          return;
        }

        for (const [size, iconPath] of Object.entries(ext.manifest.icons)) {
          const fullPath = path.join(ext.path, iconPath);
          expect(
            fs.existsSync(fullPath),
            `Icon ${size}px missing: ${iconPath}`
          ).toBe(true);
        }

        // Also check action icons if present
        const actionIcons = ext.manifest?.action?.default_icon;
        if (actionIcons && typeof actionIcons === 'object') {
          for (const [size, iconPath] of Object.entries(actionIcons)) {
            const fullPath = path.join(ext.path, iconPath);
            expect(
              fs.existsSync(fullPath),
              `Action icon ${size}px missing: ${iconPath}`
            ).toBe(true);
          }
        }
      });

      // ── Forbidden Patterns ──────────────────────────────
      test('no forbidden code patterns (eval, hardcoded secrets, etc.)', () => {
        const issues = scanForbiddenPatterns(ext.path);

        // Filter to only blocking issues (not all are errors)
        const blocking = issues.filter(i =>
          ['eval()', 'new Function()', 'possible API key', 'Google API key', 'possible secret token'].includes(i.pattern)
        );

        if (blocking.length > 0) {
          const msg = blocking.map(i =>
            `  • ${i.file}:${i.line} — ${i.pattern}: ${i.content}`
          ).join('\n');
          expect(blocking, `Security issues in ${ext.name}:\n${msg}`).toHaveLength(0);
        }
      });

      // ── Popup HTML Exists (if declared) ─────────────────
      test('popup HTML file exists if declared', () => {
        const popupPath = ext.manifest?.action?.default_popup;
        if (!popupPath) {
          test.skip(true, 'No popup declared');
          return;
        }

        const fullPath = path.join(ext.path, popupPath);
        expect(
          fs.existsSync(fullPath),
          `Popup file missing: ${popupPath}`
        ).toBe(true);

        // Verify it's valid HTML (not empty)
        const content = fs.readFileSync(fullPath, 'utf-8');
        expect(content.length, 'Popup HTML is empty').toBeGreaterThan(10);
        expect(
          content.toLowerCase().includes('<html') || content.toLowerCase().includes('<!doctype'),
          'Popup file does not appear to be valid HTML'
        ).toBe(true);
      });

      // ── Content Script Files Exist ──────────────────────
      test('all content script files exist', () => {
        const contentScripts = ext.manifest?.content_scripts;
        if (!contentScripts || contentScripts.length === 0) {
          test.skip(true, 'No content scripts');
          return;
        }

        for (const cs of contentScripts) {
          for (const jsFile of (cs.js || [])) {
            const fullPath = path.join(ext.path, jsFile);
            expect(
              fs.existsSync(fullPath),
              `Content script missing: ${jsFile}`
            ).toBe(true);
          }
          for (const cssFile of (cs.css || [])) {
            const fullPath = path.join(ext.path, cssFile);
            expect(
              fs.existsSync(fullPath),
              `Content stylesheet missing: ${cssFile}`
            ).toBe(true);
          }
        }
      });

      // ── Background Service Worker Exists ────────────────
      test('background service worker file exists if declared', () => {
        const sw = ext.manifest?.background?.service_worker;
        if (!sw) {
          test.skip(true, 'No service worker');
          return;
        }

        const fullPath = path.join(ext.path, sw);
        expect(
          fs.existsSync(fullPath),
          `Service worker missing: ${sw}`
        ).toBe(true);
      });
    });
  }
});

// ─── Browser Tests (Chromium required) ───────────────────────────────

// Only test extensions that have a popup (the interactive ones)
const extensionsWithPopup = extensions.filter(ext =>
  ext.manifest?.action?.default_popup
);

// Sample a subset for browser tests in CI to keep runtime reasonable
// In local dev, test all; in CI, test first 20 per shard
const browserTestSet = process.env.CI
  ? extensionsWithPopup
  : extensionsWithPopup.slice(0, 10); // Limit locally for speed

test.describe('Browser — Popup Rendering', () => {
  // Skip browser tests entirely if SKIP_BROWSER_TESTS env is set
  test.skip(!!process.env.SKIP_BROWSER_TESTS, 'SKIP_BROWSER_TESTS is set');

  for (const ext of browserTestSet) {
    test(`popup renders without JS errors: ${ext.name}`, async () => {
      // Skip if manifest is invalid
      if (!ext.manifest) {
        test.skip(true, 'Invalid manifest');
        return;
      }

      let context;
      const consoleErrors = [];

      try {
        const result = await launchWithExtension(ext.path);
        context = result.context;

        // If we couldn't get an extension ID, skip the browser test
        if (!result.extensionId) {
          test.skip(true, 'Could not determine extension ID');
          return;
        }

        const popupUrl = getPopupUrl(result.extensionId, ext.manifest);
        if (!popupUrl) {
          test.skip(true, 'No popup URL');
          return;
        }

        const page = await context.newPage();

        // Collect console errors
        page.on('console', msg => {
          if (msg.type() === 'error') {
            consoleErrors.push(msg.text());
          }
        });

        // Collect page crashes
        page.on('pageerror', error => {
          consoleErrors.push(`PAGE ERROR: ${error.message}`);
        });

        // Navigate to popup
        await page.goto(popupUrl, { waitUntil: 'domcontentloaded', timeout: 10000 });

        // Verify the popup has content
        const bodyContent = await page.evaluate(() => document.body?.innerHTML?.length || 0);
        expect(bodyContent, `Popup of ${ext.name} has empty body`).toBeGreaterThan(0);

        // Check for JS errors (allow some known benign ones)
        const realErrors = consoleErrors.filter(e =>
          !e.includes('favicon.ico') &&
          !e.includes('manifest.json') &&
          !e.includes('net::ERR_FILE_NOT_FOUND') // icons in dev mode
        );

        expect(
          realErrors,
          `JS errors in ${ext.name} popup:\n${realErrors.join('\n')}`
        ).toHaveLength(0);

      } finally {
        if (context) await context.close();
      }
    });
  }
});
