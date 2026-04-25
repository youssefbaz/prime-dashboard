import streamlit as st
import datetime
import pandas as pd
from utils import load_data, get_week_info, CHECKLIST, GOAL_WEIGHT

data = load_data()
wi   = get_week_info()
today = wi["today"]

st.markdown('<p class="page-title">Analytics</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Your progress over time — consistency is the metric that matters.</p>', unsafe_allow_html=True)

all_checks = data.get("daily_checks", {})
ws         = data.get("weights", {})
jobs       = data.get("jobs", [])
focus_ss   = data.get("focus_sessions", [])

# ── Summary cards ─────────────────────────────────────────
total_days_logged = len(all_checks)
total_tasks_done  = sum(sum(1 for v in checks.values() if v) for checks in all_checks.values())
total_jobs        = len(jobs)
interviews        = sum(1 for j in jobs if j.get("status") == "Interview")
focus_min         = sum(s.get("minutes", 0) for s in focus_ss)

sc1, sc2, sc3, sc4, sc5 = st.columns(5)
with sc1:
    st.markdown(f'<div class="s-card"><div class="s-label">Days logged</div><div class="s-val" style="color:#818cf8;">{total_days_logged}</div></div>', unsafe_allow_html=True)
with sc2:
    st.markdown(f'<div class="s-card"><div class="s-label">Tasks done</div><div class="s-val" style="color:#34d399;">{total_tasks_done}</div></div>', unsafe_allow_html=True)
with sc3:
    st.markdown(f'<div class="s-card"><div class="s-label">Jobs applied</div><div class="s-val" style="color:#fbbf24;">{total_jobs}</div></div>', unsafe_allow_html=True)
with sc4:
    st.markdown(f'<div class="s-card"><div class="s-label">Interviews</div><div class="s-val" style="color:#f472b6;">{interviews}</div></div>', unsafe_allow_html=True)
with sc5:
    fh = focus_min // 60
    st.markdown(f'<div class="s-card"><div class="s-label">Focus</div><div class="s-val" style="color:#a78bfa;">{fh}h</div><div class="s-sub">{focus_min} min</div></div>', unsafe_allow_html=True)

st.markdown("")

# ── Tabs ──────────────────────────────────────────────────
t1, t2, t3, t4 = st.tabs(["📋 Checklist", "⚖️ Weight", "💼 Jobs pipeline", "⏱ Focus"])

with t1:
    if all_checks:
        chart_data = []
        for d_str, checks in sorted(all_checks.items()):
            completed = sum(1 for v in checks.values() if v)
            chart_data.append({"Date": datetime.date.fromisoformat(d_str),
                                "Completed": completed, "Total": len(CHECKLIST)})
        df = pd.DataFrame(chart_data).set_index("Date")

        # Weekly comparison
        this_week_start = today - datetime.timedelta(days=today.weekday())
        last_week_start = this_week_start - datetime.timedelta(days=7)
        this_w = sum(c["Completed"] for c in chart_data if c["Date"] >= this_week_start)
        last_w = sum(c["Completed"] for c in chart_data if last_week_start <= c["Date"] < this_week_start)

        wc1, wc2, wc3 = st.columns(3)
        with wc1:
            avg = round(df["Completed"].mean(), 1) if len(df) else 0
            st.markdown(f'<div class="s-card"><div class="s-label">Daily avg</div><div class="s-val" style="color:#818cf8;">{avg}</div><div class="s-sub">tasks/day</div></div>', unsafe_allow_html=True)
        with wc2:
            st.markdown(f'<div class="s-card"><div class="s-label">This week</div><div class="s-val" style="color:#34d399;">{this_w}</div></div>', unsafe_allow_html=True)
        with wc3:
            arrow = "▲" if this_w >= last_w else "▼"
            col   = "#34d399" if this_w >= last_w else "#ef4444"
            st.markdown(f'<div class="s-card"><div class="s-label">Last week</div><div class="s-val" style="color:{col};">{last_w} {arrow}</div></div>', unsafe_allow_html=True)

        st.markdown("")
        st.markdown("**Daily checklist completion**")
        st.bar_chart(df["Completed"], use_container_width=True, color="#818cf8")
    else:
        st.info("No checklist data yet. Start checking off tasks on the Dashboard!")

with t2:
    if ws:
        wd_list = [(datetime.date.fromisoformat(d), w) for d, w in sorted(ws.items())]
        df_w    = pd.DataFrame(wd_list, columns=["Date","Weight (kg)"]).set_index("Date")

        ww1, ww2, ww3 = st.columns(3)
        start_w = wd_list[0][1]
        curr_w  = wd_list[-1][1]
        lost    = round(start_w - curr_w, 1)
        remain  = round(curr_w - GOAL_WEIGHT, 1)
        with ww1:
            st.markdown(f'<div class="s-card"><div class="s-label">Current</div><div class="s-val" style="color:#f472b6;">{curr_w}</div><div class="s-sub">kg</div></div>', unsafe_allow_html=True)
        with ww2:
            col = "#34d399" if lost >= 0 else "#ef4444"
            st.markdown(f'<div class="s-card"><div class="s-label">Lost so far</div><div class="s-val" style="color:{col};">{"−" if lost>0 else "+"}{abs(lost)}</div><div class="s-sub">kg</div></div>', unsafe_allow_html=True)
        with ww3:
            col = "#34d399" if remain <= 0 else "#fbbf24"
            st.markdown(f'<div class="s-card"><div class="s-label">To goal</div><div class="s-val" style="color:{col};">{max(0,remain)}</div><div class="s-sub">kg remaining</div></div>', unsafe_allow_html=True)

        st.markdown("")
        st.markdown("**Weight over time**")
        st.line_chart(df_w, use_container_width=True, color="#f472b6")

        # Goal line annotation
        st.markdown(f'<div style="text-align:center;font-size:13px;color:#475569;margin-top:4px;">Goal weight: <span style="color:#34d399;font-weight:600;">{GOAL_WEIGHT} kg</span></div>', unsafe_allow_html=True)
    else:
        st.info("No weight data yet. Log your weight from the Dashboard sidebar!")

