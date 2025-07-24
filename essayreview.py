import streamlit as st
import requests
import datetime

# ✅ Your n8n Webhook URL
WEBHOOK_URL = "https://nikithaks.app.n8n.cloud/webhook-test/essaysubmission"  # Replace if needed

# 📋 Page setup
st.set_page_config(page_title="Essay Submission Portal", layout="centered")

# 🎨 CSS styling
st.markdown("""
    <style>
    body {
        background-color: #d6eaff;
    }
    .stApp {
        background-color: #fefeff;
        border-radius: 12px;
        padding: 2rem;
        max-width: 700px;
        margin: auto;
        box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.05);
    }
    .header {
        background: linear-gradient(to right, #4c8bf5, #6ba9f7);
        padding: 1rem 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    .sub {
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 2rem;
        color: #444;
    }
    .stTextInput > label, .stSelectbox > label, .stTextArea > label {
        font-weight: 600;
        color: #2c3e50;
        font-size: 1rem;
    }
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px !important;
    }
    button[kind=primary] {
        background: linear-gradient(to right, #4c8bf5, #6499ff);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        padding: 0.5rem 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# 📝 Title section
st.markdown('<div class="header">📚 Essay Submission Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Submit your essay securely. Your mentor will be notified. ✍️</div>', unsafe_allow_html=True)

# 📄 Form
with st.form("essay_form", clear_on_submit=True):
    st.markdown("### 👤 Student Details")
    student_name = st.text_input("Student Name")
    student_email = st.text_input("Student Email")
    mentor_email = st.text_input("Mentor's Email")

    st.markdown("---")
    st.markdown("### 📝 Your Essay")
    essay_text = st.text_area("Paste your essay here")

    submitted = st.form_submit_button("📤 Submit Essay")

# ✅ Submit handler
if submitted:
    if not student_name or not student_email or not mentor_email or not essay_text:
        st.warning("⚠ All fields are required.")
    else:
        data = {
            "student_name": student_name,
            "student_email": student_email,
            "mentor_email": mentor_email,
            "essay": essay_text,
            "timestamp": datetime.datetime.now().isoformat()
        }

        try:
            response = requests.post(WEBHOOK_URL, json=data)
            if response.status_code == 200:
                st.success("✅ Essay submitted successfully! Your mentor will be notified.")
            else:
                st.error(f"⚠ Failed to submit. Status code: {response.status_code}")
                st.json(response.json())
        except Exception as e:
            st.error("❌ Error connecting to the webhook.")
            st.code(str(e))
