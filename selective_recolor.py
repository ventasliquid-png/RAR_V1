from PIL import Image, ImageColor
import os
import numpy as np

# Configuration
INPUT_PATH = r"C:\dev\RAR_V1\Remito Original a.jpg"
OUTPUT_PATH = r"C:\dev\RAR_V1\base_remito_v1.png"

# Colors
CORPORATIVO_OSCURO = (37, 43, 117) # #252b75
WHITE = (255, 255, 255)

def selective_recolor(img_path, target_color):
    if not os.path.exists(img_path):
        print(f"[ERROR] {img_path} not found.")
        return

    print(f"Loading {img_path}...")
    img = Image.open(img_path).convert("RGBA")
    data = np.array(img)

    # Separation Logic:
    # Text/Lines usually: Dark (Low Value) and Low Saturation.
    # Logo usually: Colored (High Saturation) OR specific colors.
    # Background: Bright (High Value).

    # Extract R, G, B, A
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

    # Calculate Brightness (Luminance)
    # Rec. 601 luma: Y = 0.299*R + 0.587*G + 0.114*B
    brightness = 0.299 * r + 0.587 * g + 0.114 * b

    # Calculate Saturation (approximation)
    # S = (Max - Min) / Max
    c_max = np.maximum(np.maximum(r, g), b)
    c_min = np.minimum(np.minimum(r, g), b)
    diff = c_max - c_min
    # Avoid div/0
    with np.errstate(divide='ignore', invalid='ignore'):
        saturation = np.where(c_max == 0, 0, diff / c_max)

    # Thresholds (We need to tune these)
    # Background: Brightness > 200 (White paper)
    # Text/Lines: Brightness < 180 (Dark ink), Saturation < 0.2 (Grayscale/Black ink)
    # Logo: Saturation > 0.2 (Colored) OR specific hues. 
    # If the logo is black, this logic fails. But user said "everything that is not logo".
    # Assuming logo is colored or distinctive.

    # Mask for Text/Lines
    # Is Dark AND Is Low Saturation
    is_dark = brightness < 200 # Allow some gray
    is_low_sat = saturation < 0.3 # Allow slight noise
    
    # We want to change pixels that are Dark AND Low Saturation
    mask = is_dark & is_low_sat

    # Apply target color
    data[mask, 0] = target_color[0]
    data[mask, 1] = target_color[1]
    data[mask, 2] = target_color[2]
    # Keep Alpha as is

    result = Image.fromarray(data)
    result.save(OUTPUT_PATH)
    print(f"[SUCCESS] Recolored image saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    selective_recolor(INPUT_PATH, CORPORATIVO_OSCURO)
