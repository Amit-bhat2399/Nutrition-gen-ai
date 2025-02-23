import streamlit as st
import google.generativeai as Genai
from PIL import Image

# Page Configuration
st.set_page_config(page_title="Amit's Nutrition Tracker", page_icon="🥑")

# Initialize session state
if "api_key_configured" not in st.session_state:
    st.session_state.api_key_configured = False
if "daily_nutrition" not in st.session_state:
    st.session_state.daily_nutrition = {}  
if "user_goal" not in st.session_state:
    st.session_state.user_goal = None  

# Sidebar: API Key Input
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

# Sidebar: Ask for user's goal
st.sidebar.header("🎯 Your Nutrition Goal")
goal_input = st.sidebar.text_input("Enter your goal (e.g., weight loss, muscle gain, digestion, general health):")

if goal_input:
    st.session_state.user_goal = goal_input
    st.sidebar.success(f"✅ Goal Set: {goal_input}")

# Sidebar: Choose Eating Context
st.sidebar.header("🍽️ Eating Context")
eating_context = st.sidebar.selectbox("Where are you eating?", ["Eating at Home", "Eating at a Restaurant"])

# User preference for vegetarian/non-vegetarian meal
if eating_context == "Eating at Home":
    veg_preference = st.sidebar.radio("Choose your preference:", ["Vegetarian", "Non-Vegetarian"])
else:
    veg_preference_restaurant = st.sidebar.radio("Choose your preference:", ["Vegetarian", "Non-Vegetarian"])

# Function to process uploaded images
def input_image_setup(uploaded_file):
    """Converts uploaded images into a format suitable for AI processing."""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
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
        response = model.generate_content([input_text])

    return response.text

# Sidebar: Multi-Image Upload
st.sidebar.header("📸 Upload Your Meals")
uploaded_files = st.sidebar.file_uploader("Upload images of meals:", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

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

            Format:
            **Meal Name:** [Detected Meal Name]  
            **Meal Summary:** [Two-line nutritional breakdown based on goal]
            """

            with st.spinner(f"🔍 Analyzing {uploaded_file.name}..."):
                try:
                    image_data = input_image_setup(uploaded_file)
                    response = get_gemini_response(input_prompt, image_data)

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

# Handling "Eating at Home"
if eating_context == "Eating at Home":
    if "recommended_dishes" not in st.session_state:
        st.session_state.recommended_dishes = []  # Store recommended dishes
    
    def generate_dish_recommendations():
        # Get the list of meals already consumed
        consumed_meals = [meal.lower() for meal in st.session_state.daily_nutrition.keys()]

        home_suggestion_prompt = f"""
        Based on the meals consumed today:
        {''.join([f"{meal}: {summary}" for meal, summary in st.session_state.daily_nutrition.items()])}

        The user’s goal is: {st.session_state.user_goal}
        - Suggest **3 dishes** that will balance their daily nutrition.
        - Ensure all dishes align with the user's dietary preference (**{veg_preference}**).
        - DO NOT suggest dishes that have already been consumed today: {', '.join(consumed_meals)}.
        - If a dish is commonly suggested but has already been eaten, provide an alternative.
        - Keep explanations concise.

        **Response Format:**
        **Top 3 Recommended Dishes:**
        1️⃣ **[Dish Name]** - [Short reason why it fits user’s goal]
        2️⃣ **[Dish Name]** - [Short reason why it fits user’s goal]
        3️⃣ **[Dish Name]** - [Short reason why it fits user’s goal]
        """

        with st.spinner("🍳 Finding the perfect dishes..."):
            home_suggestion = get_gemini_response(home_suggestion_prompt, [])
            st.session_state.recommended_dishes = home_suggestion  # Save recommendations
    
    if st.button("🍲 Suggest 3 Dishes for Today"):
        generate_dish_recommendations()

    if st.session_state.recommended_dishes:
        st.success("✅ Here are your meal recommendations:")
        st.markdown(st.session_state.recommended_dishes)

        # Add a button to refresh suggestions
        if st.button("🔄 Generate New Suggestions"):
            generate_dish_recommendations()



if eating_context == "Eating at a Restaurant":
    st.sidebar.header("📜 Upload Restaurant Menu")
    menu_files = st.sidebar.file_uploader("Upload restaurant menu images (JPG, PNG):", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if menu_files and st.button("📋 Find Best Dishes from Menu"):
        try:
            # Display uploaded menu images
            for menu_file in menu_files:
                menu_image = Image.open(menu_file)
                st.image(menu_image, caption="📜 Uploaded Restaurant Menu", use_column_width=True)

            # Process each image into AI-friendly format
            menu_image_data = []
            for menu_file in menu_files:
                menu_image_data.append(input_image_setup(menu_file)[0])  # Extracting dict from list

            # AI prompt to analyze the menu images
            restaurant_menu_prompt = f"""
            You are a professional nutritionist helping a user pick the best dish from this restaurant menu.
            The user's goal is: {st.session_state.user_goal}
            The user prefers a **{veg_preference_restaurant}** meal.
            
            The user has consumed the following meals today:
            {''.join([f"{meal}: {summary}" for meal, summary in st.session_state.daily_nutrition.items()])}

            **Your Task:**
            - Analyze the uploaded restaurant menu images.
            - DO NOT list all menu items. Instead:
              - Summarize the user's daily nutrient intake in a **readable text table** (Calories, Protein, Vitamins).
              - Identify **3 dishes** from the menu that best fill any nutritional gaps.
              - Ensure recommendations align with the user’s goal.
              - Keep explanations concise and relevant.

            **Response Format:**
            **Current Nutrient Intake Summary:**
            ```
            | Nutrient  | Amount |
            |-----------|--------|
            | Calories  | X kcal |
            | Protein   | X g    |
            | Vitamins  | [List] |
            ```

            **Top 3 Recommended Dishes:**
            1️⃣ **[Dish Name]** - [Short reason why it fits user’s goal]
            2️⃣ **[Dish Name]** - [Short reason why it fits user’s goal]
            3️⃣ **[Dish Name]** - [Short reason why it fits user’s goal]
            """

            with st.spinner("🔍 Analyzing the restaurant menu..."):
                restaurant_suggestion = get_gemini_response(restaurant_menu_prompt, menu_image_data)
                st.success("✅ Recommended Dishes from Menu:")
                st.markdown(restaurant_suggestion)

        except Exception as e:
            st.error(f"❌ Error analyzing menu: {str(e)}")

