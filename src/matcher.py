from src.cv_schema import CVProfile
from src.job_schema import JobProfile


def normalize_skill(skill: str) -> str:
    return skill.lower().strip()


def get_candidate_skills(cv: CVProfile) -> set[str]:
    skills = []

    skills.extend(cv.technical_skills)
    skills.extend(cv.programming_languages)
    skills.extend(cv.machine_learning_skills)
    skills.extend(cv.nlp_skills)
    skills.extend(cv.frameworks_and_libraries)
    skills.extend(cv.databases)

    return {
        normalize_skill(skill)
        for skill in skills
    }


def calculate_match(cv: CVProfile, job: JobProfile):
    candidate_skills = get_candidate_skills(cv)

    required_skills = [
        normalize_skill(skill)
        for skill in job.required_skills
    ]

    preferred_skills = [
        normalize_skill(skill)
        for skill in job.preferred_skills
    ]

    matched_required = [
        skill
        for skill in required_skills
        if skill in candidate_skills
    ]

    missing_required = [
        skill
        for skill in required_skills
        if skill not in candidate_skills
    ]

    matched_preferred = [
        skill
        for skill in preferred_skills
        if skill in candidate_skills
    ]

    missing_preferred = [
        skill
        for skill in preferred_skills
        if skill not in candidate_skills
    ]

    required_score = (
        len(matched_required) / len(required_skills) * 100
        if required_skills
        else 0
    )

    preferred_score = (
        len(matched_preferred) / len(preferred_skills) * 100
        if preferred_skills
        else 0
    )

    final_score = (
        required_score * 0.8
        + preferred_score * 0.2
    )

    return {
        "match_score": round(final_score, 2),
        "matched_required": matched_required,
        "missing_required": missing_required,
        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred,
    }