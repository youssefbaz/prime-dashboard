import streamlit as st
import datetime
import json
import re
import html as _html
from utils import load_data, save_data, get_week_info, GOAL_COLORS, C

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

data = load_data()
wi   = get_week_info(data)
today     = wi["today"]
today_str = wi["today_str"]
week_num  = wi["week_num"]

st.markdown('<p class="page-title">Plan My Week</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Your goals drive the plan. Claude builds around what actually matters.</p>', unsafe_allow_html=True)

# ── Claude API ────────────────────────────────────────────
try:
    CLAUDE_KEY = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    CLAUDE_KEY = ""

if not CLAUDE_KEY:
    st.error("🔴 Add `ANTHROPIC_API_KEY` to `.streamlit/secrets.toml` to use this feature.")
    st.stop()

if "weekly_plans" not in data:
    data["weekly_plans"] = []
    save_data(data)

# ── Goal helpers ──────────────────────────────────────────
goals        = data.get("goals", [])
habits       = data.get("habits", [])
habit_logs   = data.get("habit_logs", {})
focus_sessions = data.get("focus_sessions", [])
jobs         = data.get("jobs", [])

def _calc_pct(g):
    am = g.get("auto_metric")
    at = g.get("auto_target") or 1
    if am == "Jobs applied":
        return min(100, round(len(jobs) / at * 100))
    if am == "Focus hours":
        mins = sum(s.get("minutes", 0) for s in focus_sessions)
        return min(100, round((mins / 60) / at * 100))
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

def _urgency(g):
    target = g.get("target_date", "")
    if not target:
        return "on_track"
    days_left = (datetime.date.fromisoformat(target) - today).days
    if days_left < 0:
        return "overdue"
    pct = _calc_pct(g)
    if days_left == 0:
        return "urgent"
    # expected progress = what % of time has elapsed
    try:
        created = g.get("created", target)
        total_span = (datetime.date.fromisoformat(target) - datetime.date.fromisoformat(created)).days
        if total_span > 0:
            elapsed = total_span - days_left
            expected = round(elapsed / total_span * 100)
            if pct < expected - 25:
                return "lagging"
    except Exception:
        pass
    if days_left <= 7:
        return "urgent"
    return "on_track"

URGENCY_COLOR = {
    "overdue":  C["danger"],
    "lagging":  C["warning"],
    "urgent":   C["sky"],
    "on_track": C["success"],
}
URGENCY_LABEL = {
    "overdue":  "Overdue",
    "lagging":  "⚠ Lagging",
    "urgent":   "Due soon",
    "on_track": "On track",
}

active_goals = [
    g for g in goals
    if not g.get("completed")
    and (not g.get("target_date") or g.get("target_date", "") >= today_str)
]

# Auto-detect focus areas from goal categories
_cat_to_focus = {
    "Learning": ["Machine Learning", "AWS / Cloud", "Coding Practice"],
    "Career":   ["Job Applications", "Cover Letters", "Portfolio"],
    "Fitness":  ["Fitness"],
    "Health":   ["Fitness"],
    "Personal": ["Personal"],
}
_auto_focus = []
for g in active_goals:
    for f in _cat_to_focus.get(g.get("category", ""), []):
        if f not in _auto_focus:
            _auto_focus.append(f)
if not _auto_focus:
    _auto_focus = ["Machine Learning", "AWS / Cloud", "Job Applications"]

# ── Page tabs ─────────────────────────────────────────────
tab_gen, tab_saved = st.tabs(["✨ Generate Plan", "📚 Saved Plans"])

