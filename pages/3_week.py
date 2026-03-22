import streamlit as st
from utils import (get_week_info, ML_BY_WEEK, AWS_BY_WEEK,
                   PRACTICE_BY_WEEK, JOB_BY_WEEK)

wi       = get_week_info()
week_num = wi["week_num"]
day_name = wi["day_name"]
w        = max(1, min(8, week_num))

st.markdown('<p class="page-title">Week view</p>', unsafe_allow_html=True)
st.markdown(f'<p class="page-sub">Week {week_num} of 8 — your full schedule at a glance.</p>', unsafe_allow_html=True)

# Week selector
selected_week = st.slider("View week", 1, 8, week_num, key="week_sel")
w = selected_week

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
cols = st.columns(6)

for i, d in enumerate(days):
    with cols[i]:
        is_today = (d == day_name and selected_week == week_num)
        bg   = "rgba(99,102,241,0.08)" if is_today else "rgba(255,255,255,0.02)"
        bdr  = "1px solid rgba(99,102,241,0.3)" if is_today else "1px solid rgba(255,255,255,0.06)"
        badge = '<div style="display:inline-block;background:#6366f1;color:#fff;font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;padding:2px 8px;border-radius:4px;margin:6px 0;">TODAY</div>' if is_today else ""
        jt = JOB_BY_WEEK.get(w, {}).get(d, "—")
        at = AWS_BY_WEEK.get(w, {}).get(d, "—")
        mt = ML_BY_WEEK.get(w, {}).get(d, "—")
        pt = PRACTICE_BY_WEEK.get(w, {}).get(d, "—")
        st.markdown(f"""
        <div style="background:{bg};border:{bdr};border-radius:14px;padding:14px;min-height:220px;">
          <div style="font-size:14px;font-weight:700;color:#e2e8f0;">{d}</div>
          {badge}
          <div style="text-align:left;margin-top:8px;font-size:11px;line-height:1.8;">
            <div style="color:#fbbf24;">💼 {jt}</div>
            <div style="color:#60a5fa;">☁️ {at}</div>
            <div style="color:#f87171;">🧠 {mt}</div>
            <div style="color:#f472b6;">💻 {pt}</div>
          </div>
        </div>""", unsafe_allow_html=True)

# Sunday
st.markdown("")
st.markdown("""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
border-radius:14px;padding:16px 20px;display:flex;align-items:center;gap:16px;">
  <div style="font-size:14px;font-weight:700;color:#e2e8f0;min-width:40px;">Sun</div>
  <div style="font-size:13px;color:#64748b;">🧘 Rest & weekly review — reflect, plan next week, recharge.</div>
</div>
""", unsafe_allow_html=True)

# Week summary
st.markdown("")
st.markdown('<div class="sec-title">Week at a glance</div>', unsafe_allow_html=True)

summary_cols = st.columns(4)
with summary_cols[0]:
    total_jobs = sum(1 for d in days if JOB_BY_WEEK.get(w, {}).get(d, "—") != "—")
    st.markdown(f'<div class="s-card"><div class="s-label">Job tasks</div><div class="s-val" style="color:#fbbf24;">{total_jobs}</div><div class="s-sub">this week</div></div>', unsafe_allow_html=True)
with summary_cols[1]:
    st.markdown(f'<div class="s-card"><div class="s-label">AWS sessions</div><div class="s-val" style="color:#60a5fa;">6</div><div class="s-sub">Mon–Sat</div></div>', unsafe_allow_html=True)
with summary_cols[2]:
    st.markdown(f'<div class="s-card"><div class="s-label">ML sessions</div><div class="s-val" style="color:#f87171;">6</div><div class="s-sub">Mon–Sat</div></div>', unsafe_allow_html=True)
with summary_cols[3]:
    st.markdown(f'<div class="s-card"><div class="s-label">Practice days</div><div class="s-val" style="color:#f472b6;">6</div><div class="s-sub">Mon–Sat</div></div>', unsafe_allow_html=True)
