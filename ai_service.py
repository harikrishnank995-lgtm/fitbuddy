"""Gemini integration with a safe, useful local demo fallback."""
import os
from google import genai
from google.genai import types

def _client():
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=key) if key else None

def _generate(prompt: str, model: str, fallback: str) -> str:
    client = _client()
    if not client:
        return fallback + "\n\n[Demo mode: add GOOGLE_API_KEY to .env to enable Gemini-generated content.]"
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7),
        )
        text = (response.text or "").strip()
        return text if text else fallback
    except Exception:
        # Keep the app usable if the external API is unavailable or quota is exhausted.
        return fallback + "\n\n[Gemini is temporarily unavailable. Showing a sample plan instead.]"

def generate_workout_gemini(username: str, age: int, weight: float, goal: str, intensity: str) -> str:
    fallback = f"""7-DAY STARTER PLAN — {goal.replace('_', ' ').title()}
Day 1 — Full body: 5–10 min easy warm-up; chair squats, wall push-ups and glute bridges (2 sets of 8–12); gentle cool-down.
Day 2 — Cardio: 15–25 min comfortable walking or cycling; stretch gently.
Day 3 — Mobility: 15–20 min beginner-friendly mobility and balance; stop if uncomfortable.
Day 4 — Recovery: easy walk or rest, based on how you feel.
Day 5 — Full body: repeat Day 1 with comfortable effort; prioritize controlled technique.
Day 6 — Cardio + core: 15–25 min comfortable movement and 2 gentle core exercises.
Day 7 — Rest and reflect: light stretching if desired; prepare for the next week."""
    prompt = f"""Create a safe, realistic 7-day beginner-accessible fitness plan.
Name: {username}; age: {age}; weight kg: {weight}; goal: {goal}; requested intensity: {intensity}.
Include for each day: focus, 5-10 minute warm-up, main activity with sets/reps or duration, and cooldown/recovery.
Include rest/recovery days and low-impact alternatives. Do not prescribe extreme exercise, rapid weight loss, supplements, or calorie targets. Tell the user to stop if pain/dizziness occurs and consult a qualified professional for medical concerns. Keep formatting clear and concise."""
    return _generate(prompt, os.getenv("GEMINI_MODEL_WORKOUT", "gemini-2.5-pro"), fallback)

def generate_nutrition_tip_with_flash(goal: str) -> str:
    fallbacks = {
        "muscle_gain": "Include a source of protein in regular meals, drink water, and allow enough sleep and recovery.",
        "weight_loss": "Aim for balanced, regular meals with vegetables, fruit, protein and fiber; avoid crash diets and stay hydrated.",
        "flexibility": "Hydrate regularly and pair mobility practice with balanced meals and adequate recovery.",
        "general_wellness": "Build balanced meals with varied vegetables and fruit, protein, whole grains, and water throughout the day.",
    }
    fallback = fallbacks.get(goal, fallbacks["general_wellness"])
    prompt = f"Give one concise, safe nutrition or recovery tip for the fitness goal '{goal}'. Avoid medical claims, restrictive diets, calorie prescriptions, and supplements. Encourage balanced eating and hydration."
    return _generate(prompt, os.getenv("GEMINI_MODEL_TIP", "gemini-2.5-flash"), fallback)

def update_workout_plan(original_plan: str, feedback: str, goal: str, intensity: str) -> str:
    fallback = original_plan + "\n\nUpdated for your feedback: " + feedback + "\nAdjust sessions to a comfortable level, include recovery days, and choose low-impact options whenever needed."
    prompt = f"""Revise this 7-day fitness plan based on user feedback. Keep it safe, realistic, and goal-appropriate.
Goal: {goal}; requested intensity: {intensity}
Original plan:
{original_plan}
User feedback:
{feedback}
Return the complete revised 7-day plan with warm-up, main activity, cooldown/recovery, and rest days. Do not recommend extreme activity or restrictive eating. If feedback requests something unsafe, offer a safer alternative."""
    return _generate(prompt, os.getenv("GEMINI_MODEL_WORKOUT", "gemini-2.5-pro"), fallback)
