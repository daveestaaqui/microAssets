import os
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
AVATAR_PNG = os.path.join(BASE_DIR, "assets", "instagram_avatar.png")
AVATAR_JPG = os.path.join(BASE_DIR, "assets", "instagram_avatar.jpg")

def generate_avatar():
    # Warm cream background matching the website
    bg_color = "#FCFAF6"
    size = (500, 500)
    img = Image.new("RGB", size, bg_color)
    
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            # Resize logo to fit nicely (e.g., 380x380)
            logo = logo.resize((380, 380), Image.Resampling.LANCZOS)
            # Center logo
            x = (size[0] - logo.size[0]) // 2
            y = (size[1] - logo.size[1]) // 2
            img.paste(logo, (x, y), logo)
            print("Logo pasted successfully.")
        except Exception as e:
            print(f"Error pasting logo: {e}")
            
    # Save as PNG
    img.save(AVATAR_PNG, "PNG")
    # Save as JPG (for Instagram standard upload format compatibility)
    img.save(AVATAR_JPG, "JPEG", quality=95)
    print(f"Saved Instagram avatars:\n- {AVATAR_PNG}\n- {AVATAR_JPG}")

if __name__ == "__main__":
    generate_avatar()
