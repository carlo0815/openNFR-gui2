from Components.Console import Console
from os import mkdir, path, remove
from glob import glob
from Components.config import config, ConfigSubsection, ConfigInteger, ConfigText, getConfigListEntry, ConfigSelection,  ConfigIP, ConfigYesNo, ConfigSequence, ConfigNumber, NoSave, ConfigEnableDisable, configfile
import os
config.NFRSoftcam.camdir = ConfigText(default = "/usr/emu", fixed_size=False)
config.NFRSoftcam.camconfig = ConfigText(default = "/usr/keys", fixed_size=False)
def getcamcmd(cam):
	camname = cam.lower()
	xcamname = cam
	if "gbox" in camname:
                files=os.listdir("/lib")
 		for filename in files:
                	if filename.startswith('ld-2'):
                		ldcheck=filename
		symcheck = "/lib/ld-linux.so.3"
		if os.path.islink(symcheck):
			print "Symlink exist to start gbox"
		else:
			print "Create Symlink to start gbox"
			os.system("ln -sf " + ldcheck + " '/lib/ld-linux.so.3'") 	
	if getcamscript(camname):
		return config.NFRSoftcam.camdir.value + "/" + cam + " start"
	elif ".x" in camname:
	        if "mgcamd" in camname:
	        	return config.NFRSoftcam.camdir.value + "/" + cam
	        elif "oscam_oscamupdater" in camname:
	                cam_name_1 = xcamname.strip(".x")
			return config.NFRSoftcam.camdir.value + "/" + cam + " -bc " + \
				config.NFRSoftcam.camconfig.value + "/" + cam_name_1
	        else:
			emus=[]
			i = 0
			for fAdd in glob ('/etc/*.emu'):
				searchfile = open(fAdd, "r")
				emustart=[]
				cam_name = xcamname.strip(".x")
				for line in searchfile:
					if "binname" in line:
						emus.append(line[10:])
						if cam_name in emus[i]:
						        searchemu = open(fAdd, "r")
					                for line in searchemu:
								if "startcam" in line:
                                                			emustart.append(line[11:])
                                                			emustart = emustart[0].strip()
                                                			cam_count_test = emustart.count(" ")
                                                 			start_emu = emustart.split(" ", 1 )
                                                 			if (cam_count_test == 0):
                                                 				return config.NFRSoftcam.camdir.value + "/" + cam
                                                 			else: 
                                                    				return config.NFRSoftcam.camdir.value + "/" + cam + " " + start_emu[1]
                        	i = i + 1                        	
				searchfile.close()
			
			for fAdd in glob ('/etc/init.d/softcam.*'):
				emustart=[]
				cam_name = xcamname.strip(".x")
				cam_scripts = "/etc/init.d/softcam." + cam_name
				if cam_name == "oscam_oscamupdater":
				        cam_name1 = cam_name[6:]
				        cam_scripts = "/etc/init.d/softcam." + cam_name1
				if fAdd == cam_scripts:
				        cam_starts = cam_scripts + " start"
				        return cam_starts
				else:
                                        
                                        print "no emustarter found in /etc/init.d please check!"
                     	                return config.NFRSoftcam.camdir.value + "/" + cam
			
	
	else:
		if "oscam" in camname:
			return config.NFRSoftcam.camdir.value + "/" + cam + " -bc " + \
				config.NFRSoftcam.camconfig.value + "/"
		if "doscam" in camname:
			return config.NFRSoftcam.camdir.value + "/" + cam + " -bc " + \
				config.NFRSoftcam.camconfig.value + "/"				
		elif "wicard" in camname:
			return "ulimit -s 512; " + config.NFRSoftcam.camdir.value + \
			"/" + cam + " -d -c " + config.NFRSoftcam.camconfig.value + \
			"/wicardd.conf"
		elif "camd3" in camname:
			return config.NFRSoftcam.camdir.value + "/" + cam + " " + \
				config.NFRSoftcam.camconfig.value + "/camd3.config"
		elif "mbox" in camname:
			return config.NFRSoftcam.camdir.value + "/" + cam + " " + \
				config.NFRSoftcam.camconfig.value + "/mbox.cfg"
		elif "cccam" in camname:
			return config.NFRSoftcam.camdir.value + "/" + cam + " -C " + \
				config.NFRSoftcam.camconfig.value + "/CCcam.cfg"
                elif "mgcamd" in camname:
	                os.system("rm /dev/dvb/adapter0/ca1")
	                os.system("ln -sf 'ca0' '/dev/dvb/adapter0/ca1'")                 
			return config.NFRSoftcam.camdir.value + "/" + cam + " -bc " + \
				config.NFRSoftcam.camconfig.value + "/"                				
		elif "mpcs" in camname:
			return config.NFRSoftcam.camdir.value + "/" + cam + " -c " + \
				config.NFRSoftcam.camconfig.value
		elif "newcs" in camname:
			return config.NFRSoftcam.camdir.value + "/" + cam + " -C " + \
				config.NFRSoftcam.camconfig.value + "/newcs.conf"
		elif "vizcam" in camname:
			return config.NFRSoftcam.camdir.value + "/" + cam + " -b -c " + \
				config.NFRSoftcam.camconfig.value + "/"
		elif "rucam" in camname:
			return config.NFRSoftcam.camdir.value + "/" + cam + " -b"
		elif "gbox" in camname:
			return config.NFRSoftcam.camdir.value + "/" + cam + " " + \
				config.NFRSoftcam.camconfig.value + "/gbox.cfg"	
 		elif "scam" in camname and not "oscam" in camname:
			return config.NFRSoftcam.camdir.value + "/" + cam + " -s " + \
				config.NFRSoftcam.camconfig.value + "/"			
		else:
			return config.NFRSoftcam.camdir.value + "/" + cam

def getcamscript(cam):
	cam = cam.lower()
	if cam.endswith('.sh') or cam.startswith('softcam') or \
		cam.startswith('cardserver'):
		return True
	else:
		return False

def stopcam(cam):
	if getcamscript(cam):
		cmd = config.NFRSoftcam.camdir.value + "/" + cam + " stop"
	else:
		cmd = "killall -15 " + cam
	Console().ePopen(cmd)
	print "[NFR-SoftCam Manager] stopping", cam
	try:
		remove("/tmp/ecm.info")
	except:
		pass

def __createdir(list):
	dir = ""
	for line in list[1:].split("/"):
		dir += "/" + line
		if not path.exists(dir):
			try:
				mkdir(dir)
			except:
				print "[NFR-SoftCam Manager] Failed to mkdir", dir

def checkconfigdir():
	if not path.exists(config.NFRSoftcam.camconfig.value):
		__createdir("/usr/keys")
		config.NFRSoftcam.camconfig.value = "/usr/keys"
		config.NFRSoftcam.camconfig.save()
	if not path.exists(config.NFRSoftcam.camdir.value):
		if path.exists("/usr/emu"):
			config.NFRSoftcam.camdir.value = "/usr/emu"
		else:
			__createdir("/usr/emu")
			config.NFRSoftcam.camdir.value = "/usr/emu"
		config.NFRSoftcam.camdir.save()
