import datetime
import json
import os
import streamlit as st

# ─────────────────────────────────────────────────────────
# PLAN CONFIG
# ─────────────────────────────────────────────────────────
_DEFAULT_PLAN_START = datetime.date(2026, 3, 23)
_DEFAULT_PLAN_WEEKS = 8
PLAN_START   = _DEFAULT_PLAN_START                                  # kept for backward compat
PLAN_END     = _DEFAULT_PLAN_START + datetime.timedelta(weeks=_DEFAULT_PLAN_WEEKS)
GOAL_WEIGHT  = 75.0
START_WEIGHT = 86.5
DATA_FILE    = "prime_data.json"

# ─────────────────────────────────────────────────────────
# PERSISTENCE
# ─────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"daily_checks": {}, "weights": {}, "notes": {}, "missed_acks": [],
            "jobs": [], "quiz_history": {}, "flash_scores": {}, "cover_letters": [],
            "focus_sessions": []}

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

# ─────────────────────────────────────────────────────────
# DATE / WEEK HELPERS
# ─────────────────────────────────────────────────────────
def get_plan_config(data=None):
    """Return (plan_start, plan_weeks, plan_end) from saved data or defaults."""
    if data is None:
        data = load_data()
    start_str = data.get("plan_start")
    weeks = int(data.get("plan_weeks", _DEFAULT_PLAN_WEEKS))
    if start_str:
        try:
            start = datetime.date.fromisoformat(start_str)
        except ValueError:
            start = _DEFAULT_PLAN_START
    else:
        start = _DEFAULT_PLAN_START
    end = start + datetime.timedelta(weeks=weeks)
    return start, weeks, end

def get_week_info(data=None):
    if data is None:
        data = load_data()
    plan_start, plan_weeks, plan_end = get_plan_config(data)
    today      = datetime.date.today()
    now        = datetime.datetime.now()
    day_name   = today.strftime("%a")
    day_num    = (today - plan_start).days + 1
    total_days = (plan_end - plan_start).days
    week_num   = max(1, min(plan_weeks, (day_num - 1) // 7 + 1))
    has_started= today >= plan_start
    today_str  = today.isoformat()
    pct        = min(100, max(0, round((day_num / total_days) * 100))) if total_days > 0 else 0
    hour_now   = now.hour + now.minute / 60
    return dict(today=today, now=now, day_name=day_name, day_num=day_num,
                week_num=week_num, total_days=total_days, has_started=has_started,
                today_str=today_str, pct=pct, hour_now=hour_now,
                plan_start=plan_start, plan_end=plan_end, plan_weeks=plan_weeks)

def calc_streak(data):
    wi = get_week_info(data)
    streak = 0
    cd = wi["today"] - datetime.timedelta(days=1)
    while cd >= wi["plan_start"]:
        ds = cd.isoformat()
        if cd.strftime("%a") == "Sun" or ds in data.get("daily_checks", {}):
            streak += 1; cd -= datetime.timedelta(days=1)
        else:
            break
    return streak

# ─────────────────────────────────────────────────────────
# OLLAMA
# ─────────────────────────────────────────────────────────
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

def ollama_available():
    if not HAS_REQUESTS: return False
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return r.status_code == 200
    except: return False

def ollama_models():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if r.status_code == 200:
            return [m["name"] for m in r.json().get("models", [])]
    except: pass
    return []

def get_default_model():
    models = ollama_models()
    for m in models:
        if "qwen3" in m.lower(): return m
    return models[0] if models else "qwen3:14b"

def ollama_generate(prompt, model=None, max_tokens=1500):
    if not HAS_REQUESTS: return ""
    if not model: model = get_default_model()
    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": model, "prompt": prompt, "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.7}
        }, timeout=120)
        if r.status_code == 200:
            return r.json().get("response", "")
    except Exception as e:
        return f"Error: {e}"
    return ""

