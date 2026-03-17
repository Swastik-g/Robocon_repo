import cv2
import numpy as np

def generate_clear_gcode(image_path, output_file, scale=0.5):
    # Load image
    img = cv2.imread(image_path)
    if img is None: return
    
    # Pre-processing for high detail
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Use Gaussian Blur to remove noise, then Adaptive Thresholding
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    # Find contours with high precision
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_L1)
    
    with open(output_file, 'w') as f:
        f.write("G21 ; mm\nG90 ; Absolute\n")
        
        for contour in contours:
            # Filter out tiny noise (dust)
            if cv2.contourArea(contour) < 2:
                continue
                
            # Move to start (Pen UP)
            x_start, y_start = contour[0][0]
            f.write(f"G00 Z5\n")
            f.write(f"G00 X{round(x_start*scale, 2)} Y{round(y_start*scale, 2)}\n")
            
            # Start drawing (Pen DOWN)
            f.write(f"G01 Z-1 F200\n")
            for point in contour:
                x, y = point[0]
                f.write(f"G01 X{round(x*scale, 2)} Y{round(y*scale, 2)} F600\n")
            
            # Back to start to close the loop perfectly
            f.write(f"G01 X{round(x_start*scale, 2)} Y{round(y_start*scale, 2)}\n")
            
        f.write("G00 Z5\nG00 X0 Y0\nM30\n")
    print(f"High-detail G-code saved to {output_file}")

generate_clear_gcode('IITR-500x500.png', 'clear_output.gcode')