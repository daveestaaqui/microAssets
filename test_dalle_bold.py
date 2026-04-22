import os
import requests
import io
from PIL import Image, ImageFilter
from openai import OpenAI

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_KEY)

def test_prompt(app_name):
    # Ask for bold, chunky, scalable shapes
    prompt = f"An ultra-premium, ultra-minimalist, flat abstract SaaS app icon representing '{app_name}'. STRICTLY NO LETTERS, NO ALPHABET CHARACTERS, NO WORDS. ZERO TEXT. Avoid all generic clip-art. The design must be a purely abstract, bold, chunky geometric mark. Use ONLY thick lines and large solid shapes. No thin lines, no intricate details. Must be highly legible at tiny 16x16 scale. Include subtle spore-dot accents. Center the logo perfectly on a luxurious cream-colored background (#F8F5EE). Award-winning structural minimalism."
    
    print(f"Testing for {app_name}...")
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard", # standard is better for flat/bold, hd adds too much detail
        n=1,
        response_format="url"
    )
    
    image_url = response.data[0].url
    img_data = requests.get(image_url).content
    img = Image.open(io.BytesIO(img_data))
    
    base_name = f"test_bold_{app_name.replace(' ', '_')}"
    img.save(f"{base_name}_1024.png")
    
    for size in [128, 48, 16]:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        # Apply slight sharpening to prevent blurring for small icons
        if size <= 48:
            resized = resized.filter(ImageFilter.SHARPEN)
        resized.save(f"{base_name}_{size}.png")
        print(f"Saved {base_name}_{size}.png")

test_prompt("diff checker")
