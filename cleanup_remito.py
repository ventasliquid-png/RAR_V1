from PIL import Image, ImageFilter, ImageOps
import numpy as np
import os

# Configuration
INPUT_PATH = r"C:\dev\RAR_V1\Remito Original a.jpg"
OUTPUT_PATH = r"C:\dev\RAR_V1\base_remito_v1.png"

# Colors
CORPORATIVO_OSCURO = (37, 43, 117) # #252b75
WHITE = (255, 255, 255)

def process_image():
    if not os.path.exists(INPUT_PATH):
        print(f"[ERROR] {INPUT_PATH} not found.")
        return

    print(f"Loading image from {INPUT_PATH}...")
    original = Image.open(INPUT_PATH).convert("RGBA")
    
    # 1. Masks Calculation
    img_array = np.array(original)
    r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
    
    # Saturation
    max_c = np.maximum(np.maximum(r, g), b)
    min_c = np.minimum(np.minimum(r, g), b)
    diff = max_c - min_c
    
    with np.errstate(divide='ignore', invalid='ignore'):
        sat = np.where(max_c == 0, 0, diff / max_c)
        
    # Luminance
    lum = 0.299*r + 0.587*g + 0.114*b

    # Masks
    mask_logo = sat > 0.15 # Protected Area
    
    # Content Selection:
    # Slightly more permissive on "Darkness" to catch faint parts of letters
    mask_content = (lum < 230) & (sat <= 0.15)

    # 2. Extract Content
    # White = Content, Black = Empty
    content_data = np.zeros(original.size[::-1], dtype=np.uint8) # Y, X
    content_data[mask_content] = 255
    content_layer = Image.fromarray(content_data, "L")

    # 3. Restoration Pipeline (Thickening)
    print("Restoring lines integrity...")
    
    # Removed MedianFilter (it eats pixels)
    
    # A. Dilation (Thickening)
    # Using MaxFilter to expand white areas (content) into black areas
    # Size 3 might be too strong, let's try 3 but maybe separate kernels if needed.
    # Start with standard 3x3 MaxFilter.
    thickened = content_layer.filter(ImageFilter.MaxFilter(size=3))
    
    # B. Smoothing (Upscale logic)
    target_scale = 2
    w, h = thickened.size
    
    upscaled = thickened.resize((w * target_scale, h * target_scale), Image.Resampling.BICUBIC)
    blurred = upscaled.filter(ImageFilter.GaussianBlur(radius=2))
    
    # C. Thresholding
    # Lower threshold = Thicker lines.
    # If pixel > 80 (very faint gray) -> Become 255 (Full Content)
    thresholded = blurred.point(lambda p: 255 if p > 80 else 0)
    
    smooth_content = thresholded.resize((w, h), Image.Resampling.LANCZOS)
    smooth_content = smooth_content.point(lambda p: 255 if p > 128 else 0)

    # 4. Reconstruction
    print("Reconstructing final image...")
    
    final_img = Image.new("RGB", original.size, WHITE)
    final_data = np.array(final_img)
    
    original_rgb = np.array(original.convert("RGB"))
    final_data[mask_logo] = original_rgb[mask_logo]
    
    effective_content_mask = (np.array(smooth_content) > 0) & (~mask_logo)
    final_data[effective_content_mask] = CORPORATIVO_OSCURO
    
    result = Image.fromarray(final_data)
    result.save(OUTPUT_PATH)
    print(f"[SUCCESS] Restored Remito saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    process_image()
