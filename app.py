
import re
import streamlit as st

from resume_utils import (
    extract_text_from_pdf,
    calculate_score,
    calculate_ats_score,
    detect_skills,
    get_missing_skills,
    calculate_role_match,
    generate_ai_suggestions,
    calculate_smart_job_match,
    extract_job_skills,
    contains_skill
)


# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="AI Resume Analyzer PRO",
    page_icon="📄",
    layout="wide"
)

st.title("🧠 AI Resume Analyzer PRO")

st.write(
    "Upload your resume and receive AI-powered resume scoring, "
    "ATS analysis, skill detection, job matching, and career suggestions."
)

st.divider()


# =====================================
# HELPER: CLASSIFY JOB SKILLS
# =====================================

def classify_job_skills(job_description):

    all_skills = extract_job_skills(job_description)

    preferred_keywords = [
        "preferred",
        "preferably",
        "advantage",
        "nice to have",
        "good to have",
        "bonus",
        "optional",
        "plus",
        "desirable",
        "an added benefit"
    ]

    # Split the description into individual sentences
    sentences = re.split(
        r'(?<=[.!?])\s+|\n+',
        job_description.lower()
    )

    mandatory_skills = []
    preferred_skills = []

    for skill in all_skills:

        skill_is_preferred = False

        # Find the sentences containing this skill
        for sentence in sentences:

            if contains_skill(sentence, skill):

                # Check whether the sentence indicates
                # that the skill is preferred or optional
                if any(
                    keyword in sentence
                    for keyword in preferred_keywords
                ):

                    skill_is_preferred = True
                    break

        if skill_is_preferred:

            preferred_skills.append(skill)

        else:

            mandatory_skills.append(skill)

    return mandatory_skills, preferred_skills


# =====================================
# HELPER: CALCULATE MATCH PERCENTAGE
# =====================================

def calculate_weighted_match(
    detected_skills,
    mandatory_skills,
    preferred_skills
):

    detected = {
        skill.lower().strip()
        for skill in detected_skills
    }

    mandatory_matched = [
        skill for skill in mandatory_skills
        if skill.lower().strip() in detected
    ]

    preferred_matched = [
        skill for skill in preferred_skills
        if skill.lower().strip() in detected
    ]

    mandatory_missing = [
        skill for skill in mandatory_skills
        if skill.lower().strip() not in detected
    ]

    preferred_missing = [
        skill for skill in preferred_skills
        if skill.lower().strip() not in detected
    ]

    mandatory_percentage = (
        len(mandatory_matched) / len(mandatory_skills) * 100
        if mandatory_skills else None
    )

    preferred_percentage = (
        len(preferred_matched) / len(preferred_skills) * 100
        if preferred_skills else None
    )

    if mandatory_skills and preferred_skills:

        overall_percentage = (
            mandatory_percentage * 0.80
            + preferred_percentage * 0.20
        )

    elif mandatory_skills:

        overall_percentage = mandatory_percentage

    elif preferred_skills:

        overall_percentage = preferred_percentage

    else:

        overall_percentage = None

    return {
        "overall": round(overall_percentage, 2)
        if overall_percentage is not None else None,

        "mandatory_percentage": round(mandatory_percentage, 2)
        if mandatory_percentage is not None else None,

        "preferred_percentage": round(preferred_percentage, 2)
        if preferred_percentage is not None else None,

        "mandatory_matched": mandatory_matched,
        "preferred_matched": preferred_matched,
        "mandatory_missing": mandatory_missing,
        "preferred_missing": preferred_missing
    }


# =====================================
# USER INPUTS
# =====================================

uploaded_file = st.file_uploader(
    "📄 Upload Resume (PDF)",
    type=["pdf"]
)

selected_role = st.text_input(
    "🎯 Enter Your Target Job Role",
    placeholder="Example: Python Developer, AI Engineer, Data Analyst"
)

job_description = st.text_area(
    "📋 Paste Job Description",
    placeholder="Paste the job requirements here...",
    height=180
)

st.info(
    "Tip: Enter a job title and paste its job description "
    "for more accurate skill matching."
)

analyze = st.button(
    "🚀 Analyze Resume",
    type="primary"
)


# =====================================
# RESUME ANALYSIS
# =====================================

