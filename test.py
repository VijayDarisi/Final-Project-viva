from dotenv import load_dotenv
import os
import streamlit as st
from PIL import Image
import requests
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get user location based on IP
def get_current_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        loc = data.get("loc", "")  # format: "latitude,longitude"
        if loc:
            lat, lon = loc.split(",")
            return float(lat), float(lon), data.get("city", ""), data.get("region", ""), data.get("country", "")
    except Exception as e:
        print("Location fetch error:", e)
    return None, None, None, None, None

# Gemini API Call
def get_gemini_response(prompt, image=None, user_input=None):
    model = genai.GenerativeModel('gemini-2.0-flash')
    inputs = [prompt]
    if user_input:
        inputs.append(user_input)
    if image:
        inputs.append(image)
    response = model.generate_content(inputs)
    return response.text

# Image processing
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        return image
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit app
st.set_page_config(page_title="First Aid")
st.header("First Aid Recommendation System")

# Input selection
input_method = st.radio("Choose the type of input:", ('Text', 'Image'))

if input_method == 'Text':
    user_text = st.text_input("Describe your injury: ", key="user_text")
else:
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_container_width=True)

# Button
submit = st.button("Press button to get your ANSWER")

# Injury classification prompt
gemini_prompt = """
You are an expert in understanding types of wounds from images.
You will receive wound images as input.
Classify the wound as exactly one of the following categories: 'Abrasions', 'Bruises', 'Burns', 'Cut', or 'Normal'.
Only respond with one of these five labels.
"""

# On submit
if submit:
    try:
        # Get user's current location
        lat, lon, city, region, country = get_current_location()
        if not lat or not lon:
            st.error("Could not determine your current location.")
        else:
            location_coords = f"Latitude {lat}, Longitude {lon}"
            location_description = f"{city}, {region}, {country}"

            if input_method == 'Text':
                first_aid_prompt = """
                Act as a first aid specialist. Provide the user with first aid steps in 100 words (related to human body).
                """
                llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite",
                                             api_key=os.getenv("GOOGLE_API_KEY"),
                                             temperature=0.1)
                first_aid_response = llm.invoke([first_aid_prompt, f"Injury description: {user_text}"])

                st.subheader("First Aid Recommendations")
                st.write(first_aid_response.content)

            else:
                image = input_image_setup(uploaded_file)
                injury_type_response = get_gemini_response(gemini_prompt, image=image)
                st.subheader("Type of injury is")
                st.success(injury_type_response)

                first_aid_prompt = """
                Act as a first aid specialist. Provide the user with first aid steps in 100 words (related to human body).
                """
                llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite",
                                             api_key=os.getenv("GOOGLE_API_KEY"),
                                             temperature=0.1)
                first_aid_response = llm.invoke([first_aid_prompt, f"Injury type: {injury_type_response}"])

                st.subheader("First Aid Recommendations")
                st.write(first_aid_response.content)

            # Ask Gemini for nearby hospitals based on actual location
            hospital_prompt = f"""
            You are a local guide. A user is at this location: {location_coords} ({location_description}).
            List the 3 nearest well-known hospitals. Include name and approximate distance.
            Keep the list short and clear.
            """
            hospital_response = get_gemini_response(hospital_prompt)

            st.subheader("Nearby Hospitals:")
            st.write(f"Location: {location_coords} ({location_description})")
            st.write(hospital_response)

    except Exception as e:
        st.error(f"An error occurred: {e}")
