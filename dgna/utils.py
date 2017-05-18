import pandas as pd
from shapely import wkt

def format_pandana_edges_nodes(edge_df, node_df):
    node_df['id_int'] = range(1, len(node_df.index) + 1)

    with_from_int = pd.merge(edge_df,
                             node_df[['id','id_int']],
                             left_on='from',
                             right_on='id',
                             sort=False,
                             copy=False,
                             how='left')
    
    with_from_int['from_int'] = with_from_int['id_int']
    with_from_int.drop(['id_int','id'], axis=1, inplace=True)

    with_both_int = pd.merge(with_from_int,
                             node_df[['id','id_int']],
                             left_on='to',
                             right_on='id',
                             sort=False,
                             copy=False,
                             how='left')
    
    with_both_int['to_int'] = with_both_int['id_int']
    with_both_int.drop(['id_int','id'], axis=1, inplace=True)
    
    # turn mixed dtype cols into all same format
    col_list = with_both_int.select_dtypes(include=['object']).columns
    for col in col_list:
        with_both_int[col] = with_both_int[col].astype(str)

    node_df.set_index('id_int', drop=True, inplace=True)
    # turn mixed dtype col into all same format
    node_df['id'] = node_df['id'].astype(str)
    node_df = node_df[['id', 'x', 'y']]

    return with_both_int, node_df

def parse_wkt(s):
    if s.startswith('SRID'):
        s = s[s.index(';') + 1:]
    return wkt.loads(s)
