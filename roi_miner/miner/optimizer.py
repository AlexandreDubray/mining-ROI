from gurobipy import *

def _compute_sol(candidates, weights, overlaps):
    m = Model("model")
    # Comment here to show gurobi output
    m.Params.OutputFlag = 0
    nCand = len(candidates)
    cands = m.addVars([k for k in range(nCand)], vtype=GRB.BINARY)
    for k in range(nCand):
        cands[k].Obj = weights[k]

    m.update()

    for overlap_idx in overlaps:
        m.addConstr(quicksum([cands[x] for x in overlap_idx]) <= 1)

    m.optimize()

    rois_idx = list()

    for idx in range(nCand):
        if cands[idx].X == 1.0:
            rois_idx.append(idx)
    return rois_idx

def optimize(regions, weights, overlaps):
    return _compute_sol(regions, weights, overlaps)
