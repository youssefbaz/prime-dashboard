import streamlit as st
import datetime
from utils import load_data, save_data, FLASHCARDS, sm2_update, get_due_cards, CAT_STYLES, C

data       = load_data()
flash_data = data.get("flash_scores", {})

st.markdown('<p class="page-title">Flashcards</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Spaced repetition — SM-2 algorithm keeps hard cards coming back.</p>', unsafe_allow_html=True)

prev_cat   = st.session_state.get("flash_cat_prev", "All")
cat_filter = st.selectbox("Category", ["All", "ML", "AWS", "SQL"], key="flash_cat")
if cat_filter != prev_cat:
    st.session_state.flash_idx      = 0
    st.session_state.flash_show     = False
    st.session_state.flash_cat_prev = cat_filter
cards      = FLASHCARDS if cat_filter == "All" else [c for c in FLASHCARDS if c["cat"] == cat_filter]

due_indices = get_due_cards(flash_data, cards)
total_due   = len([i for i in due_indices if str(i) in flash_data])
total_new   = len([i for i in due_indices if str(i) not in flash_data])
mastered    = sum(1 for i in range(len(cards)) if flash_data.get(str(i), {}).get("reps", 0) >= 3)

st.markdown(f"""<div class="kpi-row">
  <div class="kpi-item">
    <span class="kpi-value" style="color:#ef4444;">{total_due}</span>
    <span class="kpi-label">Due today</span>
  </div>
  <div class="kpi-item">
    <span class="kpi-value" style="color:#818cf8;">{total_new}</span>
    <span class="kpi-label">New cards</span>
  </div>
  <div class="kpi-item">
    <span class="kpi-value" style="color:#34d399;">{mastered}</span>
    <span class="kpi-label">Mastered</span>
  </div>
</div>""", unsafe_allow_html=True)

st.markdown("")

if "flash_idx" not in st.session_state: st.session_state.flash_idx = 0
if "flash_show" not in st.session_state: st.session_state.flash_show = False

card_order  = due_indices if due_indices else list(range(len(cards)))
if not card_order: card_order = [0]
current_pos = st.session_state.flash_idx % len(card_order)
idx         = card_order[current_pos]
card        = cards[idx]

cat_style  = CAT_STYLES.get(card["cat"], f"color:{C['focus_mid']};background:rgba(129,140,248,0.1);")
card_info  = flash_data.get(str(idx), {})
interval   = card_info.get("interval", 0)
ef         = card_info.get("ef", 2.5)
status_txt = "New" if str(idx) not in flash_data else f"Next in {interval}d · EF: {ef}"

st.markdown(f"""
<div class="flash-card">
  <div style="display:inline-block;font-size:11px;font-weight:600;letter-spacing:1px;
  text-transform:uppercase;padding:3px 10px;border-radius:6px;margin-bottom:12px;
  {cat_style}">{card["cat"]} · {status_txt}</div>
  <div class="flash-q">{card["q"]}</div>
  {"" if not st.session_state.flash_show else f'<div class="flash-a">{card["a"]}</div>'}
</div>
""", unsafe_allow_html=True)

fc1, fc2, fc3 = st.columns(3)
with fc1:
    if st.button("⬅️ Previous", use_container_width=True, key="fprev"):
        st.session_state.flash_idx  = (current_pos - 1) % len(card_order)
        st.session_state.flash_show = False; st.rerun()
with fc2:
    label = "🙈 Hide" if st.session_state.flash_show else "👁️ Show answer"
    if st.button(label, use_container_width=True, key="fshow"):
        st.session_state.flash_show = not st.session_state.flash_show; st.rerun()
with fc3:
    if st.button("➡️ Next", use_container_width=True, key="fnext"):
        st.session_state.flash_idx  = (current_pos + 1) % len(card_order)
        st.session_state.flash_show = False; st.rerun()

if st.session_state.flash_show:
    st.markdown("")
    st.markdown('<div style="font-size:13px;color:#94a3b8;text-align:center;margin-bottom:8px;">How well did you know this?</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    def rate(q):
        data["flash_scores"] = sm2_update(str(idx), q, data.get("flash_scores", {}))
        save_data(data)
        st.session_state.flash_idx  = (current_pos + 1) % len(card_order)
        st.session_state.flash_show = False
        st.rerun()
    with r1:
        if st.button("😵 Again", use_container_width=True, key="r0"): rate(0)
    with r2:
        if st.button("😟 Hard", use_container_width=True, key="r2"): rate(2)
    with r3:
        if st.button("🙂 Good", use_container_width=True, key="r4"): rate(4)
    with r4:
        if st.button("🤩 Easy", use_container_width=True, key="r5"): rate(5)

st.markdown(f'<div style="text-align:center;color:#475569;font-size:13px;margin-top:12px;font-family:\'JetBrains Mono\',monospace;">Card {current_pos + 1} of {len(card_order)}</div>', unsafe_allow_html=True)
