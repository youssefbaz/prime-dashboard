import streamlit as st
import datetime
from utils import (load_data, save_data, get_week_info, calc_streak,
                   get_daily_quote, TRAINING, CHECKLIST, SCHEDULE_TEMPLATE,
                   ML_BY_WEEK, AWS_BY_WEEK, PRACTICE_BY_WEEK, JOB_BY_WEEK,
                   PLAN_START, PLAN_END, GOAL_WEIGHT, START_WEIGHT)

data     = load_data()
wi       = get_week_info()
today    = wi["today"]
now      = wi["now"]
day_name = wi["day_name"]
week_num = wi["week_num"]
day_num  = wi["day_num"]
total_days = wi["total_days"]
has_started = wi["has_started"]
today_str   = wi["today_str"]
pct         = wi["pct"]
hour_now    = wi["hour_now"]
streak      = calc_streak(data)
is_sunday   = day_name == "Sun"

# ── Sidebar weight + note ─────────────────────────────────
ws = data.get("weights", {})
lw = ws[sorted(ws.keys(), reverse=True)[0]] if ws else None

with st.sidebar:
    st.markdown("### ⚖️ Log weight")
    wi_val = st.number_input("kg", min_value=50.0, max_value=120.0,
                             value=float(lw if lw else START_WEIGHT), step=0.1)
    if st.button("💾 Save weight", use_container_width=True):
        data.setdefault("weights", {})[today_str] = wi_val
        save_data(data); st.success(f"Saved {wi_val} kg")
    st.markdown("---")
    st.markdown("### 📝 Quick note")
    note = st.text_area("Note", value=data.get("notes", {}).get(today_str, ""),
                        height=100, label_visibility="collapsed")
    if st.button("💾 Save note", use_container_width=True):
        data.setdefault("notes", {})[today_str] = note
        save_data(data); st.success("Saved")
    st.markdown("---")
    st.markdown("### 🔗 Quick links")
    st.markdown("[📋 DS + AWS Roadmap](https://www.notion.so/1e7a7b694ee0805a877cf71c3de56f5d)")
    st.markdown("[🔁 Weekly Review](https://www.notion.so/323a7b694ee0817e8253f196589fe26c)")

# ── Helper ────────────────────────────────────────────────
def get_today_tasks():
    w = max(1, min(8, week_num))
    d = day_name
    if d == "Sun":
        return {"job":"Weekly Review","aws":"Review & Plan","ml":"Review Notes",
                "practice":"Rest","emoji":"🧘","vibe":"Rest & Review Sunday"}
    return {
        "job":      JOB_BY_WEEK.get(w, JOB_BY_WEEK[1]).get(d, "Job Hunt"),
        "aws":      AWS_BY_WEEK.get(w, AWS_BY_WEEK[1]).get(d, "AWS Study"),
        "ml":       ML_BY_WEEK.get(w, ML_BY_WEEK[1]).get(d, "ML Study"),
        "practice": PRACTICE_BY_WEEK.get(w, PRACTICE_BY_WEEK[1]).get(d, "Coding"),
        "emoji":    {"Mon":"🔥","Tue":"⚡","Wed":"🧱","Thu":"🎯","Fri":"🏁","Sat":"🚀"}.get(d,"📋"),
        "vibe":     {"Mon":"Momentum Monday","Tue":"Turbo Tuesday","Wed":"Grind Wednesday",
                     "Thu":"Target Thursday","Fri":"Focus Friday","Sat":"Ship Saturday"}.get(d,"Study Day"),
    }

tasks = get_today_tasks()

# ── Header ────────────────────────────────────────────────
if has_started:
    st.markdown(f'<div style="font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#818cf8;font-family:\'JetBrains Mono\',monospace;margin-bottom:6px;">Week {week_num} of 8 · Day {day_num} of {total_days}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="font-size:11px;font-weight:700;letter-spacing:3px;color:#818cf8;font-family:\'JetBrains Mono\',monospace;margin-bottom:6px;">Plan starts in {(PLAN_START - today).days} days</div>', unsafe_allow_html=True)

st.markdown(f'<p class="page-title">{today.strftime("%A, %B %d")}</p>', unsafe_allow_html=True)
st.markdown(f'<p class="page-sub">{tasks["emoji"]} {tasks["vibe"]} &nbsp;·&nbsp; {now.strftime("%I:%M %p")}</p>', unsafe_allow_html=True)

# ── Daily quote ───────────────────────────────────────────
quote = get_daily_quote(today)
st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(99,102,241,0.06),rgba(236,72,153,0.04));
border:1px solid rgba(99,102,241,0.12);border-radius:14px;padding:18px 24px;margin-bottom:20px;">
  <div style="font-size:15px;color:#cbd5e1;font-style:italic;line-height:1.6;">"{quote['text']}"</div>
  <div style="font-size:12px;color:#818cf8;margin-top:6px;font-family:'JetBrains Mono',monospace;">— {quote['author']}</div>
