# Tata AIA Life Insurance - Automated Form Filler & Handwriting Generator

An automated application suite created specifically for Tata AIA Life Insurance agents to eliminate the tedious manual work of filling 3-page Member Enrollment Forms (FMQ / Group Sampoorna Raksha).

The system analyzes and reproduces your authentic human handwriting with realistic blue ballpoint pen dynamics (micro-rotation, pressure gradients, box-aligned uppercase lettering, natural checkmarks, and strikethroughs).

---

## 🚀 Key Capabilities

1. **Document Upload & AI OCR Extraction**:
   - Upload or take a photo with your Android phone of:
     - 🪪 **Aadhaar Card** (Front & Back)
     - 💳 **PAN Card**
     - 🏦 **Bank Passbook / Cancelled Cheque**
     - 📄 **Axis Bank / Tata AIA Tractor Loan Calculator Sheet**
   - Built-in RapidOCR extracts Name, Date of Birth, Gender, PAN, Bank Account Number, IFSC code, Address, PIN code, Loan Amount, Loan Term, and Total Premium.

2. **Authentic Handwriting Synthesis**:
   - Modeled after your exact handwriting from **Sample 1** and **Sample 2**.
   - **Indian Blue Ballpoint Pen Ink** (`#1447a6` / `#1b4f98`) with natural pressure variation.
   - **Per-character micro-jitter**: Organic rotation (-2.2° to +2.2°) and micro-offsets so it never looks digital.
   - **Box-aligned capitals**: Places each character inside the dedicated form boxes (Name, DOB, PAN, Mobile, Address, City, State, PIN).
   - **Natural checkmarks**: Fast-stroke checkmarks on checkboxes and all 12 medical health declarations.
   - **Compact PDF output**: Deflated to ~750 KB for instant WhatsApp sharing and printing.

3. **Android App & Mobile Experience**:
   - **Ready Android APK**: `TataAIAFormFiller.apk` included in the root folder, ready to install on any Android phone.
   - **Mobile Progressive Web App (PWA)**: Open `http://<your-ip>:8000` on Chrome for Android, tap "Add to Home screen", and use it full-screen with native camera capture.
   - **Desktop Web Portal**: Clean, modern interface accessible via `start_app.bat`.

---

## 📂 Project Structure

- **`TataAIAFormFiller.apk`**: Standalone installable Android APK file.
- **`start_app.bat`**: One-click launcher to run the web server and open the browser.
- **`server.py`**: FastAPI backend server serving OCR extraction, form generation, and preview APIs.
- **`form_filler.py`**: Handwriting rendering engine that overlays blue ink text onto `Blank form.pdf`.
- **`field_config.py`**: Precise pixel-level coordinates for all boxes and fields across Page 0, 1, and 2.
- **`document_extractor.py`**: OCR parsing engine for Aadhaar, PAN, Passbook, and Loan Sheets.
- **`static/`**: Mobile-first Web UI (HTML, CSS, JS, manifest.json, app icon).
- **`android_app/`**: Complete Android Studio Kotlin project source code.
- **`filled_sample1_bhagwat.pdf`**: Sample 1 filled form (Bhagwat Dashrath Khatal - 7.11 Lakh loan).
- **`filled_sample2_jitesh.pdf`**: Sample 2 filled form (Jitesh Shrirang Jadhav - 3.02 Lakh loan).

---

## 🏃 How to Run

### Method 1: On Your PC / Laptop (Easiest)
1. Double-click **`start_app.bat`**.
2. The browser will automatically open to `http://localhost:8000`.
3. Upload your documents or tap **Load Sample 1 / 2** to test immediately.
4. Click **Generate Handwritten Application Form** and download your filled PDF!

### Method 2: On Your Android Phone
1. Connect your Android phone to the same Wi-Fi as your computer.
2. Open Chrome on your phone and go to:
   ```
   http://10.127.47.178:8000
   ```
   *(Or click "Android Sync" in the top bar to scan the QR code with your phone camera)*.
3. You can tap **Get APK** in the top bar to download and install `TataAIAFormFiller.apk` directly on your phone!
4. Or tap **⋮ > Add to Home screen** in Chrome to install the app icon onto your Android home screen.
