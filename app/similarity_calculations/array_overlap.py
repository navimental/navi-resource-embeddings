from typing import List

def array_overlap_score(input_array: List[str], case_array: List[str]) -> float:
    """Jaccard similarity: |A ∩ B| / |A ∪ B|. Scales from 0 to 1."""
    if not input_array or not case_array:
        return 0.0

    # Normalize and clean
    input_set = {i.lower().strip() for i in input_array if i and i.strip()}
    case_set = {i.lower().strip() for i in case_array if i and i.strip()}

    if not input_set:
        return 0.0

    intersection = len(input_set & case_set)
    union = len(input_set | case_set)

    return intersection / union if union > 0 else 0.0
