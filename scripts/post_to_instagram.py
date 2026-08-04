import os
import sys
import glob
import requests

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")

if not ACCESS_TOKEN or not ACCOUNT_ID:
    print("⚠️ Notice: INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_ACCOUNT_ID environment variable missing.")
    print("To enable hands-free Meta Graph API posting, add these secrets to your GitHub repository.")
    sys.exit(0)

# Scan for published state
STATE_FILE = "_marketing/instagram_state.json"
DRAFTS_DIR = "_marketing/instagram_drafts"

# Find draft files
drafts = []
if os.path.exists(DRAFTS_DIR):
    for file in sorted(os.listdir(DRAFTS_DIR)):
        if file.endswith(".jpg"):
            base = os.path.splitext(file)[0]
            cap_file = os.path.join(DRAFTS_DIR, f"{base}.txt")
            if os.path.exists(cap_file):
                drafts.append({
                    "id": base,
                    "image_file": file,
                    "caption_file": cap_file
                })

if not drafts:
    print("✅ No posts found in queue.")
    sys.exit(0)

next_post = drafts[0]
print(f"📋 Preparing next post for Meta Graph API: {next_post['id']}")

with open(next_post["caption_file"], "r", encoding="utf-8") as f:
    caption = f.read()

# Publicly accessible HTTPS image URL hosted on GitHub Pages
IMAGE_URL = f"https://sporlyworks.com/_marketing/instagram_drafts/{next_post['image_file']}"
print(f"🌐 Image URL: {IMAGE_URL}")

# Step 1: Create Container
container_url = f"https://graph.facebook.com/v19.0/{ACCOUNT_ID}/media"
container_payload = {
    "image_url": IMAGE_URL,
    "caption": caption,
    "access_token": ACCESS_TOKEN
}

print("🚀 Creating Meta media container...")
response = requests.post(container_url, data=container_payload)
container_data = response.json()

if "id" not in container_data:
    print(f"❌ Failed to create media container: {container_data}")
    sys.exit(1)

creation_id = container_data["id"]
print(f"✅ Container created! Creation ID: {creation_id}")

# Step 2: Publish Container
publish_url = f"https://graph.facebook.com/v19.0/{ACCOUNT_ID}/media_publish"
publish_payload = {
    "creation_id": creation_id,
    "access_token": ACCESS_TOKEN
}

print("🚀 Publishing container to Instagram...")
publish_response = requests.post(publish_url, data=publish_payload)
publish_data = publish_response.json()

if "id" in publish_data:
    print(f"🎉 Successfully published post to Instagram! Media ID: {publish_data['id']}")
else:
    print(f"❌ Failed to publish post: {publish_data}")
    sys.exit(1)
