from fastapi import FastAPI, UploadFile, File, Form
import json
import tempfile
import os

from src.pdf_reader import extract_text_from_pdf
from src.groq_client import analyze_cv, analyze_job_description
from src.cv_schema import CVProfile
from src.job_schema import JobProfile
from src.semantic_matcher import get_candidate_skills, semantic_match
from src.scoring import calculate_smart_score
from src.recommender import generate_recommendations


app = FastAPI(
    title="AI CV Analyzer",
    description="AI-powered CV and job matching system",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "AI CV Analyzer API",
        "status": "running"
    }


@app.post("/analyze")
async def analyze(
    cv: UploadFile = File(...),
    job_description: str = Form(...)
):

    # =========================
    # 1. Save uploaded CV
    # =========================

    suffix = os.path.splitext(cv.filename)[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        temp_file.write(await cv.read())
        temp_path = temp_file.name

    try:

        # =========================
        # 2. Extract CV text
        # =========================

        cv_text = extract_text_from_pdf(temp_path)

        # =========================
        # 3. Analyze CV with Groq
        # =========================

        cv_json = analyze_cv(cv_text)

        cv_data = json.loads(cv_json)

        cv_profile = CVProfile(**cv_data)

        # =========================
        # 4. Analyze Job
        # =========================

        job_json = analyze_job_description(
            job_description
        )

        job_data = json.loads(job_json)

        job_profile = JobProfile(**job_data)

        # =========================
        # 5. Semantic Matching
        # =========================

        candidate_skills = get_candidate_skills(
            cv_profile
        )

        semantic_results = semantic_match(
            candidate_skills,
            job_profile.required_skills,
        )

        preferred_results = semantic_match(
            candidate_skills,
            job_profile.preferred_skills,
        )

        # =========================
        # 6. Smart Score
        # =========================

        smart_score = calculate_smart_score(
            semantic_results,
            preferred_results,
            education_match=True,
        )

        # =========================
        # 7. AI Recommendations
        # =========================

        recommendations = generate_recommendations(
            cv_profile,
            job_profile,
            semantic_results,
            smart_score,
        )

        # =========================
        # 8. Return JSON
        # =========================

        return {
            "candidate": cv_profile.model_dump(),
            "job": job_profile.model_dump(),
            "match_score": smart_score,
            "semantic_matching": semantic_results,
            "recommendations": recommendations,
        }

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)