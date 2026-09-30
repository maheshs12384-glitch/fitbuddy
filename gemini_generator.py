"""Workout plan generation with Gemini Pro."""
import json
import re

from .config import GOOGLE_API_KEY, PRO_MODEL
from .offline_plan import build_offline_plan

PLAN_SCHEMA = """Return ONLY valid JSON (no markdown fences) shaped exactly like:
{"days":[{"day":"Day 1","focus":"short focus title","warmup":"5-10 min warm-up",
"exercises":[{"name":"Exercise","sets":"3","reps":"12","rest":"45 sec"}],
"cooldown":"cooldown or recovery tip"}]}
Rules: exactly 7 day objects (Day 1 to Day 7). A rest day has "exercises": [] and a recovery tip in "cooldown"."""


def parse_plan(text: str) -> dict:
    """Turn a model reply into a validated plan dict (raises ValueError if unusable)."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    data = json.loads(text)
    days = data.get("days") if isinstance(data, dict) else None
    if not days or not isinstance(days, list):
        raise ValueError("No days in plan")
    clean = []
    for i, d in enumerate(days[:7], start=1):
        clean.append({
            "day": str(d.get("day") or f"Day {i}"),
            "focus": str(d.get("focus") or "Workout"),
            "warmup": str(d.get("warmup") or ""),
            "exercises": [
                {k: str(e.get(k, "")) for k in ("name", "sets", "reps", "rest")}
                for e in (d.get("exercises") or []) if isinstance(e, dict)
            ],
            "cooldown": str(d.get("cooldown") or ""),
        })
    return {"source": "gemini", "days": clean}


def ask_gemini(model_name: str, prompt: str, as_json: bool = False) -> str:
    import google.generativeai as genai

    genai.configure(api_key=GOOGLE_API_KEY)
    config = {"response_mime_type": "application/json"} if as_json else None
    model = genai.GenerativeModel(model_name, generation_config=config)
    return model.generate_content(prompt).text


def generate_workout_gemini(name: str, age: int, weight: float, goal: str, intensity: str) -> dict:
    if not GOOGLE_API_KEY:
        return build_offline_plan(goal, intensity)
    prompt = (
        f"You are a certified personal trainer. Create a personalised 7-day workout plan for "
        f"{name}, age {age}, weight {weight} kg. Goal: {goal}. Preferred intensity: {intensity}. "
        f"Each workout day needs a 5-10 minute warm-up, the main workout with sets/reps/rest, "
        f"and a cooldown or recovery tip. Include rest days where sensible.\n{PLAN_SCHEMA}"
    )
    try:
        return parse_plan(ask_gemini(PRO_MODEL, prompt, as_json=True))
    except Exception as exc:  # network, quota, bad JSON...
        print(f"[FitBuddy] Gemini plan failed, using offline plan: {exc}")
        return build_offline_plan(goal, intensity)
