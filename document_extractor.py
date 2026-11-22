"""
Intelligent Document Extraction Engine for Indian KYC & Banking Documents
Extracts structured customer data from Aadhaar, PAN, Bank Passbook/Cheque, and Tata AIA Loan Sheets.
"""

import re
import os
import pymupdf
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

ocr_engine = RapidOCR()

MONTH_MAP = {
    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
    'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
}

IFSC_BANK_MAP = {
    "BARB": "BANK OF BARODA",
    "SBIN": "STATE BANK OF INDIA",
    "MAHG": "MAHARASHTRA GRAMIN BANK",
    "UTIB": "AXIS BANK",
    "HDFC": "HDFC BANK",
    "ICIC": "ICICI BANK",
    "PUNB": "PUNJAB NATIONAL BANK",
    "CNRB": "CANARA BANK",
    "UBIN": "UNION BANK OF INDIA",
    "MAHB": "BANK OF MAHARASHTRA",
    "IBKL": "IDBI BANK",
    "CBIN": "CENTRAL BANK OF INDIA",
    "IOBA": "INDIAN OVERSEAS BANK",
    "IDFB": "IDFC FIRST BANK",
    "KKBK": "KOTAK MAHINDRA BANK",
    "INDB": "INDUSIND BANK",
    "YESB": "YES BANK",
    "BDBL": "BANDHAN BANK",
    "CORP": "CORPORATION BANK",
    "ANDB": "ANDHRA BANK",
    "ALLA": "ALLAHABAD BANK",
    "SYNB": "SYNDICATE BANK",
    "VIJB": "VIJAYA BANK",
    "UCBA": "UCO BANK",
    "BKDN": "DENA BANK",
    "ORBC": "ORIENTAL BANK OF COMMERCE"
}

def clean_ocr_text(lines):
    return [l[1].strip() for l in lines if l and len(l) > 1 and l[1].strip()]

def parse_date_to_ddmmyyyy(raw_str):
    if not raw_str:
        return ""
    raw = raw_str.strip()
    
    # Check DD-Mon-YY (e.g. 01-Jan-92, 15-Jun-92, 15-Oct-26, 04-Jan-91)
    m = re.search(r'(\d{1,2})[-/ ]([A-Za-z]{3})[-/ ](\d{2,4})', raw)
    if m:
        d = m.group(1).zfill(2)
        mon = MONTH_MAP.get(m.group(2).lower()[:3], '01')
        y = m.group(3)
        if len(y) == 2:
            y_int = int(y)
            y = f"19{y}" if y_int >= 40 else f"20{y}"
        return f"{d}/{mon}/{y}"
        
    # Check DD/MM/YYYY or DD-MM-YYYY
    m = re.search(r'(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})', raw)
    if m:
        return f"{m.group(1).zfill(2)}/{m.group(2).zfill(2)}/{m.group(3)}"
        
    # Check YYYY alone
    m = re.search(r'\b(19\d{2}|20\d{2})\b', raw)
    if m:
        return f"01/01/{m.group(1)}"
        
    return ""

