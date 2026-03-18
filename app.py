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
        <title>Shiva Luxury | Mortgage Audit</title>
        <style>
            body { margin: 0; padding: 0; background: #0a192f; font-family: 'Helvetica', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
            .luxury-box { background: white; padding: 40px; border-radius: 15px; width: 90%; max-width: 450px; text-align: center; border: 2px solid #d4af37; box-shadow: 0 15px 35px rgba(0,0,0,0.5); }
            .logo { font-size: 26px; font-weight: bold; letter-spacing: 3px; color: #0a192f; margin-bottom: 5px; border-bottom: 1px solid #d4af37; display: inline-block; padding-bottom: 5px; }
            h2 { font-family: 'Georgia', serif; font-weight: 400; margin: 20px 0; font-size: 18px; color: #333; }
            input, select { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; font-size: 16px; }
            .btn-gold { width: 100%; padding: 18px; background: #d4af37; color: #0a192f; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 14px; transition: 0.3s; }
            .btn-gold:hover { background: #b8962d; }
            #result { margin-top: 25px; color: #0a192f; font-weight: bold; font-size: 22px; }
            .action-buttons { display: none; margin-top: 20px; }
            .btn-action { display: block; margin-top: 10px; padding: 15px; border-radius: 5px; font-weight: bold; text-decoration: none; font-size: 14px; }
            .btn-sms { background: #0a192f; color: #d4af37; }
            .btn-vcard { background: #eee; color: #333; border: 1px solid #ccc; }
            .footer-info { margin-top: 35px; font-size: 11px; color: #777; border-top: 1px solid #eee; padding-top: 20px; line-height: 1.6; }
            .license { color: #d4af37; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="luxury-box">
            <div class="logo">SHIVA LUXURY</div>
            <h2>Mortgage & Equity Strategy Audit</h2>
            <input type="text" id="name" placeholder="Full Name">
            <input type="text" id="phone" placeholder="Phone Number">
            <input type="email" id="email" placeholder="Email Address">
            <input type="number" id="loan_amount" placeholder="Target Loan Amount ($)">
            <select id="credit">
                <option value="">Select Credit Profile</option>
                <option value="Excellent (740+)">Excellent (740+)</option>
                <option value="Good (680-739)">Good (680-739)</option>
                <option value="Fair (620-679)">Fair (620-679)</option>
            </select>
            <button class="btn-gold" id="calcBtn" onclick="sendData()">Generate My 2026 Audit</button>
            <div id="result"></div>
            
            <div id="actions" class="action-buttons">
                <a href="#" id="smsLink" class="btn-action btn-sms">TEXT SHIVA FOR STRATEGY</a>
                <a href="/download-vcard" class="btn-action btn-vcard">ADD SHIVA TO CONTACTS</a>
            </div>

            <div class="footer-info">
                <strong>SHIVA TAMARA</strong><br>
                Licensed Real Estate Agent | <span class="license">DRE# 02251909</span><br>
                Mortgage Loan Originator | <span class="license">NMLS# 2779492</span><br>
                <em>Nobility and Monarchs | Beverly Hills Financial Group</em>
            </div>
        </div>
        <script>
            async function sendData() {
                const resDiv = document.getElementById('result');
                const actionDiv = document.getElementById('actions');
                resDiv.innerHTML = "<i>Analyzing 2026 Rates...</i>";
                
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
                    
                    if(result.status === "success") {
                        resDiv.innerHTML = `Result: ${result.message}`;
                        const myPhone = "12135551234"; // Update this to your real phone
                        const smsMsg = encodeURIComponent("Hi Shiva! I just finished my Audit for " + data.loan_amount + ". Let's talk strategy.");
                        document.getElementById('smsLink').href = "sms:" + myPhone + "&body=" + smsMsg;
                        actionDiv.style.display = "block";
                    } else {
                        resDiv.innerText = "Error: " + result.message;
                    }
                } catch (e) { resDiv.innerText = "Error connecting to server."; }
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/download-vcard')
def download_vcard():
    vcard_content = (
        "BEGIN:VCARD\n"
        "VERSION:3.0\n"
        "FN:Shiva Tamara\n"
        "ORG:Nobility and Monarchs;Beverly Hills Financial Group\n"
        "TITLE:Real Estate Agent & Mortgage Loan Originator\n"
        "TEL;TYPE=CELL:3104225608\n"  # Update this to your real phone
        "EMAIL:shivatmettke@gmail.com\n" # Update this to your real email
        "NOTE:DRE# 02251909 | NMLS# 2779492\n"
        "END:VCARD"
    )
    return vcard_content, 200, {
        'Content-Type': 'text/vcard',
        'Content-Disposition': 'attachment; filename=Shiva_Tamara.vcf'
    }

@app.route('/audit', methods=['POST'])
def run_audit():
    global client
    try:
        data = request.json
        loan_amount = float(data.get('loan_amount', 0))
        annual_rate = 0.065 
        monthly_rate = annual_rate / 12
        months = 360
        
        payment = loan_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1) if loan_amount > 0 else 0
        
        if client:
            sheet = client.open("Unlock Your 2026 Buying Power").worksheet("Leads2026")
            sheet.append_row([data.get('name'), data.get('phone'), data.get('email'), loan_amount, round(payment, 2), data.get('credit'), "VCard Version"])
        
        return jsonify({"status": "success", "message": f"${payment:,.2f}/mo"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5001)))