with t3:
    if jobs:
        pipeline = {}
        for j in jobs:
            pipeline[j["status"]] = pipeline.get(j["status"], 0) + 1

        # Funnel view
        order  = ["Applied","Interview","Offer","Rejected","Ghosted"]
        colors = {"Applied":"#818cf8","Interview":"#34d399","Offer":"#f472b6","Rejected":"#ef4444","Ghosted":"#64748b"}
        for status in order:
            count = pipeline.get(status, 0)
            if count == 0: continue
            pct   = round(count / len(jobs) * 100)
            col   = colors.get(status, "#64748b")
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
            border-radius:10px;padding:12px 18px;margin-bottom:8px;display:flex;align-items:center;gap:16px;">
              <div style="min-width:90px;font-size:12px;font-weight:600;color:{col};
              text-transform:uppercase;letter-spacing:1px;font-family:'JetBrains Mono',monospace;">{status}</div>
              <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:99px;height:10px;overflow:hidden;">
                <div style="width:{pct}%;height:100%;background:{col};border-radius:99px;"></div>
              </div>
              <div style="min-width:60px;text-align:right;font-size:14px;font-weight:700;
              color:#e2e8f0;font-family:'JetBrains Mono',monospace;">{count} <span style="font-size:12px;color:#475569;">({pct}%)</span></div>
            </div>""", unsafe_allow_html=True)

        # Recent applications timeline
        st.markdown("")
        st.markdown("**Application timeline (last 30 days)**")
        thirty_ago = (today - datetime.timedelta(days=30)).isoformat()
        recent     = [(j["date"], 1) for j in jobs if j.get("date","") >= thirty_ago]
        if recent:
            df_j = pd.DataFrame(recent, columns=["Date","Applications"])
            df_j["Date"] = pd.to_datetime(df_j["Date"])
            df_j = df_j.set_index("Date").resample("D").sum()
            st.bar_chart(df_j, use_container_width=True, color="#34d399")
    else:
        st.info("No job data yet. Start logging applications in the Jobs page!")

with t4:
    if focus_ss:
        # Daily total minutes
        per_day = {}
        per_label = {}
        for s in focus_ss:
            d = s.get("date","")
            per_day[d]   = per_day.get(d, 0) + s.get("minutes", 0)
            l = s.get("label", "Other")
            per_label[l] = per_label.get(l, 0) + s.get("minutes", 0)

        days_logged = len(per_day)
        avg_min     = round(focus_min / days_logged) if days_logged else 0
        best_day    = max(per_day.items(), key=lambda x: x[1]) if per_day else ("—", 0)
        today_min   = per_day.get(today.isoformat(), 0)

        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            st.markdown(f'<div class="s-card"><div class="s-label">Today</div><div class="s-val" style="color:#a78bfa;">{today_min}</div><div class="s-sub">minutes</div></div>', unsafe_allow_html=True)
        with fc2:
            st.markdown(f'<div class="s-card"><div class="s-label">Daily avg</div><div class="s-val" style="color:#818cf8;">{avg_min}</div><div class="s-sub">min/day</div></div>', unsafe_allow_html=True)
        with fc3:
            st.markdown(f'<div class="s-card"><div class="s-label">Best day</div><div class="s-val" style="color:#34d399;">{best_day[1]}</div><div class="s-sub">{best_day[0]}</div></div>', unsafe_allow_html=True)
        with fc4:
            st.markdown(f'<div class="s-card"><div class="s-label">Sessions</div><div class="s-val" style="color:#f472b6;">{len(focus_ss)}</div><div class="s-sub">total</div></div>', unsafe_allow_html=True)

        st.markdown("")
        st.markdown("**Focus minutes per day**")
        df_f = pd.DataFrame([(datetime.date.fromisoformat(d), m) for d,m in sorted(per_day.items())],
                            columns=["Date","Minutes"]).set_index("Date")
        st.bar_chart(df_f, use_container_width=True, color="#a78bfa")

        st.markdown("**Time by category**")
        for lbl, mn in sorted(per_label.items(), key=lambda x: -x[1]):
            pct = round(mn / focus_min * 100) if focus_min else 0
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
            border-radius:10px;padding:10px 16px;margin-bottom:6px;display:flex;align-items:center;gap:14px;">
              <div style="min-width:120px;font-size:13px;color:#cbd5e1;font-weight:500;">{lbl}</div>
              <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:99px;height:8px;overflow:hidden;">
                <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#818cf8,#a78bfa);border-radius:99px;"></div>
              </div>
              <div style="min-width:80px;text-align:right;font-size:13px;font-weight:700;color:#e2e8f0;font-family:'JetBrains Mono',monospace;">{mn}m <span style="color:#475569;font-size:11px;">({pct}%)</span></div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No focus sessions yet. Run a timer on the Timer page — sessions log automatically when they complete.")
