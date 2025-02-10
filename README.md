# AI-Powered Land Area Measurement App

## Overview
This project is an AI-powered land area measurement application that allows users to select a region on an interactive map and automatically detect boundaries to calculate the area. It uses OpenStreetMap (OSM) for map visualization and integrates OpenCV, GeoPandas, and Flask for backend processing.

## Features
- Interactive map with OpenStreetMap (OSM)
- Automatic boundary detection using OpenCV
- Area calculation using GeoPandas and Shapely
- Flask-based backend for processing
- Processed image overlay on the map

## Installation

### Prerequisites
Make sure you have Python installed (preferably Python 3.8 or higher).

### Install Dependencies
Run the following command to install all required dependencies:
```bash
pip install -r requirements.txt
```

## Usage
1. Run the Flask application:
   ```bash
   python app.py
   ```
2. Open a web browser and go to `http://localhost:5000`
3. Select a region on the map.
4. The system will detect the boundary and display the measured area.

## Technologies Used
- **Flask**: Backend framework
- **OpenCV**: Image processing for boundary detection
- **GeoPandas**: Geospatial data analysis
- **Shapely**: Geometry operations
- **Leaflet.js**: Interactive map visualization
- **NumPy & SciPy**: Mathematical and scientific computing

## Folder Structure
```
project-root/
|── models/
|   |── frozen_east_text_detection.pb
│── app.py                # Flask backend
│── static/               # For processed images
│   ├── processed_images
│── templates/
│   ├── index.html        # Auto 
│   ├── manual.html       # Manual
│── requirements.txt      # Dependencies
│── README.md             # Project documentation
```

## Future Improvements
- AI-based enhanced boundary detection
- Satellite live imagery for more accurate results 
- Cloud deployment for accessibility

## Contributors
-Manav Dhamecha  
-Jenil Prajapati  
-Rudraksh Fanse  
-Samanvitha Bolisetty  
-Sherya Ashar  


