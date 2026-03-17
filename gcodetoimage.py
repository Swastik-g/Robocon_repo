from PIL import Image, ImageDraw
import re

def gcode_to_clear_image(gcode_path, output_path, img_size=(2500, 2500), scale=4):
    img = Image.new('RGB', img_size, 'white')
    draw = ImageDraw.Draw(img)
    
    last_x, last_y = 0, 0
    pen_down = False
    
    with open(gcode_path, 'r') as f:
        for line in f:
            # Check Z height
            z_match = re.search(r'Z([-+]?[0-9]*\.?[0-9]+)', line)
            if z_match:
                pen_down = float(z_match.group(1)) < 0
            
            # Get X, Y
            x_m = re.search(r'X([-+]?[0-9]*\.?[0-9]+)', line)
            y_m = re.search(r'Y([-+]?[0-9]*\.?[0-9]+)', line)
            
            if x_m or y_m:
                new_x = float(x_m.group(1)) if x_m else last_x
                new_y = float(y_m.group(1)) if y_m else last_y
                
                # Use a larger scale and offset to center the logo
                offset = 100 
                if pen_down:
                    draw.line([
                        (last_x * scale + offset, last_y * scale + offset), 
                        (new_x * scale + offset, new_y * scale + offset)
                    ], fill='black', width=2)
                
                last_x, last_y = new_x, new_y

    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_path)
    print(f"Clear image saved to {output_path}")

gcode_to_clear_image('logo_output.gcode', 'logo_from_gcode.png')