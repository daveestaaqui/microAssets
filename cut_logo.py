from PIL import Image

img = Image.open('assets/logo_v2.png').convert("RGBA")
width, height = img.size

# We want to clear pixels where x is roughly in the left or right gap
# and y is roughly in the bridge area (e.g. y=600 to 700).

for y in range(600, 700):
    for x in range(430, 480):
        # We only want to cut where it connects. To be safe, we can just clear a vertical strip
        # But maybe we want to make it look smooth.
        # Let's just clear a vertical strip of 10 pixels wide right in the middle of the gap
        if 445 < x < 455:
            img.putpixel((x, y), (0,0,0,0))

    for x in range(560, 610):
        if 575 < x < 585:
            img.putpixel((x, y), (0,0,0,0))

img.save('assets/logo_v9.png')
