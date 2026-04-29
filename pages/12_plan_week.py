import streamlit as st
import datetime
import json
import re
import html as _html
from utils import load_data, save_data, get_week_info

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
st.markdown('<p class="page-sub">Tell Claude your constraints — get a structured, actionable 7-day plan.</p>', unsafe_allow_html=True)

# ── Claude API ────────────────────────────────────────────
try:
    CLAUDE_KEY = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    CLAUDE_KEY = ""

if not CLAUDE_KEY:
    st.error("🔴 Add `ANTHROPIC_API_KEY` to `.streamlit/secrets.toml` to use this feature.")
    st.stop()

# ── Ensure weekly_plans exists ────────────────────────────
if "weekly_plans" not in data:
    data["weekly_plans"] = []
    save_data(data)

# ── Page tabs ─────────────────────────────────────────────
tab_gen, tab_saved = st.tabs(["✨ Generate Plan", "📚 Saved Plans"])

with tab_gen:
    st.markdown('<div class="sec-title">Your inputs</div>', unsafe_allow_html=True)

    ic1, ic2 = st.columns(2)

    with ic1:
        available_hours = st.slider("Available hours per day", 2, 16, 8, key="pw_hours")
        energy_level = st.selectbox(
            "Energy level this week",
            ["High — ready to crush it", "Medium — steady grind", "Low — recovery week"],
            key="pw_energy",
        )
        priorities_input = st.text_area(
            "Top priorities this week",
            placeholder="e.g.\n- Finish AWS certification prep\n- Apply to 5 jobs\n- Complete ML project chapter",
            height=130,
            key="pw_priorities",
        )

    with ic2:
        constraints_input = st.text_area(
            "Constraints & commitments",
            placeholder="e.g.\n- No availability Tuesday afternoon\n- Doctor on Thursday\n- Football on Monday & Thursday evening",
            height=130,
            key="pw_constraints",
        )
        focus_areas = st.multiselect(
            "Focus areas",
            ["Machine Learning", "AWS / Cloud", "Coding Practice", "Job Applications",
             "Cover Letters", "Portfolio", "Fitness", "Reading / Research", "Personal"],
            default=["Machine Learning", "AWS / Cloud", "Job Applications"],
            key="pw_focus",
        )
        week_start = st.date_input("Week starts", value=today, key="pw_start")

    st.markdown("")

    if st.button("🤖 Generate My Weekly Plan", use_container_width=True, type="primary", key="gen_plan"):
        if not priorities_input.strip():
            st.warning("Please enter at least one priority.")
        else:
            energy_map = {
                "High — ready to crush it": "high energy, push hard, schedule ambitious tasks",
                "Medium — steady grind":    "moderate energy, maintain consistent pace, avoid overloading",
                "Low — recovery week":      "low energy, protect rest, focus on light but consistent tasks",
            }
            energy_desc = energy_map.get(energy_level, "moderate energy")

            days_of_week = []
            for i in range(7):
                d = week_start + datetime.timedelta(days=i)
                days_of_week.append(d.strftime("%A %b %d"))

            prompt = f"""You are an expert productivity coach. Generate a detailed 7-day weekly plan.

USER PROFILE:
- Available: {available_hours} hours/day for focused work
- Energy level this week: {energy_desc}
- Focus areas: {', '.join(focus_areas) if focus_areas else 'General productivity'}

TOP PRIORITIES:
{priorities_input}

CONSTRAINTS:
{constraints_input if constraints_input.strip() else 'None specified'}

WEEK DATES: {', '.join(days_of_week)}

Return ONLY valid JSON, no markdown, no extra text:
{{
  "week_theme": "One motivational sentence for the week.",
  "plan": [
    {{
      "day": "Monday Apr 28",
      "theme": "Day theme in 4 words",
      "tasks": [
        {{"time": "10:00-12:00", "label": "Task label", "category": "ML", "priority": "high"}},
        {{"time": "13:00-15:00", "label": "Task label", "category": "AWS", "priority": "medium"}}
      ],
      "focus_hours": 6,
      "note": "One specific tip for this day."
    }}
  ],
  "weekly_goals": ["Goal 1", "Goal 2", "Goal 3"],
  "advice": "2-sentence motivational closing."
}}

Rules:
- Respect all constraints (skip or reduce tasks on constrained days)
- Distribute priorities across the week logically
- Sunday should be lighter (review + rest)
- Priority values: "high", "medium", "low"
- Category must be one of: ML, AWS, Practice, Jobs, Fitness, Personal, Review, Other
- Be specific and actionable, not generic"""

            with st.spinner("Claude is crafting your weekly plan…"):
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
                            "max_tokens": 3000,
                            "messages": [{"role": "user", "content": prompt}],
                        },
                        timeout=60,
                    )
                    if r.status_code == 200:
                        raw = r.json()["content"][0]["text"]
                        raw = re.sub(r"```json|```", "", raw).strip()
                        s = raw.find("{"); e = raw.rfind("}") + 1
                        plan_data = json.loads(raw[s:e])
                        st.session_state["pw_current_plan"] = plan_data
                        st.session_state["pw_plan_start"]   = week_start.isoformat()
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
border:1px solid rgba(99,102,241,0.15);border-radius:14px;padding:16px 22px;margin-bottom:24px;text-align:center;">
  <div style="font-size:16px;color:#c4b5fd;font-style:italic;font-weight:600;">"{week_theme}"</div>
