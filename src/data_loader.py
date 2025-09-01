import pandas as pd
import yaml

def load_data(config_path: str) -> tuple[dict, dict]:
    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Extract scalar parameters from config
    params = {
        'network_size': config['network_size'],  # |V|
        'num_clusters': config['num_clusters'],  # |C|
        't_load': config['t_load'],
        'T': config['T']
    }

    # Load station data from file (e.g., columns: station_id, s0, c, s_star)
    station_df = pd.read_csv('data/station_data.csv', index_col=None)

    # set the indices of the station data as a explicit column named 'idx'
    station_df['idx'] = [i + 1 for i in station_df.index.tolist()]

    station_df = station_df[['idx'] + [col for col in station_df.columns if col != 'idx']]
    if len(station_df) != params['network_size']:
        raise ValueError("Station data size mismatch with network_size")
    
    # Derive parameter dictionaries keyed by station_id
    params['s^0'] = dict(zip(station_df['idx'], station_df['CurrentInventory']))
    params['s^*'] = dict(zip(station_df['idx'], station_df['Optimal Inventory']))
    
    # Load travel times (e.g., as matrix or dict of dicts)
    params['t_ij'] = pd.read_csv('data/duration_matrix.csv', header=0, index_col=0).to_numpy()
    
    transdelta_df = pd.read_csv("data/delta_udf_marginal.csv")
    max_transfer_idx = transdelta_df.groupby(['from_surplus', 'to_deficit'])['transfers'].idxmax()
    max_transfer_df = transdelta_df.loc[max_transfer_idx].reset_index(drop=True)
    params['U_ij'] = max_transfer_df.set_index(['from_surplus', 'to_deficit'])['transfers'].to_dict()
    params['Delta_ij^m'] = max_transfer_df.set_index(['from_surplus', 'to_deficit', 'transfers'])['Delta UDF'].to_dict()

    # Construct sets as lists
    sets = {
        'V': sorted(params['s^0'].keys()),  # Use keys from data; assumes 1 to network_size
        'C': list(range(1, params['num_clusters'] + 1)),
    }
    sets['V^+'] = [i for i in sets['V'] if params['s^0'][i] > params['s^*'][i]]
    sets['V^-'] = [i for i in sets['V'] if params['s^0'][i] < params['s^*'][i]]
    sets['V_0'] = [0] + sets['V']  # Including depot as node 0

    dict_B = {j: sum(params['t_ij'][i, j] for i in sets['V']) for j in sets['V']}
    
    params['B'] = dict_B
    
    # Additional validation
    if not sets['V^+'] or not sets['V^-']:
        raise ValueError("No surplus or deficit stations found")
    
    return sets, params