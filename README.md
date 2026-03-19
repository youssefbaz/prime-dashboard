# 🚀 Prime Dashboard — Streamlit App

Your personal daily dashboard for the DS + AWS Roadmap and Nutrition Plan.

## Features
- **Live date display** — auto-updates every day
- **Today's schedule** — highlights the current time block with a NOW badge
- **Missed days alert** — flags every day since March 23 where you haven't checked in
- **Daily checklist** — tick off tasks and save progress (persists between sessions)
- **Weight tracker** — log daily weight with a progress chart
- **Meals overview** — all 4 meals with times and calories
- **Weekly overview** — see your entire week at a glance with today highlighted
- **Quick links** — jump to your Notion pages from the sidebar
- **Daily notes** — jot down thoughts for each day
- **Streak counter** — track consecutive completed days
- **Mobile-friendly** — works great on your phone's browser

## Deploy on Streamlit Cloud (Free)

### Step 1: Create a GitHub repo
1. Go to [github.com/new](https://github.com/new)
2. Name it `prime-dashboard`
3. Push these files:
   ```
   prime-dashboard/
   ├── app.py
   ├── requirements.txt
   └── README.md
   ```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your `prime-dashboard` repo
5. Set main file: `app.py`
6. Click **Deploy**

### Step 3: Access from your phone
1. Open the Streamlit URL on your phone's browser
2. Tap **"Add to Home Screen"** to make it feel like a native app
3. Open it every morning!

## Local Development
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data Storage
Progress is saved to `prime_data.json` in the app directory. On Streamlit Cloud, 
data persists per session. For full persistence, consider upgrading to use a 
database (Supabase, Firebase, or Google Sheets as a backend).

---
*Prime is built in silence. 🚀 Discipline = Freedom.*
