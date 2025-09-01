from gurobipy import GRB, Model

def solve_model(model: Model, config: dict) -> dict:
    model.setParam('TimeLimit', config['time_limit'])
    model.optimize()
    if model.status == GRB.OPTIMAL:
        return {v.VarName: v.X for v in model.getVars()}
    else:
        raise ValueError("No optimal solution found")