# ─────────────────────────────────────────────────────────
# SPACED REPETITION (SM-2)
# ─────────────────────────────────────────────────────────
def sm2_update(card_id, quality, flash_data):
    card     = flash_data.get(card_id, {"ef": 2.5, "interval": 1, "reps": 0,
                                         "next_review": datetime.date.today().isoformat()})
    ef       = card.get("ef", 2.5)
    interval = card.get("interval", 1)
    reps     = card.get("reps", 0)
    if quality >= 3:
        if reps == 0:   interval = 1
        elif reps == 1: interval = 6
        else:           interval = round(interval * ef)
        reps += 1
    else:
        reps = 0; interval = 1
    ef          = max(1.3, ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    next_review = (datetime.date.today() + datetime.timedelta(days=interval)).isoformat()
    flash_data[card_id] = {"ef": round(ef, 2), "interval": interval,
                            "reps": reps, "next_review": next_review, "last_quality": quality}
    return flash_data

def get_due_cards(flash_data, all_cards):
    today_str = datetime.date.today().isoformat()
    due, new  = [], []
    for i, _ in enumerate(all_cards):
        cid = str(i)
        if cid in flash_data:
            if flash_data[cid].get("next_review", "") <= today_str:
                due.append((i, flash_data[cid].get("ef", 2.5)))
        else:
            new.append(i)
    due.sort(key=lambda x: x[1])
    return [d[0] for d in due] + new[:3]

# ─────────────────────────────────────────────────────────
# GAMIFICATION
# ─────────────────────────────────────────────────────────
XP_PER_CHECK      = 15
XP_PER_JOB        = 50
XP_PER_FOCUS_MIN  = 1
XP_PER_QUIZ       = 30
XP_PER_FLASHCARD  = 20
XP_PER_WEIGHT     = 25

def calc_xp(data):
    xp = 0
    # Checklist XP
    for checks in data.get("daily_checks", {}).values():
        xp += sum(XP_PER_CHECK for v in checks.values() if v)
    
    # Focus XP
    for s in data.get("focus_sessions", []):
        xp += s.get("minutes", 0) * XP_PER_FOCUS_MIN
    
    # Job XP
    xp += len(data.get("jobs", [])) * XP_PER_JOB
    
    # Quiz XP
    xp += len(data.get("quiz_history", {})) * XP_PER_QUIZ

    # Flashcard XP
    xp += len(data.get("flash_scores", {})) * XP_PER_FLASHCARD
        
    # Weight log XP
    xp += len(data.get("weights", {})) * XP_PER_WEIGHT
    
    return xp

def get_level(xp):
    # Lvl 1: 0, Lvl 2: 500, Lvl 3: 1200, etc.
    # Simple quadratic: XP = 250 * L * (L-1)
    # L = (1 + sqrt(1 + 4*XP/250)) / 2
    import math
    if xp <= 0: return 1, 0, 500
    level = math.floor((1 + math.sqrt(1 + 8 * xp / 500)) / 2)
    current_lvl_xp = 250 * level * (level - 1)
    next_lvl_xp    = 250 * (level + 1) * level
    progress       = xp - current_lvl_xp
    required       = next_lvl_xp - current_lvl_xp
    return level, progress, required

# ─────────────────────────────────────────────────────────
# STATIC DATA
# ─────────────────────────────────────────────────────────
QUOTES = [
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"text": "Consistency is what transforms average into excellence.", "author": "Unknown"},
    {"text": "Hard choices, easy life. Easy choices, hard life.", "author": "Jerzy Gregorek"},
    {"text": "Discipline equals freedom.", "author": "Jocko Willink"},
    {"text": "We are what we repeatedly do. Excellence is not an act, but a habit.", "author": "Aristotle"},
    {"text": "The man who moves a mountain begins by carrying away small stones.", "author": "Confucius"},
    {"text": "Without data, you're just another person with an opinion.", "author": "W. Edwards Deming"},
    {"text": "Talk is cheap. Show me the code.", "author": "Linus Torvalds"},
    {"text": "In God we trust. All others must bring data.", "author": "W. Edwards Deming"},
    {"text": "A year from now you'll wish you had started today.", "author": "Karen Lamb"},
    {"text": "Fall seven times, stand up eight.", "author": "Japanese Proverb"},
    {"text": "Success is the sum of small efforts repeated day in and day out.", "author": "Robert Collier"},
    {"text": "What you do every day matters more than what you do once in a while.", "author": "Gretchen Rubin"},
    {"text": "Every master was once a disaster.", "author": "T. Harv Eker"},
    {"text": "Your future self is watching you right now through memories.", "author": "Unknown"},
]

