import streamlit as st
import PyPDF2
import re
from collections import Counter

# --- TEXT PROCESSING FUNCTIONS ---

def simple_summary(text, max_sentences=5):
    """Splits text into sentences and returns the first few for a summary."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 25]
    return "\n".join(sentences[:max_sentences])

def extract_text(file):
    """Reads PDF and converts to lowercase text."""
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.lower()

def extract_years_of_experience(text):
    """Finds 4-digit years to estimate experience."""
    year_patterns = re.findall(r"(\d{4})", text)
    current_year = 2026
    years = [int(y) for y in year_patterns if 1980 <= int(y) <= current_year]
    if not years:
        return None
    return current_year - min(years)

# --- CONFIGURATION ---

st.set_page_config(
    page_title="Resume Analyzer Pro",
    page_icon="📄",
    layout="centered",
)

# Custom Styling
BACKGROUND_IMAGE_URL = "https://d31kzl7c7thvlu.cloudfront.net/image/BG-image.jpg"
st.markdown(
    f"""
    <style>
    .stApp {{background-image: url('{BACKGROUND_IMAGE_URL}'); background-size: cover; background-position: center;}}
    .stMarkdown h1 {{color: #32a88d;}}
    .stInfo {{background-color: rgba(50, 168, 141, 0.1); border-left: 5px solid #32a88d;}}
    </style>
    """,
    unsafe_allow_html=True,
)

# Job Database
jobs = {
    "Data Scientist": ["python", "machine learning", "pandas", "numpy", "data analysis", "sql", "scikit-learn"],
    "Web Developer": ["html", "css", "javascript", "react", "node", "typescript", "mongodb"],
    "Android Developer": ["java", "kotlin", "android studio", "firebase", "xml"],
    "Cyber Security Analyst": ["network", "security", "cryptography", "ethical hacking", "firewall", "linux"],
    "DevOps Engineer": ["docker", "kubernetes", "ci/cd", "aws", "terraform", "jenkins", "ansible"],
    "Business Analyst": ["requirements", "stakeholder", "excel", "uml", "data visualization", "tableau", "jira"],
}

# --- LOGIC FUNCTIONS ---

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
                    if token in text and len(token) > 2:
                        this_score += 1
                        found.append(token)
        scores[role] = this_score
        hit_skills[role] = list(set(found))
    best = max(scores, key=scores.get)
    return best, scores, hit_skills

def ats_score(text, best_role):
    required = jobs.get(best_role, [])
    found = [skill for skill in required if skill in text]
    if not required: return 0
    base = int(len(found) / len(required) * 100)
    bonus = min(10, sum(1 for word in ["lead", "managed", "developed", "delivered"] if word in text))
    return min(100, base + bonus)

# --- SIDEBAR ---

with st.sidebar:
    st.header("⚙️ Settings")
    show_details = st.checkbox("Show Detected Keywords", True)
    show_summary = st.checkbox("Show NLP Summary", True)
    show_missing = st.checkbox("Show Missing Skills", True)
    st.divider()
    st.write("Tip: Upload your PDF to see which career path fits your skills best.")

# --- MAIN UI ---

st.markdown("# 📄 AI Resume Analyzer")
st.write("Analyze your resume's compatibility with industry roles and optimize for ATS.")

uploaded_file = st.file_uploader("Upload your Resume (PDF format)", type=["pdf"])

if uploaded_file:
    with st.spinner("Analyzing your profile..."):
        resume_text = extract_text(uploaded_file)
        
        if not resume_text.strip():
            st.error("Could not extract text. Please ensure the PDF is not a scanned image.")
        else:
            best_job, scores, hit_skills = match_job(resume_text)
            
            # 1. Recommended Role
            st.subheader("🎯 Best Fit Career Path")
            st.info(f"Based on your profile, you are a strong candidate for: **{best_job}**")

            # 2. Detected Keywords (NEW)
            if show_details:
                st.subheader("🧠 Detected Professional Keywords")
                words = re.findall(r"\b[a-z]{3,}\b", resume_text.lower())
                stop_words = {'the', 'and', 'for', 'with', 'from', 'this', 'that', 'have', 'was', 'project', 'experience'}
                unique_keywords = sorted({w for w in words if w not in stop_words and len(w) > 3})
                st.write(", ".join(unique_keywords[:50])) # Shows top 50 unique words

            # 3. Summary
            if show_summary:
                st.subheader("📝 Profile Summary")
                st.write(simple_summary(resume_text))

            # 4. Matching Chart
            st.subheader("📊 Role Match Strength")
            st.bar_chart(scores)

            # 5. Missing Skills
            if show_missing:
                st.subheader(f"⚠️ Skills to add for {best_job}")
                missing = [s for s in jobs[best_job] if s not in hit_skills[best_job]]
                if missing:
                    st.write("Consider adding these keywords to your resume:")
                    st.warning(", ".join(missing))
                else:
                    st.success("Perfect match! Your resume covers all core skills for this role.")

            # 6. Experience & ATS
            col1, col2 = st.columns(2)
            
            with col1:
                years = extract_years_of_experience(resume_text)
                st.subheader("📈 Experience")
                if years:
                    st.metric("Estimated", f"{years} Years")
                else:
                    st.write("No date patterns found.")

            with col2:
                score = ats_score(resume_text, best_job)
                st.subheader("🧾 ATS Score")
                st.metric("Compatibility", f"{score}%")
                st.progress(score / 100)

            # 7. Export
            st.divider()
            report = f"Resume Analysis Report\nRecommended Role: {best_job}\nATS Score: {score}%\nExperience: {years} years"
            st.download_button("Download Analysis Report", report, file_name="analysis.txt")
