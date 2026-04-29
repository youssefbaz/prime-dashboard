import streamlit as st
from utils import (get_week_info, ML_BY_WEEK, AWS_BY_WEEK,
                   PRACTICE_BY_WEEK, JOB_BY_WEEK, TRAINING)

wi       = get_week_info()
week_num = wi["week_num"]
day_name = wi["day_name"]
w        = max(1, min(wi["plan_weeks"], week_num))

st.markdown('<p class="page-title">Week view</p>', unsafe_allow_html=True)
st.markdown(f'<p class="page-sub">Week {week_num} of {wi["plan_weeks"]} — your full schedule at a glance.</p>', unsafe_allow_html=True)

# Extra CSS for week view cards
st.markdown("""
<style>
.wk-card {
    border-radius: 14px;
    padding: 18px 16px;
    min-height: 340px;
    margin-bottom: 12px;
}
.wk-card-normal {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
}
.wk-card-today {
    background: rgba(99,102,241,0.06);
    border: 1px solid rgba(99,102,241,0.25);
    box-shadow: 0 0 20px rgba(99,102,241,0.08);
}
.wk-day-name {
    font-size: 16px;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 4px;
}
.wk-today-badge {
    display: inline-block;
    background: #6366f1;
    color: #fff;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 4px;
    margin-bottom: 10px;
    font-family: 'JetBrains Mono', monospace;
}
.wk-section {
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px solid rgba(255,255,255,0.05);
}
.wk-section-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 4px;
}
.wk-section-value {
    font-size: 13px;
    font-weight: 500;
    color: #cbd5e1;
    line-height: 1.5;
}
.wk-training {
    margin-top: 12px;
    padding: 10px 12px;
    background: rgba(52,211,153,0.06);
    border: 1px solid rgba(52,211,153,0.12);
    border-radius: 8px;
}
.wk-training-label {
    font-size: 10px;
    font-weight: 700;
    color: #34d399;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 3px;
}
.wk-training-value {
    font-size: 12px;
    color: #6ee7b7;
    line-height: 1.4;
}
</style>
""", unsafe_allow_html=True)

# Week selector
selected_week = st.slider("View week", 1, wi["plan_weeks"], week_num, key="week_sel")
w = selected_week

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

# Use 3 columns x 2 rows for bigger cards
row1 = st.columns(3)
row2 = st.columns(3)
all_cols = row1 + row2

for i, d in enumerate(days):
    with all_cols[i]:
        is_today = (d == day_name and selected_week == week_num)
        card_cls = "wk-card wk-card-today" if is_today else "wk-card wk-card-normal"
        badge = '<div class="wk-today-badge">Today</div>' if is_today else ""

        jt = JOB_BY_WEEK.get(w, {}).get(d, "—")
        at = AWS_BY_WEEK.get(w, {}).get(d, "—")
        mt = ML_BY_WEEK.get(w, {}).get(d, "—")
        pt = PRACTICE_BY_WEEK.get(w, {}).get(d, "—")
        tr = TRAINING.get(d, {})
        tr_act   = tr.get("act", "—")
        tr_dur   = tr.get("dur", "")
        tr_focus = tr.get("focus", "")

        st.markdown(f"""<div class="{card_cls}"><div class="wk-day-name">{d}</div>{badge}<div class="wk-section"><div class="wk-section-label" style="color:#fbbf24;">💼 Job hunt</div><div class="wk-section-value">{jt}</div></div><div class="wk-section"><div class="wk-section-label" style="color:#60a5fa;">☁️ AWS</div><div class="wk-section-value">{at}</div></div><div class="wk-section"><div class="wk-section-label" style="color:#f87171;">🧠 ML</div><div class="wk-section-value">{mt}</div></div><div class="wk-section"><div class="wk-section-label" style="color:#f472b6;">💻 Practice</div><div class="wk-section-value">{pt}</div></div><div class="wk-training"><div class="wk-training-label">🏋️ Training</div><div class="wk-training-value">{tr_act} · {tr_dur} · {tr_focus}</div></div></div>""", unsafe_allow_html=True)

# Sunday
st.markdown("")
st.markdown("""<div style="background:rgba(99,102,241,0.04);border:1px solid rgba(99,102,241,0.12);border-radius:14px;padding:20px 24px;display:flex;align-items:center;gap:20px;"><div style="font-size:36px;">🧘</div><div><div style="font-size:16px;font-weight:700;color:#e2e8f0;margin-bottom:4px;">Sunday — Rest & Review</div><div style="font-size:13px;color:#94a3b8;line-height:1.6;">Reflect on the week · Review all notes · Plan next week's priorities · Stretch & recharge · Light walk if you feel like it</div></div></div>""", unsafe_allow_html=True)

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
