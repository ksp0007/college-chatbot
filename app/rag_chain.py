import os
import faiss
import numpy as np
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient
from sentence_transformers import SentenceTransformer

load_dotenv()

# Load local sentence embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # lightweight & fast

# Tavily client
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Constants
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

def search_web(query):
    results = tavily_client.search(query=query, max_results=1)
    if results and results["results"]:
        return results["results"][0]["content"]
    return "Sorry, I couldn't find any information on the web."

def load_and_split(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = []
    for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk = text[i:i + CHUNK_SIZE]
        chunks.append(chunk)
    return chunks

# Use real local semantic embedding
def get_embedding(text):
    return embedding_model.encode(text).astype("float32")

def build_index(chunks):
    dim = get_embedding("test").shape[0]
    index = faiss.IndexFlatL2(dim)
    vectors = [get_embedding(c) for c in chunks]
    index.add(np.array(vectors))
    return index, vectors

def retrieve(query, chunks, index, vectors, k=3):
    query_vec = get_embedding(query).reshape(1, -1)
    _, I = index.search(query_vec, k)
    return [chunks[i] for i in I[0]]

def ask_llm(context_chunks, query):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    system_prompt = (
        "You are a helpful assistant for a college website. "
        "The provided context may contain structured data like tables or lists. "
        "Extract **only factual information** strictly from the context. "
        "If the answer is not found, respond with: 'Not found in the provided data.'"
    )

    prompt = "The following is a structured list of designations and names. Use it to answer questions.\n\n"
    for i, chunk in enumerate(context_chunks):
        prompt += f"Chunk {i + 1}:\n{chunk}\n\n"
    prompt += f"Question: {query}\nAnswer:"

    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()


def run_rag_pipeline(user_query):
    current_dir = os.path.dirname(__file__)
    path = os.path.join(current_dir, "data", "college_info.txt")

    chunks = load_and_split(path)
    index, vectors = build_index(chunks)
    top_chunks = retrieve(user_query, chunks, index, vectors)
    answer = ask_llm(top_chunks, user_query)

    if answer.lower().startswith("not found") or "could not find" in answer.lower():
        web_answer = search_web(user_query)
        return f"(From web search)\n{web_answer}"

    return answer