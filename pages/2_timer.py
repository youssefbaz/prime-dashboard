import streamlit as st
import time
import datetime
from utils import load_data, save_data, get_week_info

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ── Page ──────────────────────────────────────────────────
st.markdown('<p class="page-title">Focus Timer</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Pomodoro-powered deep work. Sessions tracked automatically.</p>', unsafe_allow_html=True)

data      = load_data()
wi        = get_week_info()
today_str = wi["today_str"]
sessions  = data.get("focus_sessions", [])

today_sessions = [s for s in sessions if s.get("date") == today_str]
today_minutes  = sum(s.get("minutes", 0) for s in today_sessions)
total_minutes  = sum(s.get("minutes", 0) for s in sessions)

# Count completed pomodoros (25-min work sessions) today
today_pomodoros = sum(1 for s in today_sessions if s.get("mode") == "work" or
                      (s.get("minutes", 0) >= 20 and s.get("mode") is None))

# ── Pomodoro cycle state ──────────────────────────────────
# Modes: "work", "short_break", "long_break"
if "pomo_mode" not in st.session_state:
    st.session_state.pomo_mode = "work"
if "pomo_count" not in st.session_state:
    st.session_state.pomo_count = 0  # completed work sessions

# ── Settings (sidebar-like expander) ─────────────────────
with st.expander("⚙️ Pomodoro Settings", expanded=False):
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        work_dur   = st.number_input("Work (min)", 5, 120, 25, step=5, key="cfg_work")
    with sc2:
        short_dur  = st.number_input("Short break (min)", 1, 30, 5, step=1, key="cfg_short")
    with sc3:
        long_dur   = st.number_input("Long break (min)", 5, 60, 15, step=5, key="cfg_long")
    with sc4:
        daily_goal = st.number_input("Daily goal (pomodoros)", 1, 20, 8, step=1, key="cfg_goal")
    auto_transition = st.checkbox("Auto-transition between work and break", value=True, key="cfg_auto")

# ── Focus label + Spotify ─────────────────────────────────
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
            st.info("Add `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` to secrets to enable search.")
        else:
            query = st.text_input("Search Spotify", placeholder="Song, artist…", key="sp_query",
                                  label_visibility="collapsed")
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
                        del st.session_state["sp_token"]; st.rerun()
                    elif sr.status_code == 200:
                        tracks = sr.json().get("tracks", {}).get("items", [])
                        for t in tracks:
                            artists = ", ".join(a["name"] for a in t["artists"])
                            ci, cb  = st.columns([4, 1])
                            with ci:
                                st.markdown(f'<div style="font-size:13px;color:#cbd5e1;padding:4px 0;"><strong>{t["name"]}</strong><br><span style="font-size:11px;color:#64748b;">{artists}</span></div>', unsafe_allow_html=True)
                            with cb:
                                if st.button("▶", key=f"sp_{t['id']}", help="Play in sidebar"):
                                    st.session_state.sp_playing_track = t["id"]; st.rerun()
            playing = st.session_state.get("sp_playing_track")
            if playing:
                if st.button("⏹ Stop Spotify", key="sp_stop", use_container_width=True):
                    del st.session_state["sp_playing_track"]; st.rerun()

# ── Stats row ─────────────────────────────────────────────
sc1, sc2, sc3, sc4 = st.columns(4)
with sc1:
    st.markdown(f'<div class="s-card"><div class="s-label">Today</div><div class="s-val" style="color:#818cf8;">{today_minutes}m</div></div>', unsafe_allow_html=True)
with sc2:
    st.markdown(f'<div class="s-card"><div class="s-label">Sessions</div><div class="s-val" style="color:#34d399;">{len(today_sessions)}</div></div>', unsafe_allow_html=True)
with sc3:
    pomo_color = "#34d399" if today_pomodoros >= daily_goal else "#fbbf24"
    st.markdown(f'<div class="s-card"><div class="s-label">Pomodoros</div><div class="s-val" style="color:{pomo_color};">{today_pomodoros}/{daily_goal}</div></div>', unsafe_allow_html=True)
with sc4:
    st.markdown(f'<div class="s-card"><div class="s-label">All-time</div><div class="s-val" style="color:#f472b6;">{total_minutes}m</div></div>', unsafe_allow_html=True)

