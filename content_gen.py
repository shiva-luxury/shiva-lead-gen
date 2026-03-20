"""
ShivaLuxury — Phase 2 Social Content Generator
================================================
Generates ready-to-post content for Instagram, TikTok, Facebook, LinkedIn, YouTube.
Works standalone with templates; optionally enhanced by Claude API if ANTHROPIC_API_KEY is set.
"""

import os, json
from datetime import datetime, timedelta
import calendar

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
_ai_client = None

if ANTHROPIC_API_KEY:
    try:
        import anthropic
        _ai_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        print("[OK] Content AI: Claude enhanced mode")
    except ImportError:
        print("[WARN] anthropic not installed — template mode only")

PLATFORMS = ['instagram', 'tiktok', 'facebook', 'linkedin', 'youtube']

# ── Shared safe context builder ────────────────────────────────────────────────
def _ctx(data):
    """Normalize lead data into safe template context."""
    hp = float(data.get('home_price') or data.get('owner_estimate') or data.get('property_value') or 0)
    piti = float(data.get('total_piti') or 0)
    eq   = float(data.get('net_equity') or data.get('est_equity') or 0)
    wc   = float(data.get('walkaway_cash') or 0)
    return {
        'price':    f"${hp:,.0f}" if hp else "$800,000",
        'monthly':  f"${piti:,.0f}" if piti else "$5,200",
        'equity':   f"${eq:,.0f}" if eq else "$350,000",
        'walkaway': f"${wc:,.0f}" if wc else "$120,000",
        'zip':      str(data.get('zip_code') or data.get('area') or 'LA'),
        'area':     str(data.get('area') or data.get('zip_code') or 'Los Angeles'),
        'size':     str(data.get('size') or '2BR'),
        'budget':   str(data.get('budget') or '3,500'),
        'sqft':     str(data.get('sqft') or '2,000'),
        'year':     str(data.get('year_purchased') or '2018'),
        'credit':   str(data.get('credit') or '720+'),
    }

