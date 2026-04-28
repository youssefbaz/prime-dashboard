import streamlit as st
import time
import datetime
from utils import load_data, save_data, get_week_info

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ── Zen Mode CSS ──────────────────────────────────────────
st.markdown("""
<style>
.zen-dim {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.85);
    z-index: 99;
    pointer-events: none;
    transition: opacity 1s ease;
    opacity: 0;
}
.zen-active .zen-dim { opacity: 1; }
.timer-container {
    position: relative;
    z-index: 100;
    transition: all 0.6s ease;
}
.zen-active .timer-container {
    transform: scale(1.1);
    margin-top: 10vh !important;
}
.zen-active [data-testid="stSidebar"], .zen-active .page-title, .zen-active .page-sub, .zen-active .s-card, .zen-active .sec-title {
    opacity: 0.1;
    filter: blur(4px);
    pointer-events: none;
}
.timer-glow {
    text-shadow: 0 0 30px rgba(99,102,241,0.4);
}
.zen-active .timer-glow {
    text-shadow: 0 0 60px rgba(99,102,241,0.8);
}
</style>
""", unsafe_allow_html=True)

running = st.session_state.get("timer_running", False)
if running:
    st.markdown('<div class="zen-dim"></div>', unsafe_allow_html=True)
    st.markdown('<script>document.body.classList.add("zen-active")</script>', unsafe_allow_html=True)
else:
    st.markdown('<script>document.body.classList.remove("zen-active")</script>', unsafe_allow_html=True)

st.markdown('<p class="page-title">Focus Timer</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Deep work blocks — stay locked in. Sessions are tracked automatically.</p>', unsafe_allow_html=True)

data       = load_data()
wi         = get_week_info()
today_str  = wi["today_str"]
sessions   = data.get("focus_sessions", [])

# ── Focus stats (today) ────────────────────────────────────
today_sessions = [s for s in sessions if s.get("date") == today_str]
today_minutes  = sum(s.get("minutes", 0) for s in today_sessions)
total_minutes  = sum(s.get("minutes", 0) for s in sessions)

# ── Radio & Label Row ─────────────────────────────────────
r1, r2 = st.columns([1, 1])
with r1:
    session_label = st.selectbox(
        "Focus on:",
        ["💻 Practice", "☁️ AWS", "🧠 ML", "💼 Job hunt", "📓 Review", "🔬 Other"],
        key="focus_label",
    )
with r2:
    st.markdown("""<div style="height:32px;"></div>""", unsafe_allow_html=True)
    with st.expander("🎵 Spotify Search"):
        sp_cid = st.secrets.get("SPOTIFY_CLIENT_ID", "")
        sp_cs  = st.secrets.get("SPOTIFY_CLIENT_SECRET", "")
        if not sp_cid:
            st.info("Add `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` to `.streamlit/secrets.toml` to enable search.")
        else:
            query = st.text_input("Search Spotify", placeholder="Song, artist, album…", key="sp_query", label_visibility="collapsed")
            if query and HAS_REQUESTS:
                import base64
                if "sp_token" not in st.session_state:
                    creds = base64.b64encode(f"{sp_cid}:{sp_cs}".encode()).decode()
                    tok_r = requests.post(
                        "https://accounts.spotify.com/api/token",
                        headers={"Authorization": f"Basic {creds}"},
                        data={"grant_type": "client_credentials"}, timeout=5,
                    )
                    st.session_state.sp_token = tok_r.json().get("access_token") if tok_r.status_code == 200 else None
                token = st.session_state.get("sp_token")
                if token:
                    sr = requests.get(
                        "https://api.spotify.com/v1/search",
                        headers={"Authorization": f"Bearer {token}"},
                        params={"q": query, "type": "track", "limit": 5}, timeout=5,
                    )
                    if sr.status_code == 401:
                        del st.session_state["sp_token"]
                        st.rerun()
                    elif sr.status_code == 200:
                        tracks = sr.json().get("tracks", {}).get("items", [])
                        if tracks:
                            for t in tracks:
                                artists = ", ".join(a["name"] for a in t["artists"])
                                c_info, c_btn = st.columns([4, 1])
                                with c_info:
                                    st.markdown(f'<div style="font-size:13px;color:#cbd5e1;padding:6px 0;"><strong>{t["name"]}</strong><br><span style="font-size:11px;color:#64748b;">{artists}</span></div>', unsafe_allow_html=True)
                                with c_btn:
                                    if st.button("▶", key=f"sp_{t['id']}", help="Play in sidebar"):
                                        st.session_state.sp_playing_track = t["id"]
                                        st.rerun()
                        else:
                            st.warning("No tracks found.")
                    else:
                        st.error(f"Spotify error {sr.status_code}")
            # Show currently playing track
            playing = st.session_state.get("sp_playing_track")
            if playing:
                if st.button("⏹ Stop Spotify", key="sp_stop", use_container_width=True):
                    del st.session_state["sp_playing_track"]
                    st.rerun()

