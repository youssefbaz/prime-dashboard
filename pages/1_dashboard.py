import streamlit as st
import datetime
from utils import (load_data, save_data, get_week_info, calc_streak,
                   get_daily_quote, TRAINING, CHECKLIST, SCHEDULE_TEMPLATE,
                   ML_BY_WEEK, AWS_BY_WEEK, PRACTICE_BY_WEEK, JOB_BY_WEEK,
                   GOAL_WEIGHT, START_WEIGHT, calc_xp, get_level,
                   C, GOAL_COLORS, threshold_color)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

data     = load_data()
wi       = get_week_info(data)
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
plan_start  = wi["plan_start"]
plan_weeks  = wi["plan_weeks"]
streak      = calc_streak(data)
is_sunday   = day_name == "Sun"

# Gamification stats
xp = calc_xp(data)
lvl, prog, req = get_level(xp)

# ── Sidebar quick links (lightweight — keeps nav visible) ─
ws = data.get("weights", {})
lw = ws[sorted(ws.keys(), reverse=True)[0]] if ws else None

with st.sidebar:
    st.markdown("### ⚖️ Log weight")
    w_input = st.number_input("Weight (kg)", min_value=40.0, max_value=200.0,
                              value=float(lw if lw else START_WEIGHT), step=0.1,
                              key="weight_input")
    if st.button("Save weight", use_container_width=True, key="save_weight"):
        data.setdefault("weights", {})[today_str] = round(w_input, 1)
        save_data(data)
        st.success(f"Logged {w_input:.1f} kg")
        st.rerun()
    if lw:
        diff = round(lw - START_WEIGHT, 1)
        color = "#34d399" if diff <= 0 else "#fbbf24"
        st.markdown(f'<div style="font-size:12px;color:{color};margin-top:4px;">Start: {START_WEIGHT} kg · Last: {lw} kg ({diff:+.1f})</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔗 Quick links")
    st.markdown("[📋 DS + AWS Roadmap](https://www.notion.so/1e7a7b694ee0805a877cf71c3de56f5d)")
    st.markdown("[🔁 Weekly Review](https://www.notion.so/323a7b694ee0817e8253f196589fe26c)")

# ── Helper ────────────────────────────────────────────────
def get_today_tasks():
    w = max(1, min(plan_weeks, week_num))
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
    st.markdown(f'<div style="font-size:11px;font-weight:700;letter-spacing:3px;color:#818cf8;font-family:\'JetBrains Mono\',monospace;margin-bottom:6px;">Plan starts in {(plan_start - today).days} days</div>', unsafe_allow_html=True)

st.markdown(f'<p class="page-title">{today.strftime("%A, %B %d")}</p>', unsafe_allow_html=True)
st.markdown(f'<p class="page-sub">{tasks["emoji"]} {tasks["vibe"]} &nbsp;·&nbsp; {now.strftime("%I:%M %p")}</p>', unsafe_allow_html=True)

# ── Daily quote ───────────────────────────────────────────
quote = get_daily_quote(today)
st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(99,102,241,0.06),rgba(236,72,153,0.04));border:1px solid rgba(99,102,241,0.12);border-radius:14px;padding:18px 24px;margin-bottom:20px;"><div style="font-size:15px;color:#cbd5e1;font-style:italic;line-height:1.6;">"{quote['text']}"</div><div style="font-size:12px;color:#818cf8;margin-top:6px;font-family:'JetBrains Mono',monospace;">— {quote['author']}</div></div>""", unsafe_allow_html=True)

# ── Missed days alert ─────────────────────────────────────
def get_missed():
    missed = []
    if not has_started: return missed
    c = plan_start
    while c < today:
        dn = c.strftime("%a"); ds = c.isoformat()
        if dn != "Sun" and ds not in data.get("daily_checks", {}) and ds not in data.get("missed_acks", []):
            missed.append({"label": c.strftime("%a %b %d"), "str": ds})
        c += datetime.timedelta(days=1)
    return missed

missed = get_missed()
if missed:
    st.markdown(f"""<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:14px;padding:16px 22px;margin-bottom:20px;"><div style="font-size:15px;font-weight:700;color:#fca5a5;">⚠️ {len(missed)} day{"s" if len(missed)>1 else ""} without check-in</div><div style="font-size:13px;color:#f87171;margin-top:4px;">Complete your checklist to clear these.</div></div>""", unsafe_allow_html=True)
    if "show_missed" not in st.session_state:
        st.session_state.show_missed = False
    toggle_label = f"{'▲ Hide' if st.session_state.show_missed else '▼ Review'} {len(missed)} missed day(s)"
    if st.button(toggle_label, key="toggle_missed", use_container_width=True):
        st.session_state.show_missed = not st.session_state.show_missed
        st.rerun()
    if st.session_state.show_missed:
        if st.button(f"✅ Acknowledge all {len(missed)}", key="ack_all", use_container_width=True):
            data.setdefault("missed_acks", []).extend(m["str"] for m in missed)
            save_data(data); st.rerun()
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        for m in missed:
            row_l, row_r = st.columns([3, 1])
            with row_l:
                st.markdown(
                    f'<div style="padding:10px 14px;background:rgba(255,255,255,0.02);'
                    f'border:1px solid rgba(255,255,255,0.06);border-radius:10px;'
                    f'font-size:14px;color:#cbd5e1;font-family:JetBrains Mono,monospace;">'
                    f'{m["label"]}</div>',
                    unsafe_allow_html=True,
                )
            with row_r:
                if st.button("Acknowledge", key=f"ack_{m['str']}", use_container_width=True):
                    data.setdefault("missed_acks", []).append(m["str"])
                    save_data(data); st.rerun()

