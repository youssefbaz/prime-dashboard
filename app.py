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

pg = st.navigation({
    "Overview":  [dashboard],
    "Study":     [timer, week, flashcards, quiz],
    "Career":    [jobs, cover],
    "Health":    [nutrition],
    "Analytics": [charts],
})

# ─────────────────────────────────────────────────────────
# GLOBAL CSS  (injected once here, available on all pages)
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

.stApp { background: linear-gradient(145deg,#0a0a0f 0%,#111127 50%,#0d1117 100%) !important; font-family:'Outfit',sans-serif !important; }
[data-testid="stSidebar"] { background:#0d0d18 !important; border-right:1px solid rgba(255,255,255,0.06) !important; }
[data-testid="stSidebar"] * { color:#94a3b8 !important; }
[data-testid="stSidebarNavLink"][aria-current="page"] { background:rgba(99,102,241,0.12) !important; border-radius:8px !important; }
[data-testid="stSidebarNavLink"][aria-current="page"] p { color:#a5b4fc !important; font-weight:600 !important; }
[data-testid="stSidebarNavSeparator"] { border-color:rgba(255,255,255,0.06) !important; }
#MainMenu, footer, header { visibility:hidden; }
.stDeployButton { display:none; }
.block-container { max-width:1100px !important; padding-top:2rem !important; }
h1,h2,h3,h4,h5,h6 { font-family:'Outfit',sans-serif !important; color:#f1f5f9 !important; }
p,span,label,div { font-family:'Outfit',sans-serif !important; }

.stButton>button { background:linear-gradient(135deg,#6366f1,#7c3aed) !important; color:#fff !important; border:none !important; border-radius:10px !important; font-family:'Outfit' !important; font-weight:600 !important; padding:10px 24px !important; }
.stButton>button:hover { background:linear-gradient(135deg,#7c3aed,#6366f1) !important; }
.stNumberInput input,.stTextArea textarea,.stTextInput input { background:rgba(255,255,255,0.05) !important; border:1px solid rgba(255,255,255,0.06) !important; border-radius:8px !important; color:#f1f5f9 !important; }
.stSelectbox>div[data-baseweb] { background:rgba(255,255,255,0.05) !important; border:1px solid rgba(255,255,255,0.06) !important; border-radius:8px !important; color:#f1f5f9 !important; }
.stSuccess>div { background:rgba(16,185,129,0.1) !important; border:1px solid rgba(16,185,129,0.2) !important; border-radius:10px !important; color:#6ee7b7 !important; }
.stWarning>div { background:rgba(245,158,11,0.1) !important; border:1px solid rgba(245,158,11,0.2) !important; border-radius:10px !important; }
.stInfo>div { background:rgba(99,102,241,0.1) !important; border:1px solid rgba(99,102,241,0.2) !important; border-radius:10px !important; }
.stCheckbox label { color:#e2e8f0 !important; font-size:14px !important; }
.stTabs [data-baseweb="tab-list"] { gap:4px; background:transparent; border-bottom:1px solid rgba(255,255,255,0.06); }
.stTabs [data-baseweb="tab"] { background:transparent !important; border:none !important; border-radius:8px !important; padding:8px 16px !important; font-weight:500 !important; font-size:13px !important; color:#94a3b8 !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { background:rgba(99,102,241,0.12) !important; color:#a5b4fc !important; }
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"] { display:none; }

.s-card { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:18px; text-align:center; }
.s-label { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:1.5px; color:#64748b; font-family:'JetBrains Mono',monospace; margin-bottom:6px; }
.s-val { font-size:28px; font-weight:800; font-family:'JetBrains Mono',monospace; line-height:1.2; }
.s-sub { font-size:12px; color:#475569; margin-top:4px; }

.sec-title { font-size:18px; font-weight:700; color:#f1f5f9; margin-bottom:14px; font-family:'Outfit'; }
.page-title { font-size:clamp(24px,4vw,34px); font-weight:800; background:linear-gradient(135deg,#f8fafc 0%,#a5b4fc 50%,#ec4899 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; line-height:1.2; margin:0 0 4px; }
.page-sub { font-size:14px; color:#64748b; margin-bottom:24px; }

.prime-card { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:20px 22px; margin-bottom:12px; }
.pbar-outer { height:8px; background:rgba(255,255,255,0.04); border-radius:99px; overflow:hidden; margin:10px 0; }
.pbar-inner { height:100%; border-radius:99px; }
.badge { display:inline-block; font-size:11px; font-weight:600; letter-spacing:1px; text-transform:uppercase; padding:3px 10px; border-radius:6px; font-family:'JetBrains Mono',monospace; }
.flash-card { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:28px; margin:12px 0; min-height:120px; }
.flash-q { font-size:17px; font-weight:600; color:#e2e8f0; line-height:1.5; }
.flash-a { font-size:15px; color:#94a3b8; line-height:1.6; margin-top:12px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.06); }
.job-row { background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:14px 18px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; }
.sch-active { background:rgba(99,102,241,0.06); border:1px solid rgba(99,102,241,0.25); border-left:4px solid #6366f1; border-radius:0 14px 14px 0; padding:16px 20px; margin-bottom:10px; }
.sch-normal { background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:16px 20px; margin-bottom:10px; }
.now-tag { display:inline-block; font-size:10px; font-weight:800; letter-spacing:2px; color:#818cf8; background:rgba(99,102,241,0.12); padding:3px 12px; border-radius:6px; text-transform:uppercase; font-family:'JetBrains Mono',monospace; }
.prime-footer { text-align:center; color:#334155; font-size:13px; padding:32px 0 16px; border-top:1px solid rgba(255,255,255,0.04); margin-top:40px; }
.glow-a { position:fixed; top:-200px; right:-200px; width:600px; height:600px; background:radial-gradient(circle,rgba(99,102,241,0.06) 0%,transparent 70%); pointer-events:none; z-index:0; }
.glow-b { position:fixed; bottom:-200px; left:-100px; width:500px; height:500px; background:radial-gradient(circle,rgba(236,72,153,0.04) 0%,transparent 70%); pointer-events:none; z-index:0; }
</style>
<div class="glow-a"></div><div class="glow-b"></div>
""", unsafe_allow_html=True)

pg.run()
