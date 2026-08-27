# 📸 2-Minute Instagram Meta Graph API Token Setup Guide

This guide gives you the exact 3 steps to retrieve your `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_ACCOUNT_ID` so GitHub Actions can post daily graphics to your Instagram account automatically.

---

### Step 1: Open Meta Graph API Explorer (1 Click)

1. Open the [Meta Graph API Explorer](https://developers.facebook.com/tools/explorer/).
2. Select your Meta App from the **Meta App** dropdown (or create a quick App selecting "Business" / "Other").
3. In the **User or Page** dropdown, select **User Token**.
4. In the **Permissions** section, add the following 4 permissions:
   * `instagram_basic`
   * `instagram_content_publish`
   * `pages_show_list`
   * `pages_read_engagement`
5. Click **Generate Access Token** and approve the prompt.
6. Copy the generated short-lived token string.

---

### Step 2: Grab Your App Secret & Run the Generator

1. Go to [developers.facebook.com/apps](https://developers.facebook.com/apps/) -> Select your App -> **App Settings** -> **Basic**.
2. Click **Show** next to **App Secret** and copy it.
3. In your local terminal, run the helper script:
   ```bash
   python3 scripts/generate_long_lived_ig_token.py
   ```
   *Enter your App ID, App Secret, and Short-Lived Token when prompted.*
4. The script will automatically:
   * Convert your token into a **60-day Long-Lived Token**
   * Fetch your exact **Instagram Business Account ID**

---

### Step 3: Add to GitHub Secrets (Done!)

1. Go to your repository on GitHub: `github.com/daveestaaqui/microAssets/settings/secrets/actions`
2. Click **New repository secret** and add:
   * `INSTAGRAM_ACCESS_TOKEN` -> *(Paste the 60-day token)*
   * `INSTAGRAM_ACCOUNT_ID` -> *(Paste your Instagram Account ID)*

🚀 Once saved, `.github/workflows/instagram_daily_post.yml` and `social_marketing_promotions.yml` will automatically post scheduled scientific visual infographics to your Instagram feed every single morning!
