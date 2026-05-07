import streamlit as st
import datetime
from utils import (load_data, save_data, get_week_info, calc_streak,
                   get_daily_quote, CHECKLIST, GOAL_WEIGHT, START_WEIGHT,
                   calc_xp, get_level, C, GOAL_COLORS, threshold_color)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

data        = load_data()
wi          = get_week_info(data)
today       = wi["today"]
now         = wi["now"]
day_name    = wi["day_name"]
week_num    = wi["week_num"]
day_num     = wi["day_num"]
total_days  = wi["total_days"]
has_started = wi["has_started"]
today_str   = wi["today_str"]
pct         = wi["pct"]
plan_start  = wi["plan_start"]
plan_weeks  = wi["plan_weeks"]
streak      = calc_streak(data)

xp = calc_xp(data)
lvl, prog, req = get_level(xp)

# ── Raw data ──────────────────────────────────────────────
goals          = data.get("goals", [])
habits         = data.get("habits", [])
habit_logs     = data.get("habit_logs", {})
focus_sessions = data.get("focus_sessions", [])
jobs           = data.get("jobs", [])
ws             = data.get("weights", {})
lw             = ws[sorted(ws.keys(), reverse=True)[0]] if ws else None

# ── Sidebar ───────────────────────────────────────────────
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
        wc = "#34d399" if diff <= 0 else "#fbbf24"
        st.markdown(f'<div style="font-size:12px;color:{wc};margin-top:4px;">Start: {START_WEIGHT} kg · Last: {lw} kg ({diff:+.1f})</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🔗 Quick links")
    st.markdown("[📋 DS + AWS Roadmap](https://www.notion.so/1e7a7b694ee0805a877cf71c3de56f5d)")
    st.markdown("[🔁 Weekly Review](https://www.notion.so/323a7b694ee0817e8253f196589fe26c)")

# ── Header ────────────────────────────────────────────────
active_count = sum(1 for g in goals
                   if not g.get("completed")
                   and (not g.get("target_date") or g.get("target_date","") >= today_str))
habits_on_track = sum(
    1 for h in habits
    if sum(1 for i in range(7)
           if habit_logs.get(h["id"],{}).get(
               (today - datetime.timedelta(days=i)).isoformat())) >= 4
)

if has_started:
    st.markdown(
        f'<div style="font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;'
        f'color:#818cf8;font-family:\'JetBrains Mono\',monospace;margin-bottom:6px;">'
        f'Week {week_num}/{plan_weeks} · Day {day_num} of {total_days}</div>',
        unsafe_allow_html=True)
else:
    st.markdown(
        f'<div style="font-size:11px;font-weight:700;letter-spacing:3px;'
        f'color:#818cf8;font-family:\'JetBrains Mono\',monospace;margin-bottom:6px;">'
        f'Plan starts in {(plan_start - today).days} days</div>',
        unsafe_allow_html=True)

st.markdown('<p class="page-title">Life OS Dashboard</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="page-sub">{active_count} active goals &nbsp;·&nbsp; '
    f'{habits_on_track}/{len(habits)} habits on track &nbsp;·&nbsp; '
    f'{now.strftime("%I:%M %p")}</p>',
    unsafe_allow_html=True)

# ── Daily quote ───────────────────────────────────────────
quote = get_daily_quote(today)
st.markdown(
    f'<div style="background:linear-gradient(135deg,rgba(99,102,241,0.06),rgba(236,72,153,0.04));'
    f'border:1px solid rgba(99,102,241,0.12);border-radius:14px;padding:18px 24px;margin-bottom:20px;">'
    f'<div style="font-size:15px;color:#cbd5e1;font-style:italic;line-height:1.6;">"{quote["text"]}"</div>'
    f'<div style="font-size:12px;color:#818cf8;margin-top:6px;font-family:\'JetBrains Mono\',monospace;">'
    f'— {quote["author"]}</div></div>',
    unsafe_allow_html=True)

# ── Missed days alert ─────────────────────────────────────
def get_missed():
    missed = []
    if not has_started:
        return missed
    c = plan_start
    while c < today:
        dn = c.strftime("%a")
        ds = c.isoformat()
        if dn != "Sun" and ds not in data.get("daily_checks", {}) and ds not in data.get("missed_acks", []):
            missed.append({"label": c.strftime("%a %b %d"), "str": ds})
        c += datetime.timedelta(days=1)
    return missed

missed = get_missed()
if missed:
    st.markdown(
        f'<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);'
        f'border-radius:14px;padding:16px 22px;margin-bottom:20px;">'
        f'<div style="font-size:15px;font-weight:700;color:#fca5a5;">⚠️ {len(missed)} day'
        f'{"s" if len(missed)>1 else ""} without check-in</div>'
        f'<div style="font-size:13px;color:#f87171;margin-top:4px;">'
        f'Complete your checklist on the Today page to clear these.</div></div>',
        unsafe_allow_html=True)
    if "show_missed_db" not in st.session_state:
        st.session_state.show_missed_db = False
    lbl = f"{'▲ Hide' if st.session_state.show_missed_db else '▼ Review'} {len(missed)} missed day(s)"
    if st.button(lbl, key="toggle_missed_db", use_container_width=True):
        st.session_state.show_missed_db = not st.session_state.show_missed_db
        st.rerun()
    if st.session_state.show_missed_db:
        if st.button(f"✅ Acknowledge all {len(missed)}", key="ack_all_db", use_container_width=True):
            data.setdefault("missed_acks", []).extend(m["str"] for m in missed)
            save_data(data)
            st.rerun()
        for m in missed:
            row_l, row_r = st.columns([3, 1])
            with row_l:
                st.markdown(
                    f'<div style="padding:10px 14px;background:rgba(255,255,255,0.02);'
                    f'border:1px solid rgba(255,255,255,0.06);border-radius:10px;'
                    f'font-size:14px;color:#cbd5e1;font-family:JetBrains Mono,monospace;">'
                    f'{m["label"]}</div>',
                    unsafe_allow_html=True)
            with row_r:
                if st.button("Acknowledge", key=f"ack_db_{m['str']}", use_container_width=True):
                    data.setdefault("missed_acks", []).append(m["str"])
                    save_data(data)
                    st.rerun()

# ── KPI strip ─────────────────────────────────────────────
st.markdown(
    f'<div class="kpi-row">'
    f'<div class="kpi-item"><span class="kpi-value" style="color:#818cf8;">{pct}%</span>'
    f'<span class="kpi-label">Plan Progress</span>'
    f'<span class="kpi-detail">Week {week_num} of {plan_weeks}</span></div>'
    f'<div class="kpi-item"><span class="kpi-value" style="color:#f472b6;">LVL {lvl}</span>'
    f'<span class="kpi-label">Experience</span>'
    f'<span class="kpi-detail">{prog}/{req} XP to next</span></div>'
    f'<div class="kpi-item"><span class="kpi-value" style="color:#34d399;">{streak}</span>'
    f'<span class="kpi-label">Day Streak</span>'
    f'<span class="kpi-detail">Consecutive check-ins</span></div>'
    f'<div class="kpi-item"><span class="kpi-value" style="color:#fbbf24;">{lw if lw else "—"}</span>'
    f'<span class="kpi-label">Weight</span>'
    f'<span class="kpi-detail">Goal: {GOAL_WEIGHT} kg</span></div>'
    f'</div>',
    unsafe_allow_html=True)

# ── Evening AI Reflection ─────────────────────────────────
if now.hour >= 20:
    st.markdown('<div class="sec-title">🌙 Coach\'s Evening Reflection</div>', unsafe_allow_html=True)
    if f"reflection_{today_str}" not in st.session_state:
        _key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not _key:
            st.info("Add `ANTHROPIC_API_KEY` to `.streamlit/secrets.toml` to unlock Evening Reflection.")
        else:
            tc_ref = data.get("daily_checks", {}).get(today_str, {})
            done_count  = sum(1 for v in tc_ref.values() if v)
            today_focus = sum(s.get("minutes", 0) for s in focus_sessions if s.get("date") == today_str)
            prompt = (
                f"You are 'Prime Coach'. End-of-day debrief.\n"
                f"Tasks completed: {done_count}/{len(CHECKLIST)}. "
                f"Focus: {today_focus}min. Streak: {streak} days. Active goals: {active_count}.\n"
                f"Write 3 sentences: acknowledge effort, one specific tip, powerful close for tomorrow. "
                f"Concise, elite, slightly stoic."
            )
            if st.button("Generate Tonight's Reflection", use_container_width=True):
                try:
                    r = requests.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={"Content-Type": "application/json",
                                 "x-api-key": _key, "anthropic-version": "2023-06-01"},
                        json={"model": "claude-haiku-4-5-20251001", "max_tokens": 200,
                              "messages": [{"role": "user", "content": prompt}]},
                        timeout=15)
                    if r.status_code == 200:
                        st.session_state[f"reflection_{today_str}"] = r.json()["content"][0]["text"]
                        st.rerun()
                    else:
                        st.error(f"Coach unavailable. (Error {r.status_code})")
                except Exception:
                    st.error("Could not reach the coach.")
    if f"reflection_{today_str}" in st.session_state:
        st.markdown(
            f'<div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.15);'
            f'border-radius:16px;padding:24px;margin-bottom:20px;">'
            f'<div style="font-size:15px;color:#cbd5e1;font-style:italic;line-height:1.7;">'
            f'"{st.session_state[f"reflection_{today_str}"]}"</div></div>',
            unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# LIFE OS — 4-AREA KPI BOARD
# ══════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">⚡ Life Areas</div>', unsafe_allow_html=True)

# ── Compute all area metrics ──────────────────────────────
week_start = today - datetime.timedelta(days=today.weekday())

# Study
total_focus_h = sum(s.get("minutes", 0) for s in focus_sessions) / 60
week_focus_h  = sum(s.get("minutes", 0) for s in focus_sessions
                    if s.get("date", "") >= week_start.isoformat()) / 60
flash_count   = len(data.get("flash_scores", {}))
quiz_count    = len(data.get("quiz_history", {}))

# Career
total_jobs  = len(jobs)
week_jobs   = sum(1 for j in jobs
                  if j.get("date", j.get("applied", "")) >= week_start.isoformat())
cover_count = len(data.get("cover_letters", []))

# Health
def _streak(hid):
    log = habit_logs.get(hid, {})
    s = 0
    d = today
    while log.get(d.isoformat()):
        s += 1
        d -= datetime.timedelta(days=1)
    return s

best_streak_val = max((_streak(h["id"]) for h in habits), default=0)
habits_today    = sum(1 for h in habits if habit_logs.get(h["id"], {}).get(today_str, False))
gym_id = next(
    (h["id"] for h in habits
     if "gym" in h.get("id", "").lower() or "gym" in h.get("name", "").lower()),
    None)
gym_week = sum(
    1 for i in range(7)
    if gym_id and habit_logs.get(gym_id, {}).get((today - datetime.timedelta(days=i)).isoformat())
) if gym_id else 0
weight_diff = round(lw - START_WEIGHT, 1) if lw else None
weight_txt  = (f"{lw} kg ({weight_diff:+.1f})" if weight_diff is not None else (f"{lw} kg" if lw else "—"))

# Personal
def _rate30(hid):
    return sum(1 for i in range(30)
               if habit_logs.get(hid, {}).get((today - datetime.timedelta(days=i)).isoformat()))

overall_rate = round(
    sum(_rate30(h["id"]) for h in habits) / max(len(habits) * 30, 1) * 100
) if habits else 0
habits_this_week = sum(
    sum(1 for i in range(7)
        if habit_logs.get(h["id"], {}).get((today - datetime.timedelta(days=i)).isoformat()))
    for h in habits
)

# ── Goal helpers ──────────────────────────────────────────
def _goal_pct(g):
    am = g.get("auto_metric")
    at = g.get("auto_target") or 1
    if am == "Jobs applied":
        return min(100, round(total_jobs / at * 100))
    if am == "Focus hours":
        return min(100, round(total_focus_h / at * 100))
    if am == "Habit completions":
        linked = g.get("linked_habits", [])
        if linked:
            total_c = sum(
                sum(1 for v in habit_logs.get(hid, {}).values() if v)
                for hid in linked
            )
            return min(100, round(total_c / at * 100))
    ms = g.get("milestones", [])
    if ms:
        return round(sum(1 for m in ms if m.get("done")) / len(ms) * 100)
    return g.get("progress", 0)

def _goals_for(cats):
    return [g for g in goals
            if g.get("category") in cats
            and not g.get("completed")
            and (not g.get("target_date") or g.get("target_date", "") >= today_str)]

def _goal_rows_html(area_goals, color):
    if not area_goals:
        return (
            '<div style="font-size:12px;color:#2d3748;text-align:center;'
            'padding:14px 0;font-style:italic;">'
            'No active goals — add one in Goals →</div>'
        )
    html = ""
    for g in area_goals[:3]:
        p      = _goal_pct(g)
        target = g.get("target_date", "")
        dl     = (datetime.date.fromisoformat(target) - today).days if target else None
        dl_txt = f"{dl}d" if dl is not None and dl >= 0 else "—"
        dl_col = "#ef4444" if dl is not None and dl < 7 else "#64748b"
        html += (
            f'<div style="margin-bottom:10px;">'
            f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">'
            f'<span style="font-size:12px;color:#cbd5e1;font-weight:600;flex:1;overflow:hidden;'
            f'text-overflow:ellipsis;white-space:nowrap;min-width:0;">{g["title"][:34]}</span>'
            f'<span style="font-size:10px;font-family:\'JetBrains Mono\';color:{dl_col};flex-shrink:0;">{dl_txt}</span>'
            f'<span style="font-size:13px;font-weight:800;color:{color};flex-shrink:0;font-family:\'Outfit\';">{p}%</span>'
            f'</div>'
            f'<div style="height:4px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden;">'
            f'<div style="width:{p}%;height:100%;background:{color};border-radius:99px;"></div>'
            f'</div></div>'
        )
    return html

def _stat_rows_html(stats):
    return "".join(
        f'<div style="display:flex;justify-content:space-between;padding:5px 0;'
        f'border-bottom:1px solid rgba(255,255,255,0.04);">'
        f'<span style="font-size:12px;color:#64748b;">{s[0]}</span>'
        f'<span style="font-size:12px;font-weight:600;color:#94a3b8;'
        f'font-family:\'JetBrains Mono\';">{s[1]}</span></div>'
        for s in stats
    )

# ── 4 area columns ────────────────────────────────────────
a1, a2, a3, a4 = st.columns(4, gap="small")

AREAS = [
    {
        "col": a1, "icon": "🧠", "title": "STUDY", "color": C["focus_mid"],
        "headline": f"{total_focus_h:.0f}h", "hl_label": "Total focus time",
        "stats": [
            ("This week", f"{week_focus_h:.1f}h"),
            ("Flashcards reviewed", str(flash_count)),
            ("Quiz sessions", str(quiz_count)),
        ],
        "cats": ["Learning"],
    },
    {
        "col": a2, "icon": "💼", "title": "CAREER", "color": C["warning"],
        "headline": str(total_jobs), "hl_label": "Jobs applied",
        "stats": [
            ("This week", str(week_jobs)),
            ("Cover letters", str(cover_count)),
        ],
        "cats": ["Career"],
    },
    {
        "col": a3, "icon": "💪", "title": "HEALTH", "color": C["success"],
        "headline": f"{best_streak_val}🔥", "hl_label": "Best habit streak",
        "stats": [
            ("Habits today", f"{habits_today}/{len(habits)}"),
            ("Gym this week", str(gym_week)),
            ("Weight", weight_txt),
        ],
        "cats": ["Fitness", "Health"],
    },
    {
        "col": a4, "icon": "⭐", "title": "PERSONAL", "color": C["pink"],
        "headline": f"{overall_rate}%", "hl_label": "30-day habit rate",
        "stats": [
            ("Habits this week", str(habits_this_week)),
            ("Habits today", f"{habits_today}/{len(habits)}"),
        ],
        "cats": ["Personal"],
    },
]

for area in AREAS:
    area_goals = _goals_for(area["cats"])
    goal_count = len(area_goals)
    color      = area["color"]
    stats_html = _stat_rows_html(area["stats"])
    goals_html = _goal_rows_html(area_goals, color)

    with area["col"]:
        st.markdown(f"""
<div style="background:rgba(255,255,255,0.02);border:1px solid {color}22;
border-radius:18px;padding:18px 16px;">

  <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
    <span style="font-size:20px;">{area["icon"]}</span>
    <span style="font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;
    color:{color};font-family:'JetBrains Mono';">{area["title"]}</span>
    <span style="margin-left:auto;font-size:10px;color:#2d3748;font-family:'JetBrains Mono';">
    {goal_count} goal{"s" if goal_count != 1 else ""}</span>
  </div>

  <div style="margin-bottom:16px;">
    <div style="font-size:30px;font-weight:900;color:{color};font-family:'Outfit';line-height:1;">
      {area["headline"]}</div>
    <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:1px;
    font-family:'JetBrains Mono';margin-top:4px;">{area["hl_label"]}</div>
  </div>

  <div style="margin-bottom:16px;">{stats_html}</div>

  <div style="border-top:1px solid rgba(255,255,255,0.05);padding-top:14px;">
    {goals_html}
  </div>

</div>""", unsafe_allow_html=True)

# ── Recent activity feed ──────────────────────────────────
st.markdown('<div class="sec-title">🕐 Recent Activity</div>', unsafe_allow_html=True)

activity = []

for j in sorted(jobs, key=lambda x: x.get("date", x.get("applied", "")), reverse=True)[:4]:
    d = j.get("date", j.get("applied", ""))
    activity.append({
        "date": d, "icon": "💼",
        "text": f"Applied to <b>{j.get('company','?')}</b> — {j.get('role','Role')}",
        "color": C["warning"],
    })

for s in sorted(focus_sessions, key=lambda x: x.get("date", ""), reverse=True)[:4]:
    activity.append({
        "date": s.get("date", ""), "icon": "⏱️",
        "text": f"<b>{s.get('minutes', 0)}min</b> focus session — {s.get('topic', 'Study')}",
        "color": C["focus_mid"],
    })

for d_str in sorted(ws.keys(), reverse=True)[:3]:
    activity.append({
        "date": d_str, "icon": "⚖️",
        "text": f"Weight logged: <b>{ws[d_str]} kg</b>",
        "color": C["success"],
    })

for g in goals:
    if g.get("completed") and g.get("target_date", "") >= (today - datetime.timedelta(days=30)).isoformat():
        activity.append({
            "date": g.get("target_date", ""), "icon": "🎯",
            "text": f"Goal completed: <b>{g['title'][:40]}</b>",
            "color": C["pink"],
        })

activity = sorted(activity, key=lambda x: x["date"], reverse=True)[:8]

if activity:
    feed_html = ""
    for a in activity:
        d = a["date"]
        try:
            dt    = datetime.date.fromisoformat(d)
            label = ("Today" if dt == today
                     else "Yesterday" if dt == today - datetime.timedelta(days=1)
                     else dt.strftime("%b %d"))
        except Exception:
            label = d or "—"
        feed_html += (
            f'<div style="display:flex;align-items:center;gap:12px;padding:10px 0;'
            f'border-bottom:1px solid rgba(255,255,255,0.04);">'
            f'<div style="width:32px;height:32px;border-radius:8px;'
            f'background:{a["color"]}18;display:flex;align-items:center;'
            f'justify-content:center;font-size:15px;flex-shrink:0;">{a["icon"]}</div>'
            f'<div style="flex:1;font-size:13px;color:#94a3b8;line-height:1.4;">{a["text"]}</div>'
            f'<div style="font-size:11px;color:#334155;font-family:\'JetBrains Mono\';'
            f'flex-shrink:0;">{label}</div>'
            f'</div>'
        )
    st.markdown(
        f'<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);'
        f'border-radius:16px;padding:4px 20px;">{feed_html}</div>',
        unsafe_allow_html=True)
else:
    st.markdown(
        '<div style="text-align:center;padding:40px;color:#334155;font-size:14px;">'
        'No activity yet — start logging focus sessions, jobs, and weight to see your feed.</div>',
        unsafe_allow_html=True)

st.markdown(
    '<div class="prime-footer">Life OS · All areas. One system. 🚀</div>',
    unsafe_allow_html=True)
