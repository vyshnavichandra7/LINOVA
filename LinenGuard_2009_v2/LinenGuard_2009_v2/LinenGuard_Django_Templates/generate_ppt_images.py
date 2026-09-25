import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Output directory
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'presentation_assets')
os.makedirs(OUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. SLIDE 2: ECOSYSTEM & SYSTEM ARCHITECTURE DIAGRAM
# -------------------------------------------------------------
def create_slide2_architecture():
    fig, ax = plt.subplots(figsize=(14, 8.5), dpi=220)
    ax.set_facecolor('#f8fafc')
    fig.patch.set_facecolor('#ffffff')

    # Title Banner
    plt.title("LINENGUARD - SYSTEM ECOSYSTEM & ARCHITECTURE", fontsize=18, fontweight='bold', color='#0b1f3a', pad=20)

    # 1. Stakeholders Layer (Top)
    ax.text(0.5, 0.94, "USER & STAKEHOLDER TOUCHPOINTS", ha='center', va='center', fontsize=12, fontweight='bold', color='#475569')
    users = [
        ("Railway Admin / Board", "Executive Monitoring & Procurement", "#0d6efd"),
        ("Train Attender", "On-Train QR Sweep & Verification", "#198754"),
        ("Laundry Depot Staff", "Intake, Washing & Reissue Packaging", "#0dcaf0"),
        ("Train Incharge / TTE", "Discrepancy & Shift Handover", "#fd7e14")
    ]
    for i, (role, desc, col) in enumerate(users):
        x = 0.12 + i * 0.25
        box = patches.FancyBboxPatch((x - 0.11, 0.81), 0.22, 0.09, boxstyle="round,pad=0.02,rounding_size=0.02",
                                     edgecolor=col, facecolor='#ffffff', linewidth=2)
        ax.add_patch(box)
        ax.text(x, 0.865, role, ha='center', va='center', fontsize=10, fontweight='bold', color='#0b1f3a')
        ax.text(x, 0.83, desc, ha='center', va='center', fontsize=7.5, color='#64748b')

    # Down arrows from users to UI
    for i in range(4):
        x = 0.12 + i * 0.25
        ax.annotate('', xy=(x, 0.73), xytext=(x, 0.81),
                    arrowprops=dict(arrowstyle="->", color='#94a3b8', lw=1.8))

    # 2. UI & Interaction Layer
    ui_box = patches.FancyBboxPatch((0.02, 0.63), 0.96, 0.10, boxstyle="round,pad=0.02,rounding_size=0.02",
                                    edgecolor='#0d6efd', facecolor='#eff6ff', linewidth=1.8)
    ax.add_patch(ui_box)
    ax.text(0.04, 0.68, "UI / INTERACTION LAYER", va='center', fontsize=11, fontweight='bold', color='#1e3a8a')
    uis = [
        ("Admin Web Dashboard", "Chart.js, KPI Widgets, Hotspots"),
        ("Mobile QR Scanner App", "html5-qrcode, Audio Feedback, Camera"),
        ("Laundry Intake Station", "High-Volume Bag/Item Checkpoint"),
        ("Global Search & Audit", "Instant Linen / Berth Lookup")
    ]
    for i, (title, sub) in enumerate(uis):
        x = 0.32 + i * 0.20
        box = patches.FancyBboxPatch((x - 0.09, 0.645), 0.18, 0.07, boxstyle="round,pad=0.01",
                                     edgecolor='#3b82f6', facecolor='#ffffff', linewidth=1)
        ax.add_patch(box)
        ax.text(x, 0.69, title, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0b1f3a')
        ax.text(x, 0.66, sub, ha='center', va='center', fontsize=6.8, color='#64748b')

    # Down arrow to Backend
    ax.annotate('', xy=(0.5, 0.55), xytext=(0.5, 0.63),
                arrowprops=dict(arrowstyle="->", color='#0d6efd', lw=2))

    # 3. Core Backend Services & Business Logic Layer
    srv_box = patches.FancyBboxPatch((0.02, 0.30), 0.96, 0.25, boxstyle="round,pad=0.02,rounding_size=0.02",
                                     edgecolor='#0b1f3a', facecolor='#ffffff', linewidth=2)
    ax.add_patch(srv_box)
    ax.text(0.5, 0.525, "DJANGO REST BACKEND & INTELLIGENCE ENGINE", ha='center', va='center', fontsize=12, fontweight='bold', color='#0b1f3a')

    services = [
        ("QR Identification Hub", "Dynamic Tag Generation\nAlphanumeric Prefixes (BL/BS/TW/PC)\nPrintable Tag Generator"),
        ("Validation Guard Engine", "Wrong Coach Intercept\nWrong Train Intercept\nDuplicate Scan Rejection\nUnknown QR Detection"),
        ("Lifecycle Break Detector", "Expected vs Actual Analysis\nInterrupted Transition Detection\nZero Accusatory Language\nStrict Operational Flagging"),
        ("Last Verified Checkpoint", "Isolates Last Physical Stage\nExtracts Train, Coach & Berth\nRecords Verified Timestamp\nPinpoints Next Expected Step"),
        ("Coach Hotspot Analytics", "Discrepancy Frequency Matrix\nRoute Loss Percentage (<1%, 1-5%, >5%)\nPredictive Risk Categorization\nAI/ML Anomaly Integration")
    ]
    for i, (stitle, sdesc) in enumerate(services):
        x = 0.11 + i * 0.195
        box = patches.FancyBboxPatch((x - 0.088, 0.32), 0.176, 0.18, boxstyle="round,pad=0.015",
                                     edgecolor='#cbd5e1', facecolor='#f8fafc', linewidth=1.2)
        ax.add_patch(box)
        ax.text(x, 0.465, stitle, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0d6efd')
        ax.text(x, 0.39, sdesc, ha='center', va='center', fontsize=7.2, color='#334155', linespacing=1.3)

    # Down arrow to Data Layer
    ax.annotate('', xy=(0.5, 0.22), xytext=(0.5, 0.30),
                arrowprops=dict(arrowstyle="->", color='#0b1f3a', lw=2))

    # 4. Data & Persistence Layer
    db_box = patches.FancyBboxPatch((0.02, 0.04), 0.96, 0.17, boxstyle="round,pad=0.02,rounding_size=0.02",
                                    edgecolor='#198754', facecolor='#f0fdf4', linewidth=1.8)
    ax.add_patch(db_box)
    ax.text(0.04, 0.18, "DATABASE & DATA STORAGE LAYER", va='center', fontsize=11, fontweight='bold', color='#166534')

    dbs = [
        ("Linen Inventory Registry", "LinenItem (14 Status Choices, Codes, Type)"),
        ("Journey & Berth Mapping", "LinenAssignment (Train, Coach, Berth, Non-PII PNR)"),
        ("Immutable Lifecycle Stream", "LinenLifecycleEvent (Timestamp, Staff, Checkpoints)"),
        ("Attender Session Ledger", "CollectionSession & CollectionScan (Expected/Scanned/Discrepancy)")
    ]
    for i, (dtitle, ddesc) in enumerate(dbs):
        x = 0.32 + i * 0.20
        box = patches.FancyBboxPatch((x - 0.09, 0.06), 0.18, 0.10, boxstyle="round,pad=0.01",
                                     edgecolor='#86efac', facecolor='#ffffff', linewidth=1)
        ax.add_patch(box)
        ax.text(x, 0.125, dtitle, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#15803d')
        ax.text(x, 0.088, ddesc, ha='center', va='center', fontsize=6.8, color='#64748b')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "sih_slide2_ecosystem_architecture.png")
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()
    print("Created:", path)

# -------------------------------------------------------------
# 2. SLIDE 3: TECHNICAL PROCESS FLOW PIPELINE
# -------------------------------------------------------------
def create_slide3_process_flow():
    fig, ax = plt.subplots(figsize=(15, 6.5), dpi=220)
    ax.set_facecolor('#ffffff')
    fig.patch.set_facecolor('#ffffff')

    plt.title("LINENGUARD - END-TO-END OPERATIONAL PROCESS FLOW", fontsize=18, fontweight='bold', color='#0b1f3a', pad=20)

    stages = [
        ("1. Registration & QR", "Central Laundry\nUnique Code (BL-20561)\nPrintable Tag Generated\nStatus: REGISTERED", "#0d6efd"),
        ("2. Train & Berth Issue", "Rake Loading & Coach Setup\nAssigned to Coach B2 / Berth 36\nPassenger Reference (PNR-1001)\nStatus: ISSUED", "#0284c7"),
        ("3. Attender QR Sweep", "Destination Arrival Sweep\nAttender Rahul opens App\nCamera Scanner (html5-qrcode)\nStatus: COLLECTION_IN_PROGRESS", "#059669"),
        ("4. Validation Guard", "Verifies Train, Coach & Berth\nBlocks Wrong Coach Scans\nDetects Duplicate / Unknown QRs\nPlays Sound Chime / Buzz", "#d97706"),
        ("5. Breakpoint Isolation", "Expected: 100 | Returned: 94\n6 Missing Items Isolated\nLast Checkpoint: Berth 41\nStatus: UNACCOUNTED", "#dc2545"),
        ("6. Laundry & Reissue", "Depot Handover Scan\nHigh-Temp Washing Cycle\nSanitization Quality Inspection\nStatus: READY_FOR_REISSUE", "#7c3aed")
    ]

    for i, (title, desc, col) in enumerate(stages):
        x = 0.08 + i * 0.165
        # Box
        box = patches.FancyBboxPatch((x - 0.075, 0.35), 0.15, 0.45, boxstyle="round,pad=0.02,rounding_size=0.03",
                                     edgecolor=col, facecolor='#ffffff', linewidth=2.5)
        ax.add_patch(box)

        # Header bar
        hbar = patches.FancyBboxPatch((x - 0.075, 0.70), 0.15, 0.10, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      edgecolor=col, facecolor=col, linewidth=1)
        ax.add_patch(hbar)
        ax.text(x, 0.75, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#ffffff')

        # Content text
        ax.text(x, 0.52, desc, ha='center', va='center', fontsize=8, color='#334155', linespacing=1.4)

        # Connecting Chevron / Arrow
        if i < len(stages) - 1:
            ax.annotate('', xy=(x + 0.088, 0.575), xytext=(x + 0.075, 0.575),
                        arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=3, mutation_scale=18))

    # Core Differentiation Callout Box at Bottom
    callout = patches.FancyBboxPatch((0.02, 0.08), 0.96, 0.18, boxstyle="round,pad=0.02,rounding_size=0.02",
                                    edgecolor='#0b1f3a', facecolor='#0b1f3a', linewidth=1)
    ax.add_patch(callout)
    ax.text(0.5, 0.18, "CORE HACKATHON INNOVATION: LIFECYCLE BREAKPOINT DETECTION", ha='center', va='center', fontsize=11, fontweight='bold', color='#facc15')
    ax.text(0.5, 0.12, "Unlike simple counting tools, LinenGuard identifies: WHERE (Coach B2 / Berth 41) • WHEN (08:40 PM) • WHAT (Blanket BL-20562) • WHY (Missed Return Sweep) without accusatory bias.", ha='center', va='center', fontsize=8.5, color='#e2e8f0')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "sih_slide3_technical_process_flow.png")
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()
    print("Created:", path)

# -------------------------------------------------------------
# 3. SLIDE 4: CHALLENGES VS SOLUTIONS & FEASIBILITY MATRIX
# -------------------------------------------------------------
def create_slide4_challenges_solutions():
    fig, ax = plt.subplots(figsize=(14, 7.5), dpi=220)
    ax.set_facecolor('#ffffff')
    fig.patch.set_facecolor('#ffffff')

    plt.title("FEASIBILITY, CHALLENGES & MITIGATION MATRIX", fontsize=18, fontweight='bold', color='#0b1f3a', pad=20)

    cards = [
        ("CHALLENGE 1: QR TAG WEAR & TEAR",
         "Linen undergoes heavy industrial washing, thermal drying, and physical folding cycles.",
         "MITIGATION / SOLUTION",
         "Level-M error correction QR codes printed on washable thermal textile tags + instant fallback to human-readable alphanumeric code (e.g., BL-20561).",
         "#dc2626", "#16a34a"),
        ("CHALLENGE 2: MULTI-COACH CROSS-MIXING",
         "Passengers or staff move blankets between coaches during long journeys, causing inventory skew.",
         "MITIGATION / SOLUTION",
         "Real-time Validation Engine immediately triggers '⚠ WRONG COACH (Assigned to B1, not B2)' alert and prevents false returns.",
         "#ea580c", "#2563eb"),
        ("CHALLENGE 3: ATTENDER ADOPTION & WORKLOAD",
         "Train attenders work in fast-paced station turnarounds with varying digital literacy.",
         "MITIGATION / SOLUTION",
         "Mobile camera scanner with zero typing, instant synthesized audio feedback (pleasant chime for valid / buzz for error), and 1-click role logins.",
         "#d97706", "#059669"),
        ("CHALLENGE 4: PASSENGER PRIVACY & BLAME",
         "Accusing passengers of theft creates severe friction, PR crises, and customer dissatisfaction.",
         "MITIGATION / SOLUTION",
         "Strict non-accusatory terminology ('Unaccounted Linen' / 'Last Verified Checkpoint') with zero passenger PII stored (only dummy PNR reference).",
         "#4f46e5", "#0284c7")
    ]

    for i, (ctitle, cdesc, stitle, sdesc, c_col, s_col) in enumerate(cards):
        col_idx = i % 2
        row_idx = i // 2
        x = 0.03 + col_idx * 0.49
        y = 0.52 - row_idx * 0.44

        # Card container
        cbox = patches.FancyBboxPatch((x, y), 0.45, 0.38, boxstyle="round,pad=0.015,rounding_size=0.02",
                                      edgecolor='#cbd5e1', facecolor='#f8fafc', linewidth=1.5)
        ax.add_patch(cbox)

        # Challenge section
        ax.text(x + 0.02, y + 0.33, ctitle, fontsize=9.5, fontweight='bold', color=c_col)
        ax.text(x + 0.02, y + 0.27, cdesc, fontsize=8, color='#334155', wrap=True)

        # Separator line
        ax.plot([x + 0.02, x + 0.43], [y + 0.22, y + 0.22], color='#e2e8f0', lw=1.2)

        # Solution section
        ax.text(x + 0.02, y + 0.17, "✓ " + stitle, fontsize=9.5, fontweight='bold', color=s_col)
        ax.text(x + 0.02, y + 0.08, sdesc, fontsize=8, color='#0f172a', wrap=True)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "sih_slide4_challenges_solutions_matrix.png")
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()
    print("Created:", path)

# -------------------------------------------------------------
# 4. SLIDE 5: STAKEHOLDER JOURNEY & SCENARIO FLOW
# -------------------------------------------------------------
def create_slide5_stakeholder_journey():
    fig, ax = plt.subplots(figsize=(15, 7.5), dpi=220)
    ax.set_facecolor('#ffffff')
    fig.patch.set_facecolor('#ffffff')

    plt.title("STAKEHOLDER OPERATIONAL JOURNEY & IMPACTS", fontsize=18, fontweight='bold', color='#0b1f3a', pad=20)

    steps = [
        ("STEP 1: LAUNDRY DEPOT", "Laundry Staff\n\nScans batch, generates QR\nPackages sanitized kit\nDispatches to Rake\nCreates DISPATCHED event", "#0284c7"),
        ("STEP 2: COACH LOADING", "Coach Attender\n\nReceives linen packets\nAllocates to Coach B2\nSets up Berth 36 for PNR-1001\nStatus: ISSUED", "#0d6efd"),
        ("STEP 3: PASSENGER JOURNEY", "Train Passenger\n\nReceives sealed kit\nUses clean blanket & sheets\nLeaves linen on berth\nZero intrusive checks", "#059669"),
        ("STEP 4: ATTENDER SWEEP", "Attender Collection\n\nRuns coach sweep with phone\nScans QR: 94 Verified\nIdentifies 6 Unreturned\nMarks sweep COMPLETED", "#d97706"),
        ("STEP 5: TRACEABILITY BREAK", "Intelligence Engine\n\nDetects unreturned BL-20562\nIsolates Last Checkpoint:\nBerth 41 at 08:40 PM\nStatus: UNACCOUNTED", "#dc2626"),
        ("STEP 6: EXECUTIVE AUDIT", "Railway Management\n\nMonitors Coach Hotspot Map\nHigh discrepancy detected in B2\nTargets depot inspection\nSaves ₹ Cr in loss prevention", "#7c3aed")
    ]

    for i, (stitle, sdesc, col) in enumerate(steps):
        x = 0.08 + i * 0.165

        # Card
        box = patches.FancyBboxPatch((x - 0.075, 0.28), 0.15, 0.52, boxstyle="round,pad=0.02,rounding_size=0.025",
                                     edgecolor=col, facecolor='#ffffff', linewidth=2)
        ax.add_patch(box)

        # Header pill
        pill = patches.FancyBboxPatch((x - 0.07, 0.70), 0.14, 0.075, boxstyle="round,pad=0.01",
                                     edgecolor=col, facecolor=col, linewidth=1)
        ax.add_patch(pill)
        ax.text(x, 0.738, stitle, ha='center', va='center', fontsize=7.5, fontweight='bold', color='#ffffff')

        # Desc
        ax.text(x, 0.48, sdesc, ha='center', va='center', fontsize=8, color='#334155', linespacing=1.35)

        # Arrow
        if i < len(steps) - 1:
            ax.annotate('', xy=(x + 0.088, 0.54), xytext=(x + 0.075, 0.54),
                        arrowprops=dict(arrowstyle="-|>", color='#94a3b8', lw=2.5, mutation_scale=15))

    # Impact metrics box
    ibox = patches.FancyBboxPatch((0.02, 0.05), 0.96, 0.16, boxstyle="round,pad=0.02,rounding_size=0.02",
                                  edgecolor='#16a34a', facecolor='#f0fdf4', linewidth=1.5)
    ax.add_patch(ibox)
    ax.text(0.18, 0.13, "ECONOMIC IMPACT\nSaves ₹30-50 Cr annually across Indian Railways", ha='center', va='center', fontsize=9, fontweight='bold', color='#15803d')
    ax.text(0.50, 0.13, "OPERATIONAL EFFICIENCY\nReduces coach sweep audit time by 65%", ha='center', va='center', fontsize=9, fontweight='bold', color='#1e3a8a')
    ax.text(0.82, 0.13, "SUSTAINABILITY & ESG\nExtends linen lifecycle by 25%, zero paper tally logs", ha='center', va='center', fontsize=9, fontweight='bold', color='#7c3aed')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "sih_slide5_stakeholder_journey.png")
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()
    print("Created:", path)

