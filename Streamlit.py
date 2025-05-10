from dotenv import load_dotenv
import os
import streamlit as st
from PIL import Image
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()  # Load environment variables from .env file

# Configure the Google Generative AI with the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(prompt, image=None, user_input=None):
    """
    Function to generate a response using the Gemini model.
    """
    model = genai.GenerativeModel('gemini-2.0-flash')
    inputs = [prompt]
    if user_input:
        inputs.append(user_input)
    if image:
        inputs.append(image)
    response = model.generate_content(inputs)
    return response.text

def input_image_setup(uploaded_file):
    """
    Function to prepare image data for model input.
    """
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        return image
    else:
        raise FileNotFoundError("No file uploaded")

# Initialize Streamlit app
st.set_page_config(page_title="First aid")
st.header("First Aid Recommendation System")

# Input method selection
input_method = st.radio("Choose the type of input:", ('Text', 'Image'))

if input_method == 'Text':
    user_text = st.text_input("Describe your injury: ", key="user_text")
else:
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Display uploaded image if applicable
if input_method == 'Image' and uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_container_width=True)

# Button to get the answer
submit = st.button("Press button to get your ANSWER")

# Prompt for the Gemini model
gemini_prompt = """
You are an expert in understanding types of wounds from images.
You will receive wound images as input.
Classify the wound as exactly one of the following categories: 'Abrasions', 'Bruises', 'Burns', 'Cut', or 'Normal'.
Only respond with one of these five labels.
"""


# If the submit button is clicked
if submit:
    try:
        if input_method == 'Text':
            # Directly generate first aid steps from text input
            first_aid_prompt = """
            Act as a first aid specialist. Provide the user with first aid steps in 100 words (related to human body).
            """
            location = "Bharathi Salai, Ramapuram, Chennai, TamilNadu, India"

            llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", api_key=os.getenv("GOOGLE_API_KEY"), temperature=0.1)
            first_aid_response = llm.invoke([first_aid_prompt, f"Injury description: {user_text}"])
            st.subheader("First Aid Recommendations")
            st.write(first_aid_response.content)
            st.subheader("Nearby Hospitals:")
            st.write(f"Current location: {location}")
            st.write("1. MIOT Hospital - 2.1 km \n2. Apollo Hospitals - 3.4 km \n\n3. St Thomas Hospital - 3.6 km")


        else:
            # Determine injury type from image and then provide first aid recommendations
            image = input_image_setup(uploaded_file)
            injury_type_response = get_gemini_response(gemini_prompt, image=image)
            st.subheader("Type of injury is")
            st.write(injury_type_response)
            location = "Bharathi Salai, Ramapuram, Chennai, TamilNadu, India"
            first_aid_prompt = """
            Act as a first aid specialist. Provide the user with first aid steps in 100 words (related to human body).
            """
            llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", api_key=os.getenv("GOOGLE_API_KEY"), temperature=0.1)
            first_aid_response = llm.invoke([first_aid_prompt, f"Injury type: {injury_type_response}"])
            st.subheader("First Aid Recommendations")
            st.write(first_aid_response.content)
            st.subheader("Nearby Hospitals:")
            st.write(f"Current location: {location}")
            st.write("1. MIOT Hospital - 2.1 km \n2. Apollo Hospitals - 3.4 km \n\n3. St Thomas Hospital - 3.6 km")
    except Exception as e:
        st.error(f"An error occurred: {e}")
