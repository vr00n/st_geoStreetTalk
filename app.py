import streamlit as st
import osmnx as ox
import overpy

# Function to get street description
def get_street_description(lat, lng):
    try:
        st.markdown("<span style='color:gray;'>Downloading street network...</span>", unsafe_allow_html=True)
        G = ox.graph_from_point((lat, lng), dist=100, network_type='drive')
        st.markdown("<span style='color:gray;'>Street network downloaded.</span>", unsafe_allow_html=True)
        
        nearest_node = ox.distance.nearest_nodes(G, lng, lat)
        st.markdown(f"<span style='color:gray;'>Nearest node found: {nearest_node}</span>", unsafe_allow_html=True)
        
        u, v, k = ox.distance.nearest_edges(G, lng, lat)
        st.markdown(f"<span style='color:gray;'>Nearest edge found: {(u, v, k)}</span>", unsafe_allow_html=True)
        
        neighbors_u = list(G.neighbors(u))
        neighbors_v = list(G.neighbors(v))
        
        intersecting_streets_u = [G.edges[u, n, 0]['name'] for n in neighbors_u if 'name' in G.edges[u, n, 0]]
        intersecting_streets_v = [G.edges[v, n, 0]['name'] for n in neighbors_v if 'name' in G.edges[v, n, 0]]
        
        to_street = intersecting_streets_u[0] if intersecting_streets_u else "Unknown"
        from_street = intersecting_streets_v[0] if intersecting_streets_v else "Unknown"
        
        street_name_u = G.edges[u, v, k].get('name', 'Unknown')
        street_name_v = G.edges[u, v, k].get('name', 'Unknown')
        
        street_name = street_name_u if street_name_u != 'Unknown' else street_name_v
        description = f"{street_name} between {to_street} and {from_street}"
        
        st.markdown(f"<span style='color:gray;'>Generated description: {description}</span>", unsafe_allow_html=True)
        
        # Find nearest landmark using Overpass API
        description, landmark = find_nearest_landmark(lat, lng)
        return description, landmark

    except Exception as e:
        st.markdown(f"<span style='color:gray;'>An error occurred: {e}</span>", unsafe_allow_html=True)
        return "Error: Unable to process the request.", "Unknown"

# Function to find nearest landmark
def find_nearest_landmark(lat, lng):
    try:
        api = overpy.Overpass()
        query = f"""
        [out:json];
        (
          node(around:100,{lat},{lng})[amenity];
          way(around:100,{lat},{lng})[amenity];
          relation(around:100,{lat},{lng})[amenity];
        );
        out center;
        """
        result = api.query(query)
        
        landmark = "Unknown"
        if result.nodes:
            landmark = result.nodes[0].tags.get('name', 'Unknown')
        elif result.ways:
            landmark = result.ways[0].tags.get('name', 'Unknown')
        elif result.relations:
            landmark = result.relations[0].tags.get('name', 'Unknown')
        
        st.markdown(f"<span style='color:gray;'>Nearest landmark: {landmark}</span>", unsafe_allow_html=True)
        
        return landmark
    
    except Exception as e:
        st.markdown(f"<span style='color:gray;'>An error occurred: {e}</span>", unsafe_allow_html=True)
        return "Unknown"

# Streamlit app layout
st.title("Street Description Finder")
st.write("Enter latitude and longitude coordinates to get the street description.")

coords = st.text_input('Coordinates (lat, long)', '40.78168979595882, -73.9548727701682')

if st.button('Find Street Description'):
    try:
        lat, lng = map(float, coords.split(','))
        description, landmark = get_street_description(lat, lng)
        st.markdown(f"**<span style='font-size: 24px;'>{description}</span>**", unsafe_allow_html=True)
        if landmark != "Unknown":
            st.markdown(f"<span style='color:gray;'>Nearest landmark: {landmark}</span>", unsafe_allow_html=True)
        google_maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        st.markdown(f"[Google Maps Link]({google_maps_link})")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.markdown(f"<span style='color:gray;'>Error: {e}</span>", unsafe_allow_html=True)
