# src/ranking.py


def rank_candidates(candidate_results):
    """
    Rank candidates according to their final match score.

    Parameters
    ----------
    candidate_results : list
        List of candidate analysis results.

    Returns
    -------
    list
        Candidates sorted from highest to lowest score.
    """

    if not candidate_results:
        return []

    # Sort by smart score, highest first
    ranked_candidates = sorted(
        candidate_results,
        key=lambda candidate: candidate.get("smart_score", 0),
        reverse=True
    )

    # Add ranking position
    for position, candidate in enumerate(
        ranked_candidates,
        start=1
    ):
        candidate["rank"] = position

    return ranked_candidates