def get_daily_quote(date):
    return QUOTES[date.timetuple().tm_yday % len(QUOTES)]

TRAINING = {
    "Mon": {"act": "⚽ Football",    "dur": "2h",  "focus": "Cardio + team play"},
    "Tue": {"act": "🏋️ Gym – Push", "dur": "1h",  "focus": "Chest & triceps"},
    "Wed": {"act": "🚶 Walk / Core", "dur": "45m", "focus": "Active recovery"},
    "Thu": {"act": "⚽ Football",    "dur": "2h",  "focus": "Endurance"},
    "Fri": {"act": "🏋️ Gym – Pull", "dur": "1h",  "focus": "Back & biceps"},
    "Sat": {"act": "🏋️ Full Body",  "dur": "1h",  "focus": "Strength & burn"},
    "Sun": {"act": "🧘 Stretch",    "dur": "—",   "focus": "Recovery"},
}

CHECKLIST = [
    "Applied to 1–2 jobs", "Completed 2h AWS study + lab", "Went to gym 🏋️",
    "Completed 2h ML learning + notebook", "Practiced coding / LLM project (1.5h)",
    "Review + GitHub commit", "Drank 2.5L water 💧", "Ate within meal plan", "Hit 8,000+ steps",
]

ML_BY_WEEK = {
    1: {"Mon":"Linear Regression","Tue":"Logistic Regression","Wed":"Cost Functions & Gradient Descent","Thu":"Regularization (L1/L2)","Fri":"Feature Engineering","Sat":"Mini Project: Predict Housing Prices"},
    2: {"Mon":"Decision Trees","Tue":"Random Forests","Wed":"Ensemble Methods (Bagging)","Thu":"Gradient Boosting (XGBoost)","Fri":"LightGBM & CatBoost","Sat":"Mini Project: Classification Challenge"},
    3: {"Mon":"SVM","Tue":"K-Means Clustering","Wed":"DBSCAN & Hierarchical Clustering","Thu":"PCA","Fri":"Model Evaluation Metrics","Sat":"Mini Project: Customer Segmentation"},
    4: {"Mon":"Neural Networks Basics","Tue":"Activation Functions & Backprop","Wed":"CNNs for Images","Thu":"RNNs & LSTMs","Fri":"Transfer Learning","Sat":"Mini Project: Image Classifier"},
    5: {"Mon":"NLP Fundamentals","Tue":"TF-IDF & Word Embeddings","Wed":"Transformers & Attention","Thu":"BERT & Fine-tuning","Fri":"LLMs & Prompt Engineering","Sat":"Mini Project: Sentiment Analysis"},
    6: {"Mon":"Cross-validation","Tue":"Hyperparameter Tuning","Wed":"Bias-Variance Tradeoff","Thu":"Overfitting & Regularization","Fri":"Feature Selection","Sat":"Mini Project: End-to-End Pipeline"},
    7: {"Mon":"Time Series (ARIMA)","Tue":"Prophet & LSTM","Wed":"Bayesian Methods","Thu":"Reinforcement Learning Intro","Fri":"Explainable AI (SHAP/LIME)","Sat":"Mini Project: Stock Prediction"},
    8: {"Mon":"AutoML Overview","Tue":"ML System Design","Wed":"A/B Testing","Thu":"Data Pipelines & ETL","Fri":"MLOps","Sat":"Capstone: Full ML Pipeline"},
}
AWS_BY_WEEK = {
    1: {"Mon":"IAM & Security","Tue":"S3 & Storage","Wed":"EC2 Instances & AMIs","Thu":"Auto Scaling & ELB","Fri":"VPC & Networking","Sat":"Lab: Deploy Web App"},
    2: {"Mon":"RDS & Aurora","Tue":"DynamoDB","Wed":"Lambda Functions","Thu":"API Gateway","Fri":"CloudWatch","Sat":"Lab: Serverless REST API"},
    3: {"Mon":"S3 Advanced","Tue":"CloudFront & Route 53","Wed":"ECS & Docker","Thu":"EKS & Kubernetes","Fri":"SNS, SQS & EventBridge","Sat":"Lab: Event-Driven Architecture"},
    4: {"Mon":"CloudFormation","Tue":"AWS Config & SSM","Wed":"Athena & Glue","Thu":"Redshift & Data Lakes","Fri":"Kinesis Streaming","Sat":"Lab: Data Pipeline"},
    5: {"Mon":"IAM Advanced","Tue":"Secrets Manager & KMS","Wed":"SageMaker Basics","Thu":"SageMaker Training","Fri":"Step Functions & MLOps","Sat":"Lab: ML on SageMaker"},
    6: {"Mon":"CodePipeline & CI/CD","Tue":"CodeBuild & Deploy","Wed":"Multi-AZ & DR","Thu":"Global Accelerator","Fri":"Cost Optimization","Sat":"Lab: Full CI/CD Pipeline"},
    7: {"Mon":"Well-Architected","Tue":"Compliance & Governance","Wed":"Microservices Patterns","Thu":"Serverless Patterns","Fri":"Hybrid Cloud","Sat":"Lab: Architect a Solution"},
    8: {"Mon":"Exam Prep: Compute","Tue":"Exam Prep: Networking","Wed":"Exam Prep: Database","Thu":"Exam Prep: Serverless","Fri":"Practice Exam","Sat":"Capstone: End-to-End on AWS"},
}
PRACTICE_BY_WEEK = {
    1: {"Mon":"LeetCode – Arrays","Tue":"SQL – Basic Joins","Wed":"Pandas – DataFrames","Thu":"LeetCode – Strings","Fri":"SQL – Subqueries","Sat":"Build: Portfolio Page"},
    2: {"Mon":"LeetCode – Hash Maps","Tue":"SQL – Window Functions","Wed":"Pandas – GroupBy & Merge","Thu":"LeetCode – Two Pointers","Fri":"SQL – CTEs","Sat":"Build: Data Cleaning Script"},
    3: {"Mon":"LeetCode – Stacks","Tue":"SQL – Complex Joins","Wed":"NumPy – Vectorization","Thu":"LeetCode – Binary Search","Fri":"SQL – Optimization","Sat":"Build: EDA Dashboard"},
    4: {"Mon":"LeetCode – Linked Lists","Tue":"SQL – Stored Procedures","Wed":"PyTorch – Tensors","Thu":"LeetCode – Trees","Fri":"SQL – Analytics Functions","Sat":"Build: Neural Net from Scratch"},
    5: {"Mon":"LeetCode – Graphs","Tue":"SQL – Performance Tuning","Wed":"TensorFlow – Keras","Thu":"LeetCode – DP","Fri":"SQL – Data Modeling","Sat":"Build: NLP App"},
    6: {"Mon":"LeetCode – Sorting","Tue":"SQL – Real Interview Qs","Wed":"Streamlit App","Thu":"LeetCode – Recursion","Fri":"SQL – Case Studies","Sat":"Build: LLM Chatbot"},
    7: {"Mon":"LeetCode – Heap","Tue":"SQL – Advanced Analytics","Wed":"FastAPI – REST","Thu":"LeetCode – Backtracking","Fri":"SQL – Mock Interview","Sat":"Build: ML API"},
    8: {"Mon":"LeetCode – Design","Tue":"SQL – Final Review","Wed":"Docker & Deployment","Thu":"LeetCode – Mock Timed","Fri":"Full Mock Interview","Sat":"Capstone: Deploy Full App"},
}
JOB_BY_WEEK = {
    1: {"Mon":"Resume Tailoring","Tue":"LinkedIn Optimization","Wed":"Cover Letter Template","Thu":"Referrals & DMs","Fri":"Mock Interview Prep","Sat":"Portfolio Building"},
    2: {"Mon":"Apply to 3 Jobs","Tue":"LinkedIn Outreach","Wed":"Tailor Resume for DS","Thu":"Follow up on Apps","Fri":"Practice Elevator Pitch","Sat":"GitHub README Polish"},
    3: {"Mon":"Apply to 3 Jobs","Tue":"Informational Interviews","Wed":"Tailor Resume for ML Eng","Thu":"Company Research","Fri":"Behavioral STAR Stories","Sat":"Blog Post #1"},
    4: {"Mon":"Apply to 3 Jobs","Tue":"Recruiter Messages","Wed":"Portfolio Case Study","Thu":"Follow up Round 2","Fri":"Technical Phone Screen Prep","Sat":"Record Mock Interview"},
    5: {"Mon":"Apply to 3 Jobs","Tue":"Network at Virtual Event","Wed":"Salary Research","Thu":"Apply to Stretch Roles","Fri":"System Design Practice","Sat":"Blog Post #2"},
    6: {"Mon":"Apply to 3 Jobs","Tue":"Second-degree Connections","Wed":"Update Portfolio","Thu":"Negotiate Practice","Fri":"Whiteboard Coding Prep","Sat":"Open Source Contribution"},
    7: {"Mon":"Apply to 5 Jobs","Tue":"Final LinkedIn Push","Wed":"Thank-you Notes","Thu":"Follow All Leads","Fri":"Full Mock Interview","Sat":"Final Portfolio Review"},
    8: {"Mon":"Apply to 5 Jobs","Tue":"Final Outreach Blitz","Wed":"Prep for Onsites","Thu":"Company Deep Dives","Fri":"Final Mock Round","Sat":"Celebrate & Reflect 🎉"},
}