# ── Daily pomodoro progress bar ───────────────────────────
pomo_pct = min(100, round((today_pomodoros / max(1, daily_goal)) * 100))
pomo_bar_color = "linear-gradient(90deg,#10b981,#34d399)" if pomo_pct >= 100 else "linear-gradient(90deg,#6366f1,#a78bfa)"
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;margin:16px 0 6px;">
  <span style="font-size:12px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:1px;font-family:'JetBrains Mono';">Daily goal progress</span>
  <span style="font-size:13px;font-weight:700;color:{'#34d399' if pomo_pct>=100 else '#818cf8'};font-family:'JetBrains Mono';">{today_pomodoros}/{daily_goal} pomodoros</span>
</div>
<div class="pbar-outer" style="margin-bottom:20px;">
  <div class="pbar-inner" style="width:{pomo_pct}%;background:{pomo_bar_color};"></div>
</div>
""", unsafe_allow_html=True)

# ── Mode indicator ────────────────────────────────────────
mode = st.session_state.pomo_mode
mode_labels  = {"work": "🍅 Work Session", "short_break": "☕ Short Break", "long_break": "🌿 Long Break"}
mode_colors  = {"work": "#818cf8", "short_break": "#34d399", "long_break": "#60a5fa"}
mode_durations = {
    "work":        st.session_state.get("cfg_work",  25),
    "short_break": st.session_state.get("cfg_short",  5),
    "long_break":  st.session_state.get("cfg_long",  15),
}

st.markdown(f"""
<div style="text-align:center;margin-bottom:12px;">
  <span style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:2px;
  color:{mode_colors[mode]};font-family:'JetBrains Mono';">{mode_labels[mode]}</span>
  &nbsp;·&nbsp;
  <span style="font-size:12px;color:#475569;font-family:'JetBrains Mono';">Session {st.session_state.pomo_count + 1}</span>
</div>
""", unsafe_allow_html=True)

# ── Quick mode switch buttons ─────────────────────────────
mb1, mb2, mb3 = st.columns(3)
with mb1:
    active_w = mode == "work"
    if st.button(f"🍅 Work {'●' if active_w else ''}", use_container_width=True,
                 key="mode_work"):
        st.session_state.pomo_mode = "work"
        st.session_state.timer_running = False
        st.session_state.timer_seconds = mode_durations["work"] * 60
        st.session_state.timer_initial = mode_durations["work"] * 60
        st.rerun()
with mb2:
    active_s = mode == "short_break"
    if st.button(f"☕ Short {'●' if active_s else ''}", use_container_width=True,
                 key="mode_short"):
        st.session_state.pomo_mode = "short_break"
        st.session_state.timer_running = False
        st.session_state.timer_seconds = mode_durations["short_break"] * 60
        st.session_state.timer_initial = mode_durations["short_break"] * 60
        st.rerun()
with mb3:
    active_l = mode == "long_break"
    if st.button(f"🌿 Long {'●' if active_l else ''}", use_container_width=True,
                 key="mode_long"):
        st.session_state.pomo_mode = "long_break"
        st.session_state.timer_running = False
        st.session_state.timer_seconds = mode_durations["long_break"] * 60
        st.session_state.timer_initial = mode_durations["long_break"] * 60
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── Preset buttons (for the current mode duration) ────────
if mode == "work":
    p1, p2, p3, p4 = st.columns(4)
    presets = [(15, p1), (25, p2), (45, p3), (60, p4)]
    for mins, col in presets:
        with col:
            if st.button(f"{mins}m", use_container_width=True, key=f"preset_{mins}"):
                st.session_state.timer_seconds = mins * 60
                st.session_state.timer_initial = mins * 60
                st.session_state.cfg_work      = mins

custom_min = st.slider(
    "Duration", 1, 120,
    mode_durations[mode],
    key="timer_slider", label_visibility="collapsed",
)

if "timer_seconds" not in st.session_state:
    st.session_state.timer_seconds = custom_min * 60
    st.session_state.timer_initial = custom_min * 60

running   = st.session_state.get("timer_running", False)
total_sec = st.session_state.timer_seconds
initial   = st.session_state.get("timer_initial", custom_min * 60)
mins      = total_sec // 60
secs      = total_sec % 60
t_color   = mode_colors[mode] if not running else "#fff"

pulse = "animation:pulseDot 1.4s ease-in-out infinite;" if running else ""
st.markdown(f"""
<div style="text-align:center;margin:40px 0;">
  <div style="font-size:110px;font-weight:900;font-family:'JetBrains Mono';
              letter-spacing:6px;color:{t_color};line-height:1;{pulse}
              text-shadow: 0 0 {'60px' if running else '30px'} {mode_colors[mode]}60;">{mins:02d}:{secs:02d}</div>
  <div style="font-size:12px;color:#64748b;letter-spacing:5px;text-transform:uppercase;
              font-family:'JetBrains Mono';margin-top:20px;">{session_label} &nbsp;·&nbsp; {mode_labels[mode]}</div>