# ── TEMPLATES — 6 paths × 5 platforms ─────────────────────────────────────────
TEMPLATES = {

  'buy': {
    'instagram': {
      'type': 'Carousel (5 slides)',
      'hook': "You make good money. Here's EXACTLY what home that buys you in LA right now 🏡",
      'caption': "Stop scrolling Zillow wondering. This is what {monthly}/mo actually gets you in {zip}.\n\nSwipe → I break down P&I, property taxes, insurance, PMI, and HOA.\n\nThe real number. Not the Zillow estimate.\n\nI run this for every client before they fall in love with a house. DM me YOUR numbers — free, 5 minutes.",
      'hashtags': "#LARealestate #YouCan #ShivaLuxury #HomeBuying #FirstTimeHomeBuyer #BuyingAHome #LosAngelesHomes #HousingMarket2026 #KnowYourNumbers #PITI #MortgageCalculator #LAHomeBuyer",
      'cta': "DM 'NUMBERS' for your free possibilities report"
    },
    'tiktok': {
      'type': 'Talking head + screen share (60 sec)',
      'hook': "POV: You finally stop guessing and find out exactly what you can afford in LA",
      'caption': "I'm going to show you the REAL monthly payment on a {price} home in {zip}.\n\nMost people are shocked. Some are pleasantly surprised. All of them are glad they know.\n\nWatch to the end — I show you 3 ways to lower it.\n\nFollow for more LA real estate math.",
      'hashtags': "#LARealestate #HomeBuying #RealEstateTikTok #Mortgage #YouCan #ShivaLuxury #LAHomes #2026Housing #PITI",
      'cta': "Link in bio — get YOUR free possibilities report"
    },
    'facebook': {
      'type': 'Long-form post with image',
      'hook': "Are you waiting for the 'right time' to buy in LA? Let me show you something.",
      'caption': "Most people I talk to have been watching the market for 2–3 years.\n\nWaiting for prices to drop. Waiting for rates to fall.\n\nMeanwhile, LA home values have kept climbing.\n\nHere's what I tell every client: the best time to run your numbers is NOW — not to buy, but to KNOW.\n\nIf you're buying in {zip}, here's what you could do today:\n✅ Know your real PITI payment (taxes + insurance included)\n✅ Know your DTI ratio\n✅ Know what programs you actually qualify for\n✅ Know your path even if you can't buy today\n\nThis takes 5 minutes. It's free. And it changes everything.\n\nComment 'READY' and I'll send you the link.",
      'hashtags': "#LARealestate #HomeBuying #ShivaLuxury #LosAngeles #YouCan #MortgageHelp",
      'cta': "Comment 'READY' for the free report link"
    },
    'linkedin': {
      'type': 'Professional insight post',
      'hook': "Why I calculate PITI for every buyer before they see a single listing",
      'caption': "Most agents send buyers to open houses before running their numbers.\n\nI do the opposite.\n\nBefore any client sees a home, I calculate:\n→ Principal & Interest at current rates\n→ Monthly property tax (actual ZIP-code rate, not an estimate)\n→ Homeowners insurance\n→ PMI if the down payment is under 20%\n→ HOA fees\n→ Front and back DTI ratios\n\nA {price} home in {zip} has a real monthly cost of approximately {monthly}. That number changes everything about what a buyer should be targeting.\n\nI built a tool that runs this in 3 minutes. Every buyer gets their full possibilities report before they fall in love with the wrong house.\n\nThis is what professional real estate looks like in 2026.",
      'hashtags': "#RealEstate #HomeBuying #ClientFirst #ShivaLuxury #LARealestate #RealEstateTech #Mortgage",
      'cta': "Connect with me to see the tool"
    },
    'youtube': {
      'type': 'Explainer video (8–12 min)',
      'hook': "The REAL Cost of Buying a Home in LA in 2026 (Full PITI Breakdown)",
      'caption': "In this video I break down the REAL monthly cost of homeownership in Los Angeles — not just the mortgage payment, but every single component of PITI. I show how property tax rates vary by ZIP code, what PMI actually costs, and the exact DTI thresholds lenders use.\n\nTIMESTAMPS\n0:00 Why most buyers get surprised at closing\n1:30 What PITI actually stands for\n3:00 Property taxes in LA by ZIP\n5:00 PMI — what it is and how to avoid it\n7:00 The DTI ratio that determines qualification\n9:30 What to do if you don't qualify yet\n11:00 Free possibilities report",
      'hashtags': "LA real estate 2026, home buying Los Angeles, PITI breakdown, mortgage calculator LA, first time home buyer LA, ShivaLuxury",
      'cta': "Free possibilities report — link in description"
    }
  },

  'sell': {
    'instagram': {
      'type': 'Before/After carousel (4 slides)',
      'hook': "Your LA home might be worth more than you think 👀 Here's the real number",
      'caption': "I just ran the numbers for a homeowner in {zip}.\n\nBought in {year}. Estimate today: {price}. Equity: {equity}.\n\nBuying power for their next home: 5× that.\n\nMost sellers don't know their own numbers. That's why they wait.\n\nDM 'EQUITY' and I'll run yours — free, no commitment.",
      'hashtags': "#SellingHome #LARealestate #HomeEquity #ShivaLuxury #YouCan #LAHomeSeller #RealEstate2026 #EquityRich",
      'cta': "DM 'EQUITY' for your free equity report"
    },
    'tiktok': {
      'type': 'Story format (45 sec)',
      'hook': "I told a homeowner in LA she had {equity} in equity she didn't know about",
      'caption': "She bought years ago. Hasn't thought about selling. But her neighborhood changed, her family grew, and she was sitting on equity she could USE.\n\nThis is what I do — I show homeowners what's actually possible. No pressure, no pitch. Just your numbers.\n\nDM me your ZIP code and I'll run your equity estimate.",
      'hashtags': "#SellingAHome #LARealestate #HomeEquity #RealEstateTikTok #ShivaLuxury",
      'cta': "DM your ZIP for a free estimate"
    },
    'facebook': {
      'type': 'Value post with poll',
      'hook': "LA homeowners: Do you actually know what your home is worth right now?",
      'caption': "If you bought in LA in the last 10 years, you likely have significant equity — and most homeowners have NO idea how much.\n\nI run a free equity analysis for any homeowner. No obligation. No listing pitch. Just your numbers.\n\nHere's what I calculate:\n📊 Estimated market value\n💰 Net equity after your mortgage\n🏡 What you could afford to buy next\n📋 What 5% commission actually takes out vs. what you keep\n\nPoll: Do you know your home's approximate current value?\n→ Yes, roughly\n→ No idea\n→ I've been meaning to find out\n\nComment below or message me directly.",
      'hashtags': "#SellingAHome #LARealestate #HomeEquity #ShivaLuxury #LosAngeles",
      'cta': "Message 'EQUITY' for a free analysis"
    },
    'linkedin': {
      'type': 'Market insight post',
      'hook': "Why LA homeowners are sitting on life-changing equity they aren't using",
      'caption': "The average LA homeowner who bought 7+ years ago has accumulated substantial equity — often {equity} or more depending on location.\n\nMost of them:\n→ Don't know the exact number\n→ Think selling is complicated\n→ Don't realize the buyer's agent fee is paid by the BUYER\n→ Don't know their equity can become 5× buying power for their next home\n\nI specialize in educating homeowners on what's actually possible before they decide anything. The conversation is free. The information is life-changing.",
      'hashtags': "#RealEstate #LARealEstate #HomeEquity #ShivaLuxury #WealthBuilding #SellYourHome",
      'cta': "DM me for a free equity analysis"
    },
    'youtube': {
      'type': 'Case study / how-to (10 min)',
      'hook': "How Much is Your LA Home Worth in 2026? (Free Equity Calculator Walkthrough)",
      'caption': "I walk through exactly how to calculate your home's current market value, net equity, and what it means for your next move. Real numbers — condition adjustments, commission breakdown, and how to calculate buying power for your next home.\n\nTIMESTAMPS\n0:00 Why homeowners underestimate their equity\n2:00 How I estimate market value\n4:00 The commission breakdown (it's less than you think)\n6:00 Calculating your buying power\n8:00 Free equity report — run your own numbers",
      'hashtags': "sell home Los Angeles, home equity calculator, LA home value 2026, ShivaLuxury, real estate equity",
      'cta': "Run your own equity report — link in description"
    }
  },

  'lease': {
    'instagram': {
      'type': 'Tips carousel (5 slides)',
      'hook': "Renting in LA in 2026? Here's what I wish every renter knew before signing 🔑",
      'caption': "Slide 1: Your TOTAL move-in = first + last + deposit (budget 3× rent)\nSlide 2: 'Pet-friendly' ≠ 'pet-welcoming' — ask these 3 questions\nSlide 3: Parking in LA is a separate negotiation\nSlide 4: Month-to-month vs 12-month — when each makes sense\nSlide 5: Using a leasing agent costs you NOTHING\n\nDM 'LEASE' and I'll help you find your perfect place in {area}.",
      'hashtags': "#LARentals #LARenting #ShivaLuxury #YouCan #LosAngelesApartments #RentingLA #2026Rentals #LeaseLA #TenantRights",
      'cta': "DM 'LEASE' — I work for the tenant, not the landlord"
    },
    'tiktok': {
      'type': 'Quick tips (30 sec)',
      'hook': "3 things your LA landlord doesn't want you to know before you sign",
      'caption': "1. You can negotiate the lease start date\n2. Pet deposits are often negotiable\n3. A leasing agent represents YOU — and it's completely free\n\nI help renters find exactly what they need in {area}. Follow for more LA renting tips.",
      'hashtags': "#LARenting #RentingTips #LAapartments #ShivaLuxury #RealEstateTikTok #TenantTips",
      'cta': "DM me your budget and area — I'll find your match"
    },
    'facebook': {
      'type': 'Community post',
      'hook': "Looking for a rental in {area}? Here's what's actually available and how to get it.",
      'caption': "Finding a great rental in LA is harder than it looks. The best listings go fast, photos are often misleading, and half the 'available' units already have applications in.\n\nI help renters navigate this — completely free. I represent the tenant, I know which buildings are well-managed, and I find options that aren't posted publicly yet.\n\nIf you're looking for:\n🔑 {size} unit in {area}\n💰 Under ${budget}/mo\n🐾 Pet-friendly\n🚗 Parking included\n\n...message me. Let me do the searching for you.",
      'hashtags': "#LARentals #LAapartments #ShivaLuxury #YouCan #FindingApartmentLA",
      'cta': "Message me your requirements — free service"
    },
    'linkedin': {
      'type': 'Professional relocation post',
      'hook': "Relocating to LA for work? Here's how to secure housing before you arrive.",
      'caption': "One of the most stressful parts of corporate relocation is finding housing in an unfamiliar market under time pressure.\n\nI specialize in working with relocating professionals:\n→ Virtual tours and remote showings\n→ Flexible and short-term lease options\n→ Furnished transition housing\n→ Path to buying when you're ready\n\nIf you or someone on your team is relocating to the LA area, I'd be glad to help. Initial consultation is always free.",
      'hashtags': "#Relocation #LARealEstate #CorporateRelocation #ShivaLuxury #LosAngeles #TenantRep",
      'cta': "Connect with me for a free relocation consultation"
    },
    'youtube': {
      'type': 'Neighborhood guide (12 min)',
      'hook': "Best Neighborhoods to Rent in LA in 2026 — Price, Vibe & Commute Guide",
      'caption': "I break down the top rental neighborhoods in LA by budget, commute, and lifestyle — which areas have the best pet-friendly buildings, parking options, and what's actually available now. I also explain how tenant representation works and why it costs you nothing.\n\nTIMESTAMPS\n0:00 The rental market in LA right now\n2:00 Best neighborhoods by budget\n5:00 How to find pet-friendly buildings\n7:00 What tenant representation means\n9:00 How to get started",
      'hashtags': "LA apartments 2026, renting in Los Angeles, best neighborhoods LA, ShivaLuxury, tenant representation",
      'cta': "Message me your requirements — free tenant representation"
    }
  },

  'loan': {
    'instagram': {
      'type': 'Myth-busting carousel (4 slides)',
      'hook': "You're self-employed. You CAN still buy a home in LA. Here's exactly how 💼",
      'caption': "Myth: You need 2 years of tax returns.\nTruth: Bank statement loans exist.\n\nMyth: Self-employed = unqualified.\nTruth: Wrong lender, wrong question.\n\nMyth: You need W-2 income.\nTruth: DSCR, asset depletion, and P&L loans all qualify business owners.\n\nI specialize in helping self-employed buyers get the right loan for how they actually earn.\n\nDM 'SELFEMPLOYED' and let's look at your options.",
      'hashtags': "#SelfEmployedBuyer #BankStatementLoan #ShivaLuxury #YouCan #LARealestate #BusinessOwnerHomeBuyer #DSCRLoan #MortgageOptions",
      'cta': "DM 'SELFEMPLOYED' — free loan options review"
    },
    'tiktok': {
      'type': 'Education (45 sec)',
      'hook': "Banks said no. My lender said yes. Here's the loan type that changed everything.",
      'caption': "If you're self-employed and a traditional bank turned you down, you need to know about bank statement loans.\n\nInstead of tax returns, you show 12–24 months of statements. Your revenue qualifies you — not your adjusted gross income.\n\nI have lender partners who specialize in exactly this. DM me and I'll connect you — free.",
      'hashtags': "#SelfEmployedMortgage #BankStatementLoan #ShivaLuxury #RealEstateTikTok #MortgageTips",
      'cta': "DM 'BANKSTATEMENT' to get connected"
    },
    'facebook': {
      'type': 'Educational post',
      'hook': "Attention self-employed business owners in LA: you have more mortgage options than your bank told you.",
      'caption': "Most banks are set up for W-2 employees. If you own a business, your tax returns likely show less income than you actually earn — because you're smart about deductions.\n\nHere's what your bank didn't tell you:\n\n✅ Bank Statement Loans — qualify on revenue, not taxable income\n✅ DSCR Loans — qualify on rental income, not personal income\n✅ Asset Depletion — qualify based on savings and investments\n✅ P&L Statement Loans — CPA-prepared P&L as income documentation\n\nI work with lenders who specialize in self-employed borrowers. This is information you deserve to have.\n\nComment 'SELFEMPLOYED' and I'll show you which options apply.",
      'hashtags': "#SelfEmployed #BusinessOwner #MortgageOptions #ShivaLuxury #LARealestate",
      'cta': "Comment 'SELFEMPLOYED' for a free options review"
    },
    'linkedin': {
      'type': 'Professional education post',
      'hook': "Self-employed buyers are the most underserved segment in real estate.",
      'caption': "Traditional mortgage underwriting was designed for W-2 employees. It penalizes business owners for doing exactly what their CPAs tell them to do: maximize deductions.\n\nThe result: successful entrepreneurs who can't qualify through traditional channels — not because they can't afford the home, but because the system wasn't built for them.\n\nThe solution exists:\n→ Bank statement loans (12–24 months of statements)\n→ DSCR loans (rental income qualification)\n→ Asset depletion qualification\n→ P&L documentation with CPA certification\n\nI specialize in this segment. If you're a business owner who has been told 'no' — or you haven't asked yet — let's talk.",
      'hashtags': "#SelfEmployed #BusinessOwner #Mortgage #RealEstate #ShivaLuxury #Entrepreneurship #LARealestate",
      'cta': "DM me — free self-employed loan consultation"
    },
    'youtube': {
      'type': 'Deep-dive education (15 min)',
      'hook': "How Self-Employed Buyers Get Mortgages in 2026 — All 4 Loan Types Explained",
      'caption': "I walk through every non-traditional mortgage option available to self-employed buyers: bank statement loans, DSCR loans, asset depletion qualification, and P&L statement loans. How each works, who qualifies, and what documents you need.\n\nTIMESTAMPS\n0:00 Why traditional banks say no\n2:00 Bank statement loans explained\n5:00 DSCR loans for investors\n8:00 Asset depletion qualification\n10:00 P&L statement loans\n12:00 How to get started",
      'hashtags': "self employed mortgage 2026, bank statement loan LA, DSCR loan, ShivaLuxury, non-QM mortgage",
      'cta': "Get your free self-employed loan options report — link in description"
    }
  },

  'wayout': {
    'instagram': {
      'type': 'Awareness carousel (3 slides)',
      'hook': "Facing property hardship in LA? You have more options than you think. 🚪",
      'caption': "This isn't a pitch. This is information.\n\nIf you're behind on taxes, facing foreclosure, or need to get out from under a property — you may have equity you don't know about.\n\nYou may be able to walk away with cash.\nYou may be able to protect your credit.\n\nI help people in exactly this situation. Confidential. No judgment. Licensed agent.\n\nDM 'HELP' and let's see what's possible.",
      'hashtags': "#FreshStart #PropertyHelp #ShivaLuxury #YouCan #LARealestate #DistressedProperty #WalkAwayCash #ConfidentialHelp",
      'cta': "DM 'HELP' — confidential, no pressure"
    },
    'tiktok': {
      'type': 'Compassionate education (45 sec)',
      'hook': "If you're behind on your mortgage in LA — watch this before you do anything else",
      'caption': "Before you panic. Before you ignore the letters. Before you let foreclosure happen.\n\nYou need to know your options. You might have equity. You might be able to sell and walk away with cash. You might be able to protect your credit.\n\nI help people in exactly this situation. DM me. It's confidential. I'm a licensed agent, not a debt collector.",
      'hashtags': "#PropertyHelp #MortgageHelp #ShivaLuxury #FreshStart #RealEstateTikTok #LARealestate",
      'cta': "DM 'HELP' — I'll show you your options privately"
    },
    'facebook': {
      'type': 'Compassionate community post',
      'hook': "To anyone quietly dealing with a property situation they're not sure how to handle:",
      'caption': "I see you. The letters. The stress. The uncertainty.\n\nBefore you assume there's no way out — let me show you the real numbers.\n\nIf your home has any value above what you owe, you may be able to:\n✅ Sell and walk away with cash in hand\n✅ Stop collection proceedings\n✅ Protect your credit from long-term damage\n✅ Get a clean start without bankruptcy\n\nI'm a licensed real estate agent, not a collector. Everything is confidential. There is no pressure.\n\nMessage me privately. I'll show you exactly what's possible.",
      'hashtags': "#PropertyHelp #ShivaLuxury #FreshStart #LARealestate #ConfidentialHelp",
      'cta': "Message me privately — confidential consultation"
    },
    'linkedin': {
      'type': 'Referral partner post',
      'hook': "Property hardship situations in LA: what professionals should know about options",
      'caption': "Many property owners in hardship situations have equity they don't know about — and assume they have no options.\n\nAs a licensed agent who specializes in these situations, I've found that most can walk away with cash, protect their credit, and avoid bankruptcy — with the right information in time.\n\nIf you work with clients (attorneys, CPAs, advisors) who may be in this situation, I'm a confidential, professional referral partner. I handle every case with complete discretion.\n\nLet's connect.",
      'hashtags': "#RealEstate #DistressedProperty #ShivaLuxury #ReferralPartner #LARealEstate #PropertyLaw",
      'cta': "Connect with me for referral partnership"
    },
    'youtube': {
      'type': 'Honest guide (10 min)',
      'hook': "Facing Property Hardship in LA? Here Are Your Real Options (Honest Guide)",
      'caption': "I explain every option available to a property owner facing hardship — selling before foreclosure, calculating equity, protecting your credit, and understanding what a clean exit actually looks like. No sales pitch. Just real information.\n\nTIMESTAMPS\n0:00 You have more options than you think\n2:00 How to calculate your equity\n4:00 The clean sale — what it looks like\n6:00 Protecting your credit\n8:00 Free confidential consultation",
      'hashtags': "property hardship Los Angeles, foreclosure options LA, ShivaLuxury, real estate exit strategy, distressed property LA",
      'cta': "Free confidential consultation — link in description"
    }
  },

  'commercial': {
    'instagram': {
      'type': 'Education carousel (4 slides)',
      'hook': "Finding commercial space in LA? Here's what most business tenants get wrong 🏢",
      'caption': "Slide 1: NNN vs Gross lease — know the difference before you sign\nSlide 2: Buildout allowance — always negotiate, most tenants don't\nSlide 3: Parking ratios — the hidden dealbreaker\nSlide 4: CAM charges — the cost most tenants miss\n\nI represent commercial tenants in LA. I know the market, the buildings, and where the leverage is.\n\nDM 'COMMERCIAL' for a free space search.",
      'hashtags': "#CommercialRealEstate #LACommercial #ShivaLuxury #YouCan #OfficeSpace #RetailSpace #NNNLease #TenantRep",
      'cta': "DM 'COMMERCIAL' — free commercial search"
    },
    'tiktok': {
      'type': 'Education (45 sec)',
      'hook': "NNN lease vs Gross lease — which one is actually cheaper? (Most tenants get this wrong)",
      'caption': "A lower base rent does NOT always mean a better deal.\n\nA NNN lease with property tax, insurance, and CAM charges can cost 30–40% more than the base rent suggests.\n\nI help LA businesses find space AND negotiate terms that actually protect you.\n\nDM me — free commercial tenant representation.",
      'hashtags': "#CommercialRealEstate #NNNLease #ShivaLuxury #LABusiness #RealEstateTikTok #BusinessOwner",
      'cta': "DM 'NNN' to learn how to evaluate your lease"
    },
    'facebook': {
      'type': 'Business community post',
      'hook': "LA business owners: Are you overpaying for your commercial space?",
      'caption': "Most commercial leases in LA include charges that tenants don't understand or don't negotiate. CAM fees. Property tax pass-throughs. Insurance allocations. Buildout costs.\n\nI represent commercial tenants — not landlords. My job is to find the right space at the right terms and make sure you understand every line before you sign.\n\nIf you're:\n🏢 Looking for {sqft} sq ft in {area}\n📋 Approaching a lease renewal\n🔍 Trying to understand what you're currently paying for\n\n...let's talk. First consultation is free.\n\nComment 'COMMERCIAL' or message me directly.",
      'hashtags': "#CommercialRealEstate #LABusiness #ShivaLuxury #OfficeSpace #RetailLA #TenantRep",
      'cta': "Comment 'COMMERCIAL' for a free consultation"
    },
    'linkedin': {
      'type': 'Market insight post',
      'hook': "LA commercial real estate in 2026: what tenants negotiating right now are getting",
      'caption': "The LA commercial market has shifted. What informed tenants are negotiating:\n\n→ 3–6 months free rent on longer leases\n→ Full buildout allowances on Class A space\n→ Flexible early termination clauses\n→ Parking ratios above standard\n→ Personal guarantee reductions for established businesses\n\nI represent commercial tenants exclusively in this market. If you're looking for space or approaching a renewal — the leverage is there if you know how to use it.",
      'hashtags': "#CommercialRealEstate #LARealEstate #TenantRep #ShivaLuxury #BusinessRealEstate #OfficeSpace2026",
      'cta': "DM me — free commercial tenant representation"
    },
    'youtube': {
      'type': 'Market guide (12 min)',
      'hook': "LA Commercial Real Estate 2026 — What Tenants Must Know Before Signing",
      'caption': "I walk through the LA commercial market for tenants — office, retail, industrial, and flex space. How to evaluate NNN vs gross leases, how to negotiate buildout allowances, and what current market conditions mean for your leverage.\n\nTIMESTAMPS\n0:00 LA commercial market overview 2026\n2:00 NNN vs Gross lease — full breakdown\n5:00 Negotiating buildout allowances\n7:00 CAM charges explained\n9:00 Finding space in {area}\n11:00 Free commercial search",
      'hashtags': "commercial real estate LA 2026, NNN lease explained, tenant representation Los Angeles, ShivaLuxury, office space LA",
      'cta': "Free commercial space search — link in description"
    }
  }
}

