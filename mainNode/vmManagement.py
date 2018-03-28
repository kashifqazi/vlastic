import subprocess
import os
import paramiko

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
	#for cont in containers:
		#check predicted value
		#check current VM capacity
		#if capacity mismatch
	#		startVM(destid)
	#		migrateCont(cont, srcid, destid)
	#		stopVM(srcid)
	migrateCont("5697", "i-046d3a8ec1ca1a3fb", "i-0d1b8926c68847b0d")
	#print("The address is " + address)
manage()
