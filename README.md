# AquaVisionaries — sonar marine-debris detection

AquaVisionaries detects marine debris in sonar imagery with a trained YOLOv8n
model, explains every result with measured evidence, keeps a reviewable
history, and reads data from files, recordings, capture cards, network video
streams and NMEA GPS — all on your own computer, read-only.

The supplied model and data are **forward-looking imaging sonar** (fan-shaped
ARIS-style frames, 640×640, 11 classes). Earlier documentation called them
side-scan; the images themselves are fan-shaped, so the app treats them as
forward-looking fans and detects the geometry automatically.

Architecture and tech stack: `docs/AquaVisionaries_System_Architecture.pdf`.

**Release 3.0** turns the React + FastAPI app into a dark marine-sonar
operator console (Overview, Analyse, Sonar input, History & review,
Dashboard, Map / survey, Model & AI, Reports, System). The Streamlit variant
in `Aqua-Scan/` got the matching dark look. Model, weights and detection
pipeline are unchanged.

## Contents

1. What is in the release
2. Install and start
3. Using the app
4. Connecting a sonar (universal input)
5. GPS and maps
6. Tiled inference and measured results
7. Evidence, shadows, unexplained echoes, priority
8. History, reports, privacy
9. Tests
10. Troubleshooting
11. Known limitations
12. What is still needed for a specific sonar model

---

## 1. What is in the release

```text
AquaVisionaries/
├── start_app.bat / start_app.sh     one-command start (backend + built UI on port 8001)
├── start_streamlit.bat              Streamlit variant
├── requirements.txt                 Python dependencies
├── models/marine_debris_yolov8n_best.pt   model used by the FastAPI app (unchanged)
├── best.pt                          original weights used by app.py (unchanged)
├── Aqua-Scan/                       Streamlit app folder (own best.pt, app.py, requirements)
├── runs/marine_debris/yolov8n/      original training run: curves, results.csv, best.pt, last.pt
├── config/class_rules.yaml          editable priority / class rules
├── src/
│   ├── api.py                       FastAPI app (existing endpoints preserved)
│   ├── inference.py                 whole-image + tiled inference, class-aware merge
│   ├── analysis.py                  geometry, shadow, echo contrast, unexplained echoes, priority
│   ├── history.py                   SQLite detection history + human review
│   ├── stream_manager.py            source → bounded buffer → inference, GPS alignment
│   ├── report.py                    PDF reports
│   ├── localization.py              forward-fan geo-projection (unchanged maths)
│   ├── predict.py                   command-line detection
│   └── sonar_io/                    universal, read-only input layer
│       ├── decoders.py              images, 16-bit TIFF, npy/npz, CSV, raw binary
│       ├── adapters.py              video file, image folder, capture device, network stream
│       ├── gps.py                   NMEA 0183 parser; serial / UDP / TCP / log replay
│       └── vendor_template.py       how to add a documented vendor SDK/format
├── frontend/                        React + Vite source; frontend/dist is the built UI
├── samples/labelled/                12 labelled sonar frames (tests and trying the app)
├── outputs/model-performance/       stored validation metrics + tiling evaluation
├── tests/                           pytest suite + tiling evaluation script
├── train_marine_debris_yolov8.ipynb training notebook (unchanged)
└── docs/                            architecture and tech-stack PDF
```

Not included: `.venv`, `node_modules`, caches, `.git`, the 1,868-image
training dataset (download link in §11), the Colab training zip and old
prediction outputs. The original ZIP remains your full backup.

## 2. Install and start

Requirements: **Python 3.10–3.12** (tested with 3.12) and about 3 GB of disk
for PyTorch. Node.js is **not** needed to run — the interface is pre-built in
`frontend/dist`. A GPU is optional; CPU works.

### Windows

```cmd
:: 1. Extract the ZIP, e.g. to D:\AquaVisionaries_Professional_Release
cd /d D:\AquaVisionaries_Professional_Release\AquaVisionaries
:: 2. First start creates .venv and installs packages (several minutes); later starts are fast
start_app.bat
```

The browser opens <http://127.0.0.1:8001/>. Keep the window open; Ctrl+C stops.