if analyze:

    if uploaded_file is None:

        st.error("Please upload a resume PDF.")

    elif not selected_role.strip():

        st.error("Please enter your target job role.")

    else:

        with st.spinner("Analyzing your resume..."):

            try:

                # Extract PDF text
                text = extract_text_from_pdf(uploaded_file)

                if not text.strip():

                    st.error(
                        "Could not extract text from this PDF. "
                        "Please upload a text-based PDF."
                    )

                    st.stop()

                # Calculate resume score
                resume_score = calculate_score(text)

                # Calculate ATS score
                ats_score = calculate_ats_score(text)

                # Detect resume skills
                detected_skills = detect_skills(text)

                # =====================================
                # JOB MATCHING
                # =====================================

                if job_description.strip():

                    mandatory_skills, preferred_skills = (
                        classify_job_skills(job_description)
                    )

                    match_results = calculate_weighted_match(
                        detected_skills,
                        mandatory_skills,
                        preferred_skills
                    )

                    role_match = match_results["overall"]

                    matched_skills = (
                        match_results["mandatory_matched"]
                        + match_results["preferred_matched"]
                    )

                    missing_skills = (
                        match_results["mandatory_missing"]
                        + match_results["preferred_missing"]
                    )

                else:

                    mandatory_skills = []
                    preferred_skills = []

                    match_results = None

                    role_match, matched_skills = calculate_role_match(
                        detected_skills,
                        selected_role,
                        ""
                    )

                    missing_skills = get_missing_skills(
                        detected_skills,
                        selected_role,
                        ""
                    )

                # =====================================
                # AI SEMANTIC MATCHING
                # =====================================

                if job_description.strip():

                    smart_match_score = calculate_smart_job_match(
                        text,
                        job_description
                    )

                else:

                    smart_match_score = None

                # =====================================
                # CAREER SUGGESTIONS
                # =====================================

                suggestions = generate_ai_suggestions(
                    ats_score,
                    missing_skills,
                    detected_skills,
                    text
                )

            except Exception as e:

                st.error(f"Analysis failed: {str(e)}")
                st.stop()


        # =====================================
        # RESULTS
        # =====================================

        st.success("Resume analysis completed successfully!")

        st.divider()


        # =====================================
        # RESUME SCORES
        # =====================================

        st.subheader("📊 Resume Analysis Scores")

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Resume Score",
                f"{resume_score}/100"
            )

        with col2:

            st.metric(
                "ATS Score",
                f"{ats_score}/100"
            )

        with col3:

            st.metric(
                "Job Match",
                f"{role_match}%"
                if role_match is not None
                else "Not available"
            )

        with col4:

            st.metric(
                "AI Smart Match",
                f"{smart_match_score}%"
                if smart_match_score is not None
                else "Not available"
            )

        st.caption(
            "Job Match uses an 80% mandatory-skill and 20% "
            "preferred-skill weighting when both categories exist. "
            "AI Smart Match measures semantic text similarity. "
            "These scores are estimates, not hiring probabilities."
        )

        st.divider()


        # =====================================
        # TARGET JOB ANALYSIS
        # =====================================

        st.subheader("🎯 Target Job Analysis")

        st.write(f"**Selected Job Role:** {selected_role}")

        if not job_description.strip():

            st.warning(
                "No job description provided. "
                "Role-based matching will be used where available."
            )


        # =====================================
        # SKILL MATCH BREAKDOWN
        # =====================================

        if match_results is not None:

            st.subheader("📈 Skill Match Breakdown")

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Mandatory Skill Match",
                    f"{match_results['mandatory_percentage']}%"
                    if match_results["mandatory_percentage"] is not None
                    else "Not available"
                )

            with col2:

                st.metric(
                    "Preferred Skill Match",
                    f"{match_results['preferred_percentage']}%"
                    if match_results["preferred_percentage"] is not None
                    else "Not available"
                )

            st.caption(
                "Mandatory skills carry 80% of the overall score "
                "and preferred skills carry 20%, when both exist."
            )


        # =====================================
        # MATCHED MANDATORY SKILLS
        # =====================================

        st.subheader("✅ Matching Mandatory Skills")

        if match_results is not None:

            if match_results["mandatory_matched"]:

                for skill in match_results["mandatory_matched"]:

                    st.success(skill.title())

            else:

                st.warning("No mandatory skills matched.")

        elif matched_skills:

            for skill in matched_skills:

                st.success(skill.title())

        else:

            st.info("No matching skills detected.")


        # =====================================
        # MATCHED PREFERRED SKILLS
        # =====================================

        if match_results is not None:

            st.subheader("⭐ Matching Preferred Skills")

            if match_results["preferred_matched"]:

                for skill in match_results["preferred_matched"]:

                    st.success(skill.title())

            else:

                st.info("No preferred skills matched.")


        # =====================================
        # MISSING MANDATORY SKILLS
        # =====================================

        if match_results is not None:

            st.subheader("📌 Missing Mandatory Skills")

            if match_results["mandatory_missing"]:

                for skill in match_results["mandatory_missing"]:

                    st.warning(skill.title())

            else:

                st.success(
                    "All detected mandatory job skills are present."
                )


            # =====================================
            # MISSING PREFERRED SKILLS
            # =====================================

            st.subheader("📚 Preferred Skills to Improve")

            if match_results["preferred_missing"]:

                for skill in match_results["preferred_missing"]:

                    st.info(skill.title())

            else:

                st.success(
                    "All detected preferred skills are present."
                )

        else:

            st.subheader("📌 Skills to Improve")

            if missing_skills:

                for skill in missing_skills:

                    st.warning(skill.title())

            else:

                st.success(
                    "No missing skills detected for the selected role."
                )


        # =====================================
        # ALL DETECTED SKILLS
        # =====================================

        st.subheader("💻 Skills Found in Your Resume")

        if detected_skills:

            st.write(
                ", ".join(
                    skill.title()
                    for skill in detected_skills
                )
            )

        else:

            st.warning("No recognized skills detected.")


        # =====================================
        # CAREER SUGGESTIONS
        # =====================================

        st.subheader("💡 Resume Improvement Suggestions")

        for suggestion in suggestions:

            st.info(suggestion)


        # =====================================
        # SKILL DEVELOPMENT ROADMAP
        # =====================================

        if missing_skills:

            st.subheader("🛣️ Recommended Learning Roadmap")

            st.write(
                "Prioritize mandatory requirements before preferred skills."
            )

            if match_results is not None:

                if match_results["mandatory_missing"]:

                    st.markdown("**Priority 1 – Mandatory Skills**")

                    for skill in match_results["mandatory_missing"]:

                        st.write(f"- Learn and practice {skill.title()}")

                if match_results["preferred_missing"]:

                    st.markdown("**Priority 2 – Preferred Skills**")

                    for skill in match_results["preferred_missing"]:

                        st.write(f"- Explore {skill.title()}")

            else:

                for skill in missing_skills:

                    st.write(f"- Improve {skill.title()}")


        # =====================================
        # EXTRACTED RESUME TEXT
        # =====================================

        with st.expander("📄 View Extracted Resume Text"):

            st.text_area(
                "Resume Content",
                text,
                height=300
            )

        st.divider()

        st.success("Analysis report generated successfully!")