import streamlit as st
import json, random, time, datetime, re
from utils import (load_data, save_data, get_week_info,
                   ollama_available, ollama_models, get_default_model, ollama_generate,
                   QUIZ_QUESTIONS)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

data     = load_data()
wi       = get_week_info()
week_num = wi["week_num"]
today_str= wi["today_str"]

st.markdown('<p class="page-title">Interview quiz</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">AI-generated questions via Ollama or Claude API, with static bank as fallback.</p>', unsafe_allow_html=True)

ollama_ok = ollama_available()

# ── Claude API fallback ───────────────────────────────────
try:
    CLAUDE_KEY = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    CLAUDE_KEY = ""

def claude_generate(prompt, max_tokens=800):
    """Generate text via Claude API as fallback."""
    if not CLAUDE_KEY or not HAS_REQUESTS:
        return ""
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": CLAUDE_KEY,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        if r.status_code == 200:
            return r.json()["content"][0]["text"]
        else:
            return f"API error {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return f"Error: {e}"

# ── Determine AI backend ─────────────────────────────────
ai_ok = ollama_ok or bool(CLAUDE_KEY)

def generate_text(prompt, model=None, max_tokens=800):
    if ollama_ok:
        return ollama_generate(prompt, model, max_tokens)
    elif CLAUDE_KEY:
        return claude_generate(prompt, max_tokens)
    return ""

# ── AI mode (Ollama or Claude) ───────────────────────────
if ai_ok:
    if ollama_ok:
        models        = ollama_models()
        default_model = get_default_model()
        st.markdown(f"""
        <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
        border-radius:10px;padding:12px 18px;margin-bottom:16px;">
          <span style="font-size:13px;color:#34d399;font-weight:600;">🟢 Ollama connected — {default_model}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);
        border-radius:10px;padding:12px 18px;margin-bottom:16px;">
          <span style="font-size:13px;color:#a5b4fc;font-weight:600;">🟣 Claude API — Ollama offline, using Claude as fallback</span>
        </div>
        """, unsafe_allow_html=True)

    qc1, qc2 = st.columns([2, 1])
    with qc1:
        quiz_cat = st.selectbox("Category", ["ML Theory", "System Design", "Behavioral", "SQL & Python"], key="qcat")
    with qc2:
        if ollama_ok:
            sel_model = st.selectbox("Model", models,
                                     index=models.index(default_model) if default_model in models else 0,
                                     key="qmodel")
        else:
            st.selectbox("Model", ["Claude Sonnet"], disabled=True, key="qmodel_label")
            sel_model = None

    if st.button("🎲 Generate question", use_container_width=True, key="gen_q"):
        topics = {
            "ML Theory":    "machine learning: regression, classification, neural nets, NLP, model evaluation, ensembles, deep learning",
            "System Design":"ML system design: data pipelines, model serving, A/B testing, recommendation systems, MLOps on AWS",
            "Behavioral":   "behavioral interview using STAR method for data science roles",
            "SQL & Python": "SQL queries, pandas operations, Python data structures for data science",
        }
        prompt = f"""You are an expert data science interviewer. Generate ONE interview question about {topics.get(quiz_cat,"")}.
The candidate is in week {week_num} of an 8-week study program.
Return ONLY a JSON object — no markdown, no extra text:
{{"question":"...","model_answer":"...","difficulty":"medium","category":"{quiz_cat}"}}"""
        backend_label = sel_model if ollama_ok else "Claude"
        with st.spinner(f"Generating with {backend_label}…"):
            resp = generate_text(prompt, sel_model, 800)
        if resp:
            try:
                s = resp.find("{"); e = resp.rfind("}") + 1
                result = json.loads(resp[s:e])
                st.session_state.cq_question     = result.get("question", "")
                st.session_state.cq_model_answer = result.get("model_answer", "")
                st.session_state.cq_difficulty   = result.get("difficulty", "medium")
                st.session_state.cq_category     = quiz_cat
                st.session_state.cq_show         = False
                st.session_state.cq_review       = None
            except:
                st.error("Couldn't parse the response. Try again.")

    if st.session_state.get("cq_question"):
        diff_col = {"easy": "#34d399", "medium": "#fbbf24", "hard": "#ef4444"}.get(
            st.session_state.get("cq_difficulty", "medium"), "#fbbf24")
        st.markdown(f"""
        <div class="flash-card">
          <div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;">
            <span style="font-size:11px;font-weight:600;text-transform:uppercase;padding:3px 10px;
            border-radius:6px;color:#818cf8;background:rgba(129,140,248,0.1);">{st.session_state.get("cq_category","")}</span>
            <span style="font-size:11px;font-weight:600;text-transform:uppercase;padding:3px 10px;
            border-radius:6px;color:{diff_col};background:{diff_col}15;">{st.session_state.get("cq_difficulty","")}</span>
          </div>
          <div class="flash-q">{st.session_state.cq_question}</div>
        </div>
        """, unsafe_allow_html=True)

        user_ans = st.text_area("Your answer:", height=150, key="cq_user_ans",
                                placeholder="Write your answer, then get AI feedback…")
        ab1, ab2 = st.columns(2)
        with ab1:
            lbl = "🙈 Hide model answer" if st.session_state.get("cq_show") else "🔍 Show model answer"
            if st.button(lbl, use_container_width=True, key="cq_show_btn"):
                st.session_state.cq_show = not st.session_state.get("cq_show", False); st.rerun()
        with ab2:
            if user_ans and st.button("🤖 Review my answer", use_container_width=True, key="cq_rev_btn"):
                review_prompt = f"""You are an expert data science interview coach.

QUESTION: {st.session_state.cq_question}
CANDIDATE: {user_ans}
MODEL ANSWER: {st.session_state.get("cq_model_answer","")}

Score out of 10, what they got right, what they missed, one tip. 4–6 sentences. Start with the score."""
                with st.spinner("Reviewing…"):
                    st.session_state.cq_review = generate_text(review_prompt, sel_model, 500)
                st.rerun()

        if st.session_state.get("cq_show"):
            st.markdown(f"""
            <div class="flash-card" style="border-color:rgba(52,211,153,0.2);background:rgba(52,211,153,0.04);">
              <div style="font-size:12px;color:#34d399;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;font-family:'JetBrains Mono',monospace;">Model answer</div>
              <div style="font-size:15px;color:#94a3b8;line-height:1.6;">{st.session_state.get("cq_model_answer","")}</div>
            </div>""", unsafe_allow_html=True)

        if st.session_state.get("cq_review"):
            st.markdown(f"""
            <div class="flash-card" style="border-color:rgba(16,185,129,0.2);background:rgba(16,185,129,0.04);">
              <div style="font-size:12px;color:#34d399;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;font-family:'JetBrains Mono',monospace;">🤖 AI review</div>
              <div style="font-size:15px;color:#cbd5e1;line-height:1.7;">{st.session_state.cq_review}</div>
            </div>""", unsafe_allow_html=True)

        if user_ans and st.button("💾 Save session", use_container_width=True, key="cq_save"):
            source = "ollama" if ollama_ok else "claude"
            data.setdefault("quiz_history", {})[f"{source}_{today_str}_{int(time.time())}"] = {
                "question": st.session_state.cq_question, "user_answer": user_ans,
                "model_answer": st.session_state.get("cq_model_answer", ""),
                "review": st.session_state.get("cq_review", ""),
                "date": today_str, "source": source
            }
            save_data(data); st.success("Session saved! ✅")
    else:
        st.info("Click **Generate question** to get a fresh AI interview question.")

