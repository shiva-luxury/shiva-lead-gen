"""
ShivaLuxury — Phase 2 Email System
====================================
SMTP: smtp.ionos.com:587
From: st@shivaluxury.com
Env:  EMAIL_PASSWORD
"""

import smtplib, ssl, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

SMTP_HOST  = 'smtp.ionos.com'
SMTP_PORT  = 587
SMTP_FROM  = 'st@shivaluxury.com'
SMTP_PASS  = os.getenv('EMAIL_PASSWORD', '')
SHIVA_EMAIL = os.getenv('AGENT_EMAIL', 'st@shivaluxury.com')
SHIVA_PHONE = '310-422-5608'
SHIVA_NAME  = 'Shiva Tamara'

# ── Core send ──────────────────────────────────────────────────────────────────
def _send(to, subject, html):
    if not SMTP_PASS:
        print(f"[EMAIL] No EMAIL_PASSWORD — skipping: {subject[:60]}")
        return False, "EMAIL_PASSWORD not set"
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = f"Shiva Tamara | ShivaLuxury <{SMTP_FROM}>"
        msg['To']      = to
        msg.attach(MIMEText(html, 'html'))
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.ehlo(); s.starttls(context=ctx); s.login(SMTP_FROM, SMTP_PASS)
            s.sendmail(SMTP_FROM, to, msg.as_string())
        print(f"[EMAIL] ✅ Sent → {to}")
        return True, ""
    except Exception as e:
        print(f"[EMAIL] ❌ {e}")
        return False, str(e)

