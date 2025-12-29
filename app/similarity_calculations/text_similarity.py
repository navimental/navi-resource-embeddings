from typing import Optional
from openai import OpenAI
import numpy as np

client = OpenAI()

def cosine_similarity(a, b) -> float:
    a = np.array(a)
    b = np.array(b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

def embed(text: str) -> Optional[list]:
    try:
        res = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return res.data[0].embedding
    except Exception:
        return None


def text_similarity_score(input_text: str, case_text: str) -> float:
    print("Calculating similarity score")
    if not input_text or not case_text:
        return 0.0

    a = input_text.strip()
    b = case_text.strip()

    if not a or not b:
        return 0.0

    print("Generating embeddings for input text")
    emb_a = embed(a)
    print("Generating embeddings for case text")
    emb_b = embed(b)

    if emb_a is None or emb_b is None:
        return 0.0

    print("Calculating cosine similarity")
    return cosine_similarity(emb_a, emb_b)
