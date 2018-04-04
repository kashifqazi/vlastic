import subprocess
import os
import paramiko
import time
from pulp import *


def packCont (clist, vdict):
        items = clist
        itemCount = len(items)
        maxBins = 0
        binNames = []
        binCapacity = []
        binCost = []
        for bin in vdict:
                binNames.append(bin)
                binCapacity.append(vdict[bin])
                binCost.append(vdict[bin]/512)
        maxBins = len(binNames)
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
	srcIP = getIP(srcid)
	dstIP = getIP(destid)
	clientsrc = paramiko.SSHClient()
	clientsrc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	clientsrc.connect(srcIP, username='ubuntu', key_filename='/home/ubuntu/vlastic/docker2.pem')

	clientdst = paramiko.SSHClient()
        clientdst.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        clientdst.connect(dstIP.rstrip('\n'), username='ubuntu', key_filename='/home/ubuntu/vlastic/docker2.pem')

	transport = clientdst.get_transport()
	channel = transport.open_session()


	stdin, stdout, stderr = clientsrc.exec_command("sudo criu dump --tree " + contid + " --images-dir /home/ubuntu/imagedump --leave-stopped --shell-job")
	for line in stderr:
		print(line.rstrip('\n'))
	print(dstIP)

	stdin, stdout, stderr = clientsrc.exec_command("scp -i /home/ubuntu/docker2.pem /home/ubuntu/imagedump/* ubuntu@" + dstIP.rstrip('\n') + ":/home/ubuntu/imagedump/")
	for line in stderr:
		print(line.rstrip('\n'))

	channel.exec_command("sudo criu restore --tree " + contid + " --images-dir /home/ubuntu/imagedump")
	#for line in stdout:
	#	print(line.rstrip('\n'))

	clientsrc.close()
	clientdst.close()


	#bashCommand = "sudo ssh -i /home/ubuntu/vlastic/docker2.pem ubuntu@" + srcIP + " \'sudo criu dump --tree " + contid + " --images-dir /home/ubuntu/imagedump --leave-stopped --shell-job\'"
	#process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
	#output, error = process.communicate()
	#aws ssm send-command --document-name "AWS-RunPowerShellScript" --parameters commands=["echo helloWorld"] --targets "Key=instanceids,Values=i-0cb2b964d3e14fd9f"


def killContainer(cont, srcid):

	srcIP = getIP(srcid)
        clientsrc = paramiko.SSHClient()
        clientsrc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        clientsrc.connect(srcIP, username='ubuntu', key_filename='/home/ubuntu/vlastic/docker2.pem')
	stdin, stdout, stderr = clientsrc.exec_command("sudo kill -9 " + cont)
        for line in stderr:
                print(line.rstrip('\n'))
	clientsrc.close()

def getIP(id):

	bashCommand = "aws ec2 describe-instances --filters Name=instance-id,Values=" + str(id) + " --query Reservations[*].Instances[*].[PublicIpAddress] --output=text"
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
	#output = os.system(bashCommand)
	return output

def getOffOnMapping():
	vms = open('/home/ubuntu/vlastic/mainNode/vmList', 'r')
	conts = open('/home/ubuntu/vlastic/mainNode/contMapping' ,'r')

	vml = vms.readlines()
	conl = conts.readlines()

	vms.close()
	conts.close()

	vmsturnon = []
	vmsturnoff = []
	vmsneeded = []
	vmsoff = []
	vmson = []

	vmsizes = {}
	vmstats = {}

	cmapping = {}

	for c in conl:
		tmp = c.rstrip('\n').split(',')
		cmapping[tmp[0]] = tmp[1]
		if tmp[1] not in vmsneeded:
			vmsneeded.append(tmp[1])
	for v in vml:
		tmp = v.rstrip('\n').split(',')
		vmsizes[tmp[0]] = tmp[1]
		vmstats[tmp[0]] = tmp[2]
		if tmp[2] == "false":
			vmsoff.append(tmp[0])
		else:
			vmson.append(tmp[0])
	for v in vmsneeded:
		if v in vmsoff:
			vmsturnon.append(v)
			vmstats[v] = "true"

	for v in vmson:
		if v not in vmsneeded:
			vmsturnoff.append(v)
			vmstats[v] = "false"

	outfile = open('/home/ubuntu/vlastic/mainNode/vmList' ,'w')
	for v in vmstats.keys():
		outfile.write(v + ',' + vmsizes[v] + ',' + vmstats[v] + '\n')
	outfile.close()

	return vmsturnon,vmsturnoff,cmapping


