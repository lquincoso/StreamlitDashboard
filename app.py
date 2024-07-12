import streamlit as st
import pandas as pd
import plotly.express as px
import dask.dataframe as dd

# Load data with selected columns and a limit on rows
@st.cache_data
def load_data(nrows):
    url = "https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD"
    cols = ["LAT", "LON", "Crm Cd Desc"]  # Only necessary columns
    data = pd.read_csv(url, usecols=cols, nrows=nrows)
    return data

# Load only the first 20,000 rows for example
data = load_data(20000)

# Sidebar for user input
st.sidebar.title("Crime Data Filters")
crime_types = st.sidebar.multiselect("Select Crime Types:", options=data["Crm Cd Desc"].unique(), default=data["Crm Cd Desc"].unique())

# Filter data
filtered_data = data[data["Crm Cd Desc"].isin(crime_types)]

# Aggregate data
agg_data = filtered_data.groupby(['LAT', 'LON', 'Crm Cd Desc']).size().reset_index(name='Count')

# Create Plotly scatter mapbox with aggregated data
fig = px.scatter_mapbox(
    agg_data,
    lat="LAT",
    lon="LON",
    size="Count",
    color="Crm Cd Desc",
    hover_name="Crm Cd Desc",
    zoom=10,
    height=500
)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_traces(marker=dict(size=5))  # Smaller marker size
fig.update_layout(clickmode='event+select')  # Optimize interactivity

# Display map in Streamlit
st.title("Geographical Distribution of Crimes")
st.plotly_chart(fig, use_container_width=True)
