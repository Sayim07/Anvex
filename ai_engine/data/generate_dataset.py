import numpy as np
import pandas as pd


RANDOM_SEED = 42
SAMPLES_PER_CLASS = 500

rng = np.random.default_rng(RANDOM_SEED)


def generate_normal(n):
    return pd.DataFrame({
        "source_ip_entropy": rng.uniform(1.0, 2.5, n),
        "pps": rng.uniform(10, 500, n),
        "syn_ack_ratio": rng.uniform(0.5, 2.0, n),
        "port_fanout": rng.integers(1, 8, n),
        "connection_failure_rate": rng.uniform(0.0, 0.3, n),
        "subdomain_entropy": rng.uniform(1.0, 3.0, n),
        "ngram_probability": rng.uniform(0.10, 0.30, n),
        "packet_size_variance": rng.uniform(100, 5000, n),
        "mean_packet_size": rng.uniform(300, 1000, n),
        "iat_variance": rng.uniform(1.0, 20.0, n),
        "fft_periodicity": rng.uniform(0.0, 0.3, n),
        "outbound_inbound_ratio": rng.uniform(0.2, 2.0, n),
        "volume_baseline_ratio": rng.uniform(0.5, 2.0, n),
        "label": "normal",
    })


def generate_ddos(n):
    data = generate_normal(n)

    data["source_ip_entropy"] = rng.uniform(2.0, 5.0, n)
    data["pps"] = rng.uniform(1000, 10000, n)
    data["syn_ack_ratio"] = rng.uniform(5, 20, n)

    data["label"] = "ddos"

    return data


def generate_port_scan(n):
    data = generate_normal(n)

    data["port_fanout"] = rng.integers(10, 100, n)
    data["connection_failure_rate"] = rng.uniform(0.5, 1.0, n)

    data["label"] = "port_scan"

    return data


def generate_dga(n):
    data = generate_normal(n)

    data["subdomain_entropy"] = rng.uniform(3.5, 6.0, n)
    data["ngram_probability"] = rng.uniform(0.01, 0.08, n)

    data["label"] = "dga"

    return data


def generate_ja4(n):
    data = generate_normal(n)

    data["packet_size_variance"] = rng.uniform(10000, 50000, n)
    data["mean_packet_size"] = rng.uniform(1200, 2000, n)

    data["label"] = "ja4_malware"

    return data


def generate_c2(n):
    data = generate_normal(n)

    data["iat_variance"] = rng.uniform(0.01, 1.0, n)
    data["fft_periodicity"] = rng.uniform(0.4, 0.95, n)

    data["label"] = "c2_beacon"

    return data


def generate_exfil(n):
    data = generate_normal(n)

    data["outbound_inbound_ratio"] = rng.uniform(5, 20, n)
    data["volume_baseline_ratio"] = rng.uniform(3, 10, n)

    data["label"] = "exfiltration"

    return data


def main():
    datasets = [
        generate_normal(SAMPLES_PER_CLASS),
        generate_ddos(SAMPLES_PER_CLASS),
        generate_port_scan(SAMPLES_PER_CLASS),
        generate_dga(SAMPLES_PER_CLASS),
        generate_ja4(SAMPLES_PER_CLASS),
        generate_c2(SAMPLES_PER_CLASS),
        generate_exfil(SAMPLES_PER_CLASS),
    ]

    dataset = pd.concat(datasets, ignore_index=True)

    dataset = dataset.sample(
        frac=1,
        random_state=RANDOM_SEED
    ).reset_index(drop=True)

    output_path = "ai_engine/data/training.csv"

    dataset.to_csv(output_path, index=False)

    print(f"Dataset created: {output_path}")
    print(f"Rows: {len(dataset)}")
    print(f"Columns: {len(dataset.columns)}")
    print("\nClass distribution:")
    print(dataset["label"].value_counts())


if __name__ == "__main__":
    main()