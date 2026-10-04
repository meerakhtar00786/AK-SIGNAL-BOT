"""AK SIGNAL BOT - order flow, financial (macro) and narrative (news) pillars.
Every score is between -1 (sell pressure) and +1 (buy pressure)."""
import re
import numpy as np
import pandas as pd

BULL = (r"\bsurg", r"\brall", r"\bgain", r"\bjump", r"\bris(e|es|ing)\b", r"\bsoar", r"record high",
        r"bullish", r"\bupgrad", r"\bbeat", r"\bstrong", r"\bapprov", r"inflow", r"\badopt", r"\bclimb")
BEAR = (r"\bfall", r"\bdrop", r"\bplung", r"\bslump", r"\bcrash", r"bearish", r"\bdowngrad",
        r"\bmiss(es|ed)?\b", r"\bweak", r"\bban(s|ned)?\b", r"lawsuit", r"\bhack", r"outflow",
        r"\bfear", r"sell-?off", r"\btumbl")

DRIVERS = {"DXY": "DX-Y.NYB", "US10Y": "^TNX", "STOCKS": "^GSPC"}
SCALE = {"DXY": 0.0015, "US10Y": 0.01, "STOCKS": 0.004}  # 1 hour move that counts as "full"
IMPACT = {  # +1 moves with the driver, -1 moves against it
    "EUR/USD": {"DXY": -1}, "GBP/USD": {"DXY": -1},
    "AUD/USD": {"DXY": -1, "STOCKS": 1}, "NZD/USD": {"DXY": -1, "STOCKS": 1},
    "USD/JPY": {"DXY": 1, "US10Y": 1}, "USD/CAD": {"DXY": 1}, "USD/CHF": {"DXY": 1},
    "EUR/GBP": {}, "EUR/JPY": {"STOCKS": 1}, "GBP/JPY": {"STOCKS": 1}, "NZD/CAD": {"STOCKS": 1},
    "BTC/USD": {"STOCKS": 1, "DXY": -1}, "ETH/USD": {"STOCKS": 1, "DXY": -1},
    "Gold": {"DXY": -1, "US10Y": -1},
}


def _clip(x):
    return max(-1.0, min(1.0, float(x)))


def flow_score(df, n=10):
    """Close-location flow (volume weighted when the feed has volume)."""
    d = df.tail(60)
    rng = (d["High"] - d["Low"]).replace(0, np.nan)
    clv = (((d["Close"] - d["Low"]) - (d["High"] - d["Close"])) / rng).fillna(0)
    has_vol = "Volume" in d.columns and float(d["Volume"].sum()) > 0
    vol = d["Volume"] if has_vol else pd.Series(1.0, index=d.index)
    flow = (clv * vol).rolling(n).sum() / vol.rolling(n).sum()
    f = float(flow.iloc[-1]) if flow.notna().iloc[-1] else 0.0
    sc = _clip(f * 1.5)
    side = "Buyers" if sc > 0.1 else "Sellers" if sc < -0.1 else "Neither side"
    note = f"{side} in control over the last {n} candles" + (" (volume weighted)" if has_vol else " (price-pressure proxy)")
    return sc, note


def macro_score(pair, drivers):
    """drivers: {name: DataFrame with Close}. Looks at the last hour of 5-minute data."""
    parts, notes = [], []
    for name, sign in IMPACT.get(pair, {}).items():
        df = drivers.get(name)
        if df is None or len(df) < 14:
            continue
        c = df["Close"]
        pct = float(c.iloc[-1] / c.iloc[-13] - 1)
        parts.append(sign * _clip(pct / SCALE[name]))
        notes.append(f"{name} {pct * 100:+.2f}%")
    if not parts:
        return 0.0, "No macro driver for this pair"
    return _clip(np.mean(parts)), "1 hour: " + ", ".join(notes)


def parse_news(raw):
    titles = []
    for n in raw or []:
        if not isinstance(n, dict):
            continue
        body = n.get("content") if isinstance(n.get("content"), dict) else n
        t = body.get("title")
        if t:
            titles.append(str(t))
    return titles[:8]


def news_score(titles):
    if not titles:
        return 0.0, "No recent headlines found"
    s = 0
    for t in titles:
        low = t.lower()
        s += sum(bool(re.search(w, low)) for w in BULL)
        s -= sum(bool(re.search(w, low)) for w in BEAR)
    return _clip(s / max(3, len(titles))), f"{len(titles)} headlines scanned"


def combine(tech_norm, gate, flow, macro, news):
    """Technical 60%, flow 20%, macro 10%, news 10%."""
    t = _clip(tech_norm * 2)
    ctx = 0.20 * flow + 0.10 * macro + 0.10 * news
    comp = 0.60 * t + ctx
    if comp == 0:
        comp = tech_norm if tech_norm else (flow or 1e-6)
    sgn = 1 if comp > 0 else -1
    agree = gate != "WAIT" and ((gate == "CALL") == (comp > 0))
    veto = ctx * sgn < -0.12
    return {"direction": "CALL" if comp > 0 else "PUT",
            "strength": int(min(100, abs(comp) * 130)),
            "conf": "HIGH" if agree and not veto else "LOW",
            "comp": comp, "veto": veto}
