from gurobipy import *


def optimize(candidates, weights, exclusive_constraints):
    m = Model("model")
    # Comment here to show gurobi output
    m.Params.OutputFlag = 0
    nCand = len(candidates)
    cands = m.addVars([k for k in range(nCand)], vtype=GRB.BINARY)
    for k in range(nCand):
        cands[k].Obj = weights[k]

    m.update()

    for constraint in exclusive_constraints:
        m.addConstr(quicksum([cands[x] for x in constraint]) <= 1)

    m.optimize()

    rois = list()

    for idx in range(nCand):
        if cands[idx].X == 1.0:
            rois.append(candidates[idx])
    return rois
