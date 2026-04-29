import streamlit as st
import datetime
import json
from utils import load_data, save_data, get_week_info

data = load_data()
wi   = get_week_info()
today     = wi["today"]
today_str = wi["today_str"]

st.markdown('<p class="page-title">Habit Tracker</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Small habits compounded daily. Track streaks, spot patterns.</p>', unsafe_allow_html=True)

# ── Default habits seeded on first visit ─────────────────
DEFAULT_HABITS = [
    {"id": "gym",    "name": "Hit the gym",        "icon": "🏋️", "color": "#6366f1"},
    {"id": "water",  "name": "Drink 2.5 L water",   "icon": "💧", "color": "#38bdf8"},
    {"id": "study",  "name": "2h deep study",       "icon": "🧠", "color": "#a78bfa"},
    {"id": "apply",  "name": "Apply to a job",       "icon": "💼", "color": "#34d399"},
    {"id": "steps",  "name": "8 000+ steps",         "icon": "🚶", "color": "#fbbf24"},
    {"id": "code",   "name": "Write code / practice","icon": "💻", "color": "#f472b6"},
]

if "habits" not in data:
    data["habits"] = DEFAULT_HABITS
    save_data(data)
if "habit_logs" not in data:
    data["habit_logs"] = {}
    save_data(data)

habits     = data["habits"]
habit_logs = data["habit_logs"]

# ── Streak helpers ────────────────────────────────────────
def current_streak(hid):
    log = habit_logs.get(hid, {})
    streak = 0
    d = today
    while True:
        if log.get(d.isoformat()):
            streak += 1
            d -= datetime.timedelta(days=1)
        else:
            break
    return streak

def longest_streak(hid):
    log = habit_logs.get(hid, {})
    if not log:
        return 0
    dates = sorted(log.keys())
    best = cur = 0
    prev = None
    for ds in dates:
        if log[ds]:
            d = datetime.date.fromisoformat(ds)
            cur = cur + 1 if prev and (d - prev).days == 1 else 1
            best = max(best, cur)
            prev = d
        else:
            cur = 0; prev = None
    return best

def completion_rate(hid, days=30):
    log  = habit_logs.get(hid, {})
    done = sum(1 for i in range(days)
               if log.get((today - datetime.timedelta(days=i)).isoformat()))
    return round((done / days) * 100)

# ── Heatmap HTML (last 15 weeks × 7 days) ────────────────
def build_heatmap(hid, color):
    log   = habit_logs.get(hid, {})
    cells = []
    # Pad to start on Monday
    end   = today
    start = end - datetime.timedelta(days=14 * 7 + end.weekday())  # align to Monday
    d     = start
    while d <= end:
        done = log.get(d.isoformat(), False)
        future = d > today
        if future:
            bg = "rgba(255,255,255,0.03)"
        elif done:
            bg = color
        else:
            bg = "rgba(255,255,255,0.06)"
        title = d.strftime("%b %d")
        cells.append(
            f'<div title="{title}" style="width:13px;height:13px;border-radius:3px;'
            f'background:{bg};flex-shrink:0;"></div>'
        )
        d += datetime.timedelta(days=1)

    days_html = "".join(cells)
    labels = '<div style="display:flex;flex-direction:column;gap:2px;margin-right:6px;padding-top:0px;">' + \
             "".join(f'<div style="height:13px;font-size:9px;color:#475569;line-height:13px;">{l}</div>'
                     for l in ["M","T","W","T","F","S","S"]) + "</div>"

    grid = (
        '<div style="display:flex;flex-direction:column;flex-wrap:wrap;gap:2px;'
        f'height:{7*15}px;width:{15*15}px;overflow:hidden;">'
        + days_html + "</div>"
    )
    return (
        '<div style="display:flex;align-items:flex-start;gap:4px;overflow-x:auto;padding:4px 0;">'
        + labels + grid + "</div>"
    )

# ═══════════════════════════════════════════════════════════
# LAYOUT: today's check-in (left) | stats cards (right)
# ═══════════════════════════════════════════════════════════
col_log, col_stats = st.columns([2, 3])

