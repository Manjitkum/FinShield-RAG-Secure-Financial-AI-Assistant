from langchain_community.embeddings import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

blacklist_prompts = [
    "avoid reporting thresholds",
    "evade fraud detection",
    "structure transactions to hide money",
    "money laundering techniques",
    "hide source of funds",
    "bypass transaction limits"
]

user_query = "How do I make a large transaction that avoids RBI reporting thresholds?"

print(f"Query: {user_query}")
print("-" * 50)

query_embedding = embeddings.embed_query(user_query)
blacklist_embeddings = embeddings.embed_documents(blacklist_prompts)

similarities = cosine_similarity([query_embedding], blacklist_embeddings)[0]

for i, prompt in enumerate(blacklist_prompts):
    print(f"Score: {similarities[i]:.4f} | Prompt: {prompt}")

print("-" * 50)
print(f"Max Similarity: {np.max(similarities):.4f}")