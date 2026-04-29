import streamlit as st
import datetime
import json
from utils import load_data, save_data, ollama_available, ollama_models, ollama_generate

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ── API keys ──────────────────────────────────────────────
try:
    CLAUDE_KEY = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    CLAUDE_KEY = ""

try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_KEY = ""

ollama_ok = ollama_available()

# ── Build available models based on present keys ──────────
MODELS = []
if CLAUDE_KEY:
    MODELS += [
        {"id": "claude-sonnet-4-6",        "label": "Claude Sonnet 4.6",  "provider": "claude"},
        {"id": "claude-haiku-4-5-20251001", "label": "Claude Haiku 4.5",   "provider": "claude"},
    ]
if GEMINI_KEY:
    MODELS += [
        {"id": "gemini-2.0-flash",  "label": "Gemini 2.0 Flash",  "provider": "gemini"},
        {"id": "gemini-1.5-pro",    "label": "Gemini 1.5 Pro",    "provider": "gemini"},
    ]
if ollama_ok:
    for m in ollama_models():
        MODELS.append({"id": m, "label": f"Ollama · {m}", "provider": "ollama"})

MODEL_IDS    = [m["id"]    for m in MODELS]
MODEL_LABELS = [m["label"] for m in MODELS]

# ── System prompt ─────────────────────────────────────────
SYSTEM_PROMPT = """You are Prime Assistant, the AI built into Prime Dashboard — a personal productivity app for a data scientist who is:
- Actively job hunting (Data Science / ML Engineering / MLOps roles)
- Studying ML theory and AWS cloud (targeting AWS certification)
- Training at the gym 4-5x per week
- Following a structured 8-week career and study plan

You are sharp, concise, and direct. You help with: ML and Python questions, SQL, AWS, interview prep, cover letter review, career strategy, training and nutrition, and general productivity. Use markdown when it adds clarity."""

# ── Page header ───────────────────────────────────────────
st.markdown('<p class="page-title">AI Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Chat with Claude, Gemini, or Ollama — full history, multiple threads.</p>', unsafe_allow_html=True)

if not MODELS:
    st.error("🔴 No AI backend available. Add `ANTHROPIC_API_KEY` or `GEMINI_API_KEY` to secrets, or run Ollama locally.")
    st.stop()

# ── Data & session init ───────────────────────────────────
data  = load_data()
if "conversations" not in data:
    data["conversations"] = []
    save_data(data)

convs = data["conversations"]

if "active_conv_id" not in st.session_state:
    st.session_state.active_conv_id = convs[-1]["id"] if convs else None
if "selected_model_id" not in st.session_state:
    st.session_state.selected_model_id = MODEL_IDS[0]

# ── Helpers ───────────────────────────────────────────────
def get_model(mid):
    return next((m for m in MODELS if m["id"] == mid), MODELS[0])

def get_conv(cid):
    return next((c for c in data["conversations"] if c["id"] == cid), None)

def create_conv():
    cid = f"conv_{int(datetime.datetime.now().timestamp() * 1000)}"
    c   = {
        "id":       cid,
        "title":    "New conversation",
        "model":    st.session_state.selected_model_id,
        "created":  datetime.datetime.now().isoformat(timespec="seconds"),
        "messages": [],
    }
    data["conversations"].append(c)
    save_data(data)
    st.session_state.active_conv_id = cid

def call_ai(messages, model):
    """Send the full message history to the selected provider."""
    mid      = model["id"]
    provider = model["provider"]

    if provider == "claude" and HAS_REQUESTS:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": CLAUDE_KEY,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": mid,
                "max_tokens": 2048,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
            },
            timeout=60,
        )
        return r.json()["content"][0]["text"] if r.status_code == 200 else f"Error {r.status_code}: {r.text[:200]}"

    if provider == "gemini" and HAS_REQUESTS:
        # Gemini requires alternating user/model turns — ensure it starts with user
        gemini_msgs = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            # Merge consecutive same-role turns (Gemini rejects them)
            if gemini_msgs and gemini_msgs[-1]["role"] == role:
                gemini_msgs[-1]["parts"][0]["text"] += "\n" + m["content"]
            else:
                gemini_msgs.append({"role": role, "parts": [{"text": m["content"]}]})
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1/models/{mid}:generateContent?key={GEMINI_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents":           gemini_msgs,
                "systemInstruction":  {"parts": [{"text": SYSTEM_PROMPT}]},
                "generationConfig":   {"maxOutputTokens": 2048, "temperature": 0.7},
            },
            timeout=60,
        )
        return r.json()["candidates"][0]["content"]["parts"][0]["text"] if r.status_code == 200 else f"Error {r.status_code}: {r.text[:200]}"

    if provider == "ollama":
        # Build a flat prompt for Ollama (no native multi-turn API in basic generate)
        prompt = SYSTEM_PROMPT + "\n\n"
        for m in messages:
            prompt += ("User: " if m["role"] == "user" else "Assistant: ") + m["content"] + "\n"
        prompt += "Assistant:"
        return ollama_generate(prompt, mid, 2048)

    return "No provider could handle this request."

# ── Top controls row ──────────────────────────────────────
tc1, tc2, tc3, tc4 = st.columns([4, 2, 1, 1])

