from Tools.Directories import resolveFilename, SCOPE_SYSETC
#from Tools.HardwareInfo import HardwareInfo
from os import path
import sys
import os
import time
from boxbranding import getImageVersion, getMachineBuild, getBoxType
from sys import modules
import socket, fcntl, struct

def getVersionString():
	return getImageVersion()

def getFlashDateString():
	try:
		return time.strftime(_("%Y-%m-%d"), time.localtime(os.stat("/home").st_ctime))
	except:
		return _("unknown")

def getImageVersionString():
	try:
		file = open(resolveFilename(SCOPE_SYSETC, 'image-version'), 'r')
		lines = file.readlines()
		for x in lines:
			splitted = x.split('=')
			if splitted[0] == "version":
				version = splitted[1].replace('\n','')
		file.close()
		return version
	except IOError:
		return "unavailable"

def getImageUrlString():
	try:
		file = open(resolveFilename(SCOPE_SYSETC, 'image-version'), 'r')
		lines = file.readlines()
		for x in lines:
			splitted = x.split('=')
			if splitted[0] == "url":
				version = splitted[1].replace('\n','')
		file.close()
		return version
	except IOError:
		return "unavailable"
	      
def getEnigmaVersionString():
	return getImageVersion()

def getGStreamerVersionString():
	import enigma
	return enigma.getGStreamerVersionString()
	
def getKernelVersionString():
	try:
		f = open("/proc/version","r")
		kernelversion = f.read().split(' ', 4)[2].split('-',2)[0]
		f.close()
		return kernelversion
	except:
		return _("unknown")

def getLastUpdateString():
	try:
		file = open(resolveFilename(SCOPE_SYSETC, 'image-version'), 'r')
		lines = file.readlines()
		for x in lines:
			splitted = x.split('=')
			if splitted[0] == "date":
				#YYYY MM DD hh mm
				#2005 11 29 01 16
				string = splitted[1].replace('\n','')
				year = string[0:4]
				month = string[4:6]
				day = string[6:8]
				date = '-'.join((year, month, day))
				hour = string[8:10]
				minute = string[10:12]
				time = ':'.join((hour, minute))
				lastupdated = ' '.join((date, time))
		file.close()
		return lastupdated
	except IOError:
		return "unavailable"

import socket, fcntl, struct

def _ifinfo(sock, addr, ifname):
	iface = struct.pack('256s', ifname[:15])
	info  = fcntl.ioctl(sock.fileno(), addr, iface)
	if addr == 0x8927:
		return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1].upper()
	else:
		return socket.inet_ntoa(info[20:24])

def getIfConfig(ifname):
	ifreq = {'ifname': ifname}
	infos = {}
	sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# offsets defined in /usr/include/linux/sockios.h on linux 2.6
	infos['addr']    = 0x8915 # SIOCGIFADDR
	infos['brdaddr'] = 0x8919 # SIOCGIFBRDADDR
	infos['hwaddr']  = 0x8927 # SIOCSIFHWADDR
	infos['netmask'] = 0x891b # SIOCGIFNETMASK
	try:
		for k,v in infos.items():
			ifreq[k] = _ifinfo(sock, v, ifname)
	except:
		pass
	sock.close()
	return ifreq

def getIfTransferredData(ifname):
	f = open('/proc/net/dev', 'r')
	for line in f:
		if ifname in line:
			data = line.split('%s:' % ifname)[1].split()
			rx_bytes, tx_bytes = (data[0], data[8])
			f.close()
			return rx_bytes, tx_bytes

def getModelString():	
	try:
		file = open("/proc/stb/info/boxtype", "r")
		model = file.readline().strip()
		file.close()
		return model
	except IOError:
		return "unknown"		

