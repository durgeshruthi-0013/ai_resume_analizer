import streamlit as st
import PyPDF2
import re
from collections import Counter

# Replacing spaCy summary with a lightweight Regex-based summary
def simple_summary(text, max_sentences=5):
    # Split text into sentences based on punctuation followed by a space/newline
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Sort by length (shortest first) as your original code did with doc.sents
    sentences = sorted([s.strip() for s in sentences if len(s.strip()) > 10], key=len)
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
    .css-1v3fvcr {{padding: 2rem 1rem 2rem 1rem;}}
    .stButton>button {{border-radius: 10px; background: linear-gradient(135deg, #2563eb, #6366f1); border: none; color: #fff;}}
    .stFileUploader {{border-radius: 12px;}}
    .reportview-container {{background: linear-gradient(145deg, #eff6ff, #f8fafc);}}
    .stApp {{background-image: url('{BACKGROUND_IMAGE_URL}'); background-size: cover; background-position: center; background-repeat: no-repeat;}}
    .stMarkdown h1 {{color: #32a88d;}}
    .css-1d391kg {{background-color: rgba(255, 255, 255, 0.78); border-radius: 14px; padding: 1rem;}}
    div[data-testid="stSidebar"] {{background-color: rgba(255, 255, 255, 0.92) !important; border: 1px solid rgba(15, 23, 42, 0.22) !important; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.17) !important;}}
    div[data-testid="stSidebar"] h3, div[data-testid="stSidebar"] h4, div[data-testid="stSidebar"] p, div[data-testid="stSidebar"] label {{color: #0f172a !important;}}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# 📄 Resume Analyzer")
st.markdown(
    "Upload a PDF resume and get a match to a best-fit role based on keyword scores."
)

# Initialize jobs session state to allow updates from sidebar
if 'jobs' not in st.session_state:
    st.session_state.jobs = {
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
    for role, skills in st.session_state.jobs.items():
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
    required = st.session_state.jobs.get(best_role, [])
    found = [skill for skill in required if skill in text]
    if not required:
        return 0
    base_score = int(len(found) / len(required) * 100)
    bonus = min(10, sum(1 for word in ["lead", "managed", "delivered"] if word in text))
    return min(100, base_score + bonus)

with st.sidebar:
    st.header("Instructions")
    st.write(
        "- Upload a PDF resume\n"
        "- Wait for parsing\n"
        "- View Suggested Role and Scoreboard\n"
        "- Add new role keywords below"
    )

    st.subheader("Custom Role Configuration")
    new_role = st.text_input("Custom Role Name", "")
    new_skills_str = st.text_input("Custom Role Skills (comma-separated)", "")
    if st.button("Add/Update Custom Role") and new_role.strip():
        custom_skills = [s.strip().lower() for s in new_skills_str.split(",") if s.strip()]
        if custom_skills:
            st.session_state.jobs[new_role.strip()] = custom_skills
            st.success(f"Added '{new_role.strip()}'")
        else:
            st.warning("Enter at least one skill.")

    show_details = st.checkbox("Show detected keywords", True)
    show_summary = st.checkbox("Show summary", True)
    show_missing = st.checkbox("Show missing key skills", True)

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

if uploaded_file:
    st.success("Resume uploaded successfully!")
    resume_text = extract_text(uploaded_file)
    if not resume_text.strip():
        st.warning("No text found in this resume. Try another PDF.")
    else:
        best_job, scores, hit_skills = match_job(resume_text)
        st.subheader("🎯 Recommended Job Role")
        st.info(f"*{best_job}*")

        st.subheader("📊 Matching Scores")
        # Sort scores for display
        sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
        for role, score in sorted_scores.items():
            st.write(f"- {role}: *{score}*")
        st.bar_chart(list(scores.values()))

        if show_details:
            st.subheader("🧠 Detected Keywords (sample)")
            words = sorted({w for w in resume_text.split() if len(w) > 2})
            st.write(", ".join(words[:80]))

        if show_summary:
            st.subheader("📝 Resume Summary")
            st.write(simple_summary(resume_text, max_sentences=6))

        if show_missing:
            st.subheader("⚠️ Missing skills for recommended role")
            missing = [skill for skill in st.session_state.jobs[best_job] if skill not in hit_skills[best_job]]
            if missing:
                st.write(", ".join(missing[:20]))
            else:
                st.success("All recommended skills covered!")

        years_exp = extract_years_of_experience(resume_text)
        st.subheader("📈 Inferred Experience")
        if years_exp is not None and years_exp > 0:
            st.write(f"Estimated experience: *{years_exp} years*")
        else:
            st.write("Estimated experience: *Data not detected*")

        total_words, top_keywords = keyword_density(resume_text)
        st.subheader("🔑 Keyword Density")
        st.write(f"Total words analyzed: *{total_words}*")
        st.write(', '.join([f"{w} ({c})" for w, c in top_keywords]))

        st.subheader("🧾 ATS Compatibility Score")
        score = ats_score(resume_text, best_job)
        st.progress(score / 100)
        st.write(f"Your ATS score for *{best_job}* is *{score}/100*")

        st.subheader("💡 Role Skill Hit Details")
        for role in sorted_scores.keys():
            if hit_skills[role]:
                st.write(f"**{role}**: {', '.join(sorted(set(hit_skills[role]))) }")

        st.subheader("📄 Export Analysis Report")
        report_text = (
            f"Recommended: {best_job}\n"
            f"ATS Score: {score}/100\n"
            f"Experience Estimate: {years_exp if years_exp is not None else 'N/A'}\n"
            f"Top keywords: {', '.join([f'{w} ({c})' for w,c in top_keywords])}\n"
        )
        st.download_button("Download report TXT", report_text, file_name="resume_analysis.txt")
