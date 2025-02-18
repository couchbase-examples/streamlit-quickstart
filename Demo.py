import streamlit as st
from couchbase_streamlit_connector.connector import CouchbaseConnector
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from geopy.distance import geodesic

######################################### tab1 ################################################

@st.cache_data
def get_all_airports(_connection):
    query = """
    SELECT geo.lat, geo.lon, city, country, airportname as name, faa, icao, id
    FROM `travel-sample`.inventory.airport
    WHERE geo.lat IS NOT NULL 
    AND geo.lon IS NOT NULL
    AND faa IS NOT NULL;
    """
    result = _connection.query(query)
    return pd.DataFrame([row for row in result.rows()])
 
@st.cache_data       
def get_routes_for_airports(_connection, selected_airports_df):    
    airports_faa = "["
    for i in range(len(selected_airports_df)):
        if i != len(selected_airports_df) - 1:
            airports_faa += f'"{(selected_airports_df.iloc[i])["faa"]}", '
        else:
            airports_faa += f'"{(selected_airports_df.iloc[i])["faa"]}"'
    airports_faa += "]"
    query = f"""
    SELECT * FROM `travel-sample`.`inventory`.`route`
    WHERE (sourceairport IN {airports_faa} AND destinationairport IN {airports_faa});
    """
    result = _connection.query(query)
    data = []
    for row in result:
        data.append(row["route"])
    return pd.DataFrame(data)

def plot_airports_and_routes(airports_df, routes_df):
    fig = go.Figure()
    airport_coords = {
        row["faa"]: (row["lat"], row["lon"])
        for _, row in airports_df.iterrows()
        if row["faa"] is not None  # Ensure faa is not null
    }
    lats = []
    lons = []
    for _, row in routes_df.iterrows():
        source_coords = airport_coords.get(row["sourceairport"])
        dest_coords = airport_coords.get(row["destinationairport"])
        if source_coords and dest_coords:
            lats.extend([source_coords[0], dest_coords[0], None])  # None for breaks
            lons.extend([source_coords[1], dest_coords[1], None])

    fig.add_trace(go.Scattermap(
        mode="lines",
        lat=lats,
        lon=lons,
        line=dict(width=1, color="blue")
    ))
    
    airports_markers = px.scatter_map(
        airports_df, 
        lat="lat", 
        lon="lon", 
        hover_name= "name",  # Show airport name on hover
        hover_data= {
            "faa": True,
            "city": True,
            "country": True
        },  # Additional details
        color_discrete_sequence=["red"],  # Color of airport markers
    )
    fig.add_traces(airports_markers.data)
    fig.update_layout(
        mapbox_style="open-street-map",  
        margin=dict(l=0, r=0, t=50, b=0),  # Remove extra margins
        title="Airports and Flight Routes"
    )
    
    st.plotly_chart(fig, use_container_width=True)
        
def tab1_visual():
    all_airports = get_all_airports(connection)
    route_airports = set()
    for route in [
        {"sourceairport": "TLV", "destinationairport": "MRS"},
        {"sourceairport": "TLV", "destinationairport": "NCE"},
        {"sourceairport": "TNR", "destinationairport": "CDG"},
        {"sourceairport": "TPA", "destinationairport": "ATL"},
        {"sourceairport": "TPE", "destinationairport": "AMS"},
        {"sourceairport": "TPE", "destinationairport": "MNL"},
        {"sourceairport": "TRI", "destinationairport": "ATL"},
        {"sourceairport": "TRN", "destinationairport": "CDG"},
        {"sourceairport": "TUL", "destinationairport": "ATL"},
        {"sourceairport": "TUN", "destinationairport": "CDG"},
        {"sourceairport": "MCG", "destinationairport": "NIB"},
        {"sourceairport": "TUN", "destinationairport": "MRS"},
        {"sourceairport": "TUS", "destinationairport": "ATL"},
        {"sourceairport": "TXL", "destinationairport": "CDG"},
        {"sourceairport": "TXL", "destinationairport": "MRS"},
        {"sourceairport": "TYS", "destinationairport": "ATL"},
        {"sourceairport": "UIO", "destinationairport": "GYE"},
        {"sourceairport": "VCE", "destinationairport": "CDG"},
        {"sourceairport": "VCE", "destinationairport": "LYS"},
        {"sourceairport": "VCE", "destinationairport": "MRS"}
    ]:
        route_airports.add(route["sourceairport"])
        route_airports.add(route["destinationairport"])
    with st.expander("Select Airports"):
        st.checkbox("Select All Airports", key="select_all")
        container = st.container()
        with container:
            selected_airports = st.multiselect(
                "Choose airports", 
                options=all_airports["name"], 
                default=all_airports["name"] if st.session_state.get("select_all") else []
            )
    if st.button("Update Map"):
        filtered_airports = all_airports[all_airports["name"].isin(selected_airports)]
        selected_routes = get_routes_for_airports(connection, filtered_airports)
        plot_airports_and_routes(filtered_airports, selected_routes)

