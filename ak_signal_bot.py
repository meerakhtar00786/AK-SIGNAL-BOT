# AK SIGNAL BOT - premium dashboard (run: streamlit run ak_signal_bot.py)
import time
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf

import ak_engine as eng

st.set_page_config(page_title="AK SIGNAL BOT", page_icon="🥇", layout="centered")

PAIRS = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "NZD/USD": "NZDUSD=X",
    "USD/CHF": "CHF=X", "EUR/GBP": "EURGBP=X", "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X", "NZD/CAD": "NZDCAD=X",
    "BTC/USD": "BTC-USD", "ETH/USD": "ETH-USD", "Gold": "GC=F",
}
TF = {"1 min": ("1m", "5d", 60), "5 min": ("5m", "30d", 300), "15 min": ("15m", "30d", 900)}
BROKERS = ["Quotex", "IQ Option", "Pocket Option", "Binomo"]
TZ = "Asia/Karachi"

LOGO = ('<svg viewBox="0 0 64 64" width="{s}" height="{s}" xmlns="http://www.w3.org/2000/svg">'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#f6e3a4"/><stop offset=".55" stop-color="#d8b45a"/>'
        '<stop offset="1" stop-color="#9b7a2c"/></linearGradient></defs>'
        '<path d="M32 3 57 17.5v29L32 61 7 46.5v-29z" fill="#0d1326" stroke="url(#g)" stroke-width="3"/>'
        '<g fill="url(#g)"><rect x="17" y="38" width="7" height="10" rx="1.5"/>'
        '<rect x="28.5" y="31" width="7" height="17" rx="1.5"/>'
        '<rect x="40" y="23" width="7" height="25" rx="1.5"/></g>'
        '<path d="M15 34 27 26l8 4 12-13M41 17h6v6" fill="none" stroke="#fff" '
        'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;700;800&family=DM+Sans:wght@400;500;700&display=swap');
