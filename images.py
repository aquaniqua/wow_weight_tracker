import os
import random
from PIL import Image, ImageTk
from storage import resource_path

def pick_random_zone_image(zone_key, target_width=520, target_height=260):
    """Load and resize a random image from the specified zone folder."""
    folder = resource_path("zones", zone_key)
    if not os.path.isdir(folder):
        return None
    files = [f for f in os.listdir(folder)
             if f.lower().endswith(('.webp', '.png', '.jpg', '.jpeg'))]
    if not files:
        return None
    path = os.path.join(folder, random.choice(files))
    try:
        img = Image.open(path).convert("RGB")
        img = img.resize((target_width, target_height), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print("Image load error:", path, e)
        return None