### macOS / Linux

```bash
cd AquaVisionaries_Professional_Release/AquaVisionaries
./start_app.sh            # PYTHON=python3.12 ./start_app.sh to choose the interpreter
```

### Manual (any OS)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn src.api:app --host 127.0.0.1 --port 8001
```

API documentation: <http://127.0.0.1:8001/docs>.

### Developing the interface (optional)

```bash
cd frontend
npm install
npm run dev:host          # http://127.0.0.1:5174, talks to the API on :8001
npm run build             # rebuilds frontend/dist
```

`VITE_API_URL` overrides the API address in dev mode.

### Streamlit variant

```bash
cd Aqua-Scan
streamlit run app.py      # or start_streamlit.bat on Windows
```

It uses `Aqua-Scan/best.pt` and now offers **Whole image / Tiled** modes.
`Aqua-Scan/requirements.txt` is for Streamlit Community Cloud deployments.

### Command line

```bash
python src/predict.py --image samples/labelled/images/<file>.jpg [--mode tiled]
```

## 3. Using the app

The sidebar always shows the real state of API, MODEL (with CPU/GPU device),
SONAR, GPS and STORAGE, polled every 4 s from `/system/status`.

| Screen | Purpose |
|---|---|
| **Overview** | Command centre: system status, latest analysis with real counts, pending/confirmed/rejected totals, detection trend, latest real position, recent analyses, quick actions. Empty states when there is no history. |
| **Analyse** | Upload a file (or pick a bundled labelled sample frame), Whole or Tiled, confidence, tile size/overlap, input size, sonar geometry, optional navigation metadata. Shows file metadata (format, resolution, bit depth, timestamp, GPS), measured per-step server timings, and an **original vs annotated** viewer (side-by-side / slider / overlay, synchronized zoom, fit, fullscreen). Boxes are numbered `#01…`; clicking a box opens its finding and vice versa. |
| — findings | Each finding separates **AI classification** (class, confidence, box), **rule-based category** (from `config/class_rules.yaml`, with reason and source) and **human review** (confirm / reject / unsure). Evidence bars show model confidence, echo contrast and shadow darkness; the last two are labelled EXPERIMENTAL. "Why this priority" shows the exact formula. |
| — six-view gallery | Original, detection output, confidence map, geometry & shadow sample regions, unexplained bright echoes, priority & category. Each view has legend, source, expand and download; a view that cannot be computed says "Not available for this input". |
| **Sonar input** | Capture device, network stream, recording, image folder; pause/resume/disconnect; telemetry (latency, dropped frames, reconnects); GPS source panel. |
| **History & review** | Filter by class, date, review status, priority, source, category. Opening an analysis shows stored original + annotated image, findings with review actions, gallery, position, and lets you rebuild the PDF with the current review decisions. |
| **Dashboard** | 7 KPIs and 10 charts (trend, review status, class counts, confidence by class, confidence histogram, category, priority, review by class, inference time by mode, spatial count), filterable by date, class, review, priority, category, mode. |
| **Map / survey** | Leaflet/OpenStreetMap with survey positions, located detections and the GPS track — only from NMEA, EXIF or operator-entered positions. Otherwise "NO GPS LOCATION AVAILABLE". |
| **Model & AI** | Model card (file, device, classes), processing pipeline, **validation metrics** (overall + per class + confusion matrix), measured whole-vs-tiled comparison, and separately **operational metrics** from your own history. |
| **Reports** | Per-analysis PDF (generate/rebuild), CSV and JSON, plus full-history CSV. |
| **System** | Service status, accepted inputs, active class rules, architecture, what is stored. |

### Categories (harmful / harmless / useful / unknown)

`config/class_rules.yaml` gives every class a `category`, `category_reason`,
`category_source` and `operator_guidance`. They describe the **object type**
named by the class (e.g. tyres, lost fishing hooks, plastic bottles), cite a
general source where one exists, and never claim to know the material or
condition of the detected item — sonar cannot. Edit the file to change them;
a class without a rule shows "Unknown — operator review required".