######################################### tab2 #################################################

@st.cache_data
def get_all_landmarks(_connection):
    query = """
        SELECT 
            name,
            geo.lat,
            geo.lon,
            activity,
            address,
            city,
            country,
            content,
            hours,
            price,
            type
        FROM `travel-sample`.inventory.landmark
        WHERE geo.lat IS NOT MISSING 
        AND geo.lon IS NOT MISSING
    """
    result = _connection.query(query)
    landmarks = []
    for row in result:
        landmark_info = {
            'name': row['name'],
            'lat': row['lat'],
            'lon': row['lon'],
            'activity': row.get('activity', 'Not specified'),
            'address': row.get('address', 'Not specified'),
            'city': row.get('city', 'Not specified'),
            'country': row.get('country', 'Not specified'),
            'content': row.get('content', 'No description available'),
            'hours': row.get('hours', 'Not specified'),
            'price': row.get('price', 'Not specified'),
            'type': row.get('type', 'Not specified')
        }
        landmarks.append(landmark_info)
    return landmarks

@st.cache_data
def get_hotels_near_landmark(_connection, landmark_lat, landmark_lon, max_distance_km=10):
    query = """
        SELECT 
            h.name,
            h.geo.lat,
            h.geo.lon,
            h.price,
            h.description,
            h.free_breakfast,
            h.free_internet,
            h.free_parking
        FROM `travel-sample`.inventory.hotel h
        WHERE h.geo.lat IS NOT MISSING 
        AND h.geo.lon IS NOT MISSING
    """
    result = _connection.query(query)
    hotels = []
    for row in result:
        hotel_coords = (row['lat'], row['lon'])
        landmark_coords = (landmark_lat, landmark_lon)
        distance = geodesic(hotel_coords, landmark_coords).kilometers

        if distance <= max_distance_km:
            hotels.append({
                'name': row['name'],
                'lat': row['lat'],
                'lon': row['lon'],
                'distance': distance,
                'price': row['price'],
                'description': row.get('description', 'No description available'),
                'free_breakfast': row.get('free_breakfast', False),
                'free_internet': row.get('free_internet', False),
                'free_parking': row.get('free_parking', False)
            })
    return hotels

def create_landmark_map(landmarks, hotels_near_landmark):
    fig = go.Figure()        
    for hotel in hotels_near_landmark:
        color = 'red' if hotel.get('distance') <= 3 else 'orange' if hotel.get('distance') <= 6 else 'gold'
        fig.add_trace(go.Scattermap(
            lat=[hotel.get('lat')],
            lon=[hotel.get('lon')],
            mode='markers',
            marker=dict(size=10, color=color),
            text=(
                f"HOTEL: {hotel.get('name')}<br>Distance: {hotel.get('distance'):.2f} km",
            ),
            hoverinfo='text',
            name=f'Hotel ({color})'
        ))
        
    for landmark in landmarks:
        fig.add_trace(go.Scattermap(
            lat=[landmark.get('lat', 'N/A')],
            lon=[landmark.get('lon', 'N/A')],
            mode='markers',
            marker=dict(size=10, color='blue', symbol='star'),
            text=(
                f"LANDMARK: {landmark.get('name', 'N/A')}",
            ),
            hoverinfo='text',
            name='Landmark'
        ))
    
    fig.update_layout(
        mapbox_style='open-street-map',
        margin=dict(l=0, r=0, t=50, b=0),
        title='Landmarks and Hotels Nearby',
        showlegend=False,
    )
    
    st.plotly_chart(fig, use_container_width=True)

def tab2_visual():
    landmarks = get_all_landmarks(connection)
    default_landmark = [landmarks[0]['name']] if landmarks else []
    selected_landmarks = st.multiselect("Select landmarks", [landmark['name'] for landmark in landmarks], default=default_landmark)
    selected_landmarks_info = [landmark for landmark in landmarks if landmark['name'] in selected_landmarks]
    
    hotels_near_landmarks = []
    for landmark in selected_landmarks_info:
        hotels_near_landmarks.extend(get_hotels_near_landmark(
            connection, 
            landmark['lat'], 
            landmark['lon']
        ))
    
    create_landmark_map(selected_landmarks_info, hotels_near_landmarks)


######################################### tab 3 ###############################################

@st.cache_data
def get_all_cities(_connection):
    query = """
    SELECT DISTINCT city
    FROM `travel-sample`.inventory.hotel
    WHERE geo.lat IS NOT MISSING 
    AND type = "hotel" 
    AND geo.lon IS NOT MISSING
    """
    result = _connection.query(query)
    cities = []
    for row in result:
        cities.append(row["city"])
    return pd.DataFrame(cities, columns=["city"])

