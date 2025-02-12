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
            # Create a comprehensive prompt with user preferences
            prompt = f"""Generate a detailed, nutritionally balanced meal plan in JSON format for someone with the following profile:
            Age: {input_data.get('age')} years
            Weight: {input_data.get('weight')} kg
            Height: {input_data.get('height')} cm
            Goals: {', '.join(input_data.get('goals', []))}
            Dietary Restrictions: {', '.join(input_data.get('dietary_restrictions', []))}
            Activity Level: {input_data.get('activity_level')}
            Meal Preferences: {', '.join(input_data.get('meal_preferences', []))}

            The response should be a valid JSON object with the following structure:
            {
                "meals": {
                    "breakfast": [{"item": "...", "portion": "..."}],
                    "lunch": [{"item": "...", "portion": "..."}],
                    "dinner": [{"item": "...", "portion": "..."}],
                    "snacks": [{"item": "...", "portion": "..."}]
                },
                "meal_timing": {
                    "breakfast": "...",
                    "lunch": "...",
                    "dinner": "...",
                    "snacks": "..."
                },
                "hydration_guidelines": "...",
                "preparation_tips": ["...", "..."],
                "storage_instructions": ["...", "..."],
                "total_calories": 0,
                "total_protein": 0,
                "total_carbs": 0,
                "total_fat": 0,
                "total_fiber": 0
            }

            For each meal item, include:
            1. Exact portions in grams
            2. Specific ingredients and brands when relevant
            3. Alternative options considering dietary restrictions
            4. Timing based on activity level and goals
            5. Preparation and storage instructions

            The response must be a valid JSON object that can be parsed directly."""

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert nutritionist and meal planner. Generate evidence-based meal plans in valid JSON format only. Do not include any explanatory text outside the JSON structure."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" },
                max_tokens=4000,
                temperature=0.7,
                timeout=30
            )

            # Parse the response into a structured format
            try:
                meal_plan_data = response.choices[0].message.content
                if not isinstance(meal_plan_data, dict):
                    import json
                    meal_plan_data = json.loads(meal_plan_data)
                
                meal_plan = MealPlan(
                    meals=meal_plan_data["meals"],
                    meal_timing=meal_plan_data["meal_timing"],
                    hydration_guidelines=meal_plan_data["hydration_guidelines"],
                    preparation_tips=meal_plan_data["preparation_tips"],
                    storage_instructions=meal_plan_data["storage_instructions"],
                    total_calories=meal_plan_data["total_calories"],
                    total_protein=meal_plan_data["total_protein"],
                    total_carbs=meal_plan_data["total_carbs"],
                    total_fat=meal_plan_data["total_fat"],
                    total_fiber=meal_plan_data["total_fiber"]
                )
                
                # Enhance with nutritional analysis
                for meal_type, meals in meal_plan.meals.items():
                    for meal in meals:
                        nutrients = self._get_food_nutrients(meal["item"])
                        meal["nutrients"] = nutrients
                        meal["preparation_time"] = self._estimate_prep_time(meal["item"])
                        meal["difficulty_level"] = self._calculate_difficulty(meal["item"])
                        
                return meal_plan

            except Exception as e:
                print(f"Error parsing meal plan response: {str(e)}")
                raise ValueError("Failed to parse the meal plan response from the AI model")

        except Exception as e:
            print(f"Error generating meal plan: {str(e)}")
            raise

    def generate_workout_plan(self, profile_data: dict) -> WorkoutPlan:
        """Generate a comprehensive workout plan based on user profile."""
        try:
            prompt = f"""Generate a detailed workout plan in JSON format for someone with the following profile:
            Age: {profile_data.get('age')} years
            Weight: {profile_data.get('weight')} kg
            Height: {profile_data.get('height')} cm
            Goals: {', '.join(profile_data.get('goals', []))}
            Activity Level: {profile_data.get('activity_level')}

            The response should be a valid JSON object with the following structure:
            {
                "weekly_schedule": {
                    "monday": [{"exercise": "...", "sets": "...", "duration": "..."}],
                    "tuesday": [...],
                    "wednesday": [...],
                    "thursday": [...],
                    "friday": [...],
                    "saturday": [...],
                    "sunday": [...]
                },
                "intensity_level": "...",
                "estimated_calories_burn": 0,
                "warm_up": ["...", "..."],
                "cool_down": ["...", "..."],
                "safety_precautions": ["...", "..."],
                "progression_tips": ["...", "..."]
            }

            Include for each exercise:
            1. Proper form descriptions
            2. Sets, reps, and rest periods
            3. Alternative movements
            4. Equipment needed
            5. Target heart rate zones
            6. Modifications for different fitness levels

            The response must be a valid JSON object that can be parsed directly."""

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert fitness trainer. Generate evidence-based workout plans in valid JSON format only. Do not include any explanatory text outside the JSON structure."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" },
                max_tokens=4000,
                temperature=0.7,
                timeout=30
            )

            try:
                workout_data = response.choices[0].message.content
                if not isinstance(workout_data, dict):
                    import json
                    workout_data = json.loads(workout_data)
                
                workout_plan = WorkoutPlan(
                    weekly_schedule=workout_data["weekly_schedule"],
                    intensity_level=workout_data["intensity_level"],
                    estimated_calories_burn=workout_data["estimated_calories_burn"],
                    warm_up=workout_data.get("warm_up", []),
                    cool_down=workout_data.get("cool_down", []),
                    safety_precautions=workout_data.get("safety_precautions", []),
                    progression_tips=workout_data.get("progression_tips", [])
                )
                
                return workout_plan

            except Exception as e:
                print(f"Error parsing workout plan response: {str(e)}")
                raise ValueError("Failed to parse the workout plan response from the AI model")

        except Exception as e:
            print(f"Error generating workout plan: {str(e)}")
            raise

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
