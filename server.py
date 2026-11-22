"""
Tata AIA Life Insurance Form Filler - FastAPI Backend Server
Provides Document OCR Extraction, Handwriting Form Generation, and Mobile PWA API.
"""

import os
import re
import uuid
import socket
import json
import io
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pymupdf

from form_filler import fill_tata_aia_form
from document_extractor import extract_from_file, extract_nominee_from_file

app = FastAPI(title="Tata AIA Form Filler API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
BLANK_FORM_PATH = os.path.join(BASE_DIR, "Blank form.pdf")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def get_local_ip():
    """Detects primary local LAN IPv4 address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Tata AIA Form Filler is running. Place index.html in /static</h1>"

@app.get("/api/system-info")
async def get_system_info():
    ip = get_local_ip()
    port = 8000
    mobile_url = f"http://{ip}:{port}"
    return {
        "local_ip": ip,
        "port": port,
        "mobile_url": mobile_url,
        "message": f"Open on your Android phone browser: {mobile_url}"
    }

@app.post("/api/extract")
async def extract_documents(
    files: Optional[List[UploadFile]] = File(None),
    file_nominee: Optional[List[UploadFile]] = File(None),
    doc_types: Optional[str] = Form(None)
):
    """
    Accepts one or more uploaded KYC / loan files (Aadhaar, PAN, Passbook, Loan Sheet),
    as well as dedicated Nominee ID document.
    Runs OCR and merges extracted information.
    """
    merged_data = {}
    saved_paths = []
    processed_count = 0
    has_aadhaar_name = False

    if files:
        for file in files:
            if not file.filename:
                continue
            file_ext = os.path.splitext(file.filename)[1].lower() or ".jpg"
            temp_filename = f"upload_{uuid.uuid4().hex[:8]}{file_ext}"
            temp_path = os.path.join(OUTPUTS_DIR, temp_filename)

            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)

            saved_paths.append(temp_path)
            processed_count += 1

            try:
                extracted = extract_from_file(temp_path)
                # If Aadhaar front name is found, lock customer_name to it with highest priority
                if extracted.get("aadhaar_name"):
                    merged_data["customer_name"] = extracted["aadhaar_name"]
                    has_aadhaar_name = True

                for k, v in extracted.items():
                    if k == "customer_name" and has_aadhaar_name:
                        continue
                    if v and (k not in merged_data or not merged_data[k]):
                        merged_data[k] = v
            except Exception as e:
                print(f"Error extracting from {file.filename}: {e}")

    # Always ensure annual income is 200000
    merged_data["annual_income"] = "200000"

    # Process dedicated Nominee document(s) if uploaded
    if file_nominee:
        nom_list = file_nominee if isinstance(file_nominee, list) else [file_nominee]
        for nom_file in nom_list:
            if not nom_file or not nom_file.filename:
                continue
            nom_ext = os.path.splitext(nom_file.filename)[1].lower() or ".jpg"
            nom_filename = f"upload_nominee_{uuid.uuid4().hex[:8]}{nom_ext}"
            nom_path = os.path.join(OUTPUTS_DIR, nom_filename)

            with open(nom_path, "wb") as f:
                content = await nom_file.read()
                f.write(content)

            saved_paths.append(nom_path)
            processed_count += 1

            try:
                nominee_extracted = extract_nominee_from_file(nom_path)
                for k, v in nominee_extracted.items():
                    if v and (k not in merged_data or not merged_data[k]):
                        merged_data[k] = v
            except Exception as e:
                print(f"Error extracting nominee from {nom_file.filename}: {e}")

    return {
        "success": True,
        "extracted_data": merged_data,
        "uploaded_files_count": processed_count
    }

@app.post("/api/generate")
async def generate_form(
    data_str: str = Form(...),
    calc_file: Optional[UploadFile] = File(None),
    customer_sig_file: Optional[UploadFile] = File(None),
    witness_sig_file: Optional[UploadFile] = File(None)
):
    """
    Generates the filled Tata AIA Member Enrollment Form PDF with human handwriting overlay.
    Stamps borrower and witness signatures if provided.
    Returns preview image URLs and download URL.
    """
    try:
        data = json.loads(data_str)
        data["annual_income"] = "200000"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid form data JSON: {e}")

    # Ensure all text fields are UPPERCASE
    clean_data = {}
    for k, v in data.items():
        if isinstance(v, str):
            clean_data[k] = v.upper().strip()
        else:
            clean_data[k] = v
    data = clean_data

    raw_name = data.get("borrower_name", data.get("customer_name", "BORROWER"))
    clean_borrower = re.sub(r'[^A-Za-z0-9]', '_', str(raw_name).strip().upper()).strip('_') or "BORROWER"
    job_id = uuid.uuid4().hex[:10]
    out_pdf_name = f"{clean_borrower}_{job_id}.pdf"
    out_pdf_path = os.path.join(OUTPUTS_DIR, out_pdf_name)

    calc_path = None
    if calc_file and calc_file.filename:
        calc_ext = os.path.splitext(calc_file.filename)[1].lower()
        calc_path = os.path.join(OUTPUTS_DIR, f"calc_{job_id}{calc_ext}")
        with open(calc_path, "wb") as f:
            f.write(await calc_file.read())

    # Handle Customer Signature file
    borrower_sig = data.get("borrower_signature")
    if customer_sig_file and customer_sig_file.filename:
        c_ext = os.path.splitext(customer_sig_file.filename)[1].lower() or ".png"
        borrower_sig = os.path.join(OUTPUTS_DIR, f"sig_borrower_{job_id}{c_ext}")
        with open(borrower_sig, "wb") as f:
            f.write(await customer_sig_file.read())

    # Handle Witness Signature file
    witness_sig = data.get("witness_signature")
    if witness_sig_file and witness_sig_file.filename:
        w_ext = os.path.splitext(witness_sig_file.filename)[1].lower() or ".png"
        witness_sig = os.path.join(OUTPUTS_DIR, f"sig_witness_{job_id}{w_ext}")
        with open(witness_sig, "wb") as f:
            f.write(await witness_sig_file.read())

    # Generate PDF
    fill_tata_aia_form(
        BLANK_FORM_PATH,
        out_pdf_path,
        data,
        calculator_sheet_path=calc_path,
        borrower_signature=borrower_sig,
        witness_signature=witness_sig
    )

    # Render preview images for each page
    doc = pymupdf.open(out_pdf_path)
    page_urls = []
    for i in range(len(doc)):
        pix = doc[i].get_pixmap(dpi=150)
        img_name = f"preview_{job_id}_p{i}.png"
        img_path = os.path.join(OUTPUTS_DIR, img_name)
        pix.save(img_path)
        page_urls.append(f"/api/preview/{job_id}/{i}")
    doc.close()

    return {
        "success": True,
        "job_id": job_id,
        "download_url": f"/api/download/{job_id}",
        "pages": page_urls,
        "total_pages": len(page_urls)
    }

@app.get("/api/preview/{job_id}/{page_idx}")
async def get_preview(job_id: str, page_idx: int):
    img_name = f"preview_{job_id}_p{page_idx}.png"
    img_path = os.path.join(OUTPUTS_DIR, img_name)
    if os.path.exists(img_path):
        return FileResponse(img_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Preview not found")

@app.get("/api/download/{job_id}")
async def download_pdf(job_id: str):
    matches = [f for f in os.listdir(OUTPUTS_DIR) if job_id in f and f.endswith(".pdf")]
    if matches:
        pdf_name = matches[0]
        pdf_path = os.path.join(OUTPUTS_DIR, pdf_name)
        stem = pdf_name[:-4]
        if f"_{job_id}" in stem:
            clean_name = stem.replace(f"_{job_id}", "")
        else:
            clean_name = stem
        clean_name = clean_name.strip('_').upper() or "BORROWER"
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{clean_name}.pdf"
        )
    raise HTTPException(status_code=404, detail="Generated PDF not found")

if __name__ == "__main__":
    import uvicorn
    local_ip = get_local_ip()
    port = 8000
    print("\n" + "="*60)
    print("   TATA AIA AUTO FORM FILLER - SERVER READY")
    print(f"   PC Local Access:    http://localhost:{port}")
    print(f"   Android Phone Access: http://{local_ip}:{port}")
    print("="*60 + "\n")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
