import os
import subprocess
import paramiko
def colstats(cid, vmid):
	vmIP = getIP(vmid)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(vmIP, username='ubuntu', key_filename='/home/ubuntu/vlastic/docker2.pem')
	cpuusage = -1
	memusage = -1

        stdin, stdout, stderr = client.exec_command("ps -p " + str(cid) + " -o %cpu,%mem")
        for line in stdout:
		if "CPU" in line:
			continue
		temp = line.rstrip('\n').split()
                cpuusage = float(temp[0])
		memusage = float(temp[1])
	client.close()
	return cpuusage, memusage

def getIP(id):

        bashCommand = "aws ec2 describe-instances --filters Name=instance-id,Values=" + str(id) + " --query Reservations[*].Instances[*].[PublicIpAddress] --output=text"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        #output = os.system(bashCommand)
        return output

cu, mu = colstats('5826', "i-0d1b8926c68847b0d")
print(str(cu) + " " + str(mu))
