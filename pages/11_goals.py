import streamlit as st
import datetime
from utils import load_data, save_data, get_week_info

data = load_data()
wi   = get_week_info(data)
today     = wi["today"]
today_str = wi["today_str"]

st.markdown('<p class="page-title">Goals</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Define what matters. Track every step. Pin your top 3 to the Dashboard.</p>', unsafe_allow_html=True)

# ── Extra CSS ─────────────────────────────────────────────
st.markdown("""
<style>
.goal-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 18px 22px;
    margin-bottom: 12px;
    transition: all 0.25s ease;
}
.goal-card:hover { border-color: rgba(99,102,241,0.25); background: rgba(255,255,255,0.035); }
.goal-card-pinned {
    background: rgba(99,102,241,0.05);
    border: 1px solid rgba(99,102,241,0.22);
}
.goal-card-completed {
    opacity: 0.55;
    background: rgba(52,211,153,0.03);
    border: 1px solid rgba(52,211,153,0.1);
}
.goal-card-overdue {
    background: rgba(239,68,68,0.04);
    border: 1px solid rgba(239,68,68,0.15);
}
.milestone-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 13px;
    color: #94a3b8;
}
.milestone-done { text-decoration: line-through; color: #475569; }
</style>
""", unsafe_allow_html=True)

# ── Ensure goals key exists ────────────────────────────────
if "goals" not in data:
    data["goals"] = []
    save_data(data)

goals = data["goals"]

CAT_COLORS = {
    "Career":   "#fbbf24",
    "Fitness":  "#34d399",
    "Learning": "#818cf8",
    "Personal": "#f472b6",
}
CAT_ICONS = {
    "Career": "💼", "Fitness": "💪", "Learning": "🧠", "Personal": "⭐",
}
STATUS_ORDER = {"Active": 0, "Completed": 1, "Overdue": 2}

def goal_status(g):
    if g.get("completed"):
        return "Completed"
    target = g.get("target_date", "")
    if target and target < today_str:
        return "Overdue"
    return "Active"

def calc_progress(g):
    """Progress: milestone-based if milestones exist, else manual pct."""
    milestones = g.get("milestones", [])
    if milestones:
        done = sum(1 for m in milestones if m.get("done"))
        return round(done / len(milestones) * 100) if milestones else 0
    return g.get("progress", 0)

# ── Summary stats ─────────────────────────────────────────
active_goals    = [g for g in goals if goal_status(g) == "Active"]
completed_goals = [g for g in goals if goal_status(g) == "Completed"]
overdue_goals   = [g for g in goals if goal_status(g) == "Overdue"]
pinned_goals    = [g for g in goals if g.get("pinned")]

sc1, sc2, sc3, sc4 = st.columns(4)
with sc1:
    st.markdown(f'<div class="s-card"><div class="s-label">Active</div><div class="s-val" style="color:#818cf8;">{len(active_goals)}</div></div>', unsafe_allow_html=True)
with sc2:
    st.markdown(f'<div class="s-card"><div class="s-label">Completed</div><div class="s-val" style="color:#34d399;">{len(completed_goals)}</div></div>', unsafe_allow_html=True)
with sc3:
    st.markdown(f'<div class="s-card"><div class="s-label">Overdue</div><div class="s-val" style="color:#ef4444;">{len(overdue_goals)}</div></div>', unsafe_allow_html=True)
with sc4:
    st.markdown(f'<div class="s-card"><div class="s-label">Pinned</div><div class="s-val" style="color:#fbbf24;">{len(pinned_goals)}/3</div></div>', unsafe_allow_html=True)

st.markdown("")

# ── Add new goal ──────────────────────────────────────────
with st.expander("➕ Create new goal", expanded=len(goals) == 0):
    with st.form("new_goal_form", clear_on_submit=True):
        fc1, fc2 = st.columns(2)
        with fc1:
            g_title    = st.text_input("Goal title", placeholder="e.g. Land a Data Scientist role")
            g_category = st.selectbox("Category", ["Career", "Fitness", "Learning", "Personal"])
        with fc2:
            g_target   = st.date_input("Target date", value=today + datetime.timedelta(days=30))
            g_progress = st.slider("Initial progress (%)", 0, 100, 0, key="new_g_pct")

        g_milestones_raw = st.text_area(
            "Milestones (one per line, optional)",
            placeholder="Apply to 20 jobs\nGet first interview\nPass technical round",
            height=100,
        )

        if st.form_submit_button("🎯 Add goal", use_container_width=True):
            if g_title.strip():
                milestones = []
                if g_milestones_raw.strip():
                    milestones = [
                        {"text": line.strip(), "done": False}
                        for line in g_milestones_raw.strip().splitlines()
                        if line.strip()
                    ]
                new_goal = {
                    "id":          f"goal_{int(datetime.datetime.now().timestamp())}",
                    "title":       g_title.strip(),
                    "category":    g_category,
                    "target_date": g_target.isoformat(),
                    "progress":    g_progress,
                    "milestones":  milestones,
                    "completed":   False,
                    "pinned":      False,
                    "created":     today_str,
                }
                data["goals"].append(new_goal)
                save_data(data)
                st.success(f"Goal '{g_title}' created!")
                st.rerun()
            else:
                st.warning("Please enter a goal title.")

st.markdown("")