with col_log:
    st.markdown('<div class="sec-title">Today\'s habits</div>', unsafe_allow_html=True)
    changed = False
    for h in habits:
        hid  = h["id"]
        done = habit_logs.get(hid, {}).get(today_str, False)
        key  = f"hab_{hid}"
        val  = st.checkbox(
            f"{h['icon']} {h['name']}",
            value=done,
            key=key,
        )
        if val != done:
            habit_logs.setdefault(hid, {})[today_str] = val
            changed = True

    if changed:
        data["habit_logs"] = habit_logs
        save_data(data)
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Add custom habit ──────────────────────────────────
    with st.expander("➕ Add custom habit"):
        new_name = st.text_input("Habit name", key="new_hab_name", placeholder="e.g. Meditate 10 min")
        new_icon = st.text_input("Icon (emoji)", key="new_hab_icon", value="⭐", max_chars=2)
        COLORS   = ["#6366f1","#a78bfa","#34d399","#38bdf8","#fbbf24","#f472b6","#ef4444","#fb923c"]
        new_col  = st.selectbox("Color", COLORS, key="new_hab_col",
                                format_func=lambda c: c)
        if st.button("Add habit", use_container_width=True, key="add_hab_btn"):
            if new_name.strip():
                hid = f"custom_{int(datetime.datetime.now().timestamp())}"
                data["habits"].append({"id": hid, "name": new_name.strip(),
                                       "icon": new_icon or "⭐", "color": new_col})
                save_data(data)
                st.success("Habit added!")
                st.rerun()

    # ── Remove habit ──────────────────────────────────────
    if len(habits) > 0:
        with st.expander("🗑️ Remove a habit"):
            hab_names = {h["id"]: f"{h['icon']} {h['name']}" for h in habits}
            to_remove = st.selectbox("Select habit to remove", list(hab_names.keys()),
                                     format_func=lambda x: hab_names[x], key="remove_sel")
            if st.button("Remove", use_container_width=True, key="remove_btn"):
                data["habits"] = [h for h in habits if h["id"] != to_remove]
                save_data(data)
                st.warning("Habit removed.")
                st.rerun()

with col_stats:
    st.markdown('<div class="sec-title">Streaks & consistency</div>', unsafe_allow_html=True)

    # ── Streak cards grid ─────────────────────────────────
    n = len(habits)
    rows = (n + 1) // 2
    for row in range(rows):
        c1, c2 = st.columns(2)
        for ci, h in enumerate([habits[row*2], habits[row*2+1]] if row*2+1 < n else [habits[row*2]]):
            col = c1 if ci == 0 else c2
            hid   = h["id"]
            cs    = current_streak(hid)
            ls    = longest_streak(hid)
            rate  = completion_rate(hid)
            color = h.get("color", "#6366f1")
            done_today = habit_logs.get(hid, {}).get(today_str, False)
            dot = f'<span style="color:{color};margin-right:4px;">●</span>' if done_today else '<span style="color:#334155;margin-right:4px;">○</span>'
            col.markdown(f"""
            <div class="s-card" style="text-align:left;padding:16px 18px;">
              <div style="font-size:18px;margin-bottom:4px;">{h['icon']} {dot}<span style="font-size:13px;font-weight:600;color:#cbd5e1;">{h['name']}</span></div>
              <div style="display:flex;gap:16px;margin-top:10px;">
                <div>
                  <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:1px;font-family:'JetBrains Mono',monospace;">Streak</div>
                  <div style="font-size:22px;font-weight:800;color:{color};font-family:'Outfit';">{cs}🔥</div>
                </div>
                <div>
                  <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:1px;font-family:'JetBrains Mono',monospace;">Best</div>
                  <div style="font-size:22px;font-weight:800;color:#64748b;font-family:'Outfit';">{ls}</div>
                </div>
                <div>
                  <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:1px;font-family:'JetBrains Mono',monospace;">30d %</div>
                  <div style="font-size:22px;font-weight:800;color:{"#34d399" if rate>=70 else "#fbbf24" if rate>=40 else "#ef4444"};font-family:'Outfit';">{rate}%</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HEATMAPS
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">Activity heatmaps — last 15 weeks</div>', unsafe_allow_html=True)

for h in habits:
    hid   = h["id"]
    color = h.get("color", "#6366f1")
    cs    = current_streak(hid)
    rate  = completion_rate(hid)
    heatmap_html = build_heatmap(hid, color)

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
    border-radius:14px;padding:16px 20px;margin-bottom:12px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <span style="font-size:14px;font-weight:600;color:#f1f5f9;">{h['icon']} {h['name']}</span>
        <span style="font-size:12px;color:#64748b;font-family:'JetBrains Mono',monospace;">
          {cs}🔥 streak &nbsp;·&nbsp; {rate}% last 30d
        </span>
      </div>
      {heatmap_html}
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="prime-footer">Every green square is a vote for the person you\'re becoming. 🟩</div>', unsafe_allow_html=True)
