def exact_match_score(input_val: str, case_val: str) -> float:
    """Returns 1.0 if exact match, 0.0 otherwise. Handles None/empty values."""
    if not input_val or not case_val:
        return 0.0
    return 1.0 if input_val.lower().strip() == case_val.lower().strip() else 0.0