:root{--bg:#080c18;--line:#222b47;--gold:#d8b45a;--gold2:#f3dd9c;--up:#27d3a2;--down:#ff5c72;--mute:#8d97b5;--text:#eef1fb}
.stApp{background:radial-gradient(800px 420px at 85% -8%,#1b2550 0%,transparent 60%),
radial-gradient(700px 400px at 0% 100%,#2a1f0d 0%,transparent 55%),var(--bg);
color:var(--text);font-family:'DM Sans',sans-serif}
#MainMenu,footer,header[data-testid="stHeader"]{visibility:hidden;height:0}
.block-container{padding-top:1.2rem;max-width:760px}
.top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px}
.brand{display:flex;align-items:center;gap:14px}
.brand .name{font:800 26px 'Sora';background:linear-gradient(90deg,var(--gold2),var(--gold));
-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.brand .tag{color:var(--mute);font-size:13px}
.live{display:flex;align-items:center;gap:8px;color:var(--mute);font-size:13px;border:1px solid var(--line);
border-radius:99px;padding:7px 14px;background:#0d1326;white-space:nowrap}
.live i{width:8px;height:8px;border-radius:50%;background:var(--up);box-shadow:0 0 10px var(--up)}
.meta{color:var(--mute);font-size:14px;line-height:1.7}.meta b{color:var(--text)}
.stage{display:flex;justify-content:center;padding:18px 0 8px}
.orb{position:relative;width:300px;height:300px;border-radius:50%;box-shadow:0 0 90px var(--g)}
.orb .spin{position:absolute;inset:0;border-radius:50%;background:conic-gradient(var(--c),transparent 45%,var(--c));animation:spin 1.5s linear infinite}
.orb .slow{animation-duration:10s}
.orb svg.prog{position:absolute;inset:0;width:100%;height:100%;transform:rotate(-90deg)}
.orb svg.prog circle.fg{animation-name:drain;animation-timing-function:linear;animation-fill-mode:forwards}
.orb .in{position:absolute;inset:12px;border-radius:50%;background:radial-gradient(circle at 50% 30%,#1a2446,#090f1f);
display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 22px}
.orb .arr{font-size:36px;line-height:1;color:var(--c)}
.orb .w{font:800 58px/1.05 'Sora';color:var(--c)}
.orb .t{font:700 28px 'Sora';color:var(--text)}
.orb .s{font-size:13px;color:var(--mute);line-height:1.4;margin-top:3px}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes drain{from{stroke-dashoffset:0}to{stroke-dashoffset:904.8}}
.stats{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0 10px}
.stat{flex:1 1 140px;background:linear-gradient(180deg,#131a31,#0e1426);border:1px solid var(--line);border-radius:16px;padding:14px 16px;text-align:center}
.stat b{display:block;font:800 24px 'Sora'}.stat span{color:var(--mute);font-size:12.5px}
.good{color:var(--up)}.bad{color:var(--down)}
.card{background:linear-gradient(180deg,#131a31,#0e1426);border:1px solid var(--line);border-radius:18px;padding:16px 18px}
table.votes{width:100%;border-collapse:collapse;font-size:14px}
table.votes td{padding:9px 6px;border-bottom:1px solid var(--line)}
table.votes tr:last-child td{border-bottom:none}
.pill{display:inline-block;min-width:42px;text-align:center;padding:3px 10px;border-radius:99px;font-weight:700;font-size:13px}
.p-up{background:rgba(39,211,162,.15);color:var(--up)}.p-dn{background:rgba(255,92,114,.15);color:var(--down)}.p-no{background:#1b2440;color:var(--mute)}
div.stButton>button{background:linear-gradient(135deg,var(--gold2),var(--gold) 60%,#a98430);color:#1a1405;
font:700 17px 'Sora';border:0;border-radius:14px;padding:15px 22px;width:100%;box-shadow:0 12px 32px rgba(216,180,90,.28)}
div.stButton>button:hover{filter:brightness(1.08);color:#1a1405}
div[data-baseweb="select"]>div{background:#0c1224;border:1px solid var(--line);border-radius:12px}
label p{color:var(--mute)!important;font-size:13px!important}
button[data-baseweb="tab"]{font:700 15px 'Sora';color:var(--mute)}
button[data-baseweb="tab"][aria-selected="true"]{color:var(--gold2)}
div[data-baseweb="tab-highlight"]{background:var(--gold)}
.note{color:var(--mute);font-size:12.5px;line-height:1.6}
.badge{display:inline-block;padding:3px 11px;border-radius:99px;font-size:12.5px;font-weight:700}
.b-live{background:rgba(39,211,162,.15);color:var(--up)}.b-off{background:rgba(255,92,114,.15);color:var(--down)}
table.cn{width:100%;border-collapse:collapse;font-size:13.5px;text-align:right}
table.cn th{color:var(--mute);font-weight:500;padding:8px 6px;text-align:right;border-bottom:1px solid var(--line)}
table.cn th:first-child,table.cn td:first-child{text-align:left}
table.cn td{padding:8px 6px;border-bottom:1px solid #1a2240;font-variant-numeric:tabular-nums}
table.cn tr:last-child td{border-bottom:none}
@media (max-width:640px){.orb{width:262px;height:262px}.orb .w{font-size:48px}.brand .name{font-size:21px}.live{display:none}}
</style>"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------- data
@st.cache_data(ttl=45, show_spinner=False)
def load_raw(symbol, interval, period):
    df = yf.download(symbol, interval=interval, period=period, progress=False, auto_adjust=True)
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close"]].dropna()
    if df.index.tz is not None:
        df.index = df.index.tz_convert(TZ)
    return df


def load(symbol, tfname):
    """Only fully closed candles."""
    interval, period, sec = TF[tfname]
    df = load_raw(symbol, interval, period)
    if df.empty:
        return df
    if df.index.tz is None:
        return df.iloc[:-1]
    return df[df.index <= pd.Timestamp.now(tz=TZ) - pd.Timedelta(seconds=sec)]


def send_telegram(token, chat_id, text):
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                          json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
        return r.ok
    except Exception:
        return False


DISP = {"CALL": "BUY", "PUT": "SELL", "WAIT": "WAIT"}


def tg_text(job):
    res = job["res"]
    icon = {"CALL": "🟢 BUY (CALL)", "PUT": "🔴 SELL (PUT)", "WAIT": "⚪ WAIT"}[res["signal"]]
    return (f"🥇 <b>AK SIGNAL BOT</b>\n\n<b>{job['pair']}</b> | {job['tf']} | {job['broker']}\n"
            f"Signal: <b>{icon}</b>\nStrength: {res['strength']}%\nExpiry: {job['tf']}\n\n"
            f"<i>Not financial advice. Test on demo first.</i>")


def mmss(sec):
    sec = max(0, int(sec + 0.999))
    return f"{sec // 60:02d}:{sec % 60:02d}"


# ---------------------------------------------------------------- orb states
def orb_idle():
    return ('<div class="stage"><div class="orb" style="--c:#d8b45a;--g:rgba(216,180,90,.22)">'
            '<div class="spin slow"></div><div class="in"><div class="arr">◆</div>'
            '<div class="w" style="font-size:42px">READY</div>'
            '<div class="s">Choose your market and press<br>Generate signal</div></div></div></div>')


def orb_wait(left_s, boundary):
    at = pd.Timestamp(boundary, unit="s", tz="UTC").tz_convert(TZ)
    return ('<div class="stage"><div class="orb" style="--c:#d8b45a;--g:rgba(216,180,90,.32)">'
            '<div class="spin"></div><div class="in"><div class="t" style="font-size:44px">'
            f'{mmss(left_s)}</div><div class="w" style="font-size:22px">Analyzing</div>'
            f'<div class="s">Fresh signal at candle close<br>{at:%H:%M:%S}</div></div></div></div>')


def orb_signal(job, left_s):
    res = job["res"]
    c, g, arr, word, sub = {
        "CALL": ("#27d3a2", "rgba(39,211,162,.40)", "▲", "BUY", "Buy now (CALL)"),
        "PUT": ("#ff5c72", "rgba(255,92,114,.40)", "▼", "SELL", "Sell now (PUT)"),
        "WAIT": ("#8d97b5", "rgba(141,151,181,.25)", "●", "WAIT", "No clear setup, skip"),
    }[res["signal"]]
    total = max(job["end_at"] - job["start_sig"], 1)
    if "off" not in job:
        job["off"] = max(0.0, total - left_s)
    off = job["off"]
    ring = ('<svg class="prog" viewBox="0 0 300 300"><circle cx="150" cy="150" r="144" fill="none" '
            'stroke="#1b2440" stroke-width="8"/><circle class="fg" cx="150" cy="150" r="144" fill="none" '
            f'stroke="{c}" stroke-width="8" stroke-linecap="round" stroke-dasharray="904.8" '
            f'style="animation-duration:{total:.0f}s;animation-delay:-{off:.1f}s"/></svg>')
    return (f'<div class="stage"><div class="orb" style="--c:{c};--g:{g}">{ring}<div class="in">'
            f'<div class="arr">{arr}</div><div class="w">{word}</div><div class="s">{sub}</div>'
            f'<div class="t" style="margin-top:8px">{mmss(left_s)}</div><div class="s">until expiry</div>'
            '</div></div></div>')


def stats_html(job):
    res, bt = job["res"], job["bt"]
    if bt["trades"] >= 20:
        cls = "good" if bt["win_rate"] > bt["break_even"] else "bad"
        acc = f'<b class="{cls}">{bt["win_rate"]:.0f}%</b><span>Recent accuracy ({bt["trades"]} past trades)</span>'
    else:
        acc = '<b>n/a</b><span>Recent accuracy (too few trades)</span>'
    s_, r_ = res["support"], res["resistance"]
    return ('<div class="stats">'
            f'<div class="stat"><b>{res["strength"]}%</b><span>Signal strength</span></div>'
            f'<div class="stat">{acc}</div>'
            f'<div class="stat"><b>{job["tf"]}</b><span>Expiry</span></div></div>'
            f'<p class="meta">Price <b>{res["price"]:.5g}</b>. Support <b>{f"{s_[0]:.5g}" if s_ else "none"}</b>, '
            f'resistance <b>{f"{r_[0]:.5g}" if r_ else "none"}</b>. Break-even needs <b>{bt["break_even"]:.0f}%</b>.</p>')


def votes_html(res):
    rows = ""
    for v in res["votes"]:
        cls = "p-up" if v["vote"] > 0 else "p-dn" if v["vote"] < 0 else "p-no"
        rows += (f"<tr><td><b>{v['name']}</b></td><td class='meta'>{v['note']}</td>"
                 f"<td style='text-align:right'><span class='pill {cls}'>{v['vote']:+d}</span></td></tr>")
    return f"<div class='card'><table class='votes'>{rows}</table></div>"


def chart(d, pair, tf, levels=()):
    d = d.tail(70)
    f = go.Figure()
    f.add_trace(go.Candlestick(x=d.index, open=d.Open, high=d.High, low=d.Low, close=d.Close,
                               increasing_line_color="#27d3a2", decreasing_line_color="#ff5c72", name="Price"))
    for col, color in (("ema9", "#f3dd9c"), ("ema21", "#6aa9ff"), ("ema50", "#b78cff")):
        f.add_trace(go.Scatter(x=d.index, y=d[col], line=dict(width=1.3, color=color), name=col.upper()))
    last = float(d["Close"].iloc[-1])
    for lv in levels:
        f.add_hline(y=lv, line=dict(color="#27d3a2" if lv <= last else "#ff5c72", width=1, dash="dash"), opacity=.5)
    f.update_layout(height=420, margin=dict(l=8, r=8, t=34, b=8), xaxis_rangeslider_visible=False,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0e1426", font=dict(color="#c9d1ea"),
                    title=f"{pair}  {tf}", legend=dict(orientation="h", y=1.1),
                    xaxis=dict(gridcolor="#1b2440"), yaxis=dict(gridcolor="#1b2440"))
    return f


def data_age(df):
    if df.empty or df.index.tz is None:
        return 0.0
    return (pd.Timestamp.now(tz=TZ) - df.index[-1]).total_seconds()


def is_live(df, sec):
    return (not df.empty) and data_age(df) <= max(4 * sec, 600)


def closed_msg(pair, df):
    last = f"{df.index[-1]:%d %b %H:%M} PKT" if not df.empty else "none"
    return (f"{pair} market looks closed or delayed (last candle: {last}). Forex is closed on weekends. "
            "Try BTC/USD or ETH/USD, they trade 24/7.")


def candles_html(df, n=12):
    d = df.tail(n).iloc[::-1]
    dec = 5 if float(d["Close"].iloc[0]) < 50 else 2
    rows = ""
    for t, r in d.iterrows():
        mv = '<span class="good">▲ Up</span>' if r.Close >= r.Open else '<span class="bad">▼ Down</span>'
        rows += (f"<tr><td>{t:%d %b %H:%M}</td><td>{r.Open:.{dec}f}</td><td>{r.High:.{dec}f}</td>"
                 f"<td>{r.Low:.{dec}f}</td><td>{r.Close:.{dec}f}</td><td>{mv}</td></tr>")
    return ("<div class='card'><table class='cn'><tr><th>Candle (PKT)</th><th>Open</th><th>High</th>"
            f"<th>Low</th><th>Close</th><th>Move</th></tr>{rows}</table></div>")


def why_html(job):
    res = job["res"]
    if res["signal"] != "WAIT":
        return ""
    last = res["votes"][-1]
    if last["name"] == "Quality filter" and last["note"].startswith("Blocked"):
        why = last["note"].replace("Blocked: ", "")
    else:
        why = f"indicators do not agree enough (score {res['score']:+d})"
    lean = "BUY" if res["score"] > 0 else "SELL" if res["score"] < 0 else None
    tip = f" Weak lean: {lean}, but skip it." if lean else ""
    return (f"<div class='card meta'><b>Why WAIT:</b> {why}.{tip} "
            "Lower the strictness in Settings to get more (weaker) signals.</div>")


def market_panel(pair_name, tfname, res=None):
    df = load(PAIRS[pair_name], tfname)
    sec = TF[tfname][2]
    if df.empty or len(df) < 3:
        st.warning("No market data right now.")
        return
    last, prev = df.iloc[-1], df.iloc[-2]
    chg = (last.Close - prev.Close) / prev.Close * 100
    live = is_live(df, sec)
    badge = ('<span class="badge b-live">Live</span>' if live
             else '<span class="badge b-off">Market closed or delayed</span>')
    dec = 5 if last.Close < 50 else 2
    st.markdown(f"<p class='meta'><b>{pair_name}</b> on {tfname} {badge}<br>Last closed price "
                f"<b>{last.Close:.{dec}f}</b> ({chg:+.3f}%). Last candle <b>{df.index[-1]:%d %b %H:%M}</b> PKT. "
                "Compare these candles with your Quotex chart.</p>", unsafe_allow_html=True)
    d = eng.add_indicators(df.tail(300))
    levels = [lv for lv, _ in res["levels"]] if res else []
    st.plotly_chart(chart(d, pair_name, tfname, levels), use_container_width=True)
    st.markdown(candles_html(df), unsafe_allow_html=True)
    st.markdown("<p class='note'>Candles come from the real market feed, so they can differ slightly from "
                "your broker. Quotex OTC pairs use Quotex's own prices and will not match.</p>",
                unsafe_allow_html=True)


# -------------------------------------------------------------------- header
now_ts = pd.Timestamp.now(tz=TZ)
st.markdown(f"""<div class="top"><div class="brand">{LOGO.format(s=52)}
<div><div class="name">AK SIGNAL BOT</div>
<div class="tag">Real-market analysis, 9 indicators, quality filter</div></div></div>
<div class="live"><i></i>{now_ts:%d %b, %H:%M} PKT</div></div>""", unsafe_allow_html=True)

with st.expander("Settings", expanded=False):
    s1, s2, s3 = st.columns(3)
    thr = s1.slider("Signal strictness", 3, 9, 5, help="Higher means fewer but stronger signals")
    payout = s2.slider("Broker payout %", 70, 95, 85) / 100
    tg_on = s3.toggle("Send signal to Telegram")
    tg_token = st.text_input("Telegram bot token", type="password") if tg_on else ""
    tg_chat = st.text_input("Telegram chat ID") if tg_on else ""

c1, c2, c3 = st.columns(3)
broker = c1.selectbox("Broker", BROKERS)
pair = c2.selectbox("Trading asset", list(PAIRS))
tfname = c3.selectbox("Time frame", list(TF))
go_btn = st.button("Generate signal")

if go_btn:
    sec = TF[tfname][2]
    dfc = load(PAIRS[pair], tfname)
    if not is_live(dfc, sec):
        st.session_state.pop("job", None)
        st.session_state["err"] = closed_msg(pair, dfc)
    else:
        boundary = (int(time.time() // sec) + 1) * sec  # next candle open
        st.session_state["job"] = dict(
            phase="wait", pair=pair, tf=tfname, broker=broker, thr=thr, payout=payout,
            tg=(tg_token, tg_chat) if tg_on and tg_token and tg_chat else None,
            boundary=boundary, reveal_at=boundary + 2, end_at=boundary + sec)
        st.session_state.pop("err", None)

job0 = st.session_state.get("job")
active = bool(job0) and job0["phase"] in ("wait", "signal")


@st.fragment(run_every=1 if active else None)
def orb_panel():
    job = st.session_state.get("job")
    now = time.time()
    if not job:
        st.markdown(orb_idle(), unsafe_allow_html=True)
        return
    if job["phase"] == "wait":
        if now > job["end_at"]:
            st.session_state.pop("job")
            st.rerun()
        if now < job["reveal_at"]:
            st.markdown(orb_wait(job["reveal_at"] - now, job["boundary"]), unsafe_allow_html=True)
            return
        with st.spinner("Reading the closed candle..."):
            load_raw.clear()
            df = load(PAIRS[job["pair"]], job["tf"])
            if len(df) < 80 or not is_live(df, TF[job["tf"]][2]):
                st.session_state.pop("job")
                st.session_state["err"] = closed_msg(job["pair"], df)
                st.rerun()
            res = eng.analyze(df, threshold=job["thr"])
            bt = eng.backtest(df, expiry=1, threshold=job["thr"], payout=job["payout"], max_bars=900)
        job.update(res=res, bt=bt, phase="signal", start_sig=time.time())
        if res["signal"] == "WAIT":
            job["end_at"] = time.time() + 25
        if job["tg"]:
            send_telegram(job["tg"][0], job["tg"][1], tg_text(job))
        st.rerun()
    if job["phase"] == "signal":
        left = job["end_at"] - now
        if left > 0:
            st.markdown(orb_signal(job, left), unsafe_allow_html=True)
            return
        st.session_state.pop("job")
        st.rerun()


orb_panel()

if st.session_state.get("err"):
    st.error(st.session_state["err"])

job = st.session_state.get("job")
sig_job = job if job and job["phase"] == "signal" else None
if sig_job:
    st.markdown(stats_html(sig_job), unsafe_allow_html=True)
    st.markdown(why_html(sig_job), unsafe_allow_html=True)
    with st.expander("Indicator votes"):
        st.markdown(votes_html(sig_job["res"]), unsafe_allow_html=True)
else:
    st.markdown("<p class='note'>The signal appears when the current candle closes, stays until its "
                "expiry, then disappears by itself.</p>", unsafe_allow_html=True)

st.markdown("<h3 style='font-family:Sora;margin-top:18px'>Live market data</h3>", unsafe_allow_html=True)
mp_pair, mp_tf = (job["pair"], job["tf"]) if job else (pair, tfname)
market_panel(mp_pair, mp_tf, sig_job["res"] if sig_job else None)

with st.expander("Backtest"):
    b1, b2, b3 = st.columns(3)
    bt_pair = b1.selectbox("Asset", l
bt_pair = b1.selectbox("Asset", list(PAIRS), key="bt_pair")
    bt_tf = b2.selectbox("Time frame", list(TF), key="bt_tf")
    bt_exp = b3.select_slider("Expiry (candles)", [1, 2, 3, 5], value=1, key="bt_exp")
    if st.button("Run backtest"):
        with st.spinner("Testing on past candles..."):
            df = load(PAIRS[bt_pair], bt_tf)
            if df.empty or len(df) < 120:
                st.error("Not enough data for a backtest.")
            else:
                bt = eng.backtest(df, expiry=bt_exp, threshold=thr, payout=payout)
                m1, m2, m3 = st.columns(3)
                m1.metric("Trades", bt["trades"])
                m2.metric("Win rate", f"{bt['win_rate']:.1f}%")
                m3.metric("Break-even needed", f"{bt['break_even']:.1f}%")
                if bt["trades"] < 30:
                    st.warning("Too few trades to trust. Lower the strictness or try another asset.")
                elif bt["win_rate"] > bt["break_even"] + 3:
                    st.success(f"Above break-even on this sample (net {bt['net_units']:+.1f} stakes). "
                               "Past results do not guarantee the future. Test on demo.")
                else:
                    st.error(f"Not profitable on this sample (net {bt['net_units']:+.1f} stakes). "
                             "Do not trade this setting with real money.")

st.markdown("<p class='note'>Signals are indicator calculations, not predictions or financial advice. "
            "Binary options carry a high risk of losing your stake. Use a demo account first.</p>",
            unsafe_allow_html=True)
