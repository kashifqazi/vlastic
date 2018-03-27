from pulp import *

items = [("a", 500), ("b", 500), ("c", 500), ("d", 24)]

itemCount = len(items)
maxBins = 7
binCapacity = [512, 512, 512, 512, 1024, 1024, 1024]
binCost = [1, 1, 1, 1, 2, 2, 2]

y = pulp.LpVariable.dicts('BinUsed', range(maxBins), lowBound = 0, upBound = 1, cat = pulp.LpInteger)
possible_ItemInBin = [(itemTuple[0], binNum) for itemTuple in items for binNum in range(maxBins)]
x = pulp.LpVariable.dicts('itemInBin', possible_ItemInBin, lowBound = 0, upBound = 1, cat = pulp.LpInteger)

# Model formulation
prob = LpProblem("Bin Packing Problem", LpMinimize)

# Objective
prob += lpSum([binCost[i] * y[i] for i in range(maxBins)])

# Constraints
for j in items:
    prob += lpSum([x[(j[0], i)] for i in range(maxBins)]) == 1
for i in range(maxBins):
    prob += lpSum([items[j][1] * x[(items[j][0], i)] for j in range(itemCount)]) <= binCapacity[i]*y[i]
prob.solve()

print("Bins used: " + str(sum(([y[i].value() for i in range(maxBins)]))))
for i in x.keys():
    if x[i].value() == 1:
        print("Item {} is packed in bin {}.".format(*i))
