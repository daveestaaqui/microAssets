// @ts-check
const { defineConfig } = require('@playwright/test');

/**
 * SporlyWorks Extension Testing — Playwright Config
 *
 * Chromium-only (extensions aren't supported in Playwright's Firefox/WebKit).
 * Uses persistent context with --load-extension args in the test files themselves.
 */
module.exports = defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.js',

  /* Maximum time a single test can run */
  timeout: 30_000,

  /* Fail the build on console errors in tests */
  expect: {
    timeout: 10_000,
  },

  /* Retry once on CI to handle flaky extension load races */
  retries: process.env.CI ? 1 : 0,

  /* Parallel workers — each extension gets its own browser context */
  workers: process.env.CI ? 2 : 4,

  /* Reporter configuration */
  reporter: process.env.CI
    ? [['github'], ['html', { open: 'never', outputFolder: 'test-results/html-report' }]]
    : [['list'], ['html', { open: 'on-failure', outputFolder: 'test-results/html-report' }]],

  /* Shared settings for all projects */
  use: {
    /* Capture screenshot on failure */
    screenshot: 'only-on-failure',

    /* Record trace on first retry */
    trace: 'on-first-retry',

    /* No default base URL — extensions use chrome-extension:// protocol */
  },

  /* Single project: Chromium with extension support */
  projects: [
    {
      name: 'chromium-extensions',
      use: {
        /* We launch persistent contexts manually in tests to load extensions */
      },
    },
  ],

  /* Output directory for test artifacts */
  outputDir: 'test-results/artifacts',
});
