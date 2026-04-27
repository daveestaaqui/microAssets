import os
import json
import concurrent.futures
from openai import OpenAI
import requests
from PIL import Image, ImageFilter
from io import BytesIO

# Configuration
BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
ANDROID_BASE = os.path.join(BASE_DIR, "_b2b_android")
MAX_WORKERS = 10

client = OpenAI()


def _get_sharpened_icon(img, size):
    """Resize with Lanczos then sharpen for micro-scale crispness."""
    resized = img.resize(size, resample=Image.Resampling.LANCZOS)
    sharpened = resized.filter(ImageFilter.UnsharpMask(radius=1.5, percent=150, threshold=3))
    return sharpened


def _build_prompt(name, description):
    """Build the v5 spore-flare family prompt."""
    # Distill the concept to its simplest form
    concept = description if description else name
    return (
        f"A perfectly flat vector brand logo mark on a solid cream (#F8F5EE) background. "
        f"The mark represents '{concept}'. "
        f"Design rules: Use ONLY solid flat fills in charcoal (#2D2D2D). "
        f"The entire logo consists of ONE simple geometric shape — a circle, square, triangle, or simple combination — "
        f"that abstractly suggests the concept. Accompanied by exactly 3 small round dots placed asymmetrically nearby, "
        f"representing 'spores' — the brand's family signature across all products. "
        f"The logo must be perfectly clean with ZERO texture, ZERO stippling, ZERO noise, ZERO grain, ZERO shading, "
        f"ZERO gradients, ZERO 3D effects, ZERO realistic rendering. "
        f"Think: a logo printed in one ink color on a business card. Completely flat. "
        f"NO text, NO letters, NO typography. Maximum simplicity. "
        f"The mark is small and centered with enormous empty space around it."
    )


def process_extension(ext_dir):
    try:
        manifest_path = os.path.join(ext_dir, 'manifest.json')
        if not os.path.isfile(manifest_path):
            return

        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        name = manifest.get('name', os.path.basename(ext_dir))
        description = manifest.get('description', '')

        prompt = _build_prompt(name, description)

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt[:4000],
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        img_response = requests.get(image_url)
        img_response.raise_for_status()

        img = Image.open(BytesIO(img_response.content)).convert("RGBA")

        # Master spore icon (1024x1024)
        img.save(os.path.join(ext_dir, "icon_spore.png"))

        # 128x128 — clean Lanczos, no sharpening needed at this size
        icon128 = img.resize((128, 128), resample=Image.Resampling.LANCZOS)
        icon128.save(os.path.join(ext_dir, "icon128.png"))

        # 48x48 — sharpened for toolbar clarity
        icon48 = _get_sharpened_icon(img, (48, 48))
        icon48.save(os.path.join(ext_dir, "icon48.png"))

        # 16x16 — aggressively sharpened for micro-scale
        icon16 = _get_sharpened_icon(img, (16, 16))
        icon16.save(os.path.join(ext_dir, "icon16.png"))

        # Android Capacitor: override ic_launcher assets
        android_ext_path = os.path.join(ANDROID_BASE, os.path.basename(ext_dir))
        if os.path.isdir(android_ext_path):
            ic_launcher_192 = _get_sharpened_icon(img, (192, 192))
            res_base = os.path.join(android_ext_path, 'android', 'app', 'src', 'main', 'res')
            if os.path.isdir(res_base):
                for root, dirs, files in os.walk(res_base):
                    if os.path.basename(root).startswith("mipmap-"):
                        for target in ["ic_launcher.png", "ic_launcher_round.png", "ic_launcher_foreground.png"]:
                            if target in files:
                                ic_launcher_192.save(os.path.join(root, target))

        print(f"✅ Processed: {name}")

    except Exception as e:
        print(f"❌ Failed to process {os.path.basename(ext_dir)}: {str(e)}")


def main():
    extensions = []
    for entry in os.listdir(BASE_DIR):
        full_path = os.path.join(BASE_DIR, entry)
        if os.path.isdir(full_path) and not entry.startswith(('.', '_')):
            if os.path.isfile(os.path.join(full_path, 'manifest.json')):
                extensions.append(full_path)

    print(f"Found {len(extensions)} extensions to process...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_extension, extensions)

    print("\\n✅ All extensions processed.")


if __name__ == "__main__":
    main()
