import streamlit as st 
import requests
import folium 
from streamlit_folium import st_folium
from datetime import datetime

# How to run? 
# type in terminal: streamlit run app.py (make sure you are in the app dir)
st.set_page_config(
    layout="centered",
    page_title="Car price predictor",
    page_icon="🚗")

@st.cache_data
def get_geojson():
    """
    Downloads a map of Poland"
    """
    url = "https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-min.geojson"
    return requests.get(url).json()

# Welcome mess
st.header("Check the price of a car", anchor=False, text_alignment="left",)
welcome_text = "Thanks to our app, you can easily predict the price of any car based on its most essential data, such as production year, mileage, engine power, and more."
st.text(welcome_text)
st.divider()

# Year & Mileage
st.subheader("Year & Mileage", anchor=False)
prod_col, mileage_col = st.columns(2)
with prod_col:
    production_year = st.number_input(
        "Insert the year of production: ", 
        min_value=1950, 
        max_value=int(datetime.today().strftime("%Y")), 
        value=2010, 
        step=1)

with mileage_col:
    mileage = st.number_input(
        "What's the mileage: ", 
        min_value=0, 
        max_value = 10**6, 
        value=0, 
        step=1000)

# Fuel type (diesel / petrol etc)
st.divider()
st.subheader("Fuel type", anchor=False)
petrol = st.radio(
    "Select fuel type",
    ["Petrol", "Diesel", "LPG", "Hybrid", "Electric"],
    horizontal=True
)

# Car type & model
st.divider()
st.subheader("Brand & Model")
car_data = {
    "Audi": ["A3", "A4", "A6", "Q5"],
    "BMW": ["3 Series", "5 Series", "X3", "X5"],
    "Citroën": ["C3", "C4", "Berlingo"],
    "Volkswagen": ["Golf", "Passat", "Tiguan"]
}
brand_col, model_col = st.columns(2)

with brand_col:
    selected_brand = st.selectbox("Car Brand", options=sorted(car_data.keys()))

with model_col:
    models_for_brand = car_data[selected_brand]
    selected_model = st.selectbox("Car Model", options=sorted(models_for_brand))


# Addons selection
st.divider()
st.subheader("Addons", anchor = False)
addons = st.multiselect(label = "What does your car have?", options=["A/C", "ABS", "Electric Windows", "Central locking", "Radio", "Airbags", "Power steering"])
st.divider()


# Gearbox & seller 
gearbox_col, seller_col = st.columns(2)
with gearbox_col:
    st.subheader("Gearbox", anchor=False)
    gearbox = st.pills("Select one:", options=["Manual", "Automatic"])

with seller_col:
    st.subheader("Seller information", anchor=False)
    seller_type = st.pills("Seller type:", ["Private person", "Dealer / Firm"])


st.divider()

# Imported & Accident 
imported_col, accident_col = st.columns(2)

with imported_col:
    st.subheader("Imported?", anchor=False)
    imported = st.toggle("Is your car imported from abroad?")
    
    if imported:
        st.write("Your answer: **Yes**")
    else:
        st.write("Your answer: **No**")

with accident_col:
    st.subheader("An accident?", anchor=False)
    accident = st.toggle("Had an accident?")
    
    if accident:
        st.write("Your answer: **Yes**")
    else:
        st.write("Your answer: **No**")

# Body type
st.divider()
st.subheader("Body type", anchor = False)
body_type = st.selectbox(label = "Select body type:",options=["Sedan", "Hatchback", "SUV", "Coupe", "Station wagon", "Compact"])



# Colors
st.divider()
st.subheader("Color")
color_list = [
    "Black", "White", "Silver", "Gray", 
    "Blue", "Red", "Other"
]
chosen_color = st.selectbox("What is the color of your car:", color_list)

# Engine info 
st.divider()
st.subheader("Enigine information", anchor = False)
col1, col2 = st.columns(2)


with col1:
    engine_capacity = st.slider(
        "Engine Capacity (cm³)", 
        min_value=800, 
        max_value=6000, 
        value=1600, 
        step=100
    )

with col2:
    engine_power = st.slider(
        "Engine Power (HP)", 
        min_value=50, 
        max_value=800, 
        value=150, 
        step=5
    )

# Location
st.divider()
st.subheader("Location")
st.text("Car prices can vary significantly by region. Please select the correct voivodeship.")

# Map logic
geo_data = get_geojson()
m = folium.Map(location=[52.0693, 19.4803], zoom_start=6, tiles="cartodbpositron")
folium.GeoJson(
    geo_data,
    style_function=lambda feature: {
        "fillColor": "#3186cc", 
        "color": "black",       
        "weight": 1,
        "fillOpacity": 0.3,
    },
    highlight_function=lambda feature: {
        "fillColor": "#ff4b4b",
        "fillOpacity": 0.7,
    },

    tooltip=folium.features.GeoJsonTooltip(fields=['nazwa'], aliases=['voivodeship:'])
).add_to(m)

map_data = st_folium(m, width=700, height=500, returned_objects=["last_active_drawing"])
if map_data and map_data.get("last_active_drawing"):
    wybrane_woj = map_data["last_active_drawing"]["properties"]["nazwa"]
    st.success(f"You have chosen: **{wybrane_woj.capitalize()}**")
else:
    st.info("Click on the map in order to chose the voivodeship")   
st.divider()