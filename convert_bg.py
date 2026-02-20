from PIL import Image
import os

input_path = "base_remito_v1.png"
output_path = "base_remito_v1.jpg"

if os.path.exists(input_path):
    print(f"Converting {input_path} to {output_path}...")
    try:
        img = Image.open(input_path)
        # Convert to RGB (discard alpha channel for JPG)
        rgb_img = img.convert('RGB')
        rgb_img.save(output_path, quality=95)
        print("Conversion successful.")
    except Exception as e:
        print(f"Error converting image: {e}")
else:
    print(f"Error: {input_path} not found.")