with tc1:
    cur_idx = MODEL_IDS.index(st.session_state.selected_model_id) if st.session_state.selected_model_id in MODEL_IDS else 0
    chosen  = st.selectbox("Model", MODEL_LABELS, index=cur_idx,
                           key="model_picker", label_visibility="collapsed")
    st.session_state.selected_model_id = MODEL_IDS[MODEL_LABELS.index(chosen)]

with tc2:
    # Conversation selector
    if convs:
        conv_titles = [f"{c.get('title','…')[:32]}" for c in reversed(convs[-30:])]
        conv_ids    = [c["id"] for c in reversed(convs[-30:])]
        active_idx  = conv_ids.index(st.session_state.active_conv_id) if st.session_state.active_conv_id in conv_ids else 0
        picked = st.selectbox("Conversation", conv_titles, index=active_idx,
                              key="conv_picker", label_visibility="collapsed")
        st.session_state.active_conv_id = conv_ids[conv_titles.index(picked)]
    else:
        st.markdown("")

with tc3:
    if st.button("➕ New", use_container_width=True, help="Start a new conversation"):
        create_conv()
        st.rerun()

with tc4:
    if st.button("🗑️ Delete", use_container_width=True, help="Delete this conversation"):
        st.session_state["confirm_del"] = True

# ── Delete confirmation ───────────────────────────────────
if st.session_state.get("confirm_del"):
    cid_to_del = st.session_state.active_conv_id
    conv_title = get_conv(cid_to_del).get("title", "this conversation") if get_conv(cid_to_del) else "this conversation"
    st.warning(f'Delete **"{conv_title}"**? This cannot be undone.')
    cd1, cd2, cd3 = st.columns([1, 1, 4])
    with cd1:
        if st.button("Delete", use_container_width=True, key="confirm_del_yes"):
            data["conversations"] = [c for c in data["conversations"] if c["id"] != cid_to_del]
            save_data(data)
            remaining = data["conversations"]
            st.session_state.active_conv_id = remaining[-1]["id"] if remaining else None
            st.session_state["confirm_del"] = False
            st.rerun()
    with cd2:
        if st.button("Cancel", use_container_width=True, key="confirm_del_no"):
            st.session_state["confirm_del"] = False
            st.rerun()

# ── Clear all history button (sidebar) ───────────────────
with st.sidebar:
    st.markdown("---")
    if st.button("🗑️ Clear all chats", use_container_width=True, key="clear_all_btn"):
        st.session_state["confirm_clear_all"] = True
    if st.session_state.get("confirm_clear_all"):
        st.warning("Delete ALL conversations?")
        if st.button("Yes, wipe all", use_container_width=True, key="wipe_yes"):
            data["conversations"] = []
            save_data(data)
            st.session_state.active_conv_id = None
            st.session_state["confirm_clear_all"] = False
            st.rerun()
        if st.button("Cancel", use_container_width=True, key="wipe_no"):
            st.session_state["confirm_clear_all"] = False
            st.rerun()

# ── Auto-create first conversation ────────────────────────
convs = data["conversations"]
if not convs:
    create_conv()
    st.rerun()

if not st.session_state.active_conv_id:
    st.session_state.active_conv_id = convs[-1]["id"]

# ── Main chat area ────────────────────────────────────────
active_conv = get_conv(st.session_state.active_conv_id)

if not active_conv:
    st.info("No active conversation. Click ➕ New to start one.")
    st.stop()

messages = active_conv.get("messages", [])
cur_model = get_model(active_conv.get("model", st.session_state.selected_model_id))

# Model + message count badge
badge_col = {"claude": "#818cf8", "gemini": "#60a5fa", "ollama": "#34d399"}.get(cur_model["provider"], "#64748b")
st.markdown(
    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">'
    f'<span style="font-size:11px;font-weight:700;color:{badge_col};background:{badge_col}18;'
    f'padding:3px 10px;border-radius:99px;font-family:JetBrains Mono,monospace;">'
    f'{cur_model["label"]}</span>'
    f'<span style="font-size:11px;color:#475569;font-family:JetBrains Mono,monospace;">'
    f'{len(messages)} messages</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Render existing messages ──────────────────────────────
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input (always at page bottom) ───────────────────
if user_input := st.chat_input("Ask anything…"):
    ts = datetime.datetime.now().isoformat(timespec="seconds")

    # Append user message
    active_conv["messages"].append({"role": "user", "content": user_input, "ts": ts})

    # Set conversation title from first message
    if len(active_conv["messages"]) == 1:
        active_conv["title"] = user_input[:45] + ("…" if len(user_input) > 45 else "")

    # Switch to the currently selected model for this turn
    active_conv["model"] = st.session_state.selected_model_id
    model_for_turn = get_model(st.session_state.selected_model_id)

    save_data(data)

    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get and display AI response
    with st.chat_message("assistant"):
        with st.spinner(f"Thinking with {model_for_turn['label']}…"):
            response = call_ai(active_conv["messages"], model_for_turn)
        st.markdown(response)

    active_conv["messages"].append({
        "role":    "assistant",
        "content": response,
        "ts":      datetime.datetime.now().isoformat(timespec="seconds"),
    })
    save_data(data)
    st.rerun()