with tab_gen:

    # ── Goals panel ───────────────────────────────────────
    st.markdown('<div class="sec-title">🎯 Your Active Goals</div>', unsafe_allow_html=True)

    if not active_goals:
        st.info("No active goals found. Add some in the Goals page — they'll drive your weekly plan.")
        included_goal_ids = []
    else:
        st.markdown(
            '<div style="font-size:13px;color:#64748b;margin-bottom:12px;">'
            'Select which goals to include in this week\'s plan.</div>',
            unsafe_allow_html=True)

        included_goal_ids = []
        for g in active_goals:
            gid    = g.get("id", "")
            pct    = _calc_pct(g)
            cat    = g.get("category", "Personal")
            color  = GOAL_COLORS.get(cat, C["focus_mid"])
            urg    = _urgency(g)
            urg_col = URGENCY_COLOR[urg]
            urg_lbl = URGENCY_LABEL[urg]
            target  = g.get("target_date", "")
            days_left = (datetime.date.fromisoformat(target) - today).days if target else None
            dl_txt  = f"{days_left}d left" if days_left is not None and days_left >= 0 else ("Overdue" if days_left is not None else "No deadline")

            # Milestones due (pending, within ~2 weeks)
            ms_pending = [m["text"] for m in g.get("milestones", []) if not m.get("done")]

            # Habit completions this week
            linked_hids = g.get("linked_habits", [])
            hab_map = {h["id"]: h for h in habits}
            habit_week = sum(
                1 for hid in linked_hids
                for i in range(7)
                if habit_logs.get(hid, {}).get((today - datetime.timedelta(days=i)).isoformat())
            )

            col_check, col_info = st.columns([1, 12])
            with col_check:
                include = st.checkbox("", value=True, key=f"incl_{gid}", label_visibility="collapsed")
            with col_info:
                ms_html = ""
                if ms_pending:
                    ms_items = "  ·  ".join(ms_pending[:3])
                    ms_html = (
                        f'<div style="font-size:11px;color:#64748b;margin-top:4px;">'
                        f'📋 Pending: {ms_items}{"…" if len(ms_pending)>3 else ""}</div>'
                    )
                hab_html = ""
                if linked_hids:
                    hab_html = (
                        f'<div style="font-size:11px;color:#64748b;margin-top:2px;">'
                        f'🟩 Habit completions this week: {habit_week}</div>'
                    )
                st.markdown(f"""
<div style="background:rgba(255,255,255,0.02);border:1px solid {color}20;
border-radius:12px;padding:10px 14px;margin-bottom:6px;">
  <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
    <span style="font-size:13px;font-weight:700;color:#f1f5f9;flex:1;">{g["title"]}</span>
    <span style="font-size:10px;font-weight:700;color:{color};background:{color}18;
    padding:2px 8px;border-radius:99px;font-family:'JetBrains Mono';">{cat}</span>
    <span style="font-size:10px;font-weight:700;color:{urg_col};font-family:'JetBrains Mono';">{urg_lbl}</span>
    <span style="font-size:11px;color:#475569;font-family:'JetBrains Mono';">{dl_txt}</span>
    <span style="font-size:13px;font-weight:800;color:{color};font-family:'Outfit';">{pct}%</span>
  </div>
  <div style="height:3px;background:rgba(255,255,255,0.06);border-radius:99px;
  overflow:hidden;margin:8px 0 4px;">
    <div style="width:{pct}%;height:100%;background:{color};border-radius:99px;"></div>
  </div>
  {ms_html}{hab_html}
</div>""", unsafe_allow_html=True)

            if include:
                included_goal_ids.append(gid)

    st.markdown("---")

    # ── Inputs ────────────────────────────────────────────
    st.markdown('<div class="sec-title">⚙️ Week settings</div>', unsafe_allow_html=True)
    ic1, ic2 = st.columns(2)

    with ic1:
        available_hours = st.slider("Available hours per day", 2, 16, 8, key="pw_hours")
        energy_level = st.selectbox(
            "Energy level this week",
            ["High — ready to crush it", "Medium — steady grind", "Low — recovery week"],
            key="pw_energy",
        )
        extra_priorities = st.text_area(
            "Extra context (optional)",
            placeholder="Anything not captured in your goals…\ne.g. I have a presentation on Wednesday",
            height=100,
            key="pw_priorities",
        )

    with ic2:
        constraints_input = st.text_area(
            "Constraints & commitments",
            placeholder="e.g.\n- No availability Tuesday afternoon\n- Doctor on Thursday\n- Football Mon & Thu evening",
            height=130,
            key="pw_constraints",
        )
        all_focus = [
            "Machine Learning", "AWS / Cloud", "Coding Practice", "Job Applications",
            "Cover Letters", "Portfolio", "Fitness", "Reading / Research", "Personal",
        ]
        focus_areas = st.multiselect(
            "Focus areas",
            all_focus,
            default=[f for f in _auto_focus if f in all_focus],
            key="pw_focus",
        )
        week_start = st.date_input("Week starts", value=today, key="pw_start")

    st.markdown("")

    if st.button("🤖 Generate Goal-Driven Plan", use_container_width=True, type="primary", key="gen_plan"):
        included_goals = [g for g in active_goals if g.get("id","") in included_goal_ids]

        # ── Build structured goal context ─────────────────
        goal_context_lines = []
        lagging_lines      = []

        for g in included_goals:
            pct    = _calc_pct(g)
            cat    = g.get("category", "Personal")
            target = g.get("target_date", "")
            days_left = (datetime.date.fromisoformat(target) - today).days if target else None
            urg    = _urgency(g)

            ms_pending = [m["text"] for m in g.get("milestones", []) if not m.get("done")]
            linked_hids = g.get("linked_habits", [])
            hab_map  = {h["id"]: h for h in habits}
            hab_names = [hab_map[hid]["name"] for hid in linked_hids if hid in hab_map]

            line = f"- [{cat}] \"{g['title']}\" — {pct}% complete"
            if days_left is not None:
                line += f", {days_left} days remaining"
            if linked_hids:
                line += f"\n    Linked habits: {', '.join(hab_names)}"
            if ms_pending:
                line += f"\n    Pending milestones: {', '.join(ms_pending[:4])}"
            goal_context_lines.append(line)

            if urg in ("lagging", "overdue"):
                lagging_lines.append(
                    f"- \"{g['title']}\" ({cat}, {pct}% done"
                    + (f", {days_left}d left" if days_left is not None else "")
                    + ") — needs urgent focus this week"
                )

        goal_block = (
            "GOALS TO PLAN AROUND:\n" + "\n".join(goal_context_lines)
            if goal_context_lines
            else "No specific goals selected — use general productivity principles."
        )

        lagging_block = (
            "\nURGENT / LAGGING GOALS — prioritize these:\n" + "\n".join(lagging_lines)
            if lagging_lines else ""
        )

        # ── Days list ────────────────────────────────────
        days_of_week = [
            (week_start + datetime.timedelta(days=i)).strftime("%A %b %d")
            for i in range(7)
        ]
        now = datetime.datetime.now()
        if week_start.isoformat() == today_str:
            time_ctx = (
                f"CURRENT TIME: {now.strftime('%H:%M')}. "
                f"For TODAY ({days_of_week[0]}), only schedule tasks starting from {now.strftime('%H:%M')}. "
                f"For remaining days, start from 08:00 or later."
            )
        else:
            time_ctx = (
                f"Week starts {days_of_week[0]}. Schedule each day from 08:00 or later."
            )

        energy_map = {
            "High — ready to crush it": "high energy — schedule ambitious, high-volume tasks",
            "Medium — steady grind":    "moderate energy — steady, consistent pacing",
            "Low — recovery week":      "low energy — light tasks, protect rest, minimum viable progress",
        }

        prompt = f"""You are an expert productivity coach building a goal-driven 7-day plan.

USER PROFILE:
- Available: {available_hours} hours/day for focused work
- Energy: {energy_map.get(energy_level, 'moderate')}
- Focus areas: {', '.join(focus_areas) if focus_areas else 'General'}

{goal_block}{lagging_block}

CONSTRAINTS:
{constraints_input.strip() if constraints_input.strip() else 'None specified'}

{('EXTRA CONTEXT:\n' + extra_priorities.strip()) if extra_priorities.strip() else ''}

WEEK DATES: {', '.join(days_of_week)}
{time_ctx}

INSTRUCTIONS:
- Allocate time proportional to goal urgency (lagging/overdue goals get more slots)
- Map goal milestones to specific days — don't leave them vague
- Linked habits should appear as daily tasks on relevant days
- Sunday = lighter day (review, reflect, recharge)
- Respect all constraints strictly

Return ONLY valid JSON, no markdown, no extra text:
{{
  "week_theme": "One motivational sentence for the week.",
  "plan": [
    {{
      "day": "Monday Apr 28",
      "theme": "Day theme in 4 words",
      "tasks": [
        {{"time": "10:00-12:00", "label": "Specific task", "category": "ML", "priority": "high"}},
        {{"time": "13:00-15:00", "label": "Specific task", "category": "Jobs", "priority": "medium"}}
      ],
      "focus_hours": 6,
      "note": "One specific tip for this day."
    }}
  ],
  "weekly_goals": ["Goal 1", "Goal 2", "Goal 3"],
  "advice": "2-sentence motivational closing."
}}

Rules:
- Priority: "high", "medium", "low"
- Category: ML, AWS, Practice, Jobs, Fitness, Personal, Review, Other
- Be specific (name the milestone or habit, not just "study")"""

        with st.spinner("Claude is crafting your goal-driven plan…"):
            try:
                r = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": CLAUDE_KEY,
                        "anthropic-version": "2023-06-01",
                    },
                    json={
                        "model": "claude-sonnet-4-6",
                        "max_tokens": 4096,
                        "system": (
                            "You are a productivity coach. "
                            "Always respond with valid, complete JSON only. "
                            "No markdown, no code fences, no extra text before or after the JSON object."
                        ),
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=90,
                )
                if r.status_code == 200:
                    raw = r.json()["content"][0]["text"]
                    raw = re.sub(r"```json|```", "", raw).strip()
                    s = raw.find("{"); e = raw.rfind("}") + 1
                    plan_data = json.loads(raw[s:e])
                    st.session_state["pw_current_plan"]       = plan_data
                    st.session_state["pw_plan_start"]         = week_start.isoformat()
                    st.session_state["pw_included_goal_ids"]  = included_goal_ids
                else:
                    st.error(f"API error {r.status_code}: {r.text[:200]}")
            except json.JSONDecodeError as err:
                st.error(f"Could not parse Claude's response. Try again. ({err})")
            except Exception as err:
                st.error(f"Error: {err}")

    # ── Display generated plan ─────────────────────────────
    plan = st.session_state.get("pw_current_plan")
    if plan:
        st.markdown("")

        week_theme = _html.escape(plan.get("week_theme", ""))
        if week_theme:
            st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(168,85,247,0.05));
