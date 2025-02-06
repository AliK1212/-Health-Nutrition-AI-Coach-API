from typing import List, Dict
import openai
import os
import requests
from models import MealPlan, WorkoutPlan, NutritionGoals

class HealthCoach:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.OPENFOODFACTS_URL = "https://world.openfoodfacts.org/api/v0/product/"

    def generate_meal_plan(self, input_data: dict) -> MealPlan:
        """Generate a personalized meal plan based on user preferences."""
        try:
            # Create a prompt with user preferences
            prompt = f"""Create a detailed meal plan for someone with the following characteristics:
            Age: {input_data.get('age')} years
            Weight: {input_data.get('weight')} kg
            Height: {input_data.get('height')} cm
            Goals: {', '.join(input_data.get('goals', []))}
            Dietary Restrictions: {', '.join(input_data.get('dietary_restrictions', []))}
            Activity Level: {input_data.get('activity_level')}
            Meal Preferences: {', '.join(input_data.get('meal_preferences', []))}

            Please provide a detailed meal plan with the following structure:

            Breakfast:
            [List breakfast items]

            Lunch:
            [List lunch items]

            Dinner:
            [List dinner items]

            Snacks:
            [List snack items]

            Make sure to consider any dietary restrictions and preferences.
            If Halal is specified in dietary restrictions, ensure all meals are Halal-compliant.
            """

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini-2024-07-18",
                messages=[
                    {"role": "system", "content": "You are a professional nutritionist and meal planner."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )

            # Parse the response
            meal_plan = self._parse_meal_plan_response(response.choices[0].message.content)
            return meal_plan
        except Exception as e:
            print(f"Error generating meal plan: {str(e)}")
            raise e

    def analyze_nutritional_content(self, meal_data: dict) -> dict:
        total_nutrients = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "fiber": 0
        }

        for food_item in meal_data.get("items", []):
            nutrients = self._get_food_nutrients(food_item)
            for key in total_nutrients:
                total_nutrients[key] += nutrients.get(key, 0)

        return total_nutrients

    def generate_workout_plan(self, profile_data: dict) -> WorkoutPlan:
        prompt = self._create_workout_plan_prompt(profile_data)
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are a professional fitness trainer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        return self._parse_workout_plan_response(response.choices[0].message.content)

    def get_nutrition_goals(self, profile_data: dict) -> NutritionGoals:
        return self._calculate_nutrition_goals(profile_data)

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
        return f"""Create a workout plan for a person with the following profile:
        Age: {profile['age']}
        Weight: {profile['weight']}kg
        Height: {profile['height']}cm
        Goals: {', '.join(profile['goals'])}
        Activity level: {profile['activity_level']}
        
        Generate a weekly workout plan with specific exercises, sets, reps, and rest periods.
        Include both cardio and strength training components.
        END"""

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
