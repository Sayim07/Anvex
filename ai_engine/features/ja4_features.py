def calculate_splt_features(packet_sizes, packet_times):
    """Extract simple packet-size/timing statistics."""

    if not packet_sizes:
        return {
            "mean_packet_size": 0.0,
            "packet_size_variance": 0.0,
        }

    mean_size = sum(packet_sizes) / len(packet_sizes)

    variance = sum(
        (size - mean_size) ** 2
        for size in packet_sizes
    ) / len(packet_sizes)

    return {
        "mean_packet_size": mean_size,
        "packet_size_variance": variance,
    }


def extract_ja4_features(ja4, ja3, packet_sizes, packet_times):
    splt = calculate_splt_features(packet_sizes, packet_times)

    return {
        "ja4": ja4,
        "ja3": ja3,
        **splt,
    }