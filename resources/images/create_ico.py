
import os
from PIL import Image

def create_ico():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    png_path = os.path.join(current_dir, "app_icon.png")
    ico_path = os.path.join(current_dir, "app_icon.ico")
    
    if not os.path.exists(png_path):
        print(f"Error: PNG file not found at {png_path}")
        return False
    
    try:
        img = Image.open(png_path)
        
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128)]
        img_list = []
        
        for size in icon_sizes:
            resized_img = img.resize(size, Image.LANCZOS)
            img_list.append(resized_img)
        
        img_list[0].save(
            ico_path, 
            format='ICO', 
            sizes=[(img.width, img.height) for img in img_list],
            append_images=img_list[1:]
        )
        
        print(f"Successfully created ICO file at {ico_path}")
        return True
    except Exception as e:
        print(f"Error creating ICO file: {e}")
        return False

if __name__ == "__main__":
    create_ico() 