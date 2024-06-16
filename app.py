import streamlit as st
import osmnx as ox
import overpy
import networkx as nx

# Function to get street description
def get_street_description(lat, lng):
    try:
        st.markdown("<span style='color:gray;'>Downloading street network...</span>", unsafe_allow_html=True)
        G = ox.graph_from_point((lat, lng), dist=500, network_type='all_private', simplify=True)
        st.markdown("<span style='color:gray;'>Street network downloaded.</span>", unsafe_allow_html=True)
        
        st.markdown(f"<span style='color:gray;'>Finding the nearest street segment for point ({lat}, {lng})...</span>", unsafe_allow_html=True)
        nearest_node = ox.distance.nearest_nodes(G, lng, lat)
        st.markdown(f"<span style='color:gray;'>Nearest node found: {nearest_node}</span>", unsafe_allow_html=True)
        
        nearest_edge = ox.distance.nearest_edges(G, lng, lat)
        st.markdown(f"<span style='color:gray;'>Nearest edge found: {nearest_edge}</span>", unsafe_allow_html=True)
        
        u, v, _ = nearest_edge
        
        u_neighbors = list(G.neighbors(u))
        v_neighbors = list(G.neighbors(v))
        
        st.markdown(f"<span style='color:gray;'>Neighbors of node {u}: {u_neighbors}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:gray;'>Neighbors of node {v}: {v_neighbors}</span>", unsafe_allow_html=True)
        
        u_intersections = [G.nodes[n].get('name', 'Unknown') for n in u_neighbors if 'name' in G.nodes[n]]
        v_intersections = [G.nodes[n].get('name', 'Unknown') for n in v_neighbors if 'name' in G.nodes[n]]
        
        st.markdown(f"<span style='color:gray;'>Intersecting streets at node {u}: {u_intersections}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:gray;'>Intersecting streets at node {v}: {v_intersections}</span>", unsafe_allow_html=True)
        
        u_street = G.nodes[u].get('name', 'Unknown')
        v_street = G.nodes[v].get('name', 'Unknown')
        
        st.markdown(f"<span style='color:gray;'>Street name at node {u}: {u_street}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:gray;'>Street name at node {v}: {v_street}</span>", unsafe_allow_html=True)
        
        from_street = u_intersections[0] if u_intersections else 'Unknown'
        to_street = v_intersections[0] if v_intersections else 'Unknown'
        
        description = f"{u_street} between {from_street} and {to_street}"
        st.markdown(f"<span style='color:gray;'>Generated description: {description}</span>", unsafe_allow_html=True)
        
        # Overpass API to find the nearest landmark
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
        
        return description, landmark
    except Exception as e:
        st.markdown(f"<span style='color:gray;'>An error occurred: {e}</span>", unsafe_allow_html=True)
        return "Error: Unable to process the request.", "Unknown"

st.title("Street Description Finder")
st.write("Enter latitude and longitude coordinates to get the street description.")

coords = st.text_input('Coordinates (lat, long)', '40.7217267, -73.9870392')

if st.button('Find Street Description'):
    lat, lng = map(float, coords.split(","))
    description, landmark = get_street_description(lat, lng)
    st.markdown(f"<b style='font-size:20px;'>{description}</b>")
    st.markdown(f"<b style='font-size:20px;'>Nearest landmark: {landmark}</b>")
    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
    st.markdown(f"[Google Maps Link]({google_maps_url})")
