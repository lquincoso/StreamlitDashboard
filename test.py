import streamlit as st
import pandas as pd
import os
import altair as alt
import matplotlib.pyplot as plt
import plotly.express as px


#################################################################################
#NOTES: 
#df = varaiable where the data from the csv file is stored and later manipulated by pandas
#ff1 in CSS styling can be changed for different fonts. As of right now Im not using it

# Page Configuration
st.set_page_config(
    page_title="L.A. Crime Data",
    page_icon=":foggy:",                # Kinda looks like the tall part of a bridge idk
    layout="wide",                      # Side bar space
    initial_sidebar_state="expanded"    # Side bar starting position
)
#################################################################################


#################################################################################
# CSS for background
pg_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='250' height='30' viewBox='0 0 1000 120'%3E%3Cg fill='none' stroke='%230E0A22' stroke-width='10' %3E%3Cpath d='M-500 75c0 0 125-30 250-30S0 75 0 75s125 30 250 30s250-30 250-30s125-30 250-30s250 30 250 30s125 30 250 30s250-30 250-30'/%3E%3Cpath d='M-500 45c0 0 125-30 250-30S0 45 0 45s125 30 250 30s250-30 250-30s125-30 250-30s250 30 250 30s125 30 250 30s250-30 250-30'/%3E%3Cpath d='M-500 105c0 0 125-30 250-30S0 105 0 105s125 30 250 30s250-30 250-30s125-30 250-30s250 30 250 30s125 30 250 30s250-30 250-30'/%3E%3Cpath d='M-500 15c0 0 125-30 250-30S0 15 0 15s125 30 250 30s250-30 250-30s125-30 250-30s250 30 250 30s125 30 250 30s250-30 250-30'/%3E%3Cpath d='M-500-15c0 0 125-30 250-30S0-15 0-15s125 30 250 30s250-30 250-30s125-30 250-30s250 30 250 30s125 30 250 30s250-30 250-30'/%3E%3Cpath d='M-500 135c0 0 125-30 250-30S0 135 0 135s125 30 250 30s250-30 250-30s125-30 250-30s250 30 250 30s125 30 250 30s250-30 250-30'/%3E%3C/g%3E%3C/svg%3E");
}

[data-testid="stHeader"]{
background-color: rgba(0, 0, 0, 0);
}

</style>
"""
st.markdown(pg_bg_img, unsafe_allow_html= True)


# CSS for centering elements and
# 2.5 sec fade in animation
# As of right now is only being used in the headers.
st.markdown(
    """
    <style>
    .centered {
        text-align: center;
    }
    .block-container {
        padding-top: 1rem;
    }
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    .animated-title {
        animation: fadeIn 2.5s ease-in-out;
    }
    .ff1 {
    font-family: "Times New Roman", Times, serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)
#################################################################################


# Put title up in the page
st.markdown("<h1 class='centered animated-title'>Los Angeles Crime Data Dashboard</h1>", unsafe_allow_html=True)

#######################
# 3 panels
col = st.columns((1.5, 4.5, 2), gap='medium')

# Enable dark theme for Altair
alt.themes.enable("dark")

# Load data
os.chdir(r'C:\Users\arii3\OneDrive\Desktop\Website\Streamlit') # Uncomment for changing directory
df = pd.read_csv('Crime_Data_from_2020_to_Present.csv', encoding="ISO-8859-1")

#Getting the date of occurance
df["DATE OCC"] = pd.to_datetime(df["DATE OCC"])


