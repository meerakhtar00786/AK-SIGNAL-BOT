"""AK SIGNAL BOT - blue robotic theme and HTML parts."""
import pandas as pd

TZ = "Asia/Karachi"

LOGO = ('<svg viewBox="0 0 64 64" width="{s}" height="{s}" xmlns="http://www.w3.org/2000/svg">'
        '<defs><linearGradient id="rg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7dd3fc"/>'
        '<stop offset="1" stop-color="#2563eb"/></linearGradient></defs>'
        '<path d="M32 14V7" stroke="url(#rg)" stroke-width="3" stroke-linecap="round"/>'
        '<circle cx="32" cy="5" r="3" fill="#7dd3fc"/>'
        '<rect x="10" y="14" width="44" height="38" rx="12" fill="#081433" stroke="url(#rg)" stroke-width="3"/>'
        '<rect x="3" y="27" width="7" height="13" rx="3" fill="url(#rg)"/>'
        '<rect x="54" y="27" width="7" height="13" rx="3" fill="url(#rg)"/>'
        '<rect x="17" y="23" width="30" height="14" rx="7" fill="#050c22" stroke="#38bdf8" stroke-opacity=".5"/>'
        '<circle cx="25" cy="30" r="3.6" fill="#38bdf8"/><circle cx="39" cy="30" r="3.6" fill="#38bdf8"/>'
        '<path d="M21 45h5l3-4 4 6 3-4h7" fill="none" stroke="#7dd3fc" stroke-width="2.2" '
        'stroke-linecap="round" stroke-linejoin="round"/></svg>')

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=DM+Sans:wght@400;500;700&display=swap');
:root{--bg:#040916;--line:#18305f;--blue:#38bdf8;--up:#22e3a5;--down:#ff5470;--mute:#7f93bd;--text:#e8f1ff;--warn:#fbbf24}
.stApp{background:radial-gradient(900px 480px at 50% -10%,#10337a 0%,transparent 62%),
linear-gradient(rgba(56,189,248,.045) 1px,transparent 1px) 0 0/44px 44px,
linear-gradient(90deg,rgba(56,189,248,.045) 1px,transparent 1px) 0 0/44px 44px,var(--bg);
color:var(--text);font-family:'DM Sans',sans-serif}
#MainMenu,footer,header[data-testid="stHeader"]{visibility:hidden;height:0}
.block-container{padding-top:1.2rem;max-width:760px}
.top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px}
.brand{display:flex;align-items:center;gap:14px}
.brand .name{font:900 24px 'Orbitron';letter-spacing:.04em;background:linear-gradient(90deg,#bae6fd,#38bdf8 55%,#3b82f6);
-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.brand .tag{color:var(--mute);font-size:13px}
.live{display:flex;align-items:center;gap:8px;color:var(--mute);font-size:13px;border:1px solid var(--line);
border-radius:99px;padding:7px 14px;background:#07122b;white-space:nowrap}
.live i{width:8px;height:8px;border-radius:50%;background:var(--up);box-shadow:0 0 10px var(--up)}
.meta{color:var(--mute);font-size:14px;line-height:1.7}.meta b{color:var(--text)}
.stage{display:flex;justify-content:center;padding:44px 0 14px}
.orb{position:relative;width:310px;height:310px;border-radius:50%;box-shadow:0 0 90px var(--g)}
.orb .r1{position:absolute;inset:-16px;border-radius:50%;border:2px dashed var(--c);opacity:.45;animation:spin 26s linear infinite}
.orb .r2{position:absolute;inset:0;border-radius:50%;background:conic-gradient(var(--c),transparent 40%,var(--c));animation:spin 1.6s linear infinite}
.orb .slow{animation-duration:12s}
.orb svg.prog{position:absolute;inset:0;width:100%;height:100%;transform:rotate(-90deg)}
.orb svg.prog circle.fg{animation-name:drain;animation-timing-function:linear;animation-fill-mode:forwards}
.orb .in{position:absolute;inset:12px;border-radius:50%;background:radial-gradient(circle at 50% 26%,#14377d,#050c20 70%);
display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 20px}
.orb .ant{position:absolute;left:50%;top:-38px;width:4px;height:28px;margin-left:-2px;background:var(--c);border-radius:4px}
.orb .ant::after{content:"";position:absolute;top:-9px;left:-4px;width:12px;height:12px;border-radius:50%;background:var(--c);box-shadow:0 0 14px var(--c);animation:blink 1.4s ease-in-out infinite}
.orb .ear{position:absolute;top:50%;width:14px;height:64px;margin-top:-32px;background:linear-gradient(var(--c),#0a1430);border-radius:8px}
.orb .ear.l{left:-30px}.orb .ear.r{right:-30px}
.orb .eyes{display:flex;gap:24px;margin-bottom:6px}
.orb .eyes i{width:13px;height:13px;border-radius:50%;background:var(--c);box-shadow:0 0 14px var(--c);animation:blink 2.4s ease-in-out infinite}
.orb .emo{font-size:44px;line-height:1.1}
.orb .w{font:900 50px/1.05 'Orbitron';color:var(--c)}
.orb .t{font:700 26px 'Orbitron';color:var(--text);margin-top:4px}
.orb .s{font-size:13px;color:var(--mute);line-height:1.4;margin-top:3px}
.cf{font-size:12px;font-weight:700;padding:3px 12px;border-radius:99px;margin-top:6px}
.cf.hi{background:rgba(34,227,165,.16);color:var(--up)}.cf.lo{background:rgba(251,191,36,.16);color:var(--warn)}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes blink{50%{opacity:.3}}
@keyframes drain{from{stroke-dashoffset:0}to{stroke-dashoffset:904.8}}
.stats{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0 10px}
.stat{flex:1 1 140px;background:linear-gradient(180deg,#0c1b3d,#07122b);border:1px solid var(--line);border-radius:16px;padding:14px 16px;text-align:center}
.stat b{display:block;font:900 22px 'Orbitron'}.stat span{color:var(--mute);font-size:12.5px}
.good{color:var(--up)}.bad{color:var(--down)}
.card{background:linear-gradient(180deg,#0c1b3d,#07122b);border:1px solid var(--line);border-radius:18px;padding:16px 18px;margin-bottom:10px}
.pl{padding:7px 0;border-bottom:1px solid #112650}.pl:last-child{border-bottom:none}
.pn{display:flex;justify-content:space-between;font-size:14px}
.pn .upt{color:var(--up)}.pn .dnt{color:var(--down)}.pn .not{color:var(--mute)}
.pb{position:relative;height:8px;background:#0e1c3d;border-radius:99px;margin:7px 0 4px}
.pb::after{content:"";position:absolute;left:50%;top:-2px;bottom:-2px;width:2px;background:#2a4580}
.pb i{position:absolute;top:0;bottom:0;border-radius:99px}
.pb i.up{background:var(--up)}.pb i.dn{background:var(--down)}.pb i.no{background:var(--mute)}
table.votes,table.cn{width:100%;border-collapse:collapse;font-size:14px}
table.votes td{padding:9px 6px;border-bottom:1px solid #112650}
table.votes tr:last-child td{border-bottom:none}
table.cn{font-size:13.5px;text-align:right}
table.cn th{color:var(--mute);font-weight:500;padding:8px 6px;text-align:right;border-bottom:1px solid var(--line)}
table.cn th:first-child,table.cn td:first-child{text-align:left}
table.cn td{padding:8px 6px;border-bottom:1px solid #0f2248;font-variant-numeric:tabular-nums}
table.cn tr:last-child td{border-bottom:none}
.pill{display:inline-block;min-width:42px;text-align:center;padding:3px 10px;border-radius:99px;font-weight:700;font-size:13px}
.p-up{background:rgba(34,227,165,.15);color:var(--up)}.p-dn{background:rgba(255,84,112,.15);color:var(--down)}.p-no{background:#112650;color:var(--mute)}
.badge{display:inline-block;padding:3px 11px;border-radius:99px;font-size:12.5px;font-weight:700}
.b-live{background:rgba(34,227,165,.15);color:var(--up)}.b-off{background:rgba(255,84,112,.15);color:var(--down)}
div.stButton>button{background:linear-gradient(135deg,#7dd3fc,#38bdf8 45%,#2563eb);color:#03112b;
font:900 15px 'Orbitron';letter-spacing:.04em;border:0;border-radius:14px;padding:15px 22px;width:100%;box-shadow:0 12px 34px rgba(56,189,248,.32)}
div.stButton>button:hover{filter:brightness(1.1);color:#03112b}
div[data-baseweb="select"]>div{background:#07122b;border:1px solid var(--line);border-radius:12px}
label p{color:var(--mute)!important;font-size:13px!important}
.note{color:var(--mute);font-size:12.5px;line-height:1.6}
@media (max-width:640px){.orb{width:262px;height:262px}.orb .w{font-size:40px}.orb .emo{font-size:36px}.brand .name{font-size:19px}.live{display:none}}
</style>"""


def mmss(sec):
    sec = max(0, int(sec + 0.999))
    return f"{sec // 60:02d}:{sec % 60:02d}"


def _orb(c, g, inner, ring="", spin=""):
    return (f'<div class="stage"><div class="orb" style="--c:{c};--g:{g}"><div class="ant"></div>'
            f'<div class="ear l"></div><div class="ear r"></div><div class="r1"></div>{spin}{ring}'
            f'<div class="in"><div class="eyes"><i></i><i></i></div>{inner}</div></div></div>')


def orb_idle():
    return _orb("#38bdf8", "rgba(56,189,248,.28)",
                '<div class="w" style="font-size:36px">READY</div>'
                '<div class="s">Choose your market and press<br>Generate signal</div>',
                spin='<div class="r2 slow"></div>')


def orb_wait(left_s, boundary):
    at = pd.Timestamp(boundary, unit="s", tz="UTC").tz_convert(TZ)
    return _orb("#38bdf8", "rgba(56,189,248,.42)",
                f'<div class="t" style="font-size:42px">{mmss(left_s)}</div>'
                '<div class="w" style="font-size:20px">ANALYZING</div>'
                f'<div class="s">Fresh signal at candle close<br>{at:%H:%M:%S}</div>',
                spin='<div class="r2"></div>')


def orb_signal(job, left_s):
    fin = job["final"]
    up = fin["direction"] == "CALL"
    c, g = ("#22e3a5", "rgba(34,227,165,.48)") if up else ("#ff5470", "rgba(255,84,112,.48)")
    emo, word = ("📈", "BUY") if up else ("📉", "SELL")
    hi = fin["conf"] == "HIGH"
    total = max(job["end_at"] - job["start_sig"], 1)
    if "off" not in job:
        job["off"] = max(0.0, total - left_s)
    ring = ('<svg class="prog" viewBox="0 0 300 300"><circle cx="150" cy="150" r="144" fill="none" '
            'stroke="#10234d" stroke-width="8"/><circle class="fg" cx="150" cy="150" r="144" fill="none" '
            f'stroke="{c}" stroke-width="8" stroke-linecap="round" stroke-dasharray="904.8" '
            f'style="animation-duration:{total:.0f}s;animation-delay:-{job["off"]:.1f}s"/></svg>')
    inner = (f'<div class="emo">{emo}</div><div class="w">{word}</div>'
             f'<div class="cf {"hi" if hi else "lo"}">{"HIGH CONFIDENCE" if hi else "LOW CONFIDENCE · SKIP"}</div>'
             f'<div class="t">{mmss(left_s)}</div><div class="s">until expiry</div>')
    return _orb(c, g, inner, ring=ring)


def stats_html(job):
    fin, bt, res = job["final"], job["bt"], job["res"]
    if bt["trades"] >= 20:
        cls = "good" if bt["win_rate"] > bt["break_even"] else "bad"
        acc = f'<b class="{cls}">{bt["win_rate"]:.0f}%</b><span>Recent accuracy, technical ({bt["trades"]} trades)</span>'
    else:
        acc = '<b>n/a</b><span>Recent accuracy (too few trades)</span>'
    s_, r_ = res["support"], res["resistance"]
    return ('<div class="stats">'
            f'<div class="stat"><b>{fin["strength"]}%</b><span>Signal strength</span></div>'
            f'<div class="stat">{acc}</div>'
            f'<div class="stat"><b>{job["tf"]}</b><span>Expiry</span></div></div>'
            f'<p class="meta">Price <b>{res["price"]:.5g}</b>. Support <b>{f"{s_[0]:.5g}" if s_ else "none"}</b>, '
            f'resistance <b>{f"{r_[0]:.5g}" if r_ else "none"}</b>. Break-even needs <b>{bt["break_even"]:.0f}%</b>.</p>')


def pillars_html(pillars):
    rows = ""
    for name, sc, note in pillars:
        side = "up" if sc > 0.05 else "dn" if sc < -0.05 else "no"
        lab = {"up": "BUY", "dn": "SELL", "no": "Neutral"}[side]
        pos = "left:50%" if sc >= 0 else "right:50%"
        rows += (f'<div class="pl"><div class="pn"><b>{name}</b><span class="{side}t">{lab}</span></div>'
                 f'<div class="pb"><i class="{side}" style="{pos};width:{int(abs(sc) * 50)}%"></i></div>'
                 f'<div class="meta">{note}</div></div>')
    return f'<div class="card">{rows}</div>'


def why_html(job):
    if job["final"]["conf"] == "HIGH":
        return ""
    res = job["res"]
    last = res["votes"][-1]
    if res["signal"] == "WAIT" and last["name"] == "Quality filter" and last["note"].startswith("Blocked"):
        why = last["note"].replace("Blocked: ", "")
    elif res["signal"] == "WAIT":
        why = f"technical indicators do not agree enough (score {res['score']:+d})"
    else:
        why = "flow, macro or news point the other way"
    return (f"<div class='card meta'><b>Why low confidence:</b> {why}. The direction shown is only the "
            "best guess. Trading it is close to a coin flip, so skipping is the safer choice.</div>")


def votes_html(res):
    rows = ""
    for v in res["votes"]:
        cls = "p-up" if v["vote"] > 0 else "p-dn" if v["vote"] < 0 else "p-no"
        rows += (f"<tr><td><b>{v['name']}</b></td><td class='meta'>{v['note']}</td>"
                 f"<td style='text-align:right'><span class='pill {cls}'>{v['vote']:+d}</span></td></tr>")
    return f"<div class='card'><table class='votes'>{rows}</table></div>"


def news_html(titles):
    if not titles:
        return "<p class='meta'>No recent headlines found for this market.</p>"
    return "<div class='card meta'>" + "<br>".join("• " + t for t in titles) + "</div>"


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