</div>
""", unsafe_allow_html=True)

# ── Missed days alert ─────────────────────────────────────
def get_missed():
    missed = []
    if not has_started: return missed
    c = PLAN_START
    while c < today:
        dn = c.strftime("%a"); ds = c.isoformat()
        if dn != "Sun" and ds not in data.get("daily_checks", {}) and ds not in data.get("missed_acks", []):
            missed.append({"label": c.strftime("%a %b %d"), "str": ds})
        c += datetime.timedelta(days=1)
    return missed

missed = get_missed()
if missed:
    st.markdown(f"""
    <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
    border-radius:14px;padding:16px 22px;margin-bottom:20px;">
      <div style="font-size:15px;font-weight:700;color:#fca5a5;">⚠️ {len(missed)} day{"s" if len(missed)>1 else ""} without check-in</div>
      <div style="font-size:13px;color:#f87171;margin-top:4px;">Complete your checklist to clear these.</div>
    </div>
    """, unsafe_allow_html=True)
    with st.expander(f"Review {len(missed)} missed day(s)"):
        cols = st.columns(min(4, len(missed)))
        for i, m in enumerate(missed[:12]):
            with cols[i % min(4, len(missed))]:
                st.markdown(f"**{m['label']}**")
                if st.button("✅ Acknowledge", key=f"ack_{m['str']}"):
                    data.setdefault("missed_acks", []).append(m["str"])
                    save_data(data); st.rerun()

# ── Stat cards ────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="s-card"><div class="s-label">Progress</div><div class="s-val" style="color:#818cf8;">{pct}%</div><div class="s-sub">Week {week_num} of 8</div></div>', unsafe_allow_html=True)
with c2:
    wd  = f"{lw:.1f}" if lw else "—"
    wc  = "#34d399" if lw and lw <= GOAL_WEIGHT else "#fbbf24" if lw else "#64748b"
    st.markdown(f'<div class="s-card"><div class="s-label">Weight</div><div class="s-val" style="color:{wc};">{wd}</div><div class="s-sub">Goal: {GOAL_WEIGHT} kg</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="s-card"><div class="s-label">Streak</div><div class="s-val" style="color:#f472b6;">{streak}</div><div class="s-sub">Consecutive days</div></div>', unsafe_allow_html=True)
with c4:
    tr = TRAINING.get(day_name, {})
    st.markdown(f'<div class="s-card"><div class="s-label">Training</div><div style="font-size:15px;font-weight:700;color:#34d399;margin:6px 0;">{tr.get("act","—")}</div><div class="s-sub">{tr.get("dur","")} — {tr.get("focus","")}</div></div>', unsafe_allow_html=True)

# ── Progress bar ──────────────────────────────────────────
tc = data.get("daily_checks", {}).get(today_str, {})
cc = sum(1 for i in range(len(CHECKLIST)) if tc.get(str(i), False))
cp = round((cc / len(CHECKLIST)) * 100)
bc = "linear-gradient(90deg,#10b981,#34d399)" if cp == 100 else "linear-gradient(90deg,#6366f1,#a78bfa)"
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;margin-top:16px;">
  <span style="font-size:12px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:1px;font-family:'JetBrains Mono',monospace;">Today's progress</span>
  <span style="font-size:14px;font-weight:700;color:{"#34d399" if cp==100 else "#818cf8"};font-family:'JetBrains Mono',monospace;">{cc}/{len(CHECKLIST)}</span>
</div>
<div class="pbar-outer"><div class="pbar-inner" style="width:{cp}%;background:{bc};"></div></div>
""", unsafe_allow_html=True)

st.markdown("")

# ── Main 2-col layout ─────────────────────────────────────
col_sched, col_check = st.columns([3, 2])

with col_sched:
    st.markdown('<div class="sec-title">Schedule</div>', unsafe_allow_html=True)
    if is_sunday:
        st.markdown('<div class="sch-active" style="border-left-color:#818cf8;"><div style="font-size:15px;color:#a5b4fc;font-weight:600;">🧘 Light day — weekly review only</div></div>', unsafe_allow_html=True)
    else:
        for b in SCHEDULE_TEMPLATE:
            active = b["h"][0] <= hour_now < b["h"][1]
            detail = tasks.get(b["cat"], "") if b["cat"] else ""
            cls    = "sch-active" if active else "sch-normal"
            nw     = '<span class="now-tag">NOW</span>' if active else ""
            dh     = f'<div style="font-size:13px;color:#94a3b8;margin-top:3px;">{detail}</div>' if detail else ""
            st.markdown(f"""
            <div class="{cls}">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <span style="font-size:13px;font-family:'JetBrains Mono',monospace;color:{"#818cf8" if active else "#475569"};font-weight:600;">{b["time"]}</span>
                  <span style="margin-left:12px;font-size:14px;font-weight:600;color:{"#f1f5f9" if active else "#cbd5e1"};">{b["label"]}</span>
                  {dh}
                </div>{nw}
              </div>
            </div>""", unsafe_allow_html=True)

with col_check:
    st.markdown('<div class="sec-title">Checklist</div>', unsafe_allow_html=True)
    for i, item in enumerate(CHECKLIST):
        st.checkbox(item, value=tc.get(str(i), False), key=f"ck_{i}")
    if cp == 100:
        st.balloons()
        st.success("🏆 All tasks completed!")
    if st.button("💾 Save progress", use_container_width=True, type="primary"):
        cks = {str(i): st.session_state.get(f"ck_{i}", False) for i in range(len(CHECKLIST))}
        data.setdefault("daily_checks", {})[today_str] = cks
        save_data(data); st.success("Progress saved! ✅")

st.markdown('<div class="prime-footer">Prime is built in silence. 🚀 Discipline = Freedom.<br><small>Small daily progress > random bursts of effort.</small></div>', unsafe_allow_html=True)
