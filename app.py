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

from utils import load_data, save_data, calc_xp, get_level, get_plan_config, _DEFAULT_PLAN_START, _DEFAULT_PLAN_WEEKS
import streamlit.components.v1 as _components

data = load_data()
xp   = calc_xp(data)
lvl, prog, req = get_level(xp)
pct  = round((prog / req) * 100)
plan_start, plan_weeks, plan_end = get_plan_config(data)

pg = st.navigation({
    "Overview":  [dashboard],
    "Study":     [timer, week, flashcards, quiz],
    "Career":    [jobs, cover],
    "Health":    [nutrition],
    "Analytics": [charts],
})

# ── Persistent media players (rendered BEFORE pg.run so their
#    React tree positions are stable across page navigations) ──
_RADIO_HTML = """
<style>
  * { box-sizing:border-box; margin:0; padding:0; }
  body { background:transparent; font-family:'Inter',sans-serif; padding:4px 0; }
  .lbl { font-size:11px; font-weight:700; letter-spacing:1px; text-transform:uppercase; color:#64748b; margin-bottom:8px; }
  select { width:100%; padding:7px 10px; margin-bottom:10px; background:rgba(255,255,255,0.04); color:#e2e8f0; border:1px solid rgba(255,255,255,0.1); border-radius:8px; font-size:13px; cursor:pointer; outline:none; }
  .btns { display:flex; gap:6px; margin-bottom:8px; }
  button { flex:1; padding:7px 4px; font-size:13px; font-weight:600; border:none; border-radius:8px; cursor:pointer; background:rgba(99,102,241,0.2); color:#a5b4fc; transition:background .2s; }
  button:hover { background:rgba(99,102,241,0.4); }
  #bp { background:rgba(52,211,153,0.15); color:#34d399; } #bp:hover { background:rgba(52,211,153,0.3); }
  #bs { background:rgba(239,68,68,0.1);  color:#f87171; } #bs:hover { background:rgba(239,68,68,0.25); }
  .st { font-size:11px; color:#475569; text-align:center; }
  .st.on { color:#34d399; } .st.pa { color:#fbbf24; }
</style>
<div class="lbl">📻 Radio</div>
<select id="sel" onchange="onChange()">
  <option value="https://hitradio.ice.infomaniak.ch/hitradio-128.mp3">Hit Radio</option>
  <option value="https://radiomars.ice.infomaniak.ch/radiomars-128.mp3">Radio Mars</option>
  <option value="https://mfmradio.ice.infomaniak.ch/mfmradio-128.mp3">MFM Radio</option>
  <option value="https://luxeradio.ice.infomaniak.ch/luxeradio-128.mp3">Luxe Radio</option>
</select>
<div class="btns">
  <button id="bp" onclick="play()">▶ Play</button>
  <button onclick="pause()">⏸ Pause</button>
  <button id="bs" onclick="stop()">⏹ Stop</button>
</div>
<div class="st" id="st">Stopped</div>
<audio id="a"></audio>
<script>
  var a=document.getElementById('a'), s=document.getElementById('st');
  function set(t,c){s.textContent=t;s.className='st '+(c||'');}
  function play(){a.src=document.getElementById('sel').value;a.play();set('● Playing','on');}
  function pause(){a.pause();set('⏸ Paused','pa');}
  function stop(){a.pause();a.src='';set('Stopped','');}
  function onChange(){if(a.src&&!a.paused)play();}
  a.onerror=function(){set('⚠ Stream error','');};
</script>
"""

# Spotify: always render at same tree position. HTML changes only when
# the user picks a new track (intentional reload); stable across navigation.
_sp_track = st.session_state.get("sp_playing_track", "")
_SP_HTML = (
    f'<iframe src="https://open.spotify.com/embed/track/{_sp_track}'
    f'?utm_source=generator&theme=0" width="100%" height="80" frameborder="0"'
    f' allow="autoplay;clipboard-write;encrypted-media;picture-in-picture"></iframe>'
    if _sp_track else "<div></div>"
)

