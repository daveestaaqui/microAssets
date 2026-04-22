import os
import random

def generate_svg(name, bg_color="#F8F5EE", stroke_color="#1a1a1a", stroke_width=8):
    random.seed(name)
    svg = f'<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">\n'
    svg += f'  <rect width="512" height="512" fill="{bg_color}"/>\n'
    
    # Grid base layout for rigid geometry
    center_x, center_y = 256, 256
    
    # Types of shapes
    shapes = ["diamond", "chevron", "brackets", "hexagon", "grid"]
    shape = random.choice(shapes)
    
    svg += f'  <g stroke="{stroke_color}" stroke-width="{stroke_width}" fill="none" stroke-linejoin="miter" stroke-linecap="square">\n'
    
    if shape == "diamond":
        svg += f'    <polygon points="256,128 384,256 256,384 128,256"/>\n'
        if random.random() > 0.5:
            svg += f'    <polygon points="256,170 341,256 256,341 170,256"/>\n'
    elif shape == "chevron":
        svg += f'    <polyline points="170,170 341,170 256,300 170,170"/>\n'
        svg += f'    <polyline points="170,341 256,426 341,341"/>\n'
    elif shape == "brackets":
        svg += f'    <polyline points="200,150 128,256 200,362"/>\n'
        svg += f'    <polyline points="312,150 384,256 312,362"/>\n'
        svg += f'    <line x1="280" y1="120" x2="232" y2="392"/>\n'
    elif shape == "hexagon":
        svg += f'    <polygon points="256,128 366,192 366,320 256,384 145,320 145,192"/>\n'
        if random.random() > 0.5:
            svg += f'    <polygon points="256,178 322,217 322,295 256,334 189,295 189,217"/>\n'
    elif shape == "grid":
        for i in range(156, 357, 100):
            svg += f'    <line x1="{i}" y1="156" x2="{i}" y2="356"/>\n'
            svg += f'    <line x1="156" y1="{i}" x2="356" y2="{i}"/>\n'
            
    # Add spore dots
    num_dots = random.randint(3, 7)
    svg += f'  </g>\n'
    svg += f'  <g fill="{stroke_color}">\n'
    for _ in range(num_dots):
        dx = random.choice([-1, 1]) * random.randint(30, 150)
        dy = random.choice([-1, 1]) * random.randint(30, 150)
        r = random.choice([4, 6, 8])
        svg += f'    <circle cx="{center_x + dx}" cy="{center_y + dy}" r="{r}"/>\n'
    svg += f'  </g>\n'
    svg += f'</svg>\n'
    return svg

with open("test_logo.svg", "w") as f:
    f.write(generate_svg("test"))