def extract_from_ocr_lines(lines_text):
    full_text = "\n".join(lines_text)
    data = {}

    # 1. PAN Pattern: 5 letters, 4 digits, 1 letter (e.g. EENPK3248L, FBZPS3059A)
    pan_match = re.search(r'\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b', full_text.upper())
    if pan_match:
        data["pan"] = pan_match.group(1)

    # 2. IFSC Code: 4 letters, 0 (or OCR'd O/Q), 6 letters/digits
    ifsc_match = re.search(r'\b([A-Z]{4})[0OQ]([A-Z0-9]{6})\b', full_text.upper())
    bank_name = None
    if ifsc_match:
        norm_ifsc = f"{ifsc_match.group(1)}0{ifsc_match.group(2)}"
        data["ifsc_code"] = norm_ifsc
        prefix = norm_ifsc[:4]
        if prefix in IFSC_BANK_MAP:
            bank_name = IFSC_BANK_MAP[prefix]

    # 3. PIN Code: 6 digits (Indian PIN)
    pin_match = re.search(r'\b([1-9][0-9]{5})\b', full_text)
    if pin_match:
        data["pincode"] = pin_match.group(1)

    # 4. Mobile Number: 10 digits starting with 6, 7, 8, 9
    mob_match = re.search(r'\b([6-9][0-9]{9})\b', full_text)
    if mob_match:
        data["mobile"] = mob_match.group(1)

    # 5. Loan Calculator extraction
    for i, line in enumerate(lines_text):
        clean_line = re.sub(r'[^a-zA-Z0-9]', '', line).lower()

        # Borrower Name
        if 'borrowername' in clean_line:
            for offset in [0, 1, 2]:
                if i + offset < len(lines_text):
                    cand = lines_text[i + offset].strip()
                    cand_clean = re.sub(r'borrower\s*name\s*[:\-]?', '', cand, flags=re.I).strip()
                    if cand_clean and len(cand_clean) > 3 and not re.search(r'joint|birth|input|date|name', cand_clean, re.I):
                        data["customer_name"] = cand_clean.upper()
                        break

        # Date of Birth
        if 'dateofbirth' in clean_line or 'dateof birth' in clean_line:
            for offset in [0, 1, 2]:
                if i + offset < len(lines_text):
                    cand = lines_text[i + offset].strip()
                    parsed_dob = parse_date_to_ddmmyyyy(cand)
                    if parsed_dob:
                        data["dob"] = parsed_dob
                        break

        # Gender
        if 'gender' in clean_line:
            for offset in [0, 1, 2]:
                if i + offset < len(lines_text):
                    cand = lines_text[i + offset].strip().lower()
                    if 'female' in cand:
                        data["gender"] = "Female"
                        break
                    elif 'male' in cand:
                        data["gender"] = "Male"
                        break

        # Loan Term (years) -> convert to months
        if 'loanterm' in clean_line:
            for offset in [0, 1, 2]:
                if i + offset < len(lines_text):
                    cand = lines_text[i + offset].strip()
                    digits = re.findall(r'\b\d+\b', cand)
                    if digits:
                        years = int(digits[0])
                        if 1 <= years <= 30:
                            months = years * 12
                            data["loan_term"] = str(months)
                            data["base_coverage_term"] = str(months)
                            break

        # Final Sum Assured
        if 'finalsumassured' in clean_line:
            for offset in [0, 1, 2]:
                if i + offset < len(lines_text):
                    cand = lines_text[i + offset].strip()
                    clean_num = "".join(filter(str.isdigit, cand))
                    if clean_num and len(clean_num) >= 4:
                        data["loan_amount"] = clean_num
                        data["base_sum_assured"] = clean_num
                        break

        # Total Premium
        if 'totalpremium' in clean_line:
            for offset in [0, 1, 2]:
                if i + offset < len(lines_text):
                    cand = lines_text[i + offset].strip()
                    clean_prem = "".join(filter(str.isdigit, cand))
                    if clean_prem and len(clean_prem) >= 3:
                        data["premium_amount"] = clean_prem
                        break

    # 5b. Aadhaar Card Extraction (Customer Name strictly as per Aadhaar Front)
    is_aadhaar = any(k in full_text.upper() for k in [
        "GOVERNMENT OF INDIA", "UIDAI", "UNIQUE IDENTIFICATION", "AADHAAR", "MERA AADHAAR"
    ]) or bool(re.search(r'\b[2-9][0-9]{3}\s[0-9]{4}\s[0-9]{4}\b', full_text)) or bool(re.search(r'\b[0-9]{12}\b', full_text))

    has_dob = bool(re.search(r'(?:DOB|Date of Birth|Birth|Year of Birth)', full_text, re.I))
    has_gender = bool(re.search(r'\b(Male|Female)\b', full_text, re.I))
    has_address_kw = bool(re.search(r'\bAddress\b', full_text, re.I))
    is_aadhaar_front = is_aadhaar and (has_dob or has_gender) and not has_address_kw

    if is_aadhaar_front:
        AADHAAR_BLACKLIST = {
            'GOVERNMENT', 'INDIA', 'AUTHORITY', 'ENROLMENT', 'ENROLLMENT', 'UNIQUE',
            'HELP', 'ADDRESS', 'FATHER', 'HUSBAND', 'MALE', 'FEMALE', 'DOB', 'BIRTH',
            'CARD', 'AADHAAR', 'UIDAI', 'STATE', 'DEPARTMENT', 'MAHARASHTRA', 'MERA',
            'YEAR', 'VID', 'INCOME', 'TAX', 'ACCOUNT', 'NUMBER', 'SIGNATURE', 'GOVT',
            'BHARAT', 'SARKAR', 'PURUSH', 'STREE', 'ENROLLMENTNO'
        }

        def score_aadhaar_name_candidate(line_str):
            clean = re.sub(r'[^A-Za-z\s]', ' ', line_str).strip()
            words = [w for w in clean.split() if len(w) >= 2]
            if not words or len(words) > 5:
                return None, 0
            for w in words:
                if w.upper() in AADHAAR_BLACKLIST:
                    return None, 0
            vowel_words = [w for w in words if re.search(r'[aeiouAEIOU]', w)]
            if len(vowel_words) < len(words):
                return None, 0
            norm_name = ' '.join(words).upper()
            if len(norm_name) < 4:
                return None, 0
            score = len(words) * 20 + min(len(norm_name), 30)
            return norm_name, score

        dob_idx = None
        for i, l in enumerate(lines_text):
            if re.search(r'(?:DOB|Date of Birth|Birth|Year of Birth)', l, re.I):
                dob_idx = i
                break

        gov_idx = None
        for i, l in enumerate(lines_text):
            if "GOVERNMENT OF INDIA" in l.upper() or "BHARAT SARKAR" in l.upper():
                gov_idx = i
                break

        best_name = None
        best_score = -1

        for i, l in enumerate(lines_text):
            norm_cand, cand_score = score_aadhaar_name_candidate(l)
            if not norm_cand:
                continue

            dist_bonus = 0
            if dob_idx is not None:
                dist = abs(i - dob_idx)
                if dist in [1, 2, 3]:
                    dist_bonus += (10 - dist * 2)
            if gov_idx is not None:
                dist = abs(i - gov_idx)
                if dist in [1, 2, 3]:
                    dist_bonus += (8 - dist * 2)

            total_score = cand_score + dist_bonus
            if total_score > best_score:
                best_score = total_score
                best_name = norm_cand

        if best_name:
            data["aadhaar_name"] = best_name
            data["customer_name"] = best_name

        if re.search(r'\b(Female|FEMALE)\b', full_text, re.I):
            data["gender"] = "Female"
        elif re.search(r'\b(Male|MALE)\b', full_text, re.I):
            data["gender"] = "Male"

    elif is_aadhaar and (has_address_kw or not is_aadhaar_front):
        # Aadhaar Back side: Extract address fields only (do not touch customer_name)
        addr_match = re.search(r'Address\s*[:：\-]?\s*([^\n\r]+)', full_text, re.I)
        if addr_match:
            cand_addr = addr_match.group(1).strip()
            cand_addr = re.sub(r'[^A-Za-z0-9\s,]', ' ', cand_addr).strip()
            if cand_addr:
                data["address_line1"] = cand_addr.upper()

        for l in lines_text:
            if ',' in l and not re.search(r'\d', l):
                parts = [p.strip().upper() for p in l.split(',') if p.strip()]
                if len(parts) >= 3 and not data.get("address_line2"):
                    data["address_line2"] = f"{parts[0]}, {parts[1]}"
                    data["city"] = parts[2]

    # Always keep annual income 200000
    data["annual_income"] = "200000"

    # 6. Customer Name & DOB from PAN or Aadhaar if not from calculator
    if not data.get("customer_name"):
        if "INCOMETAX" in full_text.upper():
            # PAN name is typically right before or after father's name
            for l in lines_text:
                if re.match(r'^[A-Z\s]{5,35}$', l) and not any(k in l for k in ["INCOME", "TAX", "DEPARTMENT", "GOVT", "INDIA", "PERMANENT", "ACCOUNT", "CARD", "SIGNATUR"]):
                    data["customer_name"] = l.strip().upper()
                    break

    if not data.get("dob"):
        dob_m = re.search(r'(?:DOB|Date of Birth|Birth)[\s:：\-]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})', full_text, re.I)
        if dob_m:
            data["dob"] = parse_date_to_ddmmyyyy(dob_m.group(1))

    # 7. Bank Account Number Detection (Priority: explicit label)
    acc_found = None
    micr_match = re.search(r'MICR[\s:：\-]*([0-9]{9})', full_text, re.I)
    micr_val = micr_match.group(1) if micr_match else None

    for i, line in enumerate(lines_text):
        if re.search(r'\b(Account\s*Number|Account\s*No|A/c\s*No|A/c\s*Number|Acc\s*No|Khata\s*No|SB\s*A/c)\b', line, re.I):
            for off in range(3):
                if i + off < len(lines_text):
                    cand_text = lines_text[i + off]
                    # Digits possibly spaced or hyphenated
                    digits_match = re.search(r'\b([0-9\s\-]{9,22})\b', cand_text)
                    if digits_match:
                        cand_digits = re.sub(r'[^0-9]', '', digits_match.group(1))
                        if 9 <= len(cand_digits) <= 18:
                            if cand_digits != data.get("pincode") and cand_digits != data.get("mobile") and cand_digits != micr_val:
                                acc_found = cand_digits
                                break
            if acc_found:
                break

    if not acc_found:
        # Fallback: look for 9-18 digit strings, excluding phone, pincode, MICR, and Aadhaar
        candidates = re.findall(r'\b([0-9]{9,18})\b', full_text)
        for c in candidates:
            if c != data.get("mobile") and c != data.get("pincode") and c != micr_val and len(c) != 12:
                acc_found = c
                break

    if acc_found:
        data["bank_account_no"] = acc_found

    # 8. Bank Name and Branch Detection
    branch_str = ""
    branch_match = re.search(r'(?:Branch\s*Name|Branch)[\s:：\-]*\n?([A-Za-z0-9\s,]+)', full_text, re.I)
    if branch_match:
        branch_cand = branch_match.group(1).split('\n')[0].strip()
        branch_cand = re.split(r'\b(?:phone|email|ifsc|tel|pin|micr)\b', branch_cand, flags=re.I)[0].strip(' ,-:')
        if branch_cand and len(branch_cand) > 2:
            branch_str = branch_cand.upper()

    # Known banks check if not detected from IFSC
    if not bank_name:
        for b in IFSC_BANK_MAP.values():
            if re.search(r'\b' + re.escape(b) + r'\b', full_text, re.I):
                bank_name = b
                break

    if bank_name and branch_str:
        data["bank_name_branch"] = f"{bank_name}, {branch_str}"
    elif bank_name:
        data["bank_name_branch"] = bank_name
    elif branch_str:
        data["bank_name_branch"] = branch_str

    # 9. Address detection
    at_match = re.search(r'\b(AT\s+[A-Za-z]+)', full_text, re.I)
    post_match = re.search(r'\b(POST\s+[A-Za-z]+)', full_text, re.I)
    dist_match = re.search(r'\b(DIST\s+[A-Za-z]+)', full_text, re.I)
    
    if at_match and post_match:
        data["address_line1"] = f"{at_match.group(1).upper()} {post_match.group(1).upper()}"
    elif at_match:
        data["address_line1"] = at_match.group(1).upper()
        
    if dist_match:
        data["address_line2"] = dist_match.group(1).upper()
        city_cand = re.sub(r'dist\s*', '', dist_match.group(1), flags=re.I).strip().upper()
        data["city"] = city_cand

    if "MAHARASHTRA" in full_text.upper():
        data["state"] = "MAHARASHTRA"

    # All extracted fields uppercase
    return {k: (v.upper().strip() if isinstance(v, str) else v) for k, v in data.items()}

