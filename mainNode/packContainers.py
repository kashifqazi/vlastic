from pulp import *


def packCont (clist, vdict):
	items = clist
	itemCount = len(items)
	maxBins = 5
	binNames = []
	binCapacity = []
	binCost = []
	for bin in vdict:
		binNames.append(bin)
		binCapacity.append(vdict[bin])
		binCost.append(vdict[bin]/512)
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

	outfile = open('/home/ubuntu/vlastic/mainNode/contMapping', 'w')
	for i in x.keys():
    		if x[i].value() == 1:
        		#print("Item {} is packed in bin {}.".format(*i))
			print("Item " + str(i[0]) + " in bin " + str(binNames[i[1]]) + " with capacity " + str(binCapacity[i[1]]))
			outfile.write(str(i[0]) + "," + str(binNames[i[1]]) + '\n')
	outfile.close()



def getContFuture():
	infile = open('/home/ubuntu/vlastic/mainNode/predictedLoad' ,'r')
	cl = []
	for line in infile:
		temp = line.rstrip('\n').split(',')
		cl.append((temp[0], int(temp[1])))
	infile.close()

	return cl

def getVMList():
	infile = open('/home/ubuntu/vlastic/mainNode/vmList' ,'r')
	vli = {}
	for line in infile:
		temp = line.rstrip('\n').split(',')
		vli[temp[0]] = int(temp[1])
	infile.close()
	return vli

cli = getContFuture()
vli = getVMList()
packCont(cli, vli)
