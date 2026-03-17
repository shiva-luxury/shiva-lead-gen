from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
CORS(app)

# --- GOOGLE SHEETS SETUP ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

@app.route('/audit', methods=['POST'])
def run_audit():
    data = request.json
    
    # 1. Capture the new extended data
    name = data.get('name', 'Unknown')
    phone = data.get('phone', 'No Phone')
    email = data.get('email', 'No Email')
    income = float(data.get('monthly_income', 0))
    debts = float(data.get('monthly_debts', 0))
    credit = data.get('credit', 'Not Provided')
    timeline = data.get('timeline', 'Not Provided')
    
    # 2. Mortgage Math
    max_allowable_payment = (income * 0.43) - debts
    
    # 3. Personalized Message
    if max_allowable_payment > 500:
        result_message = f"Success! Based on your audit, your estimated buying power is ${max_allowable_payment:,.2f}/mo. Since your timeline is {timeline}, we should verify your pre-approval soon."
    else:
        result_message = "Audit Complete. Based on your current profile, we should look at an equity-building strategy first."

    # 4. SAVE TO GOOGLE SHEETS
    try:
        sheet = client.open("Unlock Your 2026 Buying Power").worksheet("Leads2026")
        # Added Credit and Timeline to the row below
        sheet.append_row([name, phone, email, income, debts, round(max_allowable_payment, 2), credit, timeline])
        print(f"✅ Full Audit Captured: {name} ({credit})")
    except Exception as e:
        print(f"❌ Google Sheets Error: {e}")

    return jsonify({
        "status": "success",
        "message": result_message,
        "next_step": "DM Shiva 'STRATEGY' for your full breakdown."
    })

if __name__ == '__main__':
    app.run(port=5001, debug=True)