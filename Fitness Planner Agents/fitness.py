import streamlit as st
import pandas as pd
import numpy as np
from mesa import Agent

# Inject custom CSS for a full black background and neon theme
def apply_custom_theme():
    st.markdown("""
        <style>
            /* Full-page black background */
            html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], [data-testid="stHeader"] {
                background-color: #000000 !important;
                color: #00FFAB !important;
            }
            /* Main content alignment */
            [data-testid="stAppViewContainer"] {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 10px;
            }
            /* Styling for input boxes and buttons */
            input, select, textarea {
                background-color: #1f1f1f;
                color: #00FFAB !important;
                border: 1px solid #00FFAB;
                border-radius: 5px;
                padding: 10px;
                width: 100%;
            }
            button {
                background-color: #00FFAB !important;
                color: #000000 !important;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 16px;
                transition: 0.3s ease;
                cursor: pointer;
            }
            button:hover {
                background-color: #000000 !important;
                color: #00FFAB !important;
                border: 1px solid #00FFAB;
            }
            /* Title and headers styling */
            h1, h2, h3 {
                text-align: center;
                color: #00FFAB !important;
            }
            /* Center container for inputs */
            .stButton, .stNumberInput, .stSelectbox {
                margin: auto;
            }
            /* Results container with glowing border */
            .stContainer {
                border: 2px solid #00FFAB;
                background-color: #1f1f1f;
                border-radius: 10px;
                padding: 20px;
                margin: 20px auto;
                width: 80%;
                box-shadow: 0px 0px 10px #00FFAB;
            }
        </style>
    """, unsafe_allow_html=True)

# Apply the custom theme
apply_custom_theme()

# Placeholder data loading function
def load_placeholder_data():
    return pd.DataFrame()

# Placeholder dataset
abbrev_df = load_placeholder_data()

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

    def calculate_bmr(self):
        if self.gender == 'male':
            return 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            return 10 * self.weight + 6.25 * self.height - 5 * self.age - 161

    def calculate_tdee(self):
        activity_multiplier = {'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55, 'active': 1.725}
        return self.bmr * activity_multiplier.get(self.activity_level, 1.2)

# Streamlit interface
st.title("🌟 Personalized Diet and Workout Planner 🌟")

with st.container():
    st.header("Enter Your Details Below")
    height = st.number_input("Enter your height (cm):", value=170.0)
    weight = st.number_input("Enter your current weight (kg):", value=70.0)
    desired_weight = st.number_input("Enter your desired weight (kg):", value=65.0)
    age = st.number_input("Enter your age:", value=25)
    gender = st.selectbox("Select your gender:", ['male', 'female'])
    activity_level = st.selectbox("Select your activity level:", ['sedentary', 'light', 'moderate', 'active'])
    body_fat_percentage = st.number_input("Enter your body fat percentage:", value=15.0)
    goal = st.selectbox("Select your fitness goal:", ['bulking', 'cutting', 'maintaining'])
    dietary_preference = st.selectbox("Select your dietary preference:", ['vegetarian', 'non-vegetarian', 'omnivorous'])
    start = st.button("Start Planning")

if start:
    agent = UserAgent(1, None, height, weight, desired_weight, age, gender, activity_level, body_fat_percentage, goal, dietary_preference)
    st.subheader("📊 Results")
    st.write(f"**BMR**: {agent.bmr:.2f} kcal")
    st.write(f"**TDEE**: {agent.tdee:.2f} kcal")

    # Placeholder for diet recommendations
    st.subheader("🍽️ Diet Recommendations")
    st.write("Feature under construction...")

    # Placeholder for workout plan
    st.subheader("🏋️ Workout Plan")
    st.write("Feature under construction...")
