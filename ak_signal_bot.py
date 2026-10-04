# AK SIGNAL BOT - main app (run: streamlit run ak_signal_bot.py)
import time
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf

import ak_engine as eng
import ak_context as cx
import ak_theme as th

st.set_page_config(page_title="AK SIGNAL BOT", page_icon="🤖", layout="centered")
st.markdown(th.CSS, unsafe_allow_html=True)

TZ = th.TZ
PAIRS = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "NZD/USD": "NZDUSD=X",
    "USD/CHF": "CHF=X", "EUR/GBP": "EURGBP=X", "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X", "NZD/CAD": "NZDCAD=X",
    "BTC/USD": "BTC-USD", "ETH/USD": "ETH-USD", "Gold": "GC=F",
}
TF = {"1 min": ("1m", "5d", 60), "5 min": ("5m", "30d", 300), "15 min": ("15m", "30d", 900)}
BROKERS = ["Quotex", "IQ Option", "Pocket Option", "Binomo"]


# ---------------------------------------------------------------------- data
def _clean(df):
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


@st.cache_data(ttl=45, show_spinner=False)
def load_raw(symbol, interval, period):
    df = _clean(yf.download(symbol, interval=interval, period=period, progress=False, auto_adjust=True))
    if df.empty:
        return df
    df = df[[c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]].dropna()
    if df.index.tz is not None:
        df.index = df.index.tz_convert(TZ)
    return df


@st.cache_data(ttl=300, show_spinner=False)
def load_ctx(symbol):
    df = _clean(yf.download(symbol, interval="5m", period="5d", progress=False, auto_adjust=True))
    return df[["Close"]].dropna() if not df.empty else pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def load_news(symbol):
    try:
        return cx.parse_news(yf.Ticker(symbol).news)
    except Exception:
        return []


def load(symbol, tfname):
    """Only fully closed candles."""
    interval, period, sec = TF[tfname]
    df = load_raw(symbol, interval, period)
    if df.empty:
        return df
    if df.index.tz is None:
        return df.iloc[:-1]
    return df[df.index <= pd.Timestamp.now(tz=TZ) - pd.Timedelta(seconds=sec)]


def is_live(df, sec):
    if df.empty:
        return False
    if df.index.tz is None:
        return True
    return (pd.Timestamp.now(tz=TZ) - df.index[-1]).total_seconds() <= max(4 * sec, 600)


def closed_msg(pair, df):
    last = f"{df.index[-1]:%d %b %H:%M} PKT" if not df.empty else "none"
    return (f"{pair} market looks closed or delayed (last candle: {last}). Forex is closed on weekends. "
            "Try BTC/USD or ETH/USD, they trade 24/7.")


def send_telegram(token, chat_id, text):
    try:
        return requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                             json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10).ok
    except Exception:
        return False


def tg_text(job):
    up = job["final"]["direction"] == "CALL"
    conf = "HIGH confidence" if job["final"]["conf"] == "HIGH" else "LOW confidence, skip"
    return (f"🤖 <b>AK SIGNAL BOT</b>\n\n<b>{job['pair']}</b> | {job['tf']} | {job['broker']}\n"
            f"Signal: <b>{'📈 BUY (CALL)' if up else '📉 SELL (PUT)'}</b>\n{conf}\n"
            f"Strength: {job['final']['strength']}%\nExpiry: {job['tf']}\n\n"
            "<i>Not financial advice. Test on demo first.</i>")


# ----------------------------------------------------------------- analysis
def build(job, df):
    res = eng.analyze(df, threshold=job["thr"])
    bt = eng.backtest(df, expiry=1, threshold=job["thr"], payout=job["payout"], max_bars=900)
    f_sc, f_note = cx.flow_score(df)
    drivers = {n: load_ctx(cx.DRIVERS[n]) for n in cx.IMPACT.get(job["pair"], {})}
    m_sc, m_note = cx.macro_score(job["pair"], drivers)
    titles = load_news(PAIRS[job["pair"]])
    n_sc, n_note = cx.news_score(titles)
    t_norm = res["score"] / eng.MAX_SCORE
    t_note = "9 indicators, quality filter " + ("passed" if res["signal"] != "WAIT" else "blocked")
    final = cx.combine(t_norm, res["signal"], f_sc, m_sc, n_sc)
    pillars = [("Technical", max(-1.0, min(1.0, t_norm * 2)), t_note), ("Order flow", f_sc, f_note),
               ("Financial (macro)", m_sc, m_note), ("Narrative (news)", n_sc, n_note)]
    return dict(res=res, bt=bt, final=final, pillars=pillars, titles=titles)


