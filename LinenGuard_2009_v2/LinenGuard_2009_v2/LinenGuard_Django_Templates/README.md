# LINENGUARD
### AI-Powered Railway Linen Loss Prevention & Traceability System
**Indian Railways Operational Traceability Platform**

> *"We don't just count missing linen. We track where the linen lifecycle breaks."*

---

## 1. Problem Statement

Indian Railways provides millions of bedsheets, blankets, pillow covers, and towels daily to air-conditioned coach passengers. However, substantial inventory discrepancies occur between laundry dispatch, coach issuance, and terminal return sweeps.

Without item-level digital traceability:
- Depots cannot isolate whether an item was lost during transit, misplaced across coaches, or left uncollected.
- Attenders lack real-time validation tools during coach sweeps.
- Audits result in speculative blame rather than targeted operational intervention.

---

## 2. Solution Overview

**LinenGuard** establishes an unbroken, digital chain-of-custody for every individual linen item using unique QR identifiers and checkpoint event verification:

```
REGISTERED
   ↓
IN LAUNDRY
   ↓
DISPATCHED
   ↓
LOADED TO TRAIN
   ↓
ASSIGNED TO COACH
   ↓
ASSIGNED TO BERTH
   ↓
ISSUED TO PASSENGER
   ↓
COLLECTION EXPECTED
   ↓
ATTENDER SCANS RETURNED LINEN → (RETURNED ✓) → LAUNDRY RECEIVED → WASHING → READY FOR REISSUE
   ↓ (If return scan is missed)
LIFECYCLE BREAK DETECTED
   ↓
UNACCOUNTED STATUS + LAST VERIFIED CHECKPOINT (Coach B2 / Berth 36)
```

The system isolates the **Last Verified Checkpoint**, the **time of verification**, and the **specific broken lifecycle transition** without making accusatory claims or compromising passenger privacy.

---

## 3. Technology Stack

- **Backend**: Python 3.11, Django 5.2, Django REST Framework (DRF)
- **Database**: SQLite (Zero configuration, fully portable)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Bootstrap Icons
- **QR Engine**: Python `qrcode` library + PIL/Pillow for dynamic label rendering and printable tags
- **Camera QR Scanner**: `html5-qrcode` library for responsive in-browser mobile scanning with Web Audio sound feedback
- **Analytics & Data Viz**: Chart.js 4.4

---

## 4. Architecture & Data Models

1. **`Train`**: Train number, name, source, and destination stations.
2. **`Coach`**: Associated train, coach number (e.g. B1, B2), and type (AC 3 Tier, 2 Tier, etc.).
3. **`LinenItem`**: Unique linen code (e.g., `BL-20561`, `BS-10245`), QR code, category (Bedsheet, Blanket, Towel, Pillow Cover), and 14 lifecycle status choices.
4. **`LinenAssignment`**: Non-PII link binding linen to train, coach, berth, passenger reference (e.g. `PNR-1001`), and journey date.
5. **`LinenLifecycleEvent`**: Immutable chronological checkpoint ledger capturing event type, timestamp, location, train/coach/berth, and staff user.
6. **`CollectionSession`**: Train attender sweep session recording expected vs. scanned quantities and discrepancy status.
7. **`CollectionScan`**: Verification log capturing scan result (`SUCCESS`, `WRONG_COACH`, `WRONG_TRAIN`, `ALREADY_RETURNED`, `UNKNOWN_QR`).

---

## 5. Quick Start & Installation

### Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- `pip` package manager

### Setup Instructions

```bash
# 1. Navigate to the project directory
cd C:\Users\Lahari\.gemini\antigravity\scratch\linenguard

# 2. Install dependencies (if not already installed)
pip install django djangorestframework pillow qrcode

# 3. Apply database migrations
python manage.py migrate

# 4. Seed the Operational Demo Dataset
python manage.py seed_demo

# 5. Start development server
python manage.py runserver
```

Open your browser and navigate to:
**`http://127.0.0.1:8000/`**

---

## 6. Demo Credentials & User Roles

