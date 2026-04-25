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

:root {
  --glass-bg: rgba(255,255,255,0.04);
  --glass-bg-hover: rgba(255,255,255,0.06);
  --glass-border: rgba(255,255,255,0.08);
  --glass-border-hover: rgba(255,255,255,0.14);
  --ease: cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeInUp { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
@keyframes drift     { 0%,100% { transform:translate(0,0); } 50% { transform:translate(40px,-30px); } }
@keyframes pulseDot  { 0%,100% { opacity:0.5; } 50% { opacity:1; } }
@keyframes shimmer   { 0% { background-position:-200% 0; } 100% { background-position:200% 0; } }

.stApp { background: radial-gradient(ellipse at top, #14142b 0%, #0a0a0f 45%, #08080d 100%) !important; font-family:'Outfit',sans-serif !important; }
[data-testid="stSidebar"] { background:rgba(13,13,24,0.7) !important; backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px); border-right:1px solid rgba(255,255,255,0.06) !important; }
[data-testid="stSidebar"] * { color:#94a3b8 !important; }
[data-testid="stSidebarNavLink"] { transition:all 0.25s var(--ease) !important; }
[data-testid="stSidebarNavLink"]:hover { background:rgba(255,255,255,0.04) !important; border-radius:8px !important; transform:translateX(2px); }
[data-testid="stSidebarNavLink"][aria-current="page"] { background:linear-gradient(90deg,rgba(99,102,241,0.18),rgba(99,102,241,0.04)) !important; border-radius:8px !important; box-shadow:inset 2px 0 0 #818cf8; }
[data-testid="stSidebarNavLink"][aria-current="page"] p { color:#a5b4fc !important; font-weight:600 !important; }
[data-testid="stSidebarNavSeparator"] { border-color:rgba(255,255,255,0.06) !important; }
#MainMenu, footer, header { visibility:hidden; }
.stDeployButton { display:none; }
.block-container { max-width:1100px !important; padding-top:2rem !important; animation: fadeInUp 0.5s var(--ease); }
h1,h2,h3,h4,h5,h6 { font-family:'Outfit',sans-serif !important; color:#f1f5f9 !important; }
p,span,label,div { font-family:'Outfit',sans-serif !important; }
::selection { background:rgba(129,140,248,0.4); color:#fff; }
*::-webkit-scrollbar { width:8px; height:8px; }
*::-webkit-scrollbar-track { background:transparent; }
*::-webkit-scrollbar-thumb { background:rgba(99,102,241,0.25); border-radius:99px; }
*::-webkit-scrollbar-thumb:hover { background:rgba(99,102,241,0.45); }

.stButton>button { background:linear-gradient(135deg,#6366f1,#7c3aed) !important; color:#fff !important; border:none !important; border-radius:10px !important; font-family:'Outfit' !important; font-weight:600 !important; padding:10px 24px !important; transition:all 0.25s var(--ease) !important; box-shadow:0 4px 14px rgba(99,102,241,0.25) !important; }
.stButton>button:hover { transform:translateY(-2px); box-shadow:0 8px 24px rgba(99,102,241,0.4) !important; filter:brightness(1.1); }
.stButton>button:active { transform:translateY(0); }
.stNumberInput input,.stTextArea textarea,.stTextInput input { background:rgba(255,255,255,0.04) !important; border:1px solid rgba(255,255,255,0.08) !important; border-radius:10px !important; color:#f1f5f9 !important; transition:all 0.2s var(--ease) !important; }
.stNumberInput input:focus,.stTextArea textarea:focus,.stTextInput input:focus { border-color:rgba(129,140,248,0.5) !important; box-shadow:0 0 0 3px rgba(129,140,248,0.12) !important; }
.stSelectbox>div[data-baseweb] { background:rgba(255,255,255,0.04) !important; border:1px solid rgba(255,255,255,0.08) !important; border-radius:10px !important; color:#f1f5f9 !important; }
.stSlider [data-baseweb="slider"] [role="slider"] { background:#818cf8 !important; box-shadow:0 0 0 6px rgba(129,140,248,0.15) !important; }
.stSuccess>div { background:rgba(16,185,129,0.08) !important; border:1px solid rgba(16,185,129,0.2) !important; border-radius:12px !important; color:#6ee7b7 !important; backdrop-filter:blur(10px); }
.stWarning>div { background:rgba(245,158,11,0.08) !important; border:1px solid rgba(245,158,11,0.2) !important; border-radius:12px !important; backdrop-filter:blur(10px); }
.stInfo>div    { background:rgba(99,102,241,0.08) !important; border:1px solid rgba(99,102,241,0.2) !important; border-radius:12px !important; backdrop-filter:blur(10px); }
.stError>div   { background:rgba(239,68,68,0.08) !important; border:1px solid rgba(239,68,68,0.2) !important; border-radius:12px !important; backdrop-filter:blur(10px); }
.stCheckbox label { color:#e2e8f0 !important; font-size:14px !important; transition:color 0.2s var(--ease); }
.stCheckbox label:hover { color:#a5b4fc !important; }
.stTabs [data-baseweb="tab-list"] { gap:4px; background:transparent; border-bottom:1px solid rgba(255,255,255,0.06); }
.stTabs [data-baseweb="tab"] { background:transparent !important; border:none !important; border-radius:8px !important; padding:8px 16px !important; font-weight:500 !important; font-size:13px !important; color:#94a3b8 !important; transition:all 0.2s var(--ease) !important; }
.stTabs [data-baseweb="tab"]:hover { color:#cbd5e1 !important; background:rgba(255,255,255,0.03) !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { background:rgba(99,102,241,0.15) !important; color:#a5b4fc !important; }
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"] { display:none; }

/* Glassmorphic cards with tilt effect */
.s-card { 
    background:var(--glass-bg); 
    backdrop-filter:blur(12px); 
    -webkit-backdrop-filter:blur(12px); 
    border:1px solid var(--glass-border); 
    border-radius:16px; 
    padding:18px; 
    text-align:center; 
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position:relative; 
    overflow:hidden; 
}
.s-card::before { 
    content:""; 
    position:absolute; 
    inset:0; 
    background:linear-gradient(135deg,rgba(255,255,255,0.05) 0%,transparent 50%); 
    pointer-events:none; 
}
.s-card:hover { 
    transform: translateY(-5px) rotateX(2deg) rotateY(2deg); 
    border-color:var(--glass-border-hover); 
    background:var(--glass-bg-hover); 
    box-shadow: 0 15px 35px rgba(0,0,0,0.4), 0 0 20px rgba(99,102,241,0.1); 
}
.s-label { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:1.5px; color:#64748b; font-family:'JetBrains Mono',monospace; margin-bottom:6px; position:relative; }
.s-val { font-size:28px; font-weight:800; font-family:'JetBrains Mono',monospace; line-height:1.2; position:relative; }
.s-sub { font-size:12px; color:#475569; margin-top:4px; position:relative; }

.sec-title { font-size:18px; font-weight:700; color:#f1f5f9; margin-bottom:14px; font-family:'Outfit'; }
.page-title { font-size:clamp(24px,4vw,34px); font-weight:800; background:linear-gradient(135deg,#f8fafc 0%,#a5b4fc 50%,#ec4899 100%); background-size:200% 200%; -webkit-background-clip:text; -webkit-text-fill-color:transparent; line-height:1.2; margin:0 0 4px; animation:shimmer 8s ease infinite; }
.page-sub { font-size:14px; color:#64748b; margin-bottom:24px; }

.prime-card { 
    background:var(--glass-bg); 
    backdrop-filter:blur(12px); 
    -webkit-backdrop-filter:blur(12px); 
    border:1px solid var(--glass-border); 
    border-radius:16px; 
    padding:20px 22px; 
    margin-bottom:12px; 
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.prime-card:hover { 
    border-color:var(--glass-border-hover); 
    transform:translateY(-3px) scale(1.01); 
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
}
.pbar-outer { height:8px; background:rgba(255,255,255,0.04); border-radius:99px; overflow:hidden; margin:10px 0; }
.pbar-inner { height:100%; border-radius:99px; transition:width 0.6s var(--ease); position:relative; }
.pbar-inner::after { content:""; position:absolute; inset:0; background:linear-gradient(90deg,transparent,rgba(255,255,255,0.3),transparent); background-size:200% 100%; animation:shimmer 2.5s linear infinite; }
.badge { display:inline-block; font-size:11px; font-weight:600; letter-spacing:1px; text-transform:uppercase; padding:3px 10px; border-radius:6px; font-family:'JetBrains Mono',monospace; }
.flash-card { background:var(--glass-bg); backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px); border:1px solid var(--glass-border); border-radius:18px; padding:28px; margin:12px 0; min-height:120px; transition:all 0.3s var(--ease); }
.flash-card:hover { border-color:var(--glass-border-hover); }
.flash-q { font-size:17px; font-weight:600; color:#e2e8f0; line-height:1.5; }
.flash-a { font-size:15px; color:#94a3b8; line-height:1.6; margin-top:12px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.06); animation:fadeInUp 0.35s var(--ease); }
.job-row { background:var(--glass-bg); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px); border:1px solid var(--glass-border); border-radius:12px; padding:14px 18px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; transition:all 0.25s var(--ease); }
.job-row:hover { border-color:rgba(129,140,248,0.3); transform:translateX(4px); }
.sch-active { background:linear-gradient(90deg,rgba(99,102,241,0.12),rgba(99,102,241,0.02)); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px); border:1px solid rgba(99,102,241,0.3); border-left:4px solid #6366f1; border-radius:0 14px 14px 0; padding:16px 20px; margin-bottom:10px; box-shadow:0 4px 20px rgba(99,102,241,0.15); }
.sch-normal { background:var(--glass-bg); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px); border:1px solid var(--glass-border); border-radius:14px; padding:16px 20px; margin-bottom:10px; transition:all 0.25s var(--ease); }
.sch-normal:hover { border-color:var(--glass-border-hover); transform:translateX(2px); }
.now-tag { display:inline-block; font-size:10px; font-weight:800; letter-spacing:2px; color:#818cf8; background:rgba(99,102,241,0.18); padding:3px 12px; border-radius:6px; text-transform:uppercase; font-family:'JetBrains Mono',monospace; position:relative; }
.now-tag::before { content:"●"; margin-right:4px; animation:pulseDot 1.4s ease-in-out infinite; }
.prime-footer { text-align:center; color:#334155; font-size:13px; padding:32px 0 16px; border-top:1px solid rgba(255,255,255,0.04); margin-top:40px; }
.glow-a { position:fixed; top:-200px; right:-200px; width:600px; height:600px; background:radial-gradient(circle,rgba(99,102,241,0.10) 0%,transparent 70%); pointer-events:none; z-index:0; animation:drift 22s ease-in-out infinite; }
.glow-b { position:fixed; bottom:-200px; left:-100px; width:500px; height:500px; background:radial-gradient(circle,rgba(236,72,153,0.07) 0%,transparent 70%); pointer-events:none; z-index:0; animation:drift 28s ease-in-out infinite reverse; }
</style>
<div class="glow-a"></div><div class="glow-b"></div>
""", unsafe_allow_html=True)

pg.run()
