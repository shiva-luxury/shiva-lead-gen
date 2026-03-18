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
    return None

try:
    creds = get_creds()
    if creds:
        client = gspread.authorize(creds)
except Exception as e:
    print(f"Startup Error: {e}")

# --- THE LUXURY FRONT END ---
@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Shiva Luxury | 2026 Audit</title>
        <style>
            body { margin: 0; padding: 0; background: #0a192f; font-family: 'Helvetica', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
            .luxury-box { background: white; padding: 40px; border-radius: 15px; width: 90%; max-width: 450px; text-align: center; border: 2px solid #d4af37; box-shadow: 0 15px 35px rgba(0,0,0,0.5); }
            .logo { font-size: 24px; font-weight: bold; letter-spacing: 2px; color: #0a192f; margin-bottom: 5px; }
            h2 { font-family: 'Georgia', serif; font-weight: 400; margin-bottom: 25px; font-size: 18px; color: #333; }
            input, select { width: 100%; padding: 12px; margin-bottom: 12px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            .btn-gold { width: 100%; padding: 16px; background: #d4af37; color: #0a192f; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; text-transform: uppercase; }
            #result { margin-top: 20px; color: #0a192f; font-size: 16px; line-height: 1.6; }
            .sms-btn { display: block; margin-top: 15px; padding: 15px; background: #0a192f; color: #d4af37; text-decoration: none; border-radius: 5px; font-weight: bold; }
            .footer-info { margin-top: 30px; font-size: 10px; color: #999; border-top: 1px solid #eee; padding-top: 15px; }
        </style>
    </head>
    <body>
        <div class="luxury-box">
            <div class="logo">SHIVALUXURY</div>
            <h2>2026 Mortgage & Equity Audit</h2>
            <input type="text" id="name" placeholder="Full Name">
            <input type="text" id="phone" placeholder="Phone Number">
            <input type="email" id="email" placeholder="Email Address">
            <input type="number" id="loan_amount" placeholder="Desired Loan Amount ($)">
            <select id="credit">
                <option value="">Select Credit Profile</option>
                <option value="Excellent (740+)">Excellent (740+)</option>
                <option value="Good (680-739)">Good (680-739)</option>
                <option value="Fair (620-679)">Fair (620-679)</option>
            </select>
            <button class="btn-gold" onclick="sendData()">Calculate My Payment</button>
            <div id="result"></div>
            <div class="footer-info">
                Shiva Tamara | Licensed Real Estate Agent | DRE# 02251909<br>Nobility and Monarchs
            </div>
        </div>
        <script>
            async function sendData() {
                const resDiv = document.getElementById('result');
                resDiv.innerHTML = "<i>Consulting 2026 market data...</i>";
                const data = {
                    name: document.getElementById('name').value,
                    phone: document.getElementById('phone').value,
                    email: document.getElementById('email').value,
                    loan_amount: document.getElementById('loan_amount').value,
                    credit: document.getElementById('credit').value
                };
                try {
                    const response = await fetch('/audit', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    const result = await response.json();
                    const myPhone = "12135551234"; // Update this to your real number
                    const smsMsg = encodeURIComponent("Hi Shiva! I just finished my Audit. Let's talk strategy.");
                    
                    if(result.status === "success") {
                        resDiv.innerHTML = `<strong>✅ ${result.message}</strong><br><small>Based on a 6.5% market rate.</small><a href="sms:${myPhone}&body=${smsMsg}" class="sms-btn">TEXT SHIVA FOR STRATEGY</a>`;
                    } else {
                        resDiv.innerText = "Error: " + result.message;
                    }
                } catch (e) { resDiv.innerText = "Error connecting to server."; }
            }
        </script>
    </body>
    </html>
    ''')

# --- THE ENHANCED CALCULATION ENGINE ---
@app.route('/audit', methods=['POST'])
def run_audit():
    global client
    try:
        data = request.json
        loan_amount = float(data.get('loan_amount', 0))
        
        # 1. The Magic Formula Logic
        annual_rate = 0.065 # 6.5% Market Rate
        monthly_rate = annual_rate / 12
        months = 360 # 30-year fixed
        
        # P * (r(1+r)^n) / ((1+r)^n - 1)
        if loan_amount > 0:
            payment = loan_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
        else:
            payment = 0
        
        # 2. Save to Google Sheets
        if client:
            sheet = client.open("Unlock Your 2026 Buying Power").worksheet("Leads2026")
            sheet.append_row([
                data.get('name'), 
                data.get('phone'), 
                data.get('email'), 
                loan_amount, 
                round(payment, 2), 
                data.get('credit'), 
                "2026 Calculator"
            ])
        
        return jsonify({
            "status": "success", 
            "message": f"Estimated P&I: ${payment:,.2f}/mo"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5001)))
