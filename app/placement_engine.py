import os
import re
import json
import sqlite3
import pandas as pd
import requests
from difflib import SequenceMatcher
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIG ====================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.1-8b-instant"

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR,"data", "students.db")
CSV_PATH = os.path.join(BASE_DIR, "data", "Year-wise-Placements-2024-25-In-Progress copy.csv")

# ==================== INITIALIZE DATABASE ====================

def initialize_database():
    if os.path.exists(DB_PATH):
        return  # Don't rebuild every reload

    print("Loading placement CSV...")

    # Read CSV (actual header is at row index 2)
    df = pd.read_csv(CSV_PATH, header=3)

    # Clean column names
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace("\r", "", regex=True)
    df.columns = df.columns.str.replace("\n", " ", regex=True)

    # Detect important columns dynamically
    company_candidates = [col for col in df.columns if "Organ" in col or "Company" in col]
    if not company_candidates:
        raise Exception(f"Company column not found. Available columns: {df.columns.tolist()}")
    company_col = company_candidates[0]

    designation_candidates = [col for col in df.columns if "Designation" in col]
    if not designation_candidates:
        raise Exception(f"Designation column not found. Available columns: {df.columns.tolist()}")
    designation_col = designation_candidates[0]

    ctc_candidates = [col for col in df.columns if "CTC" in col]
    if not ctc_candidates:
        raise Exception(f"CTC column not found. Available columns: {df.columns.tolist()}")
    ctc_col = ctc_candidates[0]


    df["Company"] = df[company_col].astype(str).str.strip()
    df["Designation"] = df[designation_col].astype(str).str.strip()

    df["CTC_LPA"] = pd.to_numeric(
        df[ctc_col].astype(str).str.replace(r"[^0-9.\-]", "", regex=True),
        errors="coerce"
    ).fillna(0)

    # Department columns
    DEPT_COLS = [
        'CSE', 'IT', 'CSE (AIML)', 'AIML', 'AIDS', 'CSE (IOT, CS&BCT)',
        'ECE', 'EEE', 'MECH', 'CIVIL', 'CHEM', 'Bio- Tech', 'MCA',
        'MTech/ CSE', 'MTech/ AIDS', 'M.E/ Comm', 'ME / VLSI & ESVD',
        'M.E/ PSPE', 'M.E/ Cad/Cam', 'ME/ Thermal', 'ME/ Struc', 'MBA'
    ]

    rows = []

    for _, r in df.iterrows():
        for dep in DEPT_COLS:
            if dep in df.columns:
                count = pd.to_numeric(r.get(dep, 0), errors="coerce")
                if pd.notna(count):
                    for _ in range(int(count)):
                        rows.append({
                            "Department": dep,
                            "Placed": "Yes",
                            "Company": r["Company"],
                            "Designation": r["Designation"],
                            "CTC_LPA": r["CTC_LPA"],
                        })

    students = pd.DataFrame(rows)

    with sqlite3.connect(DB_PATH) as conn:
        students.to_sql("students", conn, if_exists="replace", index=False)

    print(f"Database ready with {len(students)} rows.")


initialize_database()

# ==================== LOAD ENTITIES ====================

def load_entities():
    with sqlite3.connect(DB_PATH) as conn:
        companies = pd.read_sql("SELECT DISTINCT Company FROM students;", conn)["Company"].tolist()
        departments = pd.read_sql("SELECT DISTINCT Department FROM students;", conn)["Department"].tolist()
    return companies, departments


company_list, dept_list = load_entities()
company_lookup = {c.lower(): c for c in company_list}
dept_lookup = {d.lower(): d for d in dept_list}

# ==================== ENTITY EXTRACTION ====================

ENTITY_PROMPT = """
Extract ONLY company and department from the query.
Return JSON:
{
  "company": "...",
  "department": "..."
}
If not present, return null.
"""

def extract_entities(query: str):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": ENTITY_PROMPT + f"\nQuery: {query}"}],
        "temperature": 0
    }

    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload)
        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content)
    except:
        return {"company": None, "department": None}

# ==================== FUZZY MATCH ====================

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]", "", text)
    return text

def match_entity_to_db(entity: str, lookup_dict: dict, threshold: float = 0.6):
    if not entity:
        return None

    norm_entity = normalize_text(entity)
    best_match = None
    best_score = 0

    for key, original in lookup_dict.items():
        score = SequenceMatcher(None, norm_entity, key).ratio()
        if score > best_score:
            best_score = score
            best_match = original

    return best_match if best_score >= threshold else None

# ==================== SQL GENERATION ====================

SYSTEM_PROMPT = """
You generate SQLite queries only.

Table: students
Columns: Department, Placed, Company, Designation, CTC_LPA

Rules:
- Use LOWER(column) LIKE '%value%' for filtering
- Use COUNT(*) when counting students
- When asking about CTC or package, use CTC_LPA column
- For highest package use MAX(CTC_LPA)
- For average package use AVG(CTC_LPA)
- Always include Placed='Yes' when counting placements
- Return ONLY SQL query
"""



def english_to_sql(question: str):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        "temperature": 0
    }

    resp = requests.post(GROQ_API_URL, headers=headers, json=payload)
    sql = resp.json()["choices"][0]["message"]["content"].strip()

    if not sql.endswith(";"):
        sql += ";"

    return sql

# ==================== RUN SQL ====================

def run_sql(sql):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql(sql, conn)
    except:
        return pd.DataFrame()

# ==================== MAIN HANDLER ====================

def handle_placement_query(question: str):
    entities = extract_entities(question)

    matched_company = match_entity_to_db(
        entities.get("company"), company_lookup
    )
    matched_dept = match_entity_to_db(
        entities.get("department"), dept_lookup
    )

    rewritten = question
    if matched_company:
        rewritten += f" (company: {matched_company})"
    if matched_dept:
        rewritten += f" (department: {matched_dept})"

    sql = english_to_sql(rewritten)
    result = run_sql(sql)

    if result.empty:
        return "No placement data found."

    # ---- If single value result (COUNT / MAX / AVG / DISTINCT etc.) ----
    if len(result.columns) == 1:
        value = result.iloc[0, 0]
        column_name = result.columns[0].lower()

        # COUNT queries
        if "count" in column_name:
            if matched_company:
                return f"{value} students were placed in {matched_company}."
            elif matched_dept:
                return f"{value} students were placed from {matched_dept}."
            else:
                return f"{value} students were placed."

        # CTC / MAX / AVG queries
        if "ctc" in column_name or "max" in column_name or "avg" in column_name:
            if matched_company:
                return f"The CTC offered by {matched_company} is {value} LPA."
            elif matched_dept:
                return f"The CTC for {matched_dept} is {value} LPA."
            else:
                return f"The CTC is {value} LPA."

        # Fallback for other single value queries
        return f"{value}"

    # ---- If multiple rows (table result) ----
    return result.to_string(index=False)