def getCurrentContMap():

	infile = open('/home/ubuntu/vlastic/mainNode/containerList' ,'r')
	contmap = {}
	for line in infile:
		tmp = line.rstrip('\n').split(',')
		contmap[tmp[0]] = tmp[1]
	infile.close()

	return contmap


def copyFileContents(inf, outf):

	infile = open(inf, 'r')
	outfile = open(outf, 'w')

	for line in infile:
		outfile.write(line.rstrip('\n') + '\n')
	infile.close()
	outfile.close()

def predict():

	infile = open('/home/ubuntu/vlastic/mainNode/predictedLoad', 'r')
	loads = infile.readlines()
	infile.close()

	outfile = open('/home/ubuntu/vlastic/mainNode/predictedLoad', 'w')
	for l in loads:
		print l
		tmp = l.rstrip('\n').split(',')
		if tmp[1] == '200':
			outfile.write(tmp[0]+',500\n')
		else:
			outfile.write(tmp[0]+',200\n')
	outfile.close()

def recordLogs(cm):

	# Format of log file
	# timestamp,cont1(pload1;vmx),cont2(pload2;vmy),cont3(pload3;vmz),...,noofvms
	# :
	# :

	pload = open('/home/ubuntu/vlastic/mainNode/predictedLoad' ,'r')
	pl = {}
	for line in pload:
		tmp = line.rstrip('\n').split(',')
		pl[tmp[0]] = tmp[1]
	pload.close()

	outfile = open('/home/ubuntu/vlastic/mainNode/logs', 'a')

	outfile.write(str(time.time()) + ',')

	vms = []
	for c in cm.keys():
		outfile.write(c + "(" + pl[c] + ";" + cm[c] + "),")
		if cm[c] not in vms:
			vms.append(cm[c])
	outfile.write(str(len(vms)) + '\n')
	outfile.close()


def manage():

	# Important Files at mainNode
	# Historical Loads of Container - actualLoad
	# VM ids and status - vmlList
	# Container IDs and Locations - containerList
	# New Container Mappings - contMapping
	# New Predicted Loads of Containers - predictedLoad

	while (True):

		print('Predicting...')
		predict() #Predict all cont loads from containerList and actualLoad, store in predictedLoad
		cli = getContFuture()
		vli = getVMList()
		print('Packing...')
		packCont(cli, vli) #Pack containers, mapping stored in contMapping
		shutVMs, unusedVMs, cmap = getOffOnMapping()
		cmapcurrent = getCurrentContMap()
		print('Starting VMs Needed...')
		for vmid in shutVMs:
			startVM(vmid) #Start VMs needed but switched off
		print('Migrating Containers...')
		for cont in cmap.keys():
			if cmap[cont] != cmapcurrent[cont]:
				print('Migrating ' + cont + '...')
				migrateCont(cont, cmapcurrent[cont], cmap[cont]) #Move containers according to mapping
				killContainer(cont, cmapcurrent[cont]) #Kill moved containers at source
		copyFileContents('/home/ubuntu/vlastic/mainNode/contMapping', '/home/ubuntu/vlastic/mainNode/containerList') #Update container locations clist = cmapping
		print('Shuttin VMs Unneeded...')
		for vmid in unusedVMs:
			shutVM(vmid) #Shut unneeded VMs

		print('Recording Logs...')
		recordLogs(cmap) #Record Logs for analysis
		print('Sleeping...')
		time.sleep(600) #That's all for now, folks! Sleep for 30 minutes

def testing():
	migrateCont("5697", "i-046d3a8ec1ca1a3fb", "i-0d1b8926c68847b0d")

manage()
