from pydantic import BaseModel
from typing import List, Optional, Dict

class HealthInput(BaseModel):
    age: int
    weight: float
    height: float
    goals: List[str]
    dietary_restrictions: Optional[List[str]] = []
    activity_level: str
    meal_preferences: Optional[List[str]] = []

class MealPlan(BaseModel):
    meals: Dict[str, List[Dict[str, str]]]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float

class WorkoutPlan(BaseModel):
    weekly_schedule: Dict[str, List[Dict[str, str]]]
    intensity_level: str
    estimated_calories_burn: float

class NutritionGoals(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
