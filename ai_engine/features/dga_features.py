from collections import Counter
from math import log2


def calculate_subdomain_entropy(subdomain):
    """Calculate Shannon entropy of a subdomain."""

    if not subdomain:
        return 0.0

    counts = Counter(subdomain)
    total = len(subdomain)

    entropy = 0.0

    for count in counts.values():
        probability = count / total
        entropy -= probability * log2(probability)

    return entropy


def calculate_character_ngram_probability(text, n=2):
    """
    Calculate the average observed n-gram probability
    within the supplied text.
    """

    if not text or len(text) < n:
        return 0.0

    ngrams = [
        text[i:i + n]
        for i in range(len(text) - n + 1)
    ]

    counts = Counter(ngrams)
    total = len(ngrams)

    probabilities = [
        count / total
        for count in counts.values()
    ]

    return sum(probabilities) / len(probabilities)


def extract_dga_features(subdomain):
    return {
        "subdomain_entropy": calculate_subdomain_entropy(subdomain),
        "ngram_probability": calculate_character_ngram_probability(subdomain),
    }