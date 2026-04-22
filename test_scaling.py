import io
from PIL import Image, ImageEnhance, ImageFilter

def test_crop_scaling(input_file, output_prefix):
    img = Image.open(input_file).convert("RGBA")
    w, h = img.size
    
    # Normal resizing (for 128px) - High fidelity
    normal_128 = img.resize((128, 128), Image.Resampling.LANCZOS)
    normal_128.save(f"{output_prefix}_128_normal.png")
    
    # Crop the center 60% of the image to remove padding and focus on the core geometry
    crop_size = int(w * 0.6)
    left = (w - crop_size) // 2
    top = (h - crop_size) // 2
    right = left + crop_size
    bottom = top + crop_size
    cropped = img.crop((left, top, right, bottom))
    
    # 48px: Crop center, scale, Slight Contrast boost
    img_48 = cropped.resize((48, 48), Image.Resampling.LANCZOS)
    enhancer = ImageEnhance.Contrast(img_48)
    img_48 = enhancer.enhance(1.5)
    img_48.save(f"{output_prefix}_48_cropped.png")
    
    # 16px: Extreme crop (center 40%), Nearest Neighbor downscale (zero blur pixelation)
    extreme_crop_size = int(w * 0.4)
    el = (w - extreme_crop_size) // 2
    et = (h - extreme_crop_size) // 2
    extreme_cropped = img.crop((el, et, el + extreme_crop_size, et + extreme_crop_size))
    
    img_16_nearest = extreme_cropped.resize((16, 16), Image.Resampling.NEAREST)
    img_16_nearest.save(f"{output_prefix}_16_nearest.png")
    
    img_16_lanczos = extreme_cropped.resize((16, 16), Image.Resampling.LANCZOS)
    enhancer_16 = ImageEnhance.Contrast(img_16_lanczos)
    img_16_lanczos = enhancer_16.enhance(2.0)
    img_16_lanczos.save(f"{output_prefix}_16_lanczos.png")
    
    print("Testing scales generated.")

if __name__ == "__main__":
    test_crop_scaling("test_bold_diff_checker_1024.png", "test_scaling_diff")
