import streamlit as st
import datetime
import json
import os
import pandas as pd
import random
import time

# ─────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────
PLAN_START = datetime.date(2026, 3, 23)
PLAN_END = datetime.date(2026, 5, 18)
GOAL_WEIGHT = 75.0
START_WEIGHT = 86.5

st.set_page_config(page_title="Prime Dashboard", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")

# ─────────────────────────────────────────────────────────
# PERSISTENCE
# ─────────────────────────────────────────────────────────
DATA_FILE = "prime_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"daily_checks": {}, "weights": {}, "notes": {}, "missed_acks": [], "jobs": [], "quiz_history": {}, "flash_scores": {}}

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

data = load_data()

# ─────────────────────────────────────────────────────────
# DYNAMIC SCHEDULE DATA (by week)
# ─────────────────────────────────────────────────────────
ML_BY_WEEK = {
    1: {"Mon": "Linear Regression", "Tue": "Logistic Regression", "Wed": "Cost Functions & Gradient Descent", "Thu": "Regularization (L1/L2)", "Fri": "Feature Engineering", "Sat": "Mini Project: Predict Housing Prices"},
    2: {"Mon": "Decision Trees", "Tue": "Random Forests", "Wed": "Ensemble Methods (Bagging)", "Thu": "Gradient Boosting (XGBoost)", "Fri": "LightGBM & CatBoost", "Sat": "Mini Project: Classification Challenge"},
    3: {"Mon": "SVM (Support Vector Machines)", "Tue": "K-Means Clustering", "Wed": "DBSCAN & Hierarchical Clustering", "Thu": "PCA (Dimensionality Reduction)", "Fri": "Model Evaluation Metrics", "Sat": "Mini Project: Customer Segmentation"},
    4: {"Mon": "Neural Networks Basics", "Tue": "Activation Functions & Backprop", "Wed": "CNNs for Images", "Thu": "RNNs & LSTMs", "Fri": "Transfer Learning", "Sat": "Mini Project: Image Classifier"},
    5: {"Mon": "NLP Fundamentals", "Tue": "TF-IDF & Word Embeddings", "Wed": "Transformers & Attention", "Thu": "BERT & Fine-tuning", "Fri": "LLMs & Prompt Engineering", "Sat": "Mini Project: Sentiment Analysis"},
    6: {"Mon": "Cross-validation Techniques", "Tue": "Hyperparameter Tuning", "Wed": "Bias-Variance Tradeoff", "Thu": "Overfitting & Regularization", "Fri": "Feature Selection Methods", "Sat": "Mini Project: End-to-End Pipeline"},
    7: {"Mon": "Time Series (ARIMA)", "Tue": "Prophet & LSTM for Time Series", "Wed": "Bayesian Methods", "Thu": "Reinforcement Learning Intro", "Fri": "Explainable AI (SHAP/LIME)", "Sat": "Mini Project: Stock Prediction"},
    8: {"Mon": "AutoML Overview", "Tue": "ML System Design Patterns", "Wed": "A/B Testing & Experimentation", "Thu": "Data Pipelines & ETL", "Fri": "ML in Production (MLOps)", "Sat": "Capstone: Full ML Pipeline"},
}

AWS_BY_WEEK = {
    1: {"Mon": "IAM & Security Basics", "Tue": "S3 & Storage Classes", "Wed": "EC2 Instances & AMIs", "Thu": "EC2 Auto Scaling & ELB", "Fri": "VPC & Networking", "Sat": "Lab: Deploy Web App on EC2"},
    2: {"Mon": "RDS & Aurora", "Tue": "DynamoDB", "Wed": "Lambda Functions", "Thu": "API Gateway", "Fri": "CloudWatch & Monitoring", "Sat": "Lab: Serverless REST API"},
    3: {"Mon": "S3 Advanced (Lifecycle, Versioning)", "Tue": "CloudFront & Route 53", "Wed": "ECS & Docker on AWS", "Thu": "EKS & Kubernetes", "Fri": "SNS, SQS & EventBridge", "Sat": "Lab: Event-Driven Architecture"},
    4: {"Mon": "CloudFormation", "Tue": "AWS Config & Systems Manager", "Wed": "Athena & Glue", "Thu": "Redshift & Data Lakes", "Fri": "Kinesis Streaming", "Sat": "Lab: Data Pipeline"},
    5: {"Mon": "IAM Advanced (Roles, Policies)", "Tue": "Secrets Manager & KMS", "Wed": "SageMaker Basics", "Thu": "SageMaker Training & Endpoints", "Fri": "Step Functions & MLOps", "Sat": "Lab: ML on SageMaker"},
    6: {"Mon": "CodePipeline & CI/CD", "Tue": "CodeBuild & CodeDeploy", "Wed": "Multi-AZ & Disaster Recovery", "Thu": "Global Accelerator & Caching", "Fri": "Cost Optimization & Billing", "Sat": "Lab: Full CI/CD Pipeline"},
    7: {"Mon": "Well-Architected Framework", "Tue": "Compliance & Governance", "Wed": "Microservices Patterns", "Thu": "Serverless Patterns", "Fri": "Hybrid Cloud & Direct Connect", "Sat": "Lab: Architect a Solution"},
    8: {"Mon": "Exam Prep: Compute & Storage", "Tue": "Exam Prep: Networking & Security", "Wed": "Exam Prep: Database & Analytics", "Thu": "Exam Prep: Serverless & Containers", "Fri": "Practice Exam", "Sat": "Capstone: End-to-End on AWS"},
}

PRACTICE_BY_WEEK = {
    1: {"Mon": "LeetCode – Arrays", "Tue": "SQL – Basic Joins", "Wed": "Pandas – DataFrames", "Thu": "LeetCode – Strings", "Fri": "SQL – Subqueries", "Sat": "Build: Portfolio Page"},
    2: {"Mon": "LeetCode – Hash Maps", "Tue": "SQL – Window Functions", "Wed": "Pandas – GroupBy & Merge", "Thu": "LeetCode – Two Pointers", "Fri": "SQL – CTEs", "Sat": "Build: Data Cleaning Script"},
    3: {"Mon": "LeetCode – Stacks & Queues", "Tue": "SQL – Complex Joins", "Wed": "NumPy – Vectorization", "Thu": "LeetCode – Binary Search", "Fri": "SQL – Optimization", "Sat": "Build: EDA Dashboard"},
    4: {"Mon": "LeetCode – Linked Lists", "Tue": "SQL – Stored Procedures", "Wed": "PyTorch – Tensors", "Thu": "LeetCode – Trees", "Fri": "SQL – Analytics Functions", "Sat": "Build: Neural Net from Scratch"},
    5: {"Mon": "LeetCode – Graphs", "Tue": "SQL – Performance Tuning", "Wed": "TensorFlow – Keras", "Thu": "LeetCode – Dynamic Programming", "Fri": "SQL – Data Modeling", "Sat": "Build: NLP App with HuggingFace"},
    6: {"Mon": "LeetCode – Sorting", "Tue": "SQL – Real Interview Qs", "Wed": "Streamlit App", "Thu": "LeetCode – Recursion", "Fri": "SQL – Case Studies", "Sat": "Build: LLM Chatbot"},
    7: {"Mon": "LeetCode – Heap & Priority Queue", "Tue": "SQL – Advanced Analytics", "Wed": "FastAPI – REST Endpoints", "Thu": "LeetCode – Backtracking", "Fri": "SQL – Mock Interview", "Sat": "Build: ML API with FastAPI"},
    8: {"Mon": "LeetCode – Design Problems", "Tue": "SQL – Final Review", "Wed": "Docker & Deployment", "Thu": "LeetCode – Mock Timed", "Fri": "Full Mock Interview", "Sat": "Capstone: Deploy Full App"},
}

JOB_BY_WEEK = {
    1: {"Mon": "Resume Tailoring", "Tue": "LinkedIn Optimization", "Wed": "Cover Letter Template", "Thu": "Referrals & DMs", "Fri": "Mock Interview Prep", "Sat": "Portfolio Building"},
    2: {"Mon": "Apply to 3 Jobs", "Tue": "LinkedIn Outreach (5 people)", "Wed": "Tailor Resume for DS", "Thu": "Follow up on Apps", "Fri": "Practice Elevator Pitch", "Sat": "GitHub README Polish"},
    3: {"Mon": "Apply to 3 Jobs", "Tue": "Informational Interviews", "Wed": "Tailor Resume for ML Eng", "Thu": "Company Research", "Fri": "Behavioral STAR Stories", "Sat": "Blog Post #1"},
    4: {"Mon": "Apply to 3 Jobs", "Tue": "Recruiter Messages", "Wed": "Portfolio Case Study", "Thu": "Follow up Round 2", "Fri": "Technical Phone Screen Prep", "Sat": "Record Mock Interview"},
    5: {"Mon": "Apply to 3 Jobs", "Tue": "Network at Virtual Event", "Wed": "Salary Research", "Thu": "Apply to Stretch Roles", "Fri": "System Design Practice", "Sat": "Blog Post #2"},
    6: {"Mon": "Apply to 3 Jobs", "Tue": "Second-degree Connections", "Wed": "Update Portfolio with Projects", "Thu": "Negotiate Practice", "Fri": "Whiteboard Coding Prep", "Sat": "Open Source Contribution"},
    7: {"Mon": "Apply to 5 Jobs", "Tue": "Final LinkedIn Push", "Wed": "Thank-you Notes", "Thu": "Follow All Leads", "Fri": "Full Mock Interview", "Sat": "Final Portfolio Review"},
    8: {"Mon": "Apply to 5 Jobs", "Tue": "Final Outreach Blitz", "Wed": "Prep for Onsites", "Thu": "Company Deep Dives", "Fri": "Final Mock Round", "Sat": "Celebrate & Reflect 🎉"},
}

TRAINING = {
    "Mon": {"act": "⚽ Football", "dur": "2h", "focus": "Cardio + team play"},
    "Tue": {"act": "🏋️ Gym – Push", "dur": "1h", "focus": "Chest & triceps"},
    "Wed": {"act": "🚶 Walk / Core", "dur": "45m", "focus": "Active recovery"},
    "Thu": {"act": "⚽ Football", "dur": "2h", "focus": "Endurance"},
    "Fri": {"act": "🏋️ Gym – Pull", "dur": "1h", "focus": "Back & biceps"},
    "Sat": {"act": "🏋️ Full Body", "dur": "1h", "focus": "Strength & burn"},
    "Sun": {"act": "🧘 Stretch", "dur": "—", "focus": "Recovery"},
}

MEALS = [
    {"time": "9:30 AM", "name": "Breakfast", "icon": "🍳", "desc": "2 eggs + cheese + pain de mie + coffee + fruit", "kcal": "400–500"},
    {"time": "1:00 PM", "name": "Lunch", "icon": "🍲", "desc": "Protein + carbs + veggies + olive oil", "kcal": "500–600"},
    {"time": "7:00 PM", "name": "Dinner", "icon": "🥗", "desc": "Light protein + veggies/salad", "kcal": "400–500"},
    {"time": "10:00 PM", "name": "Snack", "icon": "🍎", "desc": "Greek yogurt + berries OR fruit + nuts", "kcal": "200–250"},
]

CHECKLIST = [
    "Applied to 1–2 jobs", "Completed 2h AWS study + lab", "Went to gym 🏋️",
    "Completed 2h ML learning + notebook", "Practiced coding / LLM project (1.5h)",
    "Review + GitHub commit", "Drank 2.5L water 💧", "Ate within meal plan", "Hit 8,000+ steps",
]

# ─────────────────────────────────────────────────────────
# FLASHCARDS DATA
# ─────────────────────────────────────────────────────────
FLASHCARDS = [
    {"q": "What is the bias-variance tradeoff?", "a": "Bias = error from wrong assumptions (underfitting). Variance = error from sensitivity to training data (overfitting). The tradeoff is finding the sweet spot between the two.", "cat": "ML"},
    {"q": "What is L1 vs L2 regularization?", "a": "L1 (Lasso) adds absolute value of weights → can zero out features (feature selection). L2 (Ridge) adds squared weights → shrinks all weights but keeps them non-zero.", "cat": "ML"},
    {"q": "Explain precision vs recall.", "a": "Precision = TP/(TP+FP) — of predicted positives, how many are correct. Recall = TP/(TP+FN) — of actual positives, how many did we find.", "cat": "ML"},
    {"q": "What is gradient descent?", "a": "Optimization algorithm that iteratively adjusts parameters in the direction of steepest decrease of the loss function. Learning rate controls step size.", "cat": "ML"},
    {"q": "What is cross-validation?", "a": "Technique to evaluate model performance by splitting data into k folds, training on k-1 and testing on 1, rotating through all folds. Reduces overfitting to a single train/test split.", "cat": "ML"},
    {"q": "Explain the ROC-AUC curve.", "a": "ROC plots True Positive Rate vs False Positive Rate at different thresholds. AUC = area under this curve. AUC=1 is perfect, AUC=0.5 is random.", "cat": "ML"},
    {"q": "What is a confusion matrix?", "a": "A 2x2 table showing TP, TN, FP, FN. Used to evaluate classification models beyond simple accuracy.", "cat": "ML"},
    {"q": "Explain random forest vs gradient boosting.", "a": "Random Forest: parallel trees, bagging, reduces variance. Gradient Boosting: sequential trees, each corrects previous errors, reduces bias. GB often more accurate but prone to overfitting.", "cat": "ML"},
    {"q": "What is the vanishing gradient problem?", "a": "In deep networks, gradients become very small during backpropagation through many layers, causing early layers to learn extremely slowly. Solved by ReLU, skip connections, batch norm.", "cat": "ML"},
    {"q": "What are transformers?", "a": "Architecture using self-attention mechanism to process sequences in parallel (not sequentially like RNNs). Foundation of BERT, GPT. Key: Query, Key, Value attention.", "cat": "ML"},
    {"q": "What is IAM in AWS?", "a": "Identity and Access Management. Controls who (authentication) can do what (authorization) on which AWS resources. Uses users, groups, roles, and policies.", "cat": "AWS"},
    {"q": "S3 vs EBS vs EFS?", "a": "S3: object storage, unlimited, accessed via HTTP. EBS: block storage attached to one EC2. EFS: network file system, shared across EC2 instances.", "cat": "AWS"},
    {"q": "What is a VPC?", "a": "Virtual Private Cloud — your own isolated network in AWS. Contains subnets (public/private), route tables, internet gateways, NAT gateways, security groups.", "cat": "AWS"},
    {"q": "Lambda vs EC2?", "a": "Lambda: serverless, pay per invocation, auto-scales, max 15min. EC2: full server, pay per hour, you manage scaling. Lambda for event-driven, EC2 for long-running.", "cat": "AWS"},
    {"q": "What is CloudFormation?", "a": "Infrastructure as Code (IaC) service. Define AWS resources in YAML/JSON templates, deploy as stacks. Enables reproducible, version-controlled infrastructure.", "cat": "AWS"},
    {"q": "Explain SageMaker.", "a": "Fully managed ML service. Provides notebooks, training jobs, hyperparameter tuning, model hosting, and MLOps pipelines. Supports built-in algorithms and custom containers.", "cat": "AWS"},
    {"q": "What is a SQL JOIN?", "a": "Combines rows from 2+ tables based on a related column. INNER: matching rows only. LEFT: all left + matching right. FULL: all rows from both.", "cat": "SQL"},
    {"q": "Window functions vs GROUP BY?", "a": "GROUP BY collapses rows into groups. Window functions (OVER, PARTITION BY) compute values across rows without collapsing — you keep all rows.", "cat": "SQL"},
    {"q": "What is a CTE?", "a": "Common Table Expression. A named temporary result set defined with WITH clause. Makes complex queries readable. Can be recursive.", "cat": "SQL"},
    {"q": "Explain indexing in databases.", "a": "Indexes are data structures (B-tree, hash) that speed up reads at the cost of slower writes and extra storage. Like a book's index — find data without scanning every row.", "cat": "SQL"},
]

# ─────────────────────────────────────────────────────────
# INTERVIEW QUIZ DATA
# ─────────────────────────────────────────────────────────
QUIZ_QUESTIONS = [
    {"q": "You're building a model to detect fraudulent transactions. Only 0.1% of transactions are fraudulent. What metric would you use and why?", "a": "Accuracy would be misleading (99.9% by predicting all non-fraud). Use Precision-Recall AUC, F1-score, or recall at a fixed precision threshold. Recall matters most — you don't want to miss fraud.", "cat": "ML Theory"},
    {"q": "Explain how you would design an ML pipeline for a recommendation system.", "a": "1) Data collection (user behavior, items). 2) Feature engineering (collaborative filtering, content-based features). 3) Model: matrix factorization or deep learning. 4) A/B test. 5) Serve via API with caching. 6) Monitor for drift.", "cat": "System Design"},
    {"q": "Tell me about a time you solved a difficult technical problem.", "a": "Use STAR: Situation (context), Task (what was needed), Action (what you did specifically), Result (measurable outcome). Be specific about YOUR contribution.", "cat": "Behavioral"},
    {"q": "What is the difference between bagging and boosting?", "a": "Bagging: train models in parallel on random subsets, aggregate (reduces variance). Boosting: train models sequentially, each fixing previous errors (reduces bias). Random Forest = bagging, XGBoost = boosting.", "cat": "ML Theory"},
    {"q": "How would you handle missing data?", "a": "Options: 1) Remove rows (if few). 2) Impute with mean/median/mode. 3) Use model-based imputation (KNN, MICE). 4) Create a 'missing' indicator feature. 5) Use algorithms that handle missing values (XGBoost). Choice depends on % missing and mechanism (MCAR/MAR/MNAR).", "cat": "ML Theory"},
    {"q": "Design a real-time fraud detection system on AWS.", "a": "Kinesis Data Streams → Lambda for feature extraction → SageMaker endpoint for inference → DynamoDB for decisions → SNS for alerts → S3 for logging → CloudWatch monitoring. Use Step Functions for orchestration.", "cat": "System Design"},
    {"q": "Why do you want to be a Data Scientist?", "a": "Connect to: 1) Passion for finding patterns in data. 2) Impact — DS decisions affect real users/business. 3) Continuous learning — field evolves fast. 4) Bridge between technical and business. Be authentic, give specific examples.", "cat": "Behavioral"},
    {"q": "What is feature importance and how do you calculate it?", "a": "Measures how much each feature contributes to predictions. Methods: 1) Tree-based (Gini importance). 2) Permutation importance. 3) SHAP values (model-agnostic, best). 4) Correlation analysis. 5) L1 regularization coefficients.", "cat": "ML Theory"},
    {"q": "How would you architect a data lake on AWS?", "a": "S3 as storage (raw/processed/curated zones) → Glue for ETL & catalog → Athena for ad-hoc queries → Redshift for analytics → Lake Formation for governance → IAM for access control. Use Parquet format for efficiency.", "cat": "System Design"},
    {"q": "Describe a project where you had to communicate technical results to non-technical stakeholders.", "a": "STAR method. Focus on: how you translated complex metrics into business impact, what visualizations you used, how you handled pushback or confusion, and the outcome/decision that resulted.", "cat": "Behavioral"},
    {"q": "What is the difference between batch and online learning?", "a": "Batch: train on entire dataset at once, retrain periodically. Online: update model incrementally with each new data point. Online is better for streaming data and concept drift, but harder to debug.", "cat": "ML Theory"},
    {"q": "How do you detect and handle data drift in production?", "a": "Monitor: 1) Feature distributions (KS test, PSI). 2) Prediction distributions. 3) Model performance metrics. Handle: retrain on recent data, use sliding windows, set up alerts. AWS: SageMaker Model Monitor.", "cat": "System Design"},
]

# ─────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Outfit:wght@300;400;500;600;700;800;900&display=swap');
.stApp { background: linear-gradient(145deg, #0a0a0f 0%, #111127 50%, #0d1117 100%) !important; font-family: 'Outfit', sans-serif !important; }
[data-testid="stSidebar"] { background: #0d0d18 !important; border-right: 1px solid rgba(255,255,255,0.06) !important; }
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { max-width: 1100px !important; padding-top: 2rem !important; }
h1,h2,h3,h4,h5,h6 { font-family: 'Outfit', sans-serif !important; color: #f1f5f9 !important; }
p, span, label, div { font-family: 'Outfit', sans-serif !important; }
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: transparent; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 8px; }
.stTabs [data-baseweb="tab"] { background: transparent !important; border: none !important; border-radius: 8px !important; padding: 8px 16px !important; font-family: 'Outfit' !important; font-weight: 500 !important; font-size: 13px !important; color: #94a3b8 !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { background: rgba(99,102,241,0.12) !important; color: #a5b4fc !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
.stCheckbox { margin-bottom: 2px !important; }
.stCheckbox label { color: #e2e8f0 !important; font-size: 14px !important; }
.stButton > button { background: linear-gradient(135deg, #6366f1, #7c3aed) !important; color: #fff !important; border: none !important; border-radius: 10px !important; font-family: 'Outfit' !important; font-weight: 600 !important; padding: 10px 24px !important; }
.stButton > button:hover { background: linear-gradient(135deg, #7c3aed, #6366f1) !important; }
.stNumberInput input, .stTextArea textarea, .stTextInput input, .stSelectbox select, .stSelectbox div[data-baseweb] { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 8px !important; color: #f1f5f9 !important; }
.stSuccess > div { background: rgba(16,185,129,0.1) !important; border: 1px solid rgba(16,185,129,0.2) !important; border-radius: 10px !important; color: #6ee7b7 !important; }
.stWarning > div { background: rgba(245,158,11,0.1) !important; border: 1px solid rgba(245,158,11,0.2) !important; border-radius: 10px !important; }
.stInfo > div { background: rgba(99,102,241,0.1) !important; border: 1px solid rgba(99,102,241,0.2) !important; border-radius: 10px !important; }

.hdr-badge { font-size: 11px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: #818cf8; font-family: 'JetBrains Mono', monospace; margin-bottom: 6px; }
.hdr-date { font-size: clamp(26px,5vw,38px); font-weight: 800; background: linear-gradient(135deg, #f8fafc 0%, #a5b4fc 50%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2; margin: 0; font-family: 'Outfit'; }
.hdr-vibe { font-size: 15px; color: #94a3b8; margin-top: 6px; }
.hdr-vibe .tm { font-size: 13px; color: #475569; font-family: 'JetBrains Mono', monospace; margin-left: 14px; }

.s-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 18px; text-align: center; }
.s-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; color: #64748b; font-family: 'JetBrains Mono', monospace; margin-bottom: 6px; }
.s-val { font-size: 28px; font-weight: 800; font-family: 'JetBrains Mono', monospace; line-height: 1.2; }
.s-sub { font-size: 12px; color: #475569; margin-top: 4px; }

.alert-box { background: linear-gradient(135deg, rgba(239,68,68,0.10) 0%, rgba(239,68,68,0.04) 100%); border: 1px solid rgba(239,68,68,0.2); border-radius: 14px; padding: 18px 22px; margin-bottom: 20px; }
.sch-active { background: rgba(99,102,241,0.06); border: 1px solid rgba(99,102,241,0.25); border-left: 4px solid #6366f1; border-radius: 14px; padding: 16px 20px; margin-bottom: 10px; }
.sch-normal { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 16px 20px; margin-bottom: 10px; }
.now-tag { display: inline-block; font-size: 10px; font-weight: 800; letter-spacing: 2px; color: #818cf8; background: rgba(99,102,241,0.12); padding: 3px 12px; border-radius: 6px; text-transform: uppercase; font-family: 'JetBrains Mono', monospace; }

.meal-c { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 20px; text-align: center; }
.wk-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 14px; text-align: center; min-height: 200px; }
.wk-today { background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.25); }
.td-badge { display: inline-block; background: #6366f1; color: #fff; font-size: 9px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; padding: 2px 8px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; }
.lk-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 18px 22px; margin-bottom: 10px; display: block; text-decoration: none !important; transition: all 0.2s; }
.lk-card:hover { border-color: rgba(99,102,241,0.3); background: rgba(99,102,241,0.04); }
.pbar-outer { height: 8px; background: rgba(255,255,255,0.04); border-radius: 99px; overflow: hidden; margin: 10px 0 20px; }
.pbar-inner { height: 100%; border-radius: 99px; transition: width 0.5s cubic-bezier(0.4,0,0.2,1); }
.sec-title { font-size: 18px; font-weight: 700; color: #f1f5f9; margin-bottom: 14px; font-family: 'Outfit'; }
.prime-footer { text-align: center; color: #334155; font-size: 14px; padding: 32px 0 16px; border-top: 1px solid rgba(255,255,255,0.04); margin-top: 40px; }
.prime-footer small { font-size: 12px; color: #1e293b; display: block; margin-top: 4px; }

.flash-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 28px; margin: 12px 0; min-height: 120px; }
.flash-q { font-size: 17px; font-weight: 600; color: #e2e8f0; line-height: 1.5; }
.flash-a { font-size: 15px; color: #94a3b8; line-height: 1.6; margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.06); }
.flash-cat { display: inline-block; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 3px 10px; border-radius: 6px; margin-bottom: 12px; font-family: 'JetBrains Mono', monospace; }

.job-row { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 14px 18px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }

.timer-display { font-size: 64px; font-weight: 800; font-family: 'JetBrains Mono', monospace; text-align: center; letter-spacing: 4px; }

.glow-a { position: fixed; top: -200px; right: -200px; width: 600px; height: 600px; background: radial-gradient(circle, rgba(99,102,241,0.06) 0%, transparent 70%); pointer-events: none; z-index: 0; }
.glow-b { position: fixed; bottom: -200px; left: -100px; width: 500px; height: 500px; background: radial-gradient(circle, rgba(236,72,153,0.04) 0%, transparent 70%); pointer-events: none; z-index: 0; }
</style>
<div class="glow-a"></div><div class="glow-b"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# COMPUTED VALUES
# ─────────────────────────────────────────────────────────
today = datetime.date.today()
now = datetime.datetime.now()
day_name = today.strftime("%a")
day_num = (today - PLAN_START).days + 1
week_num = max(1, min(8, (day_num - 1) // 7 + 1))
total_days = (PLAN_END - PLAN_START).days
has_started = today >= PLAN_START
is_sunday = day_name == "Sun"
today_str = today.isoformat()
hour_now = now.hour + now.minute / 60
pct = min(100, max(0, round((day_num / total_days) * 100))) if total_days > 0 else 0

# Dynamic tasks for today
def get_today_tasks():
    w = max(1, min(8, week_num))
    d = day_name
    if d == "Sun":
        return {"job": "Weekly Review", "aws": "Review & Plan", "ml": "Review Notes", "practice": "Rest", "emoji": "🧘", "vibe": "Rest & Review Sunday"}
    return {
        "job": JOB_BY_WEEK.get(w, JOB_BY_WEEK[1]).get(d, "Job Hunt"),
        "aws": AWS_BY_WEEK.get(w, AWS_BY_WEEK[1]).get(d, "AWS Study"),
        "ml": ML_BY_WEEK.get(w, ML_BY_WEEK[1]).get(d, "ML Study"),
        "practice": PRACTICE_BY_WEEK.get(w, PRACTICE_BY_WEEK[1]).get(d, "Coding Practice"),
        "emoji": {"Mon": "🔥", "Tue": "⚡", "Wed": "🧱", "Thu": "🎯", "Fri": "🏁", "Sat": "🚀"}.get(d, "📋"),
        "vibe": {"Mon": "Momentum Monday", "Tue": "Turbo Tuesday", "Wed": "Grind Wednesday", "Thu": "Target Thursday", "Fri": "Focus Friday", "Sat": "Ship Saturday"}.get(d, "Study Day"),
    }

tasks_today = get_today_tasks()

SCHEDULE = [
    {"time": "10:00 – 11:00", "label": "💼 Job hunt", "cat": "job", "h": (10, 11)},
    {"time": "11:00 – 13:00", "label": "☁️ AWS deep dive", "cat": "aws", "h": (11, 13)},
    {"time": "13:00 – 13:30", "label": "🏃 Pre-gym", "cat": None, "h": (13, 13.5)},
    {"time": "13:30 – 14:30", "label": "🏋️ Gym", "cat": None, "h": (13.5, 14.5)},
    {"time": "14:30 – 15:00", "label": "🍽️ Lunch", "cat": None, "h": (14.5, 15)},
    {"time": "15:00 – 15:30", "label": "💤 Nap", "cat": None, "h": (15, 15.5)},
    {"time": "15:30 – 17:30", "label": "🧠 ML deep dive", "cat": "ml", "h": (15.5, 17.5)},
    {"time": "17:30 – 17:45", "label": "☕ Break", "cat": None, "h": (17.5, 17.75)},
    {"time": "17:45 – 19:15", "label": "💻 Practice", "cat": "practice", "h": (17.75, 19.25)},
    {"time": "19:15 – 19:45", "label": "📓 Review", "cat": None, "h": (19.25, 19.75)},
]

def is_current(b): return b["h"][0] <= hour_now < b["h"][1]

# Missed days
def get_missed():
    missed = []
    if not has_started: return missed
    c = PLAN_START
    while c < today:
        dn = c.strftime("%a"); ds = c.isoformat()
        if dn != "Sun" and ds not in data.get("daily_checks", {}) and ds not in data.get("missed_acks", []):
            missed.append({"day_name": dn, "str": ds, "label": c.strftime("%a %b %d")})
        c += datetime.timedelta(days=1)
    return missed

# Streak
streak = 0
cd = today - datetime.timedelta(days=1)
while cd >= PLAN_START:
    ds = cd.isoformat()
    if cd.strftime("%a") == "Sun" or ds in data.get("daily_checks", {}):
        streak += 1; cd -= datetime.timedelta(days=1)
    else: break

# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗂️ Quick links")
    st.markdown("[📋 DS + AWS Roadmap](https://www.notion.so/1e7a7b694ee0805a877cf71c3de56f5d)")
    st.markdown("[🥗 Nutrition System](https://www.notion.so/2a6a7b694ee080f6af92d59df04b63eb)")
    st.markdown("[🔁 Weekly Review](https://www.notion.so/323a7b694ee0817e8253f196589fe26c)")
    st.markdown("---")
    st.markdown("### ⚖️ Log weight")
    wi = st.number_input("kg", min_value=50.0, max_value=120.0, value=START_WEIGHT, step=0.1)
    if st.button("💾 Save weight", use_container_width=True):
        data.setdefault("weights", {})[today_str] = wi
        save_data(data); st.success(f"Saved {wi} kg")
    st.markdown("---")
    st.markdown("### 📝 Note")
    note = st.text_area("", value=data.get("notes", {}).get(today_str, ""), height=100, label_visibility="collapsed")
    if st.button("💾 Save note", use_container_width=True):
        data.setdefault("notes", {})[today_str] = note
        save_data(data); st.success("Saved")

# ─────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────
if has_started:
    st.markdown(f'<div class="hdr-badge">Week {week_num} of 8 · Day {day_num} of {total_days}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="hdr-badge">Plan starts in {(PLAN_START - today).days} days</div>', unsafe_allow_html=True)

st.markdown(f'<p class="hdr-date">{today.strftime("%A, %B %d, %Y")}</p>', unsafe_allow_html=True)
st.markdown(f'<p class="hdr-vibe">{tasks_today["emoji"]} {tasks_today["vibe"]}<span class="tm">{now.strftime("%I:%M %p")}</span></p>', unsafe_allow_html=True)
st.markdown("")

# MISSED ALERT
missed = get_missed()
if missed:
    st.markdown(f'<div class="alert-box"><div style="font-size:15px;font-weight:700;color:#fca5a5;">⚠️ {len(missed)} day{"s" if len(missed)>1 else ""} without check-in</div><div style="font-size:13px;color:#f87171;opacity:0.8;margin-top:4px;">Complete your checklist to clear these.</div></div>', unsafe_allow_html=True)
    with st.expander(f"🔍 Review {len(missed)} missed day(s)"):
        cs = st.columns(min(4, max(1, len(missed))))
        for i, m in enumerate(missed[:12]):
            with cs[i % min(4, max(1, len(missed)))]:
                st.markdown(f"**{m['label']}**")
                if st.button("✅", key=f"a_{m['str']}"):
                    data.setdefault("missed_acks", []).append(m["str"])
                    save_data(data); st.rerun()

# STATS
st.markdown("")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="s-card"><div class="s-label">Progress</div><div class="s-val" style="color:#818cf8;">{pct}%</div><div class="s-sub">Week {week_num} of 8</div></div>', unsafe_allow_html=True)

ws = data.get("weights", {})
lw = ws[sorted(ws.keys(), reverse=True)[0]] if ws else None
with c2:
    wd = f"{lw:.1f}" if lw else "—"
    wc = "#34d399" if lw and lw <= GOAL_WEIGHT else "#fbbf24" if lw else "#64748b"
    st.markdown(f'<div class="s-card"><div class="s-label">Weight</div><div class="s-val" style="color:{wc};">{wd}</div><div class="s-sub">Goal: {GOAL_WEIGHT} kg</div></div>', unsafe_allow_html=True)

with c3:
    st.markdown(f'<div class="s-card"><div class="s-label">Streak</div><div class="s-val" style="color:#f472b6;">{streak}</div><div class="s-sub">Consecutive days</div></div>', unsafe_allow_html=True)

tr = TRAINING.get(day_name, {})
with c4:
    st.markdown(f'<div class="s-card"><div class="s-label">Training</div><div style="font-size:16px;font-weight:700;color:#34d399;margin:6px 0;">{tr.get("act","—")}</div><div class="s-sub">{tr.get("dur","")} — {tr.get("focus","")}</div></div>', unsafe_allow_html=True)

# PROGRESS BAR
tc = data.get("daily_checks", {}).get(today_str, {})
cc = sum(1 for i in range(len(CHECKLIST)) if tc.get(str(i), False))
cp = round((cc / len(CHECKLIST)) * 100)
bc = "linear-gradient(90deg,#10b981,#34d399)" if cp == 100 else "linear-gradient(90deg,#6366f1,#a78bfa)"
st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;"><span style="font-size:12px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:1px;font-family:\'JetBrains Mono\',monospace;">Today\'s progress</span><span style="font-size:14px;font-weight:700;color:{"#34d399" if cp==100 else "#818cf8"};font-family:\'JetBrains Mono\',monospace;">{cc}/{len(CHECKLIST)}</span></div><div class="pbar-outer"><div class="pbar-inner" style="width:{cp}%;background:{bc};"></div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["📋 Today", "⏱️ Timer", "📅 Week", "💼 Jobs", "📊 Charts", "🃏 Cards", "🧪 Quiz", "🍽️ Meals"])

# ═══════════════ TAB: TODAY ═══════════════
with tab1:
    cl, cr = st.columns([3, 2])
    with cl:
        st.markdown('<div class="sec-title">Schedule</div>', unsafe_allow_html=True)
        if is_sunday:
            st.markdown('<div class="sch-active" style="border-left-color:#818cf8;"><div style="font-size:15px;color:#a5b4fc;font-weight:600;">🧘 Light day — weekly review only</div></div>', unsafe_allow_html=True)
        else:
            for b in SCHEDULE:
                a = is_current(b)
                d = tasks_today.get(b["cat"], "") if b["cat"] else ""
                cls = "sch-active" if a else "sch-normal"
                nw = '<span class="now-tag">NOW</span>' if a else ""
                dh = f'<div style="font-size:13px;color:#94a3b8;margin-top:3px;">{d}</div>' if d else ""
                st.markdown(f'<div class="{cls}"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span style="font-size:13px;font-family:\'JetBrains Mono\',monospace;color:{"#818cf8" if a else "#475569"};font-weight:600;">{b["time"]}</span><span style="margin-left:12px;font-size:14px;font-weight:600;color:{"#f1f5f9" if a else "#cbd5e1"};">{b["label"]}</span>{dh}</div>{nw}</div></div>', unsafe_allow_html=True)

    with cr:
        st.markdown('<div class="sec-title">Checklist</div>', unsafe_allow_html=True)
        for i, item in enumerate(CHECKLIST):
            st.checkbox(item, value=tc.get(str(i), False), key=f"ck_{i}")
        if cp == 100:
            st.balloons(); st.success("🏆 All tasks completed!")
        if st.button("💾 Save progress", use_container_width=True, type="primary"):
            cks = {str(i): st.session_state.get(f"ck_{i}", False) for i in range(len(CHECKLIST))}
            data.setdefault("daily_checks", {})[today_str] = cks
            save_data(data); st.success("Progress saved! ✅")

# ═══════════════ TAB: TIMER ═══════════════
with tab2:
    st.markdown('<div class="sec-title">Focus timer</div>', unsafe_allow_html=True)

    # Timer using Streamlit components
    preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
    with preset_col1:
        if st.button("15 min", use_container_width=True, key="t15"):
            st.session_state.timer_seconds = 15 * 60
    with preset_col2:
        if st.button("30 min", use_container_width=True, key="t30"):
            st.session_state.timer_seconds = 30 * 60
    with preset_col3:
        if st.button("45 min", use_container_width=True, key="t45"):
            st.session_state.timer_seconds = 45 * 60
    with preset_col4:
        if st.button("60 min", use_container_width=True, key="t60"):
            st.session_state.timer_seconds = 60 * 60

    custom_min = st.slider("Or set custom minutes:", 1, 120, 25, key="timer_slider")

    if "timer_seconds" not in st.session_state:
        st.session_state.timer_seconds = custom_min * 60

    total_sec = st.session_state.timer_seconds
    mins = total_sec // 60
    secs = total_sec % 60

    # Color based on time
    if total_sec > 600:
        t_color = "#818cf8"
    elif total_sec > 120:
        t_color = "#fbbf24"
    else:
        t_color = "#ef4444"

    st.markdown(f'<div class="timer-display" style="color:{t_color};margin:30px 0;">{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)

    # Progress ring
    if custom_min * 60 > 0:
        timer_pct = round((total_sec / (custom_min * 60)) * 100)
    else:
        timer_pct = 100
    st.markdown(f'<div class="pbar-outer" style="height:6px;margin:0 auto 20px;max-width:300px;"><div class="pbar-inner" style="width:{timer_pct}%;background:linear-gradient(90deg,{t_color},{t_color}88);"></div></div>', unsafe_allow_html=True)

    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        if st.button("▶️ Start", use_container_width=True, key="tstart"):
            st.session_state.timer_running = True
            st.session_state.timer_seconds = custom_min * 60
    with bc2:
        if st.button("⏸️ Pause", use_container_width=True, key="tpause"):
            st.session_state.timer_running = False
    with bc3:
        if st.button("⏹️ Reset", use_container_width=True, key="treset"):
            st.session_state.timer_running = False
            st.session_state.timer_seconds = custom_min * 60

    if st.session_state.get("timer_running", False) and total_sec > 0:
        time.sleep(1)
        st.session_state.timer_seconds -= 1
        if st.session_state.timer_seconds <= 0:
            st.session_state.timer_running = False
            st.success("⏰ Time's up! Great focus session!")
            st.balloons()
        st.rerun()

    st.markdown("")
    st.info("💡 **Tip:** Use 45-min blocks during study, 15-min for breaks. The Pomodoro rhythm keeps you sharp.")

# ═══════════════ TAB: WEEK ═══════════════
with tab3:
    st.markdown(f'<div class="sec-title">Week {week_num} overview — dynamic schedule</div>', unsafe_allow_html=True)
    wcs = st.columns(7)
    for i, d in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
        with wcs[i]:
            it = d == day_name
            cls = "wk-card wk-today" if it else "wk-card"
            tb = '<div class="td-badge" style="margin:6px 0;">TODAY</div>' if it else ""
            w = max(1, min(8, week_num))
            if d == "Sun":
                st.markdown(f'<div class="{cls}"><div style="font-size:14px;font-weight:700;color:#e2e8f0;">{d}</div>{tb}<div style="color:#64748b;font-size:12px;margin-top:8px;">Rest + Review</div></div>', unsafe_allow_html=True)
            else:
                jt = JOB_BY_WEEK.get(w, {}).get(d, "—")
                at = AWS_BY_WEEK.get(w, {}).get(d, "—")
                mt = ML_BY_WEEK.get(w, {}).get(d, "—")
                pt = PRACTICE_BY_WEEK.get(w, {}).get(d, "—")
                st.markdown(f'<div class="{cls}"><div style="font-size:14px;font-weight:700;color:#e2e8f0;">{d}</div>{tb}<div style="text-align:left;margin-top:8px;font-size:11px;line-height:1.6;"><div style="color:#fbbf24;">💼 {jt}</div><div style="color:#60a5fa;">☁️ {at}</div><div style="color:#f87171;">🧠 {mt}</div><div style="color:#f472b6;">💻 {pt}</div></div></div>', unsafe_allow_html=True)

# ═══════════════ TAB: JOBS ═══════════════
with tab4:
    st.markdown('<div class="sec-title">Job application tracker</div>', unsafe_allow_html=True)

    with st.form("job_form", clear_on_submit=True):
        jc1, jc2, jc3 = st.columns([2, 2, 1])
        with jc1:
            company = st.text_input("Company")
        with jc2:
            role = st.text_input("Role")
        with jc3:
            status = st.selectbox("Status", ["Applied", "Interview", "Rejected", "Offer", "Ghosted"])
        
        jc4, jc5 = st.columns([2, 1])
        with jc4:
            job_url = st.text_input("Job URL (optional)")
        with jc5:
            job_note = st.text_input("Note (optional)")
        
        if st.form_submit_button("➕ Add application", use_container_width=True):
            if company and role:
                data.setdefault("jobs", []).append({
                    "company": company, "role": role, "status": status,
                    "url": job_url, "note": job_note, "date": today_str
                })
                save_data(data); st.success(f"Added {company} — {role}")
                st.rerun()

    jobs = data.get("jobs", [])
    if jobs:
        # Stats
        jsc1, jsc2, jsc3, jsc4 = st.columns(4)
        status_counts = {}
        for j in jobs:
            status_counts[j["status"]] = status_counts.get(j["status"], 0) + 1
        
        with jsc1:
            st.markdown(f'<div class="s-card"><div class="s-label">Total</div><div class="s-val" style="color:#818cf8;">{len(jobs)}</div></div>', unsafe_allow_html=True)
        with jsc2:
            st.markdown(f'<div class="s-card"><div class="s-label">Interviews</div><div class="s-val" style="color:#34d399;">{status_counts.get("Interview", 0)}</div></div>', unsafe_allow_html=True)
        with jsc3:
            this_week = sum(1 for j in jobs if j.get("date", "") >= (today - datetime.timedelta(days=7)).isoformat())
            st.markdown(f'<div class="s-card"><div class="s-label">This week</div><div class="s-val" style="color:#fbbf24;">{this_week}</div></div>', unsafe_allow_html=True)
        with jsc4:
            st.markdown(f'<div class="s-card"><div class="s-label">Offers</div><div class="s-val" style="color:#f472b6;">{status_counts.get("Offer", 0)}</div></div>', unsafe_allow_html=True)

        st.markdown("")
        status_colors = {"Applied": "#818cf8", "Interview": "#34d399", "Rejected": "#ef4444", "Offer": "#f472b6", "Ghosted": "#64748b"}
        
        for j in reversed(jobs[-20:]):
            sc = status_colors.get(j["status"], "#64748b")
            st.markdown(f"""
            <div class="job-row">
                <div>
                    <span style="font-weight:600;color:#e2e8f0;font-size:14px;">{j['company']}</span>
                    <span style="color:#64748b;margin-left:8px;font-size:13px;">{j['role']}</span>
                    {f'<div style="font-size:12px;color:#475569;margin-top:2px;">{j.get("note","")}</div>' if j.get("note") else ""}
                </div>
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:12px;color:#475569;font-family:'JetBrains Mono',monospace;">{j.get('date','')}</span>
                    <span style="font-size:11px;font-weight:700;color:{sc};background:{sc}15;padding:3px 10px;border-radius:6px;text-transform:uppercase;letter-spacing:1px;font-family:'JetBrains Mono',monospace;">{j['status']}</span>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No applications yet. Start adding above!")

# ═══════════════ TAB: CHARTS ═══════════════
with tab5:
    st.markdown('<div class="sec-title">Weekly progress</div>', unsafe_allow_html=True)

    # Checklist completion by day
    all_checks = data.get("daily_checks", {})
    if all_checks:
        chart_data = []
        for d_str, checks in sorted(all_checks.items()):
            completed = sum(1 for v in checks.values() if v)
            chart_data.append({"Date": datetime.date.fromisoformat(d_str), "Completed": completed, "Total": len(CHECKLIST)})
        
        if chart_data:
            df_chart = pd.DataFrame(chart_data).set_index("Date")
            st.markdown("**Daily checklist completion**")
            st.bar_chart(df_chart["Completed"], use_container_width=True, color="#818cf8")

    # Weight chart
    if ws:
        st.markdown("")
        st.markdown("**Weight progress**")
        wd_list = [(datetime.date.fromisoformat(d), w) for d, w in sorted(ws.items())]
        df_w = pd.DataFrame(wd_list, columns=["Date", "Weight (kg)"]).set_index("Date")
        st.line_chart(df_w, use_container_width=True, color="#f472b6")
        if len(wd_list) >= 2:
            lo = wd_list[0][1] - wd_list[-1][1]; rm = wd_list[-1][1] - GOAL_WEIGHT
            st.markdown(f'<div style="display:flex;gap:24px;justify-content:center;margin:10px 0;"><span style="color:#34d399;font-weight:700;font-family:\'JetBrains Mono\',monospace;">▼ Lost: {lo:.1f} kg</span><span style="color:#475569;">·</span><span style="color:#fbbf24;font-weight:700;font-family:\'JetBrains Mono\',monospace;">→ Remaining: {rm:.1f} kg</span></div>', unsafe_allow_html=True)

    # Jobs pipeline chart
    jobs = data.get("jobs", [])
    if jobs:
        st.markdown("")
        st.markdown("**Job applications pipeline**")
        pipeline = {}
        for j in jobs:
            pipeline[j["status"]] = pipeline.get(j["status"], 0) + 1
        df_j = pd.DataFrame(list(pipeline.items()), columns=["Status", "Count"]).set_index("Status")
        st.bar_chart(df_j, use_container_width=True, color="#34d399")

    if not all_checks and not ws and not jobs:
        st.info("Charts will appear once you start logging data!")

# ═══════════════ TAB: FLASHCARDS ═══════════════
with tab6:
    st.markdown('<div class="sec-title">Flashcards</div>', unsafe_allow_html=True)

    cat_filter = st.selectbox("Category", ["All", "ML", "AWS", "SQL"], key="flash_cat")
    cards = FLASHCARDS if cat_filter == "All" else [c for c in FLASHCARDS if c["cat"] == cat_filter]

    if "flash_idx" not in st.session_state:
        st.session_state.flash_idx = 0
    if "flash_show" not in st.session_state:
        st.session_state.flash_show = False

    idx = st.session_state.flash_idx % len(cards)
    card = cards[idx]

    cat_colors = {"ML": "color:#f472b6;background:rgba(244,114,182,0.1);", "AWS": "color:#60a5fa;background:rgba(96,165,250,0.1);", "SQL": "color:#fbbf24;background:rgba(251,191,36,0.1);"}
    cat_style = cat_colors.get(card["cat"], "color:#818cf8;background:rgba(129,140,248,0.1);")

    st.markdown(f'<div class="flash-card"><div class="flash-cat" style="{cat_style}">{card["cat"]}</div><div class="flash-q">{card["q"]}</div>', unsafe_allow_html=True)
    
    if st.session_state.flash_show:
        st.markdown(f'<div class="flash-a">{card["a"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        if st.button("⬅️ Previous", use_container_width=True, key="fprev"):
            st.session_state.flash_idx = (idx - 1) % len(cards)
            st.session_state.flash_show = False; st.rerun()
    with fc2:
        if st.button("👁️ Show answer" if not st.session_state.flash_show else "🙈 Hide", use_container_width=True, key="fshow"):
            st.session_state.flash_show = not st.session_state.flash_show; st.rerun()
    with fc3:
        if st.button("➡️ Next", use_container_width=True, key="fnext"):
            st.session_state.flash_idx = (idx + 1) % len(cards)
            st.session_state.flash_show = False; st.rerun()

    if st.button("🔀 Shuffle", use_container_width=True, key="fshuffle"):
        st.session_state.flash_idx = random.randint(0, len(cards) - 1)
        st.session_state.flash_show = False; st.rerun()

    st.markdown(f'<div style="text-align:center;color:#475569;font-size:13px;margin-top:12px;font-family:\'JetBrains Mono\',monospace;">Card {idx + 1} of {len(cards)}</div>', unsafe_allow_html=True)

# ═══════════════ TAB: QUIZ ═══════════════
with tab7:
    st.markdown('<div class="sec-title">Interview prep quiz</div>', unsafe_allow_html=True)

    quiz_cat = st.selectbox("Category", ["All", "ML Theory", "System Design", "Behavioral"], key="quiz_cat")
    qs = QUIZ_QUESTIONS if quiz_cat == "All" else [q for q in QUIZ_QUESTIONS if q["cat"] == quiz_cat]

    if "quiz_idx" not in st.session_state:
        st.session_state.quiz_idx = random.randint(0, len(qs) - 1)
    if "quiz_show" not in st.session_state:
        st.session_state.quiz_show = False

    qidx = st.session_state.quiz_idx % len(qs)
    question = qs[qidx]

    qcat_colors = {"ML Theory": "color:#f472b6;background:rgba(244,114,182,0.1);", "System Design": "color:#34d399;background:rgba(52,211,153,0.1);", "Behavioral": "color:#fbbf24;background:rgba(251,191,36,0.1);"}
    qcat_style = qcat_colors.get(question["cat"], "color:#818cf8;background:rgba(129,140,248,0.1);")

    st.markdown(f'<div class="flash-card"><div class="flash-cat" style="{qcat_style}">{question["cat"]}</div><div class="flash-q">{question["q"]}</div></div>', unsafe_allow_html=True)

    user_answer = st.text_area("Your answer:", height=120, key="quiz_answer", placeholder="Think through your answer before revealing the model response...")

    if st.session_state.quiz_show:
        st.markdown(f'<div class="flash-card" style="border-color:rgba(52,211,153,0.2);background:rgba(52,211,153,0.04);"><div style="font-size:12px;font-weight:600;color:#34d399;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;font-family:\'JetBrains Mono\',monospace;">Model answer</div><div style="font-size:15px;color:#94a3b8;line-height:1.6;">{question["a"]}</div></div>', unsafe_allow_html=True)

    qc1, qc2 = st.columns(2)
    with qc1:
        if st.button("🔍 Reveal answer" if not st.session_state.quiz_show else "🙈 Hide answer", use_container_width=True, key="qshow"):
            st.session_state.quiz_show = not st.session_state.quiz_show; st.rerun()
    with qc2:
        if st.button("🎲 Next question", use_container_width=True, key="qnext"):
            st.session_state.quiz_idx = random.randint(0, len(qs) - 1)
            st.session_state.quiz_show = False; st.rerun()

    # Quiz history
    quiz_history = data.get("quiz_history", {})
    total_attempted = len(quiz_history)
    st.markdown(f'<div style="text-align:center;color:#475569;font-size:13px;margin-top:16px;font-family:\'JetBrains Mono\',monospace;">Questions practiced: {total_attempted}</div>', unsafe_allow_html=True)

    if user_answer and st.button("💾 Save my answer", use_container_width=True, key="qsave"):
        data.setdefault("quiz_history", {})[f"{today_str}_{qidx}"] = {
            "question": question["q"], "user_answer": user_answer, "date": today_str
        }
        save_data(data); st.success("Answer saved!")

# ═══════════════ TAB: MEALS ═══════════════
with tab8:
    st.markdown('<div class="sec-title">Daily meals</div>', unsafe_allow_html=True)
    mcs = st.columns(4)
    for i, m in enumerate(MEALS):
        with mcs[i]:
            st.markdown(f'<div class="meal-c"><div style="font-size:28px;margin-bottom:8px;">{m["icon"]}</div><div style="font-weight:700;color:#e2e8f0;font-size:15px;">{m["name"]}</div><div style="color:#818cf8;font-size:12px;font-weight:600;margin:6px 0;font-family:\'JetBrains Mono\',monospace;">{m["time"]} · {m["kcal"]} kcal</div><div style="color:#64748b;font-size:13px;line-height:1.5;">{m["desc"]}</div></div>', unsafe_allow_html=True)

    st.markdown(""); st.markdown('<div class="sec-title">Daily targets</div>', unsafe_allow_html=True)
    tcs = st.columns(4)
    for col, (lb, vl, sb, co) in zip(tcs, [("Calories","1,500–1,850","kcal/day","#818cf8"),("Protein","130–150g","per day","#34d399"),("Water","2.5L","minimum","#60a5fa"),("Last meal","Before 23:00","window","#fbbf24")]):
        with col:
            st.markdown(f'<div class="s-card"><div class="s-label">{lb}</div><div style="font-size:18px;font-weight:700;color:{co};margin:6px 0;font-family:\'JetBrains Mono\',monospace;">{vl}</div><div class="s-sub">{sb}</div></div>', unsafe_allow_html=True)

# FOOTER
st.markdown('<div class="prime-footer">Prime is built in silence. 🚀 Discipline = Freedom.<small>Small daily progress > random bursts of effort.</small></div>', unsafe_allow_html=True)
