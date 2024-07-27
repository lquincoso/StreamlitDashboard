import os
import folium
import joblib
import pandas as pd
import requests
import streamlit as st
import plotly.express as px
import altair as alt
import dask.dataframe as dd

from io import StringIO
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu

# ========================================================
# STARTER UI ELEMENTS                                    |
# ========================================================

st.set_page_config(
    layout="wide",
    page_title="L.A. Crime Data",
    page_icon=":foggy:"
)



css_file = os.path.abspath('style.css')
with open(css_file) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

# ========================================================
# STREAMLIT DASHBOARD                                    |
# ========================================================

colx, coly = st.columns([1, 1])
with colx:
    st.markdown("<h2 class='centered animated-title'>L.A. Crime Dashboard</h2>", unsafe_allow_html=True)
with coly:
    selection = option_menu(
        menu_title=None,
        options=["Data", "Predictive Model"],
        orientation="horizontal",
        icons=["bar-chart-fill","activity"]
    )

if selection == "Data":
    # TREND ANALYSIS ===================|

    with st.container(border=True):

        @st.cache_data()
        def load_crime_csv():
            crime_data_csv = os.path.abspath('Crime_Data_from_2020_to_Present.csv')
            crime_data = pd.read_csv(crime_data_csv)
            crime_data['DATE OCC'] = pd.to_datetime(crime_data['DATE OCC'], format='%m/%d/%Y')
            crime_data['month-year'] = crime_data['DATE OCC'].dt.to_period('M')
            return crime_data


        @st.cache_data()
        def total_crime_data(crime_data):
            total_crime = crime_data.groupby('month-year').size().reset_index(name='total crime')
            total_crime = total_crime[total_crime['month-year'] != pd.Period('2024-05', freq='M')]
            total_crime['month-year'] = total_crime['month-year'].dt.to_timestamp()
            return total_crime


        @st.cache_data()
        def filter_trend_data(crime_data, selected_crime):
            crime_trend = crime_data[crime_data['Crm Cd Desc'] == selected_crime]
            crime_trend['month-year'] = crime_trend['DATE OCC'].dt.to_period('M')
            occurrences_per_month = crime_trend.groupby('month-year').size().reset_index(name='occurrences')
            occurrences_per_month = occurrences_per_month[
                occurrences_per_month['month-year'] != pd.Period('2024-05', freq='M')]
            occurrences_per_month['month-year'] = occurrences_per_month['month-year'].dt.to_timestamp()
            return occurrences_per_month


        crime_data = load_crime_csv()
        total_crime = total_crime_data(crime_data)
        crime_codes = crime_data['Crm Cd Desc'].unique()

        col1, col2, col3 = st.columns([1, 2, 2])

        with col1:
            select_crime = st.selectbox('Select Crime', crime_codes)

        with col3:
            total_graph = px.line(
                total_crime,
                x='month-year',
                y='total crime',
                title='TOTAL CRIME',
                height=500
            )
            st.plotly_chart(total_graph, use_container_width=True)


        with col2:

            filter_graph = px.line(
                filter_trend_data(crime_data, select_crime),
                x='month-year',
                y='occurrences',
                title="CRIME: "+select_crime,
                height=500
            )
            st.plotly_chart(filter_graph, use_container_width=True)

    # TEMPORAL ANALYSIS ================|

    with st.container(border=True):

        col1, col2, col3 = st.columns([1,2,1.5])

        with col1:

            # Load data
            df = pd.read_csv('Crime_Data_from_2020_to_Present.csv', encoding="ISO-8859-1")

            # Getting the date of occurance
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
            df_filtered = df.copy()
            crime_counts = df_filtered.groupby('AREA NAME').size().reset_index(name='crime_count')
            total_crimes = crime_counts['crime_count'].sum()
            crime_counts['crime_percentage'] = (crime_counts['crime_count'] / total_crimes) * 100
            selected_color_theme = 'blues'

            filter_option = st.radio("Select wether to filter data by year or a specific date range:",
                                     ("Year", "Date Range"))

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

            color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo',
                                'viridis']
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
                    df_filtered_seasons[season] = df_filtered[
                        (df_filtered["DATE OCC"].dt.month >= start_month) & (df_filtered["DATE OCC"].dt.month <= end_month)]
                else:
                    df_filtered_seasons[season] = df_filtered[
                        (df_filtered["DATE OCC"].dt.month >= start_month) | (df_filtered["DATE OCC"].dt.month <= end_month)]

            # Calculate crime percentages for each season
            crime_counts_seasons = {season: len(df_season) for season, df_season in df_filtered_seasons.items()}
            total_season_crimes = sum(crime_counts_seasons.values())
            crime_percentage_seasons = {season: (count / total_season_crimes) * 100 for season, count in
                                        crime_counts_seasons.items()}

            # Getting the hour from TIME OCC
            df_filtered["HOUR OCC"] = pd.to_datetime(df_filtered["TIME OCC"], format='mixed').dt.hour
            crime_counts_hourly = df_filtered.groupby("HOUR OCC").size().reset_index(name='crime_count')

            # Getting day of the week from DATE OCC
            df_filtered['DAY OF WEEK'] = df_filtered["DATE OCC"].dt.day_name()
            crime_counts_weekly = df_filtered.groupby("DAY OF WEEK").size().reset_index(name='crime_count')


            # Heatmap function
            def make_heatmap(input_df, input_x, input_y, input_color_theme, name_x, name_y):
                heatmap = alt.Chart(input_df).mark_rect().encode(
                    x=alt.X(f'{input_x}:O',
                            axis=alt.Axis(title=name_x, titleFontSize=18, titlePadding=15, titleFontWeight=900)),
                    color=alt.Color(f'{input_y}:Q',
                                    legend=None,
                                    scale=alt.Scale(scheme=input_color_theme)),
                    y=alt.Y(f'{input_y}:Q',
                            axis=alt.Axis(title=name_y, titleFontSize=18, titlePadding=15, titleFontWeight=900))
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
                                           labels={input_column: input_column.capitalize()}
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
            #filters here
            st.write("#")
            st.write("#")
            # Crime percentages by season
            st.markdown("<h4 class='centered animated-title'>Crime Percentage by Season</h4>", unsafe_allow_html=True)
            for season, percentage in crime_percentage_seasons.items():
                st.metric(label=f"{season}", value=f"{percentage:.2f}%")

        with col2:
            # Heatmap
            st.markdown("<h4 class='centered animated-title'>Crime Heatmap by State Area</h4>", unsafe_allow_html=True)
            heatmap = make_heatmap(crime_counts, 'AREA NAME', 'crime_count', selected_color_theme, "Area", "Crime Count")
            st.altair_chart(heatmap, use_container_width=True)

            # Crime patterns by hour
            st.markdown("<h4 class='centered animated-title'>Crime Patterns by Hour of the Day</h4>",
                        unsafe_allow_html=True)
            crime_patterns_by_hour = make_heatmap(crime_counts_hourly, 'HOUR OCC', 'crime_count', selected_color_theme,
                                                  "Hour of the day", "Number of crimes")
            st.altair_chart(crime_patterns_by_hour, use_container_width=True)



        with col3:
            # Donut chart for Crime percentages
            donut_chart = make_donut(crime_counts, selected_color_theme)
            st.plotly_chart(donut_chart, use_container_width=True)

            # Crime patterns by day of the week
            st.markdown("<h4 class='centered animated-title'>Crime Patterns by Day of the Week</h4>",
                        unsafe_allow_html=True)
            crime_patterns_by_weekly = make_heatmap(crime_counts_weekly, 'DAY OF WEEK', 'crime_count', selected_color_theme,
                                                    "Day of the Week", "Number of crimes")
            st.altair_chart(crime_patterns_by_weekly, use_container_width=True)

    # Geographical Distribution ================|

    with st.container(border=True):
        col1, col2 = st.columns((0.5, 2))
        with col1:
            @st.cache_data
            def load_data(nrows):
                url = "https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD"
                cols = ["LAT", "LON", "Crm Cd Desc"]  # Only necessary columns
                data = pd.read_csv(url, usecols=cols, nrows=nrows)
                return data


            # Load only the first 20,000 rows for example
            data = load_data(20000)
            st.markdown(
                """
                <style>
                div[data-baseweb="select"] {
                    max-height: 500px;
                    overflow: auto;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            # user input
            crime_types = st.multiselect("Select Crime Types:", options=data["Crm Cd Desc"].unique(),
                                                 default=data["Crm Cd Desc"].unique())

            # Filter data
            filtered_data = data[data["Crm Cd Desc"].isin(crime_types)]

            # Aggregate data
            agg_data = filtered_data.groupby(['LAT', 'LON', 'Crm Cd Desc']).size().reset_index(name='Count')

        with col2:
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
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
            fig.update_traces(marker=dict(size=5))  # Smaller marker size
            fig.update_layout(clickmode='event+select')  # Optimize interactivity

            # Display map in Streamlit
            st.markdown("<h4 class='centered animated-title'>Geographical Distribution of Crimes</h4>",
                        unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)

if selection == "Predictive Model":
    with st.container(border=True):
        @st.cache_data
        def download_data(url):
            response = requests.get(url)
            if response.status_code == 200:
                data = StringIO(response.text)
                return pd.read_csv(data)
            else:
                st.error("Failed to download the dataset.")
                return None


        @st.cache_data
        def load_model():
            model = joblib.load(os.path.abspath('models/knn_model.pkl'))
            feature_columns = joblib.load(os.path.abspath('models/feature_columns.pkl'))
            return model, feature_columns


        def prepare_input_data(area_name, day_of_week, hour_of_day, month, is_weekend, feature_columns):
            input_data = {
                'AREA_NAME': [area_name],
                'DayOfWeek': [day_of_week],
                'HourOfDay': [hour_of_day],
                'Month': [month],
                'IsWeekend': [is_weekend]
            }
            input_df = pd.DataFrame(input_data)
            input_df = pd.get_dummies(input_df, columns=['AREA_NAME'])

            for col in feature_columns:
                if col not in input_df.columns:
                    input_df[col] = 0

            return input_df


        # URL of the dataset
        url = 'https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD'

        # Loading the dataset
        df = download_data(url)

        # Preprocessing steps to ensure required columns are available
        df = df.rename(columns={
            "Crm Cd Desc": "Crime Code Descript",
            "AREA NAME": "AREA_NAME"
        })

        model, feature_columns = load_model()

        # Streamlit Interface
        st.markdown("<h4 class='centered animated-title'>Crime Prediction Model</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns((0.5, 2))
        with col1:
            st.write('Input Features')
            area_name = st.selectbox('Area Name', sorted(df['AREA_NAME'].unique()))
            day_of_week = st.selectbox('Day of the Week', range(7), format_func=lambda x:
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][x])
            hour_of_day = st.slider('Hour of the Day', 0, 23, 12)
            month = st.selectbox('Month', range(1, 13))
            is_weekend = st.selectbox('Is Weekend', [0, 1], format_func=lambda x: 'Yes' if x == 1 else 'No')

            if st.button('Predict'):
                # Preparing input data (received from the user)
                input_data = prepare_input_data(area_name, day_of_week, hour_of_day, month, is_weekend, feature_columns)

                # Making a prediction
                prediction = model.predict(input_data)

                st.write('## Prediction')
                st.write(f'The predicted crime category is: **{prediction[0]}**')
        with col2:
            # Adding a map of Los Angeles in order to display target area
            st.write('Map of Los Angeles with Predicted Crime Areas')

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
