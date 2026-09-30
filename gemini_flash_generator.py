"""Fast nutrition / recovery tips with Gemini Flash."""
from .config import FLASH_MODEL, GOOGLE_API_KEY
from .gemini_generator import ask_gemini
from .offline_plan import offline_tip


def generate_nutrition_tip_with_flash(goal: str, intensity: str = "medium") -> str:
    if not GOOGLE_API_KEY:
        return offline_tip(goal)
    prompt = (
        f"Give ONE concise, practical nutrition or recovery tip (max 2 sentences, plain text) "
        f"for someone whose fitness goal is '{goal}' and trains at {intensity} intensity."
    )
    try:
        return ask_gemini(FLASH_MODEL, prompt).strip()
    except Exception as exc:
        print(f"[FitBuddy] Gemini tip failed, using offline tip: {exc}")
        return offline_tip(goal)
