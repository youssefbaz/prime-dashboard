import streamlit as st
import datetime
import json
import os
import subprocess
from utils import load_data, save_data, ollama_available, ollama_models, ollama_generate

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Project root (one level up from pages/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

You are sharp, concise, and direct. You help with: ML and Python questions, SQL, AWS, interview prep, cover letter review, career strategy, training and nutrition, and general productivity. Use markdown when it adds clarity.

You also have the ability to modify Prime Dashboard itself. When the user asks you to change something in the app:
1. Use list_files to understand the project structure if needed.
2. Use read_file to read the relevant file(s) before making any changes.
3. Use write_file to apply the changes — always write the complete file content.
4. Use git_commit_and_push to commit and push to GitHub with a descriptive message.
Always confirm what you changed and why."""

# ── Tool definitions (Claude only) ───────────────────────
TOOLS = [
    {
        "name": "read_file",
        "description": "Read a file from the Prime Dashboard project. Use before writing to understand current code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to project root, e.g. 'pages/9_nutrition.py' or 'utils.py'"
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write or overwrite a file in the Prime Dashboard project. Write the complete file content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path":    {"type": "string", "description": "File path relative to project root"},
                "content": {"type": "string", "description": "Complete file content to write"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "list_files",
        "description": "List files in the Prime Dashboard project directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory to list relative to project root (default: '.')",
                }
            },
        },
    },
    {
        "name": "git_commit_and_push",
        "description": "Stage all modified files, create a git commit, and push to GitHub. Call this after all write_file calls are done.",
        "input_schema": {
            "type": "object",
            "properties": {
                "commit_message": {
                    "type": "string",
                    "description": "Descriptive commit message (e.g. 'feat: add water intake tracker to nutrition page')",
                }
            },
            "required": ["commit_message"],
        },
    },
]

TOOL_ICONS = {
    "read_file":           "📖",
    "write_file":          "✏️",
    "list_files":          "📁",
    "git_commit_and_push": "🚀",
}

# ── Tool executor ─────────────────────────────────────────
def execute_tool(name: str, inputs: dict) -> str:
    if name == "read_file":
        rel  = inputs.get("path", "")
        path = os.path.normpath(os.path.join(PROJECT_ROOT, rel))
        if not path.startswith(PROJECT_ROOT + os.sep) and path != PROJECT_ROOT:
            return "Error: path is outside the project root"
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return f"File not found: {rel}"
        except Exception as exc:
            return f"Error reading file: {exc}"

    if name == "write_file":
        rel     = inputs.get("path", "")
        content = inputs.get("content", "")
        path    = os.path.normpath(os.path.join(PROJECT_ROOT, rel))
        if not path.startswith(PROJECT_ROOT + os.sep) and path != PROJECT_ROOT:
            return "Error: path is outside the project root"
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            return f"Written: {rel}"
        except Exception as exc:
            return f"Error writing file: {exc}"

    if name == "list_files":
        directory = inputs.get("directory", ".")
        base = os.path.normpath(os.path.join(PROJECT_ROOT, directory))
        if not base.startswith(PROJECT_ROOT + os.sep) and base != PROJECT_ROOT:
            return "Error: path is outside the project root"
        try:
            result = []
            for root, dirs, files in os.walk(base):
                dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d != "__pycache__")
                for f in sorted(files):
                    rel = os.path.relpath(os.path.join(root, f), PROJECT_ROOT)
                    result.append(rel.replace("\\", "/"))
            return "\n".join(result[:150]) or "(empty)"
        except Exception as exc:
            return f"Error listing files: {exc}"

    if name == "git_commit_and_push":
        msg = inputs.get("commit_message", "update via Prime Assistant")
        full_msg = msg + "\n\nCo-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
        try:
            r1 = subprocess.run(["git", "add", "-A"], cwd=PROJECT_ROOT,
                                capture_output=True, text=True)
            if r1.returncode != 0:
                return f"git add failed: {r1.stderr}"

            r2 = subprocess.run(["git", "commit", "-m", full_msg],
                                cwd=PROJECT_ROOT, capture_output=True, text=True)
            if r2.returncode != 0:
                out = (r2.stdout + r2.stderr).lower()
                if "nothing to commit" in out:
                    return "Nothing to commit — no file changes detected."
                return f"git commit failed: {r2.stderr}"

            r3 = subprocess.run(["git", "push"], cwd=PROJECT_ROOT,
                                capture_output=True, text=True)
            if r3.returncode != 0:
                return f"Committed locally but push failed: {r3.stderr}\n(You may need to push manually.)"

            short = msg[:72]
            return f"Committed and pushed: \"{short}\""
        except Exception as exc:
            return f"Git error: {exc}"

    return f"Unknown tool: {name}"


def action_summary(name: str, inputs: dict, result: str) -> str:
    if name == "read_file":
        chars = len(result)
        return f"Read `{inputs.get('path', '?')}` — {chars:,} chars"
    if name == "write_file":
        lines = inputs.get("content", "").count("\n") + 1
        return f"Wrote `{inputs.get('path', '?')}` — {lines} lines"
    if name == "list_files":
        count = result.count("\n") + 1 if result.strip() else 0
        return f"Listed {count} files in `{inputs.get('directory', '.')}`"
    if name == "git_commit_and_push":
        return result
    return f"{name}: done"


# ── AI call (returns text + actions taken) ────────────────
def call_ai(messages, model):
    mid      = model["id"]
    provider = model["provider"]

    # ── Claude (with tool use agentic loop) ───────────────
    if provider == "claude" and HAS_REQUESTS:
        api_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
        actions: list[tuple[str, str]] = []  # (icon + label, detail)

        for _ in range(15):  # max rounds to prevent infinite loops
            r = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": CLAUDE_KEY,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model":      mid,
                    "max_tokens": 4096,
                    "system":     SYSTEM_PROMPT,
                    "tools":      TOOLS,
                    "messages":   api_messages,
                },
                timeout=120,
            )
            if r.status_code != 200:
                return f"Error {r.status_code}: {r.text[:200]}", actions

            resp        = r.json()
            stop_reason = resp.get("stop_reason")
            content     = resp.get("content", [])

            if stop_reason == "tool_use":
                tool_results = []
                for block in content:
                    if block["type"] == "tool_use":
                        result  = execute_tool(block["name"], block["input"])
                        summary = action_summary(block["name"], block["input"], result)
                        icon    = TOOL_ICONS.get(block["name"], "🔧")
                        actions.append((f"{icon} {block['name']}", summary))
                        tool_results.append({
                            "type":        "tool_result",
                            "tool_use_id": block["id"],
                            "content":     result,
                        })
                api_messages.append({"role": "assistant", "content": content})
                api_messages.append({"role": "user",      "content": tool_results})

            else:  # end_turn or max_tokens
                text = "".join(b["text"] for b in content if b.get("type") == "text")
                return text or "Done.", actions

        return "Reached maximum tool iterations.", actions

    # ── Gemini ────────────────────────────────────────────
    if provider == "gemini" and HAS_REQUESTS:
        gemini_msgs = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            if gemini_msgs and gemini_msgs[-1]["role"] == role:
                gemini_msgs[-1]["parts"][0]["text"] += "\n" + m["content"]
            else:
                gemini_msgs.append({"role": role, "parts": [{"text": m["content"]}]})
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{mid}:generateContent?key={GEMINI_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents":           gemini_msgs,
                "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "generationConfig":   {"maxOutputTokens": 2048, "temperature": 0.7},
            },
            timeout=60,
        )
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"], []
        if r.status_code == 429:
            return (
                "⚠️ Gemini quota exceeded. Switch to **Claude** or **Ollama** in the model "
                "selector above, or upgrade your Google AI plan at [ai.google.dev](https://ai.google.dev)."
            ), []
        return f"Error {r.status_code}: {r.text[:200]}", []

    # ── Ollama ────────────────────────────────────────────
    if provider == "ollama":
        prompt = SYSTEM_PROMPT + "\n\n"
        for m in messages:
            prompt += ("User: " if m["role"] == "user" else "Assistant: ") + m["content"] + "\n"
        prompt += "Assistant:"
        return ollama_generate(prompt, mid, 2048), []

    return "No provider could handle this request.", []


# ── Page header ───────────────────────────────────────────
st.markdown('<p class="page-title">AI Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Chat with Claude, Gemini, or Ollama — full history, multiple threads. Claude can also edit the app and push to GitHub.</p>', unsafe_allow_html=True)

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

# ── Top controls row ──────────────────────────────────────
tc1, tc2, tc3, tc4 = st.columns([4, 2, 1, 1])

with tc1:
    cur_idx = MODEL_IDS.index(st.session_state.selected_model_id) if st.session_state.selected_model_id in MODEL_IDS else 0
    chosen  = st.selectbox("Model", MODEL_LABELS, index=cur_idx,
                           key="model_picker", label_visibility="collapsed")
    st.session_state.selected_model_id = MODEL_IDS[MODEL_LABELS.index(chosen)]

with tc2:
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

messages  = active_conv.get("messages", [])
cur_model = get_model(active_conv.get("model", st.session_state.selected_model_id))

badge_col = {"claude": "#818cf8", "gemini": "#60a5fa", "ollama": "#34d399"}.get(cur_model["provider"], "#64748b")
tools_badge = (
    '<span style="font-size:11px;font-weight:700;color:#34d399;background:#34d39918;'
    'padding:3px 10px;border-radius:99px;font-family:JetBrains Mono,monospace;">🔧 tools enabled</span>'
    if cur_model["provider"] == "claude" else ""
)
st.markdown(
    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">'
    f'<span style="font-size:11px;font-weight:700;color:{badge_col};background:{badge_col}18;'
    f'padding:3px 10px;border-radius:99px;font-family:JetBrains Mono,monospace;">'
    f'{cur_model["label"]}</span>'
    f'{tools_badge}'
    f'<span style="font-size:11px;color:#475569;font-family:JetBrains Mono,monospace;">'
    f'{len(messages)} messages</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Render existing messages ──────────────────────────────
for msg in messages:
    with st.chat_message(msg["role"]):
        # Show tool actions taken (stored with assistant messages)
        if msg["role"] == "assistant" and msg.get("actions"):
            with st.expander(f"🔧 {len(msg['actions'])} action(s) taken", expanded=False):
                for label, detail in msg["actions"]:
                    st.markdown(f"**{label}**  \n{detail}")
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────
if user_input := st.chat_input("Ask anything… or say 'change X in the app'"):
    ts = datetime.datetime.now().isoformat(timespec="seconds")

    active_conv["messages"].append({"role": "user", "content": user_input, "ts": ts})

    if len(active_conv["messages"]) == 1:
        active_conv["title"] = user_input[:45] + ("…" if len(user_input) > 45 else "")

    active_conv["model"] = st.session_state.selected_model_id
    model_for_turn = get_model(st.session_state.selected_model_id)
    save_data(data)

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        if model_for_turn["provider"] == "claude":
            with st.status(f"Working with {model_for_turn['label']}…", expanded=True) as status:
                st.write("Thinking…")
                response, actions = call_ai(active_conv["messages"], model_for_turn)
                if actions:
                    for label, detail in actions:
                        st.write(f"{label} — {detail}")
                status.update(
                    label=f"Done · {len(actions)} action(s)" if actions else "Done",
                    state="complete",
                    expanded=bool(actions),
                )
        else:
            with st.spinner(f"Thinking with {model_for_turn['label']}…"):
                response, actions = call_ai(active_conv["messages"], model_for_turn)

        st.markdown(response)

    active_conv["messages"].append({
        "role":    "assistant",
        "content": response,
        "actions": actions,
        "ts":      datetime.datetime.now().isoformat(timespec="seconds"),
    })
    save_data(data)
    st.rerun()
