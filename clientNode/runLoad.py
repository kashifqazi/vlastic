import subprocess
import time

def runCont():
	infile = open('/home/ubuntu/vlastic/clientNode/load', 'r')
	for load in infile:
		bashCommand = "stress-ng --vm 1 --vm-bytes " + str(load.rstrip('\n') + " -t 30")
		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
		output, error = process.communicate()
	infile.close()

runCont()
