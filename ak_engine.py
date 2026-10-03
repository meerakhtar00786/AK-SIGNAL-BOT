"""
AK SIGNAL BOT - PRO engine
EMA 9/21/50/100/200, RSI, MACD, Stochastic, Bollinger, ATR, ADX/DI,
Support/Resistance, candle patterns + quality gates (regime, volatility,
agreement, opposing S/R). Needs only pandas + numpy.
"""
import numpy as np
import pandas as pd


# ---------------------------------------------------------------- indicators
def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def rsi(close, n=14):
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = up / dn.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50)


def atr(df, n=14):
    pc = df["Close"].shift()
    tr = pd.concat([df["High"] - df["Low"],
                    (df["High"] - pc).abs(),
                    (df["Low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def adx_calc(df, n=14):
    up = df["High"].diff()
    dn = -df["Low"].diff()
    plus_dm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=df.index)
    a = atr(df, n).replace(0, np.nan)
    pdi = 100 * plus_dm.ewm(alpha=1 / n, adjust=False).mean() / a
    mdi = 100 * minus_dm.ewm(alpha=1 / n, adjust=False).mean() / a
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    adx = dx.ewm(alpha=1 / n, adjust=False).mean()
    return pdi.fillna(0), mdi.fillna(0), adx.fillna(0)


def add_indicators(df, p=None):
    p = p or {}
    d = df.copy()
    c = d["Close"]
    d["ema9"] = ema(c, p.get("ema_fast", 9))
    d["ema21"] = ema(c, p.get("ema_mid", 21))
    d["ema50"] = ema(c, p.get("ema_slow", 50))
    d["ema100"] = ema(c, 100)
    d["ema200"] = ema(c, 200)
    d["rsi"] = rsi(c, p.get("rsi_len", 14))
    m = ema(c, 12) - ema(c, 26)
    d["macd"], d["macd_sig"] = m, ema(m, 9)
    d["macd_hist"] = d["macd"] - d["macd_sig"]
    lo, hi = d["Low"].rolling(14).min(), d["High"].rolling(14).max()
    d["stoch_k"] = ((c - lo) / (hi - lo).replace(0, np.nan) * 100).fillna(50)
    d["stoch_d"] = d["stoch_k"].rolling(3).mean()
    mid = c.rolling(20).mean()
    sd = c.rolling(20).std()
    d["bb_mid"], d["bb_up"], d["bb_low"] = mid, mid + 2 * sd, mid - 2 * sd
    d["atr"] = atr(d)
    d["atr_ma"] = d["atr"].rolling(50).mean()
    d["pdi"], d["mdi"], d["adx"] = adx_calc(d)
    w = p.get("pivot_w", 3)
    d["piv_h"] = d["High"] == d["High"].rolling(2 * w + 1, center=True).max()
    d["piv_l"] = d["Low"] == d["Low"].rolling(2 * w + 1, center=True).min()
    return d


# ---------------------------------------------------------- support/resistance
def sr_levels(d, t, lookback=150, w=3):
    """Levels known at bar t (only confirmed pivots, no look-ahead)."""
    lo_i = max(0, t - lookback)
    hi_i = t - w
    if hi_i <= lo_i:
        return []
    seg = d.iloc[lo_i:hi_i + 1]
    pts = list(seg.loc[seg["piv_h"], "High"]) + list(seg.loc[seg["piv_l"], "Low"])
    if not pts:
        return []
    tol = max(float(d["atr"].iloc[t]) * 0.6, 1e-12)
    pts.sort()
    groups, cur = [], [pts[0]]
    for x in pts[1:]:
        if x - np.mean(cur) <= tol:
            cur.append(x)
        else:
            groups.append(cur)
            cur = [x]
    groups.append(cur)
    return [(float(np.mean(g)), len(g)) for g in groups]  # (price, touches)


# -------------------------------------------------------------------- scoring
MAX_SCORE = 16  # 2+2+1+1+1+3+2 (original) + 2 (ADX) + 2 (higher trend)


def score_at(d, t, p=None):
    p = p or {}
    r, q = d.iloc[t], d.iloc[t - 1]
    price, a = float(r["Close"]), float(r["atr"])
    votes = []

    def vote(name, v, note):
        votes.append({"name": name, "vote": v, "note": note})

    # EMA trend (2)
    if r.ema9 > r.ema21 > r.ema50:
        vote("EMA trend", 2, "9 > 21 > 50, uptrend")
    elif r.ema9 < r.ema21 < r.ema50:
        vote("EMA trend", -2, "9 < 21 < 50, downtrend")
    elif r.ema9 > r.ema21:
        vote("EMA trend", 1, "Fast EMA above mid EMA")
    elif r.ema9 < r.ema21:
        vote("EMA trend", -1, "Fast EMA below mid EMA")
    else:
        vote("EMA trend", 0, "Flat")

    # Higher trend proxy (2): EMA 100 / 200
    if t < 200:
        vote("Higher trend", 0, "Not enough history yet")
    elif price > r.ema100 > r.ema200:
        vote("Higher trend", 2, "Price > EMA100 > EMA200")
    elif price < r.ema100 < r.ema200:
        vote("Higher trend", -2, "Price < EMA100 < EMA200")
    elif price > r.ema200:
        vote("Higher trend", 1, "Price above EMA200")
    else:
        vote("Higher trend", -1, "Price below EMA200")

    # ADX / DI (2)
    if r.adx >= 25:
        vote("ADX", 2 if r.pdi > r.mdi else -2,
             f"ADX {r.adx:.0f}, strong {'up' if r.pdi > r.mdi else 'down'}trend")
    elif r.adx >= 18:
        vote("ADX", 1 if r.pdi > r.mdi else -1, f"ADX {r.adx:.0f}, building trend")
    else:
        vote("ADX", 0, f"ADX {r.adx:.0f}, ranging market")

    # RSI (2)
    lo_, hi_ = p.get("rsi_low", 30), p.get("rsi_high", 70)
    if r.rsi < lo_:
        vote("RSI", 2, f"{r.rsi:.0f}, oversold")
    elif r.rsi > hi_:
        vote("RSI", -2, f"{r.rsi:.0f}, overbought")
    elif r.rsi < 40 and r.rsi > q.rsi:
        vote("RSI", 1, f"{r.rsi:.0f}, rising from low zone")
    elif r.rsi > 60 and r.rsi < q.rsi:
        vote("RSI", -1, f"{r.rsi:.0f}, falling from high zone")
    else:
        vote("RSI", 0, f"{r.rsi:.0f}, neutral")

    # MACD (1)
    if r.macd_hist > 0 and r.macd_hist > q.macd_hist:
        vote("MACD", 1, "Histogram positive and growing")
    elif r.macd_hist < 0 and r.macd_hist < q.macd_hist:
        vote("MACD", -1, "Histogram negative and falling")
    else:
        vote("MACD", 0, "No clear momentum")

    # Stochastic (1)
    if r.stoch_k < 20 and r.stoch_k > r.stoch_d:
        vote("Stochastic", 1, "Oversold, K crossing up")
    elif r.stoch_k > 80 and r.stoch_k < r.stoch_d:
        vote("Stochastic", -1, "Overbought, K crossing down")
    else:
        vote("Stochastic", 0, f"K {r.stoch_k:.0f}")

    # Bollinger (1)
    if price < r.bb_low:
        vote("Bollinger", 1, "Price below lower band")
    elif price > r.bb_up:
        vote("Bollinger", -1, "Price above upper band")
    else:
        vote("Bollinger", 0, "Inside bands")

    # Support / Resistance (3)
    levels = sr_levels(d, t, p.get("sr_lookback", 150), p.get("pivot_w", 3))
    sup = [x for x in levels if x[0] <= price]
    res = [x for x in levels if x[0] > price]
    ns = max(sup, key=lambda x: x[0]) if sup else None
    nr = min(res, key=lambda x: x[0]) if res else None
    near = a * 0.7
    sr_v, sr_n = 0, "No level nearby"
    if ns and price - ns[0] <= near:
        sr_v, sr_n = (3 if ns[1] >= 2 else 2), f"At support {ns[0]:.5g} ({ns[1]} touches)"
    if nr and nr[0] - price <= near:
        if sr_v == 0 or (nr[0] - price) < (price - ns[0] if ns else 1e9):
            sr_v, sr_n = (-3 if nr[1] >= 2 else -2), f"At resistance {nr[0]:.5g} ({nr[1]} touches)"
    vote("Support/Resistance", sr_v, sr_n)

    # Candle pattern (2)
    body = abs(r.Close - r.Open)
    rng = max(r.High - r.Low, 1e-12)
    lw = min(r.Open, r.Close) - r.Low
    uw = r.High - max(r.Open, r.Close)
    bull_eng = r.Close > r.Open and q.Close < q.Open and r.Close >= q.Open and r.Open <= q.Close
    bear_eng = r.Close < r.Open and q.Close > q.Open and r.Close <= q.Open and r.Open >= q.Close
    if bull_eng:
        vote("Candle", 2, "Bullish engulfing")
    elif bear_eng:
        vote("Candle", -2, "Bearish engulfing")
    elif lw > 2 * body and lw > 0.55 * rng:
        vote("Candle", 1, "Hammer / long lower wick")
    elif uw > 2 * body and uw > 0.55 * rng:
        vote("Candle", -1, "Shooting star / long upper wick")
    else:
        vote("Candle", 0, "No pattern")

    total = sum(v["vote"] for v in votes)
    return {"score": total, "votes": votes, "price": price, "atr": a,
            "support": ns, "resistance": nr, "levels": levels}


def decide(score, threshold=5):
    thr = threshold * MAX_SCORE / 12.0  # slider meaning stays the same
    if score >= thr:
        return "CALL"
    if score <= -thr:
        return "PUT"
    return "WAIT"


# -------------------------------------------------------------- quality gates
REVERSAL = {"RSI", "Stochastic", "Bollinger", "Support/Resistance"}


def signal_at(d, t, p=None, threshold=5):
    res = score_at(d, t, p)
    sig = decide(res["score"], threshold)
    votes = res["votes"]
    if sig != "WAIT":
        dirn = 1 if sig == "CALL" else -1
        r = d.iloc[t]
        agree = sum(1 for v in votes if v["vote"] * dirn > 0)
        oppose = sum(1 for v in votes if v["vote"] * dirn < 0)
        sr_v = next(v["vote"] for v in votes if v["name"] == "Support/Resistance")
        vr = float(r.atr / r.atr_ma) if r.atr_ma and r.atr_ma == r.atr_ma else 1.0
        reason = None
        if vr < 0.6 or vr > 2.5:
            reason = f"volatility out of range (x{vr:.1f} of normal)"
        elif agree < 4:
            reason = f"only {agree} indicators agree"
        elif oppose > 2:
            reason = f"{oppose} indicators point the other way"
        elif sr_v * dirn <= -2:
            reason = "price is at an opposing support/resistance level"
        elif r.adx >= 25 and dirn != (1 if r.pdi > r.mdi else -1):
            reason = "against a strong trend"
        elif r.adx < 18 and not any(v["name"] in REVERSAL and v["vote"] * dirn > 0 for v in votes):
            reason = "ranging market with no reversal trigger"
        if reason:
            sig = "WAIT"
            votes.append({"name": "Quality filter", "vote": 0, "note": "Blocked: " + reason})
        else:
            votes.append({"name": "Quality filter", "vote": 0,
                          "note": f"Passed ({agree} agree, {oppose} oppose)"})
    res["signal"] = sig
    return res


def analyze(df, p=None, threshold=5):
    """Signal for the last fully closed candle."""
    d = add_indicators(df, p)
    t = len(d) - 1
    res = signal_at(d, t, p, threshold)
    res["strength"] = int(min(100, abs(res["score"]) / MAX_SCORE * 100))
    res["time"] = d.index[t]
    res["df"] = d
    return res


# ------------------------------------------------------------------- backtest
def backtest(df, expiry=1, threshold=5, payout=0.85, p=None, max_bars=2500):
    d = add_indicators(df, p).tail(max_bars).reset_index(drop=False)
    start = min(210, max(60, len(d) // 3))
    wins = losses = 0
    for t in range(start, len(d) - expiry):
        sig = signal_at(d, t, p, threshold)["signal"]
        if sig == "WAIT":
            continue
        entry, exit_ = d["Close"].iloc[t], d["Close"].iloc[t + expiry]
        win = (exit_ > entry) if sig == "CALL" else (exit_ < entry)
        wins += int(win)
        losses += int(not win)
    n = wins + losses
    wr = wins / n * 100 if n else 0.0
    be = 100 / (1 + payout)
    return {"trades": n, "wins": wins, "losses": losses, "win_rate": wr,
            "break_even": be, "net_units": wins * payout - losses}