# ── Base HTML template ─────────────────────────────────────────────────────────
def _wrap(body, accent='#d4af37'):
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Helvetica Neue',Arial,sans-serif;background:#f4f4f4;}}
.w{{max-width:600px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.12);}}
.hdr{{background:linear-gradient(135deg,#0a192f,#0d2240);padding:24px 32px;text-align:center;border-bottom:3px solid {accent};}}
.brand{{font-size:24px;font-weight:700;color:{accent};letter-spacing:4px;text-transform:uppercase;}}
.brand em{{color:rgba(255,255,255,.6);font-style:normal;font-weight:400;}}
.sub{{font-size:10px;letter-spacing:3px;color:rgba(255,255,255,.28);text-transform:uppercase;margin-top:3px;}}
.body{{padding:28px 32px;}}
.lbl{{font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#999;font-weight:600;margin-bottom:6px;display:block;}}
.row{{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid #f0ede8;font-size:14px;}}
.row:last-child{{border:none;}}
.rk{{color:#666;}}
.rv{{font-weight:600;color:#0a192f;}}
.big{{font-size:38px;font-weight:700;color:{accent};text-align:center;padding:14px 0 4px;font-family:Georgia,serif;}}
.ctr{{text-align:center;color:#999;font-size:12px;margin-bottom:12px;}}
.script{{background:#faf7f0;border-left:3px solid {accent};border-radius:0 6px 6px 0;padding:12px 16px;margin:8px 0;font-size:13px;color:#333;line-height:1.65;font-style:italic;}}
.slbl{{font-size:9px;letter-spacing:2px;text-transform:uppercase;color:{accent};font-weight:700;margin-bottom:4px;font-style:normal;display:block;}}
.badge{{display:inline-block;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:700;}}
.hot{{background:#fff0f0;color:#b71c1c;border:1px solid #ef9a9a;}}
.warm{{background:#fff8e1;color:#e65100;border:1px solid #ffcc80;}}
.active{{background:#e8f5e9;color:#1b5e20;border:1px solid #a5d6a7;}}
.nurture{{background:#f3f3f3;color:#555;border:1px solid #ccc;}}
.btn{{display:inline-block;padding:13px 28px;border-radius:6px;text-decoration:none;font-weight:700;font-size:13px;letter-spacing:1px;text-transform:uppercase;margin:4px;}}
.btn-gold{{background:{accent};color:#0a192f;}}
.btn-navy{{background:#0a192f;color:{accent};border:1px solid {accent};}}
.btn-green{{background:#2e7d32;color:#fff;}}
.brow{{text-align:center;padding:18px 0 10px;}}
.sec{{font-size:10px;letter-spacing:2px;text-transform:uppercase;color:{accent};font-weight:700;margin:20px 0 10px;border-top:1px solid #f0ede8;padding-top:16px;}}
.poss{{background:#faf7f0;border:1px solid #e8e0d0;border-radius:7px;padding:10px 14px;margin:6px 0;font-size:13px;color:#333;line-height:1.55;}}
.poss strong{{color:#0a192f;}}
.ftr{{background:#0a192f;padding:18px 32px;text-align:center;font-size:11px;color:rgba(255,255,255,.32);line-height:1.9;}}
.ftr strong{{color:{accent};}}
.disc{{font-size:10px;color:#bbb;text-align:center;padding:12px 32px;line-height:1.6;border-top:1px solid #eee;}}
</style></head><body>
<div class="w">
  <div class="hdr">
    <div class="brand">Shiva<em>Luxury</em></div>
    <div class="sub">Real Estate · Mortgage · Leasing · Investments</div>
  </div>
  <div class="body">{body}</div>
  <div class="ftr">
    <strong>Shiva Tamara</strong> · ShivaLuxury · DRE# 02251909 · NMLS 2779492<br>
    Nobility and Monarchs Real Estate · Beverly Hills Financial Group<br>
    Beverly Hills, CA · <strong>{SHIVA_PHONE}</strong> · {SMTP_FROM}
  </div>
</div>
</body></html>"""

def _fmt(n):
    try: return f"${float(n or 0):,.0f}"
    except: return str(n)

def _priority_badge(p):
    p = str(p)
    if 'HOT' in p:    return f'<span class="badge hot">{p}</span>'
    if 'WARM' in p:   return f'<span class="badge warm">{p}</span>'
    if 'ACTIVE' in p: return f'<span class="badge active">{p}</span>'
    return f'<span class="badge nurture">{p}</span>'

# ── AGENT ALERT EMAIL ──────────────────────────────────────────────────────────
PATH_LABELS = {
    'buyer':        ('🏠', 'BUYER LEAD',        '#d4af37'),
    'seller':       ('🏡', 'SELLER LEAD',       '#d4af37'),
    'fresh_start':  ('🚨', 'DISTRESSED LEAD',   '#ef5350'),
    'lease':        ('🔑', 'LEASE LEAD',        '#42a5f5'),
    'commercial':   ('🏢', 'COMMERCIAL LEAD',   '#7e57c2'),
    'self_employed':('💼', 'SELF-EMPLOYED LEAD','#26a69a'),
}

SUBJECT_TEMPLATES = {
    'buyer':        "🏠 NEW BUYER — {name} | {segment} | {priority}",
    'seller':       "🏡 NEW SELLER — {name} | {segment} | {priority}",
    'fresh_start':  "🚨 DISTRESSED — {name} | {zip} — ACT NOW",
    'lease':        "🔑 LEASE — {name} | {area} | {priority}",
    'commercial':   "🏢 COMMERCIAL — {name} | {sqft} sqft | {priority}",
    'self_employed':"💼 SELF-EMPLOYED — {name} | {credit} credit | {priority}",
}

def _shiva_numbers(path, data, calc):
    rows = []
    if path == 'buyer':
        rows = [
            ('Total PITI', f"${calc.get('total_piti',0):,.2f}/mo"),
            ('Loan Amount', _fmt(data.get('loan_amount') or (float(data.get('home_price',0) or 0) - float(data.get('down_payment',0) or 0)))),
            ('Home Price',  _fmt(data.get('home_price','N/A'))),
            ('Qualification', calc.get('qualification','—')),
            ('Front DTI', f"{calc.get('front_dti',0):.1f}%"),
            ('Back DTI',  f"{calc.get('back_dti',0):.1f}%"),
        ]
    elif path == 'seller':
        rows = [
            ('Est. Value',       _fmt(calc.get('est_value',0))),
            ('Net Equity',       _fmt(calc.get('net_equity',0))),
            ('After Commission', _fmt(calc.get('after_commission',0))),
            ('Buying Power',     _fmt(calc.get('buying_power',0))),
        ]
    elif path == 'fresh_start':
        rows = [
            ('Property Value', _fmt(calc.get('prop_value',0))),
            ('Total Owed',     _fmt(calc.get('total_owed',0))),
            ('Est. Equity',    _fmt(calc.get('est_equity',0))),
            ('Walkaway Cash',  _fmt(calc.get('walkaway_cash',0))),
        ]
    elif path == 'lease':
        rows = [
            ('Area',     data.get('area','—')),
            ('Budget',   f"${data.get('budget','—')}/mo"),
            ('Size',     data.get('size','—')),
            ('Move-In',  data.get('move_in','—')),
        ]
    elif path == 'commercial':
        rows = [
            ('Area',       data.get('area','—')),
            ('Sq Ft',      data.get('sqft','—')),
            ('Space Type', data.get('space_type','—')),
            ('Budget',     f"${data.get('budget','—')}/mo"),
        ]
    elif path == 'self_employed':
        rows = [
            ('Monthly Revenue', _fmt(data.get('monthly_revenue',0))),
            ('Bank Balance',    _fmt(data.get('bank_balance',0))),
            ('Target Price',    _fmt(data.get('home_price',0))),
            ('Loan Options',    ', '.join([l['name'] for l in calc.get('loan_options',[])])),
        ]
    return ''.join(f'<div class="row"><span class="rk">{k}</span><span class="rv">{v}</span></div>' for k,v in rows)

def send_lead_alert(path, data, calc):
    ico, label, accent = PATH_LABELS.get(path, ('📋','LEAD','#d4af37'))
    name    = str(data.get('name','Unknown')).strip()
    first   = name.split()[0] if name else 'there'
    phone   = str(data.get('phone',''))
    email   = str(data.get('email',''))
    zip_c   = str(data.get('zip_code', data.get('area','')))
    priority= str(calc.get('priority',''))
    segment = str(calc.get('segment',''))
    script  = calc.get('script', {})
    sqft    = str(data.get('sqft',''))
    credit  = str(data.get('credit',''))
    area    = str(data.get('area',''))

    subject = SUBJECT_TEMPLATES.get(path,'📋 NEW LEAD — {name}').format(
        name=name, segment=segment, priority=priority,
        zip=zip_c, area=area, sqft=sqft, credit=credit)

    # Contact buttons
    tel_link   = f"tel:{phone.replace('-','').replace('(','').replace(')','').replace(' ','')}"
    mail_link  = f"mailto:{email}"

    # Build script blocks
    script_html = ''
    for key, lbl in [('call_opener','Call Opener'),('opener','Call Opener'),
                     ('sms_followup','SMS Follow-Up'),('sms','SMS'),
                     ('voicemail','Voicemail')]:
        v = script.get(key,'')
        if v:
            script_html += f'<div class="script"><span class="slbl">{lbl}</span>{v}</div>'
            break
    for key, lbl in [('sms_followup','SMS Follow-Up'),('sms','SMS')]:
        v = script.get(key,'')
        if v and lbl not in script_html:
            script_html += f'<div class="script"><span class="slbl">{lbl}</span>{v}</div>'
            break

    # All submitted data
    skip = {'name','phone','email'}
    extra_rows = ''.join(
        f'<div class="row"><span class="rk">{k.replace("_"," ").title()}</span><span class="rv">{v}</span></div>'
        for k,v in data.items() if k not in skip and v and str(v).strip()
    )

    body = f"""
<p style="font-size:13px;color:#999;margin-bottom:16px;">{datetime.now().strftime('%A, %B %d %Y · %I:%M %p')}</p>

<div style="background:{'#fff0f0' if 'HOT' in priority else '#fff8e1' if 'WARM' in priority else '#f0f4ff'};border-radius:8px;padding:14px 18px;margin-bottom:18px;border:1px solid {'#ffcdd2' if 'HOT' in priority else '#ffe082' if 'WARM' in priority else '#c5cae9'};">
  <div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#888;margin-bottom:6px;">{ico} {label}</div>
  <div style="font-size:22px;font-weight:700;color:#0a192f;">{name}</div>
  <div style="margin-top:6px;">{_priority_badge(priority)}</div>
</div>

<div class="brow">
  <a href="{tel_link}" class="btn btn-gold">📞 Call {first}</a>
  <a href="sms:{phone}" class="btn btn-navy">💬 Text {first}</a>
  <a href="{mail_link}" class="btn btn-green">✉️ Email</a>
</div>

<span class="lbl">Contact</span>
<div class="row"><span class="rk">Phone</span><span class="rv"><a href="{tel_link}" style="color:#0a192f;">{phone}</a></span></div>
<div class="row"><span class="rk">Email</span><span class="rv"><a href="{mail_link}" style="color:#0a192f;">{email}</a></span></div>
<div class="row"><span class="rk">ZIP / Area</span><span class="rv">{zip_c}</span></div>

<div class="sec">Key Numbers</div>
{_shiva_numbers(path, data, calc)}

<div class="sec">Conversation Scripts</div>
{script_html if script_html else '<p style="font-size:13px;color:#aaa;">No scripts generated.</p>'}

<div class="sec">All Submitted Data</div>
{extra_rows}
"""
    return _send(SHIVA_EMAIL, subject, _wrap(body, accent))


# ── LEAD WELCOME EMAIL ─────────────────────────────────────────────────────────
WELCOME_SUBJECTS = {
    'buyer':        "Your Possibilities Report is Ready, {first} 🏠",
    'seller':       "Your Home Equity Report is Ready, {first} 🏡",
    'fresh_start':  "Your Confidential Options Report, {first}",
    'lease':        "Your Leasing Options Are Ready, {first} 🔑",
    'commercial':   "Your Commercial Space Report, {first} 🏢",
    'self_employed':"Your Path to Homeownership, {first} 💼",
}

def _lead_hero(path, calc):
    if path == 'buyer':
        return (f"${calc.get('total_piti',0):,.0f}/mo", "Your Estimated Monthly Payment")
    elif path == 'seller':
        return (_fmt(calc.get('net_equity',0)), "Your Estimated Net Equity")
    elif path == 'fresh_start':
        return (_fmt(calc.get('walkaway_cash',0)), "Estimated Cash in Your Pocket")
    elif path == 'lease':
        return ("Options Ready", "I'm searching for your perfect place")
    elif path == 'commercial':
        return ("Search Started", "Your commercial space criteria is locked in")
    else:
        return ("Loan Options Ready", "Your self-employed lending profile")

def _lead_key_points(path, calc, data):
    points = []
    if path == 'buyer':
        points = [
            f"💵 Your estimated payment: <strong>${calc.get('total_piti',0):,.0f}/mo</strong> (P&I + tax + insurance)",
            f"📊 Your qualification: <strong>{calc.get('qualification','See full report')}</strong>",
            f"🏡 Your wishlist is logged — I'll match you to active listings in {data.get('zip_code','your area')}",
        ]
    elif path == 'seller':
        points = [
            f"📈 Estimated home value: <strong>{_fmt(calc.get('est_value',0))}</strong>",
            f"💰 Net equity after mortgage: <strong>{_fmt(calc.get('net_equity',0))}</strong>",
            f"🏡 Buying power for your next home: <strong>{_fmt(calc.get('buying_power',0))}</strong>",
        ]
    elif path == 'fresh_start':
        points = [
            f"💰 Estimated cash to you: <strong>{_fmt(calc.get('walkaway_cash',0))}</strong>",
            "🛡️ Your credit can be protected — <strong>no foreclosure on your record</strong>",
            "🤝 Everything is confidential — I'm a licensed agent, not a collector",
        ]
    elif path == 'lease':
        points = [
            f"🔍 I'm searching {data.get('area','your area')} for a {data.get('size','unit')} within your budget",
            "🔑 My service is completely free to you — I represent the tenant",
            "🐾 I'll specifically filter for your must-haves and restrictions",
        ]
    elif path == 'commercial':
        points = [
            f"🏢 Searching {data.get('sqft','your target')} sq ft in {data.get('area','your area')}",
            "📋 I'll review lease terms and flag any hidden costs before you sign",
            "🤝 Tenant representation at no cost to you",
        ]
    else:
        loans = calc.get('loan_options', [])
        points = [
            f"💼 Loan options available to you: <strong>{', '.join(l['name'] for l in loans[:3])}</strong>",
            "📄 No 2-year tax returns required with bank statement loans",
            "🔗 I'll connect you with my specialized self-employed lender partners",
        ]
    return ''.join(f'<div class="poss">{p}</div>' for p in points)

def send_welcome_email(path, data, calc):
    name  = str(data.get('name','')).strip()
    first = name.split()[0] if name else 'there'
    email = str(data.get('email','')).strip()
    if not email or '@' not in email:
        return False, "No valid email"

    subject = WELCOME_SUBJECTS.get(path, "Your ShivaLuxury Report is Ready, {first} 🏡").format(first=first)
    hero_val, hero_lbl = _lead_hero(path, calc)
    key_pts = _lead_key_points(path, calc, data)

    accent = '#ef5350' if path == 'fresh_start' else '#d4af37'

    body = f"""
<p style="font-size:16px;color:#333;line-height:1.6;margin-bottom:18px;">Hi <strong>{first}</strong>! It's Shiva Tamara from ShivaLuxury. I just ran your report and I wanted you to have your numbers right away.</p>

<div style="background:linear-gradient(135deg,#0a192f,#0d2240);border-radius:10px;padding:20px;text-align:center;border:1px solid rgba(212,175,55,.3);margin-bottom:18px;">
  <div style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:rgba(255,255,255,.4);margin-bottom:6px;">{hero_lbl}</div>
  <div style="font-size:38px;font-weight:700;color:{'#4ade80' if path=='fresh_start' else '#d4af37'};font-family:Georgia,serif;">{hero_val}</div>
</div>

<span class="lbl">What This Means For You</span>
{key_pts}

<div class="sec">Ready to talk through your options?</div>
<div class="brow">
  <a href="tel:{SHIVA_PHONE.replace('-','')}" class="btn btn-gold">📞 Call Shiva — {SHIVA_PHONE}</a>
</div>
<div class="brow">
  <a href="sms:{SHIVA_PHONE.replace('-','')}&body={f'Hi Shiva! I just got my report and want to discuss my options.'}" class="btn btn-navy">💬 Text Me</a>
</div>

<p style="font-size:12px;color:#999;text-align:center;margin-top:16px;line-height:1.6;">
  I'm here Monday–Saturday, 9am–7pm PT.<br>
  <strong>Shiva Tamara</strong> · DRE# 02251909 · NMLS 2779492<br>
  ShivaLuxury · Beverly Hills, CA
</p>
"""
    disc = '<p class="disc">This report is an estimate for informational purposes only and does not constitute a loan commitment, appraisal, or legal advice. All figures are subject to lender approval, appraisal, and market conditions. ShivaLuxury DRE# 02251909.</p>'
    return _send(email, subject, _wrap(body, accent).replace('</body>', disc + '</body>'))
