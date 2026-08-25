from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

import json
import tempfile
import os

# Only force offline mode if the model is already cached locally.
# This avoids blocking startup if the model hasn't been downloaded
# yet on a fresh machine.
_hf_cache = os.path.expanduser(
    "~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2"
)

if os.path.exists(_hf_cache):
    os.environ["HF_HUB_OFFLINE"] = "1"

from src.pdf_reader import extract_text_from_pdf
from src.groq_client import analyze_cv, analyze_job_description
from src.cv_schema import CVProfile
from src.job_schema import JobProfile
from src.semantic_matcher import get_candidate_skills, semantic_match
from src.scoring import (
    calculate_smart_score,
    extract_years_of_experience,
    calculate_experience_score,
    calculate_project_relevance,
)
from src.recommender import generate_recommendations


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="AI CV Analyzer",
    description="AI-powered CV and job matching system",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HELPERS
# ============================================================

def normalize_cv_data(cv_data):
    """
    Normalize AI output before sending it to CVProfile.

    Groq can sometimes return experience items as objects:

    {
        "title": "...",
        "organization": "...",
        "description": "..."
    }

    while CVProfile expects strings.

    This function converts those objects into readable strings.
    """

    if not isinstance(cv_data, dict):
        return cv_data

    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

    experience = cv_data.get("experience")

    if isinstance(experience, list):

        normalized_experience = []

        for item in experience:

            if isinstance(item, dict):

                parts = []

                for key in [
                    "title",
                    "role",
                    "position",
                    "organization",
                    "company",
                    "description",
                    "date",
                    "period",
                ]:

                    value = item.get(key)

                    if value:
                        parts.append(str(value))

                if parts:
                    normalized_experience.append(" - ".join(parts))
                else:
                    normalized_experience.append(
                        json.dumps(item, ensure_ascii=False)
                    )

            elif item is not None:
                normalized_experience.append(str(item))

        cv_data["experience"] = normalized_experience

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    projects = cv_data.get("projects")

    if isinstance(projects, list):

        normalized_projects = []

        for item in projects:

            if isinstance(item, dict):

                parts = []

                for key in [
                    "name",
                    "title",
                    "description",
                    "technologies",
                    "technology",
                ]:

                    value = item.get(key)

                    if value:

                        if isinstance(value, list):
                            value = ", ".join(
                                str(v) for v in value
                            )

                        parts.append(str(value))

                if parts:
                    normalized_projects.append(
                        " - ".join(parts)
                    )
                else:
                    normalized_projects.append(
                        json.dumps(item, ensure_ascii=False)
                    )

            elif item is not None:
                normalized_projects.append(str(item))

        cv_data["projects"] = normalized_projects

    return cv_data


def normalize_list(value):
    """
    Make sure a value is always a list of strings.
    """

    if value is None:
        return []

    if isinstance(value, list):

        result = []

        for item in value:

            if isinstance(item, dict):

                parts = []

                for key, val in item.items():

                    if val:
                        parts.append(str(val))

                result.append(" - ".join(parts))

            else:
                result.append(str(item))

        return result

    return [str(value)]


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "AI CV Analyzer API",
        "status": "running"
    }


# ============================================================
# ANALYZE
# ============================================================

