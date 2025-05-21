import streamlit as st
import pandas as pd
import numpy as np
from mesa import Agent

# Step 1: Load and Preprocess Datasets
def load_and_clean_abbrev_data(path):
    abbrev_df = pd.read_csv(path)
    abbrev_df['Energ_Kcal'] = pd.to_numeric(abbrev_df['Energ_Kcal'], errors='coerce')
    abbrev_df['Protein_(g)'] = pd.to_numeric(abbrev_df['Protein_(g)'], errors='coerce')
    abbrev_df['Carbohydrt_(g)'] = pd.to_numeric(abbrev_df['Carbohydrt_(g)'], errors='coerce')
    abbrev_df['Water_(g)'] = pd.to_numeric(abbrev_df['Water_(g)'], errors='coerce')
    abbrev_df.dropna(subset=['Shrt_Desc', 'Energ_Kcal', 'Protein_(g)', 'Carbohydrt_(g)', 'Water_(g)'], inplace=True)
    return abbrev_df

def load_and_clean_indian_cuisine_data(path):
    indian_cuisines_df = pd.read_csv(path)
    indian_cuisines_df['calories'] = indian_cuisines_df['calories'].str.replace(' kcal', '').astype(float)
    indian_cuisines_df['proteins'] = indian_cuisines_df['proteins'].str.replace('g', '').astype(float)
    indian_cuisines_df['carbohydrates'] = indian_cuisines_df['carbohydrates'].str.replace('g', '').astype(float)
    indian_cuisines_df['fats'] = indian_cuisines_df['fats'].str.replace('g', '').astype(float)
    indian_cuisines_df.dropna(subset=['cuisine', 'calories', 'proteins', 'carbohydrates'], inplace=True)
    return indian_cuisines_df

def load_and_clean_gym_data(path):
    gym_data = pd.read_csv(path)
    gym_data = gym_data[['Title', 'Type', 'BodyPart', 'Equipment', 'Level']].dropna()
    return gym_data

# Load datasets
abbrev_df = load_and_clean_abbrev_data('ABBREV.csv')
indian_cuisines_df = load_and_clean_indian_cuisine_data('indian_cuisines.csv')
gym_data = load_and_clean_gym_data('megaGymDataset.csv')

