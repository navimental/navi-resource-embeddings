from dotenv import load_dotenv

# Load .env BEFORE importing any routers or deps
load_dotenv()

from app.supabase_client import add_embeddings_to_resources

if __name__ == "__main__":
    print("Starting resource embeddings update...")
    add_embeddings_to_resources()
    print("Resource embeddings update completed.")