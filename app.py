import streamlit as st
from dotenv import load_dotenv, find_dotenv
import os
import google.generativeai as Genai
from PIL import Image
load_dotenv(find_dotenv())

#page config - streamlit

st.set_page_config("page_title = 'Amit's Nutrition Monitor",page_icon = "🥑🌱🥦🍎")
Genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, image):
    model = Genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content([input, image[0]])
    return response.text

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type" : uploaded_file.type,
                "data" : bytes_data,
            }
        ]
        return image_parts
    else:
        FileNotFoundError("No image uploaded, Please try again")
    
#sidebar navigation building
st.sidebar.title("Navigation")
st.sidebar.header("Upload Section")
uploaded_file = st.sidebar.file_uploader("So what have we cooked today?", type = ["jpg","jpeg", "png","HEIF"])


st.header("Lets check the nutrition content of your meal")
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption = "I wish someone cooked food for me while i built this app",use_container_width = True)


submit = st.button("Analyse this Food")

input_prompt = """
You are an expert nutritionist analyzing the food items in the image.
Start by determining if the image contains food items. 
If the image does not contain any food items, 
clearly state "No food items detected in the image." 
and do not provide any calorie information. 
If food items are detected, 
start by naming the meal based on the image. mention a fun fact about the particular meal if possible, 
identify and list every ingredient you can find in the image, 
and then estimate the total calories for each ingredient. 
Summarize the total calories based on the identified ingredients. 
Follow the format below:

If no food items are detected:
No food items detected in the image.

If food items are detected then you must provide a markdown table for the contents below while keeping the details as below:
Meal Name: [Name of the meal]
Fun Fact : state a fun fact about the meal 

1. Ingredient 1 - estimated calories
2. Ingredient 2 - estimated calories
----
Total estimated calories: X


Finally, mention whether the food is healthy or not, 
and provide the percentage split of protein, carbs, and fats in the food item.Feel 
Also mention what part of the daily necessary vitamins , micros and macros is covered by this meal. 
Come up with suggestions on what other food item i can add with this that might be a good combination nutritionally 
Also, mention the total fiber content in the food item and any other important details.

Note: Always identify ingredients and provide an estimated calorie count, 
even if some details are uncertain.





"""


# Actions to take when the analyse food button is clicked 
if submit: 
    with st.spinner("Processing...."): 
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_response(input_prompt, image_data)
        st.success("Done!")
        #Display the subheader and the response from the AI Model
        st.subheader("Heres the food analysis")
        st.write(response)