"""Feedback-based plan revision with Gemini Pro."""
import json

from .config import GOOGLE_API_KEY, PRO_MODEL
from .gemini_generator import PLAN_SCHEMA, ask_gemini, parse_plan
from .offline_plan import build_offline_plan


def _offline_update(plan: dict, feedback: str, goal: str, intensity: str) -> dict:
    """Simple rule-based edits so feedback still does something without an API key."""
    fb = feedback.lower()
    plan = json.loads(json.dumps(plan))  # deep copy
    for d in plan["days"]:
        exs = d["exercises"]
        if "cardio" in fb and exs and "Rest" not in d["focus"]:
            exs.append({"name": "Extra cardio: brisk jog or cycling", "sets": "1", "reps": "10 min", "rest": "-"})
        if "yoga" in fb or "stretch" in fb or "flex" in fb:
            if exs:
                exs.append({"name": "Yoga flow", "sets": "1", "reps": "8 min", "rest": "-"})
        if any(w in fb for w in ("easier", "too hard", "tired", "less")):
            for e in exs:
                if e["sets"].isdigit() and int(e["sets"]) > 2:
                    e["sets"] = str(int(e["sets"]) - 1)
        if any(w in fb for w in ("harder", "too easy", "more intense", "challeng")):
            for e in exs:
                if e["sets"].isdigit():
                    e["sets"] = str(int(e["sets"]) + 1)
    if "rest" in fb:
        for d in plan["days"][-2:]:
            if d["exercises"]:
                d.update(focus="Rest & recovery", exercises=[], warmup="",
                         cooldown="Extra rest day added from your feedback.")
                break
    plan["source"] = "offline"
    return plan


def update_workout_plan(original_plan: dict, feedback: str, goal: str = "", intensity: str = "medium") -> dict:
    if not GOOGLE_API_KEY:
        return _offline_update(original_plan, feedback, goal, intensity)
    prompt = (
        f"Here is a user's current 7-day workout plan (goal: {goal}, intensity: {intensity}) as JSON:\n"
        f"{json.dumps(original_plan)}\n\nThe user's feedback: \"{feedback}\"\n"
        f"Revise the plan to reflect the feedback while keeping it safe and balanced.\n{PLAN_SCHEMA}"
    )
    try:
        return parse_plan(ask_gemini(PRO_MODEL, prompt, as_json=True))
    except Exception as exc:
        print(f"[FitBuddy] Gemini update failed, using rule-based update: {exc}")
        return _offline_update(original_plan, feedback, goal, intensity)