# ── KPI strip ─────────────────────────────────────────────
st.markdown(f"""<div class="kpi-row">
  <div class="kpi-item">
    <span class="kpi-value" style="color:#818cf8;">{pct}%</span>
    <span class="kpi-label">Progress</span>
    <span class="kpi-detail">Week {week_num} of 8</span>
  </div>
  <div class="kpi-item">
    <span class="kpi-value" style="color:#f472b6;">LVL {lvl}</span>
    <span class="kpi-label">Experience</span>
    <span class="kpi-detail">{prog}/{req} XP to next</span>
  </div>
  <div class="kpi-item">
    <span class="kpi-value" style="color:#34d399;">{streak}</span>
    <span class="kpi-label">Streak</span>
    <span class="kpi-detail">Consecutive days</span>
  </div>
  <div class="kpi-item">
    <span class="kpi-value" style="color:#fbbf24;">{lw if lw else '—'}</span>
    <span class="kpi-label">Weight</span>
    <span class="kpi-detail">Goal: {GOAL_WEIGHT} kg</span>
  </div>
</div>""", unsafe_allow_html=True)

# ── AI Daily Reflection (After 8 PM) ──────────────────────
if now.hour >= 20:
    st.markdown('<div class="sec-title">🌙 Coach\'s Evening Reflection</div>', unsafe_allow_html=True)
    
    # Check if reflection already generated today
    if f"reflection_{today_str}" not in st.session_state:
        _reflection_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not _reflection_key:
            st.info("Add `ANTHROPIC_API_KEY` to `.streamlit/secrets.toml` to unlock Evening Reflection.")
        else:
            _tc_ref = data.get("daily_checks", {}).get(today_str, {})
            done_count  = sum(1 for v in _tc_ref.values() if v)
            _focus_ref  = data.get("focus_sessions", [])
            today_focus = sum(s.get("minutes", 0) for s in _focus_ref if s.get("date") == today_str)

            prompt = f"""You are 'Prime Coach', a high-performance mentor. It's the end of the day.
Summary of today:
- Tasks completed: {done_count} out of {len(CHECKLIST)}
- Focus time: {today_focus} minutes
- Vibe: {tasks['vibe']}

Write a 3-sentence motivational debrief.
1st sentence: Acknowledge the effort (be direct).
2nd sentence: One specific piece of advice based on the progress.
3rd sentence: A powerful closing for tomorrow.
Be concise, elite, and slightly stoic."""

            if st.button("Generate Today's Reflection", use_container_width=True):
                try:
                    r = requests.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "Content-Type": "application/json",
                            "x-api-key": _reflection_key,
                            "anthropic-version": "2023-06-01",
                        },
                        json={
                            "model": "claude-haiku-4-5-20251001",
                            "max_tokens": 200,
                            "messages": [{"role": "user", "content": prompt}],
                        },
                        timeout=15,
                    )
                    if r.status_code == 200:
                        text = r.json()["content"][0]["text"]
                        st.session_state[f"reflection_{today_str}"] = text
                        st.rerun()
                    else:
                        st.error(f"Coach is busy. (Error {r.status_code})")
                except Exception:
                    st.error("Could not reach the coach.")
    
    if f"reflection_{today_str}" in st.session_state:
        st.markdown(f"""
        <div style="background:rgba(99,102,241,0.06); border:1px solid rgba(99,102,241,0.15); border-radius:16px; padding:24px; margin-bottom:30px;">
            <div style="font-size:15px; color:#cbd5e1; font-style:italic; line-height:1.7;">"{st.session_state[f"reflection_{today_str}"]}"</div>
        </div>
        """, unsafe_allow_html=True)

# ── Progress bar ──────────────────────────────────────────
tc = data.get("daily_checks", {}).get(today_str, {})
cc = sum(1 for i in range(len(CHECKLIST)) if tc.get(str(i), False))
cp = round((cc / len(CHECKLIST)) * 100)
bc = "linear-gradient(90deg,#10b981,#34d399)" if cp == 100 else "linear-gradient(90deg,#6366f1,#a78bfa)"
st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;margin-top:16px;"><span style="font-size:12px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:1px;font-family:'JetBrains Mono',monospace;">Today's progress</span><span style="font-size:14px;font-weight:700;color:{"#34d399" if cp==100 else "#818cf8"};font-family:'JetBrains Mono',monospace;">{cc}/{len(CHECKLIST)}</span></div><div class="pbar-outer"><div class="pbar-inner" style="width:{cp}%;background:{bc};"></div></div>""", unsafe_allow_html=True)

st.markdown("")

