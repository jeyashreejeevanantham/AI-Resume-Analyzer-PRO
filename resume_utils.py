
import os
import re
import PyPDF2
import streamlit as st

# Avoid unnecessary TensorFlow imports through Transformers.
os.environ["USE_TF"] = "0"

from sentence_transformers import SentenceTransformer, util


# ==========================================
# 1. PDF TEXT EXTRACTION
# ==========================================

def extract_text_from_pdf(file):

    reader = PyPDF2.PdfReader(file)
    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    return text


# ==========================================
# 2. SKILLS DATABASE
# ==========================================

SKILLS_DATABASE = [
    # Programming languages
    "python", "java", "c++", "c#", "javascript",
    "typescript", "php", "ruby", "go", "rust",

    # Web development
    "html", "css", "react", "angular", "vue",
    "node.js", "express", "django", "flask",
    "fastapi", "bootstrap", "tailwind css",

    # Databases
    "sql", "mysql", "postgresql", "mongodb",
    "oracle", "sqlite", "redis", "database",

    # AI, ML and data science
    "machine learning", "deep learning",
    "artificial intelligence", "generative ai",
    "natural language processing", "computer vision",
    "data analysis", "data science", "data engineering",
    "pandas", "numpy", "matplotlib", "seaborn",
    "tensorflow", "keras", "pytorch",
    "scikit-learn", "statistics",

    # Analytics
    "power bi", "tableau", "excel", "looker",

    # Cloud and DevOps
    "aws", "azure", "google cloud",
    "docker", "kubernetes", "jenkins",
    "git", "github", "linux", "terraform", "ci/cd",

    # Software engineering
    "rest api", "microservices", "spring boot",
    ".net", "unit testing", "software development",
    "data structures", "algorithms",
    "object oriented programming", "debugging",
    "api development", "testing",

    # Cybersecurity
    "cybersecurity", "network security",
    "ethical hacking", "penetration testing",
    "cryptography",

    # UI/UX
    "figma", "adobe xd", "wireframing",
    "prototyping", "user research",
    "user experience", "user interface",

    # Business
    "business analysis", "market research",
    "digital marketing", "seo", "content marketing",
    "project management",

    # Soft skills
    "communication", "leadership",
    "problem solving", "agile", "scrum"
]


# ==========================================
# 3. SKILL ALIASES
# ==========================================

SKILL_ALIASES = {
    "py": "python",
    "js": "javascript",
    "html5": "html",
    "css3": "css",
    "postgres": "postgresql",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "oop": "object oriented programming",
    "object-oriented programming": "object oriented programming",
    "restful api": "rest api",
    "rest apis": "rest api",
    "data structure": "data structures",
    "dsa": "data structures",
    "problem-solving": "problem solving",
    "powerbi": "power bi",
    "nodejs": "node.js",
    "unit tests": "unit testing",
    "unit test": "unit testing"
}


# ==========================================
# 4. ROLE-BASED SKILL REQUIREMENTS
# ==========================================

ROLE_SKILLS = {

    "python developer": [
        "python",
        "object oriented programming",
        "data structures",
        "algorithms",
        "sql",
        "git",
        "rest api",
        "debugging",
        "unit testing"
    ],

    "machine learning engineer": [
        "python",
        "machine learning",
        "deep learning",
        "scikit-learn",
        "pandas",
        "numpy",
        "statistics",
        "tensorflow",
        "sql"
    ],

    "data analyst": [
        "python",
        "sql",
        "excel",
        "pandas",
        "numpy",
        "data analysis",
        "statistics",
        "power bi",
        "matplotlib"
    ],

    "data scientist": [
        "python",
        "sql",
        "machine learning",
        "statistics",
        "pandas",
        "numpy",
        "scikit-learn",
        "data analysis",
        "data science"
    ],

    "ai engineer": [
        "python",
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "generative ai",
        "natural language processing",
        "rest api",
        "git"
    ],

    "frontend developer": [
        "html",
        "css",
        "javascript",
        "react",
        "git",
        "api development"
    ],

    "backend developer": [
        "python",
        "sql",
        "rest api",
        "git",
        "debugging",
        "unit testing",
        "database"
    ]
}


# ==========================================
# 5. TEXT NORMALIZATION
# ==========================================

