import os
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo-nav.png")
AVATAR_PNG = os.path.join(BASE_DIR, "assets", "instagram_avatar.png")
AVATAR_JPG = os.path.join(BASE_DIR, "assets", "instagram_avatar.jpg")

def generate_avatar():
    canvas_size = (1080, 1080)
    
    # Load exact website navigation logo
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            
            # Load website parchment texture background
            parchment_path = os.path.join(BASE_DIR, "assets", "parchment-tile.jpg")
            if not os.path.exists(parchment_path):
                parchment_path = os.path.join(BASE_DIR, "assets", "parchment-seamless.jpg")
                
            if os.path.exists(parchment_path):
                tile = Image.open(parchment_path).convert("RGBA")
                canvas = Image.new("RGBA", canvas_size)
                for x in range(0, 1080, tile.width):
                    for y in range(0, 1080, tile.height):
                        canvas.paste(tile, (x, y))
            else:
                canvas = Image.new("RGBA", canvas_size, (252, 250, 246, 255)) # #FCFAF6
                
            w, h = logo.size
            aspect = w / h
            target_h = 760
            target_w = int(target_h * aspect)
            
            logo_resized = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
            offset_x = (canvas_size[0] - target_w) // 2
            offset_y = (canvas_size[1] - target_h) // 2
            
            # Composite natively using logo's clean alpha channel
            canvas.paste(logo_resized, (offset_x, offset_y), logo_resized)
            
            final_avatar = canvas.convert("RGB")
            final_avatar.save(AVATAR_PNG, "PNG")
            final_avatar.save(AVATAR_JPG, "JPEG", quality=100)
            print("✅ Successfully generated authentic website logo avatar.")
            return
        except Exception as e:
            print(f"Error generating avatar: {e}")
            
    # Fallback
    canvas = Image.new("RGB", canvas_size, "#FCFAF6")
    canvas.save(AVATAR_JPG, "JPEG", quality=95)

if __name__ == "__main__":
    generate_avatar()
