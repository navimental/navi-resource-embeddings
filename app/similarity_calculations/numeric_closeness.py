def age_proximity_score(input_age: int, case_age: int) -> float:
    if input_age is None or case_age is None:
        return 0.0

    age_diff = abs(input_age - case_age)

    # Penalize more when age is lower
    # denominator grows as kids get older → differences matter less
    scale = max(min(input_age, case_age), 1)  # avoid divide by zero

    score = 1.0 - (age_diff / scale)

    return max(score, 0.0)
