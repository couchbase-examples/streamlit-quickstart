# Couchbase Connector for Streamlit

## 1. Introduction
This project provides a seamless integration between Streamlit and Couchbase, allowing developers to interact with Couchbase databases effortlessly. It enables users to fetch, insert, update, and delete data within Streamlit applications without needing to switch between different SDKs, enhancing the overall development experience.

## 2. Prerequisites
### System Requirements
- **Python 3.10 or higher** ([Check compatibility](https://docs.couchbase.com/python-sdk/current/project-docs/compatibility.html#python-version-compat))
- **Couchbase Capella account** ([Setup Guide](https://docs.couchbase.com/cloud/get-started/intro.html))
- **Operational Couchbase cluster** with configured access ([Instructions](https://docs.couchbase.com/cloud/get-started/connect.html#prerequisites))
- **Connection string** from Couchbase Capella

### Installing Dependencies
To install the required dependencies, run:
```sh
pip install couchbase streamlit couchbase-streamlit-connector
```

## 3. Running the App
1. Clone the repository and install dependencies.
2. Configure the connection details as described above.
3. Run the demo app using:

```sh
git clone https://github.com/Couchbase-Ecosystem/couchbase_streamlit_connector.git
cd ./couchbase_streamlit_connector
pip install -r requirements.txt
pip install plotly geopy numpy
streamlit run src/Demo.py
```
Or access the hosted version: [Demo App](https://couchbase-connector-demo-app.streamlit.app/)


### Cloud Deployment Using Streamlit Community Cloud

1. Fork the [repository](https://github.com/Couchbase-Ecosystem/couchbase_streamlit_connector).
2. Refer to the Streamlit documentation for guidance on deploying your app: [Deploy your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app).
3. Navigate to [Streamlit Community Cloud](https://share.streamlit.io/).
4. Deploy the repository by selecting it and adding the required secrets.

## 4. Couchbase Streamlit Demo Explanation with Code Snippets

This Streamlit application demonstrates how to connect to a Couchbase database and visualize data using interactive maps and charts. It utilizes the `travel-sample` dataset, focusing on airports, routes, landmarks, and hotels.

### Key Features and Code Explanations:

**Connection:**
- Allows users to input Couchbase connection credentials via a sidebar.
- Establishes a connection using `st.connection` and `CouchbaseConnector`.
- **Code Snippet:**

```python
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
```

**Tab 1: Flight Routes Map:**
- Fetches airport and route data from Couchbase using N1QL queries.
- Displays airports as markers on a map and flight routes as lines.
- **Code Snippet:**

```python
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
```

**Tab 2: Find Hotels Near Landmarks:**
- Retrieves landmark and hotel data.
- Calculates distances using `geopy.distance`.
- Displays landmarks and nearby hotels on a map.
- **Code Snippet:**

```python
def get_hotels_near_landmark(_connection, landmark_lat, landmark_lon, max_distance_km=10):
    # ...query hotel data...
    for row in result:
        hotel_coords = (row['lat'], row['lon'])
        landmark_coords = (landmark_lat, landmark_lon)
        distance = geodesic(hotel_coords, landmark_coords).kilometers
        # ...filter hotels by distance...
```

**Tab 3: Find Hotels in Cities:**
- Fetches hotel and city data.
- Displays hotels on a map, color-coded by average rating.
- **Code Snippet:**

```python
def create_hotel_map(hotels_df):
    # ...create plotly scatter map...
    fig = px.scatter_map(
        rated_hotels,
        lat="lat",
        lon="lon",
        color="avg_rating",
        # ...other parameters...
    )
    # ...add non rated hotels...
    st.plotly_chart(fig, use_container_width=True)
```

### Workflow:
1. **Connection:** Users input Couchbase credentials and connect.
2. **Data Retrieval:** The application executes N1QL queries.
3. **Data Processing:** Data is transformed into Pandas DataFrames.
4. **Visualization:** Interactive maps and charts are generated using Plotly.
5. **User Interaction:** Users can select airports, landmarks, and cities to filter the data and update the visualizations.

## Appendix

* **Couchbase Documentation:** [docs.couchbase.com](https://docs.couchbase.com/)
    * Comprehensive documentation for Couchbase products and services.
* **Couchbase Python SDK Documentation:** [docs.couchbase.com/python-sdk/current/](https://docs.couchbase.com/python-sdk/current/hello-world/start-using-sdk.html)
    * Detailed information on using the Couchbase Python SDK.
* **Streamlit Documentation:** [docs.streamlit.io](https://docs.streamlit.io/)
    * Official documentation for Streamlit, including API references and tutorials.
* **Streamlit Community Cloud:** [share.streamlit.io](https://share.streamlit.io/)
    * Platform for deploying and sharing Streamlit applications.
* **Geopy Documentation:** [geopy.readthedocs.io](https://geopy.readthedocs.io/en/stable/)
    * Python Geocoding Toolbox.
* **Plotly Documentation:** [plotly.com/python/](https://plotly.com/python/)
    * Python graphing library.
