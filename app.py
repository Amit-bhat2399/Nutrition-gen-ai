import streamlit as st
import google.generativeai as Genai
from PIL import Image

# Page configuration
st.set_page_config(page_title="Amit's Nutrition Monitor", page_icon="🥑🌱🥦🍎")

# Ask for API key at the beginning
if "GOOGLE_API_KEY" not in st.session_state:
    st.session_state["GOOGLE_API_KEY"] = st.text_input("Enter your Google API Key:", type="password")

# Ensure the API key is entered before proceeding
if not st.session_state["GOOGLE_API_KEY"]:
    st.warning("Please enter your API key to proceed.")
    st.stop()

# Configure Gemini API
Genai.configure(api_key=st.session_state["GOOGLE_API_KEY"])

# Function to get response from Gemini API
def get_gemini_response(input, image):
    model = Genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content([input, image[0]])
    return response.text

# Function to process uploaded image
def input_image_setup(uploaded_file):
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
        raise FileNotFoundError("No image uploaded, Please try again.")

# Sidebar navigation
st.sidebar.title("Navigation")
st.sidebar.header("Upload Section")
uploaded_file = st.sidebar.file_uploader("So what have we cooked today?", type=["jpg", "jpeg", "png", "HEIF"])

# Main section
st.header("Let's check the nutrition content of your meal")
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="I wish someone cooked food for me while I built this app", use_container_width=True)

submit = st.button("Analyze this Food")

input_prompt = """
You are an expert nutritionist analyzing the food items in the image.
Start by determining if the image contains food items. 
If the image does not contain any food items, 
clearly state "No food items detected in the image." 
and do not provide any calorie information. 
If food items are detected, 
start by naming the meal based on the image. Mention a fun fact about the meal if possible, 
identify and list every ingredient you can find in the image, 
and then estimate the total calories for each ingredient. 
Summarize the total calories based on the identified ingredients. 
Follow the format below:

If no food items are detected:
No food items detected in the image.

If food items are detected, provide a markdown table with the details below:
Meal Name: [Name of the meal]
Fun Fact: [A fun fact about the meal]

1. Ingredient 1 - estimated calories
2. Ingredient 2 - estimated calories
----
Total estimated calories: X

Finally, mention whether the food is healthy or not, 
and provide the percentage split of protein, carbs, and fats in the food item. 
Also, mention what part of the daily necessary vitamins, micros, and macros is covered by this meal. 
Suggest an additional food item that would be a good nutritional combination with this meal.
Also, mention the total fiber content in the food item and any other important details.

Note: Always identify ingredients and provide an estimated calorie count, 
even if some details are uncertain.
"""

# Actions to take when the analyze food button is clicked
if submit:
    with st.spinner("Processing..."):
        try:
            image_data = input_image_setup(uploaded_file)
            response = get_gemini_response(input_prompt, image_data)
            st.success("Done!")
            st.subheader("Here's the food analysis")
            st.write(response)
        except Exception as e:
            st.error(f"Error: {e}")