SCHEDULE_TEMPLATE = [
    {"time": "10:00 – 11:00", "label": "💼 Job hunt",    "cat": "job",      "h": (10,   11)},
    {"time": "11:00 – 13:00", "label": "☁️ AWS deep dive","cat": "aws",      "h": (11,   13)},
    {"time": "13:00 – 13:30", "label": "🏃 Pre-gym",     "cat": None,       "h": (13,   13.5)},
    {"time": "13:30 – 14:30", "label": "🏋️ Gym",        "cat": None,       "h": (13.5, 14.5)},
    {"time": "14:30 – 15:00", "label": "🍽️ Lunch",      "cat": None,       "h": (14.5, 15)},
    {"time": "15:00 – 15:30", "label": "💤 Nap",         "cat": None,       "h": (15,   15.5)},
    {"time": "15:30 – 17:30", "label": "🧠 ML deep dive","cat": "ml",       "h": (15.5, 17.5)},
    {"time": "17:30 – 17:45", "label": "☕ Break",       "cat": None,       "h": (17.5, 17.75)},
    {"time": "17:45 – 19:15", "label": "💻 Practice",    "cat": "practice", "h": (17.75,19.25)},
    {"time": "19:15 – 19:45", "label": "📓 Review",      "cat": None,       "h": (19.25,19.75)},
]