def normalize_text(text):

    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def contains_skill(text, skill):

    text = normalize_text(text)
    skill = normalize_text(skill)

    pattern = (
        r"(?<![a-zA-Z0-9])"
        + re.escape(skill)
        + r"(?![a-zA-Z0-9])"
    )

    return bool(re.search(pattern, text))


def canonical_skill(skill):

    skill = normalize_text(skill)

    return SKILL_ALIASES.get(skill, skill)


# ==========================================
# 6. REMOVE OVERLAPPING SKILLS
# ==========================================

def remove_overlapping_skills(skills):

    skills = list(set(
        canonical_skill(skill)
        for skill in skills
    ))

    # If a more specific skill exists,
    # avoid counting its generic version separately.

    overlap_rules = {
        "rest api": ["api development"],
        "unit testing": ["testing"]
    }

    for specific_skill, generic_skills in overlap_rules.items():

        if specific_skill in skills:

            for generic_skill in generic_skills:

                if generic_skill in skills:
                    skills.remove(generic_skill)

    return sorted(skills)


# ==========================================
# 7. DETECT SKILLS
# ==========================================

def detect_skills(text):

    detected = set()

    text = normalize_text(text)

    for skill in SKILLS_DATABASE:

        if contains_skill(text, skill):
            detected.add(skill)

    for alias, canonical in SKILL_ALIASES.items():

        if contains_skill(text, alias):
            detected.add(canonical)

    return remove_overlapping_skills(detected)


# ==========================================
# 8. EXTRACT JOB SKILLS
# ==========================================

def extract_job_skills(job_description):

    if not job_description or not job_description.strip():
        return []

    detected = set()

    job_description = normalize_text(job_description)

    for skill in SKILLS_DATABASE:

        if contains_skill(job_description, skill):
            detected.add(skill)

    for alias, canonical in SKILL_ALIASES.items():

        if contains_skill(job_description, alias):
            detected.add(canonical)

    return remove_overlapping_skills(detected)


# ==========================================
# 9. GET ROLE REQUIREMENTS
# ==========================================

def get_role_requirements(target_role):

    role = normalize_text(target_role)

    for role_name, skills in ROLE_SKILLS.items():

        if role_name in role or role in role_name:
            return remove_overlapping_skills(skills)

    return []


# ==========================================
# 10. RESUME SCORE
# ==========================================

