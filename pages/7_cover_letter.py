import streamlit as st
import datetime
import json
import re
from utils import (load_data, save_data, get_week_info,
                   ollama_available, ollama_models, get_default_model, ollama_generate)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

data      = load_data()
wi        = get_week_info()
today_str = wi["today_str"]
today     = wi["today"]

st.markdown('<p class="page-title">Cover letter</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Upload your resume + paste a job offer — get a tailored letter in seconds.</p>', unsafe_allow_html=True)

ollama_ok = ollama_available()

def gemini_generate(prompt, api_key, max_tokens=2000):
    """Generate text via Gemini API."""
    if not api_key or not HAS_REQUESTS:
        return ""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        r = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": max_tokens,
                }
            },
            timeout=60,
        )
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"API error {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return f"Error: {e}"

# ── AI backend selection ──────────────────────────────────
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_KEY = ""

if ollama_ok:
    models        = ollama_models()
    default_model = get_default_model()
    ai_backend    = "ollama"
    st.markdown(f"""
    <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
    border-radius:10px;padding:12px 18px;margin-bottom:20px;">
      <span style="font-size:13px;color:#34d399;font-weight:600;">🟢 Ollama connected — {default_model}</span>
    </div>""", unsafe_allow_html=True)
elif GEMINI_KEY:
    ai_backend = "gemini"
    st.markdown("""
    <div style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);
    border-radius:10px;padding:12px 18px;margin-bottom:20px;">
      <span style="font-size:13px;color:#a5b4fc;font-weight:600;">🟣 Gemini API — Ollama offline, using Gemini as fallback</span>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
    border-radius:10px;padding:14px 18px;margin-bottom:16px;">
      <span style="font-size:13px;color:#fca5a5;font-weight:600;">🔴 No AI backend available</span>
      <div style="font-size:12px;color:#7f1d1d;margin-top:4px;">Run <code>ollama serve</code> or add GEMINI_API_KEY to secrets.</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

def generate_text(prompt, model=None, max_tokens=2000):
    """Route to Ollama or Gemini depending on what's available."""
    if ai_backend == "ollama":
        return ollama_generate(prompt, model, max_tokens)
    else:
        return gemini_generate(prompt, GEMINI_KEY, max_tokens)

# ── Input columns ─────────────────────────────────────────
cl1, cl2 = st.columns(2)

with cl1:
    st.markdown("**📄 Your resume**")
    resume_method = st.radio("Input method", ["Upload file", "Paste text"], horizontal=True, key="res_method")
    resume_text   = ""
    if resume_method == "Upload file":
        uploaded = st.file_uploader("Upload resume", type=["pdf","txt","md"], key="res_upload")
        if uploaded:
            if uploaded.type == "application/pdf":
                try:
                    import io
                    import PyPDF2
                    reader      = PyPDF2.PdfReader(io.BytesIO(uploaded.read()))
                    resume_text = "\n".join(p.extract_text() or "" for p in reader.pages)
                except ImportError:
                    resume_text = uploaded.read().decode("utf-8", errors="ignore")
                except Exception as e:
                    st.warning(f"PDF parse error: {e}. Try pasting text.")
            else:
                resume_text = uploaded.read().decode("utf-8", errors="ignore")
            if resume_text:
                st.success(f"Loaded — {len(resume_text)} characters")
    else:
        resume_text = st.text_area("Paste resume text", height=220, key="res_paste",
                                   placeholder="Paste your full resume here…")

with cl2:
    st.markdown("**🏢 Job offer**")
    job_offer = st.text_area("Paste job description", height=220, key="job_offer",
                             placeholder="Paste the full job description here…")
    jf1, jf2 = st.columns(2)
    with jf1: cl_company = st.text_input("Company name", key="cl_company", placeholder="e.g. Google")
    with jf2: cl_role    = st.text_input("Role", key="cl_role", placeholder="e.g. Data Scientist")

# ── Options ───────────────────────────────────────────────
opt1, opt2 = st.columns(2)
with opt1: cl_lang = st.selectbox("Language", ["English","French","Both"], key="cl_lang")
with opt2: cl_tone = st.selectbox("Tone", ["Professional & confident","Warm & enthusiastic","Formal & corporate","Creative & bold"], key="cl_tone")

if ai_backend == "ollama":
    cl_model = st.selectbox("Model", models, index=models.index(default_model) if default_model in models else 0, key="cl_model")
else:
    cl_model = None

auto_track = st.checkbox("📌 Auto-add to Job Tracker", value=True, key="cl_autotrack")

if st.button("✨ Generate cover letter", use_container_width=True, type="primary", key="gen_cl"):
    if resume_text and job_offer:
        languages = ["English","French"] if cl_lang == "Both" else [cl_lang]
        for lang in languages:
            prompt = f"""You are an expert career coach. Write a compelling cover letter in {lang}.
Tone: {cl_tone}.

=== RESUME ===
{resume_text}

=== JOB OFFER ===
{job_offer}

Guidelines: match skills to job requirements, highlight relevant projects, 3–4 paragraphs (~350 words),
strong opening hook, confident closing. Be specific — no generic sentences. Write in {lang}."""
            backend_label = cl_model if ai_backend == "ollama" else "Gemini"
            with st.spinner(f"Writing in {lang} with {backend_label}…"):
                letter = generate_text(prompt, cl_model, 2000)
            if letter:
                st.session_state[f"cl_edit_{lang.lower()}"] = letter

        if auto_track and (cl_company or cl_role):
            company_name = cl_company or "Unknown Company"
            role_name    = cl_role or "Unknown Role"
            existing     = [j for j in data.get("jobs",[]) if j.get("company","").lower() == company_name.lower()
                            and j.get("role","").lower() == role_name.lower()]
            if not existing:
                data.setdefault("jobs",[]).append({
                    "company": company_name, "role": role_name, "status": "Applied",
                    "url": "", "note": f"Cover letter generated ({cl_lang})",
                    "date": today_str, "has_cover_letter": True
                })
                save_data(data)
        st.rerun()
    else:
        st.warning("Please provide both your resume and the job offer.")

# ── Display & edit generated letters ─────────────────────
for lang in ["english", "french"]:
    key = f"cl_edit_{lang}"
    if key in st.session_state and st.session_state[key]:
        st.markdown(f"""
        <div style="font-size:13px;font-weight:600;color:#818cf8;text-transform:uppercase;
        letter-spacing:1px;margin:24px 0 8px;font-family:'JetBrains Mono',monospace;">
        📝 Cover letter — {lang.title()}</div>""", unsafe_allow_html=True)

        edited = st.text_area(f"Edit {lang} letter", value=st.session_state[key],
                              height=380, key=f"editor_{lang}", label_visibility="collapsed")
        st.session_state[key] = edited

        btn1, btn2, btn3 = st.columns(3)
        with btn1:
            if st.button(f"📥 Download PDF", use_container_width=True, key=f"pdf_{lang}"):
                try:
                    from reportlab.lib.pagesizes import A4
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                    from reportlab.lib.units import cm
                    import io as _io
                    buf = _io.BytesIO()
                    doc = SimpleDocTemplate(buf, pagesize=A4,
                                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                                            topMargin=2.5*cm, bottomMargin=2.5*cm)
                    styles = getSampleStyleSheet()
                    body   = ParagraphStyle("Body", parent=styles["Normal"],
                                            fontSize=11, leading=16, spaceAfter=12)
                    story  = [Paragraph(today.strftime("%B %d, %Y"),
                                        ParagraphStyle("Date", parent=styles["Normal"],
                                                       fontSize=10, textColor="#666666")),
                              Spacer(1, 24)]
                    for para in edited.strip().split("\n\n"):
                        clean = para.strip().replace("\n"," ").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                        if clean: story.append(Paragraph(clean, body))
                    doc.build(story)
                    st.download_button(f"⬇️ Save {lang.title()} PDF", buf.getvalue(),
                                       f"cover_letter_{lang}_{today_str}.pdf",
                                       "application/pdf", use_container_width=True, key=f"dl_{lang}")
                except ImportError:
                    st.error("Install reportlab: `pip install reportlab`")
        with btn2:
            if st.button("🔄 Regenerate", use_container_width=True, key=f"regen_{lang}"):
                if resume_text and job_offer:
                    prompt = f"Write a cover letter in {lang.title()} (tone: {cl_tone}) matching this resume to this job.\n\nRESUME:\n{resume_text}\n\nJOB:\n{job_offer}"
                    with st.spinner("Regenerating…"):
                        new_letter = generate_text(prompt, cl_model, 2000)
                    if new_letter:
                        st.session_state[key] = new_letter; st.rerun()
        with btn3:
            if st.button("💾 Save to history", use_container_width=True, key=f"save_cl_{lang}"):
                data.setdefault("cover_letters",[]).append({
                    "letter": edited, "language": lang,
                    "date": today_str, "job_snippet": job_offer[:200] if job_offer else ""
                })
                save_data(data); st.success("Saved!")

# ── History ───────────────────────────────────────────────
saved = data.get("cover_letters", [])
if saved:
    st.markdown("")
    with st.expander(f"📚 Saved letters ({len(saved)})"):
        for i, item in enumerate(reversed(saved[-10:])):
            st.markdown(f"**{item.get('date','')}** — {item.get('language','').title()} — {item.get('job_snippet','')[:80]}…")
            with st.expander(f"View letter #{len(saved)-i}"):
                st.text(item.get("letter",""))