# ── Generator ──────────────────────────────────────────────────────────────────
def generate_content(path, lead_data=None, platform=None):
    """
    Generate social content for a given path and optional platform.
    Returns dict keyed by platform name.
    """
    if path not in TEMPLATES:
        path = 'buy'

    lead_data = lead_data or {}
    ctx = _ctx(lead_data)
    result = {}

    platforms = [platform] if platform and platform in PLATFORMS else PLATFORMS

    for p in platforms:
        tmpl = TEMPLATES[path].get(p, {})
        if not tmpl:
            continue
        try:
            formatted = {
                'content_type': tmpl.get('type', ''),
                'hook':         tmpl.get('hook', '').format(**ctx),
                'caption':      tmpl.get('caption', '').format(**ctx),
                'hashtags':     tmpl.get('hashtags', ''),
                'cta':          tmpl.get('cta', ''),
            }
        except KeyError:
            # Safe fallback if a key is missing from ctx
            formatted = {k: v for k, v in tmpl.items() if k != 'type'}
            formatted['content_type'] = tmpl.get('type', '')

        # Optional AI enhancement
        if _ai_client:
            try:
                enhanced = _ai_enhance(path, p, formatted, ctx)
                if enhanced:
                    formatted = enhanced
            except Exception as e:
                print(f"[CONTENT AI WARN] {e}")

        result[p] = formatted

    return result


