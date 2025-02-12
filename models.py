from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union

class Nutrients(BaseModel):
    calories: float = Field(..., ge=0)
    protein: float = Field(..., ge=0)
    carbs: float = Field(..., ge=0)
    fat: float = Field(..., ge=0)
    fiber: float = Field(..., ge=0)
    vitamins: Optional[List[str]] = None

class MealItem(BaseModel):
    item: str = Field(..., min_length=1)
    portion: str = Field(..., min_length=1)
    nutrients: Optional[Nutrients] = None
    preparation_time: Optional[int] = Field(None, ge=0)
    difficulty_level: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    alternatives: Optional[List[str]] = None

    @validator('alternatives')
    def validate_alternatives(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError("Alternatives list cannot be empty")
        return v

class MealPlan(BaseModel):
    meals: Dict[str, List[MealItem]]
    meal_timing: Optional[Dict[str, str]] = None
    hydration_guidelines: Optional[str] = Field(None, min_length=1)
    preparation_tips: Optional[List[str]] = None
    storage_instructions: Optional[List[str]] = None
    total_calories: float = Field(..., ge=0)
    total_protein: float = Field(..., ge=0)
    total_carbs: float = Field(..., ge=0)
    total_fat: float = Field(..., ge=0)
    total_fiber: float = Field(..., ge=0)

    @validator('meals')
    def validate_meals(cls, v):
        valid_days = {'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'}
        provided_days = {day.lower() for day in v.keys()}
        
        # Check if any invalid days were provided
        if not provided_days.issubset(valid_days):
            invalid_days = provided_days - valid_days
            raise ValueError(f"Invalid days in meal plan: {', '.join(invalid_days)}")
            
        # Check if all required days are present
        missing_days = valid_days - provided_days
        if missing_days:
            raise ValueError(f"Meal plan is missing the following days: {', '.join(missing_days)}")
            
        return v

class Exercise(BaseModel):
    exercise: str = Field(..., min_length=1)
    sets: Optional[str] = Field(None, min_length=1)
    duration: Optional[str] = Field(None, min_length=1)

    @validator('exercise')
    def validate_exercise(cls, v):
        if v.lower() == 'rest':
            return v
        return v

class WorkoutPlan(BaseModel):
    weekly_schedule: Dict[str, List[Exercise]]
    intensity_level: str = Field(..., pattern="^(?i)low|medium|high$")
    estimated_calories_burn: float = Field(..., ge=0)
    warm_up: Optional[List[str]] = None
    cool_down: Optional[List[str]] = None
    safety_precautions: Optional[List[str]] = None
    progression_tips: Optional[List[str]] = None

    @validator('weekly_schedule')
    def validate_schedule(cls, v):
        valid_days = {'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'}
        if not all(day.lower() in valid_days for day in v.keys()):
            raise ValueError("Invalid day in workout schedule")
        return v

    @validator('intensity_level')
    def normalize_intensity(cls, v):
        return v.lower()

class NutritionGoals(BaseModel):
    calories: float = Field(..., ge=0)
    protein: float = Field(..., ge=0)
    carbs: float = Field(..., ge=0)
    fat: float = Field(..., ge=0)
    fiber: float = Field(..., ge=0)

class HealthInput(BaseModel):
    age: int = Field(..., gt=0, le=120)
    weight: float = Field(..., gt=0, le=500)
    height: float = Field(..., gt=0, le=300)
    goals: List[str] = Field(..., min_items=1)
    dietary_restrictions: Optional[List[str]] = []
    activity_level: str = Field(..., pattern="^(light|moderate|active|very_active)$")
    meal_preferences: Optional[List[str]] = []

    @validator('goals')
    def validate_goals(cls, v):
        if not v:
            raise ValueError("At least one goal must be specified")
        return v
