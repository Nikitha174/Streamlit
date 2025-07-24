import streamlit as st
import pdfplumber
import docx
import io
import re
import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# --------------------------- Helper Functions ---------------------------

def extract_text(file):
    file_extension = file.name.split(".")[-1].lower()
    text = ""

    if file_extension == "pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif file_extension == "docx":
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
    elif file_extension == "txt":
        text = file.read().decode("utf-8")
    else:
        st.error("Unsupported file format. Please upload a PDF, DOCX, or TXT.")
    
    return text.strip()

def analyze_resume(text):
    analysis = {}
    doc = nlp(text.lower())

    analysis["word_count"] = len(text.split())
    analysis["has_skills"] = "skills" in text.lower()
    analysis["has_education"] = "education" in text.lower()
    analysis["has_experience"] = "experience" in text.lower()
    
    # Passive voice detection
    passive_sentences = [
        sent.text for sent in doc.sents if any(tok.dep_ == "auxpass" for tok in sent)
    ]
    analysis["passive_count"] = len(passive_sentences)

    # Suggestions
    suggestions = []
    if not analysis["has_skills"]:
        suggestions.append("Add a **Skills** section with relevant tools or programming languages.")
    if not analysis["has_experience"]:
        suggestions.append("Include a **Work Experience** section to highlight your roles.")
    if analysis["passive_count"] > 3:
        suggestions.append("Reduce the use of **passive voice** to make your resume more active and impactful.")
    if analysis["word_count"] < 150:
        suggestions.append("Your resume seems short. Consider elaborating on your achievements.")
    if "hardworking" in text.lower() or "team player" in text.lower():
        suggestions.append("Avoid clichés like **'hardworking'** or **'team player'**; use specific accomplishments instead.")
    
    analysis["suggestions"] = suggestions
    analysis["score"] = 100 - len(suggestions) * 10

    return analysis

# --------------------------- Streamlit UI ---------------------------

st.set_page_config(layout="wide", page_title="📄 Resume Analyzer")

st.title("📄 AI-Powered Resume Analyzer")
st.markdown("Upload your resume to get instant feedback and suggestions to improve it.")

with st.sidebar:
    st.header("Upload Your Resume")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])

if uploaded_file:
    resume_text = extract_text(uploaded_file)
    analysis_result = analyze_resume(resume_text)

    st.subheader("📃 Extracted Resume Text")
    with st.expander("Click to view extracted content"):
        st.write(resume_text)

    st.subheader("🔍 Resume Analysis")
    st.markdown(f"**Word Count:** {analysis_result['word_count']}")
    st.markdown(f"**Passive Voice Sentences:** {analysis_result['passive_count']}")

    st.progress(analysis_result["score"] / 100)
    st.markdown(f"**Resume Score:** {analysis_result['score']} / 100")

    st.subheader("✅ Key Sections Found")
    st.write("✅ Skills Section" if analysis_result["has_skills"] else "❌ Skills Section Missing")
    st.write("✅ Education Section" if analysis_result["has_education"] else "❌ Education Section Missing")
    st.write("✅ Experience Section" if analysis_result["has_experience"] else "❌ Experience Section Missing")

    st.subheader("💡 Suggestions for Improvement")
    if analysis_result["suggestions"]:
        for idx, suggestion in enumerate(analysis_result["suggestions"], 1):
            st.warning(f"{idx}. {suggestion}")
    else:
        st.success("Your resume looks great! No major issues found.")

else:
    st.info("Please upload a resume file to begin analysis.")

