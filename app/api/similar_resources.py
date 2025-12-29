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

def get_similar_resources_for_next_step(text) -> List[Dict[str, Any]]:
    from app.supabase_client import get_all_resources_with_embeddings
    from app.similarity_calculations.text_similarity import cosine_similarity, embed

    resources = get_all_resources_with_embeddings()
    input_embedding = embed(text)
    if input_embedding is None:
        return []

    scored_resources = []
    for resource in resources:
        resource_embedding = resource.get("embedding", {}).get("embedding")
        if resource_embedding:
            score = cosine_similarity(input_embedding, resource_embedding)
            scored_resources.append((score, resource))

    scored_resources.sort(key=lambda x: x[0], reverse=True)
    top_resources = [res for score, res in scored_resources[:5]]  # Return top 5 similar resources

    return top_resources