def chart(d, pair, tf, levels=()):
    d = d.tail(70)
    f = go.Figure()
    f.add_trace(go.Candlestick(x=d.index, open=d.Open, high=d.High, low=d.Low, close=d.Close,
                               increasing_line_color="#22e3a5", decreasing_line_color="#ff5470", name="Price"))
    for col, color in (("ema9", "#7dd3fc"), ("ema21", "#60a5fa"), ("ema50", "#a78bfa")):
        f.add_trace(go.Scatter(x=d.index, y=d[col], line=dict(width=1.3, color=color), name=col.upper()))
    last = float(d["Close"].iloc[-1])
    for lv in levels:
        f.add_hline(y=lv, line=dict(color="#22e3a5" if lv <= last else "#ff5470", width=1, dash="dash"), opacity=.5)
    f.update_layout(height=420, margin=dict(l=8, r=8, t=34, b=8), xaxis_rangeslider_visible=False,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#07122b", font=dict(color="#c9d8f5"),
                    title=f"{pair}  {tf}", legend=dict(orientation="h", y=1.1),
                    xaxis=dict(gridcolor="#10234d"), yaxis=dict(gridcolor="#10234d"))
    return f


def market_panel(pair_name, tfname, res=None):
    df = load(PAIRS[pair_name], tfname)
    if df.empty or len(df) < 3:
        st.warning("No market data right now.")
        return
    last, prev = df.iloc[-1], df.iloc[-2]
    chg = (last.Close - prev.Close) / prev.Close * 100
    live = is_live(df, TF[tfname][2])
    badge = ('<span class="badge b-live">Live</span>' if live
             else '<span class="badge b-off">Market closed or delayed</span>')
    dec = 5 if last.Close < 50 else 2
    st.markdown(f"<p class='meta'><b>{pair_name}</b> on {tfname} {badge}<br>Last closed price "
                f"<b>{last.Close:.{dec}f}</b> ({chg:+.3f}%). Last candle <b>{df.index[-1]:%d %b %H:%M}</b> PKT. "
                "Compare these candles with your Quotex chart.</p>", unsafe_allow_html=True)
    d = eng.add_indicators(df.tail(300))
    levels = [lv for lv, _ in res["levels"]] if res else []
    st.plotly_chart(chart(d, pair_name, tfname, levels), use_container_width=True)
    st.markdown(th.candles_html(df), unsafe_allow_html=True)
    st.markdown("<p class='note'>Candles come from the real market feed, so they can differ slightly from "
                "your broker. Quotex OTC pairs use Quotex's own prices and will not match.</p>",
                unsafe_allow_html=True)


def quick_card(pair_name, tfname, broker_name):
    df = load(PAIRS[pair_name], tfname)
    if df.empty:
        return "<div class='card meta'>No market data right now.</div>"
    last = df.iloc[-1]
    live = is_live(df, TF[tfname][2])
    badge = ('<span class="badge b-live">Live</span>' if live
             else '<span class="badge b-off">Market closed or delayed</span>')
    dec = 5 if last.Close < 50 else 2
    return (f"<div class='card meta'><b>{pair_name}</b> on {tfname} via {broker_name} {badge}<br>"
            f"Last closed price <b>{last.Close:.{dec}f}</b><br>Last candle <b>{df.index[-1]:%H:%M}</b> PKT<br>"
            f"Expiry <b>{tfname}</b>, same as the time frame</div>")


# -------------------------------------------------------------------- header
now_ts = pd.Timestamp.now(tz=TZ)
st.markdown(f"""<div class="top"><div class="brand">{th.LOGO.format(s=54)}
<div><div class="name">AK SIGNAL BOT</div>
<div class="tag">Technical, order flow, financial and narrative analysis</div></div></div>
<div class="live"><i></i>{now_ts:%d %b, %H:%M} PKT</div></div>""", unsafe_allow_html=True)

