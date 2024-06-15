import streamlit as st
import osmnx as ox
import random

def get_street_description(lat, lng):
    try:
        st.markdown("<span style='color:gray;'>Downloading street network...</span>", unsafe_allow_html=True)
        G = ox.graph_from_point((lat, lng), dist=500, network_type='drive')
        st.markdown("<span style='color:gray;'>Street network downloaded.</span>", unsafe_allow_html=True)

        st.markdown(f"<span style='color:gray;'>Finding the nearest street segment for point ({lat}, {lng})...</span>", unsafe_allow_html=True)
        nearest_node = ox.distance.nearest_nodes(G, lng, lat)
        st.markdown(f"<span style='color:gray;'>Nearest node found: {nearest_node}</span>", unsafe_allow_html=True)

        edges = list(G.edges(nearest_node, keys=True, data=True))
        u, v, key, data = edges[0]
        st.markdown(f"<span style='color:gray;'>Nearest edge found: ({u}, {v}, {key})</span>", unsafe_allow_html=True)

        def get_intersecting_streets(G, node):
            intersecting_streets = []
            for neighbor in G.neighbors(node):
                edge_data = G.get_edge_data(node, neighbor)
                for key in edge_data:
                    street_name = edge_data[key].get('name')
                    if street_name:
                        intersecting_streets.append(street_name if isinstance(street_name, str) else street_name[0])
            return list(set(intersecting_streets))

        streets_at_u = get_intersecting_streets(G, u)
        streets_at_v = get_intersecting_streets(G, v)
        st.markdown(f"<span style='color:gray;'>Intersecting streets at node {u}: {streets_at_u}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:gray;'>Intersecting streets at node {v}: {streets_at_v}</span>", unsafe_allow_html=True)

        if streets_at_u and streets_at_v:
            from_street = streets_at_u[0] if streets_at_u[0] != streets_at_v[0] else (streets_at_u[1] if len(streets_at_u) > 1 else "Unknown")
            to_street = streets_at_v[0] if streets_at_v[0] != streets_at_u[0] else (streets_at_v[1] if len(streets_at_v) > 1 else "Unknown")
        else:
            from_street = "Unknown"
            to_street = "Unknown"

        main_street = data.get('name', 'Unknown')

        return f"**<span style='font-size:20px;'>{main_street} between {from_street} and {to_street}</span>**"
    
    except ImportError as e:
        st.markdown("<span style='color:gray;'>An error occurred while importing necessary modules. Please ensure OSMnx and its dependencies are installed.</span>", unsafe_allow_html=True)
        st.write(str(e))
        return "<span style='color:red;'>Error: Unable to process the request due to import issues.</span>"

    except Exception as e:
        st.markdown("<span style='color:gray;'>An error occurred while processing the request.</span>", unsafe_allow_html=True)
        st.write(str(e))
        return "<span style='color:red;'>Error: Unable to process the request.</span>"

st.title('Street Description Finder')
st.write('Enter latitude and longitude coordinates to get the street description.')

coords = st.text_input('Coordinates (lat, long)', '40.74877458772793, -73.98536222939242')
coords = coords.split(',')

try:
    lat = float(coords[0].strip())
    lng = float(coords[1].strip())
except:
    st.write("Please enter valid coordinates.")

if st.button('Find Street Description'):
    description = get_street_description(lat, lng)
    st.markdown(description, unsafe_allow_html=True)