def getChipSetString():
	if getMachineBuild() in ('dm7080','dm820'):
		return "7435"
	elif getMachineBuild() in ('dm520','dm525'):
		return "73625"
	elif getMachineBuild() in ('dm900','dm920','et13000','sf5008'):
		return "7252S"
	elif getMachineBuild() in ('hd51','vs1500','h7'):
		return "7251S"
	else:
		try:
			f = open('/proc/stb/info/chipset', 'r')
			chipset = f.read()
			f.close()
			return str(chipset.lower().replace('\n','').replace('bcm','').replace('brcm','').replace('sti',''))
		except IOError:
			return "unavailable"

def getCPUSpeedString():
	if getMachineBuild() in ('vusolo4k'):
		return "1,5 GHz"
	elif getMachineBuild() in ('formuler1', 'triplex'):
		return "1,3 GHz"
	elif getMachineBuild() in ('u51','u52','u5','u5pvr','h9','cc1','sf8008','hd60','i55plus'):
		return "1,6 GHz"	
	elif getMachineBuild() in ('vuuno4k','vuultimo4k', 'gb7252', 'dags7252', '8100s'):
		return "1,7 GHz"
	elif getMachineBuild() in ('alien5','u53'):
		return "2,0 GHz"
	elif getMachineBuild() in ('hd51','hd52','sf4008','vs1500','et1x000','h7','et13000','sf5008'):
		try:
			import binascii
			f = open('/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency', 'rb')
			clockfrequency = f.read()
			f.close()
			return "%s MHz" % str(round(int(binascii.hexlify(clockfrequency), 16)/1000000,1))
		except:
			return "1,7 GHz"
	else:
		try:
			file = open('/proc/cpuinfo', 'r')
			lines = file.readlines()
			for x in lines:
				splitted = x.split(': ')
				if len(splitted) > 1:
					splitted[1] = splitted[1].replace('\n','')
					if splitted[0].startswith("cpu MHz"):
						mhz = float(splitted[1].split(' ')[0])
						if mhz and mhz >= 1000:
							mhz = "%s GHz" % str(round(mhz/1000,1))
						else:
							mhz = "%s MHz" % str(round(mhz,1))
			file.close()
			return mhz
		except IOError:
			return "unavailable"


def getCPUString():
	if getMachineBuild() in ('vuuno4k', 'vuultimo4k','xc7362', 'vusolo4k', 'hd51', 'hd52', 'sf4008', 'dm900','dm920', 'gb7252', 'dags7252', 'vs1500', 'et1x000', 'xc7439','h7','8100s','et13000','sf5008'):
		return "Broadcom"
	elif getMachineBuild() in ('u51','u52','u53','u5','u5pvr','h9','cc1','sf8008','hd60','i55plus'):
		return "Hisilicon"	
	else:
		try:
			system="unknown"
			file = open('/proc/cpuinfo', 'r')
			lines = file.readlines()
			for x in lines:
				splitted = x.split(': ')
				if len(splitted) > 1:
					splitted[1] = splitted[1].replace('\n','')
					if splitted[0].startswith("system type"):
						system = splitted[1].split(' ')[0]
					elif splitted[0].startswith("Processor"):
						system = splitted[1].split(' ')[0]
			file.close()
			return system
		except IOError:
			return "unavailable"

def getCpuCoresString():
	try:
		file = open('/proc/cpuinfo', 'r')
		lines = file.readlines()
		for x in lines:
			splitted = x.split(': ')
			if len(splitted) > 1:
				splitted[1] = splitted[1].replace('\n','')
				if splitted[0].startswith("processor"):
					if getMachineBuild() in ('u51','u52','u53','vuultimo4k','u5','u5pvr','h9','alien5','cc1','sf8008','hd60','i55plus'):
 						cores = 4						
					elif int(splitted[1]) > 0:
						cores = 2
					else:
						cores = 1
		file.close()
		return cores
	except IOError:
		return "unavailable"

def getPythonVersionString():
	try:
		import commands
		status, output = commands.getstatusoutput("python -V")
		return output.split(' ')[1]
	except:
		return _("unknown")

# For modules that do "from About import about"
about = sys.modules[__name__]
