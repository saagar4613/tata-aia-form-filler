"""
Handwriting Form Filler Engine for Tata AIA Life Insurance Forms
Accurately reproduces human blue-ballpoint handwriting on Blank form.pdf
"""

import os
import re
import io
import math
import random
import base64
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pymupdf
import cv2

from field_config import FIELD_CONFIG

# Default pen color: Classic Indian blue ballpoint ink
DEFAULT_PEN_COLOR = (20, 68, 152)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FONT_PATH = os.path.join(BASE_DIR, "fonts", "Inkfree.ttf")
DEFAULT_SECONDARY_FONT_PATH = os.path.join(BASE_DIR, "fonts", "segoepr.ttf")
if not os.path.exists(DEFAULT_FONT_PATH):
    DEFAULT_FONT_PATH = r"C:\Windows\Fonts\Inkfree.ttf"
if not os.path.exists(DEFAULT_SECONDARY_FONT_PATH):
    DEFAULT_SECONDARY_FONT_PATH = r"C:\Windows\Fonts\segoepr.ttf"

class HandwritingEngine:
    def __init__(self, font_path=DEFAULT_FONT_PATH, secondary_font_path=DEFAULT_SECONDARY_FONT_PATH, dpi=300):
        self.font_path = font_path
        self.secondary_font_path = secondary_font_path if os.path.exists(secondary_font_path) else font_path
        self.dpi = dpi
        self.scale = dpi / 72.0  # Points to pixels conversion ratio
        self._font_cache = {}

    def get_font(self, size_pt, use_secondary=False):
        font_path = self.secondary_font_path if use_secondary else self.font_path
        size_px = int(round(size_pt * self.scale))
        cache_key = (font_path, size_px)
        if cache_key not in self._font_cache:
            self._font_cache[cache_key] = ImageFont.truetype(font_path, size_px)
        return self._font_cache[cache_key]

    def render_char(self, char, font_size_pt, color=DEFAULT_PEN_COLOR, max_rot=2.5):
        """
        Renders an individual character with human ballpoint pen physics:
        - Unique elastic stroke curve warping (no two identical letters)
        - Dynamic pen pressure (variable stroke width/thickness)
        - Non-uniform aspect ratio stretch/squeeze
        - Affine slant/shear (pen angle tilt)
        - Organic ink striations & ballpoint pooling
        - Authentic blue ballpoint ink gradient fluctuations
        """
        if char == " ":
            space_w = int(round(5.0 * self.scale))
            return Image.new("RGBA", (space_w, 1), (0, 0, 0, 0)), 0, 0

        # Alternate font glyph variant occasionally (~15% of the time for alphanumeric)
        use_secondary = (random.random() < 0.15) and char.isalnum()
        size_mult = 0.93 if use_secondary else 1.0

        # Subtle font size variation (±3.5%)
        effective_size_pt = font_size_pt * size_mult * random.uniform(0.965, 1.035)
        font = self.get_font(effective_size_pt, use_secondary=use_secondary)

        bbox = font.getbbox(char)
        if bbox is None or bbox[2] <= bbox[0]:
            space_w = int(round(5.0 * self.scale))
            return Image.new("RGBA", (space_w, 1), (0, 0, 0, 0)), 0, 0

        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        pad = int(round(12.0 * self.scale))
        cw = w + pad * 2
        ch = h + pad * 2

        img = Image.new("L", (cw, ch), 0)
        draw = ImageDraw.Draw(img)

        tx = pad - bbox[0]
        ty = pad - bbox[1]

        draw.text((tx, ty), char, font=font, fill=255)
        arr = np.array(img)

        # 1. Elastic stroke curve warping (makes every instance of 'A', '0', 'R', etc. curve uniquely)
        h_a, w_a = arr.shape
        period_y = random.uniform(18.0 * self.scale, 36.0 * self.scale)
        period_x = random.uniform(18.0 * self.scale, 36.0 * self.scale)
        amp_x = random.uniform(0.4 * self.scale, 1.2 * self.scale)
        amp_y = random.uniform(0.4 * self.scale, 1.1 * self.scale)
        phase_x = random.uniform(0, 2 * math.pi)
        phase_y = random.uniform(0, 2 * math.pi)

        y_coords, x_coords = np.mgrid[0:h_a, 0:w_a].astype(np.float32)
        dx = amp_x * np.sin(2 * np.pi * y_coords / period_y + phase_x)
        dy = amp_y * np.cos(2 * np.pi * x_coords / period_x + phase_y)

        arr = cv2.remap(arr, x_coords + dx, y_coords + dy, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)

        # 2. Organic non-uniform stretch / aspect ratio variation (width vs height)
        sx = random.uniform(0.94, 1.06)
        sy = random.uniform(0.95, 1.05)
        new_w = max(4, int(round(w_a * sx)))
        new_h = max(4, int(round(h_a * sy)))
        arr = cv2.resize(arr, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # 3. Slant / Shear transformation (pen tilt angle variation)
        shear_x = random.uniform(-0.10, 0.08)
        M_shear = np.float32([[1, shear_x, -shear_x * new_h / 2.0], [0, 1, 0]])
        arr = cv2.warpAffine(arr, M_shear, (new_w + int(abs(shear_x) * new_h), new_h), flags=cv2.INTER_LINEAR)

        # 5. Micro-rotation
        rot_deg = random.uniform(-max_rot, max_rot)
        h_s, w_s = arr.shape
        M_rot = cv2.getRotationMatrix2D((w_s / 2.0, h_s / 2.0), rot_deg, 1.0)
        arr = cv2.warpAffine(arr, M_rot, (w_s, h_s), flags=cv2.INTER_LINEAR)

        # 6. Ballpoint pen ink striations & micro-porosity
        noise = np.random.normal(loc=1.0, scale=0.065, size=arr.shape)
        alpha = np.clip(arr.astype(np.float32) * noise, 0, 255).astype(np.uint8)

        # 7. Indian blue ballpoint pen ink tone fluctuations
        r = int(np.clip(color[0] + random.randint(-5, 5), 10, 42))
        g = int(np.clip(color[1] + random.randint(-6, 6), 48, 88))
        b = int(np.clip(color[2] + random.randint(-8, 8), 130, 185))

        out = np.zeros((h_s, w_s, 4), dtype=np.uint8)
        out[:, :, 0] = r
        out[:, :, 1] = g
        out[:, :, 2] = b
        out[:, :, 3] = alpha

        return Image.fromarray(out), bbox[0], bbox[1]

    def draw_checkmark(self, overlay, center_pt, box_size_pt=9.9, color=DEFAULT_PEN_COLOR):
        """Draws a natural handwriting tick mark into a checkbox."""
        draw = ImageDraw.Draw(overlay)
        cx = center_pt[0] * self.scale
        cy = center_pt[1] * self.scale
        bs = box_size_pt * self.scale

        p0 = (cx - 0.28 * bs + random.uniform(-0.8, 0.8), cy - 0.05 * bs + random.uniform(-0.8, 0.8))
        p1 = (cx - 0.05 * bs + random.uniform(-0.8, 0.8), cy + 0.32 * bs + random.uniform(-0.8, 0.8))
        p2 = (cx + 0.65 * bs + random.uniform(-0.8, 0.8), cy - 0.42 * bs + random.uniform(-0.8, 0.8))

        line_width = max(2, int(round(2.0 * (self.dpi / 300.0))))
        r, g, b = color

        for off, a in [((0, 0), 245), ((0.4, 0.4), 130), ((-0.4, -0.4), 90)]:
            col = (r, g, b, a)
            draw.line([(p0[0] + off[0], p0[1] + off[1]), (p1[0] + off[0], p1[1] + off[1])], fill=col, width=line_width)
            draw.line([(p1[0] + off[0], p1[1] + off[1]), (p2[0] + off[0], p2[1] + off[1])], fill=col, width=line_width)

    def draw_strikethrough(self, overlay, x0_pt, y0_pt, x1_pt, y1_pt, color=(20, 20, 20)):
        """Draws a hand-drawn strikethrough line with organic waviness."""
        draw = ImageDraw.Draw(overlay)
        x0 = x0_pt * self.scale
        y0 = y0_pt * self.scale
        x1 = x1_pt * self.scale
        y1 = y1_pt * self.scale

        steps = max(3, int(abs(x1 - x0) / (30 * self.scale)))
        pts = [(x0, y0)]
        for i in range(1, steps):
            t = i / float(steps)
            xi = x0 + t * (x1 - x0)
            yi = y0 + t * (y1 - y0) + random.uniform(-1.2 * self.scale, 1.2 * self.scale)
            pts.append((xi, yi))
        pts.append((x1, y1))

        width = max(2, int(round(2.2 * (self.dpi / 300.0))))
        draw.line(pts, fill=(color[0], color[1], color[2], 230), width=width)

    def render_boxed_string(self, overlay, text, box_centers_pt, font_size_pt=12.0, color=DEFAULT_PEN_COLOR):
        """Places each character of text into designated box centers."""
        text_clean = str(text).upper()
        char_idx = 0
        for i, center_pt in enumerate(box_centers_pt):
            if char_idx >= len(text_clean):
                break
            ch = text_clean[char_idx]
            char_idx += 1
            if ch == " ":
                continue

            char_img, _, _ = self.render_char(ch, font_size_pt, color=color, max_rot=2.2)
            px = int(round(center_pt[0] * self.scale - char_img.width / 2.0 + random.uniform(-0.8, 0.8) * self.scale))
            py = int(round(center_pt[1] * self.scale - char_img.height / 2.0 + random.uniform(-0.8, 0.8) * self.scale))
            overlay.paste(char_img, (px, py), char_img)

    def render_free_string(self, overlay, text, start_x_pt, baseline_y_pt, font_size_pt=11.0, color=DEFAULT_PEN_COLOR, letter_spacing_pt=0.8):
        """Renders natural handwriting on a line with organic drift."""
        cur_x = start_x_pt * self.scale
        base_y = baseline_y_pt * self.scale
        drift_y = 0.0

        for ch in str(text):
            if ch == " ":
                cur_x += 4.5 * self.scale
                continue

            char_img, _, _ = self.render_char(ch, font_size_pt, color=color, max_rot=1.8)
            drift_y += random.uniform(-0.25, 0.25)
            drift_y = max(-1.2 * self.scale, min(1.2 * self.scale, drift_y))

            px = int(round(cur_x))
            py = int(round(base_y - char_img.height / 2.0 + drift_y))
            overlay.paste(char_img, (px, py), char_img)

            font = self.get_font(font_size_pt)
            bbox = font.getbbox(ch)
            char_w = (bbox[2] - bbox[0]) if bbox else int(round(4.5 * self.scale))
            cur_x += char_w + (letter_spacing_pt * self.scale) + random.uniform(-0.2, 0.2) * self.scale


def process_and_place_signature(overlay, sig_source, x_pt, y_pt, max_w_pt, max_h_pt, scale):
    """
    Renders an uploaded or drawn signature cleanly onto the overlay image.
    Automatically removes any paper background (white, off-white, yellow, shadows, lighting gradients)
    using computer vision illumination division so that only natural ink strokes remain.
    Colorizes ink to authentic Indian blue ballpoint pen (20, 71, 166),
    and scales preserving aspect ratio.
    """
    if not sig_source:
        return
    try:
        if isinstance(sig_source, str) and sig_source.startswith("data:image"):
            header, b64_data = sig_source.split(",", 1)
            raw_bytes = base64.b64decode(b64_data)
            img = Image.open(io.BytesIO(raw_bytes))
        elif isinstance(sig_source, str) and os.path.exists(sig_source):
            img = Image.open(sig_source)
        elif hasattr(sig_source, "convert"):
            img = sig_source
        else:
            return

        img = img.convert("RGBA")
        arr = np.array(img)
        if arr.size == 0 or arr.shape[0] < 5 or arr.shape[1] < 5:
            return

        alpha_raw = arr[:, :, 3]
        # Check if already transparent canvas drawing (drawn on touch screen)
        if alpha_raw.min() < 50 and np.mean(alpha_raw == 0) > 0.3:
            alpha = alpha_raw.copy()
            # Also eliminate any white or off-white background canvas pixels
            rgb = arr[:, :, :3]
            is_white = (rgb[:, :, 0] > 215) & (rgb[:, :, 1] > 215) & (rgb[:, :, 2] > 215)
            alpha[is_white] = 0
        else:
            # Paper photo / scanned document crop
            rgb = arr[:, :, :3]
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

            # Robust illumination background estimation
            k_size = max(15, int(min(gray.shape) * 0.15) | 1)
            bg = cv2.dilate(gray, np.ones((7, 7), np.uint8))
            bg = cv2.medianBlur(bg, k_size)
            bg = np.maximum(bg, 1)

            # Normalized division flattens paper color, shadows, and vignetting to pure white
            norm = cv2.divide(gray, bg, scale=255.0)

            # Stroke darkness above background
            darkness = 255.0 - norm.astype(np.float32)

            # Anti-aliased alpha thresholding: smooth stroke edges, paper is strictly alpha = 0
            noise_floor = 18.0
            stroke_thresh = 55.0
            alpha = np.clip((darkness - noise_floor) / (stroke_thresh - noise_floor) * 255.0, 0, 255).astype(np.uint8)

        # Authentic blue ballpoint ink: (20, 71, 166)
        out_arr = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
        out_arr[:, :, 0] = 20
        out_arr[:, :, 1] = 71
        out_arr[:, :, 2] = 166
        out_arr[:, :, 3] = alpha

        # Tightly crop bounding box around strokes
        coords = np.argwhere(alpha > 25)
        if coords.size == 0:
            return
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0) + 1
        cropped = out_arr[y0:y1, x0:x1]
        img = Image.fromarray(cropped)

        target_w_px = int(round(max_w_pt * scale))
        target_h_px = int(round(max_h_pt * scale))

        orig_w, orig_h = img.size
        ratio = min(target_w_px / orig_w, target_h_px / orig_h)
        new_w = max(1, int(round(orig_w * ratio)))
        new_h = max(1, int(round(orig_h * ratio)))
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        pos_x_px = int(round(x_pt * scale))
        pos_y_px = int(round(y_pt * scale)) + (target_h_px - new_h)

        overlay.paste(resized, (pos_x_px, pos_y_px), resized)
    except Exception as e:
        print(f"Error processing signature: {e}")


