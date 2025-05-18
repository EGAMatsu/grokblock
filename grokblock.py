from PIL import Image, ImageEnhance
import numpy as np
import sys
import os

def process_image(png_path, scale=False, no_nags=True, annoys=False, overlay=False):
    nag_path = "./nag.png"                      # Path to nag overlay
    nAI_path = "./noAI.png"
    ovr_path = "./overlay.png"

    img = Image.open(png_path).convert("RGBA")  # Open the image
    if not no_nags:
        img = overlay_image(img, nag_path)
    if annoys:
        img = overlay_image(img, nAI_path)
    if overlay:
        img = overlay_multiply(img, ovr_path)

    palette_img = img.convert("P", palette=Image.ADAPTIVE, colors=252)  # Give it 256 colors
    constant_colors = [0, 0, 0, 255, 80, 0, 0, 175, 255, 255, 255, 255] # Make the Apple ][e color palette
    palette = palette_img.getpalette()[:252 * 3] + constant_colors      # Add it
    palette_img.putpalette(palette[:768])                               # Install the palette
    
    if scale:
        img_size = img.size
        scaled_img = img.resize((img_size[0] // 4, img_size[1] // 4), Image.Resampling.LANCZOS)
    else:
        scaled_img = img.resize(img.size, Image.Resampling.LANCZOS)

    return scaled_img, palette_img

def overlay_image(base_img, overlay_path):
    overlay = Image.open(overlay_path).resize(base_img.size)
    base_img.paste(overlay, (0, 0), overlay)
    return base_img

def overlay_multiply(base_img, overlay_path):
    overlay = Image.open(overlay_path).resize(base_img.size).convert("RGBA")
    anti_ai = Image.open("Anti_AI.PNG").resize(base_img.size).convert("RGBA")
    base_img = base_img.convert("RGBA")

    base_array = np.array(base_img, dtype=np.float32) / 255.0
    base_array = base_array*2
    overlay_array = np.array(overlay, dtype=np.float32) / 255.0
    anti_ai_array = np.array(anti_ai, dtype=np.float32) / 255.0

    height, width, _ = base_array.shape

    # Create a mask to alternate every pixel
    result_array = np.zeros_like(base_array)  # Initialize an empty array

    result_array[::3, ::3, :] = anti_ai_array[::3, ::3, :]  # Replace every other pixel with Anti_AI.PNG
    result_array[1::2, 1::2, :] = base_array[1::2, 1::2, :]  # Keep the rest as base image

    # Ensure values remain in valid range
    result_array = np.clip(result_array, 0, 1)
    result_array = (result_array * 255).astype(np.uint8)

    blended_img = Image.fromarray(result_array, mode="RGBA")
    return blended_img

def create_gif(png_path, scale=False, no_nag=False, double=False, keepNagForever=False, annoy=False, overlay=False):
    first_frame_path = "./Anti_AI.png"  # Add the anti-AI image as frame 0
    
    first_frame, indexed_png = process_image(png_path, scale, no_nag, annoy, overlay)
    first_frame = Image.open(first_frame_path).resize(indexed_png.size)

    frames = [first_frame]

    for i in range(8192):
        frame = indexed_png.copy()
        frames.append(frame)

    output_path = f"{os.path.splitext(png_path)[0]}.gif"

    durations = [1] + [20] * (len(frames) - 2) + [65535]

    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=durations, loop=0, disposal=2)  # Add the frames.

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage: python script.py <png_file> [-s Scale down] [-n Nag user [-hn Hold the nag forever.]] [-d Double time (Double size)]")           # Display arguments.
        sys.exit(1)

    png_file = sys.argv[1]
    scale_flag = "-s" in sys.argv
    no_nag_flag = "-n" in sys.argv
    double = "-d" in sys.argv
    annoyFlag = "-a" in sys.argv
    overlayFlag = "-o" in sys.argv

    create_gif(png_file, scale=scale_flag, no_nag=(not no_nag_flag), double=double, annoy=annoyFlag, overlay=overlayFlag)