Status labels are strict: **LIVE** appears only when a capture device or
network stream is connected *and* a frame arrived in the last 3 s. Uploads,
recordings and folders always show **Recorded replay**.

## 4. Connecting a sonar (universal input)

No sonar model was specified, so the app supports every **documented, generic**
way a sonar can deliver imagery. Pick the row that matches your equipment:

| Your sonar gives you | Choose in *Sonar input* | Live? | Notes |
|---|---|---|---|
| HDMI / VGA / composite video out from the head-unit or PC | **Sonar screen via capture card** (device index 0, 1, …) | Yes | Any UVC capture card. *Scan this computer* lists devices. Only pixels arrive; range/gain/frequency show as unavailable. |
| A network video stream from the sonar or its software | **Network video stream** (`rtsp://`, `http(s)://` MJPEG, `udp://`, `tcp://`, `rtp://`, `srt://`) | Yes | Auto-reconnect with back-off; credentials in the URL are never displayed. |
| A saved video (screen recording, vendor video export) | **Recording file** | No — replay | MP4/AVI/MKV/MOV/M4V/MPG/WMV. Every frame is analysed (no drops). |
| Multi-frame TIFF, NumPy stack, raw binary dump | **Recording file** | No — replay | Raw needs width/height/sample type/header. |
| A folder of exported images / .npy / CSV frames | **Folder of exported frames** | No — replay | Filename order, configurable frames per second. |
| One exported frame | **Analyse file** | — | JPG, PNG 8/16-bit, TIFF 8/16/32-bit/float, BMP, WebP, PGM/PPM, GIF, .npy/.npz, CSV/TSV/TXT, raw binary. |
| Proprietary logs: XTF, JSF, .aris, .sl2/.sl3, Humminbird .SON, .s7k, .all/.kmall, SDF, Oculus | Not parsed | — | Export images/video/CSV from the vendor software, or supply the spec and a sample (§12). The app refuses these files with an explanation instead of guessing. |

Data handling: original samples keep their dtype, bit depth and dimensions.
Non-8-bit data is converted for the model by a **linear min–max rescale** of
that frame (no gamma, no contrast enhancement, no clipping); the method is
shown with every result. Video frames may already carry compression from the
source codec — the app says so.

Buffering: live sources use a bounded buffer (default 4 frames) that drops the
oldest frame when full and counts drops; recordings wait instead, so every
frame is analysed. Each frame is time-stamped on arrival and paired with the
GPS fix current at that instant.

Safety: all device, stream and local-path controls are **read-only** and are
refused from other computers (HTTP 403) unless you set
`AQUASCAN_ALLOW_REMOTE_CONTROL=1`. The server binds to `127.0.0.1` by default.
A cloud-hosted copy cannot reach a sonar plugged into your laptop — run the
app locally (edge mode) next to the sonar. No remote gateway is included.

## 5. GPS and maps

Position sources (*Sonar input → Position source*):

* **NMEA 0183 over UDP** (default port 10110) — most chart plotters/GPS broadcast this
* **NMEA 0183 over TCP** — client with automatic reconnect
* **NMEA 0183 serial / USB GPS** — `COM3` or `/dev/ttyUSB0`, 4800/9600/38400/115200 baud (`pyserial`)
* **NMEA log replay** — labelled "recorded"
* **Operator-entered fixed position**
* **EXIF GPS** inside uploaded images (read automatically)

Sentences GGA, RMC, HDT/HDG and VTG are parsed; bad checksums, void RMC and
fix-quality-0 GGA are rejected. A fix older than 3 s counts as no fix.

What a marker means is always stated: *survey/vessel position (not object
position)* by default, or *estimated object position* only for a
forward-looking fan when heading, range and horizontal field of view are
known. Without a valid source the UI shows **"No GPS location available"** and
no marker is drawn. Tracks are drawn only from real timestamped fixes. Map
tiles come from OpenStreetMap (attribution shown, standard usage policy, no
API key); offline, the map is blank but coordinates remain listed.

## 6. Tiled inference and measured results

