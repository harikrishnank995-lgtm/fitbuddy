from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

Goal = Literal["general_wellness", "weight_loss", "muscle_gain", "flexibility"]
Intensity = Literal["low", "medium", "high"]

class UserInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    username: str = Field(min_length=2, max_length=100)
    user_id: str = Field(min_length=2, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=0, le=500)
    goal: Goal
    intensity: Intensity

class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=80)
    feedback: str = Field(min_length=3, max_length=1000)