def extract_nominee_from_ocr_lines(lines_text):
    """Extracts nominee details specifically from Nominee ID document (Aadhaar or PAN)."""
    full_text = "\n".join(lines_text)
    data = {}
    
    # Nominee DOB
    dob_val = None
    dob_match = re.search(r'(?:DOB|Date of Birth|Birth)[\s:：\-]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})', full_text, re.I)
    if dob_match:
        dob_val = parse_date_to_ddmmyyyy(dob_match.group(1))
    if not dob_val:
        for l in lines_text:
            p = parse_date_to_ddmmyyyy(l)
            if p:
                dob_val = p
                break
    if dob_val:
        data["nominee_dob"] = dob_val

    # Nominee Gender
    if re.search(r'\b(Female|FEMALE)\b', full_text, re.I):
        data["nominee_gender"] = "Female"
    elif re.search(r'\b(Male|MALE)\b', full_text, re.I):
        data["nominee_gender"] = "Male"
    else:
        data["nominee_gender"] = "Male"

    # Nominee Name
    name_cand = None
    if "INCOMETAX" in full_text.upper() or "PERMANENT ACCOUNT" in full_text.upper():
        for i, l in enumerate(lines_text):
            if "NAME" in l.upper() and i + 1 < len(lines_text):
                name_cand = lines_text[i+1].strip()
                break
        if not name_cand:
            for l in lines_text:
                if re.match(r'^[A-Z\s]{4,30}$', l) and not any(k in l for k in ["INCOME", "TAX", "DEPARTMENT", "GOVT", "INDIA", "PERMANENT", "ACCOUNT", "CARD", "SIGNATUR"]):
                    name_cand = l.strip()
                    break
    else:
        # Aadhaar
        for i, l in enumerate(lines_text):
            if any(k in l.upper() for k in ["GOVERNMENT", "INDIA", "ENROLMENT", "AUTHORITY"]):
                continue
            if re.match(r'^[A-Za-z\s]{5,35}$', l) and not any(k in l.lower() for k in ["dob", "birth", "gender", "male", "female", "help", "address", "unique", "authority"]):
                name_cand = l.strip()
                break
    
    if name_cand:
        cleaned = re.sub(r'[^A-Za-z\s]', '', name_cand).strip().upper()
        if len(cleaned) > 3:
            data["nominee_name"] = cleaned

    data["nominee_relation"] = "FATHER"
    data["nominee_share"] = "100 %"
    return {k: (v.upper().strip() if isinstance(v, str) else v) for k, v in data.items()}

