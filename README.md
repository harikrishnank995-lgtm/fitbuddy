# FitBuddy — AI Fitness Plan Generator

A complete FastAPI + Jinja2 + SQLite web app based on the uploaded project brief. It supports:
- Personalized 7-day workout plans
- Goal-related nutrition/recovery tips
- Feedback-based plan updates
- SQLite storage with SQLAlchemy
- Protected coach/admin dashboard
- JSON API endpoints and FastAPI interactive docs
- Demo mode when no Gemini API key is configured

## 1. Requirements
- Python 3.10 or newer
- Git (optional, for GitHub upload)
- A Gemini API key for live AI generation (optional for demo mode)

## 2. Run in VS Code on Windows
Open this folder in VS Code, then choose **Terminal → New Terminal**.

```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

If PowerShell blocks activation, use Command Prompt terminal instead:
```bat
.venv\\Scripts\\activate.bat
```

Open `.env` and add your API key:
```env
GOOGLE_API_KEY=your_real_gemini_api_key
```
Get a key from Google AI Studio. Keep `.env` private; it is excluded by `.gitignore`. You can leave the key blank to try demo mode.

For the coach dashboard, change `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env`.

Start the app:
```powershell
python run.py
```
Then open:
- Website: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
- Coach dashboard: http://127.0.0.1:8000/view-all-users (browser asks for admin credentials)

Stop the server with `Ctrl+C`.

## 3. Test
In a second terminal, activate `.venv` and run:
```powershell
pytest -q
```

## 4. API examples
In `/docs`, use `POST /api/generate-workout` with:
```json
{
  "username": "Alex",
  "user_id": "alex_01",
  "age": 24,
  "weight": 68,
  "goal": "general_wellness",
  "intensity": "medium"
}
```
Allowed goals: `general_wellness`, `weight_loss`, `muscle_gain`, `flexibility`.
Allowed intensities: `low`, `medium`, `high`.

Feedback endpoint `POST /api/submit-feedback`:
```json
{
  "user_id": "alex_01",
  "feedback": "Please include more walking and an extra recovery day."
}
```

## 5. Upload this project to GitHub
1. Create a new **empty** repository on GitHub (for example, `fitbuddy-ai-fitness`).
2. In VS Code terminal, from this project folder run:
```bash
git init
git add .
git commit -m "Build FitBuddy AI fitness planner"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/fitbuddy-ai-fitness.git
git push -u origin main
```
3. Replace `YOUR-USERNAME` with your GitHub username and use your actual repository URL.
4. Never upload `.env`, API keys, or the generated `fitbuddy.db` database.

## Notes
- Gemini model availability can vary by account and API access. If a model is unavailable, change `GEMINI_MODEL_WORKOUT` or `GEMINI_MODEL_TIP` in `.env` to a model enabled for your key.
- Workout plans are general information and not medical advice. Start at a comfortable level and seek qualified professional guidance for health concerns.
- Admin dashboard uses HTTP Basic authentication. Change the default credentials before using outside local development.
