from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.rag_chain import run_rag_pipeline
from app.placement_engine import handle_placement_query

app = FastAPI()

# ✅ CORS (REQUIRED for React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React CRA port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask_q(q: Query):
    question = q.question.lower()

    placement_keywords = ["placement", "placed", "package", "ctc", "company"]

    if any(word in question for word in placement_keywords):
        answer = handle_placement_query(q.question)
    else:
        answer = run_rag_pipeline(q.question)

    return {"answer": answer}

