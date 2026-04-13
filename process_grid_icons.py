import os
import cv2
import numpy as np

def slice_grid(image_path, output_dir, basenames, grid_dims=(2, 2)):
    # Simple script to slice the generated grids accurately
    print(f"Slicing {image_path} into {grid_dims[0]}x{grid_dims[1]} grid...")
    img = cv2.imread(image_path)
    if img is None:
        return
        
    h, w, _ = img.shape
    cell_h = h // grid_dims[0]
    cell_w = w // grid_dims[1]
    
    idx = 0
    for r in range(grid_dims[0]):
        for c in range(grid_dims[1]):
            if idx >= len(basenames):
                break
                
            y1 = r * cell_h
            y2 = (r + 1) * cell_h
            x1 = c * cell_w
            x2 = (c + 1) * cell_w
            
            crop = img[y1:y2, x1:x2]
            
            # Save different sizes
            sizes = [128, 48, 16]
            ext_dir = os.path.join(output_dir, basenames[idx])
            from pathlib import Path
            Path(ext_dir).mkdir(parents=True, exist_ok=True)
            
            for s in sizes:
                resized = cv2.resize(crop, (s, s), interpolation=cv2.INTER_AREA)
                out_path = os.path.join(ext_dir, f"icon{s}.png")
                cv2.imwrite(out_path, resized)
                
            idx += 1
