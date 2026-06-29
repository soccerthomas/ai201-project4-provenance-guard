def compute_confidence(llm_score: float, heuristic_score: float) -> float:
    """Weighted average per planning.md: 60% Groq, 40% heuristics."""
    confidence = (0.6 * llm_score) + (0.4 * heuristic_score)
    return round(min(max(confidence, 0.0), 1.0), 4)


def get_attribution(confidence: float) -> str:
    """Maps confidence to attribution label per planning.md thresholds."""
    if confidence >= 0.70:
        return "likely_ai"
    elif confidence >= 0.40:
        return "uncertain"
    else:
        return "likely_human"