from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import requests

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
NINJAS_API_KEY = os.getenv('NINJAS_API_KEY')
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_creds():
    env_creds = os.getenv('GOOGLE_CREDENTIALS')
    if env_creds:
        creds_dict = json.loads(env_creds)
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return None

client = None
try:
    creds = get_creds()
    if creds:
        client = gspread.authorize(creds)
except Exception as e:
    print(f"Startup Error: {e}")

# --- THE PITI LUXURY FRONT END ---
@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Shiva Luxury | PITI Strategy Audit</title>
        <style>
            body { margin: 0; padding: 0; background: #0a192f; font-family: 'Helvetica', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
            .luxury-box { background: white; padding: 40px; border-radius: 15px; width: 90%; max-width: 450px; text-align: center; border: 2px solid #d4af37; box-shadow: 0 15px 35px rgba(0,0,0,0.5); }
            .logo { font-size: 26px; font-weight: bold; letter-spacing: 3px; color: #0a192f; margin-bottom: 5px; border-bottom: 1px solid #d4af37; display: inline-block; padding-bottom: 5px; }
            h2 { font-family: 'Georgia', serif; font-weight: 400; margin: 20px 0; font-size: 18px; color: #333; }
            input, select { width: 100%; padding: 12px; margin-bottom: 12px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; font-size: 16px; }
            .btn-gold { width: 100%; padding: 18px; background: #d4af37; color: #0a192f; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 14px; width: 100%; }
            #result { margin-top: 25px; text-align: left; background: #f4f4f4; padding: 20px; border-radius: 8px; display: none; border-left: 5px solid #d4af37; font-size: 15px; line-height: 1.6; }
            .sms-btn { display: block; margin-top: 20px; padding: 15px; background: #0a192f; color: #d4af37; text-decoration: none; border-radius: 5px; font-weight: bold; text-align: center; }
            .footer-info { margin-top: 35px; font-size: 11px; color: #777; border-top: 1px solid #eee; padding-top: 20px; }
            .license { color: #d4af37; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="luxury-box">
            <div class="logo">SHIVA LUXURY</div>
            <h2>Full PITI Strategy Audit</h2>
            <input type="text" id="name" placeholder="Full Name">
            <input type="text" id="zip" placeholder="Property ZIP Code">
            <input type="number" id="loan_amount" placeholder="Target Loan Amount ($)">
            <input type="text" id="phone" placeholder="Phone Number">
            <select id="credit">
                <option value="">Select Credit Profile</option>
                <option value="Excellent (740+)">Excellent (740+)</option>
                <option value="Good (680-739)">Good (680-739)</option>
            </select>
            <button class="btn-gold" onclick="sendData()">Generate My Full PITI Audit</button>
            <div id="result"></div>
            <div class="footer-info">
                <strong>SHIVA TAMARA</strong><br>
                DRE# 02251909 | NMLS# 2779492
            </div>
        </div>
        <script>
            async function sendData() {
                const resDiv = document.getElementById('result');
                resDiv.style.display = "block";
                resDiv.innerHTML = "<i>Analyzing Market & Tax Data...</i>";
                
                const data = {
                    name: document.getElementById('name').value,
                    zip: document.getElementById('zip').value,
                    loan_amount: document.getElementById('loan_amount').value,
                    phone: document.getElementById('phone').value,
                    credit: document.getElementById('credit').value
                };
                
                try {
                    const response = await fetch('/audit', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    const res = await response.json();
                    
                    if(res.status === "success") {
                        resDiv.innerHTML = `
                            <strong>🏛️ Monthly PITI Estimate</strong><br>
                            • P&I: $${res.pi}<br>
                            • Property Tax: $${res.tax}<br>
                            • Est. Insurance: $${res.hoi}<br>
                            <hr style="border:0; border-top:1px solid #ccc;">
                            <strong style="font-size:18px;">TOTAL: $${res.total}/mo</strong><br>
                            <a href="sms:12135551234&body=Hi Shiva! Just finished my PITI audit for ${data.zip}. Let's talk strategy." class="sms-btn">TEXT SHIVA FOR STRATEGY</a>
                        `;
                    } else { resDiv.innerText = "Error calculating. Please check inputs."; }
                } catch (e) { resDiv.innerText = "Connection error."; }
            }
        </script>
    </body>
    </html>
    ''')

# --- THE PITI CALCULATION ENGINE ---
@app.route('/audit', methods=['POST'])
def run_audit():
    global client
    try:
        data = request.json
        loan = float(data.get('loan_amount', 0))
        zip_code = data.get('zip')
        
        # 1. Tax Logic (API-Ninjas)
        tax_rate = 0.0125 # Default 1.25%
        if NINJAS_API_KEY:
            api_url = f'https://api.api-ninjas.com/v1/propertytax?zip={zip_code}'
            r = requests.get(api_url, headers={'X-Api-Key': NINJAS_API_KEY})
            if r.status_code == 200 and len(r.json()) > 0:
                tax_rate = r.json()[0]['property_tax_50th_percentile'] / 100

        # 2. P&I Logic (6.5% Rate)
        rate = 0.065 / 12
        months = 360
        pi = loan * (rate * (1 + rate)**months) / ((1 + rate)**months - 1) if loan > 0 else 0
        
        # 3. Tax & Insurance Logic
        monthly_tax = (loan * tax_rate) / 12
        monthly_hoi = (loan * 0.0035) / 12 # 0.35% Annual Insurance Estimate
        
        total = pi + monthly_tax + monthly_hoi

        # 4. Log to Google Sheets
        if client:
            sheet = client.open("Unlock Your 2026 Buying Power").worksheet("Leads2026")
            sheet.append_row([
                data.get('name'), 
                zip_code, 
                loan, 
                round(total, 2), 
                data.get('credit'), 
                "Full PITI Audit"
            ])

        return jsonify({
            "status": "success",
            "pi": f"{pi:,.2f}",
            "tax": f"{monthly_tax:,.2f}",
            "hoi": f"{monthly_hoi:,.2f}",
            "total": f"{total:,.2f}"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5001)))
