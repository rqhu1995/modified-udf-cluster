from gurobipy import Model, GRB, quicksum

class MILPModel:
    def __init__(self, sets: dict, params: dict):
        self.model = Model("milp_problem")
        self.x = self._add_x_variables(sets, params)
        self.z = self._add_z_variables(sets)
        self._set_objective(sets, params)
        self._add_constraints(sets, params)

    def _add_x_variables(self, sets, params):
        U = params['U_ij']
        indices = [(i, j, v, m) for i in sets['V^+'] for j in sets['V^-']
                for v in sets['C'] for m in range(1, U.get((i, j), 0) + 1)]
        return self.model.addVars(indices, vtype=GRB.BINARY, name="x")

    def _add_z_variables(self, sets):
        indices = [(i, v) for i in sets['V'] for v in sets['C']]
        return self.model.addVars(indices, vtype=GRB.BINARY, name="z")

    def _set_objective(self, sets, params):
        U = params['U_ij']
        indices = [(i, j, v, m) for i in sets['V^+'] for j in sets['V^-']
                for v in sets['C'] for m in range(1, U.get((i, j), 0) + 1)]
        obj = quicksum(params['Delta_ij^m'] * self.x[i, j, v, m] for (i, j, v, m) in indices)
        self.model.setObjective(obj, GRB.MAXIMIZE)

    def _add_constraints(self, sets, params):
        # eq (3) one station in exactly one cluster
        self.model.addConstrs(quicksum(self.z[i, v] for v in sets['C']) == 1 for i in sets['V'])
        # eq (4) surplus station i only in cluster v would transfer of ijvm happen
        self.model.addConstrs(self.x[i, j, v, m] <= self.z[i, v] for i in sets['V^+'] for j in sets['V^-']
                              for v in sets['C'] for m in range(1, params['U_ij'].get((i, j), 0) + 1))
        # eq (5) eq (4) another version for deficit station j
        self.model.addConstrs(self.x[i, j, v, m] <= self.z[j, v] for i in sets['V^+'] for j in sets['V^-']
                              for v in sets['C'] for m in range(1, params['U_ij'].get((i, j), 0) + 1))
        # eq (6) transfer at a surplus station to deficit j capped by the station i's surplus
        self.model.addConstrs(quicksum(self.x[i, j, v, m] for j in sets['V^-'] for v in sets['C'] for m in range(1, params['U_ij'].get((i, j), 0) + 1)) <= (params['s^0'] - params['s^*']) for i in sets['V^+'])
        # eq (7) transfer at a deficit station from surplus i capped by the station j's deficit
        self.model.addConstrs(quicksum(self.x[i, j, v, m] for i in sets['V^+'] for v in sets['C'] for m in range(1, params['U_ij'].get((i, j), 0) + 1)) <= (params['s^*'] - params['s^0']) for j in sets['V^-'])
        # eq(8) total time of each cluster less and equal to loading time plus the maximum spanning star estimation
        self.model.addConstrs(
            quicksum(params['t_load'] * self.x[i, j, v, m] for i in sets['V^+'] for j in sets['V^-']
                      for m in range(1, params['U_ij'].get((i, j), 0) + 1)) + quicksum(params['t_ij'][i,k] * self.z[k, v] for i in sets['V^+']) <= params['T'] + params['B'][k] * (1 - self.z[k, v]) for k in sets['V'] for v in sets['C'])
        # eq(9) if m transfer is not conducted, then m+1 should also not be conducted
        self.model.addConstrs(self.x[i, j, v, m] >= self.x[i, j, v, m + 1] for i in sets['V^+'] for j in sets['V^-'] for v in sets['C'] for m in range(0, params['U_ij'].get((i, j), 0) - 1))