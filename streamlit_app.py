import streamlit as st
import pandas as pd
import joblib
import folium
from streamlit_folium import st_folium
from io import StringIO
import requests

# =================================================================================================
# PROGRAMMED AND DEVELOPED BY: Lorena A. Quincoso-Lugones                                         |
# Florida International University                                                                |
# =================================================================================================
# Streamlit Dashboard for visual display of Crime Prediction depending on the following features:
# - Area Name
# - Day of the Week
# - Hour of the Day
# - Month
# - Whether is Weekend or not
# =================================================================================================

# Function to download dataset from URL with error handling
def download_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = StringIO(response.text)
        return pd.read_csv(data)
    else:
        st.error("Failed to download the dataset.")
        return None

# URL of the dataset
url = 'https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD'

# Loading the dataset
df = download_data(url)

# Preprocessing steps to ensure required columns are available
df = df.rename(columns={
    "Crm Cd Desc": "Crime Code Descript",
    "AREA NAME": "AREA_NAME"
})

# Loading the model and feature columns (extracted from the model itself)
model = joblib.load('models/knn_model.pkl')
feature_columns = joblib.load('models/feature_columns.pkl')


# Function to prepare input data
def prepare_input_data(area_name, day_of_week, hour_of_day, month, is_weekend):
    input_data = {
        'AREA_NAME': [area_name],
        'DayOfWeek': [day_of_week],
        'HourOfDay': [hour_of_day],
        'Month': [month],
        'IsWeekend': [is_weekend]
    }
    input_df = pd.DataFrame(input_data)
    input_df = pd.get_dummies(input_df, columns=['AREA_NAME'])

    # Ensuring all necessary columns are present
    for col in feature_columns:
        if col not in input_df.columns:
            input_df[col] = 0

    return input_df


# Streamlit Interface
st.title('Crime Prediction Dashboard')

st.sidebar.header('Input Features')
area_name = st.sidebar.selectbox('Area Name', sorted(df['AREA_NAME'].unique()))
day_of_week = st.sidebar.selectbox('Day of the Week', range(7), format_func=lambda x:
['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][x])
hour_of_day = st.sidebar.slider('Hour of the Day', 0, 23, 12)
month = st.sidebar.selectbox('Month', range(1, 13))
is_weekend = st.sidebar.selectbox('Is Weekend', [0, 1], format_func=lambda x: 'Yes' if x == 1 else 'No')

# Preparing input data (received from the user)
input_data = prepare_input_data(area_name, day_of_week, hour_of_day, month, is_weekend)

# Making a prediction
prediction = model.predict(input_data)

st.write('## Prediction')
st.write(f'The predicted crime category is: **{prediction[0]}**')

if st.button('Predict'):
    st.write('Prediction:', prediction)

# Adding a map of Los Angeles in order to display target area
st.write('## Map of Los Angeles with Predicted Crime Areas')

# Defining coordinates of Los Angeles
la_coords = [34.0522, -118.2437]

# Creating a map centered on Los Angeles
m = folium.Map(location=la_coords, zoom_start=10)

# Adding coordinates for the area in order to pinpoint it as needed. Coordinate sources: Google
area_coords = {
    'Central': [34.0425, -118.2468],
    'Hollenbeck': [34.0505, -118.2117],
    'Southwest': [34.0166, -118.2971],
    'Rampart': [34.0533, -118.2760],
    'Hollywood': [34.1019, -118.3286],
    'Wilshire': [34.0595, -118.3085],
    'West LA': [34.0443, -118.4426],
    'Van Nuys': [34.1867, -118.4483],
    'Pacific': [33.9931, -118.4415],
    'Northeast': [34.1066, -118.2150],
    'Newton': [34.0106, -118.2585],
    'Harbor': [33.7903, -118.2861],
    '77th Street': [33.9454, -118.2734],
    'Foothill': [34.2727, -118.4182],
    'Devonshire': [34.2573, -118.5250],
    'Southeast': [33.9534, -118.2452],
    'Mission': [34.2723, -118.4380],
    'Olympic': [34.0496, -118.2998],
    'Topanga': [34.2279, -118.6055],
    'North Hollywood': [34.1870, -118.3863],
    'N Hollywood': [34.1867, -118.3893],
    'Valley Traffic': [34.2333, -118.4630],
    'South Traffic': [33.9720, -118.2895],
    'West Traffic': [34.0452, -118.4447],
    'Central Traffic': [34.0407, -118.2534]
}

# Adding a marker to the map
if area_name in area_coords:
    folium.Marker(location=area_coords[area_name], popup=area_name).add_to(m)
else:
    st.warning('Coordinates for the selected area are not available.')

# Displaying the map in Streamlit
st_folium(m, width=700, height=500)
