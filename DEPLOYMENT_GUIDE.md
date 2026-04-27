# SporlyWorks Deployment Guide

## Overview

This guide walks you through deploying `sporlyworks.com` using **GitHub Pages** (hosting) + **Cloudflare** (CDN/Security) for enterprise-grade performance at zero cost.

---

## Prerequisites

- GitHub account with the `microAssets` repository: `https://github.com/daveestaaqui/microAssets`
- Cloudflare account with `sporlyworks.com` domain
- Domain registered and pointed to Cloudflare

---

## Step 1: Configure GitHub Pages

### 1.1 Navigate to GitHub Settings

1. Go to: `https://github.com/daveestaaqui/microAssets`
2. Click **Settings** (gear icon) at the top
3. Click **Pages** in the left sidebar

### 1.2 Configure Branch Source

1. Under **"Build and deployment"** → **Source** dropdown
2. Select **Deploy from a branch**
3. Set:
   - **Branch:** `main`
   - **Folder:** `/ (root)`
4. Click **Save**

### 1.3 Add Custom Domain

1. Scroll to **Custom domain** field
2. Enter: `sporlyworks.com`
3. Click **Save**
4. GitHub will perform a DNS check

> ⚠️ If GitHub shows "DNS check unsuccessful," that's expected — we'll fix this in Step 2.

---

## Step 2: Configure Cloudflare DNS

### 2.1 Access Cloudflare Dashboard

1. Log into `https://dash.cloudflare.com/`
2. Select your account → `sporlyworks.com`
3. Go to **DNS** → **Records**

### 2.2 Clean Up Old Records

**Delete any existing web traffic records:**

| Type | Name | Action |
|------|------|--------|
| A    | @    | Delete (keep MX/email records) |
| A    | www  | Delete (keep MX/email records) |
| CNAME| @    | Delete (keep MX/email records) |
| CNAME| www  | Delete (keep MX/email records) |

> ✅ **Keep** any existing MX records (email) or TXT records (verification) — only remove web traffic records.

### 2.3 Add GitHub Pages CNAME Records

**Record 1 - Root Domain:**
| Type | Name | Target | Proxy Status |
|------|------|--------|--------------|
| CNAME| @    | `daveestaaqui.github.io` | ✅ Proxied (Orange Cloud ON) |

**Record 2 - WWW Subdomain:**
| Type | Name | Target | Proxy Status |
|------|------|--------|--------------|
| CNAME| www  | `daveestaaqui.github.io` | ✅ Proxied (Orange Cloud ON) |

> ℹ️ Cloudflare uses **CNAME flattening** for root domains, so this works seamlessly.

### 2.4 Configure SSL/TLS (CRITICAL)

1. Go to **SSL/TLS** in left sidebar
2. Under **Encryption mode**, select: **Full** (NOT "Full Strict")
   - **Full** allows Cloudflare and GitHub to both handle HTTPS independently
   - **Full Strict** would break the connection (both try to force HTTPS)
3. Click **Save**

---

## Step 3: Wait for Propagation

- DNS changes typically take **5-10 minutes** to propagate fully
- You can test propagation at: `https://www.nslookup.io/`
- Cloudflare dashboard will show "Propagated" status under DNS records

---

## Step 4: Verify Deployment

### Check GitHub Pages Build Status

1. Return to **Pages** → **Settings**
2. Your site URL should display: `https://daveestaaqui.github.io/microAssets/`

### Test Your Site

Visit these URLs (they should redirect via Cloudflare):

- `https://sporlyworks.com`
- `https://www.sporlyworks.com`

✅ If you see the site with the navigation bar and tool cards — **you're live!**

---

## Step 5: Test Affiliate Links

Once live, verify all affiliate links work:

| Tool | Affiliate Link | Expected Behavior |
|------|----------------|-------------------|
| Stack Auditor | Buildium (25% recurring) | Should redirect to Buildium |
| Stack Auditor | HubSpot (30% recurring) | Should redirect to HubSpot |
| AI Estimator | DigitalOcean | Should open referral signup |
| AI Estimator | Claude API | Should open Anthropic console |
| AI Estimator | GitHub Copilot | Should open Copilot page |

---

## Troubleshooting

### Issue: "ERR_TOO_MANY_REDIRECTS"

**Cause:** SSL/TLS mode is set to "Full Strict" when it should be "Full"

**Fix:**
1. Cloudflare dashboard → **SSL/TLS**
2. Change mode to **Full** (not Full Strict, not Flexible)
3. Save and wait 5 minutes

### Issue: Cloudflare orange cloud is grayed out on @ record

**Cause:** CNAME flattening limitation

**Fix:** This is normal for root domains. Cloudflare handles it automatically. The record is valid.

### Issue: Site shows GitHub Pages URL instead of custom domain

**Cause:** DNS hasn't propagated yet

**Fix:** Wait 10-15 minutes, then try again. Check propagation at `nslookup.io`

---

## What Happens Next

Once live at `sporlyworks.com`:

1. **Test all 4 tools** on mobile and desktop
2. **Verify affiliate tracking** is working (open in incognito mode)
3. **Open `marketing/social_posts.md`** to copy LinkedIn/email templates
4. **Start driving traffic** to your tools

---

## Site Structure

```
sporlyworks.com/
├── index.html          # Homepage with 4 tool cards
├── roi-calculator.html # ROI Calculator tool
├── stack-auditor.html  # Stack Auditor tool
├── ai-estimator.html   # AI Workload Estimator tool
└── style.css           # Shared stylesheet
```

---

## Metrics to Track

Once traffic starts flowing:

| Metric | Tool | Key Performance Indicator |
|--------|------|---------------------------|
| Referral Clicks | All tools | Affiliate link clicks |
| Conversion Rate | Stack Auditor | % who use Buildium |
| Engagement | AI Estimator | Time spent on calculator |
| Mobile Performance | All | SpeedIndex via PageSpeed Insights |

---

## Next Steps

1. ✅ Complete Steps 1-3 above
2. ⏳ Wait 5-10 minutes for propagation
3. 🧪 Test `sporlyworks.com` on your phone
4. 📝 Open `marketing/social_posts.md` to start promoting
5. 🚀 Launch LinkedIn/email campaigns

---

## Support

If you encounter issues:

1. Check GitHub Pages build logs: Settings → Pages → Build and deployment
2. Check Cloudflare DNS status: dash.cloudflare.com → DNS
3. Verify SSL: https://sporlyworks.com (should show HTTPS with padlock)

---

*Built with ❤️ by SporlyWorks*