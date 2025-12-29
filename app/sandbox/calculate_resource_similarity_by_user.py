import sys
import os
from typing import List, Dict, Any
import csv
from datetime import datetime
import json
import numpy as np

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dotenv import load_dotenv
load_dotenv()

from app.supabase_client import get_all_resources_with_embeddings
from app.similarity_calculations.text_similarity import cosine_similarity, embed
from app.supabase_client import get_user_profile_by_id, get_child_diagnoses_by_user_id

user_examples = [
    "fa26393b-bf47-4fb0-b3fd-01c13903d06b"
]

def calculate_resource_similarity_to_csv(test_cases: List[str]) -> str:
    """Calculate similarity scores for test cases against all resources and export to CSV."""
    
    # Create exports directory if it doesn't exist
    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{exports_dir}/resource_similarity_scores_user_{timestamp}.csv"
    
    # Get all resources with embeddings
    resources = get_all_resources_with_embeddings()

    # Get user data

    users_data = []
    for user_id in test_cases:
        user_profile = get_user_profile_by_id(user_id)
        child_diagnoses = get_child_diagnoses_by_user_id(user_id)
        combined_text = f"{user_profile.get('current_challenges', '')} {user_profile.get('first_session_notes', '')} {user_profile.get('additional_info', '')} {' '.join(child_diagnoses)}"
        users_data.append((user_id, combined_text))
    
    # Calculate scores for each test case
    all_rows = []
    for user_id, test_text in users_data:
        print(f"Processing: {test_text}")
        input_embedding = embed(test_text)
        
        if input_embedding is None:
            print(f"  Warning: Could not generate embedding for '{test_text}'")
            continue
        
        for resource in resources:
            # Handle the embedding structure - it's a list with a dict inside
            embedding_data = resource.get("embedding", [])
            resource_embedding = None
            
            if embedding_data and len(embedding_data) > 0:
                raw_embedding = embedding_data[0].get("embedding")
                
                # Parse the embedding if it's a string
                if isinstance(raw_embedding, str):
                    try:
                        # Try parsing as JSON first
                        resource_embedding = json.loads(raw_embedding)
                    except json.JSONDecodeError:
                        # If that fails, it might be a numpy array string representation
                        try:
                            resource_embedding = eval(raw_embedding)
                        except:
                            print(f"  Warning: Could not parse embedding for resource {resource.get('id')}")
                            continue
                elif isinstance(raw_embedding, list):
                    resource_embedding = raw_embedding
                else:
                    resource_embedding = raw_embedding
            
            if resource_embedding:
                try:
                    score = cosine_similarity(input_embedding, resource_embedding)
                    
                    all_rows.append({
                        "test_case": test_text,
                        "resource_id": resource.get("id", ""),
                        "resource_title": resource.get("title", ""),
                        "resource_description": resource.get("description", ""),
                        "resource_type": resource.get("type", ""),
                        "resource_source": resource.get("source", ""),
                        "resource_category": resource.get("category", ""),
                        "resource_topics": ", ".join(resource.get("topics", [])) if resource.get("topics") else "",
                        "resource_recommend_if": resource.get("recommend_if", ""),
                        "resource_state": resource.get("state", ""),
                        "resource_organization": resource.get("organization", ""),
                        "resource_default_navigator_note": resource.get("default_navigator_note", ""),
                        "similarity_score": round(score, 4)
                    })
                except Exception as e:
                    print(f"  Warning: Error calculating similarity for resource {resource.get('id')}: {e}")
    
    # Sort by test case, then by similarity score (highest first)
    all_rows.sort(key=lambda x: (x["test_case"], -x["similarity_score"]))
    
    # Write to CSV
    fieldnames = [
        "test_case",
        "resource_id",
        "resource_title",
        "resource_description",
        "resource_type",
        "resource_source",
        "resource_category",
        "resource_topics",
        "resource_recommend_if",
        "resource_state",
        "resource_organization",
        "resource_default_navigator_note",
        "similarity_score"
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"\nCSV exported to: {filename}")
    print(f"Total rows: {len(all_rows)}")
    
    return filename

if __name__ == "__main__":
    print("Starting resource similarity calculation...\n")
    csv_file = calculate_resource_similarity_to_csv(user_examples)
    print(f"\nCompleted! Results saved to: {csv_file}")