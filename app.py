from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
import os
from shapely.geometry import Polygon, Point
from rtree import index
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
from scipy import ndimage
from geographiclib.geodesic import Geodesic

app = Flask(__name__)

# Configuration
PROCESSED_DIR = r"D:\Coding\VSCODE\AI 0\static\processed_images"
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Global variables
contour_index = index.Index()
valid_polygons = []
scaling_factor = 1.0

def calculate_scaling(zoom, lat):
    """Calculate meters per pixel using Web Mercator formula"""
    return 156543.03 * np.cos(np.deg2rad(lat)) / (2 ** zoom)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/manual')
def manual():
    return render_template("manual.html")

@app.route('/process-image', methods=['POST'])
def process_image():
    global valid_polygons, contour_index, scaling_factor
    
    # Reset previous data
    contour_index = index.Index()
    valid_polygons = []
    
    # Get parameters
    file = request.files['image']
    zoom = int(request.form.get('zoom', 1))
    lat = float(request.form.get('lat', 51.505))
    scaling_factor = calculate_scaling(zoom, lat)

    # Save and verify uploaded image
    img_path = os.path.join(PROCESSED_DIR, "uploaded.png")
    file.save(img_path)
    image = cv2.imread(img_path)
    
    if image is None:
        return jsonify({"error": "Failed to read image"}), 400

    # Image processing steps
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=3)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)
    D = ndimage.distance_transform_edt(cleaned)
    coords = peak_local_max(D, min_distance=15, labels=cleaned)
    mask = np.zeros(D.shape, dtype=bool)
    mask[tuple(coords.T)] = True
    markers, _ = ndimage.label(mask)
    labels = watershed(-D, markers, mask=cleaned)
    output = np.zeros_like(image)
    valid_contours = []
    for label in np.unique(labels):
        if label == 0: continue
        mask = np.zeros(gray.shape, dtype="uint8")
        mask[labels == label] = 255
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnts:
            if cv2.contourArea(cnt) > 300:
                epsilon = 0.005 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                valid_contours.append(approx)
    for idx, cnt in enumerate(valid_contours):
        try:
            points = np.squeeze(cnt)
            if points.ndim == 1: continue
            poly = Polygon(points)
            if not poly.is_valid: poly = poly.buffer(0)
            valid_polygons.append(poly)
            contour_index.insert(idx, poly.bounds)
        except Exception as e:
            print(f"Contour error: {e}")
    cv2.drawContours(output, valid_contours, -1, (0, 255, 0), 2)
    out_path = os.path.join(PROCESSED_DIR, "processed.png")
    cv2.imwrite(out_path, output)
    
    return jsonify({
        "processed_image_url": f"/static/processed_images/processed.png?t={os.times().elapsed}",
        "width": output.shape[1],
        "height": output.shape[0],
        "contours": [np.squeeze(c).tolist() for c in valid_contours if c.shape[0] > 2]
    })

@app.route('/get-area')
def get_area():
    x = int(request.args.get('x'))
    y = int(request.args.get('y'))
    point = Point(x, y)
    for idx in contour_index.intersection((x, y, x, y)):
        if valid_polygons[idx].contains(point):
            area = valid_polygons[idx].area * (scaling_factor ** 2)
            return jsonify({"area": round(area, 2), "contour_index": idx})
    return jsonify({"area": None})

if __name__ == '__main__':
    app.run(debug=True, threaded=True)