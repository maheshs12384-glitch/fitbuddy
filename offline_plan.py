"""Built-in plans used when no Gemini key is set (or a Gemini call fails),
so the site always works."""

SETS = {"low": 2, "medium": 3, "high": 4}
REST = {"low": "60 sec", "medium": "45 sec", "high": "30 sec"}

REST_DAY = ("Rest & recovery", [])

PLANS = {
    "weight loss": [
        ("Full-body circuit", ["Bodyweight squats|15", "Push-ups|10", "Mountain climbers|30 sec", "Plank|30 sec"]),
        ("Cardio burn", ["Brisk jog or cycling|25 min", "Jumping jacks|40", "High knees|30 sec"]),
        ("Lower body + core", ["Walking lunges|12 each leg", "Glute bridges|15", "Bicycle crunches|20", "Wall sit|40 sec"]),
        REST_DAY,
        ("HIIT intervals", ["Burpees|10", "Skater jumps|20", "Squat jumps|12", "Sprint in place|30 sec"]),
        ("Upper body + core", ["Incline push-ups|12", "Dumbbell rows|12", "Shoulder taps|20", "Russian twists|20"]),
        ("Active recovery", ["Easy walk|30 min", "Cat-cow stretch|10", "Child's pose|45 sec"]),
    ],
    "muscle gain": [
        ("Push (chest, shoulders, triceps)", ["Bench or floor press|8-10", "Overhead press|8-10", "Incline push-ups|12", "Triceps dips|10-12"]),
        ("Pull (back, biceps)", ["Pull-ups or lat pulldown|8-10", "Bent-over rows|10", "Biceps curls|12", "Face pulls|15"]),
        ("Legs", ["Goblet or barbell squats|8-10", "Romanian deadlifts|10", "Walking lunges|12 each leg", "Calf raises|15"]),
        REST_DAY,
        ("Upper body volume", ["Dumbbell press|10", "Seated rows|10", "Lateral raises|15", "Hammer curls|12"]),
        ("Lower body + core", ["Leg press or split squats|10", "Hip thrusts|12", "Hanging knee raises|12", "Plank|45 sec"]),
        REST_DAY,
    ],
    "flexibility": [
        ("Hips & hamstrings", ["Low lunge hold|45 sec", "Seated forward fold|45 sec", "Pigeon pose|45 sec each side", "Butterfly stretch|45 sec"]),
        ("Spine & shoulders", ["Cat-cow|12", "Thread the needle|30 sec each side", "Cobra stretch|30 sec", "Doorway chest stretch|40 sec"]),
        ("Yoga flow", ["Sun salutations|6 rounds", "Warrior II|40 sec each side", "Downward dog|45 sec"]),
        REST_DAY,
        ("Legs & ankles", ["Deep squat hold|45 sec", "Calf stretch|40 sec each", "Quad stretch|40 sec each", "Ankle circles|15 each"]),
        ("Mobility + balance", ["Hip circles|10 each way", "Tree pose|40 sec each", "World's greatest stretch|6 each side"]),
        ("Gentle restore", ["Child's pose|60 sec", "Supine twist|45 sec each", "Legs up the wall|3 min"]),
    ],
    "endurance": [
        ("Easy run", ["Easy run or cycle|30 min", "Dynamic leg swings|12 each", "Calf raises|15"]),
        ("Strength for runners", ["Step-ups|12 each leg", "Single-leg glute bridge|12", "Plank|45 sec", "Side plank|30 sec each"]),
        ("Tempo effort", ["Warm jog|10 min", "Tempo pace|15 min", "Cool-down walk|5 min"]),
        REST_DAY,
        ("Intervals", ["Fast 1 min / easy 2 min|6 rounds", "High knees|30 sec", "Lunges|10 each"]),
        ("Cross-training", ["Swim, row or cycle|35 min", "Hip openers|8 each"]),
        ("Long slow session", ["Steady run, hike or ride|45-60 min", "Full-body stretch|8 min"]),
    ],
    "general wellness": [
        ("Full-body basics", ["Bodyweight squats|12", "Push-ups|8-10", "Bird-dog|10 each", "Plank|30 sec"]),
        ("Cardio & mood", ["Brisk walk or cycle|30 min", "Jumping jacks|30", "Arm circles|15 each way"]),
        ("Strength + balance", ["Lunges|10 each", "Dumbbell rows|12", "Single-leg stand|30 sec each", "Glute bridges|15"]),
        REST_DAY,
        ("Mobility & core", ["Cat-cow|12", "Dead bug|10 each", "Hip circles|10 each way", "Bridge hold|30 sec"]),
        ("Fun activity", ["Sport, dance or hike|40 min", "Light stretching|8 min"]),
        ("Gentle recovery", ["Easy stroll|20 min", "Full-body stretch|10 min", "Deep breathing|3 min"]),
    ],
}

TIPS = {
    "weight loss": "Fill half your plate with veggies and add a palm of protein at each meal - it keeps you full while you eat a little less.",
    "muscle gain": "Eat 20-40 g of protein within a couple of hours after training, and don't skip carbs - they refill your energy.",
    "flexibility": "Drink water and stretch when your muscles are warm; 5 minutes after a workout beats 30 cold minutes.",
    "endurance": "Eat carbs before long sessions and add a pinch of salt to your water on hot days to replace what you sweat out.",
    "general wellness": "Aim for 7-9 hours of sleep and a glass of water with every meal - the simplest recovery boost there is.",
}


def _key(goal: str) -> str:
    g = (goal or "").lower()
    for k in PLANS:
        if k in g or g in k:
            return k
    if "lose" in g or "fat" in g or "weight" in g:
        return "weight loss"
    if "muscle" in g or "strength" in g or "bulk" in g:
        return "muscle gain"
    if "flex" in g or "yoga" in g or "mobil" in g:
        return "flexibility"
    if "run" in g or "stamina" in g or "cardio" in g:
        return "endurance"
    return "general wellness"


def build_offline_plan(goal: str, intensity: str) -> dict:
    sets, rest = SETS.get(intensity, 3), REST.get(intensity, "45 sec")
    days = []
    for i, (focus, items) in enumerate(PLANS[_key(goal)], start=1):
        exercises = []
        for item in items:
            name, reps = item.split("|")
            timed = any(u in reps for u in ("min", "rounds"))
            exercises.append({
                "name": name,
                "sets": "1" if timed else str(sets),
                "reps": reps,
                "rest": "-" if timed else rest,
            })
        days.append({
            "day": f"Day {i}",
            "focus": focus,
            "warmup": "5 min easy movement: joint circles, light marching, arm swings." if exercises else "",
            "exercises": exercises,
            "cooldown": "5 min slow breathing and gentle stretching." if exercises else "Sleep well, hydrate and walk if you feel like it.",
        })
    return {"source": "offline", "days": days}


def offline_tip(goal: str) -> str:
    return TIPS[_key(goal)]
