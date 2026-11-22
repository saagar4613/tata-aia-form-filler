"""
Pre-generates both Sample 1 (Bhagwat) and Sample 2 (Jitesh) as fully filled PDFs
with handwritten blue ballpoint ink overlay.
"""

from form_filler import fill_tata_aia_form
import os

sample1_data = {
    "title": "Mr",
    "customer_name": "BHAGWAT DASHRATH KHATAL",
    "dob": "01/01/1992",
    "gender": "Male",
    "pan": "EENPK3248L",
    "marital_status": "Married",
    "annual_income": "200000",
    "address_line1": "AT BRAHMANGAON POST KAVI",
    "address_line2": "DIST PARBHANI",
    "city": "PARBHANI",
    "state": "MAHARASHTRA",
    "pincode": "431509",
    "mobile": "9807330912",
    "education": "10th pass",
    "occupation": "Agriculture",
    "loan_amount": "711221",
    "loan_term": "60",
    "premium_amount": "11221",
    "base_sum_assured": "711221",
    "base_coverage_term": "60",
    "bank_account_no": "80054420607",
    "bank_name_branch": "MAHARASHTRA GRAMIN BANK, JINTUR",
    "ifsc_code": "MAHG0004205",
    "nominee_name": "DASRATH PATHILBUVA KHATAL",
    "nominee_dob": "01/01/1970",
    "nominee_gender": "Male",
    "nominee_relation": "FATHER",
    "nominee_share": "100 %",
    "height": "173",
    "weight": "72",
    "date": "30/10/2026",
    "place": "parbhani",
    "witness_name": "Shubham Bhujbal"
}

sample2_data = {
    "title": "Mr",
    "customer_name": "JITESH SHRIRANG JADHAV",
    "dob": "15/06/1992",
    "gender": "Male",
    "pan": "BEYPJ8359E",
    "marital_status": "Married",
    "annual_income": "200000",
    "address_line1": "RAIKHODA JOGWADA",
    "address_line2": "DIST PARBHANI",
    "city": "PARBHANI",
    "state": "MAHARASHTRA",
    "pincode": "431509",
    "mobile": "9890989309",
    "education": "12th pass",
    "occupation": "Agriculture",
    "loan_amount": "302888",
    "loan_term": "36",
    "premium_amount": "2888",
    "base_sum_assured": "302888",
    "base_coverage_term": "36",
    "bank_account_no": "38302782948",
    "bank_name_branch": "SBI, JINTUR",
    "ifsc_code": "SBIN0003423",
    "nominee_name": "RENUKA JITESH JADHAV",
    "nominee_dob": "01/01/1996",
    "nominee_gender": "Female",
    "nominee_relation": "WIFE",
    "nominee_share": "100 %",
    "height": "173",
    "weight": "71",
    "date": "15/10/2026",
    "place": "parbhani",
    "witness_name": "Swarup Gadhe"
}

out1 = "filled_sample1_bhagwat.pdf"
out2 = "filled_sample2_jitesh.pdf"

fill_tata_aia_form("Blank form.pdf", out1, sample1_data)
fill_tata_aia_form("Blank form.pdf", out2, sample2_data)

print(f"Generated: {out1} ({os.path.getsize(out1)} bytes)")
print(f"Generated: {out2} ({os.path.getsize(out2)} bytes)")
