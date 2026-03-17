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

# We define 'client' here so the whole app can see it
client = None

def get_creds():
    env_creds = os.getenv('GOOGLE_CREDENTIALS')
    if env_creds:
        creds_dict = json.loads(env_creds)
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    if os.path.exists("credentials.json"):
        return ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    raise Exception("No Google Credentials found.")

try:
    creds = get_creds()
    client = gspread.authorize(creds)
except Exception as e:
    print(f"Startup Error: {e}")

# --- HOME PAGE (The "Front Door" for shivaluxury.com) ---
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
            #result { margin-top: 20px; color: #333; font-size: 15px; }
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
            <div style="display: flex; gap: 10px;">
                <input type="number" id="income" placeholder="Monthly Inc ($)">
                <input type="number" id="debts" placeholder="Monthly Debt ($)">
            </div>
            <select id="credit">
                <option value="">Select Credit Profile</option>
                <option value="Excellent (740+)">Excellent (740+)</option>
                <option value="Good (680-739)">Good (680-739)</option>
                <option value="Fair (620-679)">Fair (620-679)</option>
                <option value="Building (Below 620)">Building (Below 620)</option>
            </select>
            <button class="btn-gold" onclick="sendData()">Generate My Audit</button>
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
                    monthly_income: document.getElementById('income').value,
                    monthly_debts: document.getElementById('debts').value,
                    credit: document.getElementById('credit').value
                };
                try {
                    const response = await fetch('/audit', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    const result = await response.json();
                    const myPhone = "1213555123
