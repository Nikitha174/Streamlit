import streamlit as st
import google.generativeai as genai
import pandas as pd

# ------------------ Configure Gemini 1.5 Flash ------------------
genai.configure(api_key="AIzaSyA8VuHfXaj_HZ5-kHxk94vCf4r07X4lfoo")  # Replace with your Gemini API key
model = genai.GenerativeModel('gemini-1.5-flash')

# ------------------ Session State Initialization ------------------
if "quiz" not in st.session_state:
    st.session_state.quiz = []
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "score" not in st.session_state:
    st.session_state.score = 0
if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = pd.DataFrame(columns=["Name", "Score", "Topic"])
if "answers" not in st.session_state:
    st.session_state.answers = []

# ------------------ Custom CSS ------------------
st.markdown("""
    <style>
        body {
            background: linear-gradient(to right, #ffecd2, #fcb69f);
        }
        .title {
            text-align: center;
            font-size: 3rem;
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
        .correct {
            color: green;
            font-weight: bold;
        }
        .incorrect {
            color: red;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ App Title ------------------
st.markdown('<h1 class="title">🧠 AI Quiz Game</h1>', unsafe_allow_html=True)

# ------------------ User Input ------------------
user_name = st.text_input("👤 Enter your name to begin:", key="user_name")

# ------------------ Topic Selection ------------------
topics = ["C", "Python", "Full Stack", "SQL", "Math", "Space", "Java"]
topic = st.selectbox("📚 Choose a Topic", topics)

# ------------------ Generate Quiz Using Gemini ------------------
def generate_quiz(topic):
    prompt = f"""
    Generate exactly 3 multiple-choice questions about {topic}.
    Each question should have 4 options labeled A to D, and one correct answer.
    Format like this:

    Q: What is the capital of France?
    A. Berlin
    B. Rome
    C. Madrid
    D. Paris
    Answer: D

    Do NOT include explanations or any extra text.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# ------------------ Parse Gemini Response ------------------
def parse_questions(text):
    questions = []
    blocks = text.strip().split("Q:")
    for block in blocks[1:]:
        lines = block.strip().split("\n")
        if len(lines) < 6:  # ensure question + 4 options + answer
            continue
        q_text = lines[0].strip()
        options = [line[3:].strip() for line in lines[1:5]]
        correct = [line for line in lines if "Answer:" in line][0].split(":")[1].strip()
        questions.append({
            "question": q_text,
            "options": options,
            "correct": correct
        })
    return questions

# ------------------ Start Quiz ------------------
if st.button("🎯 Generate Quiz"):
    if not user_name:
        st.warning("Please enter your name before starting the quiz.")
    else:
        with st.spinner("✨ Generating your quiz..."):
            raw_text = generate_quiz(topic)
            try:
                quiz_data = parse_questions(raw_text)
                if not quiz_data:
                    raise ValueError("Parsing failed.")
                st.session_state.quiz = quiz_data
                st.session_state.submitted = False
                st.session_state.score = 0
                st.session_state.answers = []
            except Exception as e:
                st.error("❌ Failed to generate or parse quiz.")
                st.text(raw_text)

# ------------------ Display Quiz ------------------
if st.session_state.quiz and not st.session_state.submitted:
    st.markdown("### 📝 Answer the Questions:")
    st.session_state.answers = []
    for i, q in enumerate(st.session_state.quiz):
        st.markdown(f"**Q{i+1}: {q['question']}**")
        for j, option in zip(["A", "B", "C", "D"], q["options"]):
            st.markdown(f"{j}. {option}")
        user_choice = st.radio(
            "Choose your answer:",
            ["A", "B", "C", "D"],
            key=f"q_{i}"
        )
        st.session_state.answers.append(user_choice)

    if st.button("✅ Submit Answers"):
        score = 0
        for i, q in enumerate(st.session_state.quiz):
            if st.session_state.answers[i] == q["correct"]:
                score += 1
        st.session_state.score = score
        st.session_state.submitted = True

        # Update leaderboard
        new_score = {"Name": user_name, "Score": score, "Topic": topic}
        st.session_state.leaderboard = pd.concat(
            [st.session_state.leaderboard, pd.DataFrame([new_score])],
            ignore_index=True
        )

# ------------------ Show Results ------------------
if st.session_state.submitted:
    st.success(f"🎉 {user_name}, you scored {st.session_state.score} out of {len(st.session_state.quiz)}!")
    st.balloons()

    for i, q in enumerate(st.session_state.quiz):
        st.markdown(f"**Q{i+1}: {q['question']}**")
        for j, option in zip(["A", "B", "C", "D"], q["options"]):
            option_text = f"{j}. {option}"
            if j == q["correct"] and j == st.session_state.answers[i]:
                st.markdown(f"<div class='correct'>✅ {option_text} (Correct)</div>", unsafe_allow_html=True)
            elif j == st.session_state.answers[i] and j != q["correct"]:
                st.markdown(f"<div class='incorrect'>❌ {option_text} (Your answer)</div>", unsafe_allow_html=True)
            elif j == q["correct"]:
                st.markdown(f"<div class='correct'>✅ {option_text} (Correct Answer)</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"{option_text}")

# ------------------ Leaderboard ------------------
st.markdown("### 🏆 Leaderboard (Top Scores)")
if not st.session_state.leaderboard.empty:
    top_scores = st.session_state.leaderboard.sort_values(by="Score", ascending=False).head(10).reset_index(drop=True)
    st.dataframe(top_scores.style.highlight_max(axis=0), use_container_width=True)
else:
    st.info("No scores yet. Be the first to play!")
