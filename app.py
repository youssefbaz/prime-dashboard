import streamlit as st
import datetime
import json
import os

st.set_page_config(
    page_title="Prime Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────────────────────
dashboard  = st.Page("pages/1_dashboard.py",     title="Dashboard",    icon="📋", default=True)
timer      = st.Page("pages/2_timer.py",          title="Timer",        icon="⏱️")
week       = st.Page("pages/3_week.py",           title="Week view",    icon="📅")
flashcards = st.Page("pages/4_flashcards.py",     title="Flashcards",   icon="🃏")
quiz       = st.Page("pages/5_quiz.py",           title="Quiz",         icon="🧪")
jobs       = st.Page("pages/6_jobs.py",           title="Jobs",         icon="💼")
cover      = st.Page("pages/7_cover_letter.py",   title="Cover letter", icon="📝")
charts     = st.Page("pages/8_charts.py",         title="Charts",       icon="📊")
nutrition  = st.Page("pages/9_nutrition.py",      title="Nutrition",    icon="🍽️")

from utils import load_data, calc_xp, get_level

data = load_data()
xp   = calc_xp(data)
lvl, prog, req = get_level(xp)
pct  = round((prog / req) * 100)

pg = st.navigation({
    "Overview":  [dashboard],
    "Study":     [timer, week, flashcards, quiz],
    "Career":    [jobs, cover],
    "Health":    [nutrition],
    "Analytics": [charts],
})

# ── Sidebar Gamification ──────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:10px 0 20px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:6px;">
            <span style="font-size:12px; font-weight:800; color:#818cf8; letter-spacing:1px; font-family:'JetBrains Mono';">LVL {lvl}</span>
            <span style="font-size:11px; color:#64748b; font-family:'JetBrains Mono';">{prog}/{req} XP</span>
        </div>
        <div style="height:6px; background:rgba(255,255,255,0.05); border-radius:10px; overflow:hidden;">
            <div style="width:{pct}%; height:100%; background:linear-gradient(90deg,#6366f1,#ec4899); border-radius:10px; transition:width 0.8s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# GLOBAL CSS  (injected once here, available on all pages)
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Outfit:wght@300;400;500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

:root {
  --glass-bg: rgba(255,255,255,0.03);
  --glass-bg-hover: rgba(255,255,255,0.06);
  --glass-border: rgba(255,255,255,0.08);
  --glass-border-hover: rgba(255,255,255,0.14);
  --ease: cubic-bezier(0.4, 0, 0.2, 1);
  --accent: #6366f1;
}

@keyframes fadeInUp { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
@keyframes drift     { 0%,100% { transform:translate(0,0); } 50% { transform:translate(40px,-30px); } }
@keyframes pulseDot  { 0%,100% { opacity:0.4; transform:scale(1); } 50% { opacity:0.8; transform:scale(1.1); } }
@keyframes shimmer   { 0% { background-position:-200% 0; } 100% { background-position:200% 0; } }

.stApp { background: radial-gradient(circle at 50% -20%, #1a1a3a 0%, #0a0a0f 60%, #07070a 100%) !important; font-family:'Inter',sans-serif !important; }
[data-testid="stSidebar"] { background:rgba(8,8,12,0.8) !important; backdrop-filter:blur(30px); -webkit-backdrop-filter:blur(30px); border-right:1px solid rgba(255,255,255,0.05) !important; }
[data-testid="stSidebar"] * { color:#94a3b8 !important; }
[data-testid="stSidebarNavLink"] { margin: 2px 0 !important; border-radius:10px !important; transition:all 0.3s var(--ease) !important; padding: 10px 14px !important; }
[data-testid="stSidebarNavLink"]:hover { background:rgba(255,255,255,0.04) !important; transform:translateX(4px); }
[data-testid="stSidebarNavLink"][aria-current="page"] { background:linear-gradient(90deg,rgba(99,102,241,0.15),rgba(99,102,241,0.02)) !important; box-shadow:inset 3px 0 0 #818cf8 !important; }
[data-testid="stSidebarNavLink"][aria-current="page"] p { color:#e2e8f0 !important; font-weight:600 !important; }

#MainMenu, footer, header { visibility:hidden; }
.stDeployButton { display:none; }
.block-container { max-width:1150px !important; padding-top:2.5rem !important; animation: fadeInUp 0.6s var(--ease); }
h1,h2,h3,h4,h5,h6 { font-family:'Outfit',sans-serif !important; color:#f8fafc !important; font-weight:700 !important; }
p,span,label,div { font-family:'Inter',sans-serif !important; }
::selection { background:rgba(99,102,241,0.3); color:#fff; }

/* Custom Scrollbar */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.1); border-radius:99px; }
::-webkit-scrollbar-thumb:hover { background:rgba(99,102,241,0.4); }

.stButton>button { 
    background: linear-gradient(135deg,#6366f1,#a855f7) !important; 
    color:#fff !important; 
    border:none !important; 
    border-radius:12px !important; 
    font-family:'Outfit' !important; 
    font-weight:600 !important; 
    padding:12px 28px !important; 
    transition:all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important; 
    box-shadow:0 10px 15px -3px rgba(99,102,241,0.3) !important;
}
.stButton>button:hover { transform:translateY(-3px) scale(1.02); box-shadow:0 20px 25px -5px rgba(99,102,241,0.4) !important; filter:brightness(1.15); }
.stButton>button:active { transform:translateY(0); }

.stNumberInput input,.stTextArea textarea,.stTextInput input { 
    background:rgba(255,255,255,0.03) !important; 
    border:1px solid rgba(255,255,255,0.06) !important; 
    border-radius:12px !important; 
    color:#f1f5f9 !important; 
    padding: 10px 14px !important;
}
.stNumberInput input:focus,.stTextArea textarea:focus,.stTextInput input:focus { border-color:rgba(129,140,248,0.4) !important; box-shadow:0 0 0 3px rgba(129,140,248,0.1) !important; }

/* Glassmorphic cards with tilt effect */
.s-card { 
    background:var(--glass-bg); 
    backdrop-filter:blur(20px); 
    -webkit-backdrop-filter:blur(20px); 
    border:1px solid var(--glass-border); 
    border-radius:20px; 
    padding:24px; 
    text-align:center; 
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position:relative; 
    overflow:hidden; 
}
.s-card::before { 
    content:""; 
    position:absolute; 
    top:0; left:-100%; width:100%; height:100%;
    background:linear-gradient(90deg,transparent,rgba(255,255,255,0.05),transparent);
    transition:0.5s;
}
.s-card:hover::before { left:100%; }
.s-card:hover { 
    transform: translateY(-8px) rotateX(2deg); 
    border-color:var(--glass-border-hover); 
    background:var(--glass-bg-hover); 
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); 
}
.s-label { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:2px; color:#64748b; font-family:'JetBrains Mono',monospace; margin-bottom:10px; }
.s-val { font-size:32px; font-weight:800; font-family:'Outfit'; line-height:1; color:#f8fafc; }
.s-sub { font-size:13px; color:#475569; margin-top:8px; }

.sec-title { font-size:20px; font-weight:800; color:#f1f5f9; margin: 30px 0 16px; font-family:'Outfit'; display:flex; align-items:center; gap:10px; }
.page-title { font-size:clamp(28px,5vw,42px); font-weight:900; background:linear-gradient(135deg,#fff 0%,#818cf8 50%,#c084fc 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:-1px; margin-bottom:6px; animation: fadeInUp 0.5s ease; }
.page-sub { font-size:16px; color:#94a3b8; margin-bottom:32px; font-weight:400; }

.badge-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 16px;
    text-align: center;
    transition: all 0.3s ease;
}
.badge-card:hover { transform: scale(1.05); background: rgba(255,255,255,0.04); border-color: rgba(99,102,241,0.3); }
.badge-icon { font-size: 32px; margin-bottom: 8px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3)); }
.badge-name { font-size: 11px; font-weight: 700; color: #cbd5e1; text-transform: uppercase; letter-spacing: 1px; }

/* Progress bars, job rows, schedule cards */
.pbar-outer { height:8px; background:rgba(255,255,255,0.04); border-radius:99px; overflow:hidden; margin:10px 0; }
.pbar-inner { height:100%; border-radius:99px; transition:width 0.6s var(--ease); position:relative; }
.pbar-inner::after { content:""; position:absolute; inset:0; background:linear-gradient(90deg,transparent,rgba(255,255,255,0.3),transparent); background-size:200% 100%; animation:shimmer 2.5s linear infinite; }
.badge { display:inline-block; font-size:11px; font-weight:600; letter-spacing:1px; text-transform:uppercase; padding:3px 10px; border-radius:6px; font-family:'JetBrains Mono',monospace; }
.job-row { background:rgba(255,255,255,0.02); backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,0.05); border-radius:12px; padding:14px 18px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; transition:all 0.25s var(--ease); }
.job-row:hover { border-color:rgba(129,140,248,0.3); transform:translateX(4px); }
.sch-active { background:linear-gradient(90deg,rgba(99,102,241,0.12),rgba(99,102,241,0.02)); backdrop-filter:blur(10px); border:1px solid rgba(99,102,241,0.3); border-left:4px solid #6366f1; border-radius:0 14px 14px 0; padding:16px 20px; margin-bottom:10px; box-shadow:0 4px 20px rgba(99,102,241,0.15); }
.sch-normal { background:rgba(255,255,255,0.02); backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,0.05); border-radius:14px; padding:16px 20px; margin-bottom:10px; transition:all 0.25s var(--ease); }
.sch-normal:hover { border-color:rgba(255,255,255,0.1); transform:translateX(2px); }
.now-tag { display:inline-block; font-size:10px; font-weight:800; letter-spacing:2px; color:#818cf8; background:rgba(99,102,241,0.18); padding:3px 12px; border-radius:6px; text-transform:uppercase; font-family:'JetBrains Mono',monospace; position:relative; }
.now-tag::before { content:"●"; margin-right:4px; animation:pulseDot 1.4s ease-in-out infinite; }
.prime-footer { text-align:center; color:#334155; font-size:13px; padding:32px 0 16px; border-top:1px solid rgba(255,255,255,0.04); margin-top:40px; }

.glow-a { position:fixed; top:-200px; right:-200px; width:700px; height:700px; background:radial-gradient(circle,rgba(99,102,241,0.08) 0%,transparent 70%); pointer-events:none; z-index:0; animation:drift 25s ease-in-out infinite; }
.glow-b { position:fixed; bottom:-200px; left:-100px; width:600px; height:600px; background:radial-gradient(circle,rgba(236,72,153,0.06) 0%,transparent 70%); pointer-events:none; z-index:0; animation:drift 30s ease-in-out infinite reverse; }
</style>
<div class="glow-a"></div><div class="glow-b"></div>
""", unsafe_allow_html=True)

pg.run()
