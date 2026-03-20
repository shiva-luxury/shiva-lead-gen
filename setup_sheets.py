"""
ShivaLuxury — Google Sheets Setup Script
Deletes all old tabs and creates 6 clean tabs with correct headers
"""
import gspread, json, os
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_NAME = "Unlock Your 2026 Buying Power"

TABS = {
    "Buyers2026": [
        "Timestamp","Name","Phone","Email","ZIP",
        "Employment Type","Buy Status","Property Type","Loan Type",
        "Home Price","Down Payment $","Down Payment %","Loan Amount",
        "HOA /mo","P&I /mo","Property Tax /mo","Tax Rate","Insurance /mo",
        "PMI /mo","Total PITI /mo",
        "Monthly Income","Monthly Debts","Front DTI","Back DTI","Qualifies?",
        "Credit Range","Timeline",
        "Bedrooms","Bathrooms","Stories","Must-Haves","Commute To","Neighborhood Vibe",
        "Dream Home","Priority","Segment"
    ],
    "Sellers2026": [
        "Timestamp","Name","Phone","Email","ZIP",
        "Property Address","Year Purchased","Bedrooms","Bathrooms","Condition","Stories",
        "Has Mortgage","Mortgage Balance","Current Rate","Estimated Value",
        "Est. Market Value","Net Equity","After Commission","Buying Power Next",
        "Why Selling","After Selling Plans","Biggest Concern","Timeline",
        "Priority","Segment"
    ],
    "YourWayOut2026": [
        "Timestamp","Name","Phone","Email","ZIP",
        "Property Address","Situation Type","Years Behind on Taxes",
        "Want To Keep or Leave","Urgency",
        "Estimated Property Value","Mortgage Balance","Back Taxes Owed",
        "Other Liens","Total Owed","Est. Equity","Walkaway Cash",
        "Notes","Priority"
    ],
    "Leases2026": [
        "Timestamp","Name","Phone","Email",
        "Target Area","ZIP","Max Budget /mo","Unit Size",
        "Move-In Date","Lease Length","Move-In Funds Available",
        "Parking Spaces","Pets","Must-Haves","Notes","Priority"
    ],
    "Commercial2026": [
        "Timestamp","Name","Phone","Email",
        "Target Area","Max Budget /mo","Square Footage","Space Type",
        "Purpose","Private or Shared","Lease Length",
        "Special Requirements","Parking Spaces","Move-In Timeline",
        "Notes","Priority"
    ],
    "Loans2026": [
        "Timestamp","Name","Phone","Email","ZIP",
        "Loan Type","Employment Type","Years in Business",
        "Monthly Income","Monthly Debts","Monthly Revenue","Bank Balance",
        "Current Home Value","Current Balance","Current Rate","Current Payment",
        "Target Loan Amount","Credit Range",
        "Notes","Priority","Loan Options Available"
    ]
}

def main():
    # Load credentials
    creds = None
    for f in ['shiva-lead-gen-76897a1dbdb5.json','credentials.json']:
        if os.path.exists(f):
            creds = Credentials.from_service_account_file(f, scopes=SCOPES)
            print(f"[OK] Credentials: {f}")
            break

    if not creds:
        env = os.getenv('GOOGLE_CREDENTIALS')
        if env:
            creds = Credentials.from_service_account_info(json.loads(env), scopes=SCOPES)
            print("[OK] Credentials from environment")

    if not creds:
        print("[ERROR] No credentials found!")
        return

    gc = gspread.authorize(creds)

    try:
        ss = gc.open(SHEET_NAME)
        print(f"[OK] Opened sheet: {SHEET_NAME}")
    except Exception as e:
        print(f"[ERROR] Could not open sheet: {e}")
        return

    # Backup existing data
    print("\n[BACKUP] Saving existing data...")
    backup = {}
    for ws in ss.worksheets():
        data = ws.get_all_values()
        if data:
            backup[ws.title] = data
            print(f"  Backed up: {ws.title} ({len(data)} rows)")
    if backup:
        with open('sheets_backup_final.json','w') as f:
            json.dump(backup, f, indent=2)
        print(f"[OK] Backup saved to sheets_backup_final.json")

    # Delete all existing tabs
    print("\n[CLEANUP] Removing old tabs...")
    existing = ss.worksheets()
    for ws in existing:
        try:
            ss.del_worksheet(ws)
            print(f"  Deleted: {ws.title}")
        except Exception as e:
            print(f"  Could not delete {ws.title}: {e}")

    # Create 6 clean tabs with headers
    print("\n[SETUP] Creating 6 clean tabs...")
    for tab_name, headers in TABS.items():
        try:
            ws = ss.add_worksheet(title=tab_name, rows=1000, cols=len(headers)+2)
            ws.insert_row(headers, 1)

            # Format header row — navy background, gold text, bold
            ws.format(f"A1:{chr(64+len(headers))}1", {
                "backgroundColor": {"red": 0.04, "green": 0.1, "blue": 0.18},
                "textFormat": {
                    "bold": True,
                    "foregroundColor": {"red": 0.83, "green": 0.69, "blue": 0.22}
                }
            })
            print(f"  ✅ Created: {tab_name} ({len(headers)} columns)")
        except Exception as e:
            print(f"  ❌ Error creating {tab_name}: {e}")

    print(f"\n{'='*55}")
    print(f"  ✅ All 6 tabs created successfully!")
    print(f"  Sheet: {SHEET_NAME}")
    print(f"  Tabs: {', '.join(TABS.keys())}")
    print(f"{'='*55}")
    print("\nNow update app.py SHEET_NAME and TABS to match,")
    print("then restart python3 app.py and submit a test form!")

if __name__ == '__main__':
    main()
