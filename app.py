import streamlit as st
import google.generativeai as Genai
from PIL import Image

# Page Configuration
st.set_page_config(page_title="Amit's Nutrition Tracker", page_icon="🥑")

# Initialize session state
if "api_key_configured" not in st.session_state:
    st.session_state.api_key_configured = False
if "daily_nutrition" not in st.session_state:
    st.session_state.daily_nutrition = {}  # Dictionary to prevent duplicate meals
if "user_goal" not in st.session_state:
    st.session_state.user_goal = None  # Store user goal

# API Key Input in Sidebar
with st.sidebar:
    st.title("🔧 Configuration")
    api_key = st.text_input("Enter your Google API Key:", type="password")

    if api_key:
        try:
            Genai.configure(api_key=api_key)
            st.session_state.api_key_configured = True
            st.success("✅ API key configured successfully!")
        except Exception as e:
            st.error(f"⚠️ Error configuring API key: {str(e)}")
            st.session_state.api_key_configured = False

# Ask for user's goal
st.sidebar.header("🎯 Your Nutrition Goal")
goal_input = st.sidebar.text_input(
    "Enter your goal (e.g., weight loss, muscle gain, better digestion, general health):"
)

if goal_input:
    st.session_state.user_goal = goal_input
    st.sidebar.success(f"✅ Goal Set: {goal_input}")

# Function to process uploaded images
def input_image_setup(uploaded_file):
    """Converts uploaded images into a format suitable for AI processing."""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data,
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("⚠️ No image uploaded, Please try again.")

# Function to get response from AI model
def get_gemini_response(input_text, image_data=None):
    """Sends input prompt and image (if available) to Gemini AI and returns the response."""
    model = Genai.GenerativeModel("gemini-2.0-flash")

    if image_data and len(image_data) > 0:
        response = model.generate_content([input_text, image_data[0]])
    else:
        response = model.generate_content([input_text])  # No image data in case of summary

    return response.text

# Sidebar: Multi-Image Upload
st.sidebar.header("📸 Upload Section")
uploaded_files = st.sidebar.file_uploader("Upload today's meals:", type=["jpg", "jpeg", "png", "HEIF"], accept_multiple_files=True)

# Main Page
st.title("🍽️ Daily Nutrition Tracker")
st.header("Analyze Your Daily Meals & Get Suggestions")

if not st.session_state.api_key_configured:
    st.warning("⚠️ Please configure your Google API key in the sidebar to proceed.")
elif not st.session_state.user_goal:
    st.warning("⚠️ Please enter your goal in the sidebar to proceed.")
else:
    if uploaded_files:
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"📷 Meal Image: {uploaded_file.name}", use_container_width=True)

            input_prompt = f"""
            You are an expert nutritionist analyzing the food items in the image.
            The user's goal is: {st.session_state.user_goal}
            - Determine if the image contains food items. 
            - If no food is detected, respond: "No food items detected."
            - If food is detected:
              - Name the meal and list all identified ingredients.
              - Estimate total calories per ingredient and total meal calories.
              - Provide a **two-line summary** of the meal's nutritional benefits based on their goal.
              - Return only the **meal name** and **its two-line summary**.

            Format:
            **Meal Name:** [Detected Meal Name]  
            **Meal Summary:** [Two-line nutritional breakdown based on goal]
            """

            with st.spinner(f"🔍 Analyzing {uploaded_file.name}..."):
                try:
                    image_data = input_image_setup(uploaded_file)
                    response = get_gemini_response(input_prompt, image_data)

                    # Extract meal name and summary
                    if "**Meal Name:**" in response and "**Meal Summary:**" in response:
                        meal_name = response.split("**Meal Name:**")[1].split("**Meal Summary:**")[0].strip()
                        meal_summary = response.split("**Meal Summary:**")[1].strip()

                        if meal_name not in st.session_state.daily_nutrition:
                            st.session_state.daily_nutrition[meal_name] = meal_summary

                        st.success("✅ Analysis Complete!")
                        st.subheader(f"🍛 {meal_name}")
                        st.write(meal_summary)

                except Exception as e:
                    st.error(f"❌ Error analyzing {uploaded_file.name}: {str(e)}")

    else:
        st.info("📌 Upload images of your meals to analyze.")

    # Button to generate daily summary
    if st.button("📊 Generate Daily Nutrition Summary"):
        if not st.session_state.daily_nutrition:
            st.warning("⚠️ No meal data found. Please upload images first.")
        else:
            st.subheader("📝 **Daily Nutrition Summary**")

            # Generate short summary of total intake
            nutrition_summary_prompt = f"""
            You are a nutrition expert reviewing a person's daily meals.
            The user's goal is: {st.session_state.user_goal}
            Based on the following unique meal breakdowns, generate:
            - A **two-line summary** of total calories, macronutrients, and key vitamins/minerals obtained.

            Meals consumed:
            {''.join([f"{meal}: {summary}" for meal, summary in st.session_state.daily_nutrition.items()])}
            """

            with st.spinner("🔄 Summarizing your nutrition..."):
                try:
                    nutrition_summary = get_gemini_response(nutrition_summary_prompt, [])
                    st.success("✅ Summary Ready!")
                    st.write(nutrition_summary)
                except Exception as e:
                    st.error(f"❌ Error generating summary: {str(e)}")

            # Generate final recommendation using analyzed meals
            final_recommendation_prompt = f"""
            Based on the unique meals consumed today:
            The user's goal is: {st.session_state.user_goal}
            -You are an expert dietician
            - Identify missing nutrients relevant to their goal.
            - Suggest **only two short** food recommendation to balance nutrition.

            Meals consumed:
            {''.join([f"{meal}: {summary}" for meal, summary in st.session_state.daily_nutrition.items()])}
            """

            with st.spinner("🔄 Checking what's missing..."):
                try:
                    missing_nutrients = get_gemini_response(final_recommendation_prompt, [])
                    st.success("✅ Final Recommendation Ready!")
                    st.write(missing_nutrients)
                except Exception as e:
                    st.error(f"❌ Error generating recommendation: {str(e)}")

            # Gut Health Improvement using analyzed meals
            gut_health_prompt = f"""
            You are an expert in gut health.
            The user's goal is: {st.session_state.user_goal}
            Based on the unique meals consumed today:
            - Suggest **only one** gut health improvement tip based on what was eaten.
            After that you are a ayurvedic expert. i want you to give me **only two** ayurvedic tips to improve this user's goal that is: {st.session_state.user_goal}
            - Keep it short and practical.

            Meals consumed:
            {''.join([f"{meal}: {summary}" for meal, summary in st.session_state.daily_nutrition.items()])}
            """

            with st.spinner("🔄 Generating gut health tip..."):
                try:
                    gut_health_tip = get_gemini_response(gut_health_prompt, [])
                    st.success("✅ Gut Health Tip Ready!")
                    st.write(gut_health_tip)
                except Exception as e:
                    st.error(f"❌ Error generating gut health tip: {str(e)}")

            # Clear daily data after summary
            st.session_state.daily_nutrition.clear()