def calculate_score(text):

    if not text or not text.strip():
        return 0

    text_lower = normalize_text(text)
    words = text_lower.split()
    word_count = len(words)

    # --------------------------------------
    # A. SKILLS COVERAGE: 15 POINTS
    # --------------------------------------

    detected = detect_skills(text)

    skill_score = min(
        len(detected) * 1.5,
        15
    )

    # --------------------------------------
    # B. RESUME SECTIONS: 20 POINTS
    # --------------------------------------

    sections = {
        "summary": ["summary", "professional summary", "profile"],
        "skills": ["technical skills", "skills"],
        "education": ["education"],
        "projects": ["projects", "academic projects"],
        "experience": ["experience", "internship", "work experience"],
        "certifications": ["certifications", "certificates"]
    }

    section_score = 0

    for section, headings in sections.items():

        if any(
            re.search(
                r"\b" + re.escape(heading) + r"\b",
                text_lower
            )
            for heading in headings
        ):

            section_score += 3.33

    section_score = min(section_score, 20)

    # --------------------------------------
    # C. PROJECT QUALITY: 20 POINTS
    # --------------------------------------

    project_score = 0

    if "project" in text_lower:
        project_score += 5

    project_action_words = [
        "built",
        "developed",
        "implemented",
        "designed",
        "created"
    ]

    project_actions = sum(
        len(re.findall(r"\b" + word + r"\b", text_lower))
        for word in project_action_words
    )

    project_score += min(project_actions * 2, 10)

    project_technology_count = sum(
        1 for skill in detected
        if contains_skill(text_lower, skill)
    )

    if project_technology_count >= 3:
        project_score += 5

    project_score = min(project_score, 20)

    # --------------------------------------
    # D. EXPERIENCE: 10 POINTS
    # --------------------------------------

    experience_score = 0

    if "experience" in text_lower or "intern" in text_lower:
        experience_score += 5

    if re.search(
        r"\b(202[0-9]|201[0-9])\b",
        text_lower
    ):
        experience_score += 3

    if any(
        word in text_lower
        for word in ["responsibilities", "worked on", "contributed"]
    ):
        experience_score += 2

    experience_score = min(experience_score, 10)

    # --------------------------------------
    # E. EDUCATION: 10 POINTS
    # --------------------------------------

    education_score = 0

    if "education" in text_lower:
        education_score += 4

    if re.search(
        r"\b(b\.?tech|bachelor|degree|b\.?e\.?|master|b\.?sc)\b",
        text_lower
    ):
        education_score += 3

    if re.search(
        r"\b(cgpa|gpa|percentage|grade)\b",
        text_lower
    ):
        education_score += 3

    education_score = min(education_score, 10)

    # --------------------------------------
    # F. ACHIEVEMENTS: 10 POINTS
    # --------------------------------------

    achievement_score = 0

    if re.search(r"\b\d+%", text_lower):
        achievement_score += 4

    if re.search(r"\b\d+\+", text_lower):
        achievement_score += 3

    if re.search(
        r"\b(improved|increased|reduced|achieved|accuracy|score)\b",
        text_lower
    ):
        achievement_score += 3

    achievement_score = min(achievement_score, 10)

    # --------------------------------------
    # G. CONTACT DETAILS: 5 POINTS
    # --------------------------------------

    contact_score = 0

    if re.search(r"\S+@\S+\.\S+", text):
        contact_score += 2

    if re.search(r"\+?\d[\d\s()-]{7,}\d", text):
        contact_score += 1

    if "linkedin" in text_lower:
        contact_score += 1

    if "github" in text_lower:
        contact_score += 1

    # --------------------------------------
    # H. READABILITY: 10 POINTS
    # --------------------------------------

    readability_score = 0

    if 250 <= word_count <= 800:
        readability_score += 5

    elif 180 <= word_count < 250 or 800 < word_count <= 950:
        readability_score += 3

    if len(re.findall(r"[.!?]", text)) >= 3:
        readability_score += 2

    if len(re.findall(r"\b[A-Z]{3,}\b", text)) < 15:
        readability_score += 3

    readability_score = min(readability_score, 10)

    # --------------------------------------
    # FINAL SCORE
    # --------------------------------------

    total = (
        skill_score
        + section_score
        + project_score
        + experience_score
        + education_score
        + achievement_score
        + contact_score
        + readability_score
    )

    return max(0, min(round(total), 100))


# ==========================================
# 11. ATS SCORE
# ==========================================

def calculate_ats_score(text):

    if not text or not text.strip():
        return 0

    text_lower = normalize_text(text)
    score = 0

    # --------------------------------------
    # A. REQUIRED SECTIONS: 30 POINTS
    # --------------------------------------

    required_sections = [
        "education",
        "skills",
        "projects",
        "experience"
    ]

    for section in required_sections:

        if re.search(
            r"\b" + re.escape(section) + r"\b",
            text_lower
        ):

            score += 7.5

    # --------------------------------------
    # B. CONTACT DETAILS: 20 POINTS
    # --------------------------------------

    if re.search(r"\S+@\S+\.\S+", text):
        score += 7

    if re.search(r"\+?\d[\d\s()-]{7,}\d", text):
        score += 5

    if "linkedin" in text_lower:
        score += 4

    if "github" in text_lower:
        score += 4

    # --------------------------------------
    # C. RESUME LENGTH: 15 POINTS
    # --------------------------------------

    word_count = len(text.split())

    if 250 <= word_count <= 800:
        score += 15

    elif 180 <= word_count < 250 or 800 < word_count <= 950:
        score += 10

    elif 120 <= word_count < 180 or 950 < word_count <= 1100:
        score += 5

    # --------------------------------------
    # D. ACTION VERBS: 15 POINTS
    # --------------------------------------

    action_words = [
        "developed",
        "built",
        "created",
        "implemented",
        "designed",
        "managed",
        "analyzed",
        "improved",
        "trained",
        "performed",
        "integrated",
        "automated"
    ]

    action_count = sum(
        len(re.findall(
            r"\b" + word + r"\b",
            text_lower
        ))
        for word in action_words
    )

    score += min(action_count * 2, 15)

    # --------------------------------------
    # E. DATES AND EDUCATION DETAILS: 10 POINTS
    # --------------------------------------

    if re.search(
        r"\b(19|20)\d{2}\b",
        text_lower
    ):
        score += 5

    if re.search(
        r"\b(cgpa|gpa|percentage|grade)\b",
        text_lower
    ):
        score += 5

    # --------------------------------------
    # F. TECHNICAL SKILL IDENTIFICATION: 10 POINTS
    # --------------------------------------

    detected = detect_skills(text)

    if len(detected) >= 5:
        score += 10

    elif len(detected) >= 3:
        score += 7

    elif len(detected) >= 1:
        score += 4

    return max(0, min(round(score), 100))


