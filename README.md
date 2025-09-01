# Modified UDF Cluster Optimization

This project implements a Mixed Integer Linear Programming (MILP) model for optimizing inventory redistribution in a bike-sharing or similar station network. It focuses on minimizing costs associated with transferring items between surplus and deficit stations, incorporating user-defined functions (UDF) for marginal costs and considering travel times and clustering constraints.

## Features

- **Data Loading**: Loads station data, travel times, and precomputed delta UDF marginal values from CSV files.
- **MILP Model Building**: Constructs an optimization model using station inventories, optimal levels, and transfer costs.
- **Optimization**: Solves the MILP problem to find optimal transfer strategies.
- **Post-Processing**: Processes the solution to extract actionable results.
- **Configurable**: Uses YAML configuration for easy parameter tuning.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd modified-udf-cluster
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Note: You may need to install an MILP solver like Gurobi or PuLP separately, depending on the optimizer module implementation.

## Usage

1. Prepare your data files in the `data/` directory:
   - `station_data.csv`: Station information including current and optimal inventories.
   - `duration_matrix.csv`: Travel times between stations.
   - `delta_udf_marginal.csv`: Precomputed marginal UDF values for transfers.

2. Configure parameters in `config/config.yaml`:
   ```yaml
   data_path: 'config/config.yaml'
   network_size: 100
   num_clusters: 5
   t_load: 10
   T: 480
   ```

3. Run the main script:
   ```bash
   python main.py
   ```

4. For data generation, use the Jupyter notebook:
   ```bash
   jupyter notebook generate_delta.ipynb
   ```

## Project Structure

```
.
├── config/
│   └── config.yaml          # Configuration parameters
├── data/
│   ├── station_data.csv     # Station inventory data
│   ├── duration_matrix.csv  # Travel time matrix
│   └── delta_udf_marginal.csv # Marginal UDF data
├── src/
│   ├── data_loader.py       # Data loading utilities
│   ├── model_builder.py     # MILP model construction
│   ├── optimizer.py         # Optimization solver
│   ├── post_processor.py    # Solution processing
│   └── utils.py             # Helper functions
├── tests/                   # Unit tests
├── generate_delta.ipynb     # Notebook for generating delta UDF data
├── main.py                  # Main entry point
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Add tests if applicable.
5. Submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.