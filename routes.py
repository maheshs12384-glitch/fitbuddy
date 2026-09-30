import json
import os

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from . import database as dbm
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan
from .config import GOOGLE_API_KEY

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
templates.env.filters["fromjson"] = lambda s: json.loads(s) if s else None

router = APIRouter()
GOALS = [
    ("weight loss", "🔥", "Weight loss"),
    ("muscle gain", "💪", "Muscle gain"),
    ("flexibility", "🧘", "Flexibility"),
    ("endurance", "🏃", "Endurance"),
    ("general wellness", "🌿", "General wellness"),
]


def render(request: Request, name: str, **ctx):
    ctx.setdefault("ai_live", bool(GOOGLE_API_KEY))
    return templates.TemplateResponse(request, name, ctx)


def result_context(user, message=""):
    plan = user.plan
    return dict(
        user=user,
        original=json.loads(plan.original_plan),
        updated=json.loads(plan.updated_plan) if plan.updated_plan else None,
        tip=plan.nutrition_tip,
        last_feedback=plan.last_feedback,
        message=message,
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return render(request, "index.html", goals=GOALS, error=None, form={})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: str = Form(...),
    weight: str = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(dbm.get_db),
):
    form = dict(username=username, user_id=user_id, age=age, weight=weight, goal=goal, intensity=intensity)
    try:
        data = UserInput(**form)
    except ValidationError as exc:
        first = exc.errors()[0]
        field = str(first["loc"][0]) if first["loc"] else "form"
        msg = f"Check the {field.replace('_', ' ')} field: {first['msg']}."
        return render(request, "index.html", goals=GOALS, error=msg, form=form)

    plan = generate_workout_gemini(data.username, data.age, data.weight, data.goal, data.intensity)
    tip = generate_nutrition_tip_with_flash(data.goal, data.intensity)
    user = dbm.save_user(db, data)
    dbm.save_plan(db, user, plan, tip)
    return render(request, "result.html", **result_context(user, "Your 7-day plan is ready!"))


@router.get("/plan/{user_id}", response_class=HTMLResponse)
def view_plan(request: Request, user_id: str, db: Session = Depends(dbm.get_db)):
    user = dbm.get_user(db, user_id)
    if not user or not user.plan:
        return render(request, "index.html", goals=GOALS, form={},
                      error=f"No plan found for ID '{user_id}'. Create one below.")
    return render(request, "result.html", **result_context(user))


@router.get("/feedback", response_class=HTMLResponse)
def feedback_page(request: Request, user_id: str = ""):
    return render(request, "feedback.html", user_id=user_id, error=None)


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(request: Request, user_id: str = Form(...), feedback: str = Form(...),
                    db: Session = Depends(dbm.get_db)):
    try:
        data = FeedbackRequest(user_id=user_id.strip(), feedback=feedback.strip())
    except ValidationError:
        return render(request, "feedback.html", user_id=user_id,
                      error="Add your User ID and at least a few words of feedback.")
    user = dbm.get_user(db, data.user_id)
    if not user or not user.plan:
        return render(request, "feedback.html", user_id=user_id,
                      error=f"We couldn't find User ID '{data.user_id}'. Check the ID or create a plan first.")
    current = json.loads(user.plan.updated_plan or user.plan.original_plan)
    revised = update_workout_plan(current, data.feedback, user.goal, user.intensity)
    dbm.update_plan(db, user, revised, data.feedback)
    return render(request, "result.html", **result_context(user, "Plan updated with your feedback!"))


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(dbm.get_db)):
    users = dbm.get_all_users(db)
    rows = [dict(user=u, original=json.loads(u.plan.original_plan) if u.plan else None,
                 updated=json.loads(u.plan.updated_plan) if u.plan and u.plan.updated_plan else None)
            for u in users]
    stats = dict(total=len(users), updated=sum(1 for r in rows if r["updated"]),
                 goals=len({u.goal for u in users}))
    return render(request, "all_users.html", rows=rows, stats=stats)


@router.post("/delete-user/{user_id}")
def delete_user(user_id: str, db: Session = Depends(dbm.get_db)):
    dbm.delete_user(db, user_id)
    return RedirectResponse("/view-all-users", status_code=303)


# ---- JSON API (also visible at /docs) ----
@router.get("/api/users")
def api_users(db: Session = Depends(dbm.get_db)):
    return [dict(user_id=u.user_id, username=u.username, age=u.age, weight=u.weight,
                 goal=u.goal, intensity=u.intensity) for u in dbm.get_all_users(db)]


@router.get("/api/plan/{user_id}")
def api_plan(user_id: str, db: Session = Depends(dbm.get_db)):
    user = dbm.get_user(db, user_id)
    if not user or not user.plan:
        return JSONResponse({"detail": "Plan not found"}, status_code=404)
    return dict(user_id=user.user_id, original=json.loads(user.plan.original_plan),
                updated=json.loads(user.plan.updated_plan) if user.plan.updated_plan else None,
                nutrition_tip=user.plan.nutrition_tip)
