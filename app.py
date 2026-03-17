from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)
CORS(app)

# --- GOOGLE SHEETS SETUP ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
client = None

def get_creds():
    env_creds = os.getenv('GOOGLE_CREDENTIALS')
    if env_creds:
        creds_dict = json.loads(env_creds)
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    if os.path.exists("credentials.json"):
        return ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    return None

try:
    creds = get_creds()
    if creds:
        client = gspread.authorize(creds)
except Exception as e:
    print(f"Startup Error: {e}")

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Shiva Luxury | 2026 Audit</title>
        <style>
            body { margin: 0; background: #0a192f; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
            .box { background: white; padding: 30px; border-radius: 12px; width: 90%; max-width: 400px; text-align: center; border: 2px solid #d4af37; }
            input, select { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            button { width: 100%; padding: 15px; background: #d4af37; color: #0a192f; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }
            #res { margin-top: 15px; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2 style="color:#0a192f; margin-bottom:20px;">2026 Mortgage Audit</h2>
            <input type="text" id="n" placeholder="Full Name">
            <input type="text" id="p" placeholder="Phone Number">
            <input type="email" id="e" placeholder="Email Address">
            <input type="number" id="i" placeholder="Monthly Income ($)">
            <input type="number" id="d" placeholder="Monthly Debt ($)">
            <select id="c">
                <option value="Excellent">Excellent (740+)</option>
                <option value="Good">Good (680-739)</option>
                <option value="Fair">Fair (620-679)</option>
            </select>
            <button onclick="send()">Generate My Audit</button>
            <div id="res"></div>
        </div>
        <script>
            async function send() {
                const r = document.getElementById('res');
                r.innerHTML = "Processing...";
                const data = {
                    name: document.getElementById('n').value,
                    phone: document.getElementById('p').value,
                    email: document.getElementById('e').value,
                    monthly_income: document.getElementById('i').value,
                    monthly_debts: document.getElementById('d').value,
                    credit: document.getElementById('c').value
                };
                const response = await fetch('/audit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const res = await response.json();
                r.innerHTML = "<strong>" + res.message + "</strong>";
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/audit', methods=['POST'])
def run_audit():
    global client
    try:
        data = request.json
        inc = float(data.get('monthly_income', 0))
        deb = float(data.get('monthly_debts', 0))
        pwr = (inc * 0.43) - deb
        if client:
            sheet = client.open("Unlock Your 2026 Buying Power").worksheet("Leads2026")
            sheet.append_row([data.get('name'), data.get('phone'), data.get('email'), inc, deb, round(pwr, 2), data.get('credit')])
        return jsonify({"status": "success", "message": f"Estimated Power: ${pwr:,.2f}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5001)))
