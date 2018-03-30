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
		for vmid in shutVMs:
			startVM(vmid) #Start VMs needed but switched off
		for cont-vm-pair in contMapping:
			migrateCont(cont, src, dest) #Move containers according to mapping
			kill -9 cont #Kill moved containers at source
		containerList = contMapping #Update container locations
		for vmid in unusedVMs:
			shutVM(vmid) #Shut unneeded VMs

		time.sleep(1800) #That's all for now, folks! Sleep for 30 minutes

def testing():
	migrateCont("5697", "i-046d3a8ec1ca1a3fb", "i-0d1b8926c68847b0d")

testing()
