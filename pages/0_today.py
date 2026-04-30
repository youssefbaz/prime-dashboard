import streamlit as st
import datetime
import json
from utils import (load_data, save_data, get_week_info, QUOTES, SCHEDULE_TEMPLATE,
                   ML_BY_WEEK, AWS_BY_WEEK, PRACTICE_BY_WEEK, JOB_BY_WEEK, get_plan_config,
                   C, FOCUS_COLORS, threshold_color)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

data     = load_data()
wi       = get_week_info(data)
today    = wi["today"]
now      = wi["now"]
day_name = wi["day_name"]
week_num = wi["week_num"]
day_num  = wi["day_num"]
total_days = wi["total_days"]
today_str  = wi["today_str"]
pct        = wi["pct"]
hour_now   = wi["hour_now"]
plan_start, plan_weeks, plan_end = get_plan_config(data)

# ── Page header ───────────────────────────────────────────
day_labels = {
    "Mon": ("Momentum Monday",   "🔥"),
    "Tue": ("Turbo Tuesday",     "⚡"),
    "Wed": ("Grind Wednesday",   "🧱"),
    "Thu": ("Target Thursday",   "🎯"),
    "Fri": ("Focus Friday",      "🏁"),
    "Sat": ("Ship Saturday",     "🚀"),
    "Sun": ("Recovery Sunday",   "🧘"),
}
vibe, vibe_emoji = day_labels.get(day_name, ("Study Day", "📋"))

st.markdown(f'<div style="font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#818cf8;font-family:\'JetBrains Mono\',monospace;margin-bottom:6px;">Day {day_num} of {total_days} &nbsp;·&nbsp; Week {week_num}/{plan_weeks}</div>', unsafe_allow_html=True)
st.markdown(f'<p class="page-title">{vibe_emoji} {today.strftime("%A, %B %d")}</p>', unsafe_allow_html=True)
st.markdown(f'<p class="page-sub">{vibe} &nbsp;·&nbsp; {now.strftime("%I:%M %p")}</p>', unsafe_allow_html=True)

# ── Layout: left (weather + quote + priorities) | right (schedule + progress) ──
col_left, col_right = st.columns([5, 4], gap="large")

# ═══════════════════════════════════════════════════════════
# LEFT COLUMN
# ═══════════════════════════════════════════════════════════
with col_left:

    # ── Weather widget ────────────────────────────────────
    city = data.get("weather_city", "Paris")
    st.markdown(f'<div class="sec-title">🌤️ Weather · {city}</div>', unsafe_allow_html=True)

    with st.expander("📍 Change city"):
        with st.form("city_form"):
            new_city = st.text_input("City name", value=city)
            if st.form_submit_button("Update"):
                if new_city.strip() and new_city.strip() != city:
                    data["weather_city"] = new_city.strip()
                    save_data(data)
                    for k in [k for k in st.session_state if k.startswith("weather_")]:
                        del st.session_state[k]
                    st.rerun()

    weather_key = f"weather_{today_str}_{city}"
    if weather_key not in st.session_state and HAS_REQUESTS:
        try:
            r = requests.get(f"https://wttr.in/{city}?format=j1", timeout=8)
            if r.status_code == 200:
                st.session_state[weather_key] = r.json()
        except Exception:
            st.session_state[weather_key] = None

    weather_data = st.session_state.get(weather_key)

    if weather_data:
        try:
            current  = weather_data["current_condition"][0]
            temp_c   = current.get("temp_C", "—")
            feels    = current.get("FeelsLikeC", "—")
            humidity = current.get("humidity", "—")
            wind_kmph = current.get("windspeedKmph", "—")
            desc     = current["weatherDesc"][0]["value"] if current.get("weatherDesc") else "—"
            uv_index = current.get("uvIndex", "—")

            # Weather icon mapping
            weather_icons = {
                "sunny": "☀️", "clear": "☀️", "partly cloudy": "⛅",
                "overcast": "☁️", "cloudy": "☁️", "mist": "🌫️",
                "fog": "🌫️", "rain": "🌧️", "drizzle": "🌦️",
                "thunder": "⛈️", "snow": "❄️", "blizzard": "🌨️",
                "haze": "🌫️", "light rain": "🌦️",
            }
            w_icon = "🌡️"
            for k, v in weather_icons.items():
                if k in desc.lower():
                    w_icon = v
                    break

            # Advice based on conditions
            advice = ""
            if int(temp_c) > 30:
                advice = "Stay hydrated — hot day!"
            elif int(temp_c) < 15:
                advice = "Layer up before heading out."
            elif "rain" in desc.lower():
                advice = "Bring an umbrella."
            else:
                advice = "Good conditions for outdoor training."

            st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(99,102,241,0.06),rgba(56,189,248,0.04));