# Step 2: Define Mesa Agent
class UserAgent(Agent):
    def __init__(self, unique_id, model, height, weight, desired_weight, age, gender, activity_level, body_fat_percentage, goal, dietary_preference):
        if model is not None:
            super().__init__(unique_id, model)
        self.height = height
        self.weight = weight
        self.desired_weight = desired_weight
        self.age = age
        self.gender = gender
        self.activity_level = activity_level
        self.body_fat_percentage = body_fat_percentage
        self.goal = goal
        self.dietary_preference = dietary_preference
        self.bmr = self.calculate_bmr()
        self.tdee = self.calculate_tdee()
        self.lean_body_mass = self.calculate_lean_body_mass()
        self.protein_intake = self.calculate_protein_intake()

    def calculate_bmr(self):
        if self.gender == 'male':
            return 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            return 10 * self.weight + 6.25 * self.height - 5 * self.age - 161

    def calculate_tdee(self):
        activity_multiplier = {'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55, 'active': 1.725}
        return self.bmr * activity_multiplier.get(self.activity_level, 1.2)

    def calculate_lean_body_mass(self):
        return self.weight * (1 - (self.body_fat_percentage / 100))

    def calculate_protein_intake(self):
        if self.goal == 'bulking':
            return self.lean_body_mass * 2.2
        elif self.goal == 'cutting':
            return self.lean_body_mass * 2.7
        else:
            return self.lean_body_mass * 1.8

    def filter_food_by_dietary_preference(self, df):
        """Filter food items based on dietary preference."""
        if self.dietary_preference == 'vegetarian':
            return df[~df['Shrt_Desc'].str.contains('BEEF|CHICKEN|TURKEY|PORK|MUTTON|FISH|EGG|PRAWN', case=False)]
        elif self.dietary_preference == 'non-vegetarian':
            return df[df['Shrt_Desc'].str.contains('BEEF|CHICKEN|TURKEY|PORK|MUTTON|FISH|EGG|PRAWN', case=False)]
        elif self.dietary_preference == 'omnivorous':
            return df[df['Shrt_Desc'].str.contains('CHICKEN|MUTTON|FISH|PRAWN|EGG', case=False)]
        return df

    def recommend_diet(self):
        """Recommend diet dynamically based on user profile."""
        recommendations = []
        # Filter foods based on fitness goal
        if self.goal == 'bulking':
            filtered_abbrev = abbrev_df[abbrev_df['Energ_Kcal'] > self.tdee * 0.2]
        elif self.goal == 'cutting':
            filtered_abbrev = abbrev_df[abbrev_df['Energ_Kcal'] < self.tdee * 0.2]
        else:  # maintaining
            filtered_abbrev = abbrev_df[abbrev_df['Energ_Kcal'] <= self.tdee]

        # Apply dietary preference
        filtered_abbrev = self.filter_food_by_dietary_preference(filtered_abbrev)

        # Filter out rows with 0.0 values for Protein or Carbs
        filtered_abbrev = filtered_abbrev[
            (filtered_abbrev['Protein_(g)'] > 0) & 
            (filtered_abbrev['Carbohydrt_(g)'] > 0)
        ]

        # Shuffle the results for dynamic output
        shuffled_data = filtered_abbrev.sample(frac=1).head(5)

        # Generate recommendations
        for _, row in shuffled_data.iterrows():
            recommendations.append(
                f"Food: {row['Shrt_Desc']}, Calories: {row['Energ_Kcal']} kcal, Protein: {row['Protein_(g)']} g, "
                f"Carbs: {row['Carbohydrt_(g)']} g, Water: {row['Water_(g)']} g"
            )

        return recommendations

    def recommend_workout_plan(self):
        """Generate a workout plan."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        workout_plan = {}
        for day in days:
            workouts = gym_data.sample(5)
            workout_plan[day] = workouts[['Title', 'Type', 'BodyPart', 'Equipment', 'Level']].to_dict(orient='records')
        return workout_plan

# Step 3: Streamlit Interface
st.title("Personalized Diet and Workout Planner")

# User Inputs
with st.sidebar:
    st.header("User Inputs")
    height = st.number_input("Enter your height (cm):", value=170.0)
    weight = st.number_input("Enter your current weight (kg):", value=70.0)
    desired_weight = st.number_input("Enter your desired weight (kg):", value=65.0)
    age = st.number_input("Enter your age:", value=25)
    gender = st.selectbox("Select your gender:", ['male', 'female'])
    activity_level = st.selectbox("Select your activity level:", ['sedentary', 'light', 'moderate', 'active'])
    body_fat_percentage = st.number_input("Enter your body fat percentage:", value=15.0)
    goal = st.selectbox("Select your fitness goal:", ['bulking', 'cutting', 'maintaining'])
    dietary_preference = st.selectbox("Select your dietary preference:", ['vegetarian', 'non-vegetarian', 'omnivorous'])
    start = st.button("Start")

if start:
    # Create an agent
    agent = UserAgent(1, None, height, weight, desired_weight, age, gender, activity_level, body_fat_percentage, goal, dietary_preference)

    # Display Results
    st.subheader("Results")
    st.write(f"**BMR**: {agent.bmr:.2f} kcal")
    st.write(f"**TDEE**: {agent.tdee:.2f} kcal")
    st.write(f"**Protein Intake**: {agent.protein_intake:.2f} g")

    # Diet Recommendations
    st.subheader("Diet Recommendations")
    diet_recommendations = agent.recommend_diet()
    for rec in diet_recommendations:
        st.write(rec)

    # Workout Plan
    st.subheader("Weekly Workout Plan")
    workout_plan = agent.recommend_workout_plan()
    for day, exercises in workout_plan.items():
        st.write(f"**{day}:**")
        for exercise in exercises:
            st.write(f"- {exercise['Title']} | {exercise['BodyPart']} | {exercise['Type']} | {exercise['Equipment']} | {exercise['Level']}")

