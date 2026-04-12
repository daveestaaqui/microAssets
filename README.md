<p align="center">
  <img src="https://img.shields.io/badge/Extensions-87%20Chrome%20%2B%2085%20Firefox-blue?style=for-the-badge&logo=googlechrome" alt="Extension Count" />
  <img src="https://img.shields.io/badge/QA%20Gate-Automated-brightgreen?style=for-the-badge&logo=githubactions" alt="QA Gate" />
  <img src="https://img.shields.io/badge/AI%20Review-GPT--4o-purple?style=for-the-badge&logo=openai" alt="AI Review" />
  <img src="https://img.shields.io/badge/License-Proprietary-orange?style=for-the-badge" alt="License" />
</p>

# 🧩 SporlyWorks — microAssets

> **172 browser extensions** across Chrome and Firefox, powered by an autonomous AI-driven QA pipeline.

SporlyWorks is a portfolio of productivity, developer, and utility browser extensions distributed through the Chrome Web Store and Firefox Add-ons. Every extension is automatically tested, reviewed, and version-bumped via a fully autonomous CI/CD pipeline.

---

## 📊 Portfolio at a Glance

| Platform | Extensions | Testing |
|---|---|---|
| 🌐 Chrome (MV3) | 87 | ✅ Static + Browser rendering |
| 🦊 Firefox (MV2/3) | 85 | ✅ Static analysis |
| **Total** | **172** | **700+ automated tests** |

---

## 🤖 Automated QA Pipeline

Every pull request triggers a **6-job CI/CD pipeline** that blocks merges on failure:

```
┌─────────────────┐
│  🔍 Lint         │ ← Manifest JSON validation (15s)
│    Manifests     │
└───────┬─────────┘
        │
   ┌────┴────┬──────────────────┐
   │         │                  │
   ▼         ▼                  ▼
┌──────┐  ┌────────┐  ┌──────────────────┐
│ 🛡️   │  │ 🦊     │  │ 🌐 Browser Tests │
│Chrome│  │Firefox │  │   (4 shards)     │
│Static│  │Analysis│  │ Popup Rendering  │
└──┬───┘  └───┬────┘  └──────┬───────────┘
   │          │               │
   └──────────┴───────────────┘
              │
              ▼
        ┌──────────┐
        │ ✅ QA     │ ← Blocks merge on failure
        │ Summary   │
        │ + Badge   │
        └──────────┘
```

### What Gets Tested

| Test Category | Scope | Details |
|---|---|---|
| **Manifest Lint** | All 172 | JSON validity, MV3 compliance, required fields, description length |
| **Icon Validation** | All 172 | Icon path declarations, size completeness |
| **Security Scan** | All 172 | `eval()`, hardcoded keys, `document.write()`, suspicious tokens |
| **File Existence** | All 172 | Popup HTML, content scripts, service workers |
| **Firefox Consistency** | 85 | Version match with Chrome counterpart, `browser.*` API usage |
| **Popup Rendering** | 87 Chrome | Real Chromium loads each extension, checks for JS errors |

### AI Code Reviews

Every PR is automatically reviewed by **Qodo PR-Agent** powered by **GPT-4o**:

- 📋 **PR Summary** — auto-generated description and type labels
- 🔍 **Inline Review** — security, permissions, and MV3 compliance checks
- 💡 **Code Suggestions** — up to 6 actionable improvements per PR
- 🏷️ **Effort Estimate** — review effort scoring (1-5)

---

## 🔢 Auto Version Bump

When a PR merges to `main`, any modified extensions automatically get their **patch version incremented** — preventing Chrome Web Store upload collisions.

```
merge to main → detect changed dirs → bump 1.2.3 → 1.2.4 → commit
```

---

## 🚀 CWS Publish

One-click publishing via GitHub Actions:

```
Actions → 🚀 CWS Publish → Run workflow
  ├── Mode: all | changed-only | single
  ├── Extension: (for single mode)
  └── Dry run: true/false
```

Builds zip packages, uploads via CWS API, and publishes for review — all from CI.

---

## 🛠️ Local Development

```bash
# Install dependencies
npm install

# Run all static tests
npx playwright test --grep "Static Analysis"

# Run Chrome browser tests (renders popups in real Chromium)
npx playwright test --grep "Browser"

# Run Firefox tests
npx playwright test tests/firefox.shared.spec.js

# Run manifest linter standalone
node tests/helpers/manifest-lint.js

# Bump versions (dry run)
node _scripts/version-bump.js --dry-run

# Bump a specific extension
node _scripts/version-bump.js --extension json-formatter
```

---

## 📁 Repository Structure

```
microAssets/
├── json-formatter/          # Chrome extension (87 total)
│   ├── manifest.json
│   ├── popup/
│   └── ...
├── json-formatter-firefox/  # Firefox variant (85 total)
│   ├── manifest.json
│   └── ...
├── tests/
│   ├── extension.shared.spec.js    # Chrome test suite
│   ├── firefox.shared.spec.js      # Firefox test suite
│   └── helpers/
│       ├── extension-loader.js     # Extension discovery + Chromium launcher
│       └── manifest-lint.js        # Standalone manifest validator
├── _scripts/
│   ├── version-bump.js             # Auto version incrementer
│   ├── cws_ci_publish.py           # CI-safe CWS publisher
│   └── cws_master_publish.py       # Local CWS publisher
├── .github/
│   ├── workflows/
│   │   ├── test_extensions.yml     # QA Gate pipeline
│   │   ├── pr_agent.yml            # AI code review
│   │   ├── version_bump.yml        # Auto version bump on merge
│   │   └── cws_publish.yml         # One-click CWS publish
│   └── badges/                     # Auto-generated CI badges
├── playwright.config.js
├── .pr_agent.toml                  # AI reviewer settings
└── package.json
```

---

<p align="center">
  <strong>Built by <a href="https://sporlyworks.com">SporlyWorks</a></strong><br/>
  <em>Autonomous AI-governed browser extension portfolio</em>
</p>