</div>
""", unsafe_allow_html=True)

timer_pct = round((total_sec / max(initial, 1)) * 100)
st.markdown(f'<div class="pbar-outer" style="max-width:500px;margin:0 auto 40px;height:4px;"><div class="pbar-inner" style="width:{timer_pct}%;background:{mode_colors[mode]};"></div></div>', unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────
bc1, bc2, bc3 = st.columns(3)
with bc1:
    if st.button("▶ Start", use_container_width=True, type="primary", key="timer_start"):
        st.session_state.timer_running = True
with bc2:
    if st.button("⏸ Pause", use_container_width=True, key="timer_pause"):
        st.session_state.timer_running = False
with bc3:
    if st.button("⏹ Reset", use_container_width=True, key="timer_reset"):
        st.session_state.timer_running = False
        st.session_state.timer_seconds = mode_durations[mode] * 60
        st.session_state.timer_initial = mode_durations[mode] * 60

# ── Tick ──────────────────────────────────────────────────
if st.session_state.get("timer_running", False) and total_sec > 0:
    time.sleep(1)
    st.session_state.timer_seconds -= 1

    if st.session_state.timer_seconds <= 0:
        st.session_state.timer_running = False
        completed_min = round(initial / 60)

        # Save completed session
        data.setdefault("focus_sessions", []).append({
            "date":    today_str,
            "minutes": completed_min,
            "label":   session_label,
            "mode":    mode,
            "ts":      datetime.datetime.now().isoformat(timespec="seconds"),
        })
        save_data(data)
        st.balloons()

        # Auto-transition logic
        if st.session_state.get("cfg_auto", True):
            if mode == "work":
                st.session_state.pomo_count += 1
                # Every 4 pomodoros → long break, else short break
                if st.session_state.pomo_count % 4 == 0:
                    st.session_state.pomo_mode = "long_break"
                    next_dur = mode_durations["long_break"]
                else:
                    st.session_state.pomo_mode = "short_break"
                    next_dur = mode_durations["short_break"]
            else:
                st.session_state.pomo_mode = "work"
                next_dur = mode_durations["work"]

            st.session_state.timer_seconds = next_dur * 60
            st.session_state.timer_initial = next_dur * 60
        else:
            st.session_state.timer_seconds = mode_durations[mode] * 60
            st.session_state.timer_initial = mode_durations[mode] * 60

    st.rerun()

st.markdown("")
st.info("💡 25-min work → 5-min break → repeat. Every 4 pomodoros take a 15-min long break.")

# ── Today's session log ───────────────────────────────────
if today_sessions:
    st.markdown('<div class="sec-title" style="margin-top:24px;">Today\'s sessions</div>', unsafe_allow_html=True)

    mode_icons = {"work": "🍅", "short_break": "☕", "long_break": "🌿"}
    for s in reversed(today_sessions[-10:]):
        ts_str  = s.get("ts", "")[-8:] if s.get("ts") else ""
        s_mode  = s.get("mode", "work")
        s_icon  = mode_icons.get(s_mode, "🍅")
        s_color = mode_colors.get(s_mode, "#818cf8")
        st.markdown(
            f'<div class="job-row">'
            f'<div style="display:flex;align-items:center;gap:10px;">'
            f'<span style="font-size:16px;">{s_icon}</span>'
            f'<span style="font-weight:600;color:#e2e8f0;">{s.get("label","Focus")}</span>'
            f'</div>'
            f'<div style="display:flex;gap:14px;align-items:center;">'
            f'<span style="font-size:12px;color:#475569;font-family:JetBrains Mono,monospace;">{ts_str}</span>'
            f'<span class="badge" style="color:{s_color};background:{s_color}18;">{s.get("minutes",0)} min</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
