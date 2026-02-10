from PIL import Image, ImageOps, ImageDraw
import os

# Configuration
INPUT_PATH = r"C:\dev\RAR_V1\Remito Original a.jpg"
OUTPUT_PATH = r"C:\dev\RAR_V1\base_remito_PRUEBA_COLOR.png"

# Colors
CORPORATIVO_OSCURO = (37, 43, 117) # #252b75
WHITE = (255, 255, 255)

def advanced_recolor():
    if not os.path.exists(INPUT_PATH):
        print(f"[ERROR] {INPUT_PATH} not found.")
        return

    print(f"Loading {INPUT_PATH}...")
    original = Image.open(INPUT_PATH).convert("RGBA")
    w, h = original.size

    # 1. Global Unification (Smart Tinting)
    # This prevents halos by mapping the entire grayscale spectrum of the lines
    # to the target color spectrum (Target -> White).
    print("Applying Smart Tinting (Global)...")
    gray = original.convert("L")
    unified = ImageOps.colorize(gray, black=CORPORATIVO_OSCURO, white=WHITE).convert("RGBA")

    # 2. Logo Protection (Masking)
    # We need to copy the original logo back onto the unified image.
    # Heuristic: Logo is in Top-Left.
    # Let's estimate the region. 
    # Based on previous steps, logo target was ~334x378 px inside a 637x420 area.
    # The user manual placement might vary.
    # Let's define a safe box that covers the logo.
    # If we take 35% Width and 18% Height, we likely cover it.
    
    # However, simply pasting a rectangle might cut lines that 'unified' correctly.
    # Ideal: Detect where the "Color" is in the original and keep it.
    
    # Detection Strategy:
    # "Color" pixels (High Saturation) in the Top-Left quadrant should be kept.
    # Everything else (Grayscale/Purple-ish) should be from 'unified'.
    
    print("Protecting Logo Region...")
    
    # Work on pixels
    final_img = Image.new("RGBA", original.size)
    unified_pixels = unified.load()
    original_pixels = original.load()
    final_pixels = final_img.load()
    
    # Define ROI for detection (Top Left Quadrant)
    roi_w = int(w * 0.45)
    roi_h = int(h * 0.25)
    
    for y in range(h):
        for x in range(w):
            # Default: Use Unified Pixel
            pixel_u = unified_pixels[x, y]
            
            # Logic to switch to Original:
            # 1. Must be in ROI
            if x < roi_w and y < roi_h:
                # 2. Must be "Logo Content"
                # Check for Saturation or Difference from Unified style
                r, g, b, a = original_pixels[x, y]
                
                # Smart Check: Is it colored?
                # Simple Saturation: Max(RGB) - Min(RGB)
                sat = max(r, g, b) - min(r, g, b)
                
                # Also check if it's NOT the purple/lila line color.
                # Purple is Red+Blue. 
                # If Green is significantly lower than Red and Blue, it's Purple.
                # If it's the Corporate Blue logo (Cyan/Blue-ish), Green might be higher?
                # Logo "Liquid Sound" is usually Cyan/Blue gradient or Multicolor.
                
                # Let's trust the "Color" heuristic.
                # If Saturation > Threshold -> Keep Original
                # Threshold: 30 seems safe for digital logos.
                if sat > 30:
                    final_pixels[x, y] = original_pixels[x, y]
                else:
                    # It's gray or faint purple -> Use Unified
                    final_pixels[x, y] = pixel_u
            else:
                # Outside ROI -> Always Unified
                final_pixels[x, y] = pixel_u
                
    final_img.save(OUTPUT_PATH)
    print(f"[SUCCESS] Proof of Concept saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    try:
        advanced_recolor()
    except Exception as e:
        print(f"[ERROR] {e}")
