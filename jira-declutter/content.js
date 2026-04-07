// Jira Declutter
(function() {
  'use strict';
  const KEY = 'jira_declutter_enabled';
  chrome.storage.local.get([KEY], r => {
    if (r[KEY] === false) return;
    const style = document.createElement('style');
    style.textContent = `
      /* Hide top navigation banner/ads */
      [data-testid="atlassian-navigation"], .aui-banner { display: none !important; }
      /* Hide sidebar promotions */
      [data-testid="sidebar-recommendations"], .aui-sidebar-footer { display: none !important; }
      /* Simplify board view */
      [data-testid="software-board.header"] .css-1h4m4hb { display: none !important; }
      /* Hide feedback widgets */
      [data-testid="feedback-button"], .atlaskit-portal-container { display: none !important; }
      /* Collapse empty swimlanes */
      .ghx-swimlane:empty { display: none !important; }
      /* Clean issue detail panel */
      .aui-nav-breadcrumbs { margin: 0 !important; }
    `;
    document.head.appendChild(style);
  });
  chrome.runtime.onMessage.addListener(msg => {
    if (msg.type === 'TOGGLE') location.reload();
  });
})();
