from functools import partial

import gurobipy as gp
from gurobipy import GRB


class CallbackData:
    def __init__(self):
        self.last_gap_change_time = 0
        self.last_gap = GRB.INFINITY


def callback(model, where, *, cbdata):
    if where != GRB.Callback.MIP:
        return
    if model.cbGet(GRB.Callback.MIP_SOLCNT) == 0:
        return

    GAP = abs(model.cbGet(GRB.Callback.MIP_OBJBST) - model.cbGet(GRB.Callback.MIP_OBJBND)) / model.cbGet(GRB.Callback.MIP_OBJBND)

    if (abs(cbdata.last_gap - GAP) < epsilon_to_compare_gap) or (model.cbGet(GRB.Callback.RUNTIME) - cbdata.last_gap_change_time > time_from_best):
        print("GAP : ", cbdata.last_gap - GAP)
        print("TIME : ", model.cbGet(GRB.Callback.RUNTIME) - cbdata.last_gap_change_time)
        model.terminate()
    if GAP != cbdata.last_gap :
        cbdata.last_gap = GAP
        cbdata.last_gap_change_time = model.cbGet(GRB.Callback.RUNTIME)
        return


with gp.read("mkp.mps") as model:
    # Global variables used in the callback function
    time_from_best = 50
    epsilon_to_compare_gap = 1e-4

    # Initialize data passed to the callback function
    callback_data = CallbackData()
    callback_func = partial(callback, cbdata=callback_data)

    model.optimize(callback_func)