FLASHCARDS = [
    {"q":"What is the bias-variance tradeoff?","a":"Bias = error from wrong assumptions (underfitting). Variance = error from sensitivity to training data (overfitting). The sweet spot minimises total error.","cat":"ML"},
    {"q":"What is L1 vs L2 regularization?","a":"L1 (Lasso) adds absolute weights → can zero features. L2 (Ridge) adds squared weights → shrinks all weights but none to zero.","cat":"ML"},
    {"q":"Explain precision vs recall.","a":"Precision = TP/(TP+FP). Recall = TP/(TP+FN). Precision cares about false alarms; recall cares about missing positives.","cat":"ML"},
    {"q":"What is gradient descent?","a":"Iteratively adjusts parameters in the direction of steepest decrease of the loss function. Learning rate controls step size.","cat":"ML"},
    {"q":"What is cross-validation?","a":"Split data into k folds, train on k-1, test on 1, rotate. More reliable than a single split.","cat":"ML"},
    {"q":"Explain ROC-AUC.","a":"ROC plots TPR vs FPR at every threshold. AUC=1 perfect, 0.5 random. Use PR-AUC for imbalanced datasets.","cat":"ML"},
    {"q":"Random forest vs gradient boosting?","a":"RF: parallel trees, bagging, reduces variance. GB: sequential trees, each corrects previous errors, reduces bias. GB often more accurate but prone to overfitting.","cat":"ML"},
    {"q":"What is the vanishing gradient problem?","a":"Gradients shrink to near-zero in deep networks during backpropagation, making early layers learn very slowly. Solved by ReLU, skip connections, batch norm.","cat":"ML"},
    {"q":"What are transformers?","a":"Architecture using self-attention to process sequences in parallel. Foundation of BERT and GPT. Key: Query, Key, Value attention matrices.","cat":"ML"},
    {"q":"What is IAM in AWS?","a":"Identity and Access Management. Controls who can do what on which AWS resources via users, groups, roles, and policies.","cat":"AWS"},
    {"q":"S3 vs EBS vs EFS?","a":"S3: object storage, unlimited, HTTP. EBS: block storage attached to one EC2. EFS: network file system shared across EC2 instances.","cat":"AWS"},
    {"q":"Lambda vs EC2?","a":"Lambda: serverless, pay per invocation, max 15 min. EC2: full server, pay per hour, you manage scaling. Lambda for event-driven, EC2 for long-running.","cat":"AWS"},
    {"q":"What is CloudFormation?","a":"Infrastructure as Code. Define AWS resources in YAML/JSON templates, deploy as stacks. Version-controlled, reproducible infrastructure.","cat":"AWS"},
    {"q":"What is a SQL JOIN?","a":"Combines rows from 2+ tables on a related column. INNER: matching rows. LEFT: all left + matching right. FULL: all rows from both.","cat":"SQL"},
    {"q":"Window functions vs GROUP BY?","a":"GROUP BY collapses rows into groups. Window functions compute across rows without collapsing — you keep all rows.","cat":"SQL"},
    {"q":"What is a CTE?","a":"Common Table Expression. Named temp result set defined with WITH clause. Makes complex queries readable. Can be recursive.","cat":"SQL"},
]

