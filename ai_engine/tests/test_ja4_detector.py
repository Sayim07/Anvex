from ai_engine.detectors.ja4_detector import detect_ja4


result = detect_ja4(
    ja4="t13d1516h2_8daaf6152771",
    ja3="771,4865-4866-4867",
    packet_sizes=[
        1500, 1400, 1600, 1550,
        1700, 1450, 1800
    ],
    packet_times=[
        0.1, 0.2, 0.3, 0.4,
        0.5, 0.6, 0.7
    ],
)

print("JA4 Detection Result:")
print(result)