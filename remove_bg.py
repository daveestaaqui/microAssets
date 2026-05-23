import sys
from PIL import Image

def remove_white_bg(input_path, output_path, tolerance=240):
    img = Image.open(input_path).convert("RGBA")
    data = img.getdata()
    
    new_data = []
    for item in data:
        if item[0] > tolerance and item[1] > tolerance and item[2] > tolerance:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    img.save(output_path, "PNG")

if len(sys.argv) == 3:
    remove_white_bg(sys.argv[1], sys.argv[2], tolerance=235)
    print(f"Background removed and saved to {sys.argv[2]}")