def _ai_enhance(path, platform, base, ctx):
    """Call Claude to enhance a template with AI-generated copy."""
    prompt = f"""You are a social media specialist for ShivaLuxury, a luxury real estate brand in Los Angeles. DRE 02251909.

Brand voice: direct, data-driven, empowering, luxury but accessible. The agent is Shiva Tamara.

Enhance this {platform} post for the '{path}' path with this client context: {json.dumps(ctx)}.

Base template:
Hook: {base['hook']}
Caption: {base['caption']}
CTA: {base['cta']}

Return ONLY valid JSON with keys: hook, caption, hashtags, cta. Keep the same structure but make it more specific, compelling, and human. Keep hashtags appropriate for {platform}. Max caption length: {"2200" if platform == "instagram" else "500" if platform == "tiktok" else "1500"}."""

    resp = _ai_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip()
    # Extract JSON
    if '{' in text:
        text = text[text.index('{'):text.rindex('}')+1]
    parsed = json.loads(text)
    parsed['content_type'] = base['content_type']
    return parsed


# ── 30-Day Content Calendar ────────────────────────────────────────────────────
_WEEK_SCHEDULE = [
    # (day_of_week, platform, path_rotation_index)
    (0, 'instagram', [0, 1]),   # Monday: buy/sell
    (1, 'tiktok',    [3, 4]),   # Tuesday: loan/wayout
    (2, 'facebook',  [2, 5]),   # Wednesday: lease/commercial
    (3, 'linkedin',  [0, 1]),   # Thursday: buy/sell
    (4, 'instagram', [5, 3]),   # Friday: commercial/loan
    (5, 'tiktok',    [0]),      # Saturday: buy (high engagement)
    (6, 'facebook',  [2]),      # Sunday: lease/lifestyle
]
_PATHS = ['buy', 'sell', 'lease', 'loan', 'wayout', 'commercial']
_POST_TIMES = {
    'instagram': ['9:00 AM', '6:00 PM'],
    'tiktok':    ['7:00 AM', '8:00 PM'],
    'facebook':  ['10:00 AM', '3:00 PM'],
    'linkedin':  ['8:00 AM', '12:00 PM'],
    'youtube':   ['2:00 PM'],
}
_NOTES = {
    'instagram': 'Top engagement: Tue/Wed/Thu. Use Stories + Reels.',
    'tiktok':    'Post 2–3× per week for algorithm boost.',
    'facebook':  'Best for educational content + community building.',
    'linkedin':  'Business hours only. Professional tone.',
    'youtube':   'Premiere at 2 PM for live chat engagement.',
}

