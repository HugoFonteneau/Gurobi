import json
import pandas as pd
import numpy as np
import gurobipy as gp
from gurobipy import GRB

with open("portfolio-example.json", "r") as f:
    data = json.load(f)

n = data["num_assets"]
sigma = np.array(data["covariance"])
mu = np.array(data["expected_return"])
mu_0 = data["target_return"]
k = data["portfolio_max_size"]

with gp.Model("portfolio") as model:
    # Name the modeling objects to retrieve them

    x = model.addVars(n, vtype=GRB.CONTINUOUS, name="x")
    y = model.addVars(n, vtype=GRB.BINARY, name="y")

    quadexpr = 0
    for i in range(n):
        for j in range(n):
            quadexpr += x[i] * sigma[i, j] * x[j]

    model.setObjective(quadexpr, sense=GRB.MINIMIZE)

    model.addConstr(mu_0 <= gp.quicksum(x[i] * mu[i] for i in range(n)), "return")
    model.addConstr(y.sum() <= k, "kactionsMax")
    model.addConstr(x.sum() == 1, "100%invest")
    for i in range(n):
        model.addConstr(x[i] - y[i] <= 0, f"C_{i}")

    model.optimize()

    # Write the solution into a DataFrame
    portfolio = [var.X for var in model.getVars() if "x" in var.VarName]
    risk = model.ObjVal
    expected_return = model.getRow(model.getConstrByName("return")).getValue()
    df = pd.DataFrame(
        data=portfolio + [risk, expected_return],
        index=[f"asset_{i}" for i in range(n)] + ["risk", "return"],
        columns=["Portfolio"],
    )
    print(df)