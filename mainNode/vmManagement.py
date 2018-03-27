import subprocess

def startVM(id):
	print (id)
	bashCommand = "aws ec2 start-instances --instance-ids " + str(id)
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	output, error = process.communicate()

def stopVM(id):
	print (id)
	bashCommand = "aws ec2 stop-instances --instance-ids " + str(id)
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	output, error = process.communicate()

def migrateCont(contid, srcid, destid):
	#use criu to migrate
	print (contid)
def manage():
	#for cont in containers:
		#check predicted value
		#check current VM capacity
		#if capacity mismatch
	#		startVM(destid)
	#		migrateCont(cont, srcid, destid)
	#		stopVM(srcid)
	startVM("i-046d3a8ec1ca1a3fb")

manage()
