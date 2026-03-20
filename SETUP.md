# ShivaLuxury Lead Engine — Setup Guide

## What Was Fixed
| Bug | Fix |
|-----|-----|
| `oauth2client` deprecated / broken on Render | Replaced with `google-auth` |
| Credentials only loaded from env var | Now tries local JSON files first |
| `index.html` had hardcoded Render URL | Auto-detects local vs deployed |
| `monthly_income`, `monthly_debts`, `timeline` ignored | All mapped in `/audit` |
| No DTI calculation | Added front/back DTI with qualify logic |
| Tax API crash on empty response | Hardened with try/catch + default |
| No conversation scripts | Full scripts endpoint + inline display |

---

## Run Locally

```bash
# 1. Install
pip install -r requirements.txt

# 2. Make sure your JSON file is in the same folder:
#    shiva-lead-gen-76897a1dbdb5.json  ← this is your working file

# 3. Run
python app.py

# 4. Open browser
open http://localhost:5001
```

---

## Google Sheets — Check These

1. **Sheet must be named exactly:** `Unlock Your 2026 Buying Power`
2. **Worksheet/tab must be named:** `Leads2026`
3. **Share the sheet with:** `shiva-leads@shiva-lead-gen.iam.gserviceaccount.com`
   - Open the sheet → Share → paste that email → Editor role

**Verify at:** http://localhost:5001/health

---

## Deploy to Render

1. Push files to GitHub
2. New Web Service on render.com → connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `python app.py`
5. Add Environment Variable:
   - Key: `GOOGLE_CREDENTIALS`
   - Value: paste the **entire contents** of `shiva-lead-gen-76897a1dbdb5.json`

---

## New Columns in Google Sheets (21 total)

A: Name · B: Phone · C: Email · D: ZIP · E: Loan Amount
F: Total PITI · G: P&I · H: Monthly Tax · I: Tax Rate
J: Credit · K: Timeline · L: Loan Type · M: Monthly Income
N: Monthly Debts · O: Front DTI · P: Back DTI · Q: Qualifies?
R: Priority · S: Segment · T: Refi Flag · U: Timestamp

**Row Colors:**
- 🟡 Gold = Luxury leads ($750K+)
- 🔴 Pink = HOT leads (excellent credit + immediate timeline)

---

## Phase 2 Roadmap (When Ready)

- [ ] TitlePro247 data extraction for refinance candidates
- [ ] Competitor SEO keyword scraper
- [ ] Blog article generator (semantic/niche keywords)
- [ ] Social media content scheduler
- [ ] New buyer/seller finder bot
- [ ] Google My Business integration
