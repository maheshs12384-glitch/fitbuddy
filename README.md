# FitBuddy – AI Fitness Plan Generator (FastAPI + Gemini)

Colourful, animated web app that builds a personalised 7-day workout plan, adds a nutrition tip,
rewrites the plan from your feedback, and gives coaches a dashboard of all members.

## Run it

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then paste your Gemini key into GOOGLE_API_KEY
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000  (API docs: http://127.0.0.1:8000/docs)

No API key? The app still works in demo mode with built-in plans and tips.
Get a free key at https://aistudio.google.com/apikey

## Pages
| Route | What it does |
|---|---|
| `/` | Form: name, user ID, age, weight, goal, intensity |
| `/generate-workout` | Creates plan (Gemini Pro) + tip (Gemini Flash), saves to SQLite |
| `/plan/{user_id}` | Re-open a saved plan |
| `/feedback`, `/submit-feedback` | Send feedback; plan is rewritten, original is kept |
| `/view-all-users` | Coach dashboard: search, compare original vs updated, delete |
| `/api/users`, `/api/plan/{user_id}` | JSON endpoints |

## Structure
```
app/  main.py routes.py database.py schemas.py config.py
      gemini_generator.py  gemini_flash_generator.py  updated_plan.py  offline_plan.py
templates/  base, index, result, feedback, all_users
static/     css/style.css  js/app.js
```

## Notes
- Model names are set in `.env` (`GEMINI_PRO_MODEL`, `GEMINI_FLASH_MODEL`). Older names such as
  `gemini-1.5-pro` have been retired by Google, so the defaults use the current 2.5 models.
- If a Gemini call fails, FitBuddy falls back to its built-in plan so the page never breaks.
- Delete `fitbuddy.db` to reset all data.
