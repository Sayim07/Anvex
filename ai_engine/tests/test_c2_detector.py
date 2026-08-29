from ai_engine.detectors.c2_detector import detect_c2


result = detect_c2(
    [
        10.0, 10.1, 9.9, 10.0,
        10.1, 9.9, 10.0, 10.1,
        9.9, 10.0
    ]
)

print("C2 Beacon Detection Result:")
print(result)