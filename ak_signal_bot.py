# AK SIGNAL BOT - premium dashboard (run: streamlit run ak_signal_bot.py)
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf

import ak_engine as eng

st.set_page_config(page_title="AK SIGNAL BOT", page_icon="🥇", layout="wide")

PAIRS = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "NZD/USD": "NZDUSD=X",
    "USD/CHF": "CHF=X", "EUR/GBP": "EURGBP=X", "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X", "NZD/CAD": "NZDCAD=X",
    "BTC/USD": "BTC-USD", "ETH/USD": "ETH-USD", "Gold": "GC=F",
}
TF = {"1 min": ("1m", "5d"), "5 min": ("5m", "30d"),
      "15 min": ("15m", "30d"), "1 hour": ("1h", "90d")}
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
.stApp{background:radial-gradient(900px 420px at 80% -8%,#1b2550 0%,transparent 60%),
radial-gradient(700px 400px at 5% 100%,#2a1f0d 0%,transparent 55%),var(--bg);
color:var(--text);font-family:'DM Sans',sans-serif}
#MainMenu,footer,header[data-testid="stHeader"]{visibility:hidden;height:0}
.block-container{padding-top:1.4rem;max-width:1180px}
.top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:18px}
.brand{display:flex;align-items:center;gap:14px}
.brand .name{font:800 27px 'Sora';letter-spacing:.01em;background:linear-gradient(90deg,var(--gold2),var(--gold));
-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.brand .tag{color:var(--mute);font-size:13px}
.live{display:flex;align-items:center;gap:8px;color:var(--mute);font-size:13px;border:1px solid var(--line);
border-radius:99px;padding:7px 14px;background:#0d1326}
.live i{width:8px;height:8px;border-radius:50%;background:var(--up);box-shadow:0 0 10px var(--up)}
.card{background:linear-gradient(180deg,#131a31,#0e1426);border:1px solid var(--line);border-radius:20px;padding:22px 24px;margin-bottom:16px}
.card h4{font:700 16px 'Sora';margin:0 0 4px}
.res{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap;min-height:210px}
.res.CALL{border-color:rgba(39,211,162,.6);box-shadow:0 20px 60px rgba(39,211,162,.14)}
.res.PUT{border-color:rgba(255,92,114,.6);box-shadow:0 20px 60px rgba(255,92,114,.14)}
.word{font:800 68px/1 'Sora';letter-spacing:-.02em}
.CALL .word{color:var(--up)}.PUT .word{color:var(--down)}.WAIT .word,.idle .word{color:var(--mute)}
.meta{color:var(--mute);font-size:14px;line-height:1.75}.meta b{color:var(--text)}
.ring{animation:fill 1.1s ease-out}@keyframes fill{from{stroke-dashoffset:339.3}}
table.votes{width:100%;border-collapse:collapse;font-size:14px}
table.votes td{padding:10px 6px;border-bottom:1px solid var(--line)}
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
@media (max-width:640px){.word{font-size:50px}.brand .name{font-size:21px}.live{display:none}}
</style>"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------- data
@st.cache_data(ttl=45, show_spinner=False)
def load(symbol, interval, period):
    df = yf.download(symbol, interval=interval, period=period, progress=False, auto_adjust=True)
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close"]].dropna()
    if df.index.tz is not None:
        df.index = df.index.tz_convert(TZ)
    return df.iloc[:-1]  # drop the candle that is still forming


def send_telegram(token, chat_id, text):
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                          json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
        return r.ok, r.text
    except Exception as ex:
        return False, str(ex)


def tg_text(broker, pair, tf, expiry, res):
    icon = {"CALL": "🟢 CALL (UP)", "PUT": "🔴 PUT (DOWN)", "WAIT": "⚪ WAIT"}[res["signal"]]
    return (f"🥇 <b>AK SIGNAL BOT</b>\n\n<b>{pair}</b> | {tf} | {broker}\nSignal: <b>{icon}</b>\n"
            f"Strength: {res['strength']}%\nEntry: next candle open\nPrice: {res['price']:.5g}\n"
            f"Expiry: {expiry} candle(s)\n\n<i>Not financial advice. Test on demo first.</i>")


def gauge(pct, color):
    off = 339.3 * (1 - pct / 100)
    return (f'<svg viewBox="0 0 140 140" width="136"><circle cx="70" cy="70" r="54" fill="none" '
            f'stroke="#1b2440" stroke-width="10"/><circle class="ring" cx="70" cy="70" r="54" fill="none" '
            f'stroke="{color}" stroke-width="10" stroke-linecap="round" stroke-dasharray="339.3" '
            f'stroke-dashoffset="{off:.1f}" transform="rotate(-90 70 70)"/>'
            f'<text x="70" y="77" text-anchor="middle" fill="#eef1fb" font-family="Sora" '
            f'font-weight="800" font-size="26">{pct}%</text></svg>')


def votes_html(res):
    rows = ""
    for v in res["votes"]:
        cls = "p-up" if v["vote"] > 0 else "p-dn" if v["vote"] < 0 else "p-no"
        rows += (f"<tr><td><b>{v['name']}</b></td><td class='meta'>{v['note']}</td>"
                 f"<td style='text-align:right'><span class='pill {cls}'>{v['vote']:+d}</span></td></tr>")
    return f"<table class='votes'>{rows}</table>"


def chart(res, pair, tf):
    d = res["df"].tail(90)
    f = go.Figure()
    f.add_trace(go.Candlestick(x=d.index, open=d.Open, high=d.High, low=d.Low, close=d.Close,
                               increasing_line_color="#27d3a2", decreasing_line_color="#ff5c72", name="Price"))
    for col, color in (("ema9", "#f3dd9c"), ("ema21", "#6aa9ff"), ("ema50", "#b78cff")):
        f.add_trace(go.Scatter(x=d.index, y=d[col], line=dict(width=1.3, color=color), name=col.upper()))
    f.add_trace(go.Scatter(x=d.index, y=d.bb_up, line=dict(width=.8, color="#4b5679", dash="dot"), name="BB"))
    f.add_trace(go.Scatter(x=d.index, y=d.bb_low, line=dict(width=.8, color="#4b5679", dash="dot"), showlegend=False))
    for lv, _ in res["levels"]:
        f.add_hline(y=lv, line=dict(color="#27d3a2" if lv <= res["price"] else "#ff5c72", width=1, dash="dash"), opacity=.5)
    f.update_layout(height=470, margin=dict(l=8, r=8, t=34, b=8), xaxis_rangeslider_visible=False,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0e1426", font=dict(color="#c9d1ea"),
                    title=f"{pair}  {tf}", legend=dict(orientation="h", y=1.1),
                    xaxis=dict(gridcolor="#1b2440"), yaxis=dict(gridcolor="#1b2440"))
    return f


# -------------------------------------------------------------------- header
now = pd.Timestamp.now(tz=TZ)
st.markdown(f"""<div class="top"><div class="brand">{LOGO.format(s=54)}
<div><div class="name">AK SIGNAL BOT</div>
<div class="tag">Real-market analysis with 9 indicators and a quality filter</div></div></div>
<div class="live"><i></i>{now:%d %b, %H:%M} Pakistan time</div></div>""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Signal", "Market scanner", "Backtest"])

with st.expander("Settings", expanded=False):
    c1, c2, c3 = st.columns(3)
    thr = c1.slider("Signal strictness", 3, 9, 6, help="Higher means fewer but stronger signals")
    payout = c2.slider("Broker payout %", 70, 95, 85) / 100
    tg_on = c3.toggle("Send signal to Telegram")
    tg_token = st.text_input("Telegram bot token", type="password") if tg_on else ""
    tg_chat = st.text_input("Telegram chat ID") if tg_on else ""

# ---------------------------------------------------------------------- tabs
with tab1:
    left, right = st.columns([1, 1.25], gap="large")
    with left:
        st.markdown("<div class='card'><h4>Create a signal</h4>"
                    "<div class='meta'>Choose your market and press the button.</div></div>", unsafe_allow_html=True)
        broker = st.selectbox("Broker", BROKERS)
        pair = st.selectbox("Trading asset", list(PAIRS))
        tf = st.selectbox("Time frame", list(TF), index=1)
        expiry = st.select_slider("Expiry (candles)", [1, 2, 3, 5], value=1)
        go_btn = st.button("Generate signal")
        st.markdown("<p class='note'>Real market pairs only. Quotex OTC prices are made by Quotex "
                    "and cannot be analysed outside it.</p>", unsafe_allow_html=True)
    interval, period = TF[tf]
    if go_btn:
        with st.spinner("Reading the market..."):
            df = load(PAIRS[pair], interval, period)
        if df.empty or len(df) < 80:
            st.session_state.pop("res", None)
            right.error("No data received. Forex is closed on weekends. Try BTC/USD or ETH/USD.")
        else:
            res = eng.analyze(df, threshold=thr)
            res.update(pair=pair, tf=tf, expiry=expiry, broker=broker)
            st.session_state["res"] = res
            if tg_on and tg_token and tg_chat:
                ok, msg = send_telegram(tg_token, tg_chat, tg_text(broker, pair, tf, expiry, res))
                (right.success("Sent to Telegram") if ok else right.error(f"Telegram error: {msg}"))
    res = st.session_state.get("res")
    with right:
        if res:
            col = {"CALL": "#27d3a2", "PUT": "#ff5c72", "WAIT": "#8d97b5"}[res["signal"]]
            label = {"CALL": "Buy / Up", "PUT": "Sell / Down", "WAIT": "No clear setup, stay out"}[res["signal"]]
            s_, r_ = res["support"], res["resistance"]
            st.markdown(f"""<div class="card res {res['signal']}">
<div><div class="word">{res['signal']}</div><div class="meta">{label}</div>
<div class="meta" style="margin-top:10px"><b>{res['pair']}</b> on <b>{res['tf']}</b> via {res['broker']}<br>
Enter at the <b>next candle open</b>, expiry <b>{res['expiry']} candle(s)</b><br>
Price <b>{res['price']:.5g}</b><br>
Support <b>{f'{s_[0]:.5g}' if s_ else 'none'}</b>, resistance <b>{f'{r_[0]:.5g}' if r_ else 'none'}</b></div></div>
<div style="text-align:center">{gauge(res['strength'], col)}<div class="meta">Signal strength</div></div></div>""",
                        unsafe_allow_html=True)
        else:
            st.markdown("<div class='card res idle'><div><div class='word'>READY</div>"
                        "<div class='meta'>Your signal will appear here.</div></div></div>", unsafe_allow_html=True)
    if res:
        a, b = st.columns([1, 1.5], gap="large")
        with a:
            st.markdown(f"<div class='card'><h4>Indicator votes</h4>{votes_html(res)}</div>", unsafe_allow_html=True)
        with b:
            st.plotly_chart(chart(res, res["pair"], res["tf"]), use_container_width=True)

with tab2:
    st.markdown("<p class='meta'>Scan every asset on the chosen time frame and rank the strongest setups.</p>",
                unsafe_allow_html=True)
    scan_tf = st.selectbox("Scanner time frame", list(TF), index=1, key="scan_tf")
    if st.button("Scan all assets"):
        rows, bar = [], st.progress(0.0)
        for i, (name, sym) in enumerate(PAIRS.items()):
            df = load(sym, *TF[scan_tf])
            if not df.empty and len(df) >= 80:
                r = eng.analyze(df, threshold=thr)
                rows.append({"Asset": name, "Signal": r["signal"], "Strength %": r["strength"],
                             "Score": r["score"], "Price": round(r["price"], 5)})
            bar.progress((i + 1) / len(PAIRS))
        bar.empty()
        if rows:
            st.dataframe(pd.DataFrame(rows).sort_values("Strength %", ascending=False),
                         hide_index=True, use_container_width=True)
        else:
            st.warning("No data. Forex is closed on weekends; try again on a weekday.")

with tab3:
    st.markdown("<p class='meta'>Test the strategy on recent history before trusting it.</p>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3)
    bt_pair = b1.selectbox("Asset", list(PAIRS), key="bt_pair")
    bt_tf = b2.selectbox("Time frame", list(TF), index=1, key="bt_tf")
    bt_exp = b3.select_slider("Expiry (candles)", [1, 2, 3, 5], value=1, key="bt_exp")
    if st.button("Run backtest"):
        with st.spinner("Testing on past candles..."):
            df = load(PAIRS[bt_pair], *TF[bt_tf])
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
