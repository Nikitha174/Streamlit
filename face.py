import streamlit as st
import cv2
import numpy as np
from datetime import datetime
from PIL import Image

# ------------------- App Config -----------------------
st.set_page_config(page_title="🧠 Face Detection App", layout="wide")

# ------------------- Title -----------------------
st.markdown("""
    <h1 style='text-align: center; color: #4B0082;'>🔍 Face Detection with OpenCV</h1>
    <p style='text-align: center;'>Choose webcam or upload a video | Switch between Haar and DNN | Adjust detection</p>
    <hr>
""", unsafe_allow_html=True)

# ------------------- Sidebar -----------------------
st.sidebar.header("🛠️ Settings")

mode = st.sidebar.radio("Choose Input Mode", ["Webcam", "Upload Video"])

model_type = st.sidebar.selectbox("Choose Detection Model", ["Haar Cascade", "DNN (SSD)"])

scale_factor = st.sidebar.slider("Scale Factor (Haar Only)", 1.01, 1.5, 1.1, 0.01)
min_neighbors = st.sidebar.slider("Min Neighbors (Haar Only)", 1, 10, 5)

confidence_threshold = st.sidebar.slider("Confidence Threshold (DNN Only)", 0.1, 1.0, 0.5)

st.sidebar.markdown("---")
st.sidebar.info("📌 Real-time face detection using OpenCV.\n\nAdjust detection parameters for better results.")

# ------------------- Load Models -----------------------

haar_model = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

dnn_model_path = {
    "proto": "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt",
    "weights": "https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
}

@st.cache_resource
def load_dnn_model():
    net = cv2.dnn.readNetFromCaffe(dnn_model_path["proto"], dnn_model_path["weights"])
    return net

# ------------------- Detection Functions -----------------------

def detect_faces_haar(frame, scale, neighbors):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = haar_model.detectMultiScale(gray, scale, neighbors)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return frame, len(faces)

def detect_faces_dnn(frame, net, conf_threshold):
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                 (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()
    count = 0
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            count += 1
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
    return frame, count

# ------------------- Video Processing -----------------------

def process_video(video_source):
    if model_type == "DNN (SSD)":
        net = load_dnn_model()

    cap = cv2.VideoCapture(video_source)

    stframe = st.empty()
    face_counter = st.empty()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if model_type == "Haar Cascade":
            processed_frame, face_count = detect_faces_haar(frame, scale_factor, min_neighbors)
        else:
            processed_frame, face_count = detect_faces_dnn(frame, net, confidence_threshold)

        face_counter.info(f"🧑‍🤝‍🧑 Faces Detected: {face_count}")
        frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        stframe.image(frame_rgb, channels="RGB", use_column_width=True)

    cap.release()

# ------------------- Main -----------------------

if mode == "Upload Video":
    uploaded_file = st.file_uploader("📤 Upload a Video", type=["mp4", "mov", "avi"])
    if uploaded_file:
        tfile = f"temp_video_{datetime.now().strftime('%H%M%S')}.mp4"
        with open(tfile, 'wb') as f:
            f.write(uploaded_file.read())
        process_video(tfile)

elif mode == "Webcam":
    st.warning("⚠️ Allow camera access when prompted. Press 'Stop' button to exit.")
    process_video(0)

# ------------------- Footer -----------------------
st.markdown("""
    <hr>
    <div style="text-align: center;">
        <small>Made with ❤️ using OpenCV + Streamlit</small>
    </div>
""", unsafe_allow_html=True)