# Stats bar
sc1, sc2, sc3 = st.columns(3)
with sc1:
    st.markdown(f'<div class="s-card"><div class="s-label">Today</div><div class="s-val" style="color:#818cf8;">{today_minutes}m</div></div>', unsafe_allow_html=True)
with sc2:
    st.markdown(f'<div class="s-card"><div class="s-label">Sessions</div><div class="s-val" style="color:#34d399;">{len(today_sessions)}</div></div>', unsafe_allow_html=True)
with sc3:
    st.markdown(f'<div class="s-card"><div class="s-label">All-time</div><div class="s-val" style="color:#f472b6;">{total_minutes}m</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Timer Display ─────────────────────────────────────────
st.markdown('<div class="timer-container">', unsafe_allow_html=True)

# Presets
p1, p2, p3, p4 = st.columns(4)
with p1:
    if st.button("15m", use_container_width=True):
        st.session_state.timer_seconds = 15 * 60
        st.session_state.timer_initial = 15 * 60
with p2:
    if st.button("25m", use_container_width=True):
        st.session_state.timer_seconds = 25 * 60
        st.session_state.timer_initial = 25 * 60
with p3:
    if st.button("45m", use_container_width=True):
        st.session_state.timer_seconds = 45 * 60
        st.session_state.timer_initial = 45 * 60
with p4:
    if st.button("60m", use_container_width=True):
        st.session_state.timer_seconds = 60 * 60
        st.session_state.timer_initial = 60 * 60

custom_min = st.slider("Duration", 1, 120, 25, key="timer_slider", label_visibility="collapsed")

if "timer_seconds" not in st.session_state:
    st.session_state.timer_seconds = custom_min * 60
    st.session_state.timer_initial = custom_min * 60

total_sec = st.session_state.timer_seconds
initial   = st.session_state.get("timer_initial", custom_min * 60)
mins      = total_sec // 60
secs      = total_sec % 60
t_color   = "#818cf8" if not running else "#fff"

pulse = "animation:pulseDot 1.4s ease-in-out infinite;" if running else ""
st.markdown(f"""
<div style="text-align:center;margin:40px 0;">
    <div class="timer-glow" style="font-size:120px;font-weight:900;font-family:'JetBrains Mono';
                letter-spacing:8px;color:{t_color};line-height:1;{pulse}">{mins:02d}:{secs:02d}</div>
    <div style="font-size:12px;color:#64748b;letter-spacing:5px;text-transform:uppercase;
                font-family:'JetBrains Mono';margin-top:20px;">
      {session_label}
    </div>
</div>
""", unsafe_allow_html=True)

timer_pct = round((total_sec / max(initial, 1)) * 100)
st.markdown(f'<div class="pbar-outer" style="max-width:500px;margin:0 auto 40px;height:4px;background:rgba(255,255,255,0.02);"><div class="pbar-inner" style="width:{timer_pct}%;background:linear-gradient(90deg,#6366f1,#ec4899);"></div></div>', unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────
bc1, bc2, bc3 = st.columns(3)
with bc1:
    if st.button("▶ Start Focus", use_container_width=True, type="primary"):
        st.session_state.timer_running = True
with bc2:
    if st.button("⏸ Pause", use_container_width=True):
        st.session_state.timer_running = False
with bc3:
    if st.button("⏹ Reset", use_container_width=True):
        st.session_state.timer_running = False
        st.session_state.timer_seconds = custom_min * 60
        st.session_state.timer_initial = custom_min * 60

st.markdown('</div>', unsafe_allow_html=True)

# ── Tick ──────────────────────────────────────────────────
if st.session_state.get("timer_running", False) and total_sec > 0:
    time.sleep(1)
    st.session_state.timer_seconds -= 1
    if st.session_state.timer_seconds <= 0:
        st.session_state.timer_running = False
        completed_min = round(initial / 60)
        data.setdefault("focus_sessions", []).append({
            "date":    today_str,
            "minutes": completed_min,
            "label":   session_label,
            "ts":      datetime.datetime.now().isoformat(timespec="seconds"),
        })
        save_data(data)
        st.balloons()
    st.rerun()

st.markdown("")
st.info("💡 45-min blocks for deep study, 15-min breaks between. The Pomodoro rhythm keeps you sharp.")

# ── Recent sessions log ───────────────────────────────────
if today_sessions:
    st.markdown('<div class="sec-title" style="margin-top:24px;">Today\'s sessions</div>', unsafe_allow_html=True)
    for s in reversed(today_sessions[-8:]):
        ts_str = s.get("ts", "")[-8:] if s.get("ts") else ""
        st.markdown(
            f'<div class="job-row">'
            f'<div><span style="font-weight:600;color:#e2e8f0;">{s.get("label","Focus")}</span></div>'
            f'<div style="display:flex;gap:14px;align-items:center;">'
            f'<span style="font-size:12px;color:#475569;font-family:JetBrains Mono,monospace;">{ts_str}</span>'
            f'<span class="badge" style="color:#a5b4fc;background:rgba(129,140,248,0.12);">{s.get("minutes",0)} min</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