Tiled mode splits the image into overlapping tiles (default 320 px, 25 %
overlap; the last tile is shifted to end on the image edge, never padded),
runs the model on each, maps boxes back to full-image coordinates, clips them,
optionally adds a whole-image pass, and merges duplicates with **class-aware
NMS (IoU ≥ 0.5)** plus same-class **containment suppression**
(intersection / smaller area ≥ 0.8) to remove boxes cut by tile boundaries.

Measured on the 187-image labelled test split (411 objects, same class,
IoU ≥ 0.5, confidence 0.25, 1 vCPU; `python tests/evaluate_tiling.py`):

| Mode | Precision | Recall | F1 | Recall, objects < 64×64 px (121) | Time / image |
|---|---|---|---|---|---|
| Whole image | 92.3 % | 96.4 % | 94.3 % | 94.2 % | 103 ms |
| Tiled + whole pass | 78.3 % | 95.6 % | 86.1 % | 95.0 % | 1,014 ms |
| Tiles only | 57.3 % | 73.7 % | 64.5 % | 77.7 % | 924 ms |

**On this dataset tiling does not improve results** — it adds false positives
(tiles show partial fans the model was not trained on) and is about 10×
slower. Whole image is therefore the default. Tiling is provided for larger,
higher-resolution survey imagery; measure it on your own labelled data with
the same script before relying on it.

## 7. Evidence, shadows, unexplained echoes, priority

Every finding shows class, model confidence, pixel box and size, whether it
came from a tile or the whole image, and these **experimental heuristics**
(not validated — the dataset has no shadow or anomaly labels):

* **Acoustic shadow.** For a forward-looking fan the apex is fitted from the
  fan edges and the region *radially behind* the object is compared with
  neighbouring regions at the same range; the box's far half is also checked
  for dark pixels. For a declared side-scan waterfall the shadow is sampled
  away from a centre nadir (untested: no side-scan data supplied). Shadow is a
  supporting signal only and never removes a detection.
* **Echo contrast.** Box 90th-percentile intensity vs. surrounding median and spread.
* **Unexplained bright echoes.** Compact returns brighter than
  max(p99.5, median + 6·MAD) that no detection covers — a prompt to look, not
  an anomaly detector. A trained anomaly detector is not provided because the
  data contains no normal-seabed reference set to calibrate one.

**Priority** = confidence × class weight from `config/class_rules.yaml`
(high ≥ 0.70, medium ≥ 0.45). All class weights are 1.0 except `Wall` (0.3,
a structure rather than debris). Hazard and recyclability are "Needs operator
review" for every class, because sonar cannot determine material and no
documented source was supplied. Machine assessment and human review are stored
and displayed separately.

## 8. History, reports, privacy

* History: SQLite at `outputs/history/aquascan_history.db` (override with
  `AQUASCAN_HISTORY_DB`). Persists until *History & review → Clear history*,
  which also deletes annotated images and reports. On ephemeral cloud hosts it
  is lost on restart.
* Stored: settings, timings, detections, measured signals, machine priority,
  position (only from a real source) and review decisions.
* **Stored preview:** for uploaded files an 8-bit JPEG display copy of the
  decoded frame (`outputs/predictions/<id>_original.jpg`) so history and PDF
  reports can show original and annotated side by side. Disable with
  `AQUASCAN_STORE_ORIGINAL_PREVIEW=0`. The raw upload itself (e.g. 16-bit TIFF,
  .npy, raw) is not kept. Uploaded recordings are deleted when you
  disconnect; leftovers older than 24 h are purged at start.
* Annotated images: `outputs/predictions/`. PDF reports: `outputs/reports/`.
* Stream frames are saved to history only if they contain detections (at most
  one per second; can be switched off).
* Exports: per-analysis PDF (original + annotated, finding-by-finding details,
  categories, review summary, methodology notes, footer), per-analysis CSV and
  JSON, full-history CSV. `POST /history/{id}/report` rebuilds a PDF with the
  current review decisions.
* Databases from release 2.0 are upgraded in place (new columns added).
* No secrets, API keys or telemetry are included; nothing leaves your computer
  except map tile requests when a map is shown.

## 9. Tests

