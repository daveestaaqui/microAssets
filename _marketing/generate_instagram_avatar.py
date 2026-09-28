import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo-nav.png")
PARCHMENT_PATH = os.path.join(BASE_DIR, "assets", "parchment-seamless.jpg")

AVATAR_PNG = os.path.join(BASE_DIR, "assets", "instagram_avatar.png")
AVATAR_JPG = os.path.join(BASE_DIR, "assets", "instagram_avatar.jpg")
AVATAR_ROOT_JPG = os.path.join(BASE_DIR, "instagram_avatar.jpg")
AVATAR_LOCKUP_JPG = os.path.join(BASE_DIR, "assets", "instagram_avatar_lockup.jpg")
PREVIEW_JPG = os.path.join(BASE_DIR, "assets", "instagram_avatar_circle_preview.jpg")
PREVIEW_LOCKUP_JPG = os.path.join(BASE_DIR, "assets", "instagram_avatar_lockup_preview.jpg")

def generate_avatar():
    canvas_size = (1080, 1080)
    
    # 1. Base Canvas from Home Page Parchment
    if os.path.exists(PARCHMENT_PATH):
        bg_tile = Image.open(PARCHMENT_PATH).convert("RGBA")
        canvas = bg_tile.resize(canvas_size, Image.Resampling.LANCZOS)
    else:
        # Fallback to homepage warm parchment color
        canvas = Image.new("RGBA", canvas_size, (245, 240, 232, 255)) # #F5F0E8

    # 2. Load and crop website logo tightly
    if not os.path.exists(LOGO_PATH):
        print(f"❌ Logo not found at {LOGO_PATH}")
        return

    logo_src = Image.open(LOGO_PATH).convert("RGBA")
    bbox = logo_src.getbbox()
    logo_tight = logo_src.crop(bbox)

    # 3. Primary Avatar: Pure Mushroom Emblem (Optimal for Instagram's Circle Crop)
    # Target height 680px gives 200px top/bottom margin, perfectly inside the 540px radius circle
    target_h = 680
    aspect = logo_tight.width / logo_tight.height
    target_w = int(target_h * aspect)
    logo_resized = logo_tight.resize((target_w, target_h), Image.Resampling.LANCZOS)

    avatar_canvas = canvas.copy()
    offset_x = (canvas_size[0] - target_w) // 2
    offset_y = (canvas_size[1] - target_h) // 2
    avatar_canvas.paste(logo_resized, (offset_x, offset_y), logo_resized)

    # Save as 100% solid, opaque RGB (Zero transparency, Zero black pixels)
    final_rgb = avatar_canvas.convert("RGB")
    final_rgb.save(AVATAR_PNG, "PNG")
    final_rgb.save(AVATAR_JPG, "JPEG", quality=100)
    final_rgb.save(AVATAR_ROOT_JPG, "JPEG", quality=100)
    print("✅ Successfully generated authentic website logo avatar (assets/instagram_avatar.jpg).")

    # 4. Secondary Option: Lockup with SPORLYWORKS text
    lockup_canvas = canvas.copy()
    lockup_th = 560
    lockup_tw = int(lockup_th * aspect)
    lockup_mushrooms = logo_tight.resize((lockup_tw, lockup_th), Image.Resampling.LANCZOS)
    lockup_x = (canvas_size[0] - lockup_tw) // 2
    lockup_y = 170
    lockup_canvas.paste(lockup_mushrooms, (lockup_x, lockup_y), lockup_mushrooms)

    draw = ImageDraw.Draw(lockup_canvas)
    font_paths = [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    ]
    font = None
    for p in font_paths:
        if os.path.exists(p):
            try:
                font = ImageFont.truetype(p, 54)
                break
            except:
                pass
    if not font:
        font = ImageFont.load_default()

    wordmark = "SPORLYWORKS"
    t_box = draw.textbbox((0, 0), wordmark, font=font)
    tw = t_box[2] - t_box[0]
    draw.text(((canvas_size[0] - tw) // 2, 755), wordmark, fill="#143A27", font=font)
    
    lockup_rgb = lockup_canvas.convert("RGB")
    lockup_rgb.save(AVATAR_LOCKUP_JPG, "JPEG", quality=100)
    print("✅ Successfully generated logo lockup avatar (assets/instagram_avatar_lockup.jpg).")

    # 5. Generate Circular Previews for visual verification
    circle_mask = Image.new("L", canvas_size, 0)
    draw_mask = ImageDraw.Draw(circle_mask)
    draw_mask.ellipse((0, 0, canvas_size[0], canvas_size[1]), fill=255)

    # Emblem Preview
    app_bg = Image.new("RGB", canvas_size, "#181818")
    app_bg.paste(final_rgb, (0, 0), circle_mask)
    draw_app = ImageDraw.Draw(app_bg)
    draw_app.ellipse((0, 0, canvas_size[0] - 1, canvas_size[1] - 1), outline="#333333", width=2)
    app_bg.save(PREVIEW_JPG, "JPEG", quality=95)

    # Lockup Preview
    app_bg_lockup = Image.new("RGB", canvas_size, "#181818")
    app_bg_lockup.paste(lockup_rgb, (0, 0), circle_mask)
    draw_app_lockup = ImageDraw.Draw(app_bg_lockup)
    draw_app_lockup.ellipse((0, 0, canvas_size[0] - 1, canvas_size[1] - 1), outline="#333333", width=2)
    app_bg_lockup.save(PREVIEW_LOCKUP_JPG, "JPEG", quality=95)
    print("✅ Generated circular crop preview simulations.")

if __name__ == "__main__":
    generate_avatar()
