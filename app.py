"""
ShivaLuxury Lead Generation Engine — app.py
============================================
FIXES applied vs original:
  - Replaced deprecated oauth2client → google-auth (works on Render/Railway/locally)
  - Credentials now load from local file OR env var — both paths work
  - All frontend fields mapped: monthly_income, monthly_debts, timeline, loan_type
  - DTI qualification logic added (front 31% / back 43%)
  - Tax API error handling hardened (was crashing on empty response)
  - Lead scoring, priority tiers, segment labels
  - Conversation scripts endpoint
  - Refinance candidate flagging
  - Gold + red row highlights in Sheets

RUN LOCALLY:
  pip install -r requirements.txt
  python app.py  →  http://localhost:5001

DEPLOY TO RENDER:
  Set env var: GOOGLE_CREDENTIALS = (paste full JSON contents of your credentials file)
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials   # FIXED: was oauth2client
import os, json, requests
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)

# ─── CONFIG ───────────────────────────────────────────────────────────────────
NINJAS_API_KEY   = os.getenv('NINJAS_API_KEY',   'fLNvcwwCTiyv07khZpSfTAbJtaPpE1aCIuYOWBHg')
MY_CONTACT_PHONE = os.getenv('MY_CONTACT_PHONE', '3104225608')
SHEET_NAME       = os.getenv('SHEET_NAME',       'Unlock Your 2026 Buying Power')
WORKSHEET_NAME   = os.getenv('WORKSHEET_NAME',   'Leads2026')

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ─── GOOGLE SHEETS CLIENT ─────────────────────────────────────────────────────
def get_gspread_client():
    """
    Tries credentials in this order:
      1. GOOGLE_CREDENTIALS env var (JSON string) — use on Render/Railway
      2. shiva-lead-gen-76897a1dbdb5.json  (your working local file)
      3. credentials.json                  (fallback)
    """
    env_creds = os.getenv('GOOGLE_CREDENTIALS')
    if env_creds:
        try:
            creds = Credentials.from_service_account_info(json.loads(env_creds), scopes=SCOPES)
            return gspread.authorize(creds)
        except Exception as e:
            print(f"[WARN] Env creds failed: {e}")

    for fname in ['shiva-lead-gen-76897a1dbdb5.json', 'credentials.json']:
        if os.path.exists(fname):
            try:
                creds = Credentials.from_service_account_file(fname, scopes=SCOPES)
                client = gspread.authorize(creds)
                print(f"[OK] Loaded credentials from {fname}")
                return client
            except Exception as e:
                print(f"[WARN] {fname} failed: {e}")

    print("[ERROR] No Google credentials found — leads will NOT save to Sheets")
    return None

sheets_client = get_gspread_client()

# ─── SERVE FRONTEND ───────────────────────────────────────────────────────────
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# ─── MAIN AUDIT ENDPOINT ──────────────────────────────────────────────────────
@app.route('/audit', methods=['POST'])
def run_audit():
    global sheets_client
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        # Pull all fields
        name           = str(data.get('name',           '')).strip()
        phone          = str(data.get('phone',          '')).strip()
        email          = str(data.get('email',          '')).strip()
        user_zip       = str(data.get('zip_code',       '90210')).strip()
        credit_profile = str(data.get('credit',         ''))
        timeline       = str(data.get('timeline',       ''))
        loan_type      = str(data.get('loan_type',      'Purchase'))

        def safe_float(val, default=0.0):
            try: return float(val or 0)
            except: return default

        monthly_income = safe_float(data.get('monthly_income'))
        monthly_debts  = safe_float(data.get('monthly_debts'))
        loan_amount    = safe_float(data.get('loan_amount'))

        # ── 1. REAL 2026 PROPERTY TAX ─────────────────────────────────────────
        tax_rate = 0.0125  # default 1.25%
        try:
            resp = requests.get(
                f'https://api.api-ninjas.com/v1/propertytax?zip={user_zip}',
                headers={'X-Api-Key': NINJAS_API_KEY}, timeout=5
            )
            if resp.status_code == 200:
                td = resp.json()
                if isinstance(td, list) and td and float(td[0].get('yearly_tax_rate', 0)) > 0:
                    tax_rate = float(td[0]['yearly_tax_rate'])
                    print(f"[OK] Real tax rate for {user_zip}: {tax_rate*100:.3f}%")
        except Exception as e:
            print(f"[WARN] Tax API error ({e}) — using default 1.25%")

        # ── 2. PITI CALCULATION ───────────────────────────────────────────────
        mo_rate = 0.065 / 12
        n       = 360
        p_and_i = (loan_amount * (mo_rate * (1+mo_rate)**n) / ((1+mo_rate)**n - 1)) if loan_amount > 0 else 0
        monthly_tax = (loan_amount * tax_rate)  / 12
        monthly_ins = (loan_amount * 0.005)     / 12   # ~0.5% annual insurance
        total_piti  = p_and_i + monthly_tax + monthly_ins

        # ── 3. DTI QUALIFICATION ──────────────────────────────────────────────
        if monthly_income > 0:
            front_dti = (total_piti / monthly_income) * 100
            back_dti  = ((total_piti + monthly_debts) / monthly_income) * 100
        else:
            front_dti = back_dti = 0

        qualifies = (front_dti <= 31 and back_dti <= 43) if monthly_income > 0 else None
        dti_msg   = (
            f"Front DTI: {front_dti:.1f}% | Back DTI: {back_dti:.1f}% — "
            f"{'✅ LIKELY QUALIFIES' if qualifies else ('⚠️ NEEDS REVIEW' if qualifies is False else 'N/A (no income entered)')}"
        )

        # ── 4. LEAD SCORING ───────────────────────────────────────────────────
        if "740+" in credit_profile and "Immediate" in timeline:
            priority = "🔥 HOT — Call Today"; p_num = 1
        elif "680" in credit_profile or "Immediate" in timeline:
            priority = "⚡ WARM — Follow Up 48hrs"; p_num = 2
        elif "620" in credit_profile:
            priority = "📋 ACTIVE — 60 Day Nurture"; p_num = 3
        else:
            priority = "🌱 NURTURE — Long-Term"; p_num = 4

        segment  = ("Ultra Luxury ($1M+)" if loan_amount >= 1_000_000 else
                    "Luxury ($750K+)"      if loan_amount >= 750_000   else
                    "Premium ($500K+)"     if loan_amount >= 500_000   else
                    "Standard")

        refi_flag = "✅ Refi Candidate" if loan_type == "Refinance" else ""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # ── 5. CONVERSATION SCRIPT ────────────────────────────────────────────
        script = build_script(name, total_piti, qualifies, credit_profile, timeline, user_zip)

        # ── 6. SAVE TO GOOGLE SHEETS ──────────────────────────────────────────
        sheets_saved = False
        sheets_error = ""
        if sheets_client:
            try:
                ws = sheets_client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
                row = [
                    name,                              # A
                    phone,                             # B
                    email,                             # C
                    user_zip,                          # D
                    f"${loan_amount:,.0f}",            # E  Loan Amount
                    f"${total_piti:,.2f}",             # F  Total PITI
                    f"${p_and_i:,.2f}",                # G  P&I
                    f"${monthly_tax:,.2f}",            # H  Monthly Tax
                    f"{tax_rate*100:.3f}%",            # I  Tax Rate
                    credit_profile,                    # J
                    timeline,                          # K
                    loan_type,                         # L
                    f"${monthly_income:,.0f}",         # M
                    f"${monthly_debts:,.0f}",          # N
                    f"{front_dti:.1f}%",               # O  Front DTI
                    f"{back_dti:.1f}%",                # P  Back DTI
                    "Yes" if qualifies else ("No" if qualifies is False else "N/A"),  # Q
                    priority,                          # R
                    segment,                           # S
                    refi_flag,                         # T
                    timestamp                          # U
                ]
                ws.append_row(row)

                last_row = len(ws.get_all_values())
                if loan_amount >= 750_000:
                    ws.format(f"A{last_row}:U{last_row}", {
                        "backgroundColor": {"red":1.0,"green":0.84,"blue":0.0},
                        "textFormat": {"bold":True,"foregroundColor":{"red":0,"green":0,"blue":0}}
                    })
                elif p_num == 1:
                    ws.format(f"A{last_row}:U{last_row}", {
                        "backgroundColor": {"red":1.0,"green":0.92,"blue":0.92}
                    })

                sheets_saved = True
                print(f"[OK] Lead saved → {name} | {segment} | {priority}")

            except gspread.exceptions.SpreadsheetNotFound:
                sheets_error = f"Sheet '{SHEET_NAME}' not found. Make sure the name matches exactly and shiva-leads@shiva-lead-gen.iam.gserviceaccount.com has Editor access."
                print(f"[ERROR] {sheets_error}")
            except Exception as e:
                sheets_error = str(e)
                print(f"[ERROR] Sheets: {e}")
        else:
            sheets_error = "No Sheets client — credentials not loaded"

        return jsonify({
            "status":        "success",
            "message":       f"Total Est. PITI: ${total_piti:,.2f}/mo",
            "breakdown":     f"P&I: ${p_and_i:,.2f} + Tax: ${monthly_tax:,.2f} + Ins: ${monthly_ins:,.2f}",
            "qualification": dti_msg,
            "qualifies":     qualifies,
            "priority":      priority,
            "segment":       segment,
            "tax_rate":      f"{tax_rate*100:.3f}%",
            "script":        script,
            "sheets_saved":  sheets_saved,
            "sheets_error":  sheets_error,
            "refi_flag":     refi_flag
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ─── CONVERSATION SCRIPT BUILDER ──────────────────────────────────────────────
def build_script(name, piti, qualifies, credit, timeline, zip_code):
    first    = name.split()[0] if name else "there"
    piti_fmt = f"${piti:,.0f}"

    opener = (
        f"Hi {first}! This is Shiva Tamara with ShivaLuxury Real Estate — DRE 02251909. "
        f"I just pulled your 2026 Buying Power Audit for the {zip_code} area. "
        + (
            f"Great news — your estimated PITI is {piti_fmt}/mo and your profile looks strong to move forward. "
            f"Do you have 10 minutes this week to map out your strategy?"
            if qualifies else
            f"Your estimated PITI is {piti_fmt}/mo. "
            f"I have a 60-day action plan that can get you in a much stronger position — "
            f"want me to walk you through it?"
        )
    )

    return {
        "call_opener":   opener,
        "sms_followup":  f"Hi {first}! 🏡 It's Shiva from ShivaLuxury. Your 2026 Audit shows ~{piti_fmt}/mo PITI. I have 3 strategies that could save you thousands — reply YES to chat!",
        "voicemail":     f"Hi {first}, Shiva Tamara — ShivaLuxury Real Estate, DRE 02251909. Calling about your 2026 Buying Power Audit. Your results are ready and I'd love to walk you through them. Call or text me at 310-422-5608. Talk soon!",
        "objections": {
            "just_looking": f"Totally understand, {first}. Most of my clients started that way. The 2026 market is moving fast — knowing your numbers now puts you miles ahead. Would a quick 10-minute call work?",
            "bad_credit":   f"No worries at all, {first}. I work with buyers at every stage. I have lender partners who specialize in credit positioning while you shop. Let me connect you — zero obligation.",
            "not_ready":    f"That's completely fine, {first}. Best time to plan is before you're ready. I can set you up with automated alerts for your target zip so you see homes the moment they hit. Want me to do that?"
        }
    }


# ─── SCRIPTS REFERENCE ────────────────────────────────────────────────────────
@app.route('/scripts', methods=['GET'])
def get_scripts():
    return jsonify({
        "buyer_qualifier":  ["Are you currently renting or do you own?","Have you been pre-approved?","What's your target timeline?","Specific neighborhood or school district?","Ideal monthly payment range?"],
        "seller_qualifier": ["How long have you owned?","Had it appraised recently?","Looking to buy after selling?","What's motivating the move?","Spoken with other agents?"],
        "refi_qualifier":   ["What's your current interest rate?","How much equity roughly?","Lower payment, cash out, or shorter term?","How long do you plan to stay?","Recent changes to income or credit?"],
        "cold_call":        "Hi, this is Shiva Tamara with ShivaLuxury Real Estate. I specialize in helping [buyers/sellers] in the [ZIP] area and I have some 2026 market data I think you'd find valuable. Do you have 2 minutes?",
        "text_intro":       "Hi [Name]! 👋 It's Shiva from ShivaLuxury. Your 2026 Mortgage Audit is ready — est. PITI is $[X]/mo. I have 3 strategies that could save you thousands. Want me to send them? 🏡"
    })


# ─── HEALTH CHECK ─────────────────────────────────────────────────────────────
@app.route('/health')
def health():
    return jsonify({
        "status":    "ok",
        "sheets":    sheets_client is not None,
        "sheet":     SHEET_NAME,
        "worksheet": WORKSHEET_NAME,
        "time":      datetime.now().isoformat()
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    print(f"\n{'='*52}")
    print(f"  ShivaLuxury Lead Engine  →  http://localhost:{port}")
    print(f"  Sheets: {'✅ Connected' if sheets_client else '❌ Not connected — check credentials'}")
    print(f"  Sheet name: {SHEET_NAME}")
    print(f"{'='*52}\n")
    app.run(host='0.0.0.0', port=port, debug=False)
