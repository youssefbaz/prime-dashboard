import streamlit as st
import datetime
from utils import load_data, save_data, get_week_info

data      = load_data()
wi        = get_week_info()
today_str = wi["today_str"]
today     = wi["today"]

st.markdown('<p class="page-title">Job tracker</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Track every application — stay on top of your pipeline.</p>', unsafe_allow_html=True)

# ── Add form ──────────────────────────────────────────────
with st.form("job_form", clear_on_submit=True):
    jc1, jc2, jc3 = st.columns([2, 2, 1])
    with jc1: company = st.text_input("Company")
    with jc2: role    = st.text_input("Role")
    with jc3: status  = st.selectbox("Status", ["Applied","Interview","Rejected","Offer","Ghosted"])
    jc4, jc5 = st.columns([2, 1])
    with jc4: job_url  = st.text_input("URL (optional)")
    with jc5: job_note = st.text_input("Note (optional)")
    if st.form_submit_button("➕ Add application", use_container_width=True):
        company = company.strip()
        role = role.strip()
        if company and role:
            data.setdefault("jobs", []).append({
                "company": company, "role": role, "status": status,
                "url": job_url.strip(), "note": job_note.strip(), "date": today_str
            })
            save_data(data); st.success(f"Added {company} — {role}"); st.rerun()
        elif not company:
            st.error("Company name is required.")
        else:
            st.error("Role / position is required.")

jobs = data.get("jobs", [])

# ── Stats ─────────────────────────────────────────────────
if jobs:
    status_counts = {}
    for j in jobs:
        status_counts[j["status"]] = status_counts.get(j["status"], 0) + 1

    this_week  = sum(1 for j in jobs if j.get("date","") >= (today - datetime.timedelta(days=7)).isoformat())
    last_week  = sum(1 for j in jobs if (today - datetime.timedelta(days=14)).isoformat()
                     <= j.get("date","") < (today - datetime.timedelta(days=7)).isoformat())
    wk_arrow   = "▲" if this_week >= last_week else "▼"
    wk_color   = "#34d399" if this_week >= last_week else "#ef4444"

    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    with sc1:
        st.markdown(f'<div class="s-card"><div class="s-label">Total</div><div class="s-val" style="color:#818cf8;">{len(jobs)}</div></div>', unsafe_allow_html=True)
    with sc2:
        st.markdown(f'<div class="s-card"><div class="s-label">This week</div><div class="s-val" style="color:{wk_color};">{this_week} <span style="font-size:14px;">{wk_arrow}</span></div><div class="s-sub">last: {last_week}</div></div>', unsafe_allow_html=True)
    with sc3:
        st.markdown(f'<div class="s-card"><div class="s-label">Interviews</div><div class="s-val" style="color:#34d399;">{status_counts.get("Interview",0)}</div></div>', unsafe_allow_html=True)
    with sc4:
        st.markdown(f'<div class="s-card"><div class="s-label">Offers</div><div class="s-val" style="color:#f472b6;">{status_counts.get("Offer",0)}</div></div>', unsafe_allow_html=True)
    with sc5:
        total = len(jobs)
        ir = round(status_counts.get("Interview",0) / total * 100) if total else 0
        st.markdown(f'<div class="s-card"><div class="s-label">Interview rate</div><div class="s-val" style="color:#fbbf24;">{ir}%</div></div>', unsafe_allow_html=True)

    st.markdown("")

    # Filter
    filter_status = st.selectbox("Filter by status", ["All"] + ["Applied","Interview","Rejected","Offer","Ghosted"], key="job_filter")
    filtered = jobs if filter_status == "All" else [j for j in jobs if j["status"] == filter_status]

    status_colors = {"Applied":"#818cf8","Interview":"#34d399","Rejected":"#ef4444","Offer":"#f472b6","Ghosted":"#64748b"}

    for j in reversed(filtered[-30:]):
        sc = status_colors.get(j["status"], "#64748b")
        cl_badge = '<span style="font-size:10px;color:#818cf8;background:rgba(129,140,248,0.12);padding:2px 8px;border-radius:4px;margin-left:8px;">📝 cover letter</span>' if j.get("has_cover_letter") else ""
        url_link = f' <a href="{j["url"]}" target="_blank" style="font-size:11px;color:#475569;text-decoration:none;">↗ link</a>' if j.get("url") else ""
        st.markdown(f"""
        <div class="job-row">
          <div>
            <span style="font-weight:600;color:#e2e8f0;font-size:14px;">{j["company"]}</span>
            <span style="color:#64748b;margin-left:8px;font-size:13px;">{j["role"]}</span>{cl_badge}{url_link}
            {f'<div style="font-size:12px;color:#475569;margin-top:2px;">{j.get("note","")}</div>' if j.get("note") else ""}
          </div>
          <div style="display:flex;align-items:center;gap:12px;">
            <span style="font-size:12px;color:#475569;font-family:'JetBrains Mono',monospace;">{j.get("date","")}</span>
            <span style="font-size:11px;font-weight:700;color:{sc};background:{sc}15;
            padding:3px 10px;border-radius:6px;text-transform:uppercase;letter-spacing:1px;
            font-family:'JetBrains Mono',monospace;">{j["status"]}</span>
          </div>
        </div>""", unsafe_allow_html=True)
else:
    st.info("No applications yet. Start adding above!")
