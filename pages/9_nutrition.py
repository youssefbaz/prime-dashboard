import streamlit as st
import re
from utils import load_data, get_week_info, GOAL_WEIGHT, START_WEIGHT

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

data = load_data()
wi   = get_week_info()
ws   = data.get("weights", {})
lw   = ws[sorted(ws.keys(), reverse=True)[0]] if ws else None

st.markdown('<p class="page-title">Nutrition planner</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Personalised meal plan based on your goals — powered by Spoonacular.</p>', unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────
def calc_tdee(weight, height, age, sex, activity_key):
    bmr = 10*weight + 6.25*height - 5*age + (5 if sex == "Male" else -161)
    mults = {"Sedentary (desk job)":1.2,"Lightly active (1–2x/week)":1.375,
             "Moderately active (3–5x/week)":1.55,"Very active (6–7x/week)":1.725}
    return round(bmr * mults.get(activity_key, 1.55))

def fetch_meal_plan(api_key, target_cal, diet, exclude):
    if not HAS_REQUESTS: return {"error":"requests not installed"}
    params = {"apiKey": api_key, "targetCalories": target_cal, "timeFrame": "day"}
    if diet:    params["diet"]    = diet
    if exclude: params["exclude"] = ",".join(exclude)
    try:
        r = requests.get("https://api.spoonacular.com/mealplans/generate", params=params, timeout=15)
        return r.json() if r.status_code == 200 else {"error": f"API {r.status_code}" if r.status_code != 402 else "daily_limit"}
    except Exception as e:
        return {"error": str(e)}

def fetch_recipe_detail(api_key, rid):
    if not HAS_REQUESTS: return None
    try:
        r = requests.get(f"https://api.spoonacular.com/recipes/{rid}/information",
                         params={"apiKey": api_key, "includeNutrition": True}, timeout=15)
        return r.json() if r.status_code == 200 else None
    except: return None

ALLERGY_MAP = {"Gluten":"gluten","Dairy":"dairy","Eggs":"egg","Nuts":"tree nuts",
               "Peanuts":"peanuts","Soy":"soy","Seafood":"seafood","Shellfish":"shellfish",
               "Pork":"pork","Onions":"onion","Salmon":"salmon"}
DIET_MAP    = {"No restriction":"","Vegetarian":"vegetarian","Vegan":"vegan",
               "Gluten-free":"gluten free","Ketogenic":"ketogenic","Paleo":"paleo"}
MEAL_LABELS = ["🍳 Breakfast","🍲 Lunch","🍽️ Dinner"]

# ── Session state ─────────────────────────────────────────
for k, v in {"np_step":1,"np_profile":{},"np_allergies":[],"np_diet":"No restriction",
             "np_plan":None,"np_details":{},"np_error":""}.items():
    if k not in st.session_state: st.session_state[k] = v

try:
    SPOON_KEY = st.secrets["SPOONACULAR_KEY"]
except Exception:
    SPOON_KEY = ""

# ── Step indicator ────────────────────────────────────────
step   = st.session_state.np_step
labels = ["Profile","Preferences","Your plan"]
scols  = st.columns(3)
for i, lbl in enumerate(labels):
    active = (i+1 == step); done = (i+1 < step)
    color  = "#818cf8" if active else ("#34d399" if done else "#334155")
    scols[i].markdown(
        f'<div style="text-align:center;padding:8px 0;border-bottom:2px solid {color};">'
        f'<span style="font-size:12px;font-weight:600;color:{color};text-transform:uppercase;'
        f'letter-spacing:1px;font-family:\'JetBrains Mono\',monospace;">{"✓ " if done else ""}{i+1}. {lbl}</span></div>',
        unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ════════════ STEP 1 — PROFILE ════════════════════════════
if step == 1:
    st.markdown('<div class="sec-title">Your profile</div>', unsafe_allow_html=True)
    p = st.session_state.np_profile
    s1, s2 = st.columns(2)
    with s1:
        sex    = st.radio("Sex", ["Male","Female"], horizontal=True, index=0 if p.get("sex","Male")=="Male" else 1)
        age    = st.number_input("Age", 16, 80, int(p.get("age",25)))
        height = st.number_input("Height (cm)", 140, 220, int(p.get("height",170)))
    with s2:
        weight      = st.number_input("Current weight (kg)", 40.0, 200.0, float(p.get("weight", float(lw if lw else START_WEIGHT))), step=0.5)
        goal_weight = st.number_input("Goal weight (kg)", 40.0, 200.0, float(p.get("goal_weight", GOAL_WEIGHT)), step=0.5)
        activity    = st.selectbox("Activity level",["Sedentary (desk job)","Lightly active (1–2x/week)","Moderately active (3–5x/week)","Very active (6–7x/week)"], index=2)

    goal_type    = st.selectbox("Goal", ["Lose weight (cut)","Gain muscle (bulk)","Maintain"], index=0)
    period_weeks = st.slider("Plan duration (weeks)", 4, 24, 8)

    tdee     = calc_tdee(weight, height, age, sex, activity)
    deficit  = 750 if (weight - goal_weight) / max(period_weeks/4,1) > 1 else 500
    if goal_type == "Lose weight (cut)":  target_cal = tdee - deficit;  goal_label = f"−{deficit} kcal deficit"
    elif goal_type == "Gain muscle (bulk)": target_cal = tdee + 300;    goal_label = "+300 kcal surplus"
    else:                                   target_cal = tdee;           goal_label = "maintenance"
    protein_g     = round(weight * (2.0 if "bulk" in goal_type else 1.8))
    weeks_to_goal = abs(round((weight - goal_weight) / (0.5 if "cut" in goal_type else 0.25))) if weight != goal_weight else 0

    st.markdown("<br>", unsafe_allow_html=True)
    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1: st.markdown(f'<div class="s-card"><div class="s-label">TDEE</div><div class="s-val" style="color:#818cf8;">{tdee}</div><div class="s-sub">kcal/day</div></div>', unsafe_allow_html=True)
    with pc2: st.markdown(f'<div class="s-card"><div class="s-label">Daily target</div><div class="s-val" style="color:#34d399;">{target_cal}</div><div class="s-sub">{goal_label}</div></div>', unsafe_allow_html=True)
    with pc3: st.markdown(f'<div class="s-card"><div class="s-label">Protein</div><div class="s-val" style="color:#fbbf24;">{protein_g}g</div><div class="s-sub">per day</div></div>', unsafe_allow_html=True)
    with pc4: st.markdown(f'<div class="s-card"><div class="s-label">Est. duration</div><div class="s-val" style="color:#f472b6;">{weeks_to_goal}w</div><div class="s-sub">to {goal_weight} kg</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Continue →", use_container_width=True):
        st.session_state.np_profile = dict(sex=sex, age=age, height=height, weight=weight,
            goal_weight=goal_weight, activity=activity, goal_type=goal_type,
            period_weeks=period_weeks, tdee=tdee, target_cal=target_cal, protein_g=protein_g)
        st.session_state.np_step = 2; st.rerun()

# ════════════ STEP 2 — PREFERENCES ════════════════════════
elif step == 2:
    st.markdown('<div class="sec-title">Dietary preferences</div>', unsafe_allow_html=True)
    diet = st.selectbox("Diet type", list(DIET_MAP.keys()),
                        index=list(DIET_MAP.keys()).index(st.session_state.get("np_diet","No restriction")))
    st.markdown("<br>**Allergies & exclusions:**", unsafe_allow_html=True)
    acols = st.columns(4)
    prev  = st.session_state.np_allergies
    selected_allergies = []
    for i, (label, val) in enumerate(ALLERGY_MAP.items()):
        with acols[i % 4]:
            if st.checkbox(label, value=(label in prev or val in prev), key=f"al_{label}"):
                selected_allergies.append(val)
    st.markdown("<br>", unsafe_allow_html=True)
    custom_ex = st.text_input("Other exclusions (comma-separated)", placeholder="e.g. mushrooms, cilantro")
    if custom_ex.strip():
        selected_allergies.extend([x.strip().lower() for x in custom_ex.split(",") if x.strip()])

    if not SPOON_KEY:
        st.warning("⚠️ No Spoonacular API key. Add `SPOONACULAR_KEY` to `.streamlit/secrets.toml`.")
        manual = st.text_input("Or enter key here (session only):", type="password", key="manual_key")
        if manual: SPOON_KEY = manual

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("← Back", use_container_width=True):
            st.session_state.np_step = 1; st.rerun()
    with b2:
        if st.button("✨ Generate meal plan", use_container_width=True, disabled=not SPOON_KEY):
            st.session_state.np_allergies = selected_allergies
            st.session_state.np_diet      = diet
            st.session_state.np_plan      = None
            st.session_state.np_details   = {}
            st.session_state.np_error     = ""
            profile   = st.session_state.np_profile
            diet_val  = DIET_MAP.get(diet, "")
            with st.spinner("Fetching your personalised meal plan…"):
                plan = fetch_meal_plan(SPOON_KEY, profile["target_cal"], diet_val, selected_allergies)
            if "error" in plan:
                st.session_state.np_error = ("Daily Spoonacular limit reached. Try again tomorrow."
                                             if plan["error"] == "daily_limit" else plan["error"])
            else:
                details = {}
                for meal in plan.get("meals", []):
                    rid = meal.get("id")
                    if rid:
                        d = fetch_recipe_detail(SPOON_KEY, rid)
                        if d: details[rid] = d
                st.session_state.np_plan    = plan
                st.session_state.np_details = details
            st.session_state.np_step = 3; st.rerun()

# ════════════ STEP 3 — RESULTS ════════════════════════════
elif step == 3:
    profile = st.session_state.np_profile
    plan    = st.session_state.np_plan
    details = st.session_state.np_details
    error   = st.session_state.np_error

    rb1, rb2 = st.columns([1, 3])
    with rb1:
        if st.button("← Edit profile"): st.session_state.np_step = 1; st.rerun()
    with rb2:
        if st.button("🔄 Regenerate plan", use_container_width=True): st.session_state.np_step = 2; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if error:
        st.markdown(f'<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:14px;padding:20px 24px;"><div style="font-size:15px;font-weight:600;color:#fca5a5;">⚠️ {error}</div></div>', unsafe_allow_html=True)

    elif plan:
        nutrients = plan.get("nutrients", {})
        meals     = plan.get("meals", [])

        # Nutrient cards
        st.markdown('<div class="sec-title">Daily targets</div>', unsafe_allow_html=True)
        nc1, nc2, nc3, nc4, nc5 = st.columns(5)
        for col, (lbl, val, color, sub) in zip([nc1,nc2,nc3,nc4,nc5], [
            ("Target cal",    profile["target_cal"],                     "#818cf8", "kcal/day"),
            ("Plan calories", round(nutrients.get("calories",0)),        "#34d399", "from Spoonacular"),
            ("Protein",       round(nutrients.get("protein",0)),         "#fbbf24", f"target {profile['protein_g']}g"),
            ("Fat",           round(nutrients.get("fat",0)),             "#f472b6", "grams"),
            ("Carbs",         round(nutrients.get("carbohydrates",0)),   "#60a5fa", "grams"),
        ]):
            col.markdown(f'<div class="s-card"><div class="s-label">{lbl}</div><div class="s-val" style="color:{color};font-size:22px;">{val}</div><div class="s-sub">{sub}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-title">Your meals</div>', unsafe_allow_html=True)

        for i, meal in enumerate(meals):
            rid     = meal.get("id")
            detail  = details.get(rid, {})
            title   = detail.get("title") or meal.get("title", f"Meal {i+1}")
            image   = detail.get("image","")
            src_url = detail.get("sourceUrl","")
            ready   = detail.get("readyInMinutes", meal.get("readyInMinutes","—"))
            servings= detail.get("servings", meal.get("servings",1))
            summary = re.sub(r'<[^>]+>', '', detail.get("summary",""))[:280] + "…" if detail.get("summary") else ""
            n_nut   = {n["name"]: round(n["amount"]) for n in detail.get("nutrition",{}).get("nutrients",[]) if n["name"] in ["Calories","Protein","Fat","Carbohydrates"]}
            meal_cal  = n_nut.get("Calories","—")
            meal_prot = n_nut.get("Protein","—")
            meal_icon = MEAL_LABELS[i] if i < len(MEAL_LABELS) else f"🍽️ Meal {i+1}"

            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
            border-radius:16px;padding:0;margin-bottom:20px;overflow:hidden;">
              <div style="padding:16px 20px 0;">
                <div style="font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;
                letter-spacing:1.5px;font-family:'JetBrains Mono',monospace;margin-bottom:6px;">{meal_icon}</div>
              </div>""", unsafe_allow_html=True)

            img_col, info_col = st.columns([1, 2])
            with img_col:
                if image:
                    st.markdown(f'<div style="padding:0 0 16px 20px;"><img src="{image}" style="width:100%;border-radius:12px;object-fit:cover;max-height:200px;" alt="{title}"></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="padding:0 0 16px 20px;height:160px;background:rgba(255,255,255,0.03);border-radius:12px;display:flex;align-items:center;justify-content:center;color:#334155;font-size:32px;">🍽️</div>', unsafe_allow_html=True)
            with info_col:
                st.markdown(f"""
                <div style="padding:4px 20px 16px 0;">
                  <div style="font-size:17px;font-weight:700;color:#f1f5f9;margin-bottom:8px;">{title}</div>
                  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;">
                    <span style="font-size:12px;background:rgba(129,140,248,0.1);color:#818cf8;padding:3px 10px;border-radius:6px;font-family:'JetBrains Mono',monospace;">🔥 {meal_cal} kcal</span>
                    <span style="font-size:12px;background:rgba(251,191,36,0.1);color:#fbbf24;padding:3px 10px;border-radius:6px;font-family:'JetBrains Mono',monospace;">💪 {meal_prot}g protein</span>
                    <span style="font-size:12px;background:rgba(255,255,255,0.05);color:#64748b;padding:3px 10px;border-radius:6px;font-family:'JetBrains Mono',monospace;">⏱ {ready} min</span>
                    <span style="font-size:12px;background:rgba(255,255,255,0.05);color:#64748b;padding:3px 10px;border-radius:6px;font-family:'JetBrains Mono',monospace;">🍽 {servings} serving{"s" if servings!=1 else ""}</span>
                  </div>
                  {f'<div style="font-size:13px;color:#64748b;line-height:1.6;margin-bottom:10px;">{summary}</div>' if summary else ""}
                  {f'<a href="{src_url}" target="_blank" style="font-size:12px;color:#818cf8;text-decoration:none;font-family:JetBrains Mono,monospace;">→ Full recipe</a>' if src_url else ""}
                </div>""", unsafe_allow_html=True)

                ingredients = detail.get("extendedIngredients", [])
                if ingredients:
                    with st.expander(f"🛒 Ingredients ({len(ingredients)})"):
                        ing_cols = st.columns(2)
                        for j, ing in enumerate(ingredients):
                            g_data   = ing.get("measures",{}).get("metric",{})
                            g_val    = g_data.get("amount","")
                            g_unit   = g_data.get("unitShort","")
                            display  = f"{round(g_val)}{g_unit}" if g_val else f"{ing.get('amount','')} {ing.get('unit','')}".strip()
                            with ing_cols[j % 2]:
                                st.markdown(f'<div style="font-size:13px;color:#94a3b8;padding:3px 0;"><span style="color:#475569;">{display}</span> {ing.get("name","")}</div>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="background:rgba(239,68,68,0.05);border:1px solid rgba(239,68,68,0.12);border-radius:14px;padding:16px 20px;margin-bottom:12px;">
          <div style="font-size:13px;font-weight:600;color:#fca5a5;margin-bottom:6px;">❌ Avoid</div>
          <div style="font-size:13px;color:#94a3b8;line-height:1.8;">Sugary drinks · Processed snacks · Late-night eating after 11 PM · Fried food · Alcohol</div>
        </div>
        <div style="background:rgba(16,185,129,0.05);border:1px solid rgba(16,185,129,0.12);border-radius:14px;padding:16px 20px;">
          <div style="font-size:13px;font-weight:600;color:#6ee7b7;margin-bottom:6px;">💡 Daily habits</div>
          <div style="font-size:13px;color:#94a3b8;line-height:1.8;">Protein first at every meal · 2.5L water/day · Eat slowly · Meal prep Sunday · Sleep 7–8h</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("Something went wrong. Click ← Edit profile to try again.")
