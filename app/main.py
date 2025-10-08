# main.py

from fastapi import FastAPI
from pydantic import BaseModel
from rag_chain import run_rag_pipeline

app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask_q(q: Query):
    answer = run_rag_pipeline(q.question)
    return {"answer": answer}
