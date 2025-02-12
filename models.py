from pydantic import BaseModel
from typing import List, Optional, Dict, Union

class Nutrients(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    vitamins: Optional[List[str]] = None

class MealItem(BaseModel):
    item: str
    portion: str
    nutrients: Optional[Nutrients] = None
    preparation_time: Optional[int] = None
    difficulty_level: Optional[str] = None
    alternatives: Optional[List[str]] = None

class MealPlan(BaseModel):
    meals: Dict[str, List[MealItem]]
    meal_timing: Optional[Dict[str, str]] = None
    hydration_guidelines: Optional[str] = None
    preparation_tips: Optional[List[str]] = None
    storage_instructions: Optional[List[str]] = None
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: float

class Exercise(BaseModel):
    exercise: str
    sets: Optional[str] = None
    duration: Optional[str] = None

class WorkoutPlan(BaseModel):
    weekly_schedule: Dict[str, List[Exercise]]
    intensity_level: str
    estimated_calories_burn: float
    warm_up: Optional[List[str]] = None
    cool_down: Optional[List[str]] = None
    safety_precautions: Optional[List[str]] = None
    progression_tips: Optional[List[str]] = None

class NutritionGoals(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float

class HealthInput(BaseModel):
    age: int
    weight: float
    height: float
    goals: List[str]
    dietary_restrictions: Optional[List[str]] = []
    activity_level: str
    meal_preferences: Optional[List[str]] = []
