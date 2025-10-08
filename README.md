# 🏫 CBIT College Chatbot

An **AI-powered chatbot** built for **Chaitanya Bharathi Institute of Technology (CBIT)** to handle student and visitor queries related to **admissions, courses, departments, faculty, placements, and events**.  

This chatbot provides instant, context-aware answers using **FastAPI**, **RAG pipelines**, and **language models**, making it easier for students and parents to get accurate information about the institution.

---

## 📚 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **CBIT College Chatbot** is designed to assist students, parents, and faculty with common queries about CBIT.  
It combines **FastAPI** for backend serving and **AI/NLP models** for intelligent response generation.  

It can:
- Retrieve answers from structured data or stored documents (like college FAQs).
- Understand natural language questions.
- Provide quick, conversational responses.

---

##  Features

✅ **Instant Query Responses** – Get instant answers to FAQs (like “What courses does CBIT offer?”).  
✅ **Context Awareness** – Maintains context for multi-turn conversations.  
✅ **RAG (Retrieval-Augmented Generation)** – Uses embedding-based document retrieval for factual accuracy.  
✅ **FastAPI Backend** – High-performance, async web framework powering the chatbot API.  
✅ **Modular Codebase** – Easy to update and maintain with separated logic for retrieval, chat, and serving.  
✅ **Future-Ready** – Can easily integrate with models like OpenAI GPT, LLaMA, or local embeddings.

---

##  Tech Stack

| Component | Technology |
|------------|-------------|
| Backend Framework | FastAPI |
| Server | Uvicorn |
| AI/NLP Model | Sentence Transformers / LLM (LLaMA / OpenAI GPT optional) |
| Data Retrieval | RAG Pipeline / Knowledge Base |
| Frontend | (Optional) HTML / JS / React UI |
| Language | Python 3.10+ |
| Environment Management | Virtualenv / venv |
| Deployment | Localhost or Cloud (Render, Railway, etc.) |

---

##  Project Structure
college-chatbot/
├── app/
│ ├── main.py # FastAPI entry point
│ ├── rag_chain.py # RAG pipeline / AI logic
│ ├── utils/ # Utility scripts (if any)
│ ├── services/ # Chat or summarization logic
│ ├── data/ # College info, FAQs, JSON data
│ └── init.py
├── requirements.txt # Dependencies
├── .env # Environment variables (ignored in Git)
├── .gitignore
└── README.md


---

## Installation & Setup

Follow these steps to set up and run the chatbot locally 👇  

##  Clone the Repository
```bash
git clone https://github.com/ksp0007/college-chatbot.git
cd college-chatbot
```
### Create a Virtual Environment and Activate it
```bash
python -m venv venv
venv\Scripts\activate
```
### Install Dependencies
``` bash
pip install -r requirements.txt
```
### Run the Application 
``` bash
uvicorn app.main:app --reload
```
✍️ Author

👤 Pavan Kumar (ksp0007)
🎓 B.Tech CSE (AI & ML), CBIT, Hyderabad
📧 kvsrdspk1@gmail.com

🌐 GitHub Profile




