import streamlit as st
import PyPDF2
import re
from collections import Counter

# --- REMOVED SPACY ---
# Replacing NLP summary with a basic Python logic to avoid deployment errors
def simple_summary(text, max_sentences=5):
    # Split text into sentences based on common punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Filter out very short lines/junk
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    # Return the first few relevant sentences
    return "\n".join(sentences[:max_sentences])

st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded",
)

BACKGROUND_IMAGE_URL = "https://d31kzl7c7thvlu.cloudfront.net/image/BG-image.jpg"

st.markdown(
    f"""
    <style>
    .stApp {{background-image: url('{BACKGROUND_IMAGE_URL}'); background-size: cover; background-position: center;}}
    .stMarkdown h1 {{color: #32a88d;}}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# 📄 Resume Analyzer")
st.markdown("Upload a PDF resume and get a match to a best-fit role based on keyword scores.")

jobs = {
    "Data Scientist": ["python", "machine learning", "pandas", "numpy", "data analysis"],
    "Web Developer": ["html", "css", "javascript", "react", "node"],
    "Android Developer": ["java", "kotlin", "android"],
    "Cyber Security Analyst": ["network", "security", "cryptography", "ethical hacking"],
    "DevOps Engineer": ["docker", "kubernetes", "ci/cd", "aws", "terraform"],
    "Business Analyst": ["requirements", "stakeholder", "excel", "uml", "data visualization"],
}

def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.lower()

def match_job(text):
    scores = {}
    hit_skills = {}
    for role, skills in jobs.items():
        this_score = 0
        found = []
        for skill in skills:
            if skill in text:
                this_score += 2
                found.append(skill)
            else:
                for token in skill.split():
                    if token in text:
                        this_score += 1
                        found.append(token)
        scores[role] = this_score
        hit_skills[role] = found
    best = max(scores, key=scores.get)
    return best, scores, hit_skills

def extract_years_of_experience(text):
    year_patterns = re.findall(r"(\d{4})", text)
    current_year = 2026
    got = [int(y) for y in year_patterns if 1980 <= int(y) <= current_year]
    if not got:
        return None
    return current_year - min(got)

def keyword_density(text):
    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    total = len(words)
    counts = Counter(words)
    return total, counts.most_common(15)

def ats_score(text, best_role):
    required = jobs.get(best_role, [])
    found = [skill for skill in required if skill in text]
    if not required: return 0
    base_score = int(len(found) / len(required) * 100)
    bonus = min(10, sum(1 for word in ["lead", "managed", "delivered"] if word in text))
    return min(100, base_score + bonus)

with st.sidebar:
    st.header("Instructions")
    st.write("- Upload a PDF\n- View Scores\n- Add Custom Roles")
    show_details = st.checkbox("Show detected keywords", True)
    show_summary = st.checkbox("Show Summary", True)
    show_missing = st.checkbox("Show missing key skills", True)

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

if uploaded_file:
    st.success("Resume uploaded successfully!")
    resume_text = extract_text(uploaded_file)
    if not resume_text.strip():
        st.warning("No text found in this resume.")
    else:
        best_job, scores, hit_skills = match_job(resume_text)
        st.subheader("🎯 Recommended Job Role")
        st.info(f"*{best_job}*")

        if show_summary:
            st.subheader("📝 Resume Summary")
            st.write(simple_summary(resume_text))

        st.subheader("📊 Matching Scores")
        st.bar_chart(scores)

        if show_missing:
            st.subheader("⚠️ Missing skills for " + best_job)
            missing = [skill for skill in jobs[best_job] if skill not in hit_skills[best_job]]
            st.write(", ".join(missing) if missing else "None!")

        years_exp = extract_years_of_experience(resume_text)
        if years_exp:
            st.subheader(f"📈 Experience: ~{years_exp} years")

        st.subheader("🧾 ATS Score")
        score = ats_score(resume_text, best_job)
        st.progress(score / 100)
        st.write(f"Score: {score}/100")
        f"Role Scores: {scores}\n"
        f"Top keywords: {', '.join([f'{w} ({c})' for w,c in top_keywords])}\n"
        )
        if st.button("Download Analysis Report"):
            st.download_button("Download report TXT", report_text, file_name="resume_analysis.txt", mime="text/plain")