border:1px solid rgba(99,102,241,0.12);border-radius:18px;padding:20px 24px;margin-bottom:20px;">
  <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px;">
    <div style="font-size:52px;line-height:1;">{w_icon}</div>
    <div>
      <div style="font-size:36px;font-weight:900;color:#f1f5f9;font-family:'Outfit';line-height:1;">{temp_c}°C</div>
      <div style="font-size:14px;color:#94a3b8;margin-top:2px;">{desc}</div>
    </div>
  </div>
  <div style="display:flex;gap:20px;flex-wrap:wrap;">
    <div style="text-align:center;">
      <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:1px;font-family:'JetBrains Mono';">Feels like</div>
      <div style="font-size:15px;font-weight:700;color:#cbd5e1;">{feels}°C</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:1px;font-family:'JetBrains Mono';">Humidity</div>
      <div style="font-size:15px;font-weight:700;color:#60a5fa;">{humidity}%</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:1px;font-family:'JetBrains Mono';">Wind</div>
      <div style="font-size:15px;font-weight:700;color:#34d399;">{wind_kmph} km/h</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:1px;font-family:'JetBrains Mono';">UV Index</div>
      <div style="font-size:15px;font-weight:700;color:#fbbf24;">{uv_index}</div>
    </div>
  </div>
  <div style="margin-top:12px;font-size:12px;color:#6366f1;font-weight:600;">💡 {advice}</div>
</div>
""", unsafe_allow_html=True)
        except Exception:
            st.info("Weather data unavailable right now.")
    else:
        st.markdown("""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
border-radius:18px;padding:24px;text-align:center;margin-bottom:20px;">
  <div style="font-size:32px;margin-bottom:8px;">🌡️</div>
  <div style="font-size:14px;color:#64748b;">Weather unavailable (no internet or wttr.in down)</div>
</div>
""", unsafe_allow_html=True)

    # ── Motivational quote (refreshes every 3 hours) ─────────
    st.markdown('<div class="sec-title">💬 Quote</div>', unsafe_allow_html=True)

    # Key changes every 3-hour block: 00-03, 03-06, ..., 21-24
    block     = now.hour // 3
    quote_key = f"ai_quote_{today_str}_{block}"
    fallback_quote = QUOTES[(today.timetuple().tm_yday * 8 + block) % len(QUOTES)]

    if quote_key not in st.session_state:
        fetched = False
        try:
            gemini_key = st.secrets.get("GEMINI_API_KEY", "")
            if gemini_key and HAS_REQUESTS:
                prompt = f"""Generate ONE short motivational quote (max 25 words) for a high-performer
