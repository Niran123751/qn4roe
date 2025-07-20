from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import re

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    content = await file.read()
    
    # Read CSV with flexible handling
    try:
        df = pd.read_csv(io.BytesIO(content), encoding='utf-8', engine='python')
    except Exception:
        return {"error": "Could not read the CSV file."}

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Try to locate likely category and amount columns
    category_col = next((col for col in df.columns if "category" in col), None)
    amount_col = next((col for col in df.columns if "amount" in col), None)

    if not category_col or not amount_col:
        return {"error": "Required columns not found in CSV."}

    # Clean category values
    df[category_col] = df[category_col].astype(str).str.strip().str.lower()

    # Clean amount: remove currency symbols, commas, spaces
    df[amount_col] = (
        df[amount_col].astype(str)
        .str.replace(",", "")
        .str.extract(r"([\d.]+)")[0]
        .astype(float)
    )

    # Filter by 'food' category and calculate sum
    total = df[df[category_col] == "food"][amount_col].sum()

    return {
        "answer": round(total, 2),
        "email": "24f2005647@ds.study.iitm.ac.in",
        "exam": "tds-2025-05-roe"
    }