@app.post("/analyze")
async def analyze(
    cvs: list[UploadFile] = File(...),
    job_description: str = Form(...)
):

    print("\n" + "=" * 60)
    print("ANALYZING JOB DESCRIPTION")
    print("=" * 60)

    # ========================================================
    # 1. ANALYZE JOB
    # ========================================================

    job_json = analyze_job_description(
        job_description
    )

    job_data = json.loads(job_json)

    job_profile = JobProfile(
        **job_data
    )

    print("\nJob analyzed successfully.")
    print(f"Job: {job_profile.job_title}")
    print(
        f"Years of experience required: "
        f"{job_profile.years_of_experience_required}"
    )

    # ========================================================
    # 2. ANALYZE ALL CVS
    # ========================================================

    candidates = []

    total_cvs = len(cvs)

    for index, cv in enumerate(cvs, start=1):

        print("\n" + "=" * 60)
        print(f"ANALYZING CV {index}/{total_cvs}")
        print("=" * 60)

        print(f"File: {cv.filename}")

        temp_path = None

        try:

            # ------------------------------------------------
            # Save CV temporarily
            # ------------------------------------------------

            suffix = os.path.splitext(
                cv.filename or ".pdf"
            )[1]

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as temp_file:

                temp_file.write(
                    await cv.read()
                )

                temp_path = temp_file.name

            # ------------------------------------------------
            # Extract text
            # ------------------------------------------------

            print("Extracting CV text...")

            cv_text = extract_text_from_pdf(
                temp_path
            )

            # ------------------------------------------------
            # AI analysis
            # ------------------------------------------------

            print("Analyzing CV with AI...")

            cv_json = analyze_cv(
                cv_text
            )

            cv_data = json.loads(
                cv_json
            )

            # ------------------------------------------------
            # Normalize AI output
            # ------------------------------------------------

            cv_data = normalize_cv_data(
                cv_data
            )

            # ------------------------------------------------
            # Make sure common list fields are valid
            # ------------------------------------------------

            if "skills" in cv_data:
                cv_data["skills"] = normalize_list(
                    cv_data["skills"]
                )

            if "programming_languages" in cv_data:
                cv_data["programming_languages"] = normalize_list(
                    cv_data["programming_languages"]
                )

            if "ml_skills" in cv_data:
                cv_data["ml_skills"] = normalize_list(
                    cv_data["ml_skills"]
                )

            if "frameworks" in cv_data:
                cv_data["frameworks"] = normalize_list(
                    cv_data["frameworks"]
                )

            if "databases" in cv_data:
                cv_data["databases"] = normalize_list(
                    cv_data["databases"]
                )

            # ------------------------------------------------
            # Pydantic validation
            # ------------------------------------------------

            cv_profile = CVProfile(
                **cv_data
            )

            print(
                f"Candidate: "
                f"{cv_profile.candidate_name}"
            )

            # ------------------------------------------------
            # DEBUG: inspect raw experience entries
            # ------------------------------------------------

            print("DEBUG - Raw experience entries:")

            if cv_profile.experience:
                for entry in cv_profile.experience:
                    print(f"  - {entry!r}")
            else:
                print("  (empty)")

            # ------------------------------------------------
            # Candidate skills
            # ------------------------------------------------

            candidate_skills = get_candidate_skills(
                cv_profile
            )

            # ------------------------------------------------
            # Required matching
            # ------------------------------------------------

            semantic_results = semantic_match(
                candidate_skills,
                job_profile.required_skills,
            )

            # ------------------------------------------------
            # Preferred matching
            # ------------------------------------------------

            preferred_results = semantic_match(
                candidate_skills,
                job_profile.preferred_skills,
            )

            # ------------------------------------------------
            # Experience score
            # ------------------------------------------------

            candidate_years = extract_years_of_experience(
                cv_profile.experience
            )

            experience_score = calculate_experience_score(
                candidate_years,
                job_profile.years_of_experience_required,
            )

            print(
                f"Estimated candidate experience: "
                f"{candidate_years} years "
                f"(score: {experience_score:.2f}%)"
            )

            # ------------------------------------------------
            # Project relevance score
            # ------------------------------------------------

            project_score = calculate_project_relevance(
                cv_profile.projects,
                job_profile.required_skills,
            )

            print(
                f"Project relevance score: "
                f"{project_score:.2f}%"
            )

            # ------------------------------------------------
            # Smart score
            # ------------------------------------------------

            smart_score = calculate_smart_score(
                semantic_results,
                preferred_results,
                education_match=True,
                experience_score=experience_score,
                project_score=project_score,
            )

            print(
                f"Smart Score: "
                f"{smart_score:.2f}%"
            )

            # ------------------------------------------------
            # Count matches
            # ------------------------------------------------

            required_matched = sum(
                1
                for result in semantic_results
                if result.get("match_type") == "exact"
            )

            preferred_matched = sum(
                1
                for result in preferred_results
                if result.get("match_type") == "exact"
            )

            # ------------------------------------------------
            # Recommendations
            # ------------------------------------------------

            recommendations = generate_recommendations(
                cv_profile,
                job_profile,
                semantic_results,
                smart_score,
            )

            # ------------------------------------------------
            # Candidate result
            # ------------------------------------------------

            candidate_result = {

                "candidate": cv_profile.model_dump(),

                "cv_filename": cv.filename,

                "smart_score": round(
                    float(smart_score),
                    2
                ),

                "required_matched": required_matched,

                "required_total": len(
                    job_profile.required_skills
                ),

                "preferred_matched": preferred_matched,

                "preferred_total": len(
                    job_profile.preferred_skills
                ),

                "semantic_matching": {
                    "required": semantic_results,
                    "preferred": preferred_results,
                },

                "recommendations": recommendations,
            }

            candidates.append(
                candidate_result
            )

        except Exception as e:

            # ------------------------------------------------
            # Don't stop the complete screening
            # if one CV has a problem.
            # ------------------------------------------------

            print(
                f"Error analyzing "
                f"{cv.filename}: {e}"
            )

            continue

        finally:

            if temp_path and os.path.exists(
                temp_path
            ):
                os.remove(
                    temp_path
                )

    # ========================================================
    # 3. SORT CANDIDATES
    # ========================================================

    candidates.sort(
        key=lambda candidate: candidate[
            "smart_score"
        ],
        reverse=True,
    )

    # ========================================================
    # 4. ADD RANK
    # ========================================================

    for index, candidate in enumerate(
        candidates,
        start=1
    ):

        candidate["rank"] = index

    # ========================================================
    # 5. TOP CANDIDATE
    # ========================================================

    top_candidate = (
        candidates[0]
        if candidates
        else None
    )

    # ========================================================
    # 6. RESPONSE
    # ========================================================

    print("\n" + "=" * 60)
    print("SCREENING COMPLETED")
    print("=" * 60)

    if top_candidate:

        print(
            "Top Candidate: "
            f"{top_candidate['candidate']['candidate_name']}"
        )

        print(
            "Score: "
            f"{top_candidate['smart_score']:.2f}%"
        )

    else:

        print(
            "No valid candidates found."
        )

    return {

        "job": job_profile.model_dump(),

        "candidates": candidates,

        "top_candidate": top_candidate,

        "total_cvs": len(cvs),

        "successful_cvs": len(candidates),
    }