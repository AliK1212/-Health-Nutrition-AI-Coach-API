from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response as JSONResponse
from models import HealthInput, MealPlan, WorkoutPlan, NutritionGoals
from health_coach import HealthCoach
import os
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="AI Health and Nutrition Coach",
    description="AI-Powered Health and Nutrition Coaching",
    version="1.0.0"
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize Redis
redis_client = redis.Redis(
    host=os.getenv("RENDER_REDIS_HOST", "localhost"),
    port=int(os.getenv("RENDER_REDIS_PORT", 6379)),
    password=os.getenv("RENDER_REDIS_PASSWORD", ""),
    decode_responses=True
)

# Add CORS middleware
origins = [
    "https://frontend-portfolio-aomn.onrender.com",
    "https://deerk-portfolio.onrender.com",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:4173",
    "https://*.onrender.com",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:8082",
    "http://localhost:8083",
    "http://localhost:8084",
    "http://localhost:8085",
    "http://localhost:8086",
    "http://localhost:8087",
    "http://localhost:8088",
    "http://localhost:8089",
    "http://localhost:8090",
    "http://localhost:8091",
    "http://localhost:8092",
    "http://localhost:8093",
    "http://localhost:8094",
    "http://localhost:8095",
    "http://localhost:8096",
    "http://localhost:8097",
    "http://localhost:8098",
    "http://localhost:8099",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

health_coach = HealthCoach()

@app.options("/{path:path}")
async def options_route(request: Request):
    return JSONResponse(
        content="OK",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "3600",
        }
    )

@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    """Health check endpoint."""
    return {"status": "ok", "message": "Health & Nutrition Coach API is running"}

@app.post("/meal-plan", response_model=MealPlan)
@limiter.limit("10/minute")
async def generate_meal_plan(request: Request, input_data: HealthInput):
    """Generate a personalized meal plan based on user input."""
    try:
        # Validate input data
        if input_data.age <= 0 or input_data.weight <= 0 or input_data.height <= 0:
            raise ValueError("Age, weight, and height must be positive numbers")
        
        # Generate meal plan
        meal_plan = health_coach.generate_meal_plan(input_data.dict())
        return meal_plan
    except ValueError as e:
        logger.error(f"Validation error in meal plan generation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating meal plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while generating meal plan")

@app.post("/analyze-meal")
@limiter.limit("10/minute")
async def analyze_meal(request: Request, meal_data: dict):
    """Analyze the nutritional content of a meal."""
    try:
        if not meal_data or not isinstance(meal_data, dict):
            raise ValueError("Invalid meal data format")
        
        analysis = health_coach.analyze_nutritional_content(meal_data)
        return analysis
    except ValueError as e:
        logger.error(f"Validation error in meal analysis: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing meal: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while analyzing meal")

@app.post("/workout-plan", response_model=WorkoutPlan)
@limiter.limit("10/minute")
async def get_workout_plan(request: Request, input_data: HealthInput):
    try:
        coach = HealthCoach()
        return await coach.generate_workout_plan(input_data.dict())
    except Exception as e:
        logger.error(f"Workout plan error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Workout plan generation failed: {str(e)}"}
        )

@app.post("/nutrition-goals", response_model=NutritionGoals)
@limiter.limit("10/minute")
async def get_nutrition_goals(request: Request, input_data: HealthInput):
    """Calculate nutrition goals based on user input."""
    try:
        # Validate input data
        if input_data.age <= 0 or input_data.weight <= 0 or input_data.height <= 0:
            raise ValueError("Age, weight, and height must be positive numbers")
        
        # Calculate nutrition goals
        goals = health_coach.get_nutrition_goals(input_data.dict())
        return goals
    except ValueError as e:
        logger.error(f"Validation error in nutrition goals calculation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating nutrition goals: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while calculating nutrition goals")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
