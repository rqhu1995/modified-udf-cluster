import pandas as pd
import yaml

def load_data(config: dict) -> tuple[dict, dict]:
    # Extract scalar parameters from config
    params = {
        'network_size': config['network_size'],  # |V|
        'num_clusters': config['num_clusters'],  # |C|
        't_load': config['t_load'],
        'T': config['T']
    }

    # Load station data from file (e.g., columns: station_id, s0, c, s_star)
    station_df = pd.read_csv(config['station_data_path'], index_col=None)

    # set the indices of the station data as a explicit column named 'idx'
    station_df['idx'] = [i + 1 for i in station_df.index.tolist()]

    station_df = station_df[['idx'] + [col for col in station_df.columns if col != 'idx']]
    if len(station_df) < params['network_size']:
        raise ValueError("Station data size mismatch with network_size")
    elif len(station_df) > params['network_size']:
        # sample the network from the station_df but preserve the original index
        station_df = sample_stations(params['network_size'], station_df, config['surplus_ratio'], config['deficit_ratio'], config['random_state'])
    # Derive parameter dictionaries keyed by station_id
    params['s^0'] = dict(zip(station_df['idx'], station_df['CurrentInventory']))
    params['s^*'] = dict(zip(station_df['idx'], station_df['Optimal Inventory']))
    
    # Load travel times (e.g., as matrix or dict of dicts)
    params['t_ij'] = pd.read_csv(config['travel_times_path'], header=0, index_col=0).to_numpy()

    transdelta_df = pd.read_csv(config['delta_marginal_path'])
    params['Delta_ij^m'] = transdelta_df.set_index(['from_surplus', 'to_deficit', 'transfers'])['Delta UDF'].to_dict()
    
    max_transfer_idx = transdelta_df.groupby(['from_surplus', 'to_deficit'])['transfers'].idxmax()
    max_transfer_df = transdelta_df.loc[max_transfer_idx].reset_index(drop=True)
    params['U_ij'] = max_transfer_df.set_index(['from_surplus', 'to_deficit'])['transfers'].to_dict()
    print(len(params['Delta_ij^m'].keys()))
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

def sample_stations(network_size: int, station_df: pd.DataFrame, surplus_ratio: float, deficit_ratio: float, random_state: int) -> pd.DataFrame:
    # Separate surplus and deficit stations
    surplus_stations = station_df[station_df['CurrentInventory'] > station_df['Optimal Inventory']]
    deficit_stations = station_df[station_df['CurrentInventory'] < station_df['Optimal Inventory']]
    balanced_stations = station_df[station_df['CurrentInventory'] == station_df['Optimal Inventory']]

    # Calculate the number of stations to sample from each group
    num_surplus = int(network_size * surplus_ratio)
    num_deficit = int(network_size * deficit_ratio)
    num_balanced = network_size - num_surplus - num_deficit

    # Sample stations from each group
    sampled_surplus = surplus_stations.sample(n=num_surplus, random_state=random_state) if not surplus_stations.empty else pd.DataFrame()
    sampled_deficit = deficit_stations.sample(n=num_deficit, random_state=random_state) if not deficit_stations.empty else pd.DataFrame()
    sampled_balanced = balanced_stations.sample(n=num_balanced, random_state=random_state) if not balanced_stations.empty else pd.DataFrame()

    # Combine the sampled stations
    sampled_stations = pd.concat([sampled_surplus, sampled_deficit, sampled_balanced])

    return sampled_stations