| Role | Username | Password | Dashboard Link | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | `/` | Executive Intelligence, analytics, audit log |
| **Attender** | `attender` | `attender123` | `/attender/` | Coach sweep, QR camera scanner, discrepancy detection |
| **Laundry** | `laundry` | `laundry123` | `/laundry/` | Intake scanner, washing cycle, reissue management |

*(Note: The login page includes convenient 1-click login buttons for rapid hackathon judging demonstrations).*

---

## 7. Step-by-Step SIH Demo Walkthrough

### Scenario: Train 12760 (Demo Express), Coach B2
- **Expected Linen Items**: 100
- **Returned Items**: 94
- **Unaccounted Items**: 6

1. **Sign In**:
   - Go to `http://127.0.0.1:8000/login/`. Click **"Admin"** for instant 1-click login.
2. **Review Executive Dashboard**:
   - View KPI counters: Total Linen, Issued, Returned, Unaccounted (6), In Laundry.
   - View Chart.js visualizations for Status Distribution, Train-wise Loss, and Coach Hotspots.
3. **Inspect Flagship Demo Item**:
   - Navigate to **"Track BL-20561"** or search `BL-20561`.
   - Observe status: `ISSUED` to Train 12760, Coach B2, Berth 36.
4. **Attender Collection Demo**:
   - Log in as `attender` or navigate to `/attender/`.
   - Open active collection sweep for Train 12760, Coach B2.
   - Click **`[ SCAN LINEN ]`**.
   - Use camera scanner or click **"Test Valid: BL-20561"**.
   - Observe instant verification card:
     - `✓ LINEN VERIFIED - Blanket | Coach B2 / Berth 36 | Status: ISSUED`
   - Click **`[ MARK AS RETURNED ]`**. Notice audio chime and real-time counter increment.
5. **Wrong Coach & Unknown QR Guard**:
   - In scanner, test wrong coach item or click **"Test Unknown QR"**.
   - Observe instant rejection alerts:
     - `⚠ WRONG COACH DETECTED` or `❌ UNKNOWN LINEN QR`.
6. **Detect Lifecycle Break & Checkpoints**:
   - Click **`[ COMPLETE COLLECTION ]`** on the attender station.
   - System calculates: Expected: 100, Collected: 94, Unaccounted: 6.
   - Navigate to `/linen/missing/` (Unaccounted Linen).
   - Click `BL-20562` (or search it) to view its **Lifecycle Timeline**:
     - Completed checkpoints: Registered, Dispatched, Train Loaded, Coach B2, Berth 41.
     - Interrupted checkpoint: `❌ RETURN SCAN NOT FOUND`.
     - System clearly identifies:
       - **Last Verified Checkpoint**: Issued to Passenger
       - **Location**: Coach B2 / Berth 41
       - **Timestamp**: 08:40 PM
       - **Next Expected Event**: Attender Collection
7. **Laundry Cycle Workflow**:
   - Open `/laundry/` to demonstrate depot intake scanning, moving items from `RECEIVED_AT_LAUNDRY` &rarr; `WASHING` &rarr; `READY_FOR_REISSUE`.

---

## 8. Verification & Automated Tests

To execute the test suite covering all 13 core validation requirements:

```bash
python manage.py test linen
```

Tests include:
- Linen registration & unique QR generation
- Journey assignment
- QR lookup service
- Valid attender collection sweep
- Wrong coach detection & blocking
- Unknown QR code handling
- Duplicate scan prevention
- Missing linen discrepancy calculation
- Lifecycle event sequencing
- Last verified checkpoint extraction
- Unaccounted status transitions
- Dashboard aggregation calculations

---

## 9. Future Enhancements

- **UHF RFID Portals**: Automatic bulk sweeps at coach entrance vestibules replacing 1-by-1 QR scans.
- **Predictive AI Anomaly Detection**: Supervised machine learning identifying route-specific and seasonal loss risk factors.
- **Handheld Terminal (HHT) Integration**: Native offline-first sync for attender mobile devices across cellular blindspots.
