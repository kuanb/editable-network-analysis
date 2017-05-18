import geopandas as gpd
import matplotlib
import numpy as np
import pandana as pdna
import pandas as pd

# relative path import
from utils.utils import format_pandana_edges_nodes, parse_wkt

# ignore display since using docker vm
matplotlib.use('Agg')
cm = matplotlib.cm
plt = matplotlib.pyplot

# settings
bbox = (-89.566399, 42.984056, -89.229584, 43.171917)

# read in osm data, load into top level variable
osm_edges = pd.read_csv('../osm_edges.csv')
osm_nodes = pd.read_csv('../osm_nodes.csv')

# let's hardcode that we are looking jusr at transit accessibility
travel_speed_km = 4.8 # avg walk speed in kilometers per hour
osm_edges['weight'] = (osm_edges['distance'] / 1000) / travel_speed_km * 60

# prep nodes and edge for pdna
osm_edges, osm_nodes = format_pandana_edges_nodes(osm_edges, osm_nodes)

# read in an example dataset
blocks_df = pd.read_csv('../data/blocks.csv')
geometry = blocks_df['geometry'].map(parse_wkt)
blocks_df = blocks_df.drop('geometry', axis=1)
crs = {'init': 'epsg:4326'}
blocks_gdf = gpd.GeoDataFrame(blocks_df, crs=crs, geometry=geometry)

# we need to extract the point lat/lon values
blocks_gdf['x'] = blocks_gdf.centroid.map(lambda p: p.x)
blocks_gdf['y'] = blocks_gdf.centroid.map(lambda p: p.y)

# now to shift over to pandana's domain
nod_x = osm_nodes['x']
nod_y = osm_nodes['y']

# use the integer representation of each from and to id
# (pandana can't handle them as strings)
edg_fr = osm_edges['from_int']
edg_to = osm_edges['to_int']
edg_wt_df = osm_edges[['weight']]

# insantiate a pandana network object
# set twoway to false since UA networks are oneways
p_net = pdna.Network(nod_x, nod_y, edg_fr, edg_to, edg_wt_df, twoway=False)

#  set node_ids as an attribute on the geodataframe
blocks_gdf['node_ids'] = p_net.get_node_ids(blocks_gdf['x'], blocks_gdf['y'])
p_net.set(blocks_gdf['node_ids'],
          variable=blocks_gdf['emp'],
          name='emp')

for n in [15,30,45,60]:
    s = p_net.aggregate(n, type='sum', decay='flat', imp_name='weight', name='emp')
    s_df = s.to_frame()
    s_df.columns = ['weight']
    s_df['id'] = s_df.index

    # get nodes results attached
    n_df = osm_nodes.copy()
    n_df['id'] = n_df.index

    n_df = pd.merge(n_df, s_df,
                    left_on='id', right_on='id',
                    sort=False, copy=False, how='left')

    # clear out nans
    n_df = n_df[n_df.weight.notnull()]


    fig_height = 20
    x_min, y_min, x_max, y_max = bbox
    bbox_aspect_ratio = (y_max - y_min) / (x_max - x_min)
    fig, ax = plt.subplots(figsize=(fig_height / bbox_aspect_ratio, fig_height))


    # start get colors
    num_bins = 5
    cmap = 'hot'
    # cmap = 'YlOrRd'
    bin_labels = range(5)
    col_values = n_df['weight'].values
    categories = pd.qcut(x=col_values, q=num_bins, labels=bin_labels)
    color_list = [cm.get_cmap(cmap)(x) for x in np.linspace(0.1, 0.9, num_bins)]
    colors = [color_list[cat] for cat in categories]
    # end get colors

    node_size = 1
    ax.scatter(n_df['x'].values, n_df['y'].values, s=node_size, c=colors, alpha=1, zorder=3)
    ax.set_facecolor('black')

    plt.savefig('testplot_' + str(n) + '_min.png', facecolor='black')

