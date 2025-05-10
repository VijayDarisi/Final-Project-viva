Maps API code 

import requests
from geopy.geocoders import Nominatim

# Your Google Maps API key (replace with your actual API key)
API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY'
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# Function to fetch the user's location
def get_user_location():
    geolocator = Nominatim(user_agent="wound_assistance_app")
    location = geolocator.geocode("India")  # You can change this to get any fixed location if needed
    return location.latitude, location.longitude

# Function to fetch nearby hospitals from Google Maps API
def find_nearby_hospitals(latitude, longitude, radius=5000):
    # Define the parameters for the Google Places API
    params = {
        'location': f"{latitude},{longitude}",
        'radius': radius,  # 5 km radius
        'type': 'hospital',  # We are looking for hospitals
        'key': API_KEY
    }

    # Make the API request
    response = requests.get(PLACES_API_URL, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        hospitals = response.json().get('results', [])
        return hospitals
    else:
        return []

# Function to return hospitals and their Google Maps links
def get_hospitals_with_links():
    # Get user's location (latitude and longitude)
    latitude, longitude = get_user_location()

    # Fetch nearby hospitals
    hospitals = find_nearby_hospitals(latitude, longitude)

    # Prepare a list of hospitals with their Google Maps links
    hospital_details = []
    if hospitals:
        for hospital in hospitals:
            name = hospital.get('name')
            address = hospital.get('vicinity')
            hospital_id = hospital.get('place_id')
            map_link = f"https://www.google.com/maps/search/?q=Hospital+{name.replace(' ', '+')}&hl=en"

            # Add hospital information to the list
            hospital_details.append({
                'name': name,
                'address': address,
                'google_maps_link': map_link
            })
    
    return hospital_details

# Example of how to use the function in Streamlit
import streamlit as st

# Streamlit application layout
st.title("Nearby Hospitals Finder")
st.write("This app will show nearby hospitals based on your location.")

# Fetch hospitals and display
hospitals_info = get_hospitals_with_links()

if hospitals_info:
    st.write(f"Found {len(hospitals_info)} hospitals nearby within a 5 km radius:")
    
    for hospital in hospitals_info:
        st.markdown(f"**{hospital['name']}**")
        st.markdown(f"Address: {hospital['address']}")
        st.markdown(f"[Open in Google Maps]({hospital['google_maps_link']})")
        st.markdown("---")
else:
    st.write("No hospitals found within the specified radius.")