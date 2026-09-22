/**
 * SporlyWorks Client-Side Telemetry & Analytics Engine (v1.0)
 * Privacy-first, zero-cookie event tracking for mycology tools and affiliate conversions.
 */

(function () {
    'use strict';

    var STORAGE_KEY = 'sporly_telemetry_events';
    var MAX_EVENTS = 100;

    var SporlyAnalytics = {
        init: function () {
            this.trackPageView();
            this.bindAffiliateClicks();
            this.bindToolInteractions();
            this.bindScrollTracking();
        },

        getEvents: function () {
            try {
                var stored = localStorage.getItem(STORAGE_KEY);
                return stored ? JSON.parse(stored) : [];
            } catch (e) {
                return [];
            }
        },

        track: function (eventType, metadata) {
            var event = {
                type: eventType,
                url: window.location.pathname,
                referrer: document.referrer || 'direct',
                timestamp: new Date().toISOString(),
                data: metadata || {}
            };

            try {
                var events = this.getEvents();
                events.unshift(event);
                if (events.length > MAX_EVENTS) {
                    events = events.slice(0, MAX_EVENTS);
                }
                localStorage.setItem(STORAGE_KEY, JSON.stringify(events));
            } catch (e) {
                // Local storage disabled or full
            }

            // Beacon hook for future backend / Cloudflare Worker ingestion
            if (navigator.sendBeacon && window._sporlyBeaconUrl) {
                try {
                    navigator.sendBeacon(window._sporlyBeaconUrl, JSON.stringify(event));
                } catch (err) {}
            }
        },

        trackPageView: function () {
            this.track('page_view', {
                title: document.title,
                screen: window.innerWidth + 'x' + window.innerHeight
            });
        },

        bindAffiliateClicks: function () {
            var self = this;
            document.addEventListener('click', function (e) {
                var target = e.target.closest('a');
                if (!target) return;

                var partner = target.getAttribute('data-partner') || target.getAttribute('data-affiliate-partner');
                var href = target.getAttribute('href') || '';

                if (partner || href.indexOf('ref=') !== -1 || href.indexOf('awin1.com') !== -1) {
                    self.track('affiliate_click', {
                        partner: partner || 'unknown',
                        href: href,
                        text: (target.innerText || '').trim().substring(0, 60),
                        rel: target.getAttribute('rel') || ''
                    });
                }
            }, true);
        },

        bindToolInteractions: function () {
            var self = this;
            // Listen for tool export buttons
            document.addEventListener('click', function (e) {
                var target = e.target.closest('button, .btn-dossier, .btn-rec-cta, .btn-cta');
                if (!target) return;

                var text = (target.innerText || '').trim();
                if (text.indexOf('Export') !== -1 || text.indexOf('Download') !== -1 || text.indexOf('Protocol') !== -1) {
                    self.track('tool_export', {
                        label: text.substring(0, 50),
                        tool: window.location.pathname
                    });
                }
            });
        },

        bindScrollTracking: function () {
            var self = this;
            var milestones = { 25: false, 50: false, 75: false, 100: false };
            var ticking = false;

            window.addEventListener('scroll', function () {
                if (!ticking) {
                    window.requestAnimationFrame(function () {
                        var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                        var docHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                        if (docHeight <= 0) return;
                        var pct = Math.round((scrollTop / docHeight) * 100);

                        [25, 50, 75, 100].forEach(function (mark) {
                            if (pct >= mark && !milestones[mark]) {
                                milestones[mark] = true;
                                self.track('scroll_depth', { depth: mark });
                            }
                        });
                        ticking = false;
                    });
                    ticking = true;
                }
            }, { passive: true });
        },

        getSummary: function () {
            var events = this.getEvents();
            var summary = {
                totalEvents: events.length,
                affiliateClicks: 0,
                byPartner: {},
                pageViews: 0,
                toolExports: 0
            };

            events.forEach(function (ev) {
                if (ev.type === 'page_view') summary.pageViews++;
                if (ev.type === 'tool_export') summary.toolExports++;
                if (ev.type === 'affiliate_click') {
                    summary.affiliateClicks++;
                    var p = ev.data.partner || 'other';
                    summary.byPartner[p] = (summary.byPartner[p] || 0) + 1;
                }
            });

            return summary;
        }
    };

    window.SporlyAnalytics = SporlyAnalytics;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () { SporlyAnalytics.init(); });
    } else {
        SporlyAnalytics.init();
    }
})();