# ── Main 2-col layout ─────────────────────────────────────
col_sched, col_check = st.columns([3, 2])

with col_sched:
    st.markdown('<div class="sec-title">Schedule</div>', unsafe_allow_html=True)
    if is_sunday:
        st.markdown('<div class="sch-active"><div style="font-size:15px;color:#a5b4fc;font-weight:600;">🧘 Light day — weekly review only</div></div>', unsafe_allow_html=True)
    else:
        # Build training info for gym block
        tr_info = TRAINING.get(day_name, {})
        gym_detail = f'{tr_info.get("act","")} — {tr_info.get("focus","")} ({tr_info.get("dur","")})' if tr_info else ""

        for b in SCHEDULE_TEMPLATE:
            active = b["h"][0] <= hour_now < b["h"][1]
            cat = b["cat"]

            # Build rich detail for EVERY block
            if cat:
                detail = tasks.get(cat, "")
            elif "Gym" in b["label"]:
                detail = gym_detail
            elif "Lunch" in b["label"]:
                detail = "Eat within meal plan · Hydrate"
            elif "Nap" in b["label"]:
                detail = "Power nap · No screens"
            elif "Pre-gym" in b["label"]:
                detail = "Warm up · Get ready"
            elif "Break" in b["label"]:
                detail = "Stretch · Hydrate · Reset"
            elif "Review" in b["label"]:
                detail = "Review notes · GitHub commit · Plan tomorrow"
            else:
                detail = ""

            cls = "sch-active" if active else "sch-normal"
            time_color = "#818cf8" if active else "#475569"
            label_color = "#f1f5f9" if active else "#cbd5e1"

            now_badge = ""
            if active:
                now_badge = '<span class="now-tag">NOW</span>'

            detail_html = ""
            if detail:
                detail_html = f'<div style="font-size:12px;color:#94a3b8;margin-top:4px;line-height:1.4;">{detail}</div>'

            html = (
                f'<div class="{cls}">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                f'<div style="flex:1;">'
                f'<span style="font-size:13px;font-family:\'JetBrains Mono\',monospace;color:{time_color};font-weight:600;">{b["time"]}</span>'
                f'<span style="margin-left:12px;font-size:14px;font-weight:600;color:{label_color};">{b["label"]}</span>'
                f'{detail_html}'
                f'</div>'
                f'{now_badge}'
                f'</div>'
                f'</div>'
            )
            st.markdown(html, unsafe_allow_html=True)

with col_check:
    st.markdown('<div class="sec-title">Checklist</div>', unsafe_allow_html=True)

    def _autosave_checks():
        cks = {str(i): st.session_state.get(f"ck_{i}", False) for i in range(len(CHECKLIST))}
        _d = load_data()
        _d.setdefault("daily_checks", {})[today_str] = cks
        save_data(_d)

    for i, item in enumerate(CHECKLIST):
        st.checkbox(item, value=tc.get(str(i), False), key=f"ck_{i}", on_change=_autosave_checks)
    if cp == 100:
        st.balloons()
        st.success("🏆 All tasks completed!")

# ── Pinned goals (from Goals page) ───────────────────────
pinned_goals = [g for g in data.get("goals", []) if g.get("pinned") and not g.get("completed")]
if pinned_goals:
    st.markdown('<div class="sec-title">📌 Pinned Goals</div>', unsafe_allow_html=True)
    for g in pinned_goals[:3]:
        milestones = g.get("milestones", [])
        if milestones:
            pct = round(sum(1 for m in milestones if m.get("done")) / len(milestones) * 100)
        else:
            pct = g.get("progress", 0)
        color  = GOAL_COLORS.get(g.get("category","Personal"), C["focus_mid"])
        target = g.get("target_date","")
        today_d = datetime.date.today()
        days_left = (datetime.date.fromisoformat(target) - today_d).days if target else None
        days_txt = f"{days_left}d left" if days_left is not None and days_left >= 0 else ("Due today!" if days_left == 0 else "Overdue")
        days_col = threshold_color(days_left if days_left is not None else -1, 7, 1, higher_is_better=False)
        st.markdown(f"""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:12px 18px;margin-bottom:8px;">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div>
      <span class="truncate" style="font-size:14px;font-weight:600;color:#e2e8f0;max-width:220px;display:inline-block;">{g['title']}</span>
      <span style="margin-left:10px;font-size:11px;color:{color};background:{color}15;padding:2px 8px;border-radius:4px;font-family:'JetBrains Mono';">{g.get('category','')}</span>
    </div>
    <div style="display:flex;gap:14px;align-items:center;">
      <span style="font-size:12px;color:{days_col};font-family:'JetBrains Mono';">{days_txt}</span>
      <span style="font-size:13px;font-weight:700;color:{color};">{pct}%</span>
    </div>
  </div>
  <div class="pbar-outer" style="margin:8px 0 0;height:4px;">
    <div class="pbar-inner" style="width:{pct}%;background:{color};"></div>
  </div>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="prime-footer">Prime is built in silence. 🚀 Discipline = Freedom.<br><small>Small daily progress > random bursts of effort.</small></div>', unsafe_allow_html=True)
