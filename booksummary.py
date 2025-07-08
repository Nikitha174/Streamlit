import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF

# 🔐 Gemini API setup
genai.configure(api_key="AIzaSyABazGJuibvYz0tfoKwtCqYMxc6VTP9-Vk")
model = genai.GenerativeModel("gemini-2.0-flash")

# 🎨 Page config
st.set_page_config(page_title="📚 Book Summarizer", layout="centered")

# 💅 Multicoloured Custom CSS
st.markdown("""
    <style>
        body, .stApp {
            background-color: #e6ccff;  /* Light lavender */
            font-family: 'Segoe UI', sans-serif;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 850px;
            margin: auto;
        }

        h1 {
            text-align: center;
            font-size: 3rem;
            font-weight: 900;
            color: #0072ff;
            margin-bottom: 0.2rem;
        }

        .stRadio > div {
            color: #333;
            font-weight: 500;
        }

        .stTextArea textarea {
            background-color: #ffffff;
            color: #333;
            border-radius: 10px;
            border: 1px solid #ccc;
            font-size: 15px;
            padding: 12px;
        }

        .stFileUploader label {
            color: #0072ff;
            font-weight: 600;
        }

        .summary-box {
            background-color: #ffffff;
            border: 1px solid #ddd;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            color: #222;
            line-height: 1.6;
        }

        .stButton button {
            background: linear-gradient(to right, #ff758c, #ff7eb3);
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.4rem;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .stButton button:hover {
            transform: scale(1.05);
            background: linear-gradient(to right, #ff8fa3, #ffa8c7);
        }

        .stMarkdown h3 {
            color: #003366;
            border-bottom: 1px solid #ddd;
            padding-bottom: 4px;
        }
    </style>
""", unsafe_allow_html=True)


# 🌟 Title
st.markdown("<h1>📘 Book Chapter Summarizer</h1>", unsafe_allow_html=True)
st.markdown("Summarize book chapters using <b>Gemini 2.0 Flash AI</b> ✨", unsafe_allow_html=True)

# 📅 Input type
input_method = st.radio("📄 Choose your input type:", ["Upload File", "Paste Text"])
uploaded_file = None
text_input = ""

# 🧾 File or text input
if input_method == "Upload File":
    uploaded_file = st.file_uploader("📁 Upload a PDF or TXT file", type=["pdf", "txt"])
else:
    text_input = st.text_area("📝 Paste your chapter content here:", height=250)

# 🔍 Extract text from file
def extract_text(file):
    try:
        if file.name.endswith(".pdf"):
            with fitz.open(stream=file.read(), filetype="pdf") as doc:
                return "\n".join([page.get_text() for page in doc])
        elif file.name.endswith(".txt"):
            return file.read().decode("utf-8")
        else:
            return ""
    except Exception as e:
        st.error(f"❌ Error extracting text: {e}")
        return ""

# 🧠 Build prompt
def build_prompt(content):
    return f"""
Please summarize the following book chapter. Return:
1. A short summary (max 5 sentences)
2. 3 to 5 key takeaways in bullet points
3. 5 relevant tags

Content:
\"\"\"{content}\"\"\"
"""

# 🎯 Generate summary
if st.button("🚀 Generate Summary"):
    content = ""
    if input_method == "Upload File" and uploaded_file:
        content = extract_text(uploaded_file)
    elif input_method == "Paste Text" and text_input.strip():
        content = text_input.strip()
    else:
        st.warning("⚠️ Please upload a file or paste some text.")
        st.stop()

    if len(content) > 8000:
        st.warning("⚠️ Content too long. Please limit to 8000 characters.")
        st.stop()

    with st.spinner("🧐 Thinking..."):
        try:
            prompt = build_prompt(content)
            response = model.generate_content(prompt)
            st.success("✅ Summary generated!")

            st.markdown("### 📄 Summary Output")
            st.markdown(f"<div class='summary-box'>{response.text}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Gemini API Error: {e}")