@st.cache_data
def get_all_hotels(_connection, cities):
    cities_str = "["
    for i in range(len(cities)):
        if i != len(cities) - 1:
            cities_str += f'"{cities[i]}", '
        else:
            cities_str += f'"{cities[i]}"'
    cities_str += "]"
    query = f"""
    SELECT h.*, geo.lat as lat, geo.lon as lon, ARRAY_AVG(ARRAY r.ratings.Overall FOR r IN h.reviews WHEN r.ratings.Overall IS NOT MISSING END) as avg_rating
    FROM `travel-sample`.inventory.hotel h
    WHERE h.geo.lat IS NOT MISSING 
    AND h.type = "hotel" 
    AND h.geo.lon IS NOT MISSING 
    AND h.city IN {cities_str}
    """
    result = _connection.query(query)
    hotels = []
    for row in result:
        hotels.append(row)
    return pd.DataFrame(hotels)

def create_hotel_map(hotels_df):
    
    if hotels_df.empty:
        fig = go.Figure()
        fig.update_layout(
            mapbox_style="open-street-map",
            margin=dict(l=0, r=0, t=50, b=0),
            title="Hotels (colored by average rating)"
        )
        # Add an invisible marker at lat:0 and lon:0
        fig.add_trace(go.Scattermap(
            lat=[0],
            lon=[0],
            mode='markers',
            marker=dict(size=0, opacity=0)
        ))
        st.plotly_chart(fig, use_container_width=True)
        return
    
    if 'avg_rating' not in hotels_df.columns:
        hotels_df['avg_rating'] = np.nan  # Add avg_rating column if it doesn't exist
    hotels_df['avg_rating'] = pd.to_numeric(hotels_df['avg_rating'], errors='coerce')
    
    # Create a column for star ratings
    hotels_df['star_rating'] = hotels_df['avg_rating'].apply(lambda x: '⭐' * int(round(x)) if not np.isnan(x) else 'No rating')

    # Separate hotels with no rating
    no_rating_hotels = hotels_df[hotels_df['avg_rating'].isna()]
    rated_hotels = hotels_df[hotels_df['avg_rating'].notna()]
    
    # Plot hotels with ratings
    fig = px.scatter_map(
        rated_hotels,
        lat="lat",
        lon="lon",
        hover_name="name",
        hover_data={
            "avg_rating": True,
            "star_rating": True
        },
        color="avg_rating",
        color_continuous_scale=px.colors.sequential.Viridis_r,  # Use Blues color scale
        range_color=[0, 5],  # Ratings typically range from 0 to 5
        zoom=1,
        size_max=10
    )
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Avg Rating: %{customdata[0]:.2f} <br>Stars: %{customdata[1]}"
    )
    
    # Plot hotels with no ratings in black
    no_rating_markers = px.scatter_map(
        no_rating_hotels,
        lat="lat",
        lon="lon",
        hover_name="name",
        hover_data={"avg_rating": False},  # Explicitly state no ratings given
        custom_data=["name"],  # Add custom data to use in hover template
        color_discrete_sequence=["orange"],
        size_max=10
    )
    no_rating_markers.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>No rating available"
    )
    fig.add_traces(no_rating_markers.data)
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=50, b=0),
        title="Hotels (colored by average rating)",
        coloraxis_colorbar=dict(
            title="Avg Rating",
            tickvals=[0, 1, 2, 3, 4, 5],
            ticktext=["0", "1", "2", "3", "4", "5"]
        )
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=50, b=0),
        title="Hotels (colored by average rating)",
        coloraxis_colorbar_title="Avg Rating"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def tab3_visual():
    all_cities = get_all_cities(connection)["city"].tolist()
    cities = st.multiselect("Select cities", all_cities, default=["Newport", "Birmingham", "London"])
    hotels = get_all_hotels(connection, cities)
    create_hotel_map(hotels)
    
######################################### Main #################################################

st.title("Couchbase Streamlit App")

st.sidebar.header("Enter Couchbase Credentials")
conn_str = st.sidebar.text_input("Connection String", "couchbases://your-cluster-url")
username = st.sidebar.text_input("Username", "admin")
password = st.sidebar.text_input("Password", type="password")
bucket_name = st.sidebar.text_input("Bucket Name", "default")
scope_name = st.sidebar.text_input("Scope Name", "_default")
collection_name = st.sidebar.text_input("Collection Name", "_default")

if st.sidebar.button("Connect"):
    try:
        connection = st.connection(
            "couchbase", 
            type=CouchbaseConnector, 
            CONNSTR=conn_str, 
            USERNAME=username, 
            PASSWORD=password,
            BUCKET_NAME=bucket_name, 
            SCOPE_NAME=scope_name, 
            COLLECTION_NAME=collection_name
        )
        st.session_state["connection"] = connection
        st.sidebar.success("Connected successfully!")
    except Exception as e:
        st.sidebar.error(f"Connection failed: {e}")

if "connection" in st.session_state:
    connection = st.session_state["connection"]
    tab1, tab2, tab3 = st.tabs(["Flight Routes Map", "Find hotels near Landmarks", "Find hotel in cities"])
    with tab1:
        tab1_visual()
    with tab2:
        tab2_visual()
    with tab3:
        tab3_visual()