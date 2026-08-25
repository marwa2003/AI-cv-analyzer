# src/scoring.py

import re
import datetime


# ============================================================
# MONTH PARSING
# ============================================================

MONTH_MAP = {
    "jan": 1, "january": 1, "janvier": 1,
    "feb": 2, "february": 2, "février": 2, "fevrier": 2,
    "mar": 3, "march": 3, "mars": 3,
    "apr": 4, "april": 4, "avril": 4,
    "may": 5, "mai": 5,
    "jun": 6, "june": 6, "juin": 6,
    "jul": 7, "july": 7, "juillet": 7,
    "aug": 8, "august": 8, "août": 8, "aout": 8,
    "sep": 9, "sept": 9, "september": 9, "septembre": 9,
    "oct": 10, "october": 10, "octobre": 10,
    "nov": 11, "november": 11, "novembre": 11,
    "dec": 12, "december": 12, "décembre": 12, "decembre": 12,
}


def _parse_month_year(text_chunk):
    """
    Try to find a (month, year) pair in a small chunk of text.
    Returns (month, year) where month may be None if only a
    year was found. Returns (None, None) if no year is found.
    """

    year_match = re.search(r"(?:19|20)\d{2}", text_chunk)

    if not year_match:
        return None, None

    year = int(year_match.group())

    month = None

    for name, num in MONTH_MAP.items():
        if re.search(rf"\b{name}\b", text_chunk, re.IGNORECASE):
            month = num
            break

    return month, year


# ============================================================
# EXPERIENCE HELPERS
# ============================================================

def extract_years_of_experience(experience_list):
    """
    Estimate total years of experience from free-text experience
    entries, parsing month + year when available for a more
    accurate (fractional) duration, falling back to year-only
    estimation otherwise.

    Handles entries like:
        "Intern - Company, City - Feb 2024 - Apr 2024"
        "AI/ML Intern - TELETIC.dz - Apr 2026 - May 2026"
        "ML Engineer - Beta Inc - 2023 - Present"
    """

    now = datetime.datetime.now()
    total_months = 0

    for entry in experience_list or []:

        has_present = bool(
            re.search(
                r"present|actuel|now|aujourd'hui",
                entry,
                re.IGNORECASE,
            )
        )

        # Split around dashes/connectors that typically separate
        # start/end dates within an entry.
        date_parts = re.split(r"–|-|to|à", entry)

        # Collect all (month, year) pairs found across the entry.
        found_dates = []

        for chunk in date_parts:
            month, year = _parse_month_year(chunk)
            if year:
                found_dates.append((month or 1, year))

        if not found_dates:
            continue

        start_month, start_year = min(
            found_dates, key=lambda d: (d[1], d[0])
        )

        if has_present:
            end_month, end_year = now.month, now.year
        else:
            end_month, end_year = max(
                found_dates, key=lambda d: (d[1], d[0])
            )

        months_diff = (
            (end_year - start_year) * 12
            + (end_month - start_month)
        )

        # Give at least 1 month of credit for any valid entry found,
        # so short internships aren't rounded down to zero.
        total_months += max(months_diff, 1)

    return round(total_months / 12, 2)


def calculate_experience_score(candidate_years, required_years):
    """
    Compare candidate's estimated years of experience against
    what the job requires. Proportional, capped at 100.

    If the job doesn't specify a requirement, don't penalize
    candidates, but still reward having some experience.
    """

    if required_years <= 0:
        return 100.0 if candidate_years > 0 else 50.0

    ratio = candidate_years / required_years

    return round(min(ratio, 1.0) * 100, 2)


# ============================================================
# PROJECT RELEVANCE
# ============================================================

def calculate_project_relevance(projects, required_skills):
    """
    Check what fraction of the job's required skills are
    actually mentioned in the candidate's project descriptions.

    Simple substring match (case-insensitive) - not semantic,
    but fast and dependency-free.
    """

    if not projects or not required_skills:
        return 0.0

    projects_text = " ".join(projects).lower()

    matched = sum(
        1
        for skill in required_skills
        if skill.lower() in projects_text
    )

    return round((matched / len(required_skills)) * 100, 2)


# ============================================================
# FINAL SCORE
# ============================================================

def calculate_smart_score(
    required_results,
    preferred_results,
    education_match=False,
    experience_score=0.0,
    project_score=0.0,
):
    """
    Calculate the final candidate/job matching score.

    Scoring weights:
        Required skills : 55%
        Preferred skills: 10%
        Education       : 10%
        Experience      : 15%
        Projects        : 10%

    Required skill matching:
        exact   = 1.0
        related = 0.6
        missing = 0.0

    Preferred skill matching:
        exact   = 1.0
        related = 0.5
        missing = 0.0
    """

    # ============================================================
    # 1. REQUIRED SKILLS
    # ============================================================

    required_score = 0.0

    if required_results:

        for result in required_results:

            match_type = result.get("match_type", "missing")

            if match_type == "exact":
                required_score += 1.0
            elif match_type == "related":
                required_score += 0.6

        required_score = (
            required_score / len(required_results)
        ) * 100

    # ============================================================
    # 2. PREFERRED SKILLS
    # ============================================================

    preferred_score = 0.0

    if preferred_results:

        for result in preferred_results:

            match_type = result.get("match_type", "missing")

            if match_type == "exact":
                preferred_score += 1.0
            elif match_type == "related":
                preferred_score += 0.5

        preferred_score = (
            preferred_score / len(preferred_results)
        ) * 100

    # ============================================================
    # 3. EDUCATION
    # ============================================================

    education_score = 100.0 if education_match else 0.0

    # ============================================================
    # 4. FINAL WEIGHTED SCORE
    # ============================================================

    final_score = (
        required_score * 0.55
        + preferred_score * 0.10
        + education_score * 0.10
        + experience_score * 0.15
        + project_score * 0.10
    )

    # ============================================================
    # 5. RETURN
    # ============================================================

    return round(final_score, 2)