# Sidebar
with st.sidebar:
    st.markdown("<h2 class='centered animated-title'>Time Range</h2>", unsafe_allow_html=True)
    filter_option = st.radio("Select wether to filter data by year or a specific date range:", ("Year", "Date Range"))

    if filter_option == "Year":
        # Extract year from 'DATE OCC'
        df['year'] = df["DATE OCC"].dt.year
        year_list = list(df['year'].unique())
        selected_year = st.selectbox('Select a year', year_list)
        df_filtered = df[df['year'] == selected_year]
    else:
        date1 = st.date_input("Start Date", df["DATE OCC"].min())
        date2 = st.date_input("End Date", df["DATE OCC"].max())
        df_filtered = df[(df["DATE OCC"] >= pd.to_datetime(date1)) & (df["DATE OCC"] <= pd.to_datetime(date2))]

    st.markdown("<h3 class='centered animated-title'>State</h3>", unsafe_allow_html=True)
    states = ["California", "Other State"]
    state = st.selectbox("Select a state", states)

    st.markdown("<h3 class='centered animated-title'>Theme</h3>", unsafe_allow_html=True)
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


#################################################################################
# Data by area name for the selected year or date range
crime_counts = df_filtered.groupby('AREA NAME').size().reset_index(name='crime_count')

# Calculate percentage of crime counts for each area
total_crimes = crime_counts['crime_count'].sum()
crime_counts['crime_percentage'] = (crime_counts['crime_count'] / total_crimes) * 100

# #Get the time for each crime
# df_filtered['hour'] = df_filtered["DATE OCC"].dt.hour
# crime_counts_hour = df_filtered.groupby('hour').size().reset_index(name='crime_count_hour')
#################################################################################


# Heatmap function
def make_heatmap(input_df, input_x, input_y, input_color_theme, name_x, name_y):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title= name_x, titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'{input_y}:Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            y=alt.Y(f'{input_y}:Q', axis=alt.Axis(title= name_y, titleFontSize=18, titlePadding=15, titleFontWeight=900))
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    return heatmap

# Choropleth map function
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(input_df[input_column])),
                               scope="usa",
                               labels={input_column:input_column.capitalize()}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

# Donut chart function
def make_donut(input_df, input_color_theme):
    fig = px.pie(input_df, values='crime_percentage', names='AREA NAME', hole=0.45, color='AREA NAME', 
                 color_discrete_sequence=px.colors.qualitative.Dark24, title='Crime Percentage by Area')
    fig.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=2)))
    fig.update_layout(showlegend=True, template='plotly_dark', colorway=px.colors.qualitative.Dark24)
    return fig

with col[1]:
    # Generate choropleth
    st.markdown("<h4 class='centered animated-title'>Crime Heatmap by State</h4>", unsafe_allow_html=True)
    choropleth = make_choropleth(crime_counts, 'AREA NAME', 'crime_count', selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)

    # Generate heatmap
    st.markdown("<h4 class='centered animated-title'>Crime Heatmap by State Area</h4>", unsafe_allow_html=True)
    heatmap = make_heatmap(crime_counts, 'AREA NAME', 'crime_count', selected_color_theme, "Area", "Crime Count")
    st.altair_chart(heatmap, use_container_width=True)

    st.write('NOTE: Not sure if the numbers are correct. Rough Math: Data set has ab 1 M enties for 5 years.'
            ' There are 21 areas. So if we divide 1M by 5 we get 200k. Lets take the acrime count for each area to be 10k,'
            ' which would be a little higher than average I think. Then 10k * 21 = 210k, so it is prob right')
    
    # # Generate heatmap for crimes per hour
    # st.markdown("<h4 class='centered animated-title'>Crime Heatmap by Hour and Area</h4>", unsafe_allow_html=True)
    # second_heatmap = make_heatmap(crime_counts_hour,'hour', 'crime_count', selected_color_theme, "Hour", "Crimes per hour")
    # st.altair_chart(second_heatmap, use_container_width=True)
    
with col[2]:
    # Generate donut chart
    st.markdown("<h4 class='centered animated-title'>Donut Chart Crime Percentage</h4>", unsafe_allow_html=True)
    donut_chart = make_donut(crime_counts, selected_color_theme)
    st.plotly_chart(donut_chart, use_container_width=True)
