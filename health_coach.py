from typing import List, Dict
import os
from openai import OpenAI
import requests
from models import MealPlan, WorkoutPlan, NutritionGoals
from functools import lru_cache

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class HealthCoach:
    def __init__(self):
        self.OPENFOODFACTS_URL = "https://world.openfoodfacts.org/api/v0/product/"

    def _is_rest_day(self, exercises):
        """Check if a day is a rest day by looking at its exercises."""
        if not exercises:
            return True
        if len(exercises) == 1 and exercises[0].get('exercise', '').lower().startswith('rest'):
            return True
        return False

    def generate_meal_plan(self, input_data: dict) -> MealPlan:
        """Generate a personalized meal plan based on user preferences."""
        try:
            user_profile = f"""
            Age: {input_data.get('age')} years
            Weight: {input_data.get('weight')} kg
            Height: {input_data.get('height')} cm
            Goals: {', '.join(input_data.get('goals', []))}
            Dietary Restrictions: {', '.join(input_data.get('dietary_restrictions', []))}
            Activity Level: {input_data.get('activity_level')}
            Meal Preferences: {', '.join(input_data.get('meal_preferences', []))}
            """

            json_structure = """
            {
                "meals": {
                    "monday": [
                        {
                            "item": "Breakfast: Oatmeal with berries",
                            "portion": "1 cup oats, 1/2 cup berries",
                            "nutrients": {
                                "calories": 300,
                                "protein": 10,
                                "carbs": 45,
                                "fat": 6,
                                "fiber": 8,
                                "vitamins": ["B", "C", "D"]
                            },
                            "preparation_time": 15,
                            "difficulty_level": "easy",
                            "alternatives": ["Whole grain toast with avocado", "Protein smoothie bowl"]
                        }
                    ]
                },
                "meal_timing": {
                    "breakfast": "7:00 AM",
                    "lunch": "12:30 PM",
                    "dinner": "6:30 PM",
                    "snacks": "10:00 AM, 3:30 PM"
                },
                "hydration_guidelines": "Drink 8-10 glasses of water daily",
                "preparation_tips": [
                    "Meal prep on Sundays",
                    "Store proteins separately"
                ],
                "storage_instructions": [
                    "Keep prepared meals refrigerated",
                    "Use airtight containers"
                ],
                "total_calories": 2500,
                "total_protein": 180,
                "total_carbs": 300,
                "total_fat": 70,
                "total_fiber": 35
            }
            """

            requirements = """
            For EACH DAY of the week (monday through sunday), include:
            1. 3 main meals (breakfast, lunch, dinner)
            2. 2-3 snacks
            3. Each meal must include:
               - Exact item name and description
               - Precise portions
               - Complete nutritional information (calories, protein, carbs, fat, fiber)
               - Optional vitamins list
               - Preparation time in minutes
               - Difficulty level (easy, medium, hard)
               - At least 2 alternatives
            4. Meal timing for all meals
            5. Comprehensive hydration guidelines
            6. At least 3 preparation tips
            7. At least 3 storage instructions
            8. Accurate total nutritional values

            IMPORTANT: Do not use [...] placeholders. Provide complete data for all 7 days.
            """

            prompt = f"""Generate a detailed, nutritionally balanced meal plan in JSON format for someone with the following profile:
{user_profile}

The response should be a valid JSON object with the following structure:
{json_structure}

Requirements:
{requirements}

The response must be a valid JSON object that can be parsed directly."""

            messages = [
                {
                    "role": "system", 
                    "content": """You are an expert nutritionist and meal planner. Generate evidence-based meal plans.
IMPORTANT: 
1. You must ONLY return a valid JSON object. Do not include ANY explanatory text.
2. Your entire response must be parseable as JSON.
3. You MUST include ALL 7 days of the week in the 'meals' object: monday, tuesday, wednesday, thursday, friday, saturday, and sunday.
4. Each day MUST have at least 5 meals (3 main meals + 2 snacks).
5. Each meal must include all required fields (item, portion, nutrients, etc.).
6. Include detailed nutritional information for each meal.
7. DO NOT use [...] or placeholder values.
8. DO NOT skip any days - all seven days are required."""
                },
                {"role": "user", "content": prompt}
            ]

            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=5000,
                temperature=0.7,
                timeout=30
            )

            try:
                meal_plan_data = response.choices[0].message.content
                if not isinstance(meal_plan_data, dict):
                    import json
                    json_start = meal_plan_data.find('{')
                    json_end = meal_plan_data.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        meal_plan_data = meal_plan_data[json_start:json_end]
                    meal_plan_data = json.loads(meal_plan_data)

                # Validate required fields
                required_fields = ['meals', 'total_calories', 'total_protein', 'total_carbs', 'total_fat', 'total_fiber']
                if not all(field in meal_plan_data for field in required_fields):
                    raise ValueError("Missing required fields in meal plan data")

                # Validate meal structure
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                for day in days:
                    if day not in meal_plan_data['meals']:
                        raise ValueError(f"Missing {day} in meal plan data")
                    meals = meal_plan_data['meals'][day]
                    if not isinstance(meals, list) or len(meals) < 5:
                        raise ValueError(f"Insufficient meals for {day}")
                    
                    # Validate each meal item
                    for meal in meals:
                        required_meal_fields = ['item', 'portion']
                        if not all(field in meal for field in required_meal_fields):
                            raise ValueError(f"Missing required fields in meal item for {day}")
                        
                        if 'nutrients' in meal:
                            required_nutrient_fields = ['calories', 'protein', 'carbs', 'fat', 'fiber']
                            if not all(field in meal['nutrients'] for field in required_nutrient_fields):
                                raise ValueError(f"Missing required nutrient fields in meal item for {day}")

                meal_plan = MealPlan(
                    meals=meal_plan_data["meals"],
                    meal_timing=meal_plan_data.get("meal_timing"),
                    hydration_guidelines=meal_plan_data.get("hydration_guidelines"),
                    preparation_tips=meal_plan_data.get("preparation_tips"),
                    storage_instructions=meal_plan_data.get("storage_instructions"),
                    total_calories=meal_plan_data["total_calories"],
                    total_protein=meal_plan_data["total_protein"],
                    total_carbs=meal_plan_data["total_carbs"],
                    total_fat=meal_plan_data["total_fat"],
                    total_fiber=meal_plan_data["total_fiber"]
                )

                return meal_plan

            except Exception as e:
                import logging
                logging.error(f"Error parsing meal plan: {str(e)}")
                logging.error(f"Raw response: {meal_plan_data}")
                raise ValueError("Failed to parse the meal plan response from the AI model")

        except Exception as e:
            raise ValueError(f"Error generating meal plan: {str(e)}")

    async def generate_workout_plan(self, profile_data: dict) -> WorkoutPlan:
        """Generate a comprehensive workout plan based on user profile."""
        try:
            user_profile = f"""
            Age: {profile_data.get('age')} years
            Weight: {profile_data.get('weight')} kg
            Height: {profile_data.get('height')} cm
            Goals: {', '.join(profile_data.get('goals', []))}
            Activity Level: {profile_data.get('activity_level')}
            """

            json_structure = """
            {
                "weekly_schedule": {
                    "monday": [
                        {
                            "exercise": "Barbell Squats",
                            "sets": "4 sets of 8-12 reps",
                            "duration": "15 min"
                        }
                    ]
                },
                "intensity_level": "High",
                "estimated_calories_burn": 3000,
                "warm_up": [
                    "5-10 minutes light cardio",
                    "Dynamic stretching for major muscle groups"
                ],
                "cool_down": [
                    "5 minutes light cardio",
                    "Static stretching"
                ],
                "safety_precautions": [
                    "Always warm up properly",
                    "Use proper form",
                    "Start with lighter weights"
                ],
                "progression_tips": [
                    "Increase weight by 5-10% when you can complete all sets",
                    "Focus on form before increasing weight"
                ]
            }
            """

            requirements = """
            For each training day:
            1. Include 4-6 exercises for training days
            2. Each exercise must include:
               - Exercise name and description
               - Sets and reps or duration
               - Rest periods between sets
            3. Mix of compound and isolation exercises
            4. Include both strength and cardio components
            5. Proper form descriptions
            6. Rest days should be marked explicitly
            7. Progressive overload recommendations
            8. Comprehensive warm-up and cool-down routines

            IMPORTANT: Do not use [...] placeholders. Provide complete workout data for all 7 days.
            """

            prompt = f"""Generate a detailed workout plan in JSON format for someone with the following profile:
{user_profile}

The response should be a valid JSON object with the following structure:
{json_structure}

Requirements:
{requirements}

The response must be a valid JSON object that can be parsed directly."""

            messages = [
                {
                    "role": "system", 
                    "content": """You are an expert fitness trainer. Generate concise workout plans.
IMPORTANT:
1. Intensity level must be lowercase: 'low', 'medium', or 'high'
2. Rest days must be [{"exercise": "Rest"}]
3. Maximum 3-5 exercises per day
4. Use abbreviated formats: '4x8-12' instead of '4 sets of 8-12 reps'"""
                },
                {"role": "user", "content": prompt}
            ]

            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                max_tokens=1200,
                temperature=0.7,
                timeout=15
            )

            try:
                workout_data = response.choices[0].message.content
                if not isinstance(workout_data, dict):
                    import json
                    json_start = workout_data.find('{')
                    json_end = workout_data.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        workout_data = workout_data[json_start:json_end]
                    workout_data = json.loads(workout_data)

                # Convert string rest days to proper format
                for day, exercises in workout_data['weekly_schedule'].items():
                    if isinstance(exercises, str) and exercises.lower() == 'rest':
                        workout_data['weekly_schedule'][day] = [{"exercise": "Rest"}]
                    elif not isinstance(exercises, list):
                        raise ValueError(f"Invalid exercise data for {day}")

                # Validate required fields
                required_fields = ['weekly_schedule', 'intensity_level', 'estimated_calories_burn']
                if not all(field in workout_data for field in required_fields):
                    raise ValueError("Missing required fields in workout plan data")

                # Validate weekly schedule
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                for day in days:
                    if day not in workout_data['weekly_schedule']:
                        raise ValueError(f"Missing {day} in workout schedule")
                    
                    exercises = workout_data['weekly_schedule'][day]
                    if not isinstance(exercises, list):
                        raise ValueError(f"Invalid exercise data for {day}")
                    
                    # Skip detailed validation for rest days
                    if len(exercises) == 1 and exercises[0].get('exercise', '').lower() == 'rest':
                        continue
                        
                    # Validate each exercise
                    for exercise in exercises:
                        if not isinstance(exercise, dict):
                            raise ValueError(f"Invalid exercise format in {day}")
                        if 'exercise' not in exercise:
                            raise ValueError(f"Missing exercise name in {day}")
                        if exercise['exercise'].lower() != 'rest' and not any(k in exercise for k in ['sets', 'duration']):
                            raise ValueError(f"Exercise must have either sets or duration in {day}")

                workout_plan = WorkoutPlan(
                    weekly_schedule=workout_data["weekly_schedule"],
                    intensity_level=workout_data["intensity_level"],
                    estimated_calories_burn=workout_data["estimated_calories_burn"],
                    warm_up=workout_data.get("warm_up"),
                    cool_down=workout_data.get("cool_down"),
                    safety_precautions=workout_data.get("safety_precautions"),
                    progression_tips=workout_data.get("progression_tips")
                )

                return workout_plan

            except Exception as e:
                import logging
                logging.error(f"Error parsing workout plan: {str(e)}")
                logging.error(f"Raw response: {workout_data}")
                raise ValueError("Failed to parse the workout plan response from the AI model")

        except Exception as e:
            raise ValueError(f"Error generating workout plan: {str(e)}")

    def get_nutrition_goals(self, profile_data: dict) -> NutritionGoals:
        """Calculate comprehensive nutrition goals based on user profile."""
        # Calculate base metabolic rate using Mifflin-St Jeor Equation
        age = int(profile_data.get('age', 0))
        weight = float(profile_data.get('weight', 0))
        height = float(profile_data.get('height', 0))
        activity_level = profile_data.get('activity_level', 'moderate')
        goals = profile_data.get('goals', [])

        # Calculate BMR
        bmr = (10 * weight) + (6.25 * height) - (5 * age)

        # Activity level multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }

        # Calculate TDEE (Total Daily Energy Expenditure)
        tdee = bmr * activity_multipliers.get(activity_level, 1.55)

        # Adjust calories based on goals
        calorie_adjustment = 0
        if 'weight_loss' in goals:
            calorie_adjustment = -500  # Create a deficit
        elif 'muscle_gain' in goals:
            calorie_adjustment = 300   # Create a surplus

        final_calories = tdee + calorie_adjustment

        # Calculate macronutrient ratios based on goals
        protein_ratio = 0.3  # 30% of calories from protein
        fat_ratio = 0.25     # 25% of calories from fat
        carb_ratio = 0.45    # 45% of calories from carbs

        if 'muscle_gain' in goals:
            protein_ratio = 0.35
            carb_ratio = 0.45
            fat_ratio = 0.20
        elif 'weight_loss' in goals:
            protein_ratio = 0.40
            fat_ratio = 0.30
            carb_ratio = 0.30

        # Calculate macros in grams
        protein = (final_calories * protein_ratio) / 4  # 4 calories per gram of protein
        carbs = (final_calories * carb_ratio) / 4      # 4 calories per gram of carbs
        fat = (final_calories * fat_ratio) / 9         # 9 calories per gram of fat
        fiber = weight * 0.5  # 0.5g fiber per kg of body weight

        return NutritionGoals(
            calories=round(final_calories),
            protein=round(protein),
            carbs=round(carbs),
            fat=round(fat),
            fiber=round(fiber),
            hydration=round(weight * 0.033, 1),  # 33ml per kg of body weight
            meal_timing={
                'breakfast': '15-25% of daily calories',
                'lunch': '25-35% of daily calories',
                'dinner': '25-35% of daily calories',
                'snacks': '15-25% of daily calories'
            },
            micronutrient_focus=[
                'Vitamin D',
                'Omega-3 fatty acids',
                'Iron',
                'Calcium',
                'Magnesium',
                'Zinc'
            ],
            supplements_recommended=self._get_supplement_recommendations(goals)
        )

    def _get_supplement_recommendations(self, goals: List[str]) -> List[dict]:
        """Get personalized supplement recommendations based on goals."""
        base_supplements = [
            {
                'name': 'Multivitamin',
                'dosage': '1 tablet',
                'timing': 'With breakfast',
                'purpose': 'Fill potential micronutrient gaps'
            }
        ]

        if 'muscle_gain' in goals:
            base_supplements.extend([
                {
                    'name': 'Creatine Monohydrate',
                    'dosage': '5g daily',
                    'timing': 'Any time',
                    'purpose': 'Improve strength and muscle gains'
                },
                {
                    'name': 'Whey Protein',
                    'dosage': '25-30g',
                    'timing': 'Post-workout',
                    'purpose': 'Support muscle recovery and growth'
                }
            ])

        return base_supplements

    def _get_food_nutrients(self, food_item: str) -> dict:
        """Fetch nutrition data from OpenFoodFacts API"""
        try:
            headers = {
                "User-Agent": os.getenv("OPENFOODFACTS_USER_AGENT", "HealthNutritionAPI - Python")
            }
            response = requests.get(f"{self.OPENFOODFACTS_URL}/{food_item}.json", headers=headers)
            data = response.json()
            
            if data.get("status") == 1:
                nutrients = data["product"]["nutriments"]
                return {
                    "calories": nutrients.get("energy-kcal_100g", 0),
                    "protein": nutrients.get("proteins_100g", 0),
                    "carbs": nutrients.get("carbohydrates_100g", 0),
                    "fat": nutrients.get("fat_100g", 0),
                    "fiber": nutrients.get("fiber_100g", 0)
                }
            return {}
        except Exception:
            return {}

    def _calculate_nutrition_goals(self, profile: dict) -> NutritionGoals:
        # Basic BMR calculation using Harris-Benedict equation
        weight = profile["weight"]
        height = profile["height"]
        age = profile["age"]
        activity_level = profile["activity_level"]
        goals = profile["goals"]

        # Activity level multipliers
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }

        # Calculate BMR
        bmr = 10 * weight + 6.25 * height - 5 * age
        
        # Adjust for activity level
        tdee = bmr * activity_multipliers.get(activity_level, 1.2)

        # Adjust based on goals
        if "weight_loss" in goals:
            calories = tdee - 500
        elif "muscle_gain" in goals:
            calories = tdee + 300
        else:
            calories = tdee

        return NutritionGoals(
            calories=round(calories),
            protein=round(weight * 2.2),  # 2.2g per kg of body weight
            carbs=round(calories * 0.45 / 4),  # 45% of calories from carbs
            fat=round(calories * 0.25 / 9),  # 25% of calories from fat
            fiber=30  # General recommendation
        )

    def _create_workout_plan_prompt(self, profile: dict) -> str:
        """Create a prompt for workout plan generation."""
        # Create user profile section
        user_profile = f"""
        Age: {profile.get('age')} years
        Weight: {profile.get('weight')} kg
        Height: {profile.get('height')} cm
        Goals: {', '.join(profile.get('goals', []))}
        Activity Level: {profile.get('activity_level')}
        """

        # Define the expected JSON structure
        json_structure = """
        {
            "weekly_schedule": {
                "monday": [{"exercise": "...", "sets": "...", "duration": "..."}],
                "tuesday": [{"exercise": "...", "sets": "...", "duration": "..."}],
                "wednesday": [{"exercise": "...", "sets": "...", "duration": "..."}],
                "thursday": [{"exercise": "...", "sets": "...", "duration": "..."}],
                "friday": [{"exercise": "...", "sets": "...", "duration": "..."}],
                "saturday": [{"exercise": "...", "sets": "...", "duration": "..."}],
                "sunday": [{"exercise": "...", "sets": "...", "duration": "..."}]
            },
            "intensity_level": "...",
            "estimated_calories_burn": 0,
            "warm_up": ["...", "..."],
            "cool_down": ["...", "..."],
            "safety_precautions": ["...", "..."],
            "progression_tips": ["...", "..."]
        }
        """

        # Combine all parts into the final prompt
        return f"""Create a workout plan for a person with the following profile:
{user_profile}

The response should be a valid JSON object with the following structure:
{json_structure}

The response must be a valid JSON object that can be parsed directly."""

    def _parse_meal_plan_response(self, response_text: str) -> MealPlan:
        # Parse the AI response into a structured meal plan
        meals = {}
        
        # Split the response into sections
        sections = response_text.split("\n\n")
        current_meal = None
        meal_items = []
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0

        for section in sections:
            if "Breakfast:" in section:
                current_meal = "breakfast"
                meal_items = []
                items = section.replace("Breakfast:", "").strip().split("\n")
                for item in items:
                    if item.strip():
                        meal_items.append({"item": item.strip(), "portion": "1 serving"})
                meals[current_meal] = meal_items
            elif "Lunch:" in section:
                current_meal = "lunch"
                meal_items = []
                items = section.replace("Lunch:", "").strip().split("\n")
                for item in items:
                    if item.strip():
                        meal_items.append({"item": item.strip(), "portion": "1 serving"})
                meals[current_meal] = meal_items
            elif "Dinner:" in section:
                current_meal = "dinner"
                meal_items = []
                items = section.replace("Dinner:", "").strip().split("\n")
                for item in items:
                    if item.strip():
                        meal_items.append({"item": item.strip(), "portion": "1 serving"})
                meals[current_meal] = meal_items
            elif "Snacks:" in section:
                current_meal = "snacks"
                meal_items = []
                items = section.replace("Snacks:", "").strip().split("\n")
                for item in items:
                    if item.strip():
                        meal_items.append({"item": item.strip(), "portion": "1 serving"})
                meals[current_meal] = meal_items

        # Estimate total nutrients (simplified)
        total_calories = 2000  # Placeholder
        total_protein = 100    # Placeholder
        total_carbs = 250     # Placeholder
        total_fat = 70       # Placeholder

        return MealPlan(
            meals=meals,
            total_calories=total_calories,
            total_protein=total_protein,
            total_carbs=total_carbs,
            total_fat=total_fat
        )

    def _parse_workout_plan_response(self, response_text: str) -> WorkoutPlan:
        # This is a simplified example - in production you'd want more robust parsing
        return WorkoutPlan(
            weekly_schedule={
                "monday": [
                    {"exercise": "Squats", "sets": "3x12"},
                    {"exercise": "Bench Press", "sets": "3x10"}
                ],
                "wednesday": [
                    {"exercise": "Deadlifts", "sets": "3x8"},
                    {"exercise": "Pull-ups", "sets": "3x8"}
                ],
                "friday": [
                    {"exercise": "Running", "duration": "30 minutes"},
                    {"exercise": "Core workout", "duration": "15 minutes"}
                ]
            },
            intensity_level="moderate",
            estimated_calories_burn=500.0
        )

    def _estimate_prep_time(self, meal_item: str) -> int:
        # Simplified example, actual implementation would require more data
        return 30

    def _calculate_difficulty(self, meal_item: str) -> str:
        # Simplified example, actual implementation would require more data
        return "Easy"

    def _identify_muscle_groups(self, exercise: str) -> List[str]:
        # Simplified example, actual implementation would require more data
        return ["Chest", "Triceps"]

    def _get_required_equipment(self, exercise: str) -> List[str]:
        # Simplified example, actual implementation would require more data
        return ["Barbell", "Bench"]

    def _calculate_exercise_difficulty(self, exercise: str) -> str:
        # Simplified example, actual implementation would require more data
        return "Moderate"

    def _get_exercise_tutorial(self, exercise: str) -> str:
        # Simplified example, actual implementation would require more data
        return "https://example.com/exercise-tutorial"
