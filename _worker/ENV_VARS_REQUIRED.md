# Worker Environment Variables — Complete List

All variables the SporlyWorks Railway worker needs across its 11 jobs.

## Core (Required for Worker to Start)

| Variable | Used By | Description |
|---|---|---|
| `CWS_CLIENT_ID` | CWS Monitor, Health Check | Chrome Web Store OAuth Client ID |
| `CWS_CLIENT_SECRET` | CWS Monitor, Health Check | Chrome Web Store OAuth Client Secret |
| `CWS_REFRESH_TOKEN` | CWS Monitor, Health Check | Chrome Web Store OAuth Refresh Token |
| `CWS_ITEM_IDS` | CWS Monitor, Health Check | JSON map of `{ "slug": "extension_id" }` |
| `DISCORD_WEBHOOK_URL` | All jobs (notifications) | Discord webhook for status alerts |
| `LICENSE_SERVER_URL` | Health Check | License server base URL |

## Publishing Jobs

| Variable | Used By | Description |
|---|---|---|
| `EDGE_CLIENT_ID` | Edge Publisher | Microsoft Edge Partner Center Client ID |
| `PLAY_SERVICE_ACCOUNT_JSON` | Play Publisher | Google Play service account JSON (base64 or raw) |
| `PLAY_PACKAGE_PREFIX` | Play Publisher | Android package prefix (default: `com.omnisuite`) |
| `GITHUB_TOKEN` | Website Sync, Factory | GitHub PAT for pushing landing page updates |
| `GITHUB_LANDING_REPO` | Website Sync | Repo for landing page (default: `daveestaaqui/micro-assets-landing-page`) |

## AI & Support Jobs

| Variable | Used By | Description |
|---|---|---|
| `GEMINI_API_KEY` | Support Agent, Review Scanner, Factory, Updater | Google Gemini/AI API key |
| `SUPPORT_EMAIL_USER` | Support Agent | Gmail address for support inbox |
| `SUPPORT_EMAIL_PASSWORD` | Support Agent | Gmail app password |
| `SUPPORT_ESCALATION_EMAIL` | Support Agent | Forwarding address for complex tickets |
| `STRIPE_SECRET_KEY` | System Monitor | Stripe API key for revenue tracking |

## Optional

| Variable | Used By | Description |
|---|---|---|
| `CWS_CANARY_SLUG` | Health Check | Extension to use as canary (default: `ai-content-bouncer`) |
| `OMNISUITE_DIR` | Factory, Updater | Workspace path (default: `~/Desktop/omniSuite`) |
| `DISABLE_AUTONOMOUS_FACTORY` | Factory | Set to `true` to disable auto-generation |
| `IMAP_SERVER` | Support Agent | Default: `imap.gmail.com` |
| `SMTP_SERVER` | Support Agent | Default: `smtp.gmail.com` |

## License Server (Separate Service)

| Variable | Used By | Description |
|---|---|---|
| `STRIPE_WEBHOOK_SECRET` | License Server | Stripe webhook signing secret |
| `PORT` | License Server | Port number (Railway auto-sets this) |
