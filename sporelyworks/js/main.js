// SporelyWorks Main JavaScript
// Static affiliate content feed renderer — NO backend dependencies

document.addEventListener('DOMContentLoaded', function () {

  // ═══════════════════════════════════════════════════════════════════════════
  // APPROVED AFFILIATE PARTNER DATA
  // Commission rates are internal-only — NOT displayed to users.
  // All links use bracketed placeholders for manual insertion.
  // ═══════════════════════════════════════════════════════════════════════════
  const affiliatePartners = [
    {
      id: 'magic-bag',
      name: 'Magic Bag',
      category: 'Grow Kits',
      // commission: '10%' — internal only, not shown
      description: 'Premium mushroom grow kits for home cultivation of legal culinary species. Everything you need to grow gourmet mushrooms at home.',
      legalNotice: 'Grow kits contain legal culinary mushroom species only. Intended for lawful home cultivation.',
      link: '[INSERT_MAGIC_BAG_LINK]'
    },
    {
      id: 'myyco',
      name: 'MYYCO',
      category: 'Liquid Cultures',
      // commission: '10%' — internal only, not shown
      description: 'High-quality liquid cultures for advanced mycologists cultivating legal culinary and gourmet mushroom species.',
      legalNotice: 'Liquid cultures are for cultivation of legal culinary and gourmet mushroom species only.',
      link: '[INSERT_MYYCO_LINK]'
    },
    {
      id: 'avalon',
      name: 'Avalon Magic Plants',
      category: 'Spores & Kits',
      // commission: '10.5%' — internal only, not shown
      description: 'Microscopy-grade spore specimens and grow kits from a trusted international supplier.',
      legalNotice: 'Spore products are sold strictly for microscopy and taxonomy purposes only. NOT for planting, growing, or cultivation.',
      link: '[INSERT_AVALON_LINK]'
    },
    {
      id: 'om-mushrooms',
      name: 'Om Mushrooms',
      category: 'Functional Supplements',
      // commission: '8-10%' — internal only, not shown
      description: 'Certified organic functional mushroom supplements with verified third-party lab testing. Capsules, powders, and drink mixes.',
      legalNotice: 'These statements have not been evaluated by the FDA. Not intended to diagnose, treat, cure, or prevent any disease.',
      link: '[INSERT_OM_MUSHROOMS_LINK]'
    },
    {
      id: 'freshcap',
      name: 'FreshCap',
      category: 'Functional Supplements',
      // commission: '8-10%' — internal only, not shown
      description: 'Science-backed mushroom extract supplements made from 100% organic fruiting bodies with verified active compound profiles.',
      legalNotice: 'These statements have not been evaluated by the FDA. Not intended to diagnose, treat, cure, or prevent any disease.',
      link: '[INSERT_FRESHCAP_LINK]'
    }
  ];

  // ═══════════════════════════════════════════════════════════════════════════
  // RENDER PARTNER CARDS — No commission shown to users
  // ═══════════════════════════════════════════════════════════════════════════
  function renderContentFeed() {
    const feedContainer = document.getElementById('content-feed');
    if (!feedContainer) return;

    const html = affiliatePartners.map(partner => `
      <article class="product-card" data-partner-id="${partner.id}" data-category="${partner.category}">
        <div class="card-header">
          <span class="partner-category">${partner.category}</span>
          <h3>${partner.name}</h3>
        </div>
        <p class="card-description">${partner.description}</p>
        <p class="legal-notice">${partner.legalNotice}</p>
        <a href="${partner.link}" class="cta-button" target="_blank" rel="noopener noreferrer">
          Explore ${partner.name} <span class="arrow">→</span>
        </a>
      </article>
    `).join('');

    feedContainer.innerHTML = html;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SCROLL ANIMATIONS
  // ═══════════════════════════════════════════════════════════════════════════
  function initScrollAnimations() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: '0px 0px -30px 0px' }
    );

    document.querySelectorAll('.product-card').forEach((el, i) => {
      el.style.animationDelay = `${i * 0.08}s`;
      observer.observe(el);
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SMOOTH SCROLL + MOBILE NAV
  // ═══════════════════════════════════════════════════════════════════════════
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // Close mobile nav if open
        const nav = document.getElementById('main-nav');
        if (nav) nav.classList.remove('open');
      });
    });
  }

  function initMobileNav() {
    const toggle = document.getElementById('nav-toggle');
    const nav = document.getElementById('main-nav');
    if (toggle && nav) {
      toggle.addEventListener('click', () => {
        nav.classList.toggle('open');
        toggle.classList.toggle('active');
        toggle.setAttribute('aria-expanded', nav.classList.contains('open'));
      });
    }
  }

  // INIT
  renderContentFeed();
  initSmoothScroll();
  initMobileNav();
  requestAnimationFrame(() => initScrollAnimations());
});