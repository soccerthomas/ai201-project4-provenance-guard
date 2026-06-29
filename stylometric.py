import re
import math


def compute_heuristic_score(text: str) -> float:
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = text.lower().split()

    if len(sentences) < 2 or len(words) < 10:
        return 0.5  # edge case: too short for reliable analysis

    # 1. Average sentence length (AI tends toward 15–25 words/sentence)
    sent_lengths = [len(s.split()) for s in sentences]
    avg_len = sum(sent_lengths) / len(sent_lengths)
    # Normalize: score high if avg is in the AI sweet spot (15–25)
    if 15 <= avg_len <= 25:
        len_score = 1.0
    elif avg_len < 15:
        len_score = avg_len / 15
    else:
        len_score = max(0.0, 1.0 - (avg_len - 25) / 25)

    # 2. Type-token ratio (vocabulary diversity; AI tends to be lower)
    unique_words = set(words)
    ttr = len(unique_words) / len(words)
    # Low TTR → more AI-like; invert so high score = AI-like
    ttr_score = max(0.0, 1.0 - ttr)

    # 3. Burstiness (variance in sentence lengths; humans are burstier)
    mean_len = avg_len
    variance = sum((l - mean_len) ** 2 for l in sent_lengths) / len(sent_lengths)
    std_dev = math.sqrt(variance)
    # Low std_dev → uniform → AI-like
    # Normalize: std_dev of 0 = score 1.0, std_dev of 10+ = score 0.0
    burst_score = max(0.0, 1.0 - std_dev / 10)

    # Weighted combination of the three heuristics
    heuristic_score = (0.4 * len_score) + (0.3 * ttr_score) + (0.3 * burst_score)
    return round(min(max(heuristic_score, 0.0), 1.0), 4)