# ── Render goals by status ────────────────────────────────
def render_goal_section(section_goals, section_title):
    if not section_goals:
        return
    st.markdown(f'<div class="sec-title">{section_title}</div>', unsafe_allow_html=True)

    for g in section_goals:
        gid    = g.get("id", "")
        cat    = g.get("category", "Personal")
        status = goal_status(g)
        pct    = calc_progress(g)
        color  = CAT_COLORS.get(cat, "#818cf8")
        icon   = CAT_ICONS.get(cat, "⭐")
        target = g.get("target_date", "")
        pinned = g.get("pinned", False)
        days_left = (datetime.date.fromisoformat(target) - today).days if target else None

        # Card class
        if status == "Completed":
            card_cls = "goal-card goal-card-completed"
        elif status == "Overdue":
            card_cls = "goal-card goal-card-overdue"
        elif pinned:
            card_cls = "goal-card goal-card-pinned"
        else:
            card_cls = "goal-card"

        # Progress bar color
        bar_color = "#34d399" if pct >= 100 else (color if status == "Active" else "#475569")

        # Days remaining label
        if days_left is not None:
            if status == "Completed":
                days_txt = "✓ Completed"
                days_col = "#34d399"
            elif days_left < 0:
                days_txt = f"⚠️ {abs(days_left)}d overdue"
                days_col = "#ef4444"
            elif days_left == 0:
                days_txt = "Due today!"
                days_col = "#fbbf24"
            else:
                days_txt = f"{days_left}d remaining"
                days_col = "#64748b"
        else:
            days_txt, days_col = "No deadline", "#475569"

        pin_indicator = ' 📌' if pinned else ''

        st.markdown(f"""
<div class="{card_cls}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
    <div style="flex:1;">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
        <span style="font-size:16px;">{icon}</span>
        <span style="font-size:15px;font-weight:700;color:#f1f5f9;">{g["title"]}{pin_indicator}</span>
      </div>
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        <span style="font-size:11px;font-weight:700;color:{color};background:{color}15;
        padding:2px 10px;border-radius:99px;font-family:'JetBrains Mono';">{cat}</span>
        <span style="font-size:12px;color:{days_col};font-family:'JetBrains Mono';">{days_txt}</span>
        <span style="font-size:12px;color:#475569;">📅 {target}</span>
      </div>
    </div>
    <div style="font-size:20px;font-weight:800;color:{bar_color};font-family:'Outfit';min-width:50px;text-align:right;">{pct}%</div>
  </div>
  <div class="pbar-outer" style="margin:8px 0;">
    <div class="pbar-inner" style="width:{pct}%;background:{bar_color};"></div>
  </div>
</div>
""", unsafe_allow_html=True)

        # Milestone checklist
        milestones = g.get("milestones", [])
        if milestones:
            with st.expander(f"📋 Milestones ({sum(1 for m in milestones if m.get('done'))}/{len(milestones)} done)", expanded=False):
                changed = False
                for mi, m in enumerate(milestones):
                    val = st.checkbox(m["text"], value=m.get("done", False),
                                      key=f"ms_{gid}_{mi}")
                    if val != m.get("done", False):
                        g["milestones"][mi]["done"] = val
                        changed = True
                if changed:
                    # Update progress based on milestones
                    done_count = sum(1 for m in milestones if m.get("done"))
                    g["progress"] = round(done_count / len(milestones) * 100)
                    save_data(data)
                    st.rerun()
        elif status == "Active":
            # Manual progress slider
            new_pct = st.slider(f"Progress for '{g['title'][:30]}'", 0, 100, pct,
                                key=f"pct_{gid}")
            if new_pct != pct:
                g["progress"] = new_pct
                save_data(data)
                st.rerun()

        # Action buttons
        ac1, ac2, ac3, ac4 = st.columns(4)
        with ac1:
            pin_label = "📌 Unpin" if pinned else "📌 Pin"
            if st.button(pin_label, key=f"pin_{gid}", use_container_width=True):
                current_pinned = sum(1 for gg in goals if gg.get("pinned"))
                if not pinned and current_pinned >= 3:
                    st.warning("Max 3 pinned goals. Unpin one first.")
                else:
                    g["pinned"] = not pinned
                    save_data(data)
                    st.rerun()
        with ac2:
            if status != "Completed":
                if st.button("✅ Complete", key=f"done_{gid}", use_container_width=True):
                    g["completed"] = True
                    g["progress"]  = 100
                    g["pinned"]    = False
                    save_data(data)
                    st.rerun()
            else:
                if st.button("↩ Reopen", key=f"reopen_{gid}", use_container_width=True):
                    g["completed"] = False
                    save_data(data)
                    st.rerun()
        with ac3:
            st.write("")  # spacer
        with ac4:
            if st.button("🗑️ Delete", key=f"del_{gid}", use_container_width=True):
                data["goals"] = [gg for gg in goals if gg.get("id") != gid]
                save_data(data)
                st.rerun()

        st.markdown("")

# Sort and render
active_sorted   = sorted(active_goals,    key=lambda g: (not g.get("pinned"), g.get("target_date", "")))
overdue_sorted  = sorted(overdue_goals,   key=lambda g: g.get("target_date", ""))
complete_sorted = sorted(completed_goals, key=lambda g: g.get("target_date", ""), reverse=True)

render_goal_section(active_sorted,   "🎯 Active Goals")
render_goal_section(overdue_sorted,  "⚠️ Overdue Goals")
render_goal_section(complete_sorted, "✅ Completed Goals")

if not goals:
    st.markdown("""
<div style="text-align:center;padding:60px 20px;color:#475569;">
  <div style="font-size:48px;margin-bottom:16px;">🎯</div>
  <div style="font-size:18px;font-weight:600;color:#64748b;margin-bottom:8px;">No goals yet</div>
  <div style="font-size:14px;">Click "Create new goal" above to get started.</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="prime-footer">Goals without deadlines are just wishes. Set the date. Do the work. 🎯</div>', unsafe_allow_html=True)