border:1px solid rgba(99,102,241,0.15);border-radius:14px;padding:16px 22px;
margin-bottom:24px;text-align:center;">
  <div style="font-size:16px;color:#c4b5fd;font-style:italic;font-weight:600;">"{week_theme}"</div>
</div>""", unsafe_allow_html=True)

        # ── Goal coverage summary ──────────────────────────
        plan_ids = st.session_state.get("pw_included_goal_ids", [])
        plan_goals = [g for g in active_goals if g.get("id","") in plan_ids]
        if plan_goals:
            st.markdown('<div class="sec-title">🎯 Goals in This Plan</div>', unsafe_allow_html=True)
            cov_cols = st.columns(min(len(plan_goals), 3))
            for ci, g in enumerate(plan_goals[:3]):
                pct   = _calc_pct(g)
                cat   = g.get("category", "Personal")
                color = GOAL_COLORS.get(cat, C["focus_mid"])
                urg   = _urgency(g)
                urg_col = URGENCY_COLOR[urg]
                target = g.get("target_date", "")
                dl = (datetime.date.fromisoformat(target) - today).days if target else None
                dl_txt = f"{dl}d left" if dl is not None and dl >= 0 else "—"
                with cov_cols[ci]:
                    st.markdown(f"""
<div style="background:rgba(255,255,255,0.02);border:1px solid {color}22;
border-radius:12px;padding:12px 14px;margin-bottom:16px;">
  <div style="font-size:10px;font-weight:700;color:{color};text-transform:uppercase;
  letter-spacing:1px;font-family:'JetBrains Mono';margin-bottom:4px;">{cat}</div>
  <div style="font-size:13px;font-weight:700;color:#f1f5f9;margin-bottom:8px;
  line-height:1.3;">{g["title"][:36]}</div>
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
    <span style="font-size:16px;font-weight:800;color:{color};font-family:'Outfit';">{pct}%</span>
    <span style="font-size:10px;color:{urg_col};font-family:'JetBrains Mono';">
    {URGENCY_LABEL[urg]} · {dl_txt}</span>
  </div>
  <div style="height:3px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden;">
    <div style="width:{pct}%;height:100%;background:{color};border-radius:99px;"></div>
  </div>
