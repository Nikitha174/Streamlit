import streamlit as st
import cv2
import numpy as np
from PIL import Image

# ----------------------------- FILTER FUNCTIONS -----------------------------

def apply_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def apply_sepia(image):
    kernel = np.array([[0.272, 0.534, 0.131],
                       [0.349, 0.686, 0.168],
                       [0.393, 0.769, 0.189]])
    sepia_image = cv2.transform(image, kernel)
    return np.clip(sepia_image, 0, 255).astype(np.uint8)

def apply_blur(image, kernel_size=15):
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

def apply_cartoon(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray_blur, 255,
                                  cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(image, 9, 250, 250)
    return cv2.bitwise_and(color, color, mask=edges)

# ----------------------------- CSS STYLING -----------------------------

st.markdown("""
    <style>
        body {
            background: linear-gradient(to right, #e0c3fc, #8ec5fc);
        }
        .main {
            background: linear-gradient(to bottom right, #ffffffcc, #f8f9ffc7);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        .title {
            text-align: center;
            font-size: 3em;
            font-weight: bold;
            background: linear-gradient(to right, #ff6ec4, #7873f5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        .stButton>button {
            background-color: #7873f5;
            color: white;
            font-weight: bold;
            border-radius: 12px;
            padding: 0.5em 1em;
            transition: 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #5a52d1;
            transform: scale(1.05);
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------- APP UI -----------------------------

st.markdown('<h1 class="title">📸 Photo Filters App</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Upload or capture a photo and apply cool visual filters instantly!</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 Upload an image", type=["jpg", "jpeg", "png"])
capture_image = st.camera_input("📸 Or take a photo")

input_image = None
if uploaded_file:
    input_image = Image.open(uploaded_file)
elif capture_image:
    input_image = Image.open(capture_image)

if input_image:
    image_np = np.array(input_image.convert("RGB"))
    image_cv2 = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    filter_option = st.selectbox("🎨 Choose a filter to apply:",
                                 ["None", "Grayscale", "Sepia", "Blur", "Cartoon"])

    if filter_option == "None":
        output_image = image_cv2
    elif filter_option == "Grayscale":
        gray_img = apply_grayscale(image_cv2)
        output_image = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
    elif filter_option == "Sepia":
        output_image = apply_sepia(image_cv2)
    elif filter_option == "Blur":
        output_image = apply_blur(image_cv2)
    elif filter_option == "Cartoon":
        output_image = apply_cartoon(image_cv2)

    output_rgb = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)

    st.markdown("### 🖼️ Preview")
    col1, col2 = st.columns(2)
    with col1:
        st.image(input_image, caption="Original", use_column_width=True)
    with col2:
        st.image(output_rgb, caption=f"{filter_option} Filter", use_column_width=True)

    st.download_button(
        label="💾 Download Filtered Image",
        data=Image.fromarray(output_rgb).convert("RGB").tobytes("raw", "RGB"),
        file_name="filtered_image.png",
        mime="image/png"
    )
else:
    st.info("👆 Upload or capture an image to begin.")