```bash
python -m pytest -q                              # full suite, 1–2 min on CPU
python tests/evaluate_tiling.py --split test     # needs the dataset folder
```

The suite covers tile coverage for uneven sizes, coordinate remapping on a
1280×1280 mosaic of real frames, duplicate/fragment merging, zero detections,
confidence changes, invalid/unsupported files, 16-bit PNG, multi-page TIFF,
npy/CSV/raw decoding, EXIF GPS, NMEA parsing, stale fixes, UDP and log-replay
GPS, API legacy fields, tiled API, GPS present/absent/invalid, history
review/CSV/clear, recording replay (never "LIVE", no dropped frames), folder
replay with pause/resume and GPS alignment, a local MJPEG network stream
(LIVE, then disconnect → reconnecting), device errors, remote-control refusal
the Streamlit tiling copy, and (release 3.0) `/system/status`, stored
original previews, measured step timings, categories, shadow sample regions,
report rebuild reflecting review, JSON export, dashboard filters, map data
only from real positions, sample listing, history clear deleting previews,
migration of a 2.0 database and the new Streamlit layout. These are
**software tests**; no physical sonar was connected.

## 10. Troubleshooting

| Problem | Fix |
|---|---|
| `start_app.bat` says Python not found | Install Python 3.12 from python.org with "Add to PATH", reopen the terminal. |
| Port 8001 busy | Edit `PORT` in `start_app.bat`, or `PORT=8010 ./start_app.sh`. |
| "Backend is not reachable" banner | The server window was closed or crashed; restart and read its last lines. |
| Capture card: "Could not open video device" | Close other apps using it (OBS, Teams), try index 1 or 2, check cable/driver. |
| Network stream fails | Open the URL in VLC first. Some devices need `rtsp://user:pass@host/path`. Firewalls must allow the port. |
| No GPS fix over UDP | Check the plotter sends NMEA 0183 (not only NMEA 2000) to this PC's IP and port; watch "sentences accepted / rejected". |
| Serial GPS error | Correct COM port and baud (often 4800 or 38400); only one program may open a port. |
| Raw file rejected | The error states the byte arithmetic — correct width/height/type/header from the device docs. |
| Map area blank | No internet for OpenStreetMap tiles; coordinates are still listed. |
| Slow tiled mode | Expected (one model pass per tile); use Whole image or larger tiles. |
| Dev UI cannot reach API | Start the backend on :8001 or set `VITE_API_URL`; other ports must be added to `CORS_ORIGINS`. |

## 11. Known limitations

* No physical sonar, capture card, RTSP camera or GPS receiver was available;
  those paths were tested with software stand-ins (local MJPEG server, UDP
  sender, NMEA logs) only.
* Proprietary vendor formats are not decoded (§4).
* Shadow, echo contrast and unexplained echoes are unvalidated heuristics;
  side-scan shadow direction is untested.
* The model was trained on 640×640 ARIS-style imagery; accuracy on other
  sonars, ranges or real seabeds is unknown until measured.
* Object geo-positions are rough geometric estimates; side-scan
  georeferencing (layback, altitude, slant-range correction) is not implemented.
* `/metrics` recomputes on the validation split only if the dataset folder is
  present; otherwise it serves `outputs/model-performance/metrics.json`
  (precision 92.7 %, recall 92.8 %, mAP50 94.5 %, mAP50-95 70.7 %).
  Dataset: <https://universe.roboflow.com/vedant-zhoqu/marine-debris-cqnuq/dataset/2>
  (CC BY 4.0) — extract it as `Marine-Debris.v2i.yolov8/` to retrain or re-evaluate.

## 12. What is still needed for a specific sonar model

To add a native, verified adapter (instead of video/export input):

1. Manufacturer, exact model and firmware version.
2. Connection used (Ethernet/USB/serial) and the official protocol or SDK documentation.
3. At least one raw recording captured from that device.
4. The GPS/heading source on the vessel (NMEA over serial/UDP, or position fields in the sonar packets).

`src/sonar_io/vendor_template.py` lists the rules such an adapter must follow
(read-only, real metadata only, original samples preserved, honest `is_live`).