with st.sidebar:
    # ① XP bar
    st.markdown(f"""
    <div style="padding:15px 5px 25px; margin-bottom:10px;">
        <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:8px;white-space:nowrap;">
            <span style="font-size:12px;font-weight:800;color:#818cf8;letter-spacing:1px;font-family:'JetBrains Mono';">LVL {lvl}</span>
            <span style="font-size:11px;color:#64748b;font-family:'JetBrains Mono';opacity:.8;">{prog}/{req} XP</span>
        </div>
        <div style="height:8px;background:rgba(255,255,255,0.1);border-radius:10px;overflow:hidden;border:1px solid rgba(255,255,255,0.05);">
            <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#6366f1,#ec4899);border-radius:10px;transition:width .8s ease;"></div>
        </div>
    </div>""", unsafe_allow_html=True)
    # ② Radio player  (constant HTML → React never recreates iframe)
    _components.html(_RADIO_HTML, height=148)
    # ③ Spotify Now Playing  (same position every render → persists on navigation)
    _components.html(_SP_HTML, height=84 if _sp_track else 2)

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
[data-testid="stSidebar"] { background:rgba(15,15,28,0.97) !important; backdrop-filter:blur(30px); -webkit-backdrop-filter:blur(30px); border-right:1px solid rgba(255,255,255,0.12) !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { color:#94a3b8 !important; }

/* Popover button styling */
[data-testid="stPopover"] > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #cbd5e1 !important;
    margin-top: 10px !important;
    margin-bottom: 20px !important;
}
[data-testid="stPopover"] > button:hover {
    background: rgba(255,255,255,0.08) !important;
    border-color: rgba(99,102,241,0.4) !important;
}

[data-testid="stSidebarNavLink"] { margin: 4px 0 !important; border-radius:10px !important; transition:all 0.3s var(--ease) !important; padding: 10px 14px !important; }
[data-testid="stSidebarNavLink"]:hover { background:rgba(255,255,255,0.04) !important; transform:translateX(4px); }
[data-testid="stSidebarNavLink"][aria-current="page"] { background:linear-gradient(90deg,rgba(99,102,241,0.15),rgba(99,102,241,0.02)) !important; box-shadow:inset 3px 0 0 #818cf8 !important; }
[data-testid="stSidebarNavLink"][aria-current="page"] p { color:#e2e8f0 !important; font-weight:600 !important; }

#MainMenu, footer, header { visibility:hidden; }
.stDeployButton { display:none; }
[data-testid="stSidebarCollapseButton"] { display:none !important; }
[data-testid="collapsedControl"] { display:none !important; }
[data-testid="stSidebar"][aria-expanded="false"] { transform:none !important; margin-left:0 !important; min-width:244px !important; }
.block-container { max-width:1150px !important; padding-top:2.5rem !important; animation: fadeInUp 0.6s var(--ease); }
h1,h2,h3,h4,h5,h6 { font-family:'Outfit',sans-serif !important; color:#f8fafc !important; font-weight:700 !important; }
p,span,label,div { font-family:'Inter',sans-serif !important; }
[data-testid="stIconMaterial"], [data-testid="stIconEmoji"] { font-family:'Material Symbols Rounded','Material Icons' !important; }
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

/* Flashcard & quiz cards */
.flash-card { background:var(--glass-bg); backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px); border:1px solid var(--glass-border); border-radius:20px; padding:28px 32px; margin-bottom:20px; transition:border-color 0.3s var(--ease); }
.flash-card:hover { border-color:var(--glass-border-hover); }
.flash-q { font-size:20px; font-weight:700; color:#f1f5f9; line-height:1.5; font-family:'Outfit',sans-serif; }
.flash-a { font-size:15px; color:#94a3b8; line-height:1.7; margin-top:20px; padding-top:20px; border-top:1px solid rgba(255,255,255,0.06); }

.glow-a { position:fixed; top:-200px; right:-200px; width:700px; height:700px; background:radial-gradient(circle,rgba(99,102,241,0.08) 0%,transparent 70%); pointer-events:none; z-index:0; animation:drift 25s ease-in-out infinite; }
.glow-b { position:fixed; bottom:-200px; left:-100px; width:600px; height:600px; background:radial-gradient(circle,rgba(236,72,153,0.06) 0%,transparent 70%); pointer-events:none; z-index:0; animation:drift 30s ease-in-out infinite reverse; }
</style>
<div class="glow-a"></div><div class="glow-b"></div>
""", unsafe_allow_html=True)

pg.run()

# ── Sidebar Plan Settings (bottom) ───────────────────────
with st.sidebar:
    st.markdown("---")
    with st.popover("⚙️ Plan Settings", use_container_width=True):
        st.markdown("### 📅 Plan Timing")
        new_start = st.date_input("Start date", value=plan_start, key="cfg_start")
        new_weeks = st.number_input("Duration (weeks)", min_value=1, max_value=52,
                                    value=plan_weeks, step=1, key="cfg_weeks")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save plan", use_container_width=True, key="save_plan"):
                data["plan_start"] = new_start.isoformat()
                data["plan_weeks"] = int(new_weeks)
                save_data(data)
                st.success("Plan updated!")
                st.rerun()
        with col2:
            if st.button("Today", help="Set start date to today", use_container_width=True):
                data["plan_start"] = datetime.date.today().isoformat()
                save_data(data)
                st.rerun()
        st.markdown("---")
        st.markdown("### ⚠️ Reset Options")
        if st.button("🗑️ Clear Today's Checklist", use_container_width=True):
            today_str = datetime.date.today().isoformat()
            if "daily_checks" in data and today_str in data["daily_checks"]:
                del data["daily_checks"][today_str]
                save_data(data)
                st.warning("Today's checklist reset.")
                st.rerun()
        if st.button("🚨 Factory Reset Plan", use_container_width=True, help="Wipes all progress, weights, and notes!"):
            data = {
                "plan_start": new_start.isoformat(),
                "plan_weeks": int(new_weeks),
                "daily_checks": {}, "weights": {}, "notes": {}, "missed_acks": [],
                "jobs": [], "quiz_history": {}, "flash_scores": {},
                "cover_letters": [], "focus_sessions": []
            }
            save_data(data)
            st.error("All data has been reset.")
            st.rerun()
