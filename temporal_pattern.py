import streamlit as st
import pandas as pd
import os
import altair as alt
import plotly.express as px


#NOTES: 
#df = varaiable where the data
#from the csv file is stored 
#and later manipulated by pandas

# Page Configuration
st.set_page_config(
    page_title="L.A. Crime Data",
    page_icon=":foggy:",                
    layout="wide",                      # Side bar space
    initial_sidebar_state="expanded"    # Side bar starting position
)


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


# Define the CSS for smooth scrolling
smooth_scroll_css = """
<style>
html {
  scroll-behavior: smooth;
}
</style>
"""

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


# Put title up in the page
st.markdown("<h1 class='centered animated-title'>Los Angeles Crime Data Dashboard</h1>", unsafe_allow_html=True)

# 3 panels
col = st.columns((1.5, 4.5, 2), gap='medium')

# Enable dark theme for Altair
alt.themes.enable("dark")

# Load data
#os.chdir(datapath) # Uncomment for changing directory
df = pd.read_csv('Crime_Data_from_2020_to_Present.csv', encoding="ISO-8859-1")


#Getting the date of occurance
df["DATE OCC"] = pd.to_datetime(df["DATE OCC"])

# Convert TIME OCC to standard time format
def convert_time_occ(time_occ):
    time_occ_str = str(int(time_occ)).zfill(4)
    if len(time_occ_str) == 1:
        return f"{time_occ_str}:00"
    elif len(time_occ_str) == 2:
        return f"{time_occ_str}:00"
    elif len(time_occ_str) == 3:
        return f"{time_occ_str[0]}:{time_occ_str[1:]}"
    else:  # length is 4
        return f"{time_occ_str[:2]}:{time_occ_str[2:]}"
    
# Apply conversion
df["TIME OCC"] = df["TIME OCC"].apply(convert_time_occ)

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

    st.markdown("<h3 class='centered animated-title'>Theme</h3>", unsafe_allow_html=True)
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


# Data by area name 
crime_counts = df_filtered.groupby('AREA NAME').size().reset_index(name='crime_count')

# Calculate percentage of crime counts for each area
total_crimes = crime_counts['crime_count'].sum()
crime_counts['crime_percentage'] = (crime_counts['crime_count'] / total_crimes) * 100


seasons = {
    "Spring": (3, 5),
    "Summer": (6, 8),
    "Fall": (9, 11),
    "Winter": (12, 2)
}

# Filter data based on seasons
df_filtered_seasons = {}
for season, (start_month, end_month) in seasons.items():
    if start_month < end_month:
        df_filtered_seasons[season] = df_filtered[(df_filtered["DATE OCC"].dt.month >= start_month) & (df_filtered["DATE OCC"].dt.month <= end_month)]
    else:
        df_filtered_seasons[season] = df_filtered[(df_filtered["DATE OCC"].dt.month >= start_month) | (df_filtered["DATE OCC"].dt.month <= end_month)]

# Calculate crime percentages for each season
crime_counts_seasons = {season: len(df_season) for season, df_season in df_filtered_seasons.items()}
total_season_crimes = sum(crime_counts_seasons.values())
crime_percentage_seasons = {season: (count / total_season_crimes) * 100 for season, count in crime_counts_seasons.items()}



# Getting the hour from TIME OCC
df_filtered["HOUR OCC"] = pd.to_datetime(df_filtered["TIME OCC"], format='mixed').dt.hour
crime_counts_hourly = df_filtered.groupby("HOUR OCC").size().reset_index(name='crime_count')

# Getting day of the week from DATE OCC
df_filtered['DAY OF WEEK'] = df_filtered["DATE OCC"].dt.day_name()
crime_counts_weekly = df_filtered.groupby("DAY OF WEEK").size().reset_index(name='crime_count')

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
        titleFontSize=14
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
    #Heatmap
    st.markdown("<h4 class='centered animated-title'>Crime Heatmap by State Area</h4>", unsafe_allow_html=True)
    heatmap = make_heatmap(crime_counts, 'AREA NAME', 'crime_count', selected_color_theme, "Area", "Crime Count")
    st.altair_chart(heatmap, use_container_width=True)    

    # Crime patterns by hour
    st.markdown("<h4 class='centered animated-title'>Crime Patterns by Hour of the Day</h4>", unsafe_allow_html=True)
    crime_patterns_by_hour = make_heatmap(crime_counts_hourly,'HOUR OCC','crime_count',selected_color_theme,"Hour of the day", "Number of crimes")
    st.altair_chart(crime_patterns_by_hour, use_container_width=True)

     # Crime patterns by day of the week
    st.markdown("<h4 class='centered animated-title'>Crime Patterns by Day of the Week</h4>", unsafe_allow_html=True)
    crime_patterns_by_weekly = make_heatmap(crime_counts_weekly, 'DAY OF WEEK', 'crime_count', selected_color_theme, "Day of the Week", "Number of crimes")
    st.altair_chart(crime_patterns_by_weekly, use_container_width=True)
 
with col[2]:
    # Donut chart for Crime percentages
    st.markdown("<h4 class='centered animated-title'>Donut Chart Crime Percentage</h4>", unsafe_allow_html=True)
    donut_chart = make_donut(crime_counts, selected_color_theme)
    st.plotly_chart(donut_chart, use_container_width=True)

    # Crime percentages by season
    st.markdown("<h4 class='centered animated-title'>Crime Percentage by Season</h4>", unsafe_allow_html=True)
    for season, percentage in crime_percentage_seasons.items():
        st.metric(label=f"Crime Percentage in {season}", value=f"{percentage:.2f}%")
