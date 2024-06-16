import streamlit as st
import osmnx as ox
import overpy
from streamlit.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Function to get street description
def get_street_description(lat, lng):
    logger.info("Downloading street network...")
    G = ox.graph_from_point((lat, lng), dist=100, network_type='drive')
    logger.info("Street network downloaded.")
    
    nearest_node = ox.distance.nearest_nodes(G, lng, lat)
    logger.info(f"Nearest node found: {nearest_node}")
    
    u, v, k = ox.distance.nearest_edges(G, lng, lat)
    logger.info(f"Nearest edge found: {(u, v, k)}")
    
    neighbors_u = list(G.neighbors(u))
    neighbors_v = list(G.neighbors(v))
    
    intersecting_streets_u = [G.edges[u, n, 0]['name'] for n in neighbors_u if 'name' in G.edges[u, n, 0]]
    intersecting_streets_v = [G.edges[v, n, 0]['name'] for n in neighbors_v if 'name' in G.edges[v, n, 0]]
    
    to_street = intersecting_streets_u[0] if intersecting_streets_u else "Unknown"
    from_street = intersecting_streets_v[0] if intersecting_streets_v else "Unknown"
    
    # Find the street name of the nearest edge
    street_name_u = G.edges[u, v, k].get('name', 'Unknown')
    street_name_v = G.edges[u, v, k].get('name', 'Unknown')
    
    # Determine the description
    street_name = street_name_u if street_name_u != 'Unknown' else street_name_v
    description = f"{street_name} between {to_street} and {from_street}"
    
    logger.info(f"Generated description: {description}")
    
    # Use Overpass API to find the nearest landmark
    api = overpy.Overpass()
    query = f"""
    [out:json];
    node(around:50,{lat},{lng})[amenity];
    out body;
    """
    result = api.query(query)
    
    nearest_landmark = "Unknown"
    if result.nodes:
        nearest_landmark = result.nodes[0].tags.get('name', 'Unknown')
        logger.info(f"Nearest landmark found: {nearest_landmark}")
    
    description = f"{description}. Nearest landmark: {nearest_landmark}"
    
    return description

# Streamlit app layout
st.title("Street Description Finder")
st.write("Enter latitude and longitude coordinates to get the street description.")

coords = st.text_input('Coordinates (lat, long)', '40.78168979595882, -73.9548727701682')

if st.button('Find Street Description'):
    try:
        lat, lng = map(float, coords.split(','))
        description = get_street_description(lat, lng)
        st.write(f"**{description}**")
        google_maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        st.markdown(f"[Google Maps Link]({google_maps_link})")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logger.error(f"Error: {e}")
