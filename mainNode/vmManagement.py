def startVM(id):
	print id

def stopVM(id):
	print id

def migrateCont(contid, srcid, destid):
	#use criu to migrate

def manage():
	for cont in containers:
		#check predicted value
		#check current VM capacity
		#if capacity mismatch
			startVM(destid)
			migrateCont(cont, srcid, destid)
			stopVM(srcid)
