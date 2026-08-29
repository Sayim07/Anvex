import numpy as np
from scipy.fft import rfft, rfftfreq


def calculate_iat_variance(inter_arrival_times):
    """Calculate variance of inter-arrival times."""

    if len(inter_arrival_times) < 2:
        return 0.0

    return float(np.var(inter_arrival_times))


def calculate_fft_periodicity(inter_arrival_times):
    """
    Estimate the dominant periodicity strength using FFT.
    """

    if len(inter_arrival_times) < 4:
        return 0.0

    values = np.asarray(inter_arrival_times, dtype=float)

    values = values - np.mean(values)

    spectrum = np.abs(rfft(values))

    if len(spectrum) <= 1:
        return 0.0

    spectrum[0] = 0

    maximum = np.max(spectrum)
    total = np.sum(spectrum)

    if total == 0:
        return 0.0

    return float(maximum / total)


def extract_c2_features(inter_arrival_times):
    return {
        "iat_variance": calculate_iat_variance(inter_arrival_times),
        "fft_periodicity": calculate_fft_periodicity(inter_arrival_times),
    }