def generate_calendar(month=None, year=None):
    now = datetime.now()
    month = month or now.month
    year  = year  or now.year
    _, days_in_month = calendar.monthrange(year, month)

    entries = []
    path_counters = {p: 0 for p in _PATHS}
    yt_count = 0
    platform_counts = {p: 0 for p in PLATFORMS}
    path_counts = {p: 0 for p in _PATHS}

    for day in range(1, days_in_month + 1):
        date = datetime(year, month, day)
        dow  = date.weekday()  # 0=Mon

        # Find schedule entry for this day-of-week
        sched = [s for s in _WEEK_SCHEDULE if s[0] == dow]
        if not sched:
            continue

        platform, path_idxs = sched[0][1], sched[0][2]
        week_num = (day - 1) // 7
        path_key = _PATHS[path_idxs[week_num % len(path_idxs)]]
        tmpl = TEMPLATES.get(path_key, {}).get(platform, {})
        post_time = _POST_TIMES[platform][week_num % len(_POST_TIMES[platform])]

        entries.append({
            'day':          day,
            'date':         date.strftime('%Y-%m-%d'),
            'weekday':      date.strftime('%A'),
            'platform':     platform,
            'path':         path_key,
            'content_type': tmpl.get('type', 'Post'),
            'hook':         tmpl.get('hook', '')[:120],
            'cta':          tmpl.get('cta', ''),
            'posting_time': post_time,
            'notes':        _NOTES[platform],
        })

        platform_counts[platform] = platform_counts.get(platform, 0) + 1
        path_counts[path_key] = path_counts.get(path_key, 0) + 1

        # Add one YouTube video per week (Thursdays)
        if dow == 3 and yt_count < 4:
            yt_tmpl = TEMPLATES.get(path_key, {}).get('youtube', {})
            entries.append({
                'day':          day,
                'date':         date.strftime('%Y-%m-%d'),
                'weekday':      date.strftime('%A'),
                'platform':     'youtube',
                'path':         path_key,
                'content_type': yt_tmpl.get('type', 'Video'),
                'hook':         yt_tmpl.get('hook', '')[:120],
                'cta':          yt_tmpl.get('cta', ''),
                'posting_time': '2:00 PM',
                'notes':        _NOTES['youtube'],
            })
            platform_counts['youtube'] = platform_counts.get('youtube', 0) + 1
            yt_count += 1

    entries.sort(key=lambda e: e['day'])

    return {
        'status':             'success',
        'month':              datetime(year, month, 1).strftime('%B %Y'),
        'total_posts':        len(entries),
        'platform_breakdown': platform_counts,
        'path_breakdown':     path_counts,
        'calendar':           entries,
    }
