import os
import requests

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = "daveestaaqui/micro-assets-landing-page"
TAG = "v1.0.0"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# 1. Get the release ID
release_response = requests.get(f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}", headers=headers)
if release_response.status_code != 200:
    print(f"Failed to fetch release: {release_response.json()}")
    exit(1)

release_id = release_response.json()["id"]

# 2. Get existing assets and delete those with the same name (clobber)
assets_response = requests.get(f"https://api.github.com/repos/{REPO}/releases/{release_id}/assets", headers=headers)
existing_assets = {asset['name']: asset['id'] for asset in assets_response.json()} if assets_response.status_code == 200 else {}

files_to_upload = [
    "/Users/davidmahler/Desktop/microAssets/_landing_page/OmniSuite_Complete.zip",
    "/Users/davidmahler/Desktop/microAssets/_landing_page/Firefox_Extensions.zip",
    "/Users/davidmahler/Desktop/microAssets/_landing_page/SporlyWorks_Android_Apps.zip"
]

for file_path in files_to_upload:
    file_name = os.path.basename(file_path)
    
    # Delete existing asset before upload if clobbering
    if file_name in existing_assets:
        print(f"Deleting previously uploaded {file_name}...")
        requests.delete(f"https://api.github.com/repos/{REPO}/releases/assets/{existing_assets[file_name]}", headers=headers)

    print(f"Uploading {file_name}...")
    with open(file_path, "rb") as f:
        # Use uploads.github.com
        upload_url = f"https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets?name={file_name}"
        res = requests.post(
            upload_url,
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Content-Type": "application/zip",
                "Accept": "application/vnd.github.v3+json"
            },
            data=f
        )
        if res.status_code == 201:
            print(f"✅ Successfully uploaded {file_name}!")
        else:
            print(f"❌ Failed to upload {file_name}: {res.text}")

print("All uploads complete.")
