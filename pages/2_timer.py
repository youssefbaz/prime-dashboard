import streamlit as st
import time

st.markdown('<p class="page-title">Focus timer</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Deep work blocks — stay locked in.</p>', unsafe_allow_html=True)

# Presets
p1, p2, p3, p4 = st.columns(4)
with p1:
    if st.button("15 min", use_container_width=True, key="t15"):
        st.session_state.timer_seconds = 15 * 60
with p2:
    if st.button("30 min", use_container_width=True, key="t30"):
        st.session_state.timer_seconds = 30 * 60
with p3:
    if st.button("45 min", use_container_width=True, key="t45"):
        st.session_state.timer_seconds = 45 * 60
with p4:
    if st.button("60 min", use_container_width=True, key="t60"):
        st.session_state.timer_seconds = 60 * 60

custom_min = st.slider("Custom duration (minutes)", 1, 120, 25, key="timer_slider")

if "timer_seconds" not in st.session_state:
    st.session_state.timer_seconds = custom_min * 60

total_sec = st.session_state.timer_seconds
mins = total_sec // 60
secs = total_sec % 60

t_color = "#818cf8" if total_sec > 600 else ("#fbbf24" if total_sec > 120 else "#ef4444")

st.markdown(f"""
<div style="text-align:center;margin:40px 0 10px;">
  <div style="font-size:72px;font-weight:800;font-family:'JetBrains Mono',monospace;
  letter-spacing:4px;color:{t_color};">{mins:02d}:{secs:02d}</div>
</div>
""", unsafe_allow_html=True)

timer_pct = round((total_sec / max(custom_min * 60, 1)) * 100)
st.markdown(f'<div class="pbar-outer" style="max-width:400px;margin:0 auto 32px;"><div class="pbar-inner" style="width:{timer_pct}%;background:{t_color};"></div></div>', unsafe_allow_html=True)

bc1, bc2, bc3 = st.columns([1, 1, 1])
with bc1:
    if st.button("▶️ Start", use_container_width=True, key="tstart"):
        st.session_state.timer_running = True
        st.session_state.timer_seconds = custom_min * 60
with bc2:
    if st.button("⏸️ Pause", use_container_width=True, key="tpause"):
        st.session_state.timer_running = False
with bc3:
    if st.button("⏹️ Reset", use_container_width=True, key="treset"):
        st.session_state.timer_running = False
        st.session_state.timer_seconds = custom_min * 60

if st.session_state.get("timer_running", False) and total_sec > 0:
    time.sleep(1)
    st.session_state.timer_seconds -= 1
    if st.session_state.timer_seconds <= 0:
        st.session_state.timer_running = False
        st.success("⏰ Time's up! Great focus session!")
        st.balloons()
    st.rerun()

st.markdown("")
st.info("💡 Use 45-min blocks for deep study, 15-min breaks between. The Pomodoro rhythm keeps you sharp.")
