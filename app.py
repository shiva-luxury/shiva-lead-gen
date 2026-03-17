from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)
CORS(app)

# --- GOOGLE SHEETS SETUP ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_creds():
    # 1. Look for the "Secret Key" you pasted into Render
    env_creds = os.getenv('GOOGLE_CREDENTIALS')
    if env_creds:
        creds_dict = json.loads(env_creds)
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    
    # 2. Look for the file on your Mac (for local testing)
    if os.path.exists("credentials.json"):
        return ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    
    raise Exception("No Google Credentials found.")

# Initialize the Google Client
try:
    creds = get_creds()
    client = gspread.authorize(creds)
except Exception as e:
    print(f"Startup Error: {e}")

@app.route('/audit', methods=['POST'])
def run_audit():
    try:
        data = request.json
        # Your audit logic
        income = float(data.get('monthly_income', 0))
        debts = float(data.get('monthly_debts', 0))
        max_payment = (income * 0.43) - debts
        
        # Save to Google Sheets
        sheet = client.open("Unlock Your 2026 Buying Power").worksheet("Leads2026")
        sheet.append_row([
            data.get('name'), data.get('phone'), data.get('email'), 
            income, debts, round(max_payment, 2), data.get('credit'), data.get('timeline')
        ])
        
        return jsonify({"status": "success", "message": f"Buying power: ${max_payment:,.2f}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Render needs this specific port logic to stay alive
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
