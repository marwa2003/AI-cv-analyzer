from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# Load embedding model
# ============================================================

model = SentenceTransformer("all-MiniLM-L6-v2")


# ============================================================
# Get all candidate skills
# ============================================================

def get_candidate_skills(cv_profile):
    """
    Collect all skills from the candidate CV.
    """

    skills = []

    skills.extend(cv_profile.programming_languages or [])
    skills.extend(cv_profile.machine_learning_skills or [])
    skills.extend(cv_profile.nlp_skills or [])
    skills.extend(cv_profile.frameworks_and_libraries or [])
    skills.extend(cv_profile.databases or [])
    skills.extend(cv_profile.technical_skills or [])

    # Remove duplicates while preserving order
    unique_skills = list(dict.fromkeys(skills))

    return unique_skills


# ============================================================
# Semantic matching
# ============================================================

def semantic_match(candidate_skills, job_skills):
    """
    Compare job skills with candidate skills using
    Sentence Transformers and cosine similarity.
    """

    if not candidate_skills or not job_skills:
        return []

    # Encode candidate skills
    candidate_embeddings = model.encode(
        candidate_skills,
        convert_to_numpy=True
    )

    # Encode job skills
    job_embeddings = model.encode(
        job_skills,
        convert_to_numpy=True
    )

    results = []

    for i, job_skill in enumerate(job_skills):

        similarities = cosine_similarity(
            job_embeddings[i].reshape(1, -1),
            candidate_embeddings
        )[0]

        best_index = similarities.argmax()

        best_similarity = float(
            similarities[best_index]
        )

        # ====================================================
        # Classification
        # ====================================================

        if best_similarity >= 0.80:

            match_type = "exact"

            best_candidate_skill = candidate_skills[
                best_index
            ]

        elif best_similarity >= 0.65:

            match_type = "related"

            best_candidate_skill = candidate_skills[
                best_index
            ]

        else:

            match_type = "missing"

            best_candidate_skill = None

        # ====================================================
        # Result
        # ====================================================

        results.append(
            {
                "job_skill": job_skill,
                "candidate_skill": best_candidate_skill,
                "similarity": round(best_similarity, 3),
                "match_type": match_type,
            }
        )

    return results