# -------------------------------------------------------------
# 5. SLIDE 6: COMPETITIVE FEATURE MATRIX
# -------------------------------------------------------------
def create_slide6_competitive_matrix():
    fig, ax = plt.subplots(figsize=(14, 7.5), dpi=220)
    ax.set_facecolor('#ffffff')
    fig.patch.set_facecolor('#ffffff')

    plt.title("COMPETITIVE FEATURE MATRIX & BENCHMARKING", fontsize=18, fontweight='bold', color='#0b1f3a', pad=20)

    features = [
        "1. Item-Level Unique Digital Identity",
        "2. Zero Special Hardware Required (Uses Smartphones)",
        "3. Real-Time Wrong Coach & Duplicate Intercept",
        "4. Last Verified Checkpoint & Breakpoint Isolation",
        "5. Automated Discrepancy & Missing Count",
        "6. Coach-Wise Loss Hotspot & Risk Classification",
        "7. Closed-Loop Laundry Intake & Reissue Tracking",
        "8. Non-Accusatory Operational Design (Zero PII)",
        "9. Clear Upgrade Path to UHF RFID Portals"
    ]

    # Data: [LinenGuard, Manual Logbook, Barcode/Excel, Active RFID]
    data = [
        [True, False, False, True],
        [True, True, False, False],
        [True, False, False, False],
        [True, False, False, False],
        [True, False, False, True],
        [True, False, False, False],
        [True, False, False, False],
        [True, True, True, True],
        [True, False, False, True]
    ]

    cols = ["Evaluation Criteria / Capabilities", "LinenGuard (Ours)", "Manual Paper Logbook", "Generic Barcode / Excel", "Costly RFID Readers"]
    col_x = [0.03, 0.44, 0.60, 0.74, 0.88]

    # Header row
    hbar = patches.Rectangle((0.02, 0.82), 0.96, 0.08, facecolor='#0b1f3a')
    ax.add_patch(hbar)
    for j, (name, x) in enumerate(zip(cols, col_x)):
        ax.text(x, 0.86, name, fontsize=10 if j > 0 else 10.5, fontweight='bold', color='#ffffff',
                ha='center' if j > 0 else 'left', va='center')

    # Rows
    for i, (feat, row) in enumerate(zip(features, data)):
        y = 0.74 - i * 0.075
        bg_col = '#f8fafc' if i % 2 == 0 else '#ffffff'
        rbar = patches.Rectangle((0.02, y - 0.025), 0.96, 0.07, facecolor=bg_col, edgecolor='#e2e8f0', lw=0.5)
        ax.add_patch(rbar)

        ax.text(0.04, y + 0.01, feat, fontsize=9.5, fontweight='semibold', color='#1e293b', va='center')

        for j, val in enumerate(row):
            cx = col_x[j + 1]
            if val:
                ax.text(cx, y + 0.01, "✓", fontsize=15, fontweight='bold', color='#16a34a', ha='center', va='center')
            else:
                ax.text(cx, y + 0.01, "✗", fontsize=15, fontweight='bold', color='#dc2626', ha='center', va='center')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "sih_slide6_competitive_matrix.png")
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()
    print("Created:", path)

if __name__ == '__main__':
    create_slide2_architecture()
    create_slide3_process_flow()
    create_slide4_challenges_solutions()
    create_slide5_stakeholder_journey()
    create_slide6_competitive_matrix()
    print("ALL 5 PRESENTATION DIAGRAMS GENERATED SUCCESSFULLY!")
