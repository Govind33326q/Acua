# AquaScan AI

AI-powered marine debris detection for side-scan sonar imagery. The application uses a trained Ultralytics YOLOv8 model, a FastAPI backend, and a React/Vite frontend.

## Project Layout

```text
AquaVisinaries/
├── Marine-Debris.v2i.yolov8/   # train, valid, test images and labels
├── models/
│   └── marine_debris_yolov8n_best.pt
├── outputs/
│   ├── predictions/            # annotated prediction images
│   └── reports/                # generated PDF reports
├── src/
│   ├── api.py                  # FastAPI application
│   ├── localization.py         # optional forward-looking fan estimate
│   ├── predict.py              # command-line prediction
│   └── report.py               # PDF report generation
├── frontend/                   # React/Vite dashboard
├── train_marine_debris_yolov8.ipynb
└── requirements.txt
```

## Requirements

- Windows 10 or later
- Python 3.12 (64-bit recommended)
- Node.js and npm
- The trained model at `models/marine_debris_yolov8n_best.pt`

Ultralytics installs its required PyTorch and OpenCV dependencies. PyTorch currently runs on CPU in the checked environment; GPU use requires installing a PyTorch build compatible with your CUDA setup.

## Python Setup

Open Command Prompt in the project directory. Create the virtual environment once, then activate it whenever opening a new terminal:

```cmd
cd /d "D:\AquaVisionaries\AquaVisinaries\AquaVisinaries"
C:\Users\govin\AppData\Local\Programs\Python\Python312\python.exe -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If you are using a different machine, replace the Python path with the location of your Python 3.12 install.

## Run a Prediction from the Command Line

From the project directory, with the virtual environment active:

```cmd
python src\predict.py --image "Marine-Debris.v2i.yolov8\test\images\marine-debris-aris3k-1014_png.rf.97f7a3c269383504d83611e2a9466948.jpg"
```

The script prints each detected class, confidence, and pixel bounding box. The annotated image is saved under `outputs\predictions\`.

## Run the Complete Application

Use two Command Prompt windows. Port `8001` is used below because port `8000` may already be occupied.

### 1. Start FastAPI

```cmd
cd /d "D:\AquaVisionaries\AquaVisinaries\AquaVisinaries"
.venv\Scripts\activate
python -m uvicorn src.api:app --host 127.0.0.1 --port 8001
```

FastAPI docs: <http://127.0.0.1:8001/docs>

### 2. Start React

```cmd
cd /d "D:\AquaVisionaries\AquaVisinaries\AquaVisinaries\frontend"
set "PATH=C:\Program Files\nodejs;%PATH%"
set "VITE_API_URL=http://127.0.0.1:8001"
"C:\Program Files\nodejs\npm.cmd" install
"C:\Program Files\nodejs\npm.cmd" run dev -- --host 127.0.0.1 --port 5174 --strictPort
```

If you prefer the project script shortcut, run:

```cmd
cd /d "D:\AquaVisionaries\AquaVisinaries\AquaVisinaries"
start_app.bat
```

Open the dashboard at <http://127.0.0.1:5174/>. Keep both terminal windows running while using the app. Upload a sonar image and select **Detect objects**. Results include the detections, annotated image, and a PDF report download.

The API allows the Vite development origins on ports 5173, 5174, and 5175. If you choose another frontend port, add that exact origin to the CORS allowlist in `src/api.py`.

## Deploy on Render

Create a **Blueprint** in Render from this repository and let it use the root `render.yaml`. It deploys the React dashboard as a static site and the FastAPI service separately. The dashboard's service URL is `https://aquascan-dashboard.onrender.com` and the API URL is `https://aquascan-api.onrender.com`; if Render assigns different URLs, update `VITE_API_URL` on the static site and `CORS_ORIGINS` on the API, then redeploy both.

The root `app.py` is a separate Streamlit interface. Deploying it on Streamlit Community Cloud will show that Streamlit UI, not the React dashboard used by `start_app.bat`.

## Outputs

- Annotated images: `outputs/predictions/`
- PDF reports: `outputs/reports/`

Reports include detections and pixel bounding boxes. Existing reports are not overwritten; repeated reports receive a numbered filename.

## Dataset and Training

The dataset is stored in `Marine-Debris.v2i.yolov8/`. Use `train_marine_debris_yolov8.ipynb` to train the model. The notebook resolves split image paths in memory and does not change the dataset. The exported `data.yaml` uses relative paths that assume a different parent layout, so use the notebook's path handling rather than passing that YAML directly to a training command from this workspace.

## Localization Note

YOLO bounding boxes are image pixels, not geographic coordinates. Geographic estimates are optional and are only enabled for a forward-looking sonar fan when GPS position, heading, range, and field of view are provided. The current side-scan dataset does not include the navigation metadata needed to locate objects; in that case the dashboard reports location as unavailable and does not invent coordinates.
