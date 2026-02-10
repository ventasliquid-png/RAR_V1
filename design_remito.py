from PIL import Image, ImageOps, ImageDraw, ImageChops
import os

# Configuration
REMITO_PATH = r"C:\dev\RAR_V1\Remito-Original.png"
LOGO_PATH = r"C:\dev\RAR_V1\Logo-color-liquid-sound-A4-(1).png"
OUTPUT_PATH = r"C:\dev\RAR_V1\base_remito_v1.png"

# Colors
CORPORATIVO_OSCURO = (37, 43, 117) # #252b75
WHITE = (255, 255, 255)

def trim(im):
    """
    Trims whitespace/transparent borders from the image.
    """
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

def clean_and_recolor(remito_img):
    """
    1. Clean top-left corner.
    2. Recolor non-white pixels to CORPORATIVO_OSCURO.
    """
    # Ensure RGBA
    img = remito_img.convert("RGBA")
    width, height = img.size

    # 1. Clean Phase: Reduced dimensions to avoid covering address
    # Previous: 0.35 w, 0.18 h -> Too big
    # New: 0.25 w, 0.12 h
    clean_w = int(width * 0.25)
    clean_h = int(height * 0.12)
    
    draw = ImageDraw.Draw(img)
    # Draw white rectangle to erase old logo
    draw.rectangle([(0, 0), (clean_w, clean_h)], fill=WHITE)
    print(f"[INFO] Cleaned area: {clean_w}x{clean_h}")

    # 2. Recolor Phase
    gray = img.convert("L")
    recolored = ImageOps.colorize(gray, black=CORPORATIVO_OSCURO, white=WHITE)
    
    return recolored.convert("RGBA"), clean_w, clean_h

def graft_logo(base_img, logo_img, max_w, max_h):
    """
    Overlay logo in the top-left area, fitting within max_w/max_h.
    """
    # Trim the logo first to remove excess whitespace
    trimmed_logo = trim(logo_img)
    print(f"[INFO] Logo trimmed from {logo_img.size} to {trimmed_logo.size}")

    base_w, base_h = base_img.size
    logo_w, logo_h = trimmed_logo.size
    
    # Calculate scale to fit within the cleaned area with some padding
    # Let's use 90% of the cleaned area as max size
    target_w_limit = int(max_w * 0.90)
    target_h_limit = int(max_h * 0.90)
    
    # Logic to fit inside the box while maintaining aspect ratio
    ratio_w = target_w_limit / logo_w
    ratio_h = target_h_limit / logo_h
    scale_factor = min(ratio_w, ratio_h)
    
    target_w = int(logo_w * scale_factor)
    target_h = int(logo_h * scale_factor)
    
    print(f"[INFO] Resizing logo to {target_w}x{target_h}")
    resized_logo = trimmed_logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Position: Centered within the cleaned area
    # clean_w = max_w, clean_h = max_h
    # X = (max_w - target_w) / 2
    # Y = (max_h - target_h) / 2
    
    pos_x = int((max_w - target_w) / 2)
    pos_y = int((max_h - target_h) / 2)
    position = (pos_x, pos_y)
    
    # Create final image
    final_img = base_img.copy()
    final_img.paste(resized_logo, position, mask=resized_logo if resized_logo.mode == 'RGBA' else None)
    
    return final_img

def main():
    if not os.path.exists(REMITO_PATH):
        print(f"[ERROR] {REMITO_PATH} not found.")
        return
    if not os.path.exists(LOGO_PATH):
        print(f"[ERROR] {LOGO_PATH} not found.")
        return

    print("Loading images...")
    remito = Image.open(REMITO_PATH)
    logo = Image.open(LOGO_PATH)
    
    # 1 & 2. Clean and Recolor
    print("Executing Cleaning and Recoloring Phase...")
    processed_base, clean_w, clean_h = clean_and_recolor(remito)
    
    # 3. Graft Logo (passing clean area dimensions to constrain logo)
    print("Executing Grafting Phase...")
    final_result = graft_logo(processed_base, logo, clean_w, clean_h)
    
    # Save
    final_result.save(OUTPUT_PATH)
    print(f"[SUCCESS] Harmonic Design Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
