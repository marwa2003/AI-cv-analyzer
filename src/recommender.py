import json

from src.groq_client import client


def generate_recommendations(
    cv_profile,
    job_profile,
    semantic_results,
    smart_score,
):
    matched_skills = []
    related_skills = []
    missing_skills = []

    for result in semantic_results:

        if result["match_type"] == "exact":
            matched_skills.append(result["job_skill"])

        elif result["match_type"] in ["related", "semantic"]:
            related_skills.append(
                f"{result['job_skill']} → {result['candidate_skill']}"
            )

        elif result["match_type"] == "missing":
            missing_skills.append(result["job_skill"])

    prompt = f"""
You are an AI career assistant.

Analyze the candidate's CV and compare it with the target job.

CANDIDATE:
{cv_profile.model_dump_json(indent=2)}

JOB:
{job_profile.model_dump_json(indent=2)}

MATCH SCORE:
{smart_score}%

MATCHED SKILLS:
{matched_skills}

RELATED SKILLS:
{related_skills}

MISSING SKILLS:
{missing_skills}

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{{
    "summary": "",
    "strengths": [],
    "missing_skills": [],
    "recommendations": [],
    "cv_improvements": []
}}

Rules:

- Do not invent experience.
- Do not claim that the candidate has a skill that is not present in the CV.
- Keep recommendations practical and specific.
- Focus on improving the candidate's chances for this particular job.
- Mention the strongest matching skills.
- Mention the most important missing skills.
- Suggest realistic ways to improve the CV.
- Keep each recommendation concise.
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

    return json.loads(response.choices[0].message.content)