from pathlib import Path
from io import BytesIO
import hashlib
import time

import numpy as np
import streamlit as st
from PIL import Image
from ultralytics import YOLO


# ---------- Page setup ----------
st.set_page_config(
    page_title="AquaScan AI | Marine Debris Detection",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_PATH = Path(__file__).parent / "best.pt"


# ---------- Custom styling ----------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: #f3f7fb;
    color: #152238;
}
[data-testid="stHeader"] {
    background: transparent;
}
.block-container {
    max-width: 1240px;
    padding: 2rem 2.5rem 3rem;
}
[data-testid="stSidebar"] {
    background: #0c1728;
}
[data-testid="stSidebar"] * {
    color: #e7eef8;
}
.hero {
    padding: 30px 34px;
    margin-bottom: 24px;
    border-radius: 24px;
    color: white;
    background: linear-gradient(115deg, #0b1728 0%, #123c53 64%, #087e8b 100%);
    box-shadow: 0 16px 40px rgba(15, 35, 60, .16);
}
.hero-badge {
    display: inline-block;
    padding: 6px 11px;
    border: 1px solid rgba(255,255,255,.25);
    border-radius: 999px;
    color: #b9f3ed;
    background: rgba(255,255,255,.08);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: .08em;
}
.hero h1 {
    margin: 16px 0 7px;
    color: white;
    font-size: clamp(32px, 5vw, 48px);
    line-height: 1.05;
}
.hero p {
    max-width: 720px;
    margin: 0;
    color: #d5e5ef;
    font-size: 16px;
}
.guide-card {
    min-height: 185px;
    padding: 22px;
    border: 1px solid #dce7f0;
    border-radius: 18px;
    background: white;
    color: #34445a;
    line-height: 1.7;
}
.guide-card strong {
    color: #10263b;
    font-size: 17px;
}
[data-testid="stMetric"] {
    padding: 17px;
    border: 1px solid #e0e9f1;
    border-radius: 16px;
    background: white;
    box-shadow: 0 5px 18px rgba(20, 40, 65, .04);
}
[data-testid="stFileUploaderDropzone"] {
    border: 1.5px dashed #6db9c4;
    border-radius: 16px;
    background: #f8fcff;
}
[data-testid="stFileUploaderDropzone"] * {
    color: #294057 !important;
}
.stButton > button,
[data-testid="stDownloadButton"] button {
    min-height: 46px;
    border: 0;
    border-radius: 12px;
    color: white;
    background: linear-gradient(100deg, #087e8b, #10a6a0);
    font-weight: 700;
}
.stButton > button:hover,
[data-testid="stDownloadButton"] button:hover {
    border: 0;
    color: white;
    background: linear-gradient(100deg, #076b78, #088e89);
}
[data-testid="stTabs"] button {
    font-weight: 700;
}
hr {
    border-color: #dfe8ef;
}
.small-muted {
    color: #64748b;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)


# ---------- Load model once and cache it ----------
@st.cache_resource(show_spinner=False)
def load_model(model_path):
    return YOLO(model_path)


# ---------- Sidebar controls ----------
with st.sidebar:
    st.markdown(
        "<div style='font-size:25px;font-weight:800;margin:8px 0 0'>🌊 AquaScan</div>"
        "<div style='font-size:11px;letter-spacing:.12em;color:#9cb1c7'>AI MONITORING STUDIO</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### Detection controls")
    st.caption("Adjust these before running the model.")

    confidence = st.slider(
        "Confidence threshold",
        min_value=0.10,
        max_value=0.90,
        value=0.25,
        step=0.05,
        help="Higher confidence can reduce weak detections.",
    )

    image_size = st.select_slider(
        "Image processing size",
        options=[320, 480, 640, 800, 1024],
        value=640,
    )

    st.markdown("---")
    if MODEL_PATH.exists():
        st.markdown("🟢 **Model weights found**")
    else:
        st.markdown("🔴 **`best.pt` is missing**")

    st.markdown("---")
    st.caption("AquaScan AI · Marine debris detection")


# ---------- Header ----------
st.markdown("""
<div class="hero">
    <span class="hero-badge">SMART OCEAN MONITORING · SIH PROJECT</span>
    <h1>See the unseen beneath the surface.</h1>
    <p>Upload an image and let AquaScan AI identify potential marine debris
    with computer vision.</p>
</div>
""", unsafe_allow_html=True)


# ---------- Upload panel ----------
upload_col, guide_col = st.columns([1.45, 1], gap="large")

with upload_col:
    st.markdown("### 01 &nbsp; Upload an image")
    uploaded_file = st.file_uploader(
        "Drag an image here or browse your device",
        type=["jpg", "jpeg", "png"],
        help="Supported formats: JPG and PNG",
    )

with guide_col:
    st.markdown("""
    <div class="guide-card">
        <strong>How it works</strong><br>
        1. Upload an underwater or marine image.<br>
        2. Adjust the detection confidence if needed.<br>
        3. Run the analysis and review the marked objects.<br>
        4. Download the annotated result.
    </div>
    """, unsafe_allow_html=True)


# ---------- Keep results visible across Streamlit reruns ----------
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    st.image(Image.open(BytesIO(file_bytes)), caption=f"Uploaded: {uploaded_file.name}")
    current_hash = hashlib.sha256(file_bytes).hexdigest()

    if st.session_state.get("uploaded_hash") != current_hash:
        st.session_state["uploaded_hash"] = current_hash
        st.session_state["analysis_result"] = None

    st.markdown(
        f"<div class='small-muted'>Selected file: <b>{uploaded_file.name}</b></div>",
        unsafe_allow_html=True,
    )

    if st.button("🔍  Analyze image", type="primary", use_container_width=True):
        if not MODEL_PATH.exists():
            st.error("Model file `best.pt` was not found beside `app.py`.")
        else:
            try:
                with st.spinner("AquaScan AI is analyzing the image..."):
                    original = Image.open(BytesIO(file_bytes)).convert("RGB")
                    original_rgb = np.array(original)
                    # YOLO accepts OpenCV-style BGR arrays.
                    image_bgr = np.ascontiguousarray(original_rgb[:, :, ::-1])

                    start_time = time.perf_counter()
                    model = load_model(str(MODEL_PATH))
                    prediction = model.predict(
                        source=image_bgr,
                        imgsz=int(image_size),
                        conf=float(confidence),
                        verbose=False,
                    )[0]
                    elapsed = time.perf_counter() - start_time

                    # YOLO's plot output is BGR; convert it for the browser.
                    annotated_rgb = np.ascontiguousarray(
                        prediction.plot()[:, :, ::-1]
                    )

                    names = model.names
                    rows = []
                    confidence_scores = []

                    if prediction.boxes is not None:
                        for box in prediction.boxes:
                            class_id = int(box.cls[0].item())
                            score = float(box.conf[0].item())
                            coords = box.xyxy[0].cpu().tolist()

                            if isinstance(names, dict):
                                label = names.get(class_id, f"Class {class_id}")
                            else:
                                label = names[class_id]

                            rows.append({
                                "Detected object": label,
                                "Confidence": f"{score:.1%}",
                                "Bounding box": ", ".join(
                                    str(round(value)) for value in coords
                                ),
                            })
                            confidence_scores.append(score)

                    st.session_state["analysis_result"] = {
                        "original": original_rgb,
                        "annotated": annotated_rgb,
                        "rows": rows,
                        "scores": confidence_scores,
                        "elapsed": elapsed,
                    }

            except Exception as error:
                st.error(f"Analysis failed: {error}")


# ---------- Results dashboard ----------
analysis = st.session_state.get("analysis_result")

if analysis:
    st.markdown("---")
    st.markdown("### 02 &nbsp; Analysis results")

    rows = analysis["rows"]
    scores = analysis["scores"]
    object_count = len(rows)
    class_count = len({row["Detected object"] for row in rows})
    average_confidence = (sum(scores) / len(scores)) if scores else 0

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Objects detected", object_count)
    metric2.metric("Unique classes", class_count)
    metric3.metric("Average confidence", f"{average_confidence:.1%}")
    metric4.metric("Processing time", f"{analysis['elapsed']:.2f}s")

    preview_tab, details_tab = st.tabs(["🖼️  Image preview", "📋  Detection details"])

    with preview_tab:
        original_col, result_col = st.columns(2, gap="large")
        with original_col:
            st.markdown("#### Original image")
            st.image(analysis["original"], use_container_width=True)
        with result_col:
            st.markdown("#### AquaScan detection")
            st.image(analysis["annotated"], use_container_width=True)

        image_buffer = BytesIO()
        Image.fromarray(analysis["annotated"]).save(image_buffer, format="PNG")

        st.download_button(
            "⬇️  Download annotated image",
            data=image_buffer.getvalue(),
            file_name="aquascan_detection.png",
            mime="image/png",
            use_container_width=True,
        )

    with details_tab:
        if rows:
            st.dataframe(
                rows,
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info(
                "No objects were detected at this confidence threshold. "
                "Try lowering the threshold in the sidebar."
            )
else:
    st.markdown("---")
    st.info("Upload an image above, then click **Analyze image** to see results.")
