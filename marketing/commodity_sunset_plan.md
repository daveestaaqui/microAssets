# Commodity Extension Sunset Plan
## SporlyWorks Portfolio Optimization — CEO Authorized

> **Status:** Approved by CEO Lena Voss (Cycle 35 directive: "Immediate Sunset")
> **Owner:** Antigravity Engineering
> **Impact:** Portfolio 87→68 Chrome, 174→136 total (Chrome + Firefox)

---

## Extensions Scheduled for Sunset (19)

| # | Extension | Reason | Browser Alternative |
|---|---|---|---|
| 1 | amazon-wide-mode | Commodity, zero differentiation | Browser zoom, Amazon native |
| 2 | base64-encoder | Commodity utility | DevTools console |
| 3 | bookmark-manager | Commodity utility | Chrome native bookmarks |
| 4 | carbon-footprint-checker | Novelty widget | None required |
| 5 | clipboard-history | Commodity utility | macOS/Windows native |
| 6 | dark-mode-everywhere | Commodity, saturated market | Chrome native dark mode |
| 7 | google-dark-search | Commodity, single-site | Google's own dark mode |
| 8 | hash-generator | Commodity utility | DevTools console, CLI |
| 9 | lorem-ipsum-generator | Commodity utility | Any lorem ipsum website |
| 10 | password-generator | Commodity utility | Chrome built-in generator |
| 11 | qr-code-generator | Commodity utility | Chrome native QR, iOS/Android |
| 12 | reading-mode | Commodity utility | Chrome native reader mode |
| 13 | reading-time-badge | Low-value novelty | Medium, any blog platform |
| 14 | screenshot-capture | Commodity utility | Chrome built-in screenshot |
| 15 | text-case-converter | Commodity utility | Any text editor |
| 16 | timestamp-converter | Commodity utility | DevTools console |
| 17 | url-encoder-decoder | Commodity utility | DevTools console |
| 18 | url-shortener | Commodity, API-dependent | bit.ly, tinyurl free |
| 19 | word-counter | Commodity utility | Any text editor, Google Docs |

---

## Phased Timeline

### Phase 1: Freeze (Immediate)
- **Action:** Stop all development, QA, and CWS submissions for these 19 extensions
- **Impact:** ~190 QA checks/cycle eliminated immediately
- **Risk:** Zero — these extensions are not generating revenue

### Phase 2: Unpublish from CWS (Week 1)
- **Action:** Unpublish all 19 Chrome extensions + 19 Firefox variants from stores
- **Note:** Existing users retain installed copies but no updates

### Phase 3: Archive (Week 2)
- **Action:** Move extension directories to `_archived/` in the repo
- **Impact:** Clean working directory, reduced `git status` noise

### Phase 4: Cleanup (Week 3)
- **Action:** Remove from CWS submission queue, portfolio dashboards, and marketing materials
- **Action:** Update QA daemon exclude list

---

## What We Keep

The remaining **68 Chrome extensions** include:
- **14 Flagship** (Pro Suite revenue core)
- **1 Keep** (site-speed-analyzer, strong standalone)
- **53 Review tier** (consolidation candidates for future cycles)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| User complaints on sunset | Low | Low | These are utility tools with free alternatives everywhere |
| SEO/backlink loss | Negligible | Negligible | No significant organic traffic to commodity tools |
| Revenue impact | Zero | Zero | None of these are monetized or monetizable |
| Developer time savings | Certain | High | ~190 fewer QA checks, smaller blast radius |
