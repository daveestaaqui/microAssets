/**
 * SporlyWorks — Smooth Page Transitions
 * Creates a subtle fade overlay on internal link navigation.
 * Works alongside the CSS View Transitions API for browsers that support it.
 */
(function() {
    // Create transition overlay
    const overlay = document.createElement('div');
    overlay.className = 'page-transition-overlay';
    document.body.appendChild(overlay);

    // Fade in on page load (remove any lingering overlay)
    window.addEventListener('pageshow', () => {
        overlay.classList.remove('active');
    });

    // Intercept internal link clicks for smooth exit
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a[href]');
        if (!link) return;
        const href = link.getAttribute('href');
        
        // Skip anchors, external links, mailto, tel, javascript
        if (!href || href.startsWith('#') || href.startsWith('mailto:') || 
            href.startsWith('tel:') || href.startsWith('javascript:') ||
            link.target === '_blank' || link.hasAttribute('download')) return;
        
        // Skip external links
        try {
            const url = new URL(href, window.location.origin);
            if (url.origin !== window.location.origin) return;
        } catch(err) { return; }

        e.preventDefault();
        overlay.classList.add('active');
        setTimeout(() => { window.location.href = href; }, 200);
    });
})();
