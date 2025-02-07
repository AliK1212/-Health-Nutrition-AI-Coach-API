from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import HealthInput, MealPlan, WorkoutPlan, NutritionGoals
from health_coach import HealthCoach
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Health & Nutrition Coach API",
    description="AI-Powered Health and Nutrition Recommendations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

health_coach = HealthCoach()

@app.options("/api/{path:path}")
async def options_route(request: Request):
    return JSONResponse(
        content="OK",
        headers={
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Methods": "POST, GET, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )

@app.post("/api/meal-plan", response_model=MealPlan)
async def generate_meal_plan(input_data: HealthInput):
    try:
        meal_plan = health_coach.generate_meal_plan(input_data.dict())
        return meal_plan
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/analyze-meal")
async def analyze_meal(meal_data: dict):
    try:
        analysis = health_coach.analyze_nutritional_content(meal_data)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/workout-plan", response_model=WorkoutPlan)
async def generate_workout_plan(input_data: HealthInput):
    try:
        workout_plan = health_coach.generate_workout_plan(input_data.dict())
        return workout_plan
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/nutrition-goals", response_model=NutritionGoals)
async def get_nutrition_goals(input_data: HealthInput):
    try:
        goals = health_coach.get_nutrition_goals(input_data.dict())
        return goals
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