with st.expander("Settings", expanded=False):
    s1, s2, s3 = st.columns(3)
    thr = s1.slider("Signal strictness", 3, 9, 5, help="Higher means fewer but stronger signals")
    payout = s2.slider("Broker payout %", 70, 95, 85) / 100
    tg_on = s3.toggle("Send signal to Telegram")
    tg_token = st.text_input("Telegram bot token", type="password") if tg_on else ""
    tg_chat = st.text_input("Telegram chat ID") if tg_on else ""

orb_box = st.container()  # the circle is drawn here, above the controls

left, right = st.columns([1.1, 1], gap="medium")
with left:
    go_btn = st.button("GENERATE SIGNAL")
    broker = st.selectbox("Broker", BROKERS)
    pair = st.selectbox("Trading asset", list(PAIRS))
    tfname = st.selectbox("Time frame", list(TF))
with right:
    st.markdown(quick_card(pair, tfname, broker), unsafe_allow_html=True)

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
        st.markdown(th.orb_idle(), unsafe_allow_html=True)
        return
    if job["phase"] == "wait":
        if now > job["end_at"]:
            st.session_state.pop("job")
            st.rerun()
        if now < job["reveal_at"]:
            st.markdown(th.orb_wait(job["reveal_at"] - now, job["boundary"]), unsafe_allow_html=True)
            return
        with st.spinner("Reading the closed candle, flow, macro and news..."):
            load_raw.clear()
            df = load(PAIRS[job["pair"]], job["tf"])
            if len(df) < 80 or not is_live(df, TF[job["tf"]][2]):
                st.session_state.pop("job")
                st.session_state["err"] = closed_msg(job["pair"], df)
                st.rerun()
            job.update(build(job, df))
        job.update(phase="signal", start_sig=time.time())
        if job["tg"]:
            send_telegram(job["tg"][0], job["tg"][1], tg_text(job))
        st.rerun()
    if job["phase"] == "signal":
        left_s = job["end_at"] - now
        if left_s > 0:
            st.markdown(th.orb_signal(job, left_s), unsafe_allow_html=True)
            return
        st.session_state.pop("job")
        st.rerun()


with orb_box:
    orb_panel()

if st.session_state.get("err"):
    st.error(st.session_state["err"])

job = st.session_state.get("job")
sig_job = job if job and job["phase"] == "signal" else None
if sig_job:
    st.markdown(th.stats_html(sig_job), unsafe_allow_html=True)
    st.markdown(th.why_html(sig_job), unsafe_allow_html=True)
    st.markdown("<h3 style='font-family:Orbitron;font-size:17px;margin:14px 0 8px'>Four-pillar analysis</h3>",
                unsafe_allow_html=True)
    st.markdown(th.pillars_html(sig_job["pillars"]), unsafe_allow_html=True)
    with st.expander("Indicator votes"):
        st.markdown(th.votes_html(sig_job["res"]), unsafe_allow_html=True)
    with st.expander("News headlines used"):
        st.markdown(th.news_html(sig_job["titles"]), unsafe_allow_html=True)
else:
    st.markdown("<p class='note'>The signal appears when the current candle closes, stays until its "
                "expiry, then disappears by itself.</p>", unsafe_allow_html=True)

st.markdown("<h3 style='font-family:Orbitron;font-size:17px;margin-top:18px'>Live market data</h3>",
            unsafe_allow_html=True)
mp_pair, mp_tf = (job["pair"], job["tf"]) if job else (pair, tfname)
market_panel(mp_pair, mp_tf, sig_job["res"] if sig_job else None)

with st.expander("Backtest"):
    b1, b2, b3 = st.columns(3)
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

st.markdown("<p class='note'>Signals are analysis, not predictions or financial advice. News and macro "
            "layers move slowly and matter little on 1-minute trades. Binary options carry a high risk of "
            "losing your stake. Use a demo account first.</p>", unsafe_allow_html=True)
