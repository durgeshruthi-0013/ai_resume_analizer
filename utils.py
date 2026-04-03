import re
import PyPDF2

# -------------------------------
# 1. Extract Text from PDF
# -------------------------------
def extract_text_from_pdf(file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)

    for page in pdf_reader.pages:
        content = page.extract_text()
        if content:
            text += content

    return text


# -------------------------------
# 2. Extract Text from TXT
# -------------------------------
def extract_text_from_txt(file):
    return file.read().decode("utf-8")


# -------------------------------
# 3. Clean Resume Text
# -------------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\W', ' ', text)   # remove special chars
    text = re.sub(r'\s+', ' ', text)  # remove extra spaces
    return text.strip()


# -------------------------------
# 4. Skill Extraction
# -------------------------------
def extract_skills(text):
    skills_list = [
        "python", "java", "c++", "sql", "html", "css",
        "javascript", "machine learning", "data science",
        "deep learning", "nlp", "react", "nodejs",
        "communication", "teamwork", "leadership",
        "problem solving", "git", "excel"
    ]

    text = text.lower()
    found_skills = []

    for skill in skills_list:
        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))


# -------------------------------
# 5. Resume Scoring
# -------------------------------
def calculate_score(found_skills):
    total_skills = 20  # total skills in list
    score = (len(found_skills) / total_skills) * 100
    return round(score, 2)


# -------------------------------
# 6. Missing Skills
# -------------------------------
def missing_skills(found_skills):
    all_skills = [
        "python", "java", "c++", "sql", "html", "css",
        "javascript", "machine learning", "data science",
        "deep learning", "nlp", "react", "nodejs",
        "communication", "teamwork", "leadership",
        "problem solving", "git", "excel"
    ]

    missing = list(set(all_skills) - set(found_skills))
    return missing


# -------------------------------
# 7. Suggestions Generator
# -------------------------------
def generate_suggestions(score, missing):
    suggestions = []

    if score < 40:
        suggestions.append("Add more technical skills to your resume.")
        suggestions.append("Include projects related to your domain.")

    elif score < 70:
        suggestions.append("Improve your resume by adding more relevant keywords.")
        suggestions.append("Highlight your achievements and experience.")

    else:
        suggestions.append("Good resume! Consider adding certifications.")
        suggestions.append("Optimize formatting for better readability.")

    if len(missing) > 0:
        suggestions.append(f"Consider adding these skills: {', '.join(missing[:5])}")

    return suggestions


# -------------------------------
# 8. File Handler (Main Function)
# -------------------------------
def process_resume(uploaded_file):
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
    else:
        text = extract_text_from_txt(uploaded_file)

    cleaned_text = clean_text(text)
    skills = extract_skills(cleaned_text)
    score = calculate_score(skills)
    missing = missing_skills(skills)
    suggestions = generate_suggestions(score, missing)

    return {
        "text": text,
        "skills": skills,
        "score": score,
        "missing_skills": missing,
        "suggestions": suggestions
    }