</div>""", unsafe_allow_html=True)

        # Weekly goals
        weekly_goals = plan.get("weekly_goals", [])
        if weekly_goals:
            st.markdown('<div class="sec-title">🎯 This Week\'s Goals</div>', unsafe_allow_html=True)
            goals_html = "".join(
                f'<div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                f'<span style="font-size:14px;">{"🥇" if i==0 else "🥈" if i==1 else "🥉"}</span>'
                f'<span style="font-size:14px;color:#e2e8f0;font-weight:500;">{_html.escape(str(g))}</span>'
                f'</div>'
                for i, g in enumerate(weekly_goals[:3])
            )
            st.markdown(f"""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
border-radius:14px;padding:16px 20px;margin-bottom:20px;">
  {goals_html}
</div>""", unsafe_allow_html=True)

        # Day cards
        st.markdown('<div class="sec-title">📅 7-Day Schedule</div>', unsafe_allow_html=True)

        cat_colors = {
            "ML": "#f87171", "AWS": "#60a5fa", "Practice": "#f472b6",
            "Jobs": "#fbbf24", "Fitness": "#34d399", "Personal": "#a78bfa",
            "Review": "#94a3b8", "Other": "#64748b",
        }
        priority_dots = {"high": "🔴", "medium": "🟡", "low": "🟢"}

        def e(s):
            """HTML-escape a string from AI output."""
            return _html.escape(str(s)) if s else ""

        day_plan = plan.get("plan", [])
        for i in range(0, len(day_plan), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j >= len(day_plan):
                    break
                day     = day_plan[i + j]
                tasks   = day.get("tasks", [])
                note    = e(day.get("note", ""))
                theme   = e(day.get("theme", ""))
                focus_h = e(day.get("focus_hours", "—"))
                day_lbl = e(day.get("day", ""))

                tasks_html = ""
                for t in tasks:
                    cat   = e(t.get("category", "Other"))
                    c_col = cat_colors.get(t.get("category", "Other"), "#64748b")
                    pdot  = priority_dots.get(t.get("priority", "medium"), "🟡")
                    time_ = e(t.get("time", ""))
                    label = e(t.get("label", ""))
                    tasks_html += f"""
<div style="display:flex;align-items:flex-start;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
  <span style="font-size:9px;margin-top:3px;">{pdot}</span>
  <div style="flex:1;">
    <div style="font-size:12px;color:#64748b;font-family:'JetBrains Mono';">{time_}</div>
    <div style="font-size:13px;color:#e2e8f0;font-weight:500;">{label}</div>
  </div>
  <span style="font-size:10px;font-weight:700;color:{c_col};background:{c_col}18;
  padding:2px 8px;border-radius:4px;font-family:'JetBrains Mono';white-space:nowrap;">{cat}</span>
