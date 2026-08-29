from ai_engine.features.dga_features import extract_dga_features


def detect_dga(subdomain):
    """
    Initial baseline DGA/DNS tunneling detector.

    Uses:
    - Subdomain entropy
    - N-gram probability
    """

    features = extract_dga_features(subdomain)

    entropy = features["subdomain_entropy"]
    ngram_probability = features["ngram_probability"]

    score = 0.0

    if entropy >= 3.5:
        score += 0.5

    if ngram_probability <= 0.08:
        score += 0.5

    detected = score >= 0.5

    return {
        "detector": "dga",
        "detected": detected,
        "score": score,
        "features": features,
    }