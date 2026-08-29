from ai_engine.features.dga_features import extract_dga_features


def detect_dga(subdomain):
    """
    Initial baseline DGA/DNS tunneling detector.

    Uses:
    - Subdomain entropy
    - N-gram probability

    Requires:
    - subdomain: a non-None string from a DNS query record (Zeek dns.log)

    If subdomain is None (DNS query field absent from upstream pipeline),
    the detector returns not-detected rather than producing a false positive.
    When subdomain=None, extract_dga_features returns ngram_probability=0.0,
    which would falsely satisfy the <= 0.08 threshold.  The guard below
    prevents that incorrect path.

    Upstream requirement: Zeek dns.log events with 'query'/'subdomain' fields.
    """

    # Guard: cannot evaluate DGA without a DNS query string.
    # Do NOT score on missing data -- 0.0 ngram_probability is not evidence
    # of DGA; it is evidence of absent upstream data.
    if subdomain is None:
        return {
            "detector": "dga",
            "detected": False,
            "score": 0.0,
            "features": {
                "subdomain_entropy": 0.0,
                "ngram_probability": 0.0,
            },
            "limitation": (
                "DGA not evaluated: no DNS query field available in the "
                "upstream pipeline.  Add Zeek dns.log events with the "
                "'query' field to enable DGA detection."
            ),
        }

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