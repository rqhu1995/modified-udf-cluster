def process_solution(solution: dict, params: dict) -> dict:
    # Compute totals or statistics
    total = sum(solution.values())
    # Save to file
    with open('results/output.csv', 'w') as f:
        # Write data
        for key, value in solution.items():
            f.write(f"{key},{value}\n")
    return {'total': total}