</div>""", unsafe_allow_html=True)

        # ── Weekly goals ───────────────────────────────────
        weekly_goals = plan.get("weekly_goals", [])
        if weekly_goals:
            st.markdown('<div class="sec-title">🏁 This Week\'s Targets</div>', unsafe_allow_html=True)
            medals = ["🥇", "🥈", "🥉"]
            goals_html = "".join(
                f'<div style="display:flex;align-items:center;gap:10px;padding:8px 0;'
                f'border-bottom:1px solid rgba(255,255,255,0.04);">'
                f'<span style="font-size:14px;">{medals[i] if i < 3 else "•"}</span>'
                f'<span style="font-size:14px;color:#e2e8f0;font-weight:500;">'
                f'{_html.escape(str(g))}</span></div>'
                for i, g in enumerate(weekly_goals[:3])
            )
            st.markdown(f"""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
border-radius:14px;padding:16px 20px;margin-bottom:20px;">{goals_html}</div>""",
                unsafe_allow_html=True)

        # ── 7-day cards ────────────────────────────────────
        st.markdown('<div class="sec-title">📅 7-Day Schedule</div>', unsafe_allow_html=True)

        cat_colors = {
            "ML": "#f87171", "AWS": "#60a5fa", "Practice": "#f472b6",
            "Jobs": "#fbbf24", "Fitness": "#34d399", "Personal": "#a78bfa",
            "Review": "#94a3b8", "Other": "#64748b",
        }
        priority_dots = {"high": "🔴", "medium": "🟡", "low": "🟢"}

        def _e(s):
            return _html.escape(str(s)) if s else ""

        day_plan   = plan.get("plan", [])
        plan_start = datetime.date.fromisoformat(
            st.session_state.get("pw_plan_start", today_str))

        for i in range(0, len(day_plan), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j >= len(day_plan):
                    break
                day     = day_plan[i + j]
                tasks   = day.get("tasks", [])
                note    = _e(day.get("note", ""))
                theme   = _e(day.get("theme", ""))
                focus_h = _e(day.get("focus_hours", "—"))
                day_lbl = _e(day.get("day", ""))

                tasks_html = ""
                for t in tasks:
                    cat   = _e(t.get("category", "Other"))
                    c_col = cat_colors.get(t.get("category", "Other"), "#64748b")
                    pdot  = priority_dots.get(t.get("priority", "medium"), "🟡")
                    time_ = _e(t.get("time", ""))
                    label = _e(t.get("label", ""))
                    tasks_html += (
                        '<div style="display:flex;align-items:flex-start;gap:8px;padding:6px 0;'
                        'border-bottom:1px solid rgba(255,255,255,0.04);overflow:hidden;">'
                        f'<span style="font-size:9px;margin-top:3px;flex-shrink:0;">{pdot}</span>'
                        '<div style="flex:1;min-width:0;overflow:hidden;">'
                        f'<div style="font-size:12px;color:#64748b;font-family:\'JetBrains Mono\';">{time_}</div>'
                        f'<div style="font-size:13px;color:#e2e8f0;font-weight:500;word-break:break-word;">{label}</div>'
                        '</div>'
                        f'<span style="display:inline-block;font-size:10px;font-weight:700;'
                        f'color:{c_col};background:{c_col}18;padding:2px 6px;border-radius:4px;'
                        f'font-family:\'JetBrains Mono\';white-space:nowrap;flex-shrink:0;">{cat}</span>'
                        '</div>'
                    )

                with col:
                    card_date    = (plan_start + datetime.timedelta(days=i + j)).isoformat()
                    is_today_card = card_date == today_str
                    border = "border:1px solid rgba(99,102,241,0.3);" if is_today_card else "border:1px solid rgba(255,255,255,0.06);"
                    bg     = "background:rgba(99,102,241,0.05);" if is_today_card else "background:rgba(255,255,255,0.02);"
                    today_badge = (
                        '<span style="font-size:10px;font-weight:700;color:#818cf8;'
                        'background:rgba(99,102,241,0.18);padding:2px 10px;border-radius:4px;'
                        'font-family:JetBrains Mono;text-transform:uppercase;letter-spacing:1px;">Today</span>'
                        if is_today_card else ""
                    )
                    theme_row = f'<div style="font-size:11px;color:#64748b;margin-top:2px;">{theme}</div>' if theme else ""
                    note_row  = f'<div style="margin-top:10px;font-size:12px;color:#6366f1;font-style:italic;">💡 {note}</div>' if note else ""

                    st.markdown(
                        f'<div style="{bg}{border}border-radius:14px;padding:16px 18px;margin-bottom:12px;">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">'
                        f'<div><span style="font-size:14px;font-weight:700;color:#f1f5f9;">{day_lbl}</span>'
                        f'{theme_row}</div>'
                        f'<div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;">'
                        f'{today_badge}'
                        f'<span style="font-size:11px;color:#475569;font-family:\'JetBrains Mono\';">{focus_h}h</span>'
                        f'</div></div>'
                        f'{tasks_html}{note_row}</div>',
                        unsafe_allow_html=True)

        # ── Coach's note ───────────────────────────────────
        advice = _html.escape(plan.get("advice", ""))
        if advice:
            st.markdown(f"""
<div style="background:rgba(16,185,129,0.05);border:1px solid rgba(16,185,129,0.15);
border-radius:14px;padding:18px 22px;margin-top:8px;">
  <div style="font-size:12px;font-weight:700;color:#6ee7b7;text-transform:uppercase;
  letter-spacing:1px;font-family:'JetBrains Mono';margin-bottom:8px;">🤖 Coach's Note</div>
  <div style="font-size:14px;color:#94a3b8;line-height:1.7;">{advice}</div>
</div>""", unsafe_allow_html=True)

        # ── Save ──────────────────────────────────────────
        st.markdown("")
        if st.button("💾 Save this plan", use_container_width=True, key="save_plan_btn"):
            saved = data.get("weekly_plans", [])
            saved.append({
                "date":       today_str,
                "week_start": st.session_state.get("pw_plan_start", today_str),
                "plan":       plan,
                "goal_ids":   st.session_state.get("pw_included_goal_ids", []),
                "inputs": {
                    "hours":       available_hours,
                    "energy":      energy_level,
                    "priorities":  extra_priorities,
                    "constraints": constraints_input,
                    "focus_areas": focus_areas,
                },
            })
            data["weekly_plans"] = saved[-10:]
            save_data(data)
            st.success("Plan saved!")

# ── Saved plans tab ───────────────────────────────────────
with tab_saved:
    saved_plans = data.get("weekly_plans", [])
    if not saved_plans:
        st.info("No saved plans yet. Generate one above!")
    else:
        st.markdown(
            f'<div style="font-size:13px;color:#64748b;margin-bottom:16px;">'
            f'{len(saved_plans)} plan(s) saved</div>',
            unsafe_allow_html=True)
        for sp in reversed(saved_plans):
            saved_date     = sp.get("date", "Unknown")
            week_start_str = sp.get("week_start", saved_date)
            theme          = sp.get("plan", {}).get("week_theme", "No theme")
            inputs         = sp.get("inputs", {})
            goal_ids       = sp.get("goal_ids", [])
            plan_goals_saved = [g["title"] for g in goals if g.get("id","") in goal_ids]

            with st.expander(f"📅 Week of {week_start_str} — saved {saved_date}"):
                st.markdown(
                    f'<div style="font-style:italic;color:#94a3b8;margin-bottom:12px;">"{theme}"</div>',
                    unsafe_allow_html=True)

                if plan_goals_saved:
                    st.markdown(f"**Goals included:** {', '.join(plan_goals_saved)}")

                if inputs:
                    st.markdown(
                        f"**Hours/day:** {inputs.get('hours','—')} &nbsp;·&nbsp; "
                        f"**Energy:** {inputs.get('energy','—')}")
                    if inputs.get("priorities"):
                        st.markdown(f"**Extra context:** {inputs['priorities']}")
                    if inputs.get("constraints"):
                        st.markdown(f"**Constraints:** {inputs['constraints']}")

                day_plan = sp.get("plan", {}).get("plan", [])
                for day in day_plan:
                    tasks_list = "  ·  ".join(t.get("label", "") for t in day.get("tasks", [])[:3])
                    if len(day.get("tasks", [])) > 3:
                        tasks_list += "…"
                    st.markdown(f"**{day.get('day','')}** — {day.get('theme','')} — {tasks_list}")

st.markdown('<div class="prime-footer">A plan built on real goals is a plan worth executing. 🗓️</div>', unsafe_allow_html=True)
