"""
ShivaLuxury — Phase 2 Outbound Prospect Finder
================================================
Searches Reddit's public JSON API for people asking about
real estate in LA. No API key required.
"""

import requests, time, os
from datetime import datetime, timezone

HEADERS = {
    "User-Agent": "ShivaLuxury-LeadFinder/1.0 (real estate; contact st@shivaluxury.com)"
}

SUBREDDITS = [
    "LosAngeles",
    "realestate",
    "FirstTimeHomeBuyer",
    "Moving",
    "SoCalRealestate",
]

QUERIES = {
    "buying": [
        "buying home Los Angeles",
        "first time buyer LA",
        "afford house LA",
        "mortgage Los Angeles",
        "pre-approval LA",
    ],
    "selling": [
        "selling home Los Angeles",
        "sell my house LA",
        "home value Los Angeles",
    ],
    "renting": [
        "looking for apartment Los Angeles",
        "rent in LA",
        "moving to Los Angeles",
        "rental {area}",
    ],
    "distressed": [
        "foreclosure Los Angeles",
        "behind on mortgage LA",
        "tax lien property California",
    ],
}

LA_KEYWORDS = [
    "los angeles", " la ", "lax", "socal", "so cal",
    "santa monica", "beverly hills", "calabasas", "sherman oaks",
    "studio city", "encino", "tarzana", "woodland hills",
    "burbank", "glendale", "pasadena", "long beach", "torrance",
    "90210", "90024", "90025", "90035", "90049",
]

HIGH_VALUE_KEYWORDS = [
    "afford", "pre-approv", "how much", "can i buy", "first time",
    "agent", "realtor", "help me", "advice", "confused",
    "scared", "overwhelmed", "qualify", "should i",
]


def _relevance(post):
    text = (post.get("title", "") + " " + post.get("text", "")).lower()
    score = 0
    for kw in LA_KEYWORDS:
        if kw in text:
            score += 2
    for kw in HIGH_VALUE_KEYWORDS:
        if kw in text:
            score += 3
    return score


def _fetch(subreddit, query, limit=5):
    """Fetch search results from one subreddit."""
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        "q": query,
        "restrict_sr": 1,
        "sort": "new",
        "limit": limit,
        "t": "month",
    }
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=8)
        if r.status_code == 429:
            print(f"[REDDIT] Rate limited on r/{subreddit} — skipping")
            return [], "rate_limited"
        if r.status_code != 200:
            return [], f"HTTP {r.status_code}"
        children = r.json().get("data", {}).get("children", [])
        return children, ""
    except Exception as e:
        return [], str(e)


def search_prospects(intent=None, subreddits=None, limit=10):
    """
    Search Reddit for real estate prospects in LA.

    Args:
        intent: "buying" | "selling" | "renting" | "distressed" | None (all)
        subreddits: list of subreddit names, or None for default set
        limit: max results to return (capped at 25)

    Returns:
        dict with status, total_found, prospects list, search_summary
    """
    limit = min(int(limit), 25)
    subs  = subreddits or SUBREDDITS
    intents = [intent] if intent and intent in QUERIES else list(QUERIES.keys())

    seen_ids   = set()
    prospects  = []
    errors     = []
    calls_made = 0

    for sub in subs:
        for itnt in intents:
            for query in QUERIES[itnt]:
                time.sleep(0.5)  # be polite to Reddit
                children, err = _fetch(sub, query, limit=5)
                calls_made += 1

                if err:
                    errors.append(f"r/{sub} '{query}': {err}")
                    continue

                for child in children:
                    d = child.get("data", {})
                    pid = d.get("id", "")
                    if not pid or pid in seen_ids:
                        continue
                    author = d.get("author", "")
                    if author in ("[deleted]", "AutoModerator", ""):
                        continue
                    if d.get("score", 0) < 0:
                        continue

                    seen_ids.add(pid)
                    post = {
                        "id":            pid,
                        "author":        f"u/{author}",
                        "title":         d.get("title", ""),
                        "text":          (d.get("selftext", "") or "")[:300].strip(),
                        "url":           f"https://reddit.com{d.get('permalink', '')}",
                        "score":         d.get("score", 0),
                        "subreddit":     d.get("subreddit", sub),
                        "posted_at":     datetime.fromtimestamp(
                                            d.get("created_utc", 0), tz=timezone.utc
                                         ).strftime("%Y-%m-%dT%H:%M:%S"),
                        "relevance_score": _relevance({"title": d.get("title",""),
                                                        "text":  d.get("selftext","")}),
                        "intent_match":  itnt,
                    }
                    prospects.append(post)

    # Sort: highest relevance first, then newest
    prospects.sort(key=lambda p: (-p["relevance_score"], -p["score"]))
    prospects = prospects[:limit]

    return {
        "status":       "success",
        "total_found":  len(prospects),
        "intent":       intent or "all",
        "prospects":    prospects,
        "search_summary": {
            "subreddits_searched": len(subs),
            "queries_run":         calls_made,
            "errors":              errors[:10],  # cap error list
        },
    }
