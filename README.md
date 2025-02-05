# Health & Nutrition AI Coach API

An AI-powered health and nutrition coach that provides personalized meal plans, workout routines, and nutrition advice. Built with FastAPI and Llama 2, this service offers intelligent recommendations based on individual health goals and preferences.

## Features

- **Personalized Meal Planning**: Generate customized meal plans based on:
  - Dietary preferences and restrictions
  - Caloric needs
  - Macronutrient requirements
  - Food allergies and intolerances

- **Workout Recommendations**: Create tailored exercise routines considering:
  - Fitness goals (weight loss, muscle gain, maintenance)
  - Current fitness level
  - Available equipment
  - Time constraints
  - Physical limitations

- **Nutrition Analysis**: Provide detailed nutritional insights:
  - Daily caloric requirements
  - Macronutrient distribution
  - Micronutrient recommendations
  - Meal timing suggestions

## Tech Stack

- **Backend**: FastAPI
- **AI Model**: Llama 2 (7B Chat)
- **Nutrition Data**: OpenFoodFacts API
- **Containerization**: Docker
- **Frontend**: React with TailwindCSS

## API Endpoints

### 1. Generate Meal Plan
```http
POST /api/meal-plan
```
Generates a personalized meal plan based on user preferences and requirements.

**Request Body**:
```json
{
  "age": "25",
  "weight": "70",
  "height": "175",
  "goals": ["weight_loss", "muscle_gain"],
  "dietary_restrictions": ["vegetarian"],
  "activity_level": "moderate",
  "meal_preferences": ["high_protein", "low_carb"]
}
```

### 2. Analyze Nutritional Goals
```http
POST /api/nutrition-goals
```
Calculates personalized nutrition goals based on user data.

**Request Body**:
```json
{
  "age": "25",
  "weight": "70",
  "height": "175",
  "activity_level": "moderate",
  "goals": ["weight_loss"]
}
```

### 3. Generate Workout Plan
```http
POST /api/workout-plan
```
Creates a customized workout routine based on fitness goals and preferences.

**Request Body**:
```json
{
  "fitness_level": "intermediate",
  "goals": ["muscle_gain"],
  "available_equipment": ["dumbbells", "bodyweight"],
  "days_per_week": 4
}
```

## Environment Variables

```env
MODEL_PATH=/app/models/llama-2-7b-chat.gguf
MAX_TOKENS=2048
OPENFOODFACTS_USER_AGENT="HealthNutritionAPI - Development"
```

## Docker Setup

The service is containerized using Docker and can be run as part of the larger application stack or independently.

### Running with Docker Compose
```bash
# Start the service
docker-compose up health-nutrition-api

# Stop the service
docker-compose down health-nutrition-api
```

### Building the Docker Image
```bash
docker build -t health-nutrition-api ./services/health-nutrition-api
```

### Running the Container
```bash
docker run -p 8004:8000 \
  -v ./models:/app/models \
  --env-file ./services/health-nutrition-api/.env \
  health-nutrition-api
```

## Development Setup

1. Clone the repository
```bash
git clone <repository-url>
cd project/services/health-nutrition-api
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Download the Llama 2 model
```bash
# Download the model and place it in the models directory
mkdir -p models
# Place llama-2-7b-chat.gguf in the models directory
```

5. Start the development server
```bash
uvicorn main:app --reload --port 8004
```

## Testing

Access the API documentation at `http://localhost:8004/docs` to test the endpoints using the Swagger UI.

Example curl commands:

```bash
# Generate a meal plan
curl -X POST http://localhost:8004/api/meal-plan \
  -H "Content-Type: application/json" \
  -d '{"age":"25","weight":"70","height":"175","goals":["weight_loss"],"dietary_restrictions":["vegetarian"],"activity_level":"moderate"}'

# Get nutrition goals
curl -X POST http://localhost:8004/api/nutrition-goals \
  -H "Content-Type: application/json" \
  -d '{"age":"25","weight":"70","height":"175","activity_level":"moderate","goals":["weight_loss"]}'
```

## Frontend Integration

The service is integrated into the main application and can be accessed through:
1. The Projects page
2. The AI Services section in the footer
3. Direct URL at `/health-nutrition`


