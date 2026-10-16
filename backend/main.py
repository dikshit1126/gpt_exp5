from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
import json
import os
import tempfile
import ollama


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Automated Legal Document Analyzer",
    description="AI-powered legal document analysis using CUAD and Ollama"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "CUADv1.json"
)


# ============================================================
# CUAD 41 CATEGORIES
# ============================================================

CUAD_CATEGORIES = [
    "Document Name",
    "Parties",
    "Agreement Date",
    "Effective Date",
    "Expiration Date",
    "Renewal Term",
    "Notice Period To Terminate Renewal",
    "Governing Law",
    "Most Favored Nation",
    "Non-Compete",
    "Exclusivity",
    "No-Solicit Of Customers",
    "Competitive Restriction Exception",
    "No-Solicit Of Employees",
    "Non-Disparagement",
    "Termination For Convenience",
    "Rofr/Rofo/Rofn",
    "Change Of Control",
    "Anti-Assignment",
    "Revenue/Profit Sharing",
    "Price Restrictions",
    "Minimum Commitment",
    "Volume Restriction",
    "Ip Ownership Assignment",
    "Joint Ip Ownership",
    "License Grant",
    "Non-Transferable License",
    "Affiliate License-Licensor",
    "Affiliate License-Licensee",
    "Unlimited/All-You-Can-Eat-License",
    "Irrevocable Or Perpetual License",
    "Source Code Escrow",
    "Post-Termination Services",
    "Audit Rights",
    "Uncapped Liability",
    "Cap On Liability",
    "Liquidated Damages",
    "Warranty Duration",
    "Insurance",
    "Covenant Not To Sue",
    "Third Party Beneficiary",
]


# ============================================================
# REQUEST MODEL
# ============================================================

class DocumentRequest(BaseModel):
    document_text: str


# ============================================================
# LOAD CUAD DATASET
# ============================================================

