import matplotlib.pyplot as plt
import pandas as pd


def process_solution(solution: dict, params: dict) -> dict:
    # Compute totals or statistics
    total = sum(solution.values())
    # Save to file
    with open("data/results/output.csv", "w") as f:
        # Write data
        cluster = dict()
        transfer = dict()
        for key, value in solution.items():
            # a. filter the clustering results
            if "z" in str(key) and int(value) > 0.5:
                station_id, cluster_id = (
                    key.replace("z[", "").replace("]", "").split(",")
                )
                if cluster_id not in cluster:
                    cluster[cluster_id] = [station_id]
                else:
                    cluster[cluster_id].append(station_id)
            elif "x" in str(key) and int(value) > 0.5:
                from_station, to_station, cluster_id_transfer, transfer_quantity = [
                    int(x) for x in key.replace("x[", "").replace("]", "").split(",")
                ]
                print(from_station, to_station, cluster_id_transfer, transfer_quantity)
                if cluster_id_transfer not in transfer:
                    transfer[cluster_id_transfer] = dict()
                if (from_station, to_station) not in transfer[cluster_id_transfer]:
                    transfer[cluster_id_transfer][(from_station, to_station)] = (
                        transfer_quantity
                    )
                else:
                    transfer[cluster_id_transfer][(from_station, to_station)] = max(
                        transfer[cluster_id_transfer][(from_station, to_station)],
                        transfer_quantity,
                    )
            # write the whole solution into csv
            f.write(f"{key},{value}\n")
    return {"total": total, "cluster": cluster, "transfer": transfer}


def visualize_results(results: dict, station_df: pd.DataFrame) -> None:
    print(station_df)
    fig, ax = plt.subplots()
    colors = ["red", "green", "orange"]
    # Visualize clustering results
    for cluster_id, stations in results["cluster"].items():
        for station in stations:
            lat, lon = station_df.loc[
                station_df["idx"] == int(station), ["Latitude", "Longitude"]
            ].values[0]
            ax.scatter(
                lon,
                lat,
                label=f"Cluster {cluster_id}",
                color=colors[int(cluster_id) - 1],
            )
    plt.savefig("data/results/clustering_results.png")
