import yaml
from src.data_loader import load_data
from src.model_builder import MILPModel
from src.optimizer import solve_model
from src.post_processor import process_solution, visualize_results

if __name__ == "__main__":
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    sets, params, station_df = load_data(config)
    milp = MILPModel(sets, params)
    solution = solve_model(milp.model, config)
    results = process_solution(solution, params)
    print(results)
    visualize_results(results, station_df)  # Uncomment to visualize results
