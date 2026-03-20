"""
ShivaLuxury — Know Your Possibilities Engine (FINAL Phase 1)
=============================================================
6 Paths: Buyer | Seller | Fresh Start | Lease | Commercial | Self-Employed
Life Events: Divorce | Getting Married | Growing Family | Relocating
Google Sheets: 6 tabs auto-created with correct headers
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google.oauth2.service_account import Credentials
import gspread, os, json, requests
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)

NINJAS_API_KEY = os.getenv('NINJAS_API_KEY',   'fLNvcwwCTiyv07khZpSfTAbJtaPpE1aCIuYOWBHg')
SHEET_NAME     = os.getenv('SHEET_NAME',       'Unlock Your 2026 Buying Power')
INT_RATE       = float(os.getenv('INTEREST_RATE', '0.065'))

SCOPES = ["https://spreadsheets.google.com/feeds",
          "https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

TABS = {
    'buyer':         'Buyers2026',
    'seller':        'Sellers2026',
    'fresh_start':   'FreshStart2026',
    'lease':         'Leases2026',
    'commercial':    'Commercial2026',
    'self_employed': 'SelfEmployed2026'
}

HEADERS = {
    'buyer':       ["Timestamp","Life Event","Name","Phone","Email","ZIP","Employment","Loan Type","Budget Mode","Home Price","Down Payment","Down %","Loan Amount","Purchase Price","Asking Price","Price/SqFt","P&I","Monthly Tax","Tax Rate","Insurance","PMI","HOA","Total PITI","Monthly Income","Monthly Debts","Front DTI","Back DTI","Qualifies?","Credit","Timeline","Priority","Segment","Beds","Baths","Stories","Garage","Must-Haves","Commute","Vibe","Dream Home","Buy Status","Purpose","Privacy","Notes"],
    'seller':      ["Timestamp","Life Event","Name","Phone","Email","ZIP","Address","Year Bought","Beds","Baths","Condition","Stories","Mortgage Balance","Owner Estimate","Est. Value","Net Equity","After Commission","Buying Power","Next Step","Concern","Timeline","Why Selling","Has Mortgage","Current Rate","Priority","Segment","Notes"],
    'fresh_start': ["Timestamp","Name","Phone","Email","ZIP","Address","Situation","Years Behind","Property Value","Mortgage Balance","Back Taxes","Other Liens","Total Owed","Est. Equity","Walkaway Cash","Primary Need","Want to Keep","Urgency","Notes","Priority"],
    'lease':       ["Timestamp","Life Event","Name","Phone","Email","ZIP","Area","Budget","Unit Size","Move-In","Lease Length","Parking","Pets","Must-Haves","Move-In Funds","Notes","Priority"],
    'commercial':  ["Timestamp","Name","Phone","Email","Area","Budget","Sq Ft","Space Type","Lease Length","Requirements","Use Type","Parking","Move-In","Notes","Priority"],
    'self_employed':["Timestamp","Name","Phone","Email","ZIP","Business Type","Years in Biz","Monthly Revenue","Monthly Income","Bank Balance","Investments","Credit","Target Price","Notes","Priority","Loan Options"]
}

# ─── SHEETS ───────────────────────────────────────────────────────────────────
def get_client():
    env = os.getenv('GOOGLE_CREDENTIALS')
    if env:
        try:
            c = gspread.authorize(Credentials.from_service_account_info(json.loads(env), scopes=SCOPES))
            print("[OK] Credentials from env"); return c
        except Exception as e: print(f"[WARN] env: {e}")
    for f in ['shiva-lead-gen-76897a1dbdb5.json','credentials.json']:
        if os.path.exists(f):
            try:
                c = gspread.authorize(Credentials.from_service_account_file(f, scopes=SCOPES))
                print(f"[OK] Credentials: {f}"); return c
            except Exception as e: print(f"[WARN] {f}: {e}")
    print("[ERROR] No credentials"); return None

gc = get_client()

def save(path_key, row):
    if not gc: return False, "No Sheets client"
    try:
        ss  = gc.open(SHEET_NAME)
        tab = TABS[path_key]
        hdrs = HEADERS[path_key]
        try:
            ws = ss.worksheet(tab)
            if ws.row_values(1) != hdrs:
                ws.delete_rows(1); ws.insert_row(hdrs, 1)
        except gspread.exceptions.WorksheetNotFound:
            ws = ss.add_worksheet(title=tab, rows=1000, cols=len(hdrs)+5)
            ws.insert_row(hdrs, 1)
            print(f"[OK] Created tab: {tab}")
        ws.append_row(row)
        return True, ""
    except gspread.exceptions.SpreadsheetNotFound:
        return False, f"Sheet '{SHEET_NAME}' not found"
    except Exception as e:
        return False, str(e)

def highlight(path_key, color_type):
    if not gc: return
    try:
        ws = gc.open(SHEET_NAME).worksheet(TABS[path_key])
        last = len(ws.get_all_values())
        fmt = {
            'gold':  {"backgroundColor":{"red":1.0,"green":0.84,"blue":0.0},"textFormat":{"bold":True}},
            'pink':  {"backgroundColor":{"red":1.0,"green":0.92,"blue":0.92}},
            'red':   {"backgroundColor":{"red":1.0,"green":0.88,"blue":0.88}},
            'green': {"backgroundColor":{"red":0.88,"green":1.0,"blue":0.88}}
        }
        col = chr(64 + len(HEADERS[path_key]))
        ws.format(f"A{last}:{col}{last}", fmt.get(color_type, fmt['pink']))
    except: pass

@app.route('/')
def home(): return send_from_directory('.', 'index.html')

@app.route('/audit', methods=['POST'])
def audit():
    try:
        data = request.get_json(force=True) or {}
        path = data.get('path', 'buyer')
        return {'buyer':buyer,'seller':seller,'fresh_start':fresh_start,
                'lease':lease,'commercial':commercial,'self_employed':self_employed
               }.get(path, buyer)(data)
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"status":"error","message":str(e)}), 500

# ══════════════════════════════════════════════════════════════════════════════
def sf(v):
    try: return float(v or 0)
    except: return 0.0

def fmt_s(n): return f"${float(n or 0):,.0f}"
def ts(): return datetime.now().strftime("%Y-%m-%d %H:%M")

# ══════════════════════════════════════════════════════════════════════════════
# BUYER
# ══════════════════════════════════════════════════════════════════════════════
def buyer(data):
    name=str(data.get('name','')).strip(); phone=str(data.get('phone','')).strip()
    email=str(data.get('email','')).strip(); zip_c=str(data.get('zip_code','90210')).strip()
    credit=str(data.get('credit','')); timeline=str(data.get('timeline',''))
    loan_type=str(data.get('loan_type','Purchase')); bm=str(data.get('budget_mode','price'))
    emp=str(data.get('employment_type','W-2 Employee'))
    life=str(data.get('life_event','none'))
    dream=str(data.get('dream_home','')); notes=str(data.get('notes',''))
    commute=str(data.get('commute','')); vibe=str(data.get('vibe',''))
    beds=str(data.get('beds','')); baths=str(data.get('baths',''))
    stories=str(data.get('stories',''))
    garage=str(data.get('garage','')); must=str(data.get('must_haves',''))
    buy_status=str(data.get('buy_status',''))
    purpose=str(data.get('purpose','Primary Residence'))
    privacy=str(data.get('privacy',''))
    inc=sf(data.get('monthly_income')); dbt=sf(data.get('monthly_debts'))
    hoa=sf(data.get('hoa')); hp=sf(data.get('home_price'))
    dp=sf(data.get('down_payment')); dpct=sf(data.get('down_pct')); la=sf(data.get('loan_amount'))

    if bm=='price' and hp>0:
        if dpct>0 and dp==0: dp=hp*dpct/100
        elif dp>0 and dpct==0: dpct=dp/hp*100
        la=hp-dp
    elif bm=='loan': hp=dp=dpct=0

    pp=sf(data.get('purchase_price')); asp=sf(data.get('asking_price')); ppsf=sf(data.get('price_per_sqft'))

    tax_rate=0.0125
    try:
        r=requests.get(f'https://api.api-ninjas.com/v1/propertytax?zip={zip_c}',headers={'X-Api-Key':NINJAS_API_KEY},timeout=5)
        if r.status_code==200:
            td=r.json()
            if isinstance(td,list) and td:
                v=float(td[0].get('yearly_tax_rate',0))
                if v>0: tax_rate=v
    except: pass

    mor=INT_RATE/12; n=360
    if loan_type=='HELOC':
        hr=sf(data.get('heloc_rate',8.5))/100/12; la=sf(data.get('heloc_borrow'))
        pi=la*hr; mtx=mins=pmi=0
    else:
        pi=la*(mor*(1+mor)**n)/((1+mor)**n-1) if la>0 else 0
        mtx=la*tax_rate/12; mins=la*0.005/12
        pmi=la*0.0085/12 if 0<dpct<20 else 0

    total=pi+mtx+mins+pmi+hoa
    if inc>0: fdti=(pi+mtx+mins+pmi)/inc*100; bdti=(total+dbt)/inc*100
    else: fdti=bdti=0
    qualifies=(fdti<=31 and bdti<=43) if inc>0 else None
    qual_msg=(f"{'Likely qualifies' if qualifies else 'May need review'} — Front {fdti:.1f}% / Back {bdti:.1f}%" if inc>0 else "Enter income to see qualification")

    if "740+" in credit and "Immediate" in timeline: priority="🔥 HOT — Call Today"; pn=1
    elif "680" in credit or "Immediate" in timeline: priority="⚡ WARM — 48hrs"; pn=2
    elif "620" in credit: priority="📋 ACTIVE — 60 Day"; pn=3
    else: priority="🌱 NURTURE"; pn=4

    ref=hp if hp>0 else la
    seg=("Ultra Luxury ($1M+)" if ref>=1_000_000 else "Luxury ($750K+)" if ref>=750_000 else "Premium ($500K+)" if ref>=500_000 else "Standard")

    # Life event priority boost
    if life in ['divorce','relocate']: priority="🔥 HOT — "+life.title(); pn=1

    wishlist=[]
    if beds: wishlist.append(f"{beds} Bedrooms")
    if baths: wishlist.append(f"{baths} Bathrooms")
    if garage: wishlist.append(garage)
    if vibe: wishlist.append(vibe)
    if commute: wishlist.append(f"Near {commute}")
    if must: wishlist+=[m.strip() for m in must.split(',') if m.strip()]

    dream_path=None
    if dream.strip() and hp>0:
        dream_path={"steps":[
            {"icon":"🏠","label":"Today — What You Can Get","value":fmt_s(hp),"desc":f"A home in your target market at today's prices with your current budget."},
            {"icon":"📈","label":"Year 3 — Projected Value","value":fmt_s(hp*1.18),"desc":f"At ~6% annual appreciation, your home could be worth {fmt_s(hp*1.18)} — building {fmt_s(hp*0.18)} in equity."},
            {"icon":"✨","label":"Year 5 — Your Stepping Stone","value":fmt_s(hp*1.34),"desc":f"In 5 years you'd have {fmt_s(hp*0.34)} in equity to leverage toward your dream home."},
            {"icon":"🌟","label":"Dream Home Goal","value":"Your Dream","desc":f"Use your equity toward: {dream[:80]}{'...' if len(dream)>80 else ''}"}
        ],"chart":[
            {"label":"Today","value":hp},{"label":"Yr 1","value":hp*1.06},{"label":"Yr 2","value":hp*1.12},
            {"label":"Yr 3","value":hp*1.18},{"label":"Yr 5","value":hp*1.34},{"label":"Yr 10","value":hp*1.79}
        ]}

    first=name.split()[0] if name else "there"
    t=fmt_s(total)
    bv=(f"Your total payment would be {t} — {fmt_s(pi)} P&I, {fmt_s(mtx)} taxes, {fmt_s(mins)} insurance"+(f", {fmt_s(pmi)} PMI" if pmi>0 else "")+(f", {fmt_s(hoa)} HOA" if hoa>0 else ".")+".")

    life_openers={
        'divorce': f"Hi {first}, this is Shiva Tamara. I know you're going through a difficult time. My job is to make sure you walk away from this with your finances protected and a clear path forward. ",
        'married': f"Hi {first}! Congratulations on the upcoming wedding! This is Shiva Tamara — let's make buying your first home together the best decision you make as a couple. ",
        'family':  f"Hi {first}! This is Shiva Tamara. Growing families need the right space — I specialize in finding homes that grow with you. ",
        'relocate':f"Hi {first}! This is Shiva Tamara. Welcome to LA — let me be your first call. I help relocators get pre-qualified before they even arrive. "
    }
    opener_prefix=life_openers.get(life,"")

    script={
        "call_opener": opener_prefix + f"I pulled your possibilities report for {zip_c}. " + (f"Great news — {bv} Your profile looks strong. Do you have 10 minutes?" if qualifies else f"{bv} I have a plan to get you there. Want to walk through it?"),
        "sms_followup": f"Hi {first}! 🏡 It's Shiva. Your possibilities report is ready — est. {t}/mo. I have strategies to save you thousands. Reply YES!",
        "voicemail": f"Hi {first}, Shiva Tamara — ShivaLuxury DRE 02251909. Your report shows {t}/mo. Call or text 310-422-5608!",
        "dream_response": f"I love that vision, {first}. Buying today at {fmt_s(hp)} is your launchpad. In 5 years that home could be worth {fmt_s(hp*1.34)}, giving you the equity to move into exactly what you described. Let's start your path today.",
        "objections": {
            "just_looking": f"Totally, {first}. Most clients started that way. 2026 market moves fast — knowing your numbers now puts you miles ahead. Quick 10 minutes?",
            "bad_credit":   f"No worries, {first}. I have lender partners who specialize in this. Let me connect you — zero obligation."
        }
    }

    row=[ts(),life,name,phone,email,zip_c,emp,loan_type,bm,
         fmt_s(hp) if hp else "N/A",fmt_s(dp) if dp else "N/A",
         f"{dpct:.1f}%" if dpct else "N/A",fmt_s(la),
         fmt_s(pp) if pp else "N/A",fmt_s(asp) if asp else "N/A",fmt_s(ppsf) if ppsf else "N/A",
         f"${pi:,.2f}",f"${mtx:,.2f}",f"{tax_rate*100:.3f}%",
         f"${mins:,.2f}",f"${pmi:,.2f}",f"${hoa:,.2f}",f"${total:,.2f}",
         fmt_s(inc),fmt_s(dbt),f"{fdti:.1f}%",f"{bdti:.1f}%",
         "Yes" if qualifies else ("No" if qualifies is False else "N/A"),
         credit,timeline,priority,seg,beds,baths,stories,garage,must,commute,vibe,dream[:80],
         buy_status,purpose,privacy,notes[:80]]
    saved,err=save('buyer',row)
    if saved: highlight('buyer','gold' if ref>=750_000 else 'pink' if pn==1 else None)
    print(f"[OK] Buyer → {name} | {seg} | {priority}")
    return jsonify({"status":"success","qualification":qual_msg,"qualifies":qualifies,
        "priority":priority,"segment":seg,"life_event":life,"wishlist":wishlist,
        "dream_path":dream_path,"sheets_saved":saved,"sheets_error":err,"script":script,
        "breakdown":{"p_and_i":round(pi,2),"monthly_tax":round(mtx,2),"tax_rate":f"{tax_rate*100:.3f}%",
                     "monthly_ins":round(mins,2),"pmi":round(pmi,2),"hoa":round(hoa,2),
                     "total_piti":round(total,2),"front_dti":round(fdti,1),"back_dti":round(bdti,1),
                     "rate":f"{INT_RATE*100:.2f}%","term":30}})

# ══════════════════════════════════════════════════════════════════════════════
# SELLER
# ══════════════════════════════════════════════════════════════════════════════
def seller(data):
    name=str(data.get('name','')).strip(); phone=str(data.get('phone','')).strip()
    email=str(data.get('email','')).strip(); address=str(data.get('address','')).strip()
    zip_c=str(data.get('zip_code','90210')).strip(); yr=str(data.get('year_purchased',''))
    beds=str(data.get('beds','3')); baths=str(data.get('baths','2'))
    cond=str(data.get('condition','Good')); stories=str(data.get('stories','2'))
    nxt=str(data.get('next_step','')); concern=str(data.get('concern',''))
    tl=str(data.get('timeline','')); notes=str(data.get('notes',''))
    life=str(data.get('life_event','none'))
    why_selling=str(data.get('why_selling',''))
    has_mortgage=str(data.get('has_mortgage',''))
    current_rate=str(data.get('current_rate',''))
    bal=sf(data.get('mortgage_balance')); est=sf(data.get('owner_estimate'))

    cm={'Excellent':1.05,'Good':1.0,'Fair':0.93,'Needs Work':0.85}
    ev=est*cm.get(cond,1.0) if est>0 else 750000
    commission=ev*0.05; net_eq=ev-bal; after_com=net_eq-commission
    buying_power=after_com*5 if after_com>0 else 0

    if "ASAP" in tl or "3-6" in tl: priority="🔥 HOT — Call Today"
    elif "6-12" in tl: priority="⚡ WARM — Follow Up"
    else: priority="🌱 NURTURE — Exploring"
    if life=='divorce': priority="🔥 HOT — Divorce / Urgent"

    seg=("Ultra Luxury ($1M+)" if ev>=1_000_000 else "Luxury ($750K+)" if ev>=750_000 else "Premium ($500K+)" if ev>=500_000 else "Standard")

    poss=[
        {"icon":"💰","title":f"Net equity: {fmt_s(net_eq)}","desc":f"After paying off your {fmt_s(bal)} mortgage, you walk away with approximately {fmt_s(net_eq)} in equity."},
        {"icon":"🏡","title":f"Buying power next: {fmt_s(buying_power)}","desc":f"Using your equity as a 20% down payment, you could buy a home up to {fmt_s(buying_power)} — a whole new range of possibilities."},
        {"icon":"🎯","title":"The buyer pays for their own agent — not you","desc":"When you sell, the buyer's agent fee is paid by the buyer. Your only cost is the listing commission (~5%). You keep far more than most sellers realize."}
    ]
    if "single" in nxt.lower() or stories=="2":
        poss.append({"icon":"♿","title":"Single-story homes are within your reach","desc":f"With {fmt_s(after_com)} in proceeds, single-story options in LA match your budget. You don't have to stay stuck in a home that no longer fits your life."})
    if life=='divorce':
        poss.append({"icon":"💔","title":"Selling in divorce — I'll make this easy","desc":f"I specialize in divorce sales. I work with both parties fairly, handle all paperwork, and make sure both of you walk away financially protected. You split {fmt_s(net_eq)} in equity."})

    concern_map={
        "Dont know what I can afford next":f"That's the most common concern. Based on your equity of {fmt_s(net_eq)}, here's what's possible next...",
        "Worried wont get enough":f"I understand. Based on today's market, your home could be worth {fmt_s(ev)}, giving you {fmt_s(net_eq)} in equity. Let's look at the real numbers.",
        "Dont know the process":"The process is simpler than most people think. I handle pricing, marketing, offers, and closing. You just say yes at the right moment.",
        "Emotional attachment":"That's completely natural. Your home holds memories. But think about what's possible next — a home that fits where you ARE today.",
        "Timing uncertainty":"The best time to explore is before you're committed. Let me show you your numbers now so you can move when YOU'RE ready.",
        "None just exploring":"Perfect — the best decisions come from information. Let me show you exactly what's possible."
    }
    first=name.split()[0] if name else "there"
    script={
        "opener":f"Hi {first}! Shiva Tamara — ShivaLuxury, DRE 02251909. Your home in {zip_c} could be worth {fmt_s(ev)}, meaning {fmt_s(net_eq)} in equity. I'd love to show you what's possible next — 10 minutes?",
        "sms":f"Hi {first}! 🏡 It's Shiva. Est. home value {fmt_s(ev)}, equity {fmt_s(net_eq)}. You have more options than you think. Reply YES!",
        "concern_response":concern_map.get(concern,"Let's talk through your situation. I'm here to help."),
        "possibilities":f"Here's what I want you to see, {first}: You have {fmt_s(net_eq)} in equity. After commission you walk away with {fmt_s(after_com)}. Buying power of {fmt_s(buying_power)} for your next home. And the buyer pays for their own agent — not you. Your life doesn't have to stay the same."
    }

    row=[ts(),life,name,phone,email,zip_c,address,yr,beds,baths,cond,stories,
         fmt_s(bal),fmt_s(est) if est else "N/A",fmt_s(ev),fmt_s(net_eq),
         fmt_s(after_com),fmt_s(buying_power),nxt,concern,tl,
         why_selling,has_mortgage,current_rate,priority,seg,notes[:80]]
    saved,err=save('seller',row)
    print(f"[OK] Seller → {name} | {seg} | {priority}")
    return jsonify({"status":"success","priority":priority,"segment":seg,
        "sheets_saved":saved,"sheets_error":err,"script":script,"possibilities":poss,
        "seller_data":{"est_value":round(ev,2),"net_equity":round(net_eq,2),
                       "after_commission":round(after_com,2),"buying_power":round(buying_power,2)}})

# ══════════════════════════════════════════════════════════════════════════════
# FRESH START
# ══════════════════════════════════════════════════════════════════════════════
def fresh_start(data):
    name=str(data.get('name','')).strip(); phone=str(data.get('phone','')).strip()
    email=str(data.get('email','')).strip(); address=str(data.get('address','')).strip()
    zip_c=str(data.get('zip_code','90210')).strip()
    situation=str(data.get('situation','Tax Delinquent'))
    years_behind=str(data.get('years_behind','1'))
    primary_need=str(data.get('primary_need',''))
    want_to_keep=str(data.get('want_to_keep',''))
    urgency=str(data.get('urgency',''))
    notes=str(data.get('notes',''))

    prop_val=sf(data.get('property_value')); mtg_bal=sf(data.get('mortgage_balance'))
    back_taxes=sf(data.get('back_taxes')); other_liens=sf(data.get('other_liens'))

    total_owed=mtg_bal+back_taxes+other_liens
    est_equity=prop_val-total_owed if prop_val>0 else 0

    # Estimate: Shiva pays back taxes + offers ~70% of equity above total owed
    closing_costs=prop_val*0.03 if prop_val>0 else 0
    if est_equity>0:
        cash_offer_base=est_equity*0.70
        walkaway_cash=max(0, cash_offer_base - closing_costs)
    else:
        walkaway_cash=0

    priority="🔥 URGENT — Distressed Lead"

    # Breakdown rows for display
    breakdown_rows=[
        {"ico":"🏠","lbl":"Estimated Property Value","val":fmt_s(prop_val),"note":"Based on your estimate","tot":False},
        {"ico":"🏦","lbl":"Remaining Mortgage","val":f"-{fmt_s(mtg_bal)}","note":"Balance owed to lender","tot":False},
        {"ico":"🏛️","lbl":"Back Taxes Owed","val":f"-{fmt_s(back_taxes)}","note":f"{years_behind} year(s) delinquent","tot":False},
        {"ico":"⚖️","lbl":"Other Liens","val":f"-{fmt_s(other_liens)}" if other_liens>0 else "$0","note":"Judgments, HOA, etc.","tot":False},
        {"ico":"💰","lbl":"Estimated Cash to You","val":fmt_s(walkaway_cash),"note":"After all debts cleared","tot":True}
    ]

    poss=[
        {"icon":"🌱","title":"Walk away debt-free with cash in hand","desc":f"Based on your numbers, you could walk away with approximately {fmt_s(walkaway_cash)} — all debts cleared, no foreclosure on your record, fresh start.","fresh":True},
        {"icon":"🛡️","title":"Stop the foreclosure clock","desc":"Once we agree on terms, I can move quickly to stop foreclosure proceedings and protect your credit from permanent damage.","fresh":True},
        {"icon":"💳","title":"Protect your credit — avoid bankruptcy","desc":"A foreclosure or tax lien stays on your credit for 7 years. A clean sale means you can rebuild and even buy again in 2–3 years.","fresh":True},
        {"icon":"🤝","title":"No harassment, no pressure — just options","desc":"I'm not a debt collector. I'm a licensed real estate agent who helps people in your situation find a dignified path forward. Everything we discuss is confidential.","fresh":True}
    ]

    if walkaway_cash > 0:
        poss.insert(0,{"icon":"✅","title":f"You could walk away with {fmt_s(walkaway_cash)}","desc":f"That's real money in your pocket — enough for a deposit on a new place, to pay off other debts, or to start fresh. You deserve that.","fresh":True})

    first=name.split()[0] if name else "there"
    script={
        "opener":f"Hi {first}, my name is Shiva Tamara — I'm a licensed real estate agent, not a collector. I'm calling because I help people in property hardship situations find a way out that protects them. I saw your situation and I have some options I'd like to walk you through — completely confidential, no pressure. Do you have a few minutes?",
        "sms":f"Hi {first}, this is Shiva — a real estate agent, not a collector. I may be able to help you walk away from your property with cash in hand and your credit protected. Completely confidential. Reply if you'd like to talk.",
        "hesitant":f"I completely understand the hesitation, {first}. You've probably been contacted by a lot of people trying to take advantage of your situation. I'm different — I'm licensed, I'm transparent, and I'll show you every number in writing. You make the decision. I just want to make sure you know all your options before the clock runs out.",
        "walk_away_clean":f"Here's what I want you to understand, {first}: you have {fmt_s(est_equity)} in equity right now. If we don't act, that equity disappears into foreclosure and you walk away with nothing. If we act now, you could walk away with {fmt_s(walkaway_cash)} in your pocket, zero debt on this property, and your credit protected. Which option sounds better to you?"
    }

    row=[ts(),name,phone,email,zip_c,address,situation,years_behind,
         fmt_s(prop_val),fmt_s(mtg_bal),fmt_s(back_taxes),fmt_s(other_liens),
         fmt_s(total_owed),fmt_s(est_equity),fmt_s(walkaway_cash),primary_need,
         want_to_keep,urgency,notes[:100],priority]
    saved,err=save('fresh_start',row)
    if saved: highlight('fresh_start','red')
    print(f"[OK] Fresh Start → {name} | {priority}")
    return jsonify({"status":"success","priority":priority,"sheets_saved":saved,"sheets_error":err,
        "script":script,"possibilities":poss,"breakdown_rows":breakdown_rows,
        "fresh_data":{"prop_value":round(prop_val,2),"total_owed":round(total_owed,2),
                      "est_equity":round(est_equity,2),"walkaway_cash":round(walkaway_cash,2)}})

# ══════════════════════════════════════════════════════════════════════════════
# LEASE
# ══════════════════════════════════════════════════════════════════════════════
def lease(data):
    name=str(data.get('name','')).strip(); phone=str(data.get('phone','')).strip()
    email=str(data.get('email','')).strip(); life=str(data.get('life_event','none'))
    zip_c=str(data.get('zip_code',''))
    area=str(data.get('area','')); budget=str(data.get('budget',''))
    size=str(data.get('size','')); move_in=str(data.get('move_in',''))
    ll=str(data.get('lease_length','')); parking=str(data.get('parking','1'))
    pets=str(data.get('pets','')); must=str(data.get('must_haves',''))
    move_in_funds=str(data.get('move_in_funds',''))
    notes=str(data.get('notes',''))

    if "ASAP" in move_in: priority="🔥 HOT — Immediate"
    elif "1 month" in move_in: priority="⚡ WARM — 30 Days"
    else: priority="📋 ACTIVE — Planning"
    if life in ['divorce','relocate']: priority="🔥 HOT — "+life.title()

    first=name.split()[0] if name else "there"
    poss=[{"icon":"🔑","title":f"{size} in {area or 'your target area'}","desc":f"Budget: ${budget}/mo · Move-in: {move_in} · Lease: {ll}"}]
    try:
        pk=int(parking.replace('+','').replace('4','4').split()[0])
        if pk>=4: poss.append({"icon":"🚗","title":f"Creative solution for {parking} parking spaces","desc":f"Finding {parking} spots on-site can be tough. I can pair a home/apartment with a nearby monthly secured parking garage — giving you all your spaces at a fraction of the cost."})
    except: pass
    if pets: poss.append({"icon":"🐾","title":f"Pet-friendly options for {pets}","desc":"I'll specifically filter for buildings that genuinely welcome your pets — not just 'pet tolerant' but actually built for it."})
    if life=='relocate': poss.append({"icon":"📦","title":"Short-term lease while you get settled","desc":"I'll find you a flexible lease so you can explore neighborhoods before committing. Then we transition you to buying when you're ready."})
    if life=='divorce': poss.append({"icon":"💔","title":"Fast placement — I understand your timeline","desc":"Divorce situations often need fast housing. I'll prioritize quick move-in options and work around your timeline."})

    script={"opener":f"Hi {first}! Shiva Tamara — ShivaLuxury, DRE 02251909. I saw your leasing inquiry for a {size} in {area}. I have some options that match — including {parking} parking. Do you have a few minutes?","sms":f"Hi {first}! 🔑 It's Shiva. I found {size} options in {area} within your budget. Reply YES to chat!"}
    row=[ts(),life,name,phone,email,zip_c,area,budget,size,move_in,ll,parking,pets,must,move_in_funds,notes[:80],priority]
    saved,err=save('lease',row)
    print(f"[OK] Lease → {name} | {priority}")
    return jsonify({"status":"success","priority":priority,"sheets_saved":saved,"sheets_error":err,"script":script,"possibilities":poss})

# ══════════════════════════════════════════════════════════════════════════════
# COMMERCIAL
# ══════════════════════════════════════════════════════════════════════════════
def commercial(data):
    name=str(data.get('name','')).strip(); phone=str(data.get('phone','')).strip()
    email=str(data.get('email','')).strip(); area=str(data.get('area',''))
    budget=str(data.get('budget','')); sqft=str(data.get('sqft',''))
    stype=str(data.get('space_type','')); ll=str(data.get('lease_length',''))
    reqs=str(data.get('requirements','')); use=str(data.get('use_type',''))
    parking=str(data.get('parking','0-5')); mv=str(data.get('move_in',''))
    notes=str(data.get('notes',''))

    if "ASAP" in mv: priority="🔥 HOT — Immediate"
    elif "1-3" in mv: priority="⚡ WARM — 30-90 Days"
    else: priority="📋 ACTIVE — Planning"

    first=name.split()[0] if name else "there"
    poss=[{"icon":"🏢","title":f"{sqft} sq ft {stype} in {area or 'LA'}","desc":f"Budget: ${budget}/mo · {use} · Lease: {ll}"}]
    if "Loading Dock" in reqs: poss.append({"icon":"🚚","title":"Loading dock — specialized search","desc":"Loading dock spaces are in high demand. I'll target industrial/flex zones with verified dock access and your required square footage."})
    if "Showroom" in reqs: poss.append({"icon":"🪟","title":"High-visibility showroom","desc":"Street-facing retail/showroom spaces in high-foot-traffic locations that maximize your visibility."})
    if any(x in parking for x in ["20+","11-20"]): poss.append({"icon":"🅿️","title":f"Large parking — creative solutions","desc":f"Finding {parking} spaces on-site can be challenging. I can combine on-site parking with nearby private lots to meet your total need at a lower cost."})

    script={"opener":f"Hi {first}! Shiva Tamara — ShivaLuxury, DRE 02251909. I saw your commercial inquiry for {sqft} sq ft in {area}. I have spaces that match your specific requirements. Do you have 10 minutes?","sms":f"Hi {first}! 🏢 It's Shiva. I found {stype} options in {area} that match your needs. Reply YES!"}
    row=[ts(),name,phone,email,area,budget,sqft,stype,ll,reqs,use,parking,mv,notes[:80],priority]
    saved,err=save('commercial',row)
    print(f"[OK] Commercial → {name} | {priority}")
    return jsonify({"status":"success","priority":priority,"sheets_saved":saved,"sheets_error":err,"script":script,"possibilities":poss})

# ══════════════════════════════════════════════════════════════════════════════
# SELF-EMPLOYED
# ══════════════════════════════════════════════════════════════════════════════
def self_employed(data):
    name=str(data.get('name','')).strip(); phone=str(data.get('phone','')).strip()
    email=str(data.get('email','')).strip(); zip_c=str(data.get('zip_code','90210')).strip()
    btype=str(data.get('business_type','')); yrs=str(data.get('years_in_business',''))
    credit=str(data.get('credit','')); notes=str(data.get('notes',''))
    rev=sf(data.get('monthly_revenue')); inc=sf(data.get('monthly_income'))
    bnk=sf(data.get('bank_balance')); inv=sf(data.get('investments')); hp=sf(data.get('home_price'))
    total_assets=bnk+inv

    if "740+" in credit: priority="🔥 HOT — Strong Profile"
    elif "680" in credit: priority="⚡ WARM — Good Candidate"
    else: priority="📋 ACTIVE — Build & Qualify"

    yrs_num=0
    try: yrs_num=int(yrs.split()[0])
    except: pass

    loan_opts=[]
    if rev>0 and yrs_num>=1:
        loan_opts.append({"tag":"AVAILABLE NOW","name":"Bank Statement Loan","desc":f"12–24 months of bank statements instead of tax returns. Your {fmt_s(rev)}/mo revenue could qualify you. Down payment typically 10–20%. Perfect for business owners with strong cash flow."})
    if "Real Estate" in btype or inv>0:
        loan_opts.append({"tag":"AVAILABLE NOW","name":"DSCR Loan","desc":"Qualifies based on the property's rental income, not your personal income. No tax returns needed. Great if you're building a rental portfolio."})
    if total_assets>=hp*0.3 and hp>0:
        loan_opts.append({"tag":"AVAILABLE NOW","name":"Asset Depletion Loan","desc":f"Your assets of {fmt_s(total_assets)} can be used as qualifying income. Lenders divide your assets over 360 months — which may be enough to qualify even without traditional income docs."})
    if not loan_opts:
        loan_opts.append({"tag":"PATH TO QUALIFY","name":"P&L Statement Loan","desc":"A 12-month profit & loss statement prepared by a CPA can substitute for tax returns with many lenders. We can start this path now."})

    roadmap=[]
    if yrs_num<2: roadmap.append({"title":"Document 24 months of business activity","desc":"Keep detailed bank statements, invoices, and business records. This is your #1 asset for qualification."})
    if "Building" in credit or "Fair" in credit:
        roadmap.append({"title":"Improve credit to 680+","desc":"Pay down revolving balances below 30%, dispute errors, avoid new inquiries. This can add 40–80 points in 6–12 months."})
        roadmap.append({"title":"Set up a business credit card","desc":"A separate business credit profile strengthens your application and shows financial discipline to lenders."})
    if bnk<hp*0.1 and hp>0: roadmap.append({"title":f"Build reserves to {fmt_s(hp*0.15)}","desc":"Lenders want 3–6 months of mortgage payments in savings. Start a dedicated home purchase account now."})
    roadmap.append({"title":"Connect with a bank statement lender today","desc":"You may qualify NOW with the right lender. I have partners who specialize in self-employed borrowers. Let me connect you — free, no obligation."})
    roadmap.append({"title":"Get pre-qualified with current documents","desc":"Even if you're not ready to buy, a pre-qualification letter shows sellers you're serious and lets you move fast when the right home appears."})

    first=name.split()[0] if name else "there"
    script={"opener":f"Hi {first}! Shiva Tamara — ShivaLuxury, DRE 02251909. I reviewed your self-employed profile. The good news — you have options most agents don't even know exist. I have lender partners who work specifically with business owners. Do you have 10 minutes?","sms":f"Hi {first}! 💼 It's Shiva. Your possibilities report is ready — you have loan options even without 2 years of tax returns. Reply YES to learn more!"}

    opts_str='; '.join([l['name'] for l in loan_opts])
    row=[ts(),name,phone,email,zip_c,btype,yrs,fmt_s(rev),fmt_s(inc),fmt_s(bnk),fmt_s(inv),credit,fmt_s(hp),notes[:80],priority,opts_str]
    saved,err=save('self_employed',row)
    print(f"[OK] Self-Employed → {name} | {priority}")
    return jsonify({"status":"success","priority":priority,"sheets_saved":saved,"sheets_error":err,"script":script,"loan_options":loan_opts,"roadmap":roadmap})

# ─── HEALTH ───────────────────────────────────────────────────────────────────
@app.route('/health')
def health():
    return jsonify({"status":"ok","sheets":gc is not None,"sheet":SHEET_NAME,
                    "tabs":list(TABS.values()),"rate":f"{INT_RATE*100:.2f}%","time":datetime.now().isoformat()})

if __name__=='__main__':
    port=int(os.environ.get("PORT",5001))
    print(f"\n{'='*58}")
    print(f"  ShivaLuxury — Know Your Possibilities (Final Phase 1)")
    print(f"  http://localhost:{port}")
    print(f"  Sheets: {'✅ Connected' if gc else '❌ Not connected'}")
    print(f"  Tabs: {', '.join(TABS.values())}")
    print(f"{'='*58}\n")
    app.run(host='0.0.0.0',port=port,debug=False)
