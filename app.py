import streamlit as st
import osmnx as ox
import networkx as nx
from shapely.geometry import Point
import geopandas as gpd

def get_street_description(lat, lng):
    try:
        # Download the street network
        st.write("Downloading street network...")
        G = ox.graph_from_point((lat, lng), dist=500, network_type='drive')
        st.write("Street network downloaded.")

        # Find the nearest street segment
        st.write(f"Finding the nearest street segment for point ({lat}, {lng})...")
        point = (lat, lng)
        nearest_node = ox.distance.nearest_nodes(G, lng, lat)
        st.write(f"Nearest node found: {nearest_node}")

        # Find the nearest edge
        u, v, key = list(G.edges(nearest_node, keys=True))[0]
        st.write(f"Nearest edge found: ({u}, {v}, {key})")

        # Get intersecting streets at each node
        def get_intersecting_streets(G, node):
            intersecting_streets = []
            for neighbor in G.neighbors(node):
                edge_data = G.get_edge_data(node, neighbor)
                for key in edge_data:
                    street_name = edge_data[key].get('name')
                    if street_name:
                        intersecting_streets.append(street_name if isinstance(street_name, str) else street_name[0])
            return list(set(intersecting_streets))

        neighbors_u = list(G.neighbors(u))
        neighbors_v = list(G.neighbors(v))
        st.write(f"Neighbors of node {u}: {neighbors_u}")
        st.write(f"Neighbors of node {v}: {neighbors_v}")

        streets_at_u = get_intersecting_streets(G, u)
        streets_at_v = get_intersecting_streets(G, v)
        st.write(f"Intersecting streets at node {u}: {streets_at_u}")
        st.write(f"Intersecting streets at node {v}: {streets_at_v}")

        # Determine the to/from streets
        if streets_at_u and streets_at_v:
            from_street = streets_at_u[0] if streets_at_u[0] != streets_at_v[0] else (streets_at_u[1] if len(streets_at_u) > 1 else "Unknown")
            to_street = streets_at_v[0] if streets_at_v[0] != streets_at_u[0] else (streets_at_v[1] if len(streets_at_v) > 1 else "Unknown")
        else:
            from_street = "Unknown"
            to_street = "Unknown"

        main_street = G.edges[u, v, key].get('name', 'Unknown')

        return f"{main_street} between {from_street} and {to_street}"
    
    except ImportError as e:
        st.write("An error occurred while importing necessary modules. Please ensure OSMnx and its dependencies are installed.")
        st.write(str(e))
        return "Error: Unable to process the request due to import issues."

    except Exception as e:
        st.write("An error occurred while processing the request.")
        st.write(str(e))
        return "Error: Unable to process the request."

# Streamlit app layout
st.title('Street Description Finder')
st.write('Enter latitude and longitude coordinates to get the street description in the format "lat, long".')

lat = st.number_input('Latitude', value=40.7217267)
lng = st.number_input('Longitude', value=-73.9870392)

if st.button('Find Street Description'):
    description = get_street_description(lat, lng)
    st.write(description)
