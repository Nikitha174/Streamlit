import streamlit as st
import google.generativeai as genai

# --- Configure Gemini API Key ---
genai.configure(api_key="AIzaSyBD-mRcr8fdbHOulRB-krRs7efQlntATRY")
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Streamlit Page Settings ---
st.set_page_config(page_title="🎯 Goal Tracker", layout="centered")

# --- Light / Dark Theme Toggle ---
theme = st.radio("Choose Theme", ["🌞 Light Mode", "🌙 Dark Mode"], horizontal=True)

# --- Apply Themed CSS ---
if theme == "🌞 Light Mode":
    bg_gradient = "linear-gradient(to right, #e0f7fa, #fce4ec)"
    card_color = "#ffffffdd"
    text_color = "#006064"
else:
    bg_gradient = "linear-gradient(to right, #232526, #414345)"
    card_color = "#333333cc"
    text_color = "#484444"

# --- Inject CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
        background: {bg_gradient};
        color: {text_color};
    }}

    .stTextInput>div>div>input, .stSelectbox>div>div {{
        border: 2px solid #ff80ab;
        border-radius: 10px;
        padding: 10px;
        background-color: #ffffffee;
    }}

    button[kind="primary"] {{
        background-color: #ff4081;
        color: white;
        border-radius: 10px;
        font-weight: 600;
        border: none;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }}

    button[kind="primary"]:hover {{
        background-color: #ec407a;
        transform: scale(1.03);
    }}

    .custom-card {{
        background-color: {card_color};
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        margin-top: 20px;
        animation: fadeIn 1s ease-in;
    }}

    .emoji-animate {{
        display: inline-block;
        animation: bounce 1.2s infinite;
    }}

    @keyframes bounce {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-5px); }}
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; }}
      to {{ opacity: 1; }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- UI ---
st.title("🎯 Goal Tracker with Motivational Quotes")
st.markdown("Get your daily dose of **inspiration** and **progress tips** tailored to your personal goals ✨")

goal = st.text_input("💡 What's your personal goal?", placeholder="e.g., Master Python, Lose weight, Get a new job")
goal_type = st.selectbox("📌 Select Goal Type", ["Health", "Career", "Education", "Personal Development", "Other"])

if st.button("Get Daily Tip & Quote 🚀") and goal.strip():
    with st.spinner("Gemini is crafting your inspiration..."):
        prompt = f"""
        I am working on this goal: '{goal}' under the category '{goal_type}'.

        Please give:
        1. A practical and motivating daily tip.
        2. A short, uplifting motivational quote with fitting emojis.

        Style should be personalized, friendly, and inspiring.
        """
        try:
            response = model.generate_content(prompt)
            # Wrap output in a styled card
            st.markdown(f"<div class='custom-card'>{response.text}</div>", unsafe_allow_html=True)
            st.markdown("<p class='emoji-animate'>✨🔥🚀</p>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"⚠️ Gemini API Error: {str(e)}")

elif goal == "":
    st.info("Type your goal above to begin 💡")