# ── Static fallback (no AI at all) ───────────────────────
else:
    st.markdown("""
    <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);
    border-radius:10px;padding:12px 18px;margin-bottom:16px;">
      <span style="font-size:13px;color:#fbbf24;font-weight:600;">⚡ No AI backend — using static question bank</span>
      <div style="font-size:12px;color:#92400e;margin-top:4px;">Run <code>ollama serve</code> or add ANTHROPIC_API_KEY for AI-generated questions.</div>
    </div>
    """, unsafe_allow_html=True)

    cat_filter = st.selectbox("Category", ["All", "ML Theory", "System Design", "Behavioral"], key="static_cat")
    qs = QUIZ_QUESTIONS if cat_filter == "All" else [q for q in QUIZ_QUESTIONS if q["cat"] == cat_filter]

    if "quiz_idx" not in st.session_state: st.session_state.quiz_idx = 0
    if "quiz_show" not in st.session_state: st.session_state.quiz_show = False

    qidx     = st.session_state.quiz_idx % len(qs)
    question = qs[qidx]
    cat_styles = {"ML Theory":"color:#f472b6;background:rgba(244,114,182,0.1);",
                  "System Design":"color:#34d399;background:rgba(52,211,153,0.1);",
                  "Behavioral":"color:#fbbf24;background:rgba(251,191,36,0.1);"}
    cst = cat_styles.get(question["cat"], "color:#818cf8;background:rgba(129,140,248,0.1);")

    st.markdown(f"""
    <div class="flash-card">
      <div style="display:inline-block;font-size:11px;font-weight:600;text-transform:uppercase;
      padding:3px 10px;border-radius:6px;margin-bottom:12px;{cst}">{question["cat"]}</div>
      <div class="flash-q">{question["q"]}</div>
    </div>""", unsafe_allow_html=True)

    if st.session_state.quiz_show:
        st.markdown(f"""
        <div class="flash-card" style="border-color:rgba(52,211,153,0.2);background:rgba(52,211,153,0.04);">
          <div style="font-size:12px;color:#34d399;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;font-family:'JetBrains Mono',monospace;">Model answer</div>
          <div style="font-size:15px;color:#94a3b8;line-height:1.6;">{question["a"]}</div>
        </div>""", unsafe_allow_html=True)

    user_ans = st.text_area("Your answer:", height=120, key="static_ans",
                            placeholder="Think through your answer…")
    sc1, sc2 = st.columns(2)
    with sc1:
        if st.button("🔍 Reveal" if not st.session_state.quiz_show else "🙈 Hide",
                     use_container_width=True, key="qshow"):
            st.session_state.quiz_show = not st.session_state.quiz_show; st.rerun()
    with sc2:
        if st.button("🎲 Next question", use_container_width=True, key="qnext"):
            st.session_state.quiz_idx  = random.randint(0, len(qs)-1)
            st.session_state.quiz_show = False; st.rerun()
    if user_ans and st.button("💾 Save answer", use_container_width=True, key="qsave"):
        data.setdefault("quiz_history", {})[f"static_{today_str}_{qidx}"] = {
            "question": question["q"], "user_answer": user_ans, "date": today_str
        }
        save_data(data); st.success("Saved!")
