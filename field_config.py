"""
Tata AIA Life Insurance Form Field Coordinates for Blank form.pdf
Page dimensions: 595.28 x 841.89 points
"""

FIELD_CONFIG = {
    "page_0": {
        # Checkboxes (x0, y0, w, h)
        "chk_product_sampoorna": (301.0, 36.5, 9.9, 9.9), # Pre-printed filled in blank form
        "chk_mr": (23.8, 343.4, 9.9, 9.9),
        "chk_mrs": (46.8, 343.4, 9.9, 9.9),
        "chk_ms": (72.6, 343.4, 9.9, 9.9),
        "chk_gender_m": (214.5, 357.8, 9.9, 9.9),
        "chk_gender_f": (238.6, 357.8, 9.9, 9.9),
        "chk_married": (155.2, 373.7, 9.9, 9.9),
        "chk_single": (269.5, 373.7, 9.9, 9.9),
        "chk_indian": (58.9, 434.8, 9.9, 9.9),
        "chk_resident": (215.3, 434.8, 9.9, 9.9),
        "chk_edu_10th": (268.6, 476.9, 9.9, 9.9),
        "chk_edu_12th": (217.1, 476.6, 9.9, 9.9),
        "chk_edu_graduate": (146.1, 476.6, 9.9, 9.9),
        "chk_occ_agri": (302.8, 489.7, 9.9, 9.9),
        "chk_occ_salaried": (82.6, 489.7, 9.9, 9.9),
        "chk_occ_self": (123.6, 489.7, 9.9, 9.9),

        # Free-form text fields (x, y, fontsize)
        "loan_amount": {"x": 236.0, "y": 103.5, "size": 9.5},
        "premium_amount": {"x": 358.0, "y": 146.5, "size": 9.5},
        "base_sum_assured": {"x": 360.0, "y": 190.0, "size": 9.0},
        "base_coverage_term": {"x": 485.0, "y": 190.0, "size": 9.0},
        "borrower_declaration_name": {"x": 105.0, "y": 252.0, "size": 10.5},

        # Boxed fields (list of x centers or start x + spacing, y)
        "loan_term_boxes": [(544.5, 101.8), (555.6, 101.8), (566.8, 101.8)], # 3 boxes
        
        # 30 Name boxes (F I R S T, M I D D L E, L A S T)
        "name_boxes": [
            (176.8, 349.1), (190.2, 349.1), (203.6, 349.1), (217.0, 349.1), (230.4, 349.1),
            (243.8, 349.1), (257.1, 349.1), (270.5, 349.1), (283.9, 349.1), (297.3, 349.1),
            (311.0, 349.1), (324.4, 349.1), (337.7, 349.1), (351.1, 349.1), (364.5, 349.1),
            (377.9, 349.1), (391.2, 349.1), (405.1, 349.1), (418.5, 349.1), (431.8, 349.1),
            (445.2, 349.1), (458.6, 349.1), (472.0, 349.1), (485.4, 349.1), (498.8, 349.1),
            (512.2, 349.1), (525.6, 349.1), (539.0, 349.1), (552.6, 349.1), (566.0, 349.1)
        ],

        # 8 DOB boxes (DDMMYYYY)
        "dob_boxes": [
            (77.7, 363.7), (91.1, 363.7), (104.5, 363.7), (117.9, 363.7),
            (131.3, 363.7), (144.7, 363.7), (157.7, 363.7), (171.1, 363.7)
        ],

        # 10 PAN boxes
        "pan_boxes": [
            (384.8, 363.7), (398.2, 363.7), (411.6, 363.7), (425.0, 363.7), (438.4, 363.7),
            (451.8, 363.7), (465.2, 363.7), (478.6, 363.7), (492.0, 363.7), (505.4, 363.7)
        ],

        # 7 Income boxes
        "income_boxes": [
            (485.5, 379.6), (499.0, 379.6), (512.4, 379.6), (525.8, 379.6),
            (539.2, 379.6), (552.6, 379.6), (566.0, 379.6)
        ],

        # Address Line 1 (34 boxes)
        "addr1_x_start": 118.1,
        "addr1_y": 395.5,
        "addr1_spacing": 13.4,
        "addr1_count": 34,

        # Address Line 2 (39 boxes)
        "addr2_x_start": 51.2,
        "addr2_y": 409.9,
        "addr2_spacing": 13.4,
        "addr2_count": 39,

        # City (11 boxes)
        "city_boxes": [
            (51.2 + i * 13.4, 425.2) for i in range(11)
        ],

        # State (16 boxes)
        "state_boxes": [
            (238.9 + i * 13.4, 425.2) for i in range(16)
        ],

        # PIN Code (6 boxes)
        "pin_boxes": [
            (493.7 + i * 13.4, 425.2) for i in range(6)
        ],

        # Mobile (10 boxes)
        "mobile_boxes": [
            (59.5 + i * 13.4, 469.4) for i in range(10)
        ],

        # Bank Account No (free-form wide box)
        "bank_acc_no": {"x": 80.0, "y": 590.0, "size": 10.5},

        # Bank Name and Branch
        "bank_name_branch": {"x": 92.0, "y": 604.5, "size": 9.5},

        # IFSC (11 characters inside box 439.54 to 571.66)
        "ifsc_boxes": [
            (445.5 + i * 11.8, 604.0) for i in range(11)
        ],

        # Nominee table (columns: Name [55-186], DOB [186-233], Gender [233-265], Rel [265-380], Share [380-416])
        "nominee_name": {"x": 58.0, "y": 651.0, "size": 9.0},
        "nominee_dob": {"x": 188.0, "y": 651.0, "size": 7.5},
        "nominee_gender": {"x": 239.0, "y": 651.0, "size": 8.0},
        "nominee_relation": {"x": 270.0, "y": 651.0, "size": 9.0},
        "nominee_share": {"x": 385.0, "y": 651.0, "size": 9.0},
    },

    "page_1": {
        # Health Q1-12 No Checkboxes
        "health_no_checks": [
            (553.7, 48.5),
            (553.7, 83.6),
            (553.7, 101.7),
            (553.7, 119.1),
            (553.7, 136.2),
            (553.7, 152.0),
            (553.7, 170.0),
            (553.7, 186.8),
            (553.7, 208.3),
            (553.7, 236.0),
            (553.7, 254.8),
            (553.7, 266.3),
            (553.7, 281.7),
            (553.7, 299.2),
            (553.7, 316.1),
        ],
        # Height & Weight (carefully calibrated to stay inside boxes)
        "height": {"x": 48.0, "y": 370.0, "size": 8.0},
        "weight": {"x": 147.0, "y": 370.0, "size": 8.0},
        "chk_weight_loss_no": (360.0, 368.2, 9.9, 9.9),

        # Declaration Date & Place
        "declaration_date": {"x": 285.0, "y": 668.5, "size": 9.5},
        "declaration_place": {"x": 380.0, "y": 668.5, "size": 9.5},

        # Signatures
        "borrower_signature_p1": {"x": 95.0, "y": 640.0, "max_w": 80.0, "max_h": 22.0},
    },

    "page_2": {
        # Assignment Section
        "assignment_date": {"x": 45.0, "y": 277.0, "size": 9.5},
        "assignment_place": {"x": 175.0, "y": 277.0, "size": 9.5},
        "witness_date": {"x": 320.0, "y": 277.0, "size": 7.8},
        "witness_place": {"x": 384.0, "y": 277.0, "size": 8.0},
        "witness_name": {"x": 490.0, "y": 268.0, "size": 9.5},
        "witness_name_line2": {"x": 490.0, "y": 278.0, "size": 9.5},

        # Signatures
        "borrower_signature_p2": {"x": 90.0, "y": 246.0, "max_w": 95.0, "max_h": 22.0},
        "witness_signature_p2": {"x": 430.0, "y": 246.0, "max_w": 90.0, "max_h": 22.0},

        # Vernacular Declarant / Witness section (optional)
        "declarant_name": {"x": 75.0, "y": 74.0, "size": 12.0},
        "declarant_addr": {"x": 95.0, "y": 86.0, "size": 12.0},
        "declarant_date": {"x": 30.0, "y": 98.0, "size": 12.0},
        "declarant_place": {"x": 125.0, "y": 98.0, "size": 12.0},
        "dec_witness_name": {"x": 360.0, "y": 74.0, "size": 12.0},
        "dec_witness_addr": {"x": 380.0, "y": 86.0, "size": 12.0},
        "dec_witness_date": {"x": 320.0, "y": 96.0, "size": 8.0},
        "dec_witness_place": {"x": 386.0, "y": 96.0, "size": 8.0},
        "vernacular_customer_date": {"x": 200.0, "y": 124.0, "size": 12.0},
        "vernacular_customer_place": {"x": 310.0, "y": 124.0, "size": 12.0},
    }
}
