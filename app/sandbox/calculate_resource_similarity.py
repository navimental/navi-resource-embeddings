import sys
import os
from typing import List, Dict, Any
import csv
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dotenv import load_dotenv
load_dotenv()

from app.supabase_client import match_similar_resources

text_cases = [
    "Get an IEP from school", 
    "Find a parent support group", 
    "Find a family therapist"
]

def calculate_resource_similarity_to_csv(test_cases: List[str]) -> str:
    """Calculate similarity scores for test cases against all resources and export to CSV."""
    
    # Create exports directory if it doesn't exist
    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{exports_dir}/resource_similarity_scores_{timestamp}.csv"
    
    # Calculate scores for each test case using database vector search
    all_rows = []
    for test_text in test_cases:
        print(f"Processing: {test_text}")
        
        # Get similar resources from database (already includes similarity scores)
        similar_resources = match_similar_resources(
            query_text=test_text,
            match_count=100,  # Get all resources to compare
            match_threshold=0.0  # No threshold, get all results
        )
        
        if not similar_resources:
            print(f"  Warning: No results returned for '{test_text}'")
            continue
        
        # Format results for CSV
        for resource in similar_resources:
            all_rows.append({
                "test_case": test_text,
                "resource_id": resource.get("resource_id", ""),
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
                "similarity_score": round(resource.get("similarity", 0), 4)
            })
        
        print(f"  Found {len(similar_resources)} similar resources")
    
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
    csv_file = calculate_resource_similarity_to_csv(text_cases)
    print(f"\nCompleted! Results saved to: {csv_file}")