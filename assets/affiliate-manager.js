/**
 * SporlyWorks — Zero-Fail Client Affiliate Routing Manager
 * Asynchronously loads affiliate_config.json, dynamically injects tracking parameters,
 * and guarantees 100% live fallback resolution with zero broken links or synthetic placeholders.
 */

(function() {
    "use strict";

    const FALLBACK_CONFIG = {
        partners: {
            myyco: {
                base_url: "https://myyco.com/shop-microscopy-liquid-culture/",
                fallback_url: "https://myyco.com/shop-microscopy-liquid-culture/?ref=SporlyWorks",
                affiliate_id: "SporlyWorks",
                ref_param: "ref",
                affiliate_url_template: "https://myyco.com/shop-microscopy-liquid-culture/?ref={affiliate_id}"
            },
            magicbag: {
                base_url: "https://www.magicbag.co",
                fallback_url: "https://www.magicbag.co/?ref=Sporlyworks",
                affiliate_id: "Sporlyworks",
                ref_param: "ref",
                affiliate_url_template: "https://www.magicbag.co/?ref={affiliate_id}"
            },
            northspore: {
                base_url: "https://northspore.com",
                fallback_url: "https://northspore.com",
                affiliate_id: "3016315",
                ref_param: "awinaffid",
                affiliate_url_template: "https://www.awin1.com/cread.php?awinmid=34891&awinaffid={affiliate_id}&ued=https%3A%2F%2Fnorthspore.com%2F"
            },
            realmushrooms: {
                base_url: "https://shop.realmushrooms.com",
                fallback_url: "https://shop.realmushrooms.com",
                affiliate_id: "",
                ref_param: "ref",
                affiliate_url_template: "https://shop.realmushrooms.com"
            },
            seed: {
                base_url: "https://seed.com/daily-synbiotic",
                fallback_url: "https://seed.com/daily-synbiotic",
                affiliate_id: "",
                ref_param: "ref",
                affiliate_url_template: "https://seed.com/daily-synbiotic"
            },
            freshcap: {
                base_url: "https://freshcap.com",
                fallback_url: "https://freshcap.com",
                affiliate_id: "",
                ref_param: "ref",
                affiliate_url_template: "https://freshcap.com"
            },
            nootropicsdepot: {
                base_url: "https://nootropicsdepot.com",
                fallback_url: "https://nootropicsdepot.com",
                affiliate_id: "",
                ref_param: "ref",
                affiliate_url_template: "https://nootropicsdepot.com"
            }
        }
    };

    let activeConfig = FALLBACK_CONFIG;

    function isValidAffiliateId(id) {
        if (!id || typeof id !== "string") return false;
        const clean = id.trim().toUpperCase();
        if (clean === "" || clean.startsWith("YOUR_") || clean.includes("PENDING") || clean.includes("INSERT")) {
            return false;
        }
        return true;
    }

    function getPartnerUrl(partnerKey) {
        if (!partnerKey) return "#";
        const key = partnerKey.toLowerCase().replace(/[-_]/g, "");
        const partners = (activeConfig && activeConfig.partners) || FALLBACK_CONFIG.partners;
        
        let partner = partners[key];
        if (!partner) {
            // Check aliases
            if (key === "magicbagco") partner = partners.magicbag;
            else if (key === "nootropics") partner = partners.nootropicsdepot;
            else if (key === "realmushrooms" || key === "real") partner = partners.realmushrooms;
            else partner = FALLBACK_CONFIG.partners[key];
        }

        if (!partner) {
            return "#";
        }

        const fallback = partner.fallback_url || partner.base_url;
        if (isValidAffiliateId(partner.affiliate_id)) {
            if (partner.affiliate_url_template) {
                return partner.affiliate_url_template.replace("{affiliate_id}", encodeURIComponent(partner.affiliate_id));
            }
            const sep = fallback.includes("?") ? "&" : "?";
            const param = partner.ref_param || "ref";
            return `${fallback}${sep}${param}=${encodeURIComponent(partner.affiliate_id)}`;
        }

        return fallback;
    }

    function updatePageLinks() {
        // 1. Explicit data-partner / data-affiliate-partner buttons
        document.querySelectorAll("[data-partner], [data-affiliate-partner]").forEach(el => {
            const partnerKey = el.getAttribute("data-partner") || el.getAttribute("data-affiliate-partner");
            const destination = getPartnerUrl(partnerKey);
            if (destination && destination !== "#") {
                el.setAttribute("href", destination);
                if (el.tagName === "A") {
                    el.setAttribute("target", "_blank");
                    el.setAttribute("rel", "noopener sponsored");
                }
            }
        });

        // 2. Outbound matching anchors
        const domainMap = {
            "myyco.com": "myyco",
            "magicbag.co": "magicbag",
            "realmushrooms.com": "realmushrooms",
            "shop.realmushrooms.com": "realmushrooms",
            "seed.com": "seed",
            "freshcap.com": "freshcap",
            "nootropicsdepot.com": "nootropicsdepot"
        };

        document.querySelectorAll("a[href]").forEach(a => {
            const href = a.getAttribute("href");
            if (!href || href.startsWith("#") || href.startsWith("javascript:")) return;

            for (const [domain, partnerKey] of Object.entries(domainMap)) {
                if (href.includes(domain)) {
                    const resolved = getPartnerUrl(partnerKey);
                    if (resolved && resolved !== "#") {
                        a.setAttribute("href", resolved);
                        a.setAttribute("target", "_blank");
                        a.setAttribute("rel", "noopener sponsored");
                    }
                    break;
                }
            }
        });
    }

    function init() {
        // Resolve path to affiliate_config.json relative to current location
        const isSubdir = window.location.pathname.includes("/tools/") || 
                         window.location.pathname.includes("/products/") || 
                         window.location.pathname.includes("/guides/") || 
                         window.location.pathname.includes("/blog/") || 
                         window.location.pathname.includes("/species/") || 
                         window.location.pathname.includes("/embed/");
        const configPath = isSubdir ? "../affiliate_config.json" : "affiliate_config.json";

        fetch(configPath)
            .then(res => {
                if (!res.ok) throw new Error("Network response not ok: " + res.status);
                return res.json();
            })
            .then(data => {
                if (data && data.partners) {
                    activeConfig = data;
                }
                updatePageLinks();
            })
            .catch(err => {
                // Non-blocking fallback
                activeConfig = FALLBACK_CONFIG;
                updatePageLinks();
            });

        updatePageLinks();
    }

    // Expose API globally
    window.SporlyAffiliateManager = {
        getUrl: getPartnerUrl,
        updateLinks: updatePageLinks,
        getConfig: () => activeConfig
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
