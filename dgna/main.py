import geopandas as gpd
import networkx as nx
import networkx as nx
import numpy as np
import pandas as pd

# relative path import
from utils import format_blocks_as_gdf, format_edges_nodes_as_gdfs, parse_wkt

# read in osm data, load into top level variable
osm_edges = pd.read_csv('./data/osm_edges.csv')
osm_nodes = pd.read_csv('./data/osm_nodes.csv')

# let's hardcode that we are looking jusr at transit accessibility
travel_speed_km = 4.8 # avg walk speed in kilometers per hour
osm_edges['weight'] = (osm_edges['distance'] / 1000) / travel_speed_km * 60

# prep nodes and edge for pdna
osm_edges, osm_nodes = format_edges_nodes_as_gdfs(osm_edges, osm_nodes)

print(osm_nodes.x.max())
print(osm_nodes.y.max())

print(osm_nodes.x.min())
print(osm_nodes.y.min())

# read in an example dataset
blocks_df = pd.read_csv('./data/blocks.csv')
blocks_gdf = format_blocks_as_gdf(blocks_df)

# initalize the graph
G=nx.DiGraph()

G.add_nodes_from(osm_nodes.id.values)

for _, edge in osm_edges.iterrows():
    G.add_edge(edge.from_int, edge.to_int, weight=edge.weight)

print('calc all_pairs_dijkstra_path')
k = nx.all_pairs_dijkstra_path(G, 60)

print(k)