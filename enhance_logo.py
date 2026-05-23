from PIL import Image, ImageEnhance

img = Image.open('assets/logo_v9.png')
enhancer = ImageEnhance.Brightness(img)
img = enhancer.enhance(1.2)
img.save('assets/logo_v10.png')
