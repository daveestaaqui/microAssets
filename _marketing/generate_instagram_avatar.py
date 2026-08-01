import os
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
AVATAR_PNG = os.path.join(BASE_DIR, "assets", "instagram_avatar.png")
AVATAR_JPG = os.path.join(BASE_DIR, "assets", "instagram_avatar.jpg")

def generate_avatar():
    bg_color = (252, 250, 246, 255) # Warm cream #FCFAF6 matching website
    canvas_size = (1080, 1080)
    
    if os.path.exists(LOGO_PATH):
        try:
            img = Image.open(LOGO_PATH).convert("RGBA")
            import numpy as np
            arr = np.array(img)
            # Remove black background pixels
            black_pixels = (arr[:,:,0] < 35) & (arr[:,:,1] < 35) & (arr[:,:,2] < 35)
            arr[black_pixels, 3] = 0
            cleaned_logo = Image.fromarray(arr)
            
            canvas = Image.new("RGBA", canvas_size, bg_color)
            logo_scaled = cleaned_logo.resize((780, 780), Image.Resampling.LANCZOS)
            offset = ((canvas_size[0] - 780) // 2, (canvas_size[1] - 780) // 2)
            canvas.paste(logo_scaled, offset, logo_scaled)
            
            final_avatar = canvas.convert("RGB")
            final_avatar.save(AVATAR_PNG, "PNG")
            final_avatar.save(AVATAR_JPG, "JPEG", quality=100)
            print("✅ Successfully generated Instagram avatar (zero black background!).")
            return
        except Exception as e:
            print(f"Error generating avatar: {e}")
            
    # Fallback solid
    canvas = Image.new("RGB", canvas_size, "#FCFAF6")
    canvas.save(AVATAR_JPG, "JPEG", quality=95)

if __name__ == "__main__":
    generate_avatar()
