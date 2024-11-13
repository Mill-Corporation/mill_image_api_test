import subprocess

def reboot():
	print('func reboot')
	cmdReboot = "sudo reboot"
	subprocess.run(cmdReboot, shell=True)
