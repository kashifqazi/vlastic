import subprocess
import os
import paramiko
import time

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
def getIP(id):

	bashCommand = "aws ec2 describe-instances --filters Name=instance-id,Values=" + str(id) + " --query Reservations[*].Instances[*].[PublicIpAddress] --output=text"
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
	#output = os.system(bashCommand)
	return output

def getOffOnMapping():
	vms = open('vmList', 'r')
	conts = open('contMapping' ,'r')

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

	outfile = open('contMapping' ,'w')
	for v in vmstats.keys():
		outfile.write(v + ',' + vmsizes[v] + ',' + vmstats[v] + '\n')
	outfile.close()

	return vmsturnon,vmsturnoff


def getCurrentContMap():

	infile = open('containerList' ,'r')
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


def manage():

	# Important Files at mainNode
	# Historical Loads of Container - actualLoad
	# VM ids and status - vmlList
	# Container IDs and Locations - containerList
	# New Container Mappings - contMapping
	# New Predicted Loads of Containers - predictedLoad

	while (True):

		predict() #Predict all cont loads from containerList and actualLoad, store in predictedLoad
		cli = getContFuture()
		vli = getVMList()
		packCont(cli, vli) #Pack containers, mapping stored in contMapping
		shutVMs, unusedVMs, cmap = getOffOnMapping()
		cmapcurrent = getCurrentContMap()
		for vmid in shutVMs:
			startVM(vmid) #Start VMs needed but switched off
		for cont in cmap.keys():
			if cmap[cont] != cmapcurrent[cont]
				migrateCont(cont, cmapcurrent[cont], cmap[cont]) #Move containers according to mapping
				kill -9 cont #Kill moved containers at source
		copyFileContents(contMapping, containerList) #Update container locations clist = cmapping
		for vmid in unusedVMs:
			shutVM(vmid) #Shut unneeded VMs

		time.sleep(1800) #That's all for now, folks! Sleep for 30 minutes

def testing():
	migrateCont("5697", "i-046d3a8ec1ca1a3fb", "i-0d1b8926c68847b0d")

testing()
