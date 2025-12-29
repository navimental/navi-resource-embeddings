import os
from app.similarity_calculations.text_similarity import embed
from supabase import create_client

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]

supabase = create_client(url, key)

def get_all_case_studies():
    res = supabase.table("navigator_simulations").select("id", "state", "current_challenges", "first_session_notes", "additional_info", "child_age", "child_diagnoses", "child_stage", "child_notes").execute()
    return res.data

def get_all_resources():
    res = supabase.table("resources").select("id", "title", "description", "type", "source", "category", "topics", "recommend_if", "topics", "state", "organization", "default_navigator_note").execute()
    return res.data

def get_all_tasks():
    res = supabase.table("roadmap_tasks").select("id", "title", "description", "state", "category", "why", "what", "who", "diagnoses", "states", "insurance", "milestone", "age_min", "age_max").execute()
    return res.data

def add_embeddings_to_resources():
    resources = get_all_resources()
    for resource in resources:
        text_to_embed = f"{resource['title']} {resource['description']} {resource['category']} {resource['topics']} {resource['recommend_if']} {resource['organization']} {resource['default_navigator_note']}"
        embedding = embed(text_to_embed)
        if embedding:
            supabase.table("resource_embeddings").upsert({
                "resource_id": resource["id"], 
                "embedding": embedding
            }).execute()
        print("Added embedding for resource ID:", resource["id"])

def get_all_resources_with_embeddings():
    # Fetch resources and their embeddings separately, then join in Python
    resources = supabase.table("resources").select("*").execute()
    embeddings = supabase.table("resource_embeddings").select("resource_id", "embedding").execute()
    
    # Create a lookup dict for embeddings
    embedding_map = {e["resource_id"]: e["embedding"] for e in embeddings.data}
    
    # Attach embeddings to resources
    for resource in resources.data:
        resource["embedding"] = embedding_map.get(resource["id"])
    
    return resources.data

def match_similar_resources(query_text: str, match_count: int = 20, match_threshold: float = 0.5):
    """Use database vector search to find similar resources."""
    query_embedding = embed(query_text)
    if not query_embedding:
        return []
    
    # Use RPC call to database function for vector similarity search
    result = supabase.rpc('match_resources', {
        'query_embedding': query_embedding,
        'match_threshold': match_threshold,
        'match_count': match_count
    }).execute()
    
    return result.data

def get_user_profile_by_id(user_id: str):
    res = supabase.table("users").select("*").eq("user_id", user_id).single().execute()
    return res.data

def get_child_diagnoses_by_user_id(user_id: str):
    res = supabase.table("user_childs").select("*").eq("user_id", user_id).execute()

    # Combine all diagnoses into a single list
    all_diagnoses = []
    for child in res.data:
        diagnoses = child.get("diagnoses", [])
        if isinstance(diagnoses, list):
            all_diagnoses.extend(diagnoses)

    return all_diagnoses