# ==========================================
# 12. MISSING SKILLS
# ==========================================

def get_missing_skills(
    detected_skills,
    target_role,
    job_description=""
):

    required_skills = extract_job_skills(job_description)

    if not required_skills:
        required_skills = get_role_requirements(target_role)

    detected_lower = {
        canonical_skill(skill)
        for skill in detected_skills
    }

    missing = []

    for skill in required_skills:

        if canonical_skill(skill) not in detected_lower:
            missing.append(skill)

    return sorted(set(missing))


# ==========================================
# 13. JOB ROLE MATCH
# ==========================================

def calculate_role_match(
    detected_skills,
    target_role,
    job_description=""
):

    required_skills = extract_job_skills(job_description)

    if not required_skills:
        required_skills = get_role_requirements(target_role)

    if not required_skills:
        return None, []

    detected_lower = {
        canonical_skill(skill)
        for skill in detected_skills
    }

    matched_skills = []

    for skill in required_skills:

        if canonical_skill(skill) in detected_lower:
            matched_skills.append(skill)

    percentage = round(
        len(matched_skills) / len(required_skills) * 100,
        2
    )

    return percentage, matched_skills


# ==========================================
# 14. AI SEMANTIC MATCHING
# ==========================================

@st.cache_resource
def load_similarity_model():

    return SentenceTransformer("all-MiniLM-L6-v2")


def calculate_smart_job_match(
    resume_text,
    job_description
):

    if not resume_text.strip() or not job_description.strip():
        return 0

    try:

        model = load_similarity_model()

        resume_embedding = model.encode(
            resume_text,
            convert_to_tensor=True
        )

        job_embedding = model.encode(
            job_description,
            convert_to_tensor=True
        )

        similarity = util.cos_sim(
            resume_embedding,
            job_embedding
        ).item()

        percentage = round(
            max(0, min(similarity * 100, 100)),
            2
        )

        return percentage

    except Exception as e:

        st.warning(
            f"AI similarity matching unavailable: {e}"
        )

        return 0


# ==========================================
# 15. CAREER SUGGESTIONS
# ==========================================

def generate_ai_suggestions(
    ats_score,
    missing_skills,
    detected_skills,
    text
):

    suggestions = []

    text_lower = text.lower()

    if ats_score < 70:

        suggestions.append(
            "Improve ATS compatibility by using clear section headings, "
            "readable formatting and relevant resume information."
        )

    elif ats_score < 85:

        suggestions.append(
            "Your resume has a reasonable ATS structure. "
            "Improve section consistency and project descriptions."
        )

    if missing_skills:

        skills = ", ".join(missing_skills)

        suggestions.append(
            f"Consider learning these job-related skills: {skills}."
        )

    if "github" not in text_lower:

        suggestions.append(
            "Add your GitHub profile to showcase your projects."
        )

    if "linkedin" not in text_lower:

        suggestions.append(
            "Include your LinkedIn profile."
        )

    if "project" not in text_lower:

        suggestions.append(
            "Add relevant academic or personal projects."
        )

    action_words = [
        "developed",
        "built",
        "created",
        "implemented",
        "designed"
    ]

    if not any(
        word in text_lower
        for word in action_words
    ):

        suggestions.append(
            "Use strong action verbs to explain your project contributions."
        )

    if len(text.split()) < 250:

        suggestions.append(
            "Add relevant projects, achievements and experience "
            "if they are missing."
        )

    elif len(text.split()) > 900:

        suggestions.append(
            "Consider keeping your resume concise and relevant."
        )

    if not suggestions:

        suggestions.append(
            "Your resume has a good structure. "
            "Continue updating your skills, projects and achievements."
        )

    return suggestions
