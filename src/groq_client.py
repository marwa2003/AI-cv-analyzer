import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set in the .env file")

client = Groq(api_key=api_key)


def analyze_cv(cv_text: str):
    prompt = f"""
You are an AI CV analysis system.

Analyze the CV below and extract the information.

CV:
{cv_text}

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{{
    "candidate_name": "",
    "education": [],
    "technical_skills": [],
    "programming_languages": [],
    "machine_learning_skills": [],
    "nlp_skills": [],
    "frameworks_and_libraries": [],
    "databases": [],
    "experience": [],
    "projects": [],
    "certifications": []
}}

Rules:
- Do not invent information.
- If information is missing, use an empty list.
- Keep skills concise.
- Keep projects as separate items.
- For "experience", include the relevant date range in each entry
  when available (e.g. "Data Analyst - Acme Corp - 2021 - 2023",
  "ML Engineer - Beta Inc - 2023 - Present"), since this is used
  to estimate years of experience.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    return response.choices[0].message.content


def analyze_job_description(job_text: str):
    prompt = f"""
You are an AI recruitment system.

Analyze the following job description.

JOB DESCRIPTION:
{job_text}

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{{
    "job_title": "",
    "required_skills": [],
    "preferred_skills": [],
    "responsibilities": [],
    "years_of_experience_required": 0
}}

Rules:
- Do not invent information.
- Extract technical skills explicitly mentioned.
- Keep each skill concise.
- Separate required skills from preferred/nice-to-have skills.
- Keep responsibilities as separate items.
- years_of_experience_required: extract the minimum number of years
  of experience mentioned (e.g. "3+ years of experience" -> 3,
  "at least 2 years" -> 2). If no experience requirement is
  mentioned, use 0.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    return response.choices[0].message.content