def load_dataset():

    if not os.path.exists(DATASET_PATH):
        return {
            "version": "unknown",
            "contracts": 0,
            "categories": len(CUAD_CATEGORIES)
        }

    try:
        with open(
            DATASET_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return {
            "version": data.get("version", "unknown"),
            "contracts": len(data.get("data", [])),
            "categories": len(CUAD_CATEGORIES)
        }

    except Exception:
        return {
            "version": "unknown",
            "contracts": 0,
            "categories": len(CUAD_CATEGORIES)
        }


# ============================================================
# DATASET INFORMATION
# ============================================================

def get_dataset_info():
    return load_dataset()


# ============================================================
# AI DOCUMENT ANALYSIS
# ============================================================

def analyze_document(document_text):

    categories = "\n".join(
        f"- {category}"
        for category in CUAD_CATEGORIES
    )

    prompt = f"""
You are an Automated Legal Document Analyzer.

Analyze the legal document provided below.

Your task is to identify important information and clauses
based ONLY on the text provided.

IMPORTANT RULES:

1. Use ONLY information present in the document.
2. Do not invent facts.
3. Do not assume missing information.
4. If information is not present, write exactly:
   "Not specified".
5. This is an information extraction and summarization task.
6. Do not provide legal advice.
7. Do not make legal conclusions.
8. Keep the output structured and concise.
9. Preserve names, dates and clause information accurately.
10. If the document explicitly states a party's role,
    include the role when identifying the parties.
11. For Document Type, identify the type only when it can
    reasonably be determined from the document itself.
12. For Governing Law, extract the actual jurisdiction if
    explicitly stated. Do not replace it with a generic
    phrase such as "applicable law" unless that exact phrase
    is the only relevant information present.
13. For each clause category, provide the relevant clause
    or a concise extraction from the document.
14. If no relevant clause exists, write "Not specified".

CUAD LEGAL CATEGORIES:

{categories}

Return the result using exactly this structure:

LEGAL DOCUMENT ANALYSIS

Document Type:

Parties:
- 

Agreement Date:

Effective Date:

Expiration Date:

Renewal Term:

Notice Period To Terminate Renewal:

Governing Law:

KEY CLAUSES

Most Favored Nation:

Non-Compete:

Exclusivity:

No-Solicit Of Customers:

Competitive Restriction Exception:

No-Solicit Of Employees:

Non-Disparagement:

Termination For Convenience:

Rofr/Rofo/Rofn:

Change Of Control:

Anti-Assignment:

Revenue/Profit Sharing:

Price Restrictions:

Minimum Commitment:

Volume Restriction:

Ip Ownership Assignment:

Joint Ip Ownership:

License Grant:

Non-Transferable License:

Affiliate License-Licensor:

Affiliate License-Licensee:

Unlimited/All-You-Can-Eat-License:

Irrevocable Or Perpetual License:

Source Code Escrow:

Post-Termination Services:

Audit Rights:

Uncapped Liability:

Cap On Liability:

Liquidated Damages:

Warranty Duration:

Insurance:

Covenant Not To Sue:

Third Party Beneficiary:

SUMMARY:

Provide a concise summary based only on the document.

DOCUMENT:

{document_text}
"""

    response = ollama.chat(
        model="llama3.2:latest",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(file_path):

    reader = PdfReader(file_path)

    extracted_text = ""

    for page_number, page in enumerate(reader.pages, start=1):

        try:
            text = page.extract_text()

            if text:
                extracted_text += (
                    f"\n\n--- PAGE {page_number} ---\n\n"
                    + text
                )

        except Exception as e:

            print(
                f"Warning: Could not extract page "
                f"{page_number}: {e}"
            )

    return extracted_text.strip(), len(reader.pages)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Automated Legal Document Analyzer API is running"
    }


# ============================================================
# DATASET INFO
# ============================================================

@app.get("/dataset-info")
def dataset_info():

    return get_dataset_info()


# ============================================================
# CATEGORIES
# ============================================================

@app.get("/categories")
def categories():

    return {
        "categories": CUAD_CATEGORIES,
        "count": len(CUAD_CATEGORIES)
    }


# ============================================================
# ANALYZE TEXT
# ============================================================

@app.post("/analyze")
def analyze(request: DocumentRequest):

    if not request.document_text.strip():

        raise HTTPException(
            status_code=400,
            detail="Document text cannot be empty."
        )

    try:

        result = analyze_document(
            request.document_text
        )

        return {
            "success": True,
            "analysis": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Document analysis failed: {str(e)}"
        )


# ============================================================
# ANALYZE PDF
# ============================================================

@app.post("/analyze-pdf")
async def analyze_pdf(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Check filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file was provided."
        )

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )


    temp_path = None

    try:

        # ----------------------------------------------------
        # Read uploaded PDF
        # ----------------------------------------------------

        contents = await file.read()

        if not contents:

            raise HTTPException(
                status_code=400,
                detail="The uploaded PDF is empty."
            )


        # ----------------------------------------------------
        # Create temporary file
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(contents)

            temp_path = temp_file.name


        # ----------------------------------------------------
        # Extract PDF text
        # ----------------------------------------------------

        extracted_text, page_count = extract_pdf_text(
            temp_path
        )


        if not extracted_text.strip():

            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not extract text from this PDF. "
                    "The PDF may contain scanned images instead "
                    "of selectable text."
                )
            )


        # ----------------------------------------------------
        # Analyze extracted text
        # ----------------------------------------------------

        result = analyze_document(
            extracted_text
        )


        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return {
            "success": True,
            "filename": file.filename,
            "pages": page_count,
            "extracted_characters": len(extracted_text),
            "analysis": result
        }


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(e)}"
        )


    finally:

        # ----------------------------------------------------
        # Remove temporary PDF
        # ----------------------------------------------------

        if temp_path and os.path.exists(temp_path):

            try:
                os.remove(temp_path)

            except Exception:
                pass