on a {vibe} ({today.strftime('%A')}). Be original and punchy.
Return ONLY valid JSON: {{"text": "...", "author": "..."}} where author is the real person or 'Unknown'."""
                r = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}",
                    headers={"Content-Type": "application/json"},
                    json={"contents": [{"parts": [{"text": prompt}]}],
                          "generationConfig": {"maxOutputTokens": 120, "temperature": 0.9}},
                    timeout=10,
                )
                if r.status_code == 200:
                    raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                    s, e = raw.find("{"), raw.rfind("}") + 1
                    st.session_state[quote_key] = json.loads(raw[s:e])
                    fetched = True
        except Exception:
            pass
        if not fetched:
            st.session_state[quote_key] = fallback_quote

    q      = st.session_state[quote_key]
    text   = q["text"] if isinstance(q, dict) else q
    author = q.get("author", "") if isinstance(q, dict) else ""
    st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(99,102,241,0.06),rgba(236,72,153,0.04));
border:1px solid rgba(99,102,241,0.12);border-radius:14px;padding:18px 24px;margin-bottom:16px;">
  <div style="font-size:16px;color:#cbd5e1;font-style:italic;line-height:1.7;">"{text}"</div>
  <div style="font-size:12px;color:#818cf8;margin-top:10px;font-family:'JetBrains Mono',monospace;">— {author}</div>
</div>""", unsafe_allow_html=True)

    # ── Top 3 priorities ─────────────────────────────────
    st.markdown('<div class="sec-title">🎯 Today\'s Top 3 Priorities</div>', unsafe_allow_html=True)

    saved_priorities = data.get("today_priorities", [])
    # Only load priorities saved for today
    if isinstance(saved_priorities, list) and len(saved_priorities) > 0:
        if isinstance(saved_priorities[0], dict):
            today_prios = [p for p in saved_priorities if p.get("date") == today_str]
            prio_texts  = [p["text"] for p in today_prios[:3]]
        else:
            prio_texts = saved_priorities[:3]
    else:
        prio_texts = []

    while len(prio_texts) < 3:
        prio_texts.append("")

    with st.form("priorities_form", clear_on_submit=False):
        p1 = st.text_input("Priority 1", value=prio_texts[0], placeholder="Most important thing today…", key="prio_1")
        p2 = st.text_input("Priority 2", value=prio_texts[1], placeholder="Second priority…",           key="prio_2")
        p3 = st.text_input("Priority 3", value=prio_texts[2], placeholder="Third priority…",            key="prio_3")
        if st.form_submit_button("💾 Save priorities", use_container_width=True):
            new_prios = [
                {"date": today_str, "text": p.strip()}
                for p in [p1, p2, p3] if p.strip()
            ]
            # Keep older dates, replace today
            other = [p for p in data.get("today_priorities", [])
                     if isinstance(p, dict) and p.get("date") != today_str]
            data["today_priorities"] = other + new_prios
            save_data(data)
            st.success("Priorities saved!")
            st.rerun()

    # Show saved priorities as styled list
    saved_today = [p for p in data.get("today_priorities", [])
                   if isinstance(p, dict) and p.get("date") == today_str]
    if saved_today:
        nums = ["1️⃣", "2️⃣", "3️⃣"]
        items_html = "".join(
            f'<div style="display:flex;align-items:center;gap:12px;padding:10px 0;'
            f'border-bottom:1px solid rgba(255,255,255,0.05);">'
            f'<span style="font-size:18px;">{nums[i]}</span>'
            f'<span style="font-size:14px;font-weight:600;color:#e2e8f0;">{p["text"]}</span>'
            f'</div>'
            for i, p in enumerate(saved_today[:3])
        )
        st.markdown(f"""
<div style="background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.15);
border-radius:14px;padding:16px 20px;margin-top:12px;">
  {items_html}
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# RIGHT COLUMN
# ═══════════════════════════════════════════════════════════
with col_right:

    # ── Course progress card ──────────────────────────────
    st.markdown('<div class="sec-title">📈 Course Progress</div>', unsafe_allow_html=True)

    days_done   = max(0, (today - plan_start).days)
    days_left   = max(0, (plan_end - today).days)
    bar_pct     = min(100, round((days_done / max(1, total_days)) * 100))
    bar_color   = threshold_color(bar_pct, 80, 50)

    # Current week focus
    w = max(1, min(plan_weeks, week_num))
    if day_name != "Sun":
        week_focus = {
            "ML":       ML_BY_WEEK.get(w, {}).get(day_name, "ML Study"),
            "AWS":      AWS_BY_WEEK.get(w, {}).get(day_name, "AWS Study"),
            "Practice": PRACTICE_BY_WEEK.get(w, {}).get(day_name, "Coding"),
            "Job":      JOB_BY_WEEK.get(w, {}).get(day_name, "Job Hunt"),
        }
    else:
        week_focus = {
            "ML": "Weekly Review", "AWS": "Review & Plan",
            "Practice": "Rest", "Job": "Weekly Review",
        }

    st.markdown(f"""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.08);
