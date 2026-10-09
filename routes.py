import os
import secrets
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import User, WorkoutPlan
from app.schemas import UserInput, FeedbackRequest
from app.ai_service import generate_workout_gemini, generate_nutrition_tip_with_flash, update_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
security = HTTPBasic()

def _admin_auth(credentials: HTTPBasicCredentials = Depends(security)):
    expected_user = os.getenv("ADMIN_USERNAME", "admin")
    expected_password = os.getenv("ADMIN_PASSWORD", "change-me")
    ok_user = secrets.compare_digest(credentials.username, expected_user)
    ok_pass = secrets.compare_digest(credentials.password, expected_password)
    if not (ok_user and ok_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect admin credentials",
                            headers={"WWW-Authenticate": "Basic"})
    return credentials.username

def _render_result(request, user, plan, tip, updated_plan=None, message=None):
    return templates.TemplateResponse(request=request, name="result.html", context={
        "user": user, "workout_plan": plan, "nutrition_tip": tip,
        "updated_plan": updated_plan, "message": message
    })

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...), user_id: str = Form(...), age: int = Form(...),
    weight: float = Form(...), goal: str = Form(...), intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(username=username, user_id=user_id, age=age, weight=weight, goal=goal, intensity=intensity)
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="index.html",
            context={"error": f"Please check your entries. {exc}"}, status_code=422)

    plan = generate_workout_gemini(data.username, data.age, data.weight, data.goal, data.intensity)
    tip = generate_nutrition_tip_with_flash(data.goal)
    user = db.query(User).filter(User.user_id == data.user_id).first()
    if user:
        user.username, user.age, user.weight = data.username, data.age, data.weight
        user.goal, user.intensity = data.goal, data.intensity
        db.query(WorkoutPlan).filter(WorkoutPlan.user_id == data.user_id).delete(synchronize_session=False)
    else:
        user = User(user_id=data.user_id, username=data.username, age=data.age, weight=data.weight,
                    goal=data.goal, intensity=data.intensity)
        db.add(user)
    db.flush()
    record = WorkoutPlan(user_id=data.user_id, original_plan=plan, nutrition_tip=tip)
    db.add(record)
    db.commit()
    db.refresh(user)
    return _render_result(request, user, plan, tip)

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request, user_id: str = Form(...), feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = FeedbackRequest(user_id=user_id, feedback=feedback)
    except Exception:
        raise HTTPException(status_code=422, detail="Enter a valid user ID and feedback (3–1000 characters).")
    user = db.query(User).options(joinedload(User.plans)).filter(User.user_id == data.user_id).first()
    if not user or not user.plans:
        raise HTTPException(status_code=404, detail="User or workout plan not found. Generate a plan first.")
    record = max(user.plans, key=lambda p: p.created_at)
    updated = update_workout_plan(record.original_plan, data.feedback, user.goal, user.intensity)
    record.updated_plan = updated
    record.last_feedback = data.feedback
    record.nutrition_tip = generate_nutrition_tip_with_flash(user.goal)
    db.commit()
    return _render_result(request, user, record.original_plan, record.nutrition_tip,
                          updated_plan=updated, message="Your plan has been updated.")

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, _: str = Depends(_admin_auth), db: Session = Depends(get_db)):
    users = db.query(User).options(joinedload(User.plans)).order_by(User.created_at.desc()).all()
    return templates.TemplateResponse(request=request, name="all_users.html", context={"users": users})

@router.get("/health")
def health():
    return {"status": "ok", "app": "FitBuddy"}

@router.post("/api/generate-workout")
def api_generate(data: UserInput, db: Session = Depends(get_db)):
    plan = generate_workout_gemini(data.username, data.age, data.weight, data.goal, data.intensity)
    tip = generate_nutrition_tip_with_flash(data.goal)
    user = db.query(User).filter(User.user_id == data.user_id).first()
    if user is None:
        user = User(user_id=data.user_id, username=data.username, age=data.age, weight=data.weight,
                    goal=data.goal, intensity=data.intensity)
        db.add(user)
    else:
        user.username, user.age, user.weight, user.goal, user.intensity = data.username, data.age, data.weight, data.goal, data.intensity
    db.flush()
    record = WorkoutPlan(user_id=data.user_id, original_plan=plan, nutrition_tip=tip)
    db.add(record)
    db.commit()
    return {"user_id": data.user_id, "workout_plan": plan, "nutrition_tip": tip}

@router.post("/api/submit-feedback")
def api_feedback(data: FeedbackRequest, db: Session = Depends(get_db)):
    user = db.query(User).options(joinedload(User.plans)).filter(User.user_id == data.user_id).first()
    if not user or not user.plans:
        raise HTTPException(status_code=404, detail="User or plan not found.")
    record = max(user.plans, key=lambda p: p.created_at)
    record.updated_plan = update_workout_plan(record.original_plan, data.feedback, user.goal, user.intensity)
    record.last_feedback = data.feedback
    db.commit()
    return {"user_id": data.user_id, "updated_plan": record.updated_plan}