def fill_tata_aia_form(blank_pdf_path, output_pdf_path, data, style="digital", calculator_sheet_path=None, borrower_signature=None, witness_signature=None):
    """
    Fills the blank Tata AIA Member Enrollment Form PDF with customer data.
    """
    engine = HandwritingEngine(dpi=300)
    doc = pymupdf.open(blank_pdf_path)

    # Force ALL form input fields to CAPITAL LETTERS
    clean_data = {}
    for k, v in data.items():
        if isinstance(v, str):
            clean_data[k] = v.upper().strip()
        else:
            clean_data[k] = v
    data = clean_data

    borrower_sig = borrower_signature or data.get("borrower_signature")
    witness_sig = witness_signature or data.get("witness_signature")

    # ---------------- PAGE 0 ----------------
    page0 = doc[0]
    p0_cfg = FIELD_CONFIG["page_0"]
    p0_scale = engine.scale
    w0_px = int(round(page0.rect.width * p0_scale))
    h0_px = int(round(page0.rect.height * p0_scale))
    overlay0 = Image.new("RGBA", (w0_px, h0_px), (0, 0, 0, 0))

    # 1. Loan Details
    if data.get("loan_amount"):
        engine.render_free_string(overlay0, data["loan_amount"], p0_cfg["loan_amount"]["x"], p0_cfg["loan_amount"]["y"], p0_cfg["loan_amount"]["size"])

    if data.get("loan_term"):
        term_str = str(data["loan_term"]).strip()
        term_boxes = p0_cfg["loan_term_boxes"]
        if len(term_str) == 2:
            engine.render_boxed_string(overlay0, term_str, term_boxes[:2], font_size_pt=9.5)
        else:
            engine.render_boxed_string(overlay0, term_str, term_boxes, font_size_pt=9.5)

    if data.get("premium_amount"):
        engine.render_free_string(overlay0, data["premium_amount"], p0_cfg["premium_amount"]["x"], p0_cfg["premium_amount"]["y"], p0_cfg["premium_amount"]["size"])

    if data.get("base_sum_assured"):
        engine.render_free_string(overlay0, data["base_sum_assured"], p0_cfg["base_sum_assured"]["x"], p0_cfg["base_sum_assured"]["y"], p0_cfg["base_sum_assured"]["size"])

    if data.get("base_coverage_term"):
        engine.render_free_string(overlay0, data["base_coverage_term"], p0_cfg["base_coverage_term"]["x"], p0_cfg["base_coverage_term"]["y"], p0_cfg["base_coverage_term"]["size"])

    if data.get("customer_name"):
        engine.render_free_string(overlay0, data["customer_name"].upper(), p0_cfg["borrower_declaration_name"]["x"], p0_cfg["borrower_declaration_name"]["y"], p0_cfg["borrower_declaration_name"]["size"])

    # 2. Title
    title = data.get("title", "Mr").lower()
    if title == "mr":
        engine.draw_checkmark(overlay0, (p0_cfg["chk_mr"][0] + 5, p0_cfg["chk_mr"][1] + 5))
    elif title in ["mrs", "mrs."]:
        engine.draw_checkmark(overlay0, (p0_cfg["chk_mrs"][0] + 5, p0_cfg["chk_mrs"][1] + 5))
    elif title in ["ms", "ms."]:
        engine.draw_checkmark(overlay0, (p0_cfg["chk_ms"][0] + 5, p0_cfg["chk_ms"][1] + 5))

    # 3. Name in boxes
    if data.get("customer_name"):
        engine.render_boxed_string(overlay0, data["customer_name"], p0_cfg["name_boxes"], font_size_pt=11.5)

    # 4. DOB (DDMMYYYY)
    dob = data.get("dob", "")
    dob_digits = "".join(filter(str.isdigit, dob))
    if len(dob_digits) == 8:
        engine.render_boxed_string(overlay0, dob_digits, p0_cfg["dob_boxes"], font_size_pt=11.5)

    # 5. Gender
    gender = data.get("gender", "M").upper()
    if gender.startswith("M"):
        engine.draw_checkmark(overlay0, (p0_cfg["chk_gender_m"][0] + 5, p0_cfg["chk_gender_m"][1] + 5))
    elif gender.startswith("F"):
        engine.draw_checkmark(overlay0, (p0_cfg["chk_gender_f"][0] + 5, p0_cfg["chk_gender_f"][1] + 5))

    # 6. PAN
    if data.get("pan"):
        engine.render_boxed_string(overlay0, data["pan"], p0_cfg["pan_boxes"], font_size_pt=11.5)

    # 7. Marital status
    marital = data.get("marital_status", "Married").lower()
    if "marr" in marital:
        engine.draw_checkmark(overlay0, (p0_cfg["chk_married"][0] + 5, p0_cfg["chk_married"][1] + 5))
    else:
        engine.draw_checkmark(overlay0, (p0_cfg["chk_single"][0] + 5, p0_cfg["chk_single"][1] + 5))

    # 8. Annual Income - always 200000
    inc_val = data.get("annual_income") or "200000"
    inc_digits = "".join(filter(str.isdigit, str(inc_val))) or "200000"
    engine.render_boxed_string(overlay0, inc_digits, p0_cfg["income_boxes"], font_size_pt=11.5)

    # 9. Address
    addr1 = data.get("address_line1", "")
    if addr1:
        addr1_boxes = [(p0_cfg["addr1_x_start"] + i * p0_cfg["addr1_spacing"], p0_cfg["addr1_y"]) for i in range(p0_cfg["addr1_count"])]
        engine.render_boxed_string(overlay0, addr1, addr1_boxes, font_size_pt=11.0)

    addr2 = data.get("address_line2", "")
    if addr2:
        addr2_boxes = [(p0_cfg["addr2_x_start"] + i * p0_cfg["addr2_spacing"], p0_cfg["addr2_y"]) for i in range(p0_cfg["addr2_count"])]
        engine.render_boxed_string(overlay0, addr2, addr2_boxes, font_size_pt=11.0)

    if data.get("city"):
        engine.render_boxed_string(overlay0, data["city"], p0_cfg["city_boxes"], font_size_pt=11.0)

    if data.get("state"):
        engine.render_boxed_string(overlay0, data["state"], p0_cfg["state_boxes"], font_size_pt=11.0)

    if data.get("pincode"):
        pin_digits = "".join(filter(str.isdigit, str(data["pincode"])))
        engine.render_boxed_string(overlay0, pin_digits, p0_cfg["pin_boxes"], font_size_pt=11.5)

    # 10. Nationality & Resident
    engine.draw_checkmark(overlay0, (p0_cfg["chk_indian"][0] + 5, p0_cfg["chk_indian"][1] + 5))
    engine.draw_checkmark(overlay0, (p0_cfg["chk_resident"][0] + 5, p0_cfg["chk_resident"][1] + 5))

    # 11. Mobile
    if data.get("mobile"):
        mob_digits = "".join(filter(str.isdigit, str(data["mobile"])))
        engine.render_boxed_string(overlay0, mob_digits, p0_cfg["mobile_boxes"], font_size_pt=11.5)

    # 12. Education & Occupation
    edu = data.get("education", "10th pass").lower()
    if "12" in edu:
        engine.draw_checkmark(overlay0, (p0_cfg["chk_edu_12th"][0] + 5, p0_cfg["chk_edu_12th"][1] + 5))
    elif "grad" in edu:
        engine.draw_checkmark(overlay0, (p0_cfg["chk_edu_graduate"][0] + 5, p0_cfg["chk_edu_graduate"][1] + 5))
    else:
        engine.draw_checkmark(overlay0, (p0_cfg["chk_edu_10th"][0] + 5, p0_cfg["chk_edu_10th"][1] + 5))

    occ = data.get("occupation", "Agriculture").lower()
    if "salar" in occ:
        engine.draw_checkmark(overlay0, (p0_cfg["chk_occ_salaried"][0] + 5, p0_cfg["chk_occ_salaried"][1] + 5))
    elif "self" in occ or "busin" in occ:
        engine.draw_checkmark(overlay0, (p0_cfg["chk_occ_self"][0] + 5, p0_cfg["chk_occ_self"][1] + 5))
    else:
        engine.draw_checkmark(overlay0, (p0_cfg["chk_occ_agri"][0] + 5, p0_cfg["chk_occ_agri"][1] + 5))

    # 13. Bank details
    if data.get("bank_account_no"):
        engine.render_free_string(overlay0, data["bank_account_no"], p0_cfg["bank_acc_no"]["x"], p0_cfg["bank_acc_no"]["y"], p0_cfg["bank_acc_no"]["size"])

    if data.get("bank_name_branch"):
        engine.render_free_string(overlay0, data["bank_name_branch"].upper(), p0_cfg["bank_name_branch"]["x"], p0_cfg["bank_name_branch"]["y"], p0_cfg["bank_name_branch"]["size"])

    if data.get("ifsc_code"):
        engine.render_boxed_string(overlay0, data["ifsc_code"].upper(), p0_cfg["ifsc_boxes"], font_size_pt=9.5)

    # 14. Nominee details (Strict column bounds, NO OVERLAP)
    if data.get("nominee_name"):
        nom_name = data["nominee_name"].upper().strip()
        parts = nom_name.split()
        if len(parts) >= 3 or len(nom_name) > 18:
            line1 = " ".join(parts[:2])
            line2 = " ".join(parts[2:])
            engine.render_free_string(overlay0, line1, p0_cfg["nominee_name"]["x"], 647.0, 8.5)
            engine.render_free_string(overlay0, line2, p0_cfg["nominee_name"]["x"], 654.5, 8.5)
        else:
            engine.render_free_string(overlay0, nom_name, p0_cfg["nominee_name"]["x"], p0_cfg["nominee_name"]["y"], p0_cfg["nominee_name"]["size"])

    if data.get("nominee_dob"):
        engine.render_free_string(overlay0, data["nominee_dob"], p0_cfg["nominee_dob"]["x"], p0_cfg["nominee_dob"]["y"], p0_cfg["nominee_dob"]["size"])

    if data.get("nominee_gender"):
        g_val = data["nominee_gender"].strip()
        g_text = "Female" if g_val.lower().startswith("f") else "Male"
        engine.render_free_string(overlay0, g_text, p0_cfg["nominee_gender"]["x"], p0_cfg["nominee_gender"]["y"], p0_cfg["nominee_gender"]["size"])

    if data.get("nominee_relation"):
        engine.render_free_string(overlay0, data["nominee_relation"].upper(), p0_cfg["nominee_relation"]["x"], p0_cfg["nominee_relation"]["y"], p0_cfg["nominee_relation"]["size"])

    share_val = data.get("nominee_share", "100 %")
    engine.render_free_string(overlay0, share_val, p0_cfg["nominee_share"]["x"], p0_cfg["nominee_share"]["y"], p0_cfg["nominee_share"]["size"])

    # Composite Page 0
    buf0 = io.BytesIO()
    overlay0.save(buf0, format="PNG")
    page0.insert_image(page0.rect, stream=buf0.getvalue(), overlay=True)

    # ---------------- PAGE 1 ----------------
    page1 = doc[1]
    p1_cfg = FIELD_CONFIG["page_1"]
    p1_scale = engine.scale
    w1_px = int(round(page1.rect.width * p1_scale))
    h1_px = int(round(page1.rect.height * p1_scale))
    overlay1 = Image.new("RGBA", (w1_px, h1_px), (0, 0, 0, 0))

    # Health declarations (all NO)
    for chk_pt in p1_cfg["health_no_checks"]:
        engine.draw_checkmark(overlay1, chk_pt)

    # Height & Weight (sanitized to numbers so they never overflow boxes)
    raw_h = str(data.get("height", "173"))
    clean_h = re.sub(r'[^0-9]', '', raw_h)[:3] or "173"
    engine.render_free_string(overlay1, clean_h, p1_cfg["height"]["x"], p1_cfg["height"]["y"], p1_cfg["height"]["size"])

    raw_w = str(data.get("weight", "72"))
    clean_w = re.sub(r'[^0-9]', '', raw_w)[:3] or "72"
    engine.render_free_string(overlay1, clean_w, p1_cfg["weight"]["x"], p1_cfg["weight"]["y"], p1_cfg["weight"]["size"])

    # Lost > 10kg weight (NO) - accurately centered inside checkbox without spilling out
    engine.draw_checkmark(overlay1, (p1_cfg["chk_weight_loss_no"][0], p1_cfg["chk_weight_loss_no"][1]), box_size_pt=7.5)

    # Declaration Date & Place
    dec_date = data.get("date", "30/10/2026")
    engine.render_free_string(overlay1, dec_date, p1_cfg["declaration_date"]["x"], p1_cfg["declaration_date"]["y"], p1_cfg["declaration_date"]["size"])

    dec_place = data.get("place", "parbhani")
    engine.render_free_string(overlay1, dec_place, p1_cfg["declaration_place"]["x"], p1_cfg["declaration_place"]["y"], p1_cfg["declaration_place"]["size"])

    # Borrower Signature on Page 1
    if borrower_sig:
        process_and_place_signature(overlay1, borrower_sig, p1_cfg["borrower_signature_p1"]["x"], p1_cfg["borrower_signature_p1"]["y"], p1_cfg["borrower_signature_p1"]["max_w"], p1_cfg["borrower_signature_p1"]["max_h"], p1_scale)

    buf1 = io.BytesIO()
    overlay1.save(buf1, format="PNG")
    page1.insert_image(page1.rect, stream=buf1.getvalue(), overlay=True)

    # ---------------- PAGE 2 ----------------
    page2 = doc[2]
    p2_cfg = FIELD_CONFIG["page_2"]
    p2_scale = engine.scale
    w2_px = int(round(page2.rect.width * p2_scale))
    h2_px = int(round(page2.rect.height * p2_scale))
    overlay2 = Image.new("RGBA", (w2_px, h2_px), (0, 0, 0, 0))

    # Assignment Section
    engine.render_free_string(overlay2, dec_date, p2_cfg["assignment_date"]["x"], p2_cfg["assignment_date"]["y"], p2_cfg["assignment_date"]["size"])
    engine.render_free_string(overlay2, dec_place, p2_cfg["assignment_place"]["x"], p2_cfg["assignment_place"]["y"], p2_cfg["assignment_place"]["size"])

    engine.render_free_string(overlay2, dec_date, p2_cfg["witness_date"]["x"], p2_cfg["witness_date"]["y"], p2_cfg["witness_date"]["size"])
    engine.render_free_string(overlay2, dec_place, p2_cfg["witness_place"]["x"], p2_cfg["witness_place"]["y"], p2_cfg["witness_place"]["size"])

    witness_name = data.get("witness_name", "Shubham Bhujbal")
    witness_parts = witness_name.split()
    if len(witness_parts) >= 2:
        engine.render_free_string(overlay2, witness_parts[0], p2_cfg["witness_name"]["x"], p2_cfg["witness_name"]["y"], p2_cfg["witness_name"]["size"])
        engine.render_free_string(overlay2, " ".join(witness_parts[1:]), p2_cfg["witness_name_line2"]["x"], p2_cfg["witness_name_line2"]["y"], p2_cfg["witness_name_line2"]["size"])
    else:
        engine.render_free_string(overlay2, witness_name, p2_cfg["witness_name"]["x"], p2_cfg["witness_name"]["y"], p2_cfg["witness_name"]["size"])

    # Signatures on Page 2
    if borrower_sig:
        process_and_place_signature(overlay2, borrower_sig, p2_cfg["borrower_signature_p2"]["x"], p2_cfg["borrower_signature_p2"]["y"], p2_cfg["borrower_signature_p2"]["max_w"], p2_cfg["borrower_signature_p2"]["max_h"], p2_scale)

    if witness_sig:
        process_and_place_signature(overlay2, witness_sig, p2_cfg["witness_signature_p2"]["x"], p2_cfg["witness_signature_p2"]["y"], p2_cfg["witness_signature_p2"]["max_w"], p2_cfg["witness_signature_p2"]["max_h"], p2_scale)

    buf2 = io.BytesIO()
    overlay2.save(buf2, format="PNG")
    page2.insert_image(page2.rect, stream=buf2.getvalue(), overlay=True)

    # If loan calculator sheet is provided, append as page 4 (like Sample 1!)
    if calculator_sheet_path and os.path.exists(calculator_sheet_path):
        calc_ext = os.path.splitext(calculator_sheet_path)[1].lower()
        if calc_ext == ".pdf":
            calc_doc = pymupdf.open(calculator_sheet_path)
            doc.insert_pdf(calc_doc)
            calc_doc.close()
        else:
            calc_img = Image.open(calculator_sheet_path)
            new_page = doc.new_page(width=595.28, height=841.89)
            new_page.insert_image(new_page.rect, filename=calculator_sheet_path)

    # Save output PDF with deflation for compact WhatsApp & mobile friendly size (~700 KB)
    doc.save(output_pdf_path, deflate=True, garbage=4)
    doc.close()
    return output_pdf_path
