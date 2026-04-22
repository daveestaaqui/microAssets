import os
import requests
import io
from PIL import Image
from openai import OpenAI

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_KEY)

def test_prompt(app_name):
    prompt = f"An ultra-premium, highly conceptual, abstract geometric SaaS app icon. STRICTLY NO LETTERS, NO ALPHABET CHARACTERS, NO WORDS, AND NO TYPOGRAPHY ALLOWED. ZERO TEXT. Avoid all generic or clip-art styles. The design must be a bespoke, intricate monoline line-art composition centered around a unique, futuristic, and purely abstract geometric representation of the concept of '{app_name}'. Include elegant, subtle geometric spore-dot motifs integrated flawlessly into the sharp, rigid, continuous lines. Center the logo perfectly on a luxurious cream-colored background (#F8F5EE). Award-winning, timeless, minimalist visual identity, purely abstract architectural logic."
    
    print(f"Testing for {app_name}...")
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="hd",
        n=1,
        response_format="url"
    )
    
    image_url = response.data[0].url
    img_data = requests.get(image_url).content
    img = Image.open(io.BytesIO(img_data))
    
    img.save(f"test_{app_name.replace(' ', '_')}.png")
    print(f"Saved test_{app_name.replace(' ', '_')}.png")

test_prompt("HTML Table to CSV Extractor")
test_prompt("Base64 Encoder")