QUIZ_QUESTIONS = [
    {"q":"You're building a fraud detection model. Only 0.1% of transactions are fraudulent. What metric and why?","a":"Accuracy is misleading (99.9% by predicting all non-fraud). Use Precision-Recall AUC or F1. Recall matters most — missing fraud is costly.","cat":"ML Theory"},
    {"q":"Design an ML pipeline for a recommendation system.","a":"Data collection → Feature engineering (collab + content) → Model (matrix factorisation or DL) → A/B test → API serving with cache → Monitor drift.","cat":"System Design"},
    {"q":"Tell me about a time you solved a difficult technical problem.","a":"STAR: Situation, Task, Action, Result. Be specific about YOUR contribution. Quantify the outcome.","cat":"Behavioral"},
    {"q":"Bagging vs boosting — explain the difference.","a":"Bagging: parallel models on random subsets, aggregate (reduces variance). Boosting: sequential, each fixes previous errors (reduces bias). RF = bagging, XGBoost = boosting.","cat":"ML Theory"},
    {"q":"How would you handle missing data?","a":"1) Remove rows. 2) Impute mean/median/mode. 3) Model-based (KNN, MICE). 4) Add 'missing' indicator feature. 5) Use algorithms that handle it natively (XGBoost). Depends on % missing and mechanism.","cat":"ML Theory"},
    {"q":"Design a real-time fraud detection system on AWS.","a":"Kinesis → Lambda (feature extraction) → SageMaker endpoint → DynamoDB (decisions) → SNS (alerts) → S3 (logs) → CloudWatch monitoring.","cat":"System Design"},
    {"q":"How do you detect and handle data drift in production?","a":"Monitor feature distributions (KS test, PSI), prediction distributions, and performance. Retrain on recent data, use sliding windows, set alerts. SageMaker Model Monitor.","cat":"System Design"},
]