def extract_from_file(file_path):
    """Processes an image or PDF file and returns extracted key-value pairs."""
    ext = os.path.splitext(file_path)[1].lower()
    all_lines = []

    if ext == ".pdf":
        doc = pymupdf.open(file_path)
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_res, _ = ocr_engine(img)
            if ocr_res:
                all_lines.extend(ocr_res)
        doc.close()
    else:
        img = Image.open(file_path).convert("RGB")
        ocr_res, _ = ocr_engine(img)
        if ocr_res:
            all_lines.extend(ocr_res)

    lines_text = clean_ocr_text(all_lines)
    return extract_from_ocr_lines(lines_text)

def extract_nominee_from_file(file_path):
    """Processes a nominee image or PDF file and returns nominee fields."""
    ext = os.path.splitext(file_path)[1].lower()
    all_lines = []

    if ext == ".pdf":
        doc = pymupdf.open(file_path)
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_res, _ = ocr_engine(img)
            if ocr_res:
                all_lines.extend(ocr_res)
        doc.close()
    else:
        img = Image.open(file_path).convert("RGB")
        ocr_res, _ = ocr_engine(img)
        if ocr_res:
            all_lines.extend(ocr_res)

    lines_text = clean_ocr_text(all_lines)
    return extract_nominee_from_ocr_lines(lines_text)

if __name__ == "__main__":
    test_bank = r"outputs\upload_09b988f0.jpg"
    res = extract_from_file(test_bank)
    print("Testing Bank Extraction on upload_09b988f0.jpg:")
    import pprint
    pprint.pprint(res)
