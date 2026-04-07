// OmniSuite Background Service Worker
// Handles lifecycle events: install tracking, uninstall feedback, onboarding

chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    // Track fresh install + set uninstall feedback URL
    chrome.runtime.setUninstallURL("https://daveestaaqui.github.io/micro-assets-landing-page/feedback.html");
    console.log("[OmniSuite] Extension installed. Uninstall feedback URL set.");
  } else if (details.reason === 'update') {
    console.log("[OmniSuite] Extension updated to version", chrome.runtime.getManifest().version);
  }
});

// Ensure uninstall URL is always set (covers updates too)
try {
  chrome.runtime.setUninstallURL("https://daveestaaqui.github.io/micro-assets-landing-page/feedback.html");
} catch (e) {
  // Silently handle — some contexts don't support this
}
