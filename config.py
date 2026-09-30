import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
# "Pro" model: workout generation + feedback updates. "Flash" model: quick tips.
PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")
FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash")