</div>"""

                with col:
                    is_today_card = (week_start + datetime.timedelta(days=i+j)).isoformat() == today_str
                    border = "border:1px solid rgba(99,102,241,0.3);" if is_today_card else "border:1px solid rgba(255,255,255,0.06);"
                    bg     = "background:rgba(99,102,241,0.05);" if is_today_card else "background:rgba(255,255,255,0.02);"
                    today_badge = '<span style="font-size:10px;font-weight:700;color:#818cf8;background:rgba(99,102,241,0.18);padding:2px 10px;border-radius:4px;font-family:JetBrains Mono;text-transform:uppercase;letter-spacing:1px;">Today</span>' if is_today_card else ""
                    theme_row   = f'<div style="font-size:11px;color:#64748b;margin-top:2px;">{theme}</div>' if theme else ""
                    note_row    = f'<div style="margin-top:10px;font-size:12px;color:#6366f1;font-style:italic;">💡 {note}</div>' if note else ""

                    st.markdown(f"""
<div style="{bg}{border}border-radius:14px;padding:16px 18px;margin-bottom:12px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
    <div>
      <span style="font-size:14px;font-weight:700;color:#f1f5f9;">{day_lbl}</span>
      {theme_row}
    </div>
    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
      {today_badge}
      <span style="font-size:11px;color:#475569;font-family:'JetBrains Mono';">{focus_h}h focus</span>
    </div>
  </div>
  {tasks_html}
  {note_row}
</div>""", unsafe_allow_html=True)

        # Advice
        advice = _html.escape(plan.get("advice", ""))
        if advice:
            st.markdown(f"""
<div style="background:rgba(16,185,129,0.05);border:1px solid rgba(16,185,129,0.15);
border-radius:14px;padding:18px 22px;margin-top:8px;">
  <div style="font-size:12px;font-weight:700;color:#6ee7b7;text-transform:uppercase;letter-spacing:1px;font-family:'JetBrains Mono';margin-bottom:8px;">🤖 Coach's Note</div>
  <div style="font-size:14px;color:#94a3b8;line-height:1.7;">{advice}</div>
</div>""", unsafe_allow_html=True)

        # Save plan
        st.markdown("")
        if st.button("💾 Save this plan", use_container_width=True, key="save_plan_btn"):
            saved_plans = data.get("weekly_plans", [])
            saved_plans.append({
                "date":       today_str,
                "week_start": st.session_state.get("pw_plan_start", today_str),
                "plan":       plan,
                "inputs": {
                    "hours":       available_hours,
                    "energy":      energy_level,
                    "priorities":  priorities_input,
                    "constraints": constraints_input,
                    "focus_areas": focus_areas,
                }
            })
            data["weekly_plans"] = saved_plans[-10:]  # Keep last 10
            save_data(data)
            st.success("Plan saved!")

with tab_saved:
    saved_plans = data.get("weekly_plans", [])
    if not saved_plans:
        st.info("No saved plans yet. Generate one in the 'Generate Plan' tab!")
    else:
        st.markdown(f'<div style="font-size:13px;color:#64748b;margin-bottom:16px;">{len(saved_plans)} plan(s) saved</div>', unsafe_allow_html=True)
        for sp in reversed(saved_plans):
            saved_date = sp.get("date", "Unknown")
            week_start_str = sp.get("week_start", saved_date)
            theme = sp.get("plan", {}).get("week_theme", "No theme")
            inputs = sp.get("inputs", {})

            with st.expander(f"📅 Week of {week_start_str} — saved {saved_date}"):
                st.markdown(f'<div style="font-style:italic;color:#94a3b8;margin-bottom:12px;">"{theme}"</div>', unsafe_allow_html=True)

                if inputs:
                    st.markdown(f"""
**Hours/day:** {inputs.get('hours', '—')} &nbsp;·&nbsp;
**Energy:** {inputs.get('energy', '—')}

**Priorities:**
{inputs.get('priorities', '—')}

**Constraints:**
{inputs.get('constraints', '—')}
""")
                day_plan = sp.get("plan", {}).get("plan", [])
                for day in day_plan:
                    tasks_list = ", ".join(t.get("label","") for t in day.get("tasks",[]))
                    st.markdown(f"**{day.get('day','')}** — {day.get('theme','')} · {tasks_list}")

st.markdown('<div class="prime-footer">A plan is not a wish. It is a commitment. 🗓️</div>', unsafe_allow_html=True)
