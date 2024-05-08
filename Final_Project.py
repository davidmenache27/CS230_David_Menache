"""
Name: David Menache
CS230: Section 4
Data: Starbucks Stores
URL: https://github.com/davidmenache27/CS230_David_Menache.git

Description:
This program provides an interactive analysis of Starbucks store locations using a dataset that includes various attributes of Starbucks stores around the globe. Users can filter data by country and city, visualize store locations on interactive maps, and explore store distributions by ownership type and density categories.
The application leverages powerful visualizations like bar charts, pie charts, and maps to offer insights into the concentration of stores across different regions and the different types ownership models within the Starbucks stores.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import seaborn as sns

# [PY1]
def load_data(filepath):
    return pd.read_csv(filepath)

# [PY2]
def filter_data(data, column, values):
    return data[data[column].isin(values)]

# Load data from a CSV file located at the specified path
data_path = "starbucks_10000_sample.csv"
df_starbucks = load_data(data_path)

df_starbucks.rename(columns={"Latitude": "lat", "Longitude": "lon"}, inplace=True)
df_starbucks['lon'] = pd.to_numeric(df_starbucks['lon'], errors='coerce')
df_starbucks['lat'] = pd.to_numeric(df_starbucks['lat'], errors='coerce')

# [DA1] Using a lambda function for data manipulation
df_starbucks['Density Category'] = df_starbucks['StoreNumber'].apply(lambda x: 'High Density' if int(x.split('-')[-1]) > 1000 else 'Low Density')

# [ST1] Sidebar for country selection
country_list = df_starbucks['CountryCode'].dropna().unique()
selected_country = st.sidebar.selectbox('Select a Country Code:', country_list)
filtered_data = filter_data(df_starbucks, 'CountryCode', [selected_country])

# [ST2] Sidebar for city selection
city_list = filtered_data['City'].dropna().unique()
selected_cities = st.sidebar.multiselect('Select Cities:', city_list)

# [ST3] Page design feature: sidebar link
st.sidebar.markdown('[Visit Starbucks Website](https://www.starbucks.com)')

if selected_cities:
    filtered_data = filter_data(filtered_data, 'City', selected_cities)

# [ST4] Display logo
logo_path = "starbucks_logo.png"
st.image(logo_path, width=100)

# Setup tabs
tab1, tab2, tab3, tab4 = st.tabs(["Data Breakdown", "Interactive Map View", "Top Cities", "Ownership Type Distribution"])

with tab1:
    # [DA2] Sorting data in ascending order by one column
    st.write("### Original Data View")
    st.write("Below is the complete dataset from the CSV file. This view helps in understanding the raw data before any filters are applied.")

    # [DA3] Displaying DataFrame with sorted data
    st.dataframe(df_starbucks)

    st.write("### Filtered Data by Country")
    st.write("This view shows data filtered by the selected country from the sidebar. It helps in analyzing specific geographic locations.")
    st.dataframe(filtered_data)

    # [DA4]
    st.write("### Sorted Data by City")
    st.write("After filtering by country, the data is sorted by city. This helps in understanding and narrowing the Starbucks stores in each city within the selected country.")
    sorted_data = filtered_data.sort_values(by='City')[['City', 'StoreNumber', 'Density Category']]
    st.dataframe(sorted_data)

    # [DA5] Pivot Table
    st.write("### Pivot Table Analysis")
    st.write("The pivot table below analyzes store by city and ownership type. It's useful for spotting trends in different business models across different cities.")
    pivot_table = pd.pivot_table(filtered_data, values='StoreNumber', index=['City'], columns='OwnershipType', aggfunc='count', fill_value=0)
    st.dataframe(pivot_table)

with tab2:
    # [VIZ1] Interactive Map View of Starbucks Locations
    st.write("### Interactive Map View of Starbucks Locations")
    st.write(
        "View Starbuck stores in a visual way through different types of maps such as heatmaps or scatterplots. Use the radio buttons to switch between visualization types.")

    # Radio button to let users choose the visualization type
    map_type = st.radio("Choose Visualization Type", ('Heatmap', 'Scatterplot'))

    # [VIZ2]
    # Define layers based on the user's choice
    if map_type == 'Heatmap':
        layers = [pdk.Layer(
            'HeatmapLayer',
            data=filtered_data,
            get_position='[lon, lat]',
            radius=100,
            intensity=1,
            opacity=0.9,
            threshold=0.5,
            pickable=True
        )]

    # [VIZ3]
    elif map_type == 'Scatterplot':
        layers = [pdk.Layer(
            "ScatterplotLayer",
            filtered_data,
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
            radius_scale=6,
            radius_min_pixels=1,
            radius_max_pixels=100,
            line_width_min_pixels=1,
            get_position=["lon", "lat"],
            get_radius=100,
            get_fill_color=[255, 140, 0],
            get_line_color=[0, 0, 0],
        )]

    # # [VIZ4] Define the view state for the map
    view_state = pdk.ViewState(
        latitude=filtered_data['lat'].mean(), # Sets the initial latitude to the mean latitude of the filtered data, centering the map around the average latitude of all stores.
        longitude=filtered_data['lon'].mean(), # Sets the initial longitude to the mean longitude of the filtered data, centering the map around the average longitude of all stores.
        zoom=3,
        bearing=0,
        pitch=0
    )

    # [VIZ5] Map with the chosen layer
    map = pdk.Deck(
        layers=layers, # Specifies the layers to be used on the map; these could be HeatmapLayer or ScatterplotLayer depending on user selection.
        initial_view_state=view_state,
        map_style='mapbox://styles/mapbox/light-v10' if map_type == 'Scatterplot' else 'mapbox://styles/mapbox/outdoors-v11', # light for scatterplots and outdoors for heatmaps.
        tooltip={"html": "Store Name:<br/> <b>{Name}</b>"}
    )

    st.pydeck_chart(map)

with tab3:
    # [DA6] Filtering data by condition
    st.write("### Top Cities by Number of Stores")
    st.write("The bar chart below ranks the top cities by the number of stores, highlighting locations with the highest concentration of Starbucks stores. This can indicate markets that Starbucks has a strong presence and potential areas for growth.")

    # Counts the occurrences of each city in the 'City' column and selects the top 10
    city_counts = filtered_data['City'].value_counts().nlargest(10)

    # Creates a figure and a set of subplots
    fig, ax = plt.subplots()

    # [VIZ6]
    # Creates a bar chart with cities on the x-axis and store counts on the y-axis
    ax.bar(city_counts.index, city_counts)

    ax.set_xlabel('City')
    ax.set_ylabel('Number of Stores')
    ax.set_title('Top 10 Cities')
    plt.xticks(rotation=45)

    # Displays the matplotlib plot in the Streamlit app
    st.pyplot(fig)

    # Counts the number of stores per city again and resets the index to turn it into a DataFrame
    city_counts = filtered_data['City'].value_counts().reset_index()
    city_counts.columns = ['City', 'Number of Stores']
    city_counts_sorted = city_counts.sort_values(by='Number of Stores', ascending=False)
    top_cities = city_counts_sorted.iloc[:10]

    # Displays the DataFrame of top cities in Streamlit
    st.dataframe(top_cities)

with tab4:
    # [VIZ7] Pie chart
    st.write("### Ownership Type Distribution")
    st.write("This pie chart shows the distribution of different types of store ownership within the selected country such as Joint Ventures (JV), Co-Owners (CO), Licensed Stores (LS), and Franchises (FR).")

    ownership_counts = filtered_data['OwnershipType'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(ownership_counts, labels=ownership_counts.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal') # Ensures the pie chart is displayed as a circle
    st.pyplot(fig)

    # [VIZ8] Bar Plot in seaborn
    # Re-counts the occurrences of each ownership type and resets the index
    ownership_counts = df_starbucks['OwnershipType'].value_counts().reset_index()

    # Renames columns for clarity
    ownership_counts.columns = ['OwnershipType', 'StoreCount']

    # Checks if the ownership_counts variable is a DataFrame, displaying an error if not
    if not isinstance(ownership_counts, pd.DataFrame):
        st.error("ownership_counts is not a DataFrame.")
    else:
        # Sets the theme for seaborn plots
        sns.set_theme(style="whitegrid")

        # Creates a new figure for the bar plot
        plt.figure(figsize=(10, 6))

        # Creates a bar plot showing the distribution of store counts by ownership type
        ax = sns.barplot(
            data=ownership_counts,
            x='OwnershipType',
            y='StoreCount',
            palette='viridis'
        )

        # Sets the title, labels, and formatting for the bar plot
        ax.set_title('Distribution of Starbucks Store Counts by Ownership Type', fontsize=16) # Name title
        ax.set_xlabel('Ownership Type', fontsize=14) # Name x axis
        ax.set_ylabel('Number of Stores', fontsize=14) # Name y axis
        ax.grid(True, which='both', linestyle='--', linewidth='0.5', color='gray') #Adds a grid to the chart.
        ax.tick_params(axis='both', which='major', labelsize=12) # Configures the tick parameters for both axes.
        sns.despine(offset=10, trim=True)

        # Displays the seaborn plot in the Streamlit app
        st.pyplot(plt)

    # [VIZ9] Subplot in seaborn
    # Extracts the 'Year' from the 'FirstSeen' date column
    df_starbucks['Year'] = pd.to_datetime(df_starbucks['FirstSeen'], format='%m/%d/%Y %I:%M:%S %p').dt.year

    # Groups the data by 'Year' and 'OwnershipType' and counts the stores, filling missing values with zero
    store_counts_by_year = df_starbucks.groupby(['Year', 'OwnershipType']).size().unstack(fill_value=0)

    # Converts the wide-form data into long-form for plotting
    store_counts_long = store_counts_by_year.reset_index().melt(id_vars='Year', var_name='OwnershipType', value_name='StoreCount')

    # Bar plot showing the number of store openings by year and ownership type
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=store_counts_long, x='Year', y='StoreCount', hue='OwnershipType', palette='tab10', ax=ax)
    ax.set_title('Starbucks Store Openings by Ownership Type Over Years')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Store Openings')

    st.pyplot(fig)
