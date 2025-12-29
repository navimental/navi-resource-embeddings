from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

import csv
import os
from datetime import datetime
from app.deps import verify_key
from app.supabase_client import get_all_case_studies
from app.similarity_calculations.array_overlap import array_overlap_score
from app.similarity_calculations.exact_match import exact_match_score
from app.similarity_calculations.numeric_closeness import age_proximity_score
from app.similarity_calculations.text_similarity import text_similarity_score

router = APIRouter()

# Scoring weights
WEIGHTS = {
    "state": 0.25, # 0 to 1, exact match
    "current_challenges": 0.20, # Array overlap - Jaccard - could it go into embeddings as well?
    "first_session_notes": 0.15, # Embeddings - cosine similarity
    "additional_info": 0.10, # Embeddings - cosine similarity
    "child_notes": 0.05, # Embeddings - cosine similarity
    "child_age": 0.10, # Numeric closeness - potential filter? If not in same age bracket?
    "child_diagnoses": 0.10, # Array overlap - Jaccard --> Factor in families of conditions, can we create a hierarchy?
    "child_stage": 0.05, # Exact match --> Remove, overlaps with diagnoses too much, make sure "null" gets a match in diagnoses
}

class CaseStudyRequest(BaseModel):
    state: str
    current_challenges: List[str]
    first_session_notes: str
    additional_info: str
    child_age: int
    child_diagnoses: List[str]
    child_stage: str
    child_notes: str
    export_csv: Optional[bool] = True


def calculate_case_similarity_detailed(input_case: CaseStudyRequest, case_study: Dict[str, Any]) -> Dict[str, float]:
    """Calculate detailed similarity scores for each component."""
    
    # Individual component scores
    state_score = exact_match_score(input_case.state, case_study.get("state", ""))
    challenges_score = array_overlap_score(
        input_case.current_challenges, 
        case_study.get("current_challenges", [])
    )
    session_notes_score = text_similarity_score(
        input_case.first_session_notes, 
        case_study.get("first_session_notes", "")
    )
    additional_info_score = text_similarity_score(
        input_case.additional_info, 
        case_study.get("additional_info", "")
    )
    age_score = age_proximity_score(
        input_case.child_age, 
        case_study.get("child_age", 0)
    )
    diagnoses_score = array_overlap_score(
        input_case.child_diagnoses, 
        case_study.get("child_diagnoses", [])
    )
    stage_score = exact_match_score(
        input_case.child_stage, 
        case_study.get("child_stage", "")
    )
    child_notes_score = text_similarity_score(
        input_case.child_notes, 
        case_study.get("child_notes", "")
    )
    
    # Calculate weighted total
    total_score = (
        state_score * WEIGHTS["state"] +
        challenges_score * WEIGHTS["current_challenges"] +
        session_notes_score * WEIGHTS["first_session_notes"] +
        additional_info_score * WEIGHTS["additional_info"] +
        age_score * WEIGHTS["child_age"] +
        diagnoses_score * WEIGHTS["child_diagnoses"] +
        stage_score * WEIGHTS["child_stage"] +
        child_notes_score * WEIGHTS["child_notes"]
    )
    
    return {
        "case_id": case_study.get("id", ""),
        "state_score": round(state_score, 3),
        "challenges_score": round(challenges_score, 3),
        "session_notes_score": round(session_notes_score, 3),
        "additional_info_score": round(additional_info_score, 3),
        "age_score": round(age_score, 3),
        "diagnoses_score": round(diagnoses_score, 3),
        "stage_score": round(stage_score, 3),
        "child_notes_score": round(child_notes_score, 3),
        "weighted_total": round(total_score, 3)
    }

def export_scoring_to_csv(input_case: CaseStudyRequest, all_case_studies: List[Dict[str, Any]]) -> str:
    """Export detailed scoring results to CSV file."""
    
    # Create exports directory if it doesn't exist
    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{exports_dir}/case_similarity_scores_{timestamp}.csv"
    
    # Calculate detailed scores for all cases
    detailed_scores = []
    for case_study in all_case_studies:
        scores = calculate_case_similarity_detailed(input_case, case_study)
        # Add all case study info
        scores.update({
            "case_state": case_study.get("state", ""),
            "case_current_challenges": ", ".join(case_study.get("current_challenges", [])),
            "case_first_session_notes": case_study.get("first_session_notes", ""),
            "case_additional_info": case_study.get("additional_info", ""),
            "case_age": case_study.get("child_age", ""),
            "case_child_diagnoses": ", ".join(case_study.get("child_diagnoses", [])),
            "case_stage": case_study.get("child_stage", ""),
            "case_child_notes": case_study.get("child_notes", "")
        })
        detailed_scores.append(scores)
    
    # Sort by weighted total (highest first)
    detailed_scores.sort(key=lambda x: x["weighted_total"], reverse=True)
    
    # Write to CSV
    fieldnames = [
        "case_id", "case_state", "case_current_challenges", "case_first_session_notes", 
        "case_additional_info", "case_age", "case_child_diagnoses", "case_stage", "case_child_notes",
        "state_score", "challenges_score", "session_notes_score", 
        "additional_info_score", "age_score", "diagnoses_score", 
        "stage_score", "child_notes_score", "weighted_total"
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(detailed_scores)
    
    return filename

def calculate_case_similarity(input_case: CaseStudyRequest, case_study: Dict[str, Any]) -> float:
    """Calculate overall similarity score between input and a case study."""
    detailed = calculate_case_similarity_detailed(input_case, case_study)
    return detailed["weighted_total"]

@router.post("/similar")
async def get_similar_case_studies(
    req: CaseStudyRequest, 
    _: None = Depends(verify_key)
) -> Dict[str, Any]:
    
    all_case_studies = get_all_case_studies()
    
    # Export to CSV if requested
    csv_filename = None
    if req.export_csv:
        csv_filename = export_scoring_to_csv(req, all_case_studies)
    
    # Calculate similarity scores for all case studies
    scored_cases = []
    for case_study in all_case_studies:
        similarity_score = calculate_case_similarity(req, case_study)
        scored_cases.append({
            "case_study": case_study,
            "similarity_score": similarity_score
        })
    
    # Sort by similarity score (highest first)
    scored_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    # Return top 5 most similar cases
    top_cases = scored_cases[:5]
    
    response = {
        "similar_cases": [
            {
                "id": case["case_study"]["id"],
                "similarity_score": round(case["similarity_score"], 3)

            }
            for case in top_cases
        ]
    }
    
    return response