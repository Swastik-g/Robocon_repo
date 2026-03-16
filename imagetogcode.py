import cv2
import numpy as np
import os

def image_to_gcode(image_path, output_file, threshold=128, scale=0.2):
    # 1. Robust File Verification
    abs_path = os.path.abspath(image_path)
    if not os.path.exists(abs_path):
        print(f"CRITICAL ERROR: Could not find file at: {abs_path}")
        print("Please ensure the filename matches exactly (including .png extension).")
        return

    # 2. Image Loading
    img = cv2.imread(abs_path)
    if img is None:
        print("CRITICAL ERROR: Failed to decode image. It might be corrupted.")
        return

    # 3. Pre-processing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    
    # 4. Contour Extraction
    # We use RETR_LIST to get all contours and CHAIN_APPROX_SIMPLE to reduce points
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"Success: Found {len(contours)} paths. Generating G-code...")

    # 5. G-code Generation
    with open(output_file, 'w') as f:
        f.write("G21 ; Set units to mm\n")
        f.write("G90 ; Absolute positioning\n")
        f.write("G00 Z5 ; Lift tool initially\n")
        
        for contour in contours:
            # Only process paths with enough points to be visible
            if len(contour) > 5:
                # Move to start of contour
                start_x, start_y = contour[0][0]
                f.write(f"G00 X{round(start_x * scale, 3)} Y{round(start_y * scale, 3)}\n")
                f.write("G01 Z-1 F200 ; Tool Down\n")
                
                # Draw the path
                for point in contour:
                    x, y = point[0]
                    f.write(f"G01 X{round(x * scale, 3)} Y{round(y * scale, 3)} F500\n")
                
                f.write("G00 Z5 ; Tool Up\n")
        
        f.write("G00 X0 Y0 ; Return to home\n")
        f.write("M30 ; End of program\n")
    
    print(f"Finished! G-code saved to: {output_file}")

# --- Execution Block ---
# Ensure 'input_logo.png' exists in the same folder as this script
if __name__ == "__main__":
    image_to_gcode('input_logo.jpg', 'output.gcode', threshold=128, scale=0.1)