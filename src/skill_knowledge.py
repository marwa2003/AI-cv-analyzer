SKILL_RELATIONSHIPS = {
    "machine learning": {
        "scikit-learn",
        "random forest",
        "svm",
        "logistic regression",
        "gradient boosting",
        "decision tree",
        "knn",
        "xgboost",
        "tensorflow",
        "pytorch",
    },

    "data analysis": {
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "r",
    },

    "nlp": {
        "tf-idf",
        "rag",
        "transformers",
        "embeddings",
        "text classification",
        "named entity recognition",
    },

    "web development": {
        "html",
        "css",
        "javascript",
        "react",
        "node.js",
        "fastapi",
    },

    "software development": {
        "git",
        "github",
        "docker",
        "testing",
        "ci/cd",
    },
}


def normalize_skill(skill: str) -> str:
    return skill.lower().strip()


def is_related(job_skill: str, candidate_skill: str) -> bool:

    job_skill = normalize_skill(job_skill)
    candidate_skill = normalize_skill(candidate_skill)

    for category, related_skills in SKILL_RELATIONSHIPS.items():

        if job_skill == category and candidate_skill in related_skills:
            return True

        if candidate_skill == category and job_skill in related_skills:
            return True

    return False