import cv2
import numpy as np
import math

def calculate_calibration(image_path):
    image = cv2.imread(image_path)
    if image is None: return None, 0
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    valid_lines = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 80 < h < 1500 and h > (w * 2): 
            valid_lines.append((x, y, w, h))
            
    if len(valid_lines) < 10: return None, len(valid_lines)
    
    sorted_lines = sorted(valid_lines, key=lambda item: item[0])
    line_centers = [x + (w / 2) for x, y, w, h in sorted_lines]
    pixel_distances = []
    for i in range(len(line_centers) - 1):
        gap = line_centers[i+1] - line_centers[i]
        if gap < 100: pixel_distances.append(gap)
        
    avg_pixel_dist = np.median(pixel_distances)
    return (10.0 / avg_pixel_dist), len(valid_lines)

def launch_ruler(img_path, ratio):
    original_img = cv2.imread(img_path)
    if original_img is None: return

    scale_percent = 12
    width = int(original_img.shape[1] * scale_percent / 100)
    height = int(original_img.shape[0] * scale_percent / 100)
    display_img = cv2.resize(original_img, (width, height), interpolation=cv2.INTER_AREA)
    clean_proxy = display_img.copy() # Keep a clean version to reset
    
    clicks = []

    def mouse_callback(event, x, y, flags, param):
        nonlocal clicks, display_img
        if event == cv2.EVENT_LBUTTONDOWN:
            # If we already have a measurement, clear it before starting a new one
            if len(clicks) == 0:
                display_img = clean_proxy.copy()

            clicks.append((x, y))
            cv2.circle(display_img, (x, y), 5, (0, 0, 255), -1)
            
            if len(clicks) == 2:
                pt1, pt2 = clicks[0], clicks[1]
                cv2.line(display_img, pt1, pt2, (0, 255, 0), 2)
                
                # Math
                proxy_dist = math.sqrt((pt2[0]-pt1[0])**2 + (pt2[1]-pt1[1])**2)
                real_um = (proxy_dist * (100 / scale_percent)) * ratio
                
                # --- NEW: DRAW TEXT ON WINDOW ---
                text = f"{real_um:.2f} um"
                # Find the midpoint of the line to place the label
                mid_x, mid_y = (pt1[0] + pt2[0]) // 2, (pt1[1] + pt2[1]) // 2
                
                # Draw black background for text (makes it easier to read)
                cv2.putText(display_img, text, (mid_x + 10, mid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 4)
                # Draw white text
                cv2.putText(display_img, text, (mid_x + 10, mid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
                
                clicks = [] # Reset clicks
                
            cv2.imshow("Linear Ruler", display_img)

    cv2.namedWindow("Linear Ruler", cv2.WINDOW_AUTOSIZE)
    cv2.imshow("Linear Ruler", display_img)
    cv2.setMouseCallback("Linear Ruler", mouse_callback)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def launch_lasso(img_path, ratio):
    original_img = cv2.imread(img_path)
    if original_img is None: return

    scale_percent = 12
    width = int(original_img.shape[1] * scale_percent / 100)
    height = int(original_img.shape[0] * scale_percent / 100)
    display_img = cv2.resize(original_img, (width, height), interpolation=cv2.INTER_AREA)
    clean_proxy = display_img.copy()

    drawing = False
    points = []

    def mouse_callback(event, x, y, flags, param):
        nonlocal drawing, points, display_img
        
        if event == cv2.EVENT_LBUTTONDOWN:
            display_img = clean_proxy.copy() # Clear previous lasso
            drawing = True
            points = [(x, y)]
            
        elif event == cv2.EVENT_MOUSEMOVE and drawing:
            points.append((x, y))
            cv2.line(display_img, points[-2], points[-1], (0, 255, 0), 2)
            cv2.imshow("Lasso Tool", display_img)
            
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            if len(points) > 2:
                cv2.line(display_img, points[-1], points[0], (0, 255, 0), 2)
                
                # Math
                contour = np.array(points).reshape((-1, 1, 2))
                multiplier = 100 / scale_percent
                real_peri = (cv2.arcLength(contour, True) * multiplier) * ratio
                real_area = (cv2.contourArea(contour) * (multiplier ** 2)) * (ratio ** 2)
                
                # --- NEW: DRAW RESULTS ON TOP-LEFT ---
                peri_text = f"P: {real_peri:.2f} um"
                area_text = f"A: {real_area:.2f} um2"
                
                # Background rectangles for text
                cv2.rectangle(display_img, (5, 5), (200, 60), (0,0,0), -1)
                # Drawing text
                cv2.putText(display_img, peri_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
                cv2.putText(display_img, area_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
                
                cv2.imshow("Lasso Tool", display_img)

    cv2.namedWindow("Lasso Tool", cv2.WINDOW_AUTOSIZE)
    cv2.imshow("Lasso Tool", display_img)
    cv2.setMouseCallback("Lasso Tool", mouse_callback)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            display_img = clean_proxy.copy()
            cv2.imshow("Lasso Tool", display_img)
        elif key == ord('q') or key == 27:
            break
    cv2.destroyAllWindows()