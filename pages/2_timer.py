import streamlit as st
import time
import datetime
from utils import load_data, save_data, get_week_info

st.markdown('<p class="page-title">Focus timer</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Deep work blocks — stay locked in. Sessions are tracked automatically.</p>', unsafe_allow_html=True)

data       = load_data()
wi         = get_week_info()
today_str  = wi["today_str"]
sessions   = data.get("focus_sessions", [])

# ── Focus stats (today) ────────────────────────────────────
today_sessions = [s for s in sessions if s.get("date") == today_str]
today_minutes  = sum(s.get("minutes", 0) for s in today_sessions)
total_minutes  = sum(s.get("minutes", 0) for s in sessions)

sc1, sc2, sc3 = st.columns(3)
with sc1:
    st.markdown(f'<div class="s-card"><div class="s-label">Today</div><div class="s-val" style="color:#818cf8;">{today_minutes}</div><div class="s-sub">minutes focused</div></div>', unsafe_allow_html=True)
with sc2:
    st.markdown(f'<div class="s-card"><div class="s-label">Sessions today</div><div class="s-val" style="color:#34d399;">{len(today_sessions)}</div><div class="s-sub">completed</div></div>', unsafe_allow_html=True)
with sc3:
    st.markdown(f'<div class="s-card"><div class="s-label">All-time</div><div class="s-val" style="color:#f472b6;">{total_minutes}</div><div class="s-sub">minutes total</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Session label (what are you working on?) ──────────────
session_label = st.selectbox(
    "What are you working on?",
    ["💻 Practice", "☁️ AWS", "🧠 ML", "💼 Job hunt", "📓 Review", "🔬 Other"],
    key="focus_label",
)

# ── Presets ────────────────────────────────────────────────
p1, p2, p3, p4 = st.columns(4)
with p1:
    if st.button("15 min", use_container_width=True, key="t15"):
        st.session_state.timer_seconds = 15 * 60
        st.session_state.timer_initial = 15 * 60
with p2:
    if st.button("30 min", use_container_width=True, key="t30"):
        st.session_state.timer_seconds = 30 * 60
        st.session_state.timer_initial = 30 * 60
with p3:
    if st.button("45 min", use_container_width=True, key="t45"):
        st.session_state.timer_seconds = 45 * 60
        st.session_state.timer_initial = 45 * 60
with p4:
    if st.button("60 min", use_container_width=True, key="t60"):
        st.session_state.timer_seconds = 60 * 60
        st.session_state.timer_initial = 60 * 60

custom_min = st.slider("Custom duration (minutes)", 1, 120, 25, key="timer_slider")

# Initial init: use slider on first load only
if "timer_seconds" not in st.session_state:
    st.session_state.timer_seconds = custom_min * 60
    st.session_state.timer_initial = custom_min * 60

total_sec = st.session_state.timer_seconds
initial   = st.session_state.get("timer_initial", custom_min * 60)
mins      = total_sec // 60
secs      = total_sec % 60

t_color = "#818cf8" if total_sec > 600 else ("#fbbf24" if total_sec > 120 else "#ef4444")
running = st.session_state.get("timer_running", False)

# ── Big circular-feel display ─────────────────────────────
pulse = "animation:pulseDot 1.4s ease-in-out infinite;" if running else ""
st.markdown(f"""
<div style="text-align:center;margin:32px 0 12px;">
  <div style="display:inline-block;padding:40px 60px;border-radius:24px;
              background:rgba(255,255,255,0.03);backdrop-filter:blur(14px);
              border:1px solid rgba(255,255,255,0.08);
              box-shadow:0 8px 40px rgba(99,102,241,0.10);">
    <div style="font-size:84px;font-weight:800;font-family:'JetBrains Mono',monospace;
                letter-spacing:6px;color:{t_color};line-height:1;{pulse}">{mins:02d}:{secs:02d}</div>
    <div style="font-size:11px;color:#64748b;letter-spacing:3px;text-transform:uppercase;
                font-family:'JetBrains Mono',monospace;margin-top:14px;">
      {session_label} · {"running" if running else "ready"}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

timer_pct = round((total_sec / max(initial, 1)) * 100)
st.markdown(f'<div class="pbar-outer" style="max-width:420px;margin:0 auto 28px;"><div class="pbar-inner" style="width:{timer_pct}%;background:linear-gradient(90deg,{t_color},#a78bfa);"></div></div>', unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────
bc1, bc2, bc3 = st.columns(3)
with bc1:
    if st.button("▶️ Start", use_container_width=True, key="tstart"):
        # Use whatever timer_seconds is currently — preset or slider
        if st.session_state.timer_seconds <= 0:
            st.session_state.timer_seconds = custom_min * 60
            st.session_state.timer_initial = custom_min * 60
        st.session_state.timer_running    = True
        st.session_state.timer_started_at = time.time()
with bc2:
    if st.button("⏸️ Pause", use_container_width=True, key="tpause"):
        st.session_state.timer_running = False
with bc3:
    if st.button("⏹️ Reset", use_container_width=True, key="treset"):
        st.session_state.timer_running = False
        st.session_state.timer_seconds = custom_min * 60
        st.session_state.timer_initial = custom_min * 60

# ── Tick ──────────────────────────────────────────────────
if st.session_state.get("timer_running", False) and total_sec > 0:
    time.sleep(1)
    st.session_state.timer_seconds -= 1
    if st.session_state.timer_seconds <= 0:
        st.session_state.timer_running = False
        # Persist completed session
        completed_min = round(initial / 60)
        data.setdefault("focus_sessions", []).append({
            "date":    today_str,
            "minutes": completed_min,
            "label":   session_label,
            "ts":      datetime.datetime.now().isoformat(timespec="seconds"),
        })
        save_data(data)
        st.success(f"⏰ Time's up! +{completed_min} min logged to {session_label}.")
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