border-radius:18px;padding:20px 22px;margin-bottom:20px;">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:12px;">
    <span style="font-size:13px;font-weight:700;color:#f1f5f9;">Week {week_num} of {plan_weeks}</span>
    <span style="font-size:12px;color:#64748b;font-family:'JetBrains Mono';">Day {day_num} · {bar_pct}% complete</span>
  </div>
  <div class="pbar-outer" style="margin:0 0 16px;">
    <div class="pbar-inner" style="width:{bar_pct}%;background:linear-gradient(90deg,{bar_color},{bar_color}99);"></div>
  </div>
  <div style="display:flex;gap:6px;flex-wrap:wrap;">
    {"".join(f'<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:6px 12px;"><div style="font-size:9px;color:{FOCUS_COLORS.get(cat, "#818cf8")};text-transform:uppercase;letter-spacing:1px;font-family:\'JetBrains Mono\';">{cat}</div><div style="font-size:12px;color:#cbd5e1;margin-top:2px;font-weight:500;">{task}</div></div>' for cat, task in week_focus.items())}
  </div>
  <div style="margin-top:14px;font-size:12px;color:#475569;font-family:'JetBrains Mono';">{days_left} days remaining in plan</div>
</div>
""", unsafe_allow_html=True)

    # ── Today's schedule ──────────────────────────────────
    st.markdown('<div class="sec-title">🗓️ Today\'s Schedule</div>', unsafe_allow_html=True)

    if day_name == "Sun":
        st.markdown("""
<div style="background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.12);
border-radius:14px;padding:18px 22px;margin-bottom:8px;">
  <div style="font-size:16px;font-weight:600;color:#a5b4fc;">🧘 Light day — rest & weekly review</div>
  <div style="font-size:13px;color:#64748b;margin-top:6px;">Reflect · Plan next week · Recharge</div>
</div>""", unsafe_allow_html=True)
    else:
        for b in SCHEDULE_TEMPLATE:
            active     = b["h"][0] <= hour_now < b["h"][1]
            passed     = hour_now >= b["h"][1]
            cls        = "sch-active" if active else "sch-normal"
            time_color = "#818cf8" if active else ("#334155" if passed else "#475569")
            label_color = "#f1f5f9" if active else ("#4b5563" if passed else "#cbd5e1")
            now_badge  = '<span class="now-tag">NOW</span>' if active else ""
            checkmark  = '<span style="color:#334155;font-size:12px;">✓</span>' if passed and not active else ""

            st.markdown(f"""
<div class="{cls}" style="{'opacity:0.5;' if passed and not active else ''}">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div>
      <span style="font-size:12px;font-family:'JetBrains Mono';color:{time_color};font-weight:600;">{b["time"]}</span>
      <span style="margin-left:10px;font-size:13px;font-weight:600;color:{label_color};">{b["label"]}</span>
    </div>
    <div style="display:flex;gap:8px;align-items:center;">{checkmark}{now_badge}</div>
  </div>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="prime-footer">Start strong. Stay consistent. Win the day. 🚀</div>', unsafe_allow_html=True)
