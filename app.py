import streamlit as st
import datetime
import json
import os
import pandas as pd

# ─────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────
PLAN_START = datetime.date(2026, 3, 23)
PLAN_END = datetime.date(2026, 5, 18)
GOAL_WEIGHT = 75.0
START_WEIGHT = 86.5

st.set_page_config(
    page_title="Prime Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────
# PERSISTENCE
# ─────────────────────────────────────────────────────────
DATA_FILE = "prime_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"daily_checks": {}, "weights": {}, "notes": {}, "missed_acks": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()

# ─────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────
WEEKLY_TASKS = {
    "Mon": {"emoji": "🔥", "vibe": "Momentum Monday", "job": "Resume Tailoring", "aws": "IAM & Security", "ml": "Linear Regression", "practice": "LeetCode – Arrays"},
    "Tue": {"emoji": "⚡", "vibe": "Turbo Tuesday", "job": "LinkedIn Networking", "aws": "S3 & Storage", "ml": "Logistic Regression", "practice": "SQL Queries"},
    "Wed": {"emoji": "🧱", "vibe": "Grind Wednesday", "job": "Cover Letter Writing", "aws": "EC2 & Compute", "ml": "Decision Trees", "practice": "Pandas"},
    "Thu": {"emoji": "🎯", "vibe": "Target Thursday", "job": "Referrals & DMs", "aws": "Lambda & API Gateway", "ml": "NLP Basics", "practice": "Regex & Strings"},
    "Fri": {"emoji": "🏁", "vibe": "Focus Friday", "job": "Mock Interview Prep", "aws": "VPC & Networking", "ml": "Model Evaluation", "practice": "Data Structures"},
    "Sat": {"emoji": "🚀", "vibe": "Ship Saturday", "job": "Portfolio Building", "aws": "SageMaker & MLOps", "ml": "Random Forests", "practice": "Build LLM App"},
    "Sun": {"emoji": "🧘", "vibe": "Rest & Review Sunday", "job": "Weekly Review", "aws": "CloudWatch & Monitoring", "ml": "Hyperparameter Tuning", "practice": "Fine-tune LLM on Colab"},
}

SCHEDULE = [
    {"time": "10:00 – 11:00", "label": "💼 Job hunt", "cat": "job", "h": (10, 11)},
    {"time": "11:00 – 13:00", "label": "☁️ AWS deep dive", "cat": "aws", "h": (11, 13)},
    {"time": "13:00 – 13:30", "label": "🏃 Pre-gym prep", "cat": None, "h": (13, 13.5)},
    {"time": "13:30 – 14:30", "label": "🏋️ Gym workout", "cat": None, "h": (13.5, 14.5)},
    {"time": "14:30 – 15:00", "label": "🍽️ Lunch", "cat": None, "h": (14.5, 15)},
    {"time": "15:00 – 15:30", "label": "💤 Nap", "cat": None, "h": (15, 15.5)},
    {"time": "15:30 – 17:30", "label": "🧠 ML deep dive", "cat": "ml", "h": (15.5, 17.5)},
    {"time": "17:30 – 17:45", "label": "☕ Break", "cat": None, "h": (17.5, 17.75)},
    {"time": "17:45 – 19:15", "label": "💻 Practice", "cat": "practice", "h": (17.75, 19.25)},
    {"time": "19:15 – 19:45", "label": "📓 Review & journal", "cat": None, "h": (19.25, 19.75)},
]

MEALS = [
    {"time": "9:30 AM", "name": "Breakfast", "icon": "🍳", "desc": "2 eggs + cheese + pain de mie + coffee + fruit", "kcal": "400–500"},
    {"time": "1:00 PM", "name": "Lunch", "icon": "🍲", "desc": "Protein + carbs + veggies + olive oil", "kcal": "500–600"},
    {"time": "7:00 PM", "name": "Dinner", "icon": "🥗", "desc": "Light protein + veggies/salad", "kcal": "400–500"},
    {"time": "10:00 PM", "name": "Snack", "icon": "🍎", "desc": "Greek yogurt + berries OR fruit + nuts", "kcal": "200–250"},
]

CHECKLIST = [
    "Applied to 1–2 jobs",
    "Completed 2h AWS study + lab",
    "Went to gym 🏋️",
    "Completed 2h ML learning + notebook",
    "Practiced coding / LLM project (1.5h)",
    "Review + GitHub commit",
    "Drank 2.5L water 💧",
    "Ate within meal plan",
    "Hit 8,000+ steps",
]

TRAINING = {
    "Mon": {"act": "⚽ Football", "dur": "2h", "focus": "Cardio + team play"},
    "Tue": {"act": "🏋️ Gym – Push", "dur": "1h", "focus": "Chest & triceps"},
    "Wed": {"act": "🚶 Walk / Core", "dur": "45 min", "focus": "Active recovery"},
    "Thu": {"act": "⚽ Football", "dur": "2h", "focus": "Endurance"},
    "Fri": {"act": "🏋️ Gym – Pull", "dur": "1h", "focus": "Back & biceps"},
    "Sat": {"act": "🏋️ Full Body", "dur": "1h", "focus": "Strength & burn"},
    "Sun": {"act": "🧘 Stretch", "dur": "—", "focus": "Recovery"},
}

# ─────────────────────────────────────────────────────────
# DARK PREMIUM STYLES
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

.stApp {
    background: linear-gradient(145deg, #0a0a0f 0%, #111127 50%, #0d1117 100%) !important;
    font-family: 'Outfit', sans-serif !important;
}
[data-testid="stSidebar"] { background: #0d0d18 !important; border-right: 1px solid rgba(255,255,255,0.06) !important; }
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { max-width: 1100px !important; padding-top: 2rem !important; }
h1,h2,h3,h4,h5,h6 { font-family: 'Outfit', sans-serif !important; color: #f1f5f9 !important; }
p, span, label, div { font-family: 'Outfit', sans-serif !important; }

.stTabs [data-baseweb="tab-list"] { gap: 4px; background: transparent; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 8px; }
.stTabs [data-baseweb="tab"] { background: transparent !important; border: none !important; border-radius: 8px !important; padding: 8px 18px !important; font-family: 'Outfit', sans-serif !important; font-weight: 500 !important; font-size: 14px !important; color: #94a3b8 !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { background: rgba(99,102,241,0.12) !important; color: #a5b4fc !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

.stCheckbox { margin-bottom: 2px !important; }
.stCheckbox label { color: #e2e8f0 !important; font-size: 14px !important; }

.stButton > button { background: linear-gradient(135deg, #6366f1, #7c3aed) !important; color: #fff !important; border: none !important; border-radius: 10px !important; font-family: 'Outfit', sans-serif !important; font-weight: 600 !important; padding: 10px 24px !important; }
.stButton > button:hover { background: linear-gradient(135deg, #7c3aed, #6366f1) !important; }

.stNumberInput input, .stTextArea textarea { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 8px !important; color: #f1f5f9 !important; }

.stSuccess > div { background: rgba(16,185,129,0.1) !important; border: 1px solid rgba(16,185,129,0.2) !important; border-radius: 10px !important; color: #6ee7b7 !important; }

.hdr-badge { font-size: 11px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: #818cf8; font-family: 'JetBrains Mono', monospace; margin-bottom: 6px; }
.hdr-date { font-size: clamp(26px,5vw,38px); font-weight: 800; background: linear-gradient(135deg, #f8fafc 0%, #a5b4fc 50%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2; margin: 0; font-family: 'Outfit', sans-serif; }
.hdr-vibe { font-size: 15px; color: #94a3b8; margin-top: 6px; }
.hdr-vibe .tm { font-size: 13px; color: #475569; font-family: 'JetBrains Mono', monospace; margin-left: 14px; }

.s-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 18px; text-align: center; }
.s-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; color: #64748b; font-family: 'JetBrains Mono', monospace; margin-bottom: 6px; }
.s-val { font-size: 28px; font-weight: 800; font-family: 'JetBrains Mono', monospace; line-height: 1.2; }
.s-sub { font-size: 12px; color: #475569; margin-top: 4px; }

.alert-box { background: linear-gradient(135deg, rgba(239,68,68,0.10) 0%, rgba(239,68,68,0.04) 100%); border: 1px solid rgba(239,68,68,0.2); border-radius: 14px; padding: 18px 22px; margin-bottom: 20px; }

.sch-active { background: rgba(99,102,241,0.06); border: 1px solid rgba(99,102,241,0.25); border-left: 4px solid #6366f1; border-radius: 14px; padding: 16px 20px; margin-bottom: 10px; }
.sch-normal { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 16px 20px; margin-bottom: 10px; }

.now-tag { display: inline-block; font-size: 10px; font-weight: 800; letter-spacing: 2px; color: #818cf8; background: rgba(99,102,241,0.12); padding: 3px 12px; border-radius: 6px; text-transform: uppercase; font-family: 'JetBrains Mono', monospace; }

.meal-c { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 20px; text-align: center; }

.wk-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 14px; text-align: center; min-height: 200px; }
.wk-today { background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.25); }

.td-badge { display: inline-block; background: #6366f1; color: #fff; font-size: 9px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; padding: 2px 8px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; }

.lk-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 18px 22px; margin-bottom: 10px; display: block; text-decoration: none !important; transition: all 0.2s; }
.lk-card:hover { border-color: rgba(99,102,241,0.3); background: rgba(99,102,241,0.04); }

.pbar-outer { height: 8px; background: rgba(255,255,255,0.04); border-radius: 99px; overflow: hidden; margin: 10px 0 20px; }
.pbar-inner { height: 100%; border-radius: 99px; transition: width 0.5s cubic-bezier(0.4,0,0.2,1); }

.prime-footer { text-align: center; color: #334155; font-size: 14px; padding: 32px 0 16px; border-top: 1px solid rgba(255,255,255,0.04); margin-top: 40px; }
.prime-footer small { font-size: 12px; color: #1e293b; display: block; margin-top: 4px; }

.sec-title { font-size: 18px; font-weight: 700; color: #f1f5f9; margin-bottom: 14px; font-family: 'Outfit', sans-serif; }

.glow-a { position: fixed; top: -200px; right: -200px; width: 600px; height: 600px; background: radial-gradient(circle, rgba(99,102,241,0.06) 0%, transparent 70%); pointer-events: none; z-index: 0; }
.glow-b { position: fixed; bottom: -200px; left: -100px; width: 500px; height: 500px; background: radial-gradient(circle, rgba(236,72,153,0.04) 0%, transparent 70%); pointer-events: none; z-index: 0; }
</style>
<div class="glow-a"></div><div class="glow-b"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────
today = datetime.date.today()
now = datetime.datetime.now()
day_name = today.strftime("%a")
day_num = (today - PLAN_START).days + 1
week_num = max(1, (day_num - 1) // 7 + 1)
total_days = (PLAN_END - PLAN_START).days
has_started = today >= PLAN_START
tasks_today = WEEKLY_TASKS.get(day_name, WEEKLY_TASKS["Mon"])
is_sunday = day_name == "Sun"
today_str = today.isoformat()
hour_now = now.hour + now.minute / 60
pct = min(100, max(0, round((day_num / total_days) * 100))) if total_days > 0 else 0

def is_current(b): return b["h"][0] <= hour_now < b["h"][1]

def get_missed():
    missed = []
    if not has_started: return missed
    c = PLAN_START
    while c < today:
        dn = c.strftime("%a")
        ds = c.isoformat()
        if dn != "Sun" and ds not in data.get("daily_checks", {}) and ds not in data.get("missed_acks", []):
            missed.append({"date": c, "day_name": dn, "str": ds, "label": c.strftime("%a %b %d")})
        c += datetime.timedelta(days=1)
    return missed

streak = 0
cd = today - datetime.timedelta(days=1)
while cd >= PLAN_START:
    ds = cd.isoformat()
    if cd.strftime("%a") == "Sun" or ds in data.get("daily_checks", {}):
        streak += 1; cd -= datetime.timedelta(days=1)
    else: break

# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗂️ Quick links")
    st.markdown("[📋 DS + AWS Roadmap](https://www.notion.so/1e7a7b694ee0805a877cf71c3de56f5d)")
    st.markdown("[🥗 Nutrition System](https://www.notion.so/2a6a7b694ee080f6af92d59df04b63eb)")
    st.markdown("[🔁 Weekly Review](https://www.notion.so/323a7b694ee0817e8253f196589fe26c)")
    st.markdown("---")
    st.markdown("### ⚖️ Log weight")
    wi = st.number_input("kg", min_value=50.0, max_value=120.0, value=START_WEIGHT, step=0.1)
    if st.button("💾 Save weight", use_container_width=True):
        data.setdefault("weights", {})[today_str] = wi
        save_data(data); st.success(f"Saved {wi} kg")
    st.markdown("---")
    st.markdown("### 📝 Note")
    note = st.text_area("", value=data.get("notes", {}).get(today_str, ""), height=100, label_visibility="collapsed")
    if st.button("💾 Save note", use_container_width=True):
        data.setdefault("notes", {})[today_str] = note
        save_data(data); st.success("Saved")

# ─────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────
if has_started:
    st.markdown(f'<div class="hdr-badge">Week {week_num} · Day {day_num} of {total_days}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="hdr-badge">Plan starts in {(PLAN_START - today).days} days</div>', unsafe_allow_html=True)

st.markdown(f'<p class="hdr-date">{today.strftime("%A, %B %d, %Y")}</p>', unsafe_allow_html=True)
st.markdown(f'<p class="hdr-vibe">{tasks_today["emoji"]} {tasks_today["vibe"]}<span class="tm">{now.strftime("%I:%M %p")}</span></p>', unsafe_allow_html=True)
st.markdown("")

# MISSED ALERT
missed = get_missed()
if missed:
    st.markdown(f"""<div class="alert-box">
        <div style="font-size:15px;font-weight:700;color:#fca5a5;">⚠️ {len(missed)} day{"s" if len(missed)>1 else ""} without check-in</div>
        <div style="font-size:13px;color:#f87171;opacity:0.8;margin-top:4px;">You haven't completed your checklist for these days.</div>
    </div>""", unsafe_allow_html=True)
    with st.expander(f"🔍 Review {len(missed)} missed day(s)"):
        cs = st.columns(min(4, max(1, len(missed))))
        for i, m in enumerate(missed):
            with cs[i % min(4, max(1, len(missed)))]:
                st.markdown(f"**{m['label']}** — {WEEKLY_TASKS[m['day_name']]['vibe']}")
                if st.button("✅ Ack", key=f"a_{m['str']}"):
                    data.setdefault("missed_acks", []).append(m["str"])
                    save_data(data); st.rerun()

# STATS
st.markdown("")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="s-card"><div class="s-label">Progress</div><div class="s-val" style="color:#818cf8;">{pct}%</div><div class="s-sub">Week {week_num} of 8</div></div>', unsafe_allow_html=True)

ws = data.get("weights", {})
lw = ws[sorted(ws.keys(), reverse=True)[0]] if ws else None
with c2:
    wd = f"{lw:.1f}" if lw else "—"
    wc = "#34d399" if lw and lw <= GOAL_WEIGHT else "#fbbf24" if lw else "#64748b"
    st.markdown(f'<div class="s-card"><div class="s-label">Weight</div><div class="s-val" style="color:{wc};">{wd}</div><div class="s-sub">Goal: {GOAL_WEIGHT} kg</div></div>', unsafe_allow_html=True)

with c3:
    st.markdown(f'<div class="s-card"><div class="s-label">Streak</div><div class="s-val" style="color:#f472b6;">{streak}</div><div class="s-sub">Consecutive days</div></div>', unsafe_allow_html=True)

tr = TRAINING.get(day_name, {})
with c4:
    st.markdown(f'<div class="s-card"><div class="s-label">Training</div><div style="font-size:16px;font-weight:700;color:#34d399;margin:6px 0;">{tr.get("act","—")}</div><div class="s-sub">{tr.get("dur","")} — {tr.get("focus","")}</div></div>', unsafe_allow_html=True)

# PROGRESS BAR
tc = data.get("daily_checks", {}).get(today_str, {})
cc = sum(1 for i in range(len(CHECKLIST)) if tc.get(str(i), False))
cp = round((cc / len(CHECKLIST)) * 100)
bc = "linear-gradient(90deg,#10b981,#34d399)" if cp == 100 else "linear-gradient(90deg,#6366f1,#a78bfa)"
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;">
    <span style="font-size:12px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:1px;font-family:'JetBrains Mono',monospace;">Today's progress</span>
    <span style="font-size:14px;font-weight:700;color:{'#34d399' if cp==100 else '#818cf8'};font-family:'JetBrains Mono',monospace;">{cc}/{len(CHECKLIST)}</span>
</div>
<div class="pbar-outer"><div class="pbar-inner" style="width:{cp}%;background:{bc};"></div></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📋 Today", "📅 Week", "🍽️ Meals", "🔗 Links"])

with tab1:
    cl, cr = st.columns([3, 2])
    with cl:
        st.markdown('<div class="sec-title">Schedule</div>', unsafe_allow_html=True)
        if is_sunday:
            st.markdown('<div class="sch-active" style="border-left-color:#818cf8;"><div style="font-size:15px;color:#a5b4fc;font-weight:600;">🧘 Light day — weekly review only</div><div style="font-size:13px;color:#818cf8;margin-top:4px;">Plan next week, rest, and recharge.</div></div>', unsafe_allow_html=True)
        else:
            for b in SCHEDULE:
                a = is_current(b)
                d = tasks_today.get(b["cat"], "") if b["cat"] else ""
                cls = "sch-active" if a else "sch-normal"
                nw = '<span class="now-tag">NOW</span>' if a else ""
                dh = f'<div style="font-size:13px;color:#94a3b8;margin-top:3px;">{d}</div>' if d else ""
                st.markdown(f'<div class="{cls}"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span style="font-size:13px;font-family:\'JetBrains Mono\',monospace;color:{"#818cf8" if a else "#475569"};font-weight:600;">{b["time"]}</span><span style="margin-left:12px;font-size:14px;font-weight:600;color:{"#f1f5f9" if a else "#cbd5e1"};">{b["label"]}</span>{dh}</div>{nw}</div></div>', unsafe_allow_html=True)

    with cr:
        st.markdown('<div class="sec-title">Checklist</div>', unsafe_allow_html=True)
        for i, item in enumerate(CHECKLIST):
            st.checkbox(item, value=tc.get(str(i), False), key=f"ck_{i}")
        if cp == 100:
            st.balloons()
            st.success("🏆 All tasks completed! You crushed it!")
        if st.button("💾 Save progress", use_container_width=True, type="primary"):
            cks = {str(i): st.session_state.get(f"ck_{i}", False) for i in range(len(CHECKLIST))}
            data.setdefault("daily_checks", {})[today_str] = cks
            save_data(data); st.success("Progress saved! ✅")

with tab2:
    st.markdown('<div class="sec-title">Weekly overview</div>', unsafe_allow_html=True)
    wcs = st.columns(7)
    for i, d in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
        with wcs[i]:
            t = WEEKLY_TASKS[d]
            it = d == day_name
            cls = "wk-card wk-today" if it else "wk-card"
            tb = '<div class="td-badge" style="margin:6px 0;">TODAY</div>' if it else ""
            if d == "Sun":
                st.markdown(f'<div class="{cls}"><div style="font-size:20px;margin-bottom:4px;">{t["emoji"]}</div><div style="font-size:14px;font-weight:700;color:#e2e8f0;">{d}</div>{tb}<div style="color:#64748b;font-size:12px;margin-top:8px;">Rest day<br>Weekly Review</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="{cls}"><div style="font-size:20px;margin-bottom:4px;">{t["emoji"]}</div><div style="font-size:14px;font-weight:700;color:#e2e8f0;">{d}</div>{tb}<div style="text-align:left;margin-top:8px;font-size:12px;line-height:1.7;"><div style="color:#fbbf24;">💼 {t["job"]}</div><div style="color:#60a5fa;">☁️ {t["aws"]}</div><div style="color:#f87171;">🧠 {t["ml"]}</div><div style="color:#f472b6;">💻 {t["practice"]}</div></div></div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="sec-title">Daily meals</div>', unsafe_allow_html=True)
    mcs = st.columns(4)
    for i, m in enumerate(MEALS):
        with mcs[i]:
            st.markdown(f'<div class="meal-c"><div style="font-size:28px;margin-bottom:8px;">{m["icon"]}</div><div style="font-weight:700;color:#e2e8f0;font-size:15px;">{m["name"]}</div><div style="color:#818cf8;font-size:12px;font-weight:600;margin:6px 0;font-family:\'JetBrains Mono\',monospace;">{m["time"]} · {m["kcal"]} kcal</div><div style="color:#64748b;font-size:13px;line-height:1.5;">{m["desc"]}</div></div>', unsafe_allow_html=True)
    
    st.markdown(""); st.markdown('<div class="sec-title">Daily targets</div>', unsafe_allow_html=True)
    tcs = st.columns(4)
    for col, (lb, vl, sb, co) in zip(tcs, [("Calories","1,500–1,850","kcal/day","#818cf8"),("Protein","130–150g","per day","#34d399"),("Water","2.5L","minimum","#60a5fa"),("Last meal","Before 23:00","eating window","#fbbf24")]):
        with col:
            st.markdown(f'<div class="s-card"><div class="s-label">{lb}</div><div style="font-size:18px;font-weight:700;color:{co};margin:6px 0;font-family:\'JetBrains Mono\',monospace;">{vl}</div><div class="s-sub">{sb}</div></div>', unsafe_allow_html=True)

    if ws:
        st.markdown(""); st.markdown('<div class="sec-title">Weight progress</div>', unsafe_allow_html=True)
        wd = [(datetime.date.fromisoformat(d), w) for d, w in sorted(ws.items())]
        df = pd.DataFrame(wd, columns=["Date", "Weight (kg)"]).set_index("Date")
        st.line_chart(df, use_container_width=True, color="#818cf8")
        if len(wd) >= 2:
            lo = wd[0][1] - wd[-1][1]; rm = wd[-1][1] - GOAL_WEIGHT
            st.markdown(f'<div style="display:flex;gap:24px;justify-content:center;margin:10px 0;"><span style="color:#34d399;font-weight:700;font-family:\'JetBrains Mono\',monospace;">▼ Lost: {lo:.1f} kg</span><span style="color:#475569;">·</span><span style="color:#fbbf24;font-weight:700;font-family:\'JetBrains Mono\',monospace;">→ Remaining: {rm:.1f} kg</span></div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="sec-title">Quick links</div>', unsafe_allow_html=True)
    for ic, ti, de, ur in [("📋","DS + AWS Roadmap","Daily schedule, ML & AWS roadmaps, interview prep","https://www.notion.so/1e7a7b694ee0805a877cf71c3de56f5d"),("🥗","Nutrition System","8-week meal plan, training schedule, weight tracker","https://www.notion.so/2a6a7b694ee080f6af92d59df04b63eb"),("🔁","Weekly Review","Sunday evening review — ties everything together","https://www.notion.so/323a7b694ee0817e8253f196589fe26c"),("📖","README — Start Here","Overview page with all links and daily flow","https://www.notion.so/328a7b694ee081b99a2bec1bb7a23bf9")]:
        st.markdown(f'<a href="{ur}" target="_blank" class="lk-card"><span style="font-size:18px;margin-right:10px;">{ic}</span><span style="font-size:15px;font-weight:700;color:#a5b4fc;">{ti}</span><div style="font-size:13px;color:#64748b;margin-top:4px;padding-left:32px;">{de}</div></a>', unsafe_allow_html=True)

st.markdown('<div class="prime-footer">Prime is built in silence. 🚀 Discipline = Freedom.<small>Small daily progress > random bursts of effort.</small></div>', unsafe_allow_html=True)
