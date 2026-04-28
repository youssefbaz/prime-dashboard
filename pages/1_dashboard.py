import streamlit as st
import datetime
from utils import (load_data, save_data, get_week_info, calc_streak,
                   get_daily_quote, TRAINING, CHECKLIST, SCHEDULE_TEMPLATE,
                   ML_BY_WEEK, AWS_BY_WEEK, PRACTICE_BY_WEEK, JOB_BY_WEEK,
                   GOAL_WEIGHT, START_WEIGHT, calc_xp, get_level)

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

# ── Stat cards ────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="s-card"><div class="s-label">Progress</div><div class="s-val" style="color:#818cf8;">{pct}%</div><div class="s-sub">Week {week_num} of 8</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="s-card"><div class="s-label">Experience</div><div class="s-val" style="color:#f472b6;">LVL {lvl}</div><div class="s-sub">{prog}/{req} XP to next</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="s-card"><div class="s-label">Streak</div><div class="s-val" style="color:#34d399;">{streak}</div><div class="s-sub">Consecutive days</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="s-card"><div class="s-label">Weight</div><div class="s-val" style="color:#fbbf24;">{lw if lw else "—"}</div><div class="s-sub">Goal: {GOAL_WEIGHT} kg</div></div>', unsafe_allow_html=True)

# ── AI Daily Reflection (After 8 PM) ──────────────────────
if now.hour >= 20:
    st.markdown('<div class="sec-title">🌙 Coach\'s Evening Reflection</div>', unsafe_allow_html=True)
    
    # Check if reflection already generated today
    if f"reflection_{today_str}" not in st.session_state:
        # Prepare data for Gemini
        tc = data.get("daily_checks", {}).get(today_str, {})
        done_count = sum(1 for v in tc.values() if v)
        focus_ss = data.get("focus_sessions", [])
        today_focus = sum(s.get("minutes",0) for s in focus_ss if s.get("date") == today_str)
        
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
                GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "")
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
                if r.status_code == 200:
                    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                    st.session_state[f"reflection_{today_str}"] = text
                    st.rerun()
                else:
                    st.error(f"Coach is busy. (Error {r.status_code})")
            except:
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
        st.markdown('<div class="sch-active" style="border-left-color:#818cf8;"><div style="font-size:15px;color:#a5b4fc;font-weight:600;">🧘 Light day — weekly review only</div></div>', unsafe_allow_html=True)
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
