def validate_incident_data(text: str, source: str) -> bool:
    """
    Basic validation fyrir ai output
    (þarf að bæta sma við..)
    """

    # Er texti
    if not text or not isinstance(text, str) or not text.strip():
        return False

    # Er þetta of stutt
    if len(text.strip()) < 10:
        return False

    return True


if __name__ == "__main__":
    # Stutt test
    print("Data validation test\n")

    test_cases = [
    ]

    for text, source, expected_valid in test_cases:
        is_valid = validate_incident_data(text, source)
        status = "ok" if is_valid == expected_valid else "nei"
        print(f"{status} Text: '{text[:50]}' -> Valid: {is_valid} (expected: {expected_valid})")