from PIL import Image, ImageDraw, ImageFont
import os

img = Image.new("RGBA", (512, 512), (0, 38, 99, 255)) # Tata AIA navy
draw = ImageDraw.Draw(img)

# Crimson accent stripe
draw.rectangle([0, 480, 512, 512], fill=(184, 20, 36, 255))

# Draw white shield/document icon and text
draw.rectangle([120, 80, 392, 420], outline=(255, 255, 255, 255), width=16)
draw.line([(160, 160), (350, 160)], fill=(255, 255, 255, 255), width=12)
draw.line([(160, 220), (350, 220)], fill=(255, 255, 255, 255), width=12)
draw.line([(160, 280), (310, 280)], fill=(255, 255, 255, 255), width=12)

# Checkmark
draw.line([(160, 350), (200, 390)], fill=(184, 20, 36, 255), width=16)
draw.line([(200, 390), (320, 310)], fill=(184, 20, 36, 255), width=16)

out_path = r"C:\Users\patha\OneDrive\Desktop\Application Form\static\icon.png"
img.save(out_path)
print("Saved icon.png")
