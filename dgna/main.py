import geopandas as gpd
import networkx as nx
import networkx as nx
import numpy as np
import pandas as pd
from pyproj import Proj, transform
from shapely.geometry import box

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

# read in an example dataset
blocks_df = pd.read_csv('./data/blocks.csv')
blocks_gdf = format_blocks_as_gdf(blocks_df)

# initalize the graph, load in original osm walk matrix
G=nx.DiGraph()

G.add_nodes_from(osm_nodes.id.values)

for _, edge in osm_edges.iterrows():
    G.add_edge(edge.from_int, edge.to_int, weight=edge.weight)

# reproject the matrix to madison specific, meter units
inProj = Proj(init='epsg:4326')
outProj = Proj(init='epsg:3070')

x_min, y_min = osm_nodes.x.min(), osm_nodes.y.min()
x_max, y_max = osm_nodes.x.max(), osm_nodes.y.max()

x2_min, y2_min = transform(inProj, outProj, x_min, y_min)
x2_max, y2_max = transform(inProj, outProj, x_max, y_max)

# now establish the grid over the area, at 200 meter accuracy
grid_width = 200
grid_height = 200

# figure out how many rows, how many columns
rows = ceil((y2_max - y2_min) / grid_height)
cols = ceil((x2_max - x2_min) / grid_width)

all_cols = []
for col in range(cols):
    grid_x_left = x2_min + (col * grid_width)
    grid_x_right = x2_min + ((col + 1) * grid_width)
    
    current_col = {
        'cells': [],
        'x_left': grid_x_left,
        'x_right': grid_x_right
    }

    for row in range(rows):
        grid_y_top = y2_max - (row * grid_height)
        grid_y_bottom = y2_max - ((row + 1) * grid_height)

        new_grid_square = box(grid_x_left, grid_x_left, grid_x_right, grid_y_top)

        # add to current col being built
        current_col['cells'].append(new_grid_square)

    all_cols.append(current_col)



print('calc all_pairs_dijkstra_path')
k = nx.all_pairs_dijkstra_path(G, 60)


print(k)