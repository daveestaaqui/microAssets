// Quick Note Taker — Background Service Worker
// Handles extension installation and lifecycle events

chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    // Initialize default notes storage
    chrome.storage.local.set({ notes: [] });
  }
});
