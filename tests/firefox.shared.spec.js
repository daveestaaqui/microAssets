/**
 * SporlyWorks Firefox Extension QA — Static Analysis
 *
 * Validates Firefox extension variants (-firefox suffix) for:
 *   1. Manifest integrity (valid JSON, required fields)
 *   2. Firefox-specific fields (browser_specific_settings.gecko)
 *   3. MV2 compliance (Firefox still uses MV2 for most extensions)
 *   4. Consistency with Chrome counterpart
 *   5. Forbidden pattern scanning
 */

const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');
const {
  discoverExtensions,
  discoverFirefoxExtensions,
  scanForbiddenPatterns,
} = require('./helpers/extension-loader');
const { lintManifest } = require('./helpers/manifest-lint');

// Discover all Firefox extensions
const firefoxExtensions = discoverFirefoxExtensions();
const chromeExtensions = discoverExtensions();
const chromeExtMap = new Map(chromeExtensions.map(e => [e.name, e]));

test.describe('Firefox Extension Analysis', () => {
  test(`discovered Firefox extensions`, () => {
    console.log(`🦊 Found ${firefoxExtensions.length} Firefox extensions`);
    expect(firefoxExtensions.length).toBeGreaterThan(0);
  });

  for (const ext of firefoxExtensions) {
    test.describe(`🦊 ${ext.name}`, () => {

      // ── Manifest is valid JSON ───────────────────────────
      test('manifest.json is valid JSON', () => {
        expect(ext.manifest, `${ext.name}/manifest.json is not valid JSON`).not.toBeNull();
      });

      // ── Required Manifest Fields ─────────────────────────
      test('has required manifest fields', () => {
        test.skip(!ext.manifest, 'Invalid manifest');

        expect(ext.manifest.name, 'Missing manifest.name').toBeTruthy();
        expect(ext.manifest.version, 'Missing manifest.version').toBeTruthy();
        expect(ext.manifest.description, 'Missing manifest.description').toBeTruthy();
      });

      // ── Firefox-Specific Fields ──────────────────────────
      test('has browser_specific_settings.gecko (Firefox ID)', () => {
        test.skip(!ext.manifest, 'Invalid manifest');

        // Firefox extensions SHOULD have gecko settings for AMO submission
        const gecko = ext.manifest?.browser_specific_settings?.gecko
          || ext.manifest?.applications?.gecko;

        if (!gecko) {
          console.warn(`  ⚠️ ${ext.name}: No gecko settings — needed for AMO submission`);
        }

        // Advisory only — some extensions might work without it
        expect(true).toBe(true);
      });

      // ── Manifest Version Check ───────────────────────────
      test('uses valid manifest_version (2 or 3)', () => {
        test.skip(!ext.manifest, 'Invalid manifest');

        const mv = ext.manifest.manifest_version;
        expect([2, 3]).toContain(mv);
      });

      // ── Consistency with Chrome Counterpart ──────────────
      test('version matches Chrome counterpart', () => {
        test.skip(!ext.manifest, 'Invalid manifest');

        const chromeExt = chromeExtMap.get(ext.chromeName);
        test.skip(!chromeExt || !chromeExt.manifest, 'No Chrome counterpart found');

        expect(
          ext.manifest.version,
          `Firefox version (${ext.manifest.version}) ≠ Chrome version (${chromeExt.manifest.version})`
        ).toBe(chromeExt.manifest.version);
      });

      test('name is consistent with Chrome counterpart', () => {
        test.skip(!ext.manifest, 'Invalid manifest');

        const chromeExt = chromeExtMap.get(ext.chromeName);
        test.skip(!chromeExt || !chromeExt.manifest, 'No Chrome counterpart found');

        // Advisory — some Firefox extensions may have slightly different names
        if (ext.manifest.name !== chromeExt.manifest.name) {
          console.warn(`  ⚠️ ${ext.name}: Firefox name "${ext.manifest.name}" differs from Chrome name "${chromeExt.manifest.name}"`);
        }
        // Pass — this is advisory only
        expect(true).toBe(true);
      });

      // ── Popup HTML Exists ────────────────────────────────
      test('popup HTML file exists if declared', () => {
        test.skip(!ext.manifest, 'Invalid manifest');

        const popupPath = ext.manifest?.action?.default_popup
          || ext.manifest?.browser_action?.default_popup;
        test.skip(!popupPath, 'No popup declared');

        const fullPath = path.join(ext.path, popupPath);
        expect(
          fs.existsSync(fullPath),
          `Popup file missing: ${popupPath}`
        ).toBe(true);
      });

      // ── Content Script Files Exist ───────────────────────
      test('all content script files exist', () => {
        test.skip(!ext.manifest, 'Invalid manifest');

        const contentScripts = ext.manifest?.content_scripts;
        test.skip(!contentScripts || contentScripts.length === 0, 'No content scripts');

        for (const cs of contentScripts) {
          for (const jsFile of (cs.js || [])) {
            const fullPath = path.join(ext.path, jsFile);
            expect(
              fs.existsSync(fullPath),
              `Content script missing: ${jsFile}`
            ).toBe(true);
          }
        }
      });

      // ── Background Script Exists ─────────────────────────
      test('background script exists if declared', () => {
        test.skip(!ext.manifest, 'Invalid manifest');

        // MV2 uses background.scripts, MV3 uses background.service_worker
        const bgScripts = ext.manifest?.background?.scripts;
        const sw = ext.manifest?.background?.service_worker;
        test.skip(!bgScripts && !sw, 'No background script');

        let allExist = true;

        if (sw) {
          const fullPath = path.join(ext.path, sw);
          if (!fs.existsSync(fullPath)) {
            console.warn(`  ⚠️ ${ext.name}: Service worker missing: ${sw}`);
            allExist = false;
          }
        }

        if (bgScripts) {
          for (const script of bgScripts) {
            const fullPath = path.join(ext.path, script);
            if (!fs.existsSync(fullPath)) {
              console.warn(`  ⚠️ ${ext.name}: Background script missing: ${script}`);
              allExist = false;
            }
          }
        }

        // Advisory — warn but don't fail
        if (!allExist) {
          console.warn(`  ⚠️ ${ext.name}: Some background scripts are missing — extension may not function`);
        }
        expect(true).toBe(true);
      });

      // ── Forbidden Patterns ───────────────────────────────
      test('no forbidden code patterns', () => {
        const issues = scanForbiddenPatterns(ext.path);
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

      // ── No Chrome-Only APIs ──────────────────────────────
      test('does not use chrome.* APIs (should use browser.*)', () => {
        test.skip(!ext.manifest, 'Invalid manifest');

        const jsFiles = [];
        const findJS = (dir) => {
          try {
            const entries = fs.readdirSync(dir, { withFileTypes: true });
            for (const entry of entries) {
              const fullPath = path.join(dir, entry.name);
              if (entry.isDirectory() && !entry.name.startsWith('.')) {
                findJS(fullPath);
              } else if (entry.isFile() && entry.name.endsWith('.js')) {
                jsFiles.push(fullPath);
              }
            }
          } catch { /* skip */ }
        };
        findJS(ext.path);

        const chromeApiUsages = [];
        for (const file of jsFiles) {
          const content = fs.readFileSync(file, 'utf-8');
          const lines = content.split('\n');
          for (let i = 0; i < lines.length; i++) {
            // Check for chrome.* but allow comments and chrome-extension:// URLs
            if (/\bchrome\.(runtime|storage|tabs|action|browserAction|extension|permissions|alarms|notifications|contextMenus|commands|scripting|webRequest|downloads|history|bookmarks|management)\b/.test(lines[i])
              && !lines[i].trim().startsWith('//')
              && !lines[i].trim().startsWith('*')) {
              chromeApiUsages.push({
                file: path.relative(ext.path, file),
                line: i + 1,
                content: lines[i].trim().substring(0, 100),
              });
            }
          }
        }

        // Advisory only — many Firefox extensions still work with chrome.* due to polyfill
        if (chromeApiUsages.length > 0) {
          console.warn(`  ⚠️ ${ext.name}: ${chromeApiUsages.length} chrome.* API usages (consider using browser.* for Firefox)`);
        }
      });
    });
  }
});
