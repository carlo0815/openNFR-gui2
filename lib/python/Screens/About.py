from __future__ import print_function
from __future__ import absolute_import
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Sources.StaticText import StaticText
from Components.Harddisk import Harddisk, harddiskmanager
from Components.NimManager import nimmanager
from Components.About import about
from Components.config import config
from Components.ScrollLabel import ScrollLabel
from Components.Console import Console
from Components.SystemInfo import SystemInfo
from Components.Label import Label
from enigma import eTimer, getEnigmaVersionString
from boxbranding import getBoxType, getMachineBrand, getMachineBuild, getMachineName, getImageVersion, getImageBuild, getDriverDate, getOEVersion
from Components.Console import Console
from Components.Pixmap import MultiPixmap
from Components.Network import iNetwork

from Tools.StbHardware import getFPVersion
from Tools.Multiboot import GetCurrentImage, GetCurrentImageMode 
from os import path, popen
from re import search
import six

SIGN = '°' if six.PY3 else str('\xc2\xb0')


class About(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("About"))
		OpenNFRVersion = _("OpenNFR %s") % about.getImageVersionString()
		self["OpenNFRVersion"] = Label(OpenNFRVersion)
		
		AboutText = _("Model:\t\t%s %s\n") % (getMachineBrand(), getMachineName())
		
		bootloader = ""
		if path.exists('/sys/firmware/devicetree/base/bolt/tag'):
			f = open('/sys/firmware/devicetree/base/bolt/tag', 'r')
			bootloader = f.readline().replace('\x00', '').replace('\n', '')
			f.close()
			AboutText += _("Bootloader:\t\t%s\n") % (bootloader)

		if path.exists('/proc/stb/info/chipset'):
			AboutText += _("Chipset:\t\tBCM%s") % about.getChipSetString() + "\n"

		cpuMHz = ""
		if getMachineBuild() in ('u41', 'u42', 'u43'):
			cpuMHz = _("   (1.0 GHz)")
		elif getMachineBuild() in ('dags72604', 'vusolo4k', 'vuultimo4k', 'vuzero4k', 'gb72604', 'vuduo4kse'):
			cpuMHz = "   (1,5 GHz)"
		elif getMachineBuild() in ('formuler1', 'triplex'):
			cpuMHz = "   (1,3 GHz)"
		elif getMachineBuild() in ('gbmv200', 'plus', 'u51', 'u5', 'u53', 'u52', 'u54', 'u55', 'u56', 'u57', 'u5pvr', 'h9', 'h9combo', 'cc1', 'sf8008', 'hd60', 'hd61', 'i55plus', 'ustym4kpro', 'v8plus', 'multibox', 'multiboxse'):
			cpuMHz = "   (1,6 GHz)"			
		elif getMachineBuild() in ('vuuno4k', 'vuultimo4k', 'gb7252', 'dags7252', '8100s'):
			cpuMHz = "   (1,7 GHz)"
		elif getMachineBuild() in ('alien5', 'hzero', 'h8'):
			cpuMHz = "   (2,0 GHz)"
		elif getMachineBuild() in ('vuduo4k'):
			cpuMHz = _("   (2.1 GHz)")
		elif getMachineBuild() in ('sf5008', 'et13000', 'et1x000', 'hd52', 'hd51', 'sf4008', 'vs1500', 'h7', 'osmio4k', 'osmio4kplus', 'osmini4k'):
			try:
				import binascii
				f = open('/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency', 'rb')
				clockfrequency = f.read()
				f.close()
				cpuMHz = "   (%s MHz)" % str(round(int(binascii.hexlify(clockfrequency), 16)/1000000,1))
			except:
				cpuMHz = "   (1,7 GHz)"
		else:
			if path.exists('/proc/cpuinfo'):
				f = open('/proc/cpuinfo', 'r')
				temp = f.readlines()
				f.close()
				try:
					for lines in temp:
						lisp = lines.split(': ')
						if lisp[0].startswith('cpu MHz'):
							#cpuMHz = "   (" +  lisp[1].replace('\n', '') + " MHz)"
							cpuMHz = "   (" +  str(int(float(lisp[1].replace('\n', '')))) + " MHz)"
							break
				except:
					pass

		AboutText += _("CPU:\t\t%s") % about.getCPUString() + cpuMHz + "\n"
		AboutText += _("Cores:\t\t%s") % about.getCpuCoresString() + "\n"
		
		tempinfo = ""
		if path.exists('/proc/stb/sensors/temp0/value'):
			f = open('/proc/stb/sensors/temp0/value', 'r')
			tempinfo = f.read()
			f.close()
		elif path.exists('/proc/stb/fp/temp_sensor'):
			f = open('/proc/stb/fp/temp_sensor', 'r')
			tempinfo = f.read()
			f.close()
		elif path.exists('/proc/stb/sensors/temp/value'):
			f = open('/proc/stb/sensors/temp/value', 'r')
			tempinfo = f.read()
			f.close()
		if tempinfo and int(tempinfo.replace('\n', '')) > 0:
			AboutText += _("System temperature:\t%s") % tempinfo.replace('\n', '').replace(' ', '') + SIGN + "C\n"

		tempinfo = ""
		if path.exists('/proc/stb/fp/temp_sensor_avs'):
			f = open('/proc/stb/fp/temp_sensor_avs', 'r')
			tempinfo = f.read()
			f.close()
		elif path.exists('/proc/stb/power/avs'):
			f = open('/proc/stb/power/avs', 'r')
			tempinfo = f.read()
			f.close()
		elif path.exists('/sys/devices/virtual/thermal/thermal_zone0/temp'):
			try:
				f = open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r')
				tempinfo = f.read()
				tempinfo = tempinfo[:-4]
				f.close()
			except:
				tempinfo = ""
		elif path.exists('/proc/hisi/msp/pm_cpu'):
			try:
				for line in open('/proc/hisi/msp/pm_cpu').readlines():
					line = [x.strip() for x in line.strip().split(":")]
					if line[0] in ("Tsensor"):
						temp = line[1].split("=")
						temp = line[1].split(" ")
						tempinfo = temp[2]
			except:
				tempinfo = ""
		if tempinfo and int(tempinfo.replace('\n', '')) > 0:
			AboutText += _("Processor temperature:\t%s") % tempinfo.replace('\n', '').replace(' ', '') + SIGN + "C\n"
		imagestarted = ""
		bootname = ''
		if path.exists('/boot/bootname'):
			f = open('/boot/bootname', 'r')
			bootname = f.readline().split('=')[1]
			f.close()

		if SystemInfo["canMultiBoot"]:
			slot = image = GetCurrentImage()
			bootmode = ""
			part = "eMMC slot %s" %slot
			if SystemInfo["canMode12"]:
				bootmode = " bootmode = %s" %GetCurrentImageMode()
			if SystemInfo["HasHiSi"] and "sda" in SystemInfo["canMultiBoot"][slot]['device']:
				if slot > 4:
					image -=4
				else:
					image -=1
				part = "SDcard slot %s (%s) " %(image, SystemInfo["canMultiBoot"][slot]['device'])
			AboutText += _("Selected Image:\t\t%s") % _("STARTUP_") + str(slot) + "  (" + part + bootmode + ")\n"
		string = getDriverDate()
		year = string[0:4]
		month = string[4:6]
		day = string[6:8]
		driversdate = '-'.join((year, month, day))
		AboutText += _("Drivers:\t\t%s") % driversdate + "\n"
		AboutText += _("Image:\t\t%s") % about.getImageVersionString() + "\n"
		AboutText += _("Build:\t\t%s") % getImageBuild() + "\n"
		AboutText += _("Kernel: \t\t%s") % about.getKernelVersionString() + "\n"
		AboutText += _("Oe-Core:\t\t%s") % getOEVersion() + "\n"
		AboutText += _("Enigma (re)starts:\t%d\n") % config.misc.startCounter.value
		AboutText += _("GStreamer:\t\t%s") % about.getGStreamerVersionString() + "\n"
		AboutText += _("Python:\t\t%s") % about.getPythonVersionString() + "\n"

		fp_version = getFPVersion()
		if fp_version is None:
			fp_version = ""
		elif fp_version != 0:
			fp_version = _("Front Panel:\t\t%s") % fp_version 
			AboutText += fp_version + "\n"
		else:
			fp_version = _("Front Panel:\t\tVersion unknown")
			AboutText += fp_version + "\n"

		if getMachineBuild() not in ('gbmv200', 'vuduo4k', 'v8plus', 'ustym4kpro', 'hd60', 'hd61', 'i55plus', 'osmio4k', 'osmio4kplus', 'h9', 'h9combo', 'vuzero4k', 'sf5008', 'et13000', 'et1x000', 'hd51', 'hd52', 'vusolo4k', 'vuuno4k', 'vuuno4kse', 'vuultimo4k', 'sf4008', 'dm820', 'dm7080', 'dm900', 'dm920', 'gb7252', 'dags7252', 'vs1500', 'h7', 'xc7439', '8100s', 'u41', 'u42', 'u43', 'u5', 'u5pvr', 'u52', 'u53', 'u54', 'u55', 'u56', 'u51', 'cc1', 'sf8008'):
			AboutText += _("Installed:\t\t%s") % about.getFlashDateString() + "\n"
		AboutText += _("Last Upgrade:\t\t%s") % about.getLastUpdateString() + "\n\n" 
		
		self["FPVersion"] = StaticText(fp_version)

		AboutText += _("WWW:\t\t%s") % about.getImageUrlString() + "\n\n"
		AboutText += _("based on:\t\t%s") % "www.github.com/oe-alliance" + "\n\n"
		# don't remove the string out of the _(), or it can't be "translated" anymore.
		# TRANSLATORS: Add here whatever should be shown in the "translator" about screen, up to 6 lines (use \n for newline)
		info = _("TRANSLATOR_INFO")

		if info == _("TRANSLATOR_INFO"):
			info = ""

		infolines = _("").split("\n")
		infomap = {}
		for x in infolines:
			l = x.split(': ')
			if len(l) != 2:
				continue
			(type, value) = l
			infomap[type] = value

		translator_name = infomap.get("Language-Team", "none")
		if translator_name == "none":
			translator_name = infomap.get("Last-Translator", "")

		self["FPVersion"] = StaticText(fp_version)

		self["TunerHeader"] = StaticText(_("Detected NIMs:"))

		nims = nimmanager.nimList()
		for count in range(len(nims)):
			if count < 4:
				self["Tuner" + str(count)] = StaticText(nims[count])
			else:
				self["Tuner" + str(count)] = StaticText("")

		self["HDDHeader"] = StaticText(_("Detected HDD:"))

		hddlist = harddiskmanager.HDDList()
		hddinfo = ""
		if hddlist:
			for count in range(len(hddlist)):
				if hddinfo:
					hddinfo += "\n"
				hdd = hddlist[count][1]
				if int(hdd.free()) > 1024:
					hddinfo += "%s\n(%s, %d GB %s)" % (hdd.model(), hdd.capacity(), hdd.free()/1024, _("free"))
				else:
					hddinfo += "%s\n(%s, %d MB %s)" % (hdd.model(), hdd.capacity(), hdd.free(), _("free"))
		else:
			hddinfo = _("none")
		self["hddA"] = StaticText(hddinfo)
		
		self["AboutScrollLabel"] = ScrollLabel(AboutText)

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"], 
			{
				"cancel": self.close,
				"ok": self.close,
				"green": self.showTranslationInfo,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			})

	def showTranslationInfo(self):
		self.session.open(TranslationInfo)

class Devices(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Device Information"))
		self.skinName = ["SystemDevicesInfo", "About"]
		
		OpenNFRVersion = _("OpenNFR %s") % about.getImageVersionString()
		self["OpenNFRVersion"] = Label(OpenNFRVersion)
		
		self.AboutText = ""
		self["AboutScrollLabel"] = ScrollLabel(self.AboutText)
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.populate2)
		self.populate()

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			})
			
	def populate(self):
		scanning = _("Wait please while scanning for devices...")
		self["AboutScrollLabel"].setText(scanning)
		self.activityTimer.start(10)

	def populate2(self):
		self.activityTimer.stop()
		self.Console = Console()
		
		self.AboutText = _("Model:\t%s %s\n") % (getMachineBrand(), getMachineName())
		self.AboutText += "\n" + _("Detected NIMs:") + "\n"

		nims = nimmanager.nimList()
		for count in list(range(len(nims))):
			if count < 4:
				self["Tuner" + str(count)] = StaticText(nims[count])
			else:
				self["Tuner" + str(count)] = StaticText("")
			self.AboutText += nims[count] + "\n"

		self.AboutText += "\n" + _("Detected HDD:") + "\n"

		self.list = []
		list2 = []
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			parts = line.strip().split()
			if not parts:
				continue
			device = parts[3]
			if not search('sd[a-z][1-9]', device):
				continue
			if device in list2:
				continue

			mount = '/dev/' + device
			f = open('/proc/mounts', 'r')
			for line in f.readlines():
				if device in line:
					parts = line.strip().split()
					mount = str(parts[1])
					break
			f.close()

			if not mount.startswith('/dev/'):
				size = Harddisk(device).diskSize()
				free = Harddisk(device).free()

				if ((float(size) / 1024) / 1024) >= 1:
					sizeline = _("Size: ") + str(round(((float(size) / 1024) / 1024), 2)) + " " + _("TB")
				elif (size / 1024) >= 1:
					sizeline = _("Size: ") + str(round((float(size) / 1024), 2)) +  " " + _("GB")
				elif size >= 1:
					sizeline = _("Size: ") + str(size) +  " " + _("MB")
				else:
					sizeline = _("Size: ") + _("unavailable")

				if ((float(free) / 1024) / 1024) >= 1:
					freeline = _("Free: ") + str(round(((float(free) / 1024) / 1024), 2)) +  " " + _("TB")
				elif (free / 1024) >= 1:
					freeline = _("Free: ") + str(round((float(free) / 1024), 2)) +  " " + _("GB")
				elif free >= 1:
					freeline = _("Free: ") + str(free) +  " " + _("MB")
				else:
					freeline = _("Free: ") + _("full")
				self.list.append(mount + '\t' + sizeline + ' \t' + freeline)
			else:
				self.list.append(mount + '\t' + _('Not mounted'))

			list2.append(device)
		self.list = '\n'.join(self.list)
		
		self.AboutText += self.list + "\n"
		self.AboutText += "\n" + _("Network Servers:") + "\n"
		#self.mountinfo = _("none")
		self.Console.ePopen("df -mh | grep -v '^Filesystem'", self.Stage1Complete)
		#self.AboutText +=self.mountinfo
		#self["AboutScrollLabel"].setText(self.AboutText)

	def Stage1Complete(self, result, retval, extra_args=None):
		result = six.ensure_str(result)
		result = result.replace('\n                        ', ' ').split('\n')
		self.mountinfo = ""
		for line in result:
			self.parts = line.split()
			if line and self.parts[0] and (self.parts[0].startswith('192') or self.parts[0].startswith('//192')):
				line = line.split()
				ipaddress = line[0]
				mounttotal = line[1]
				mountfree = line[3]
				if self.mountinfo:
					self.mountinfo += "\n"
				self.mountinfo += "%s (%sB, %sB %s)" % (ipaddress, mounttotal, mountfree, _("free"))
		if self.mountinfo:
			self.mountinfo += "\n"
		else:
			self.mountinfo += (_('none'))
		try:
			self.AboutText += self.mountinfo + "\n"
		except:
			pass

		self["AboutScrollLabel"].setText(self.AboutText) 


class SystemMemoryInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Memory Information"))
		#self.skinName = ["SystemMemoryInfo", "About"]
		self.skinName = ["About"]
		
		OpenNFRVersion = _("OpenNFR %s") % about.getImageVersionString()
		self["OpenNFRVersion"] = Label(OpenNFRVersion)
		
		self["AboutScrollLabel"] = ScrollLabel()

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
									{
										"cancel": self.close,
										"ok": self.close,
									})
									
		out_lines = open("/proc/meminfo").readlines()
		self.AboutText = _("RAM") + '\n\n'
		RamTotal = "-"
		RamFree = "-"
		for lidx in list(range(len(out_lines) - 1)):
			tstLine = out_lines[lidx].split()
			if "MemTotal:" in tstLine:
				MemTotal = out_lines[lidx].split()
				self.AboutText += _("Total Memory:") + "\t" + MemTotal[1] + "\n"
			if "MemFree:" in tstLine:
				MemFree = out_lines[lidx].split()
				self.AboutText += _("Free Memory:") + "\t" + MemFree[1] + "\n"
			if "Buffers:" in tstLine:
				Buffers = out_lines[lidx].split()
				self.AboutText += _("Buffers:") + "\t" + Buffers[1] + "\n"
			if "Cached:" in tstLine:
				Cached = out_lines[lidx].split()
				self.AboutText += _("Cached:") + "\t" + Cached[1] + "\n"
			if "SwapTotal:" in tstLine:
				SwapTotal = out_lines[lidx].split()
				self.AboutText += _("Total Swap:") + "\t" + SwapTotal[1] + "\n"
			if "SwapFree:" in tstLine:
				SwapFree = out_lines[lidx].split()
				self.AboutText += _("Free Swap:") + "\t" + SwapFree[1] + "\n\n"

		self.Console = Console()
		self.Console.ePopen("df -mh / | grep -v '^Filesystem'", self.Stage1Complete)

	def Stage1Complete(self, result, retval, extra_args=None):
		result = six.ensure_str(result)
		flash = str(result).replace('\n', '')
		flash = flash.split()
		RamTotal = flash[1]
		RamFree = flash[3]

		self.AboutText += _("FLASH") + '\n\n'
		self.AboutText += _("Total:") + "\t" + RamTotal + "\n"
		self.AboutText += _("Free:") + "\t" + RamFree + "\n\n"

		self["AboutScrollLabel"].setText(self.AboutText)

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.close,
				"ok": self.close,
			})
			
class SystemNetworkInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Network Information"))
		self.skinName = ["SystemNetworkInfo", "About"]
		
		OpenNFRVersion = _("OpenNFR %s") % about.getImageVersionString()
		self["OpenNFRVersion"] = Label(OpenNFRVersion)
		
		self["LabelBSSID"] = StaticText()
		self["LabelESSID"] = StaticText()
		self["LabelQuality"] = StaticText()
		self["LabelSignal"] = StaticText()
		self["LabelBitrate"] = StaticText()
		self["LabelEnc"] = StaticText()
		self["LabelChannel"] = StaticText(_('Channel:'))
		self["LabelEncType"] = StaticText(_('Encryption Type:'))
		self["LabelFrequency"] = StaticText(_('Frequency:'))
		self["LabelFrequencyNorm"] = StaticText(_('Frequency Norm:'))
		self["BSSID"] = StaticText()
		self["ESSID"] = StaticText()
		self["quality"] = StaticText()
		self["signal"] = StaticText()
		self["bitrate"] = StaticText()
		self["enc"] = StaticText()
		self["channel"] = StaticText()
		self["encryption_type"] = StaticText()
		self["frequency"] = StaticText()
		self["frequency_norm"] = StaticText()

		self["IFtext"] = StaticText()
		self["IF"] = StaticText()
		self["Statustext"] = StaticText()
		self["statuspic"] = MultiPixmap()
		self["statuspic"].setPixmapNum(1)
		self["statuspic"].hide()

		self.iface = None
		self.createscreen()
		self.iStatus = None

		if iNetwork.isWirelessInterface(self.iface):
			try:
				from Plugins.SystemPlugins.WirelessLan.Wlan import iStatus

				self.iStatus = iStatus
			except:
				pass
			self.resetList()
			self.onClose.append(self.cleanup)
		self.updateStatusbar()

		self["key_red"] = StaticText(_("Close"))

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
									{
										"cancel": self.close,
										"ok": self.close,
										"up": self["AboutScrollLabel"].pageUp,
										"down": self["AboutScrollLabel"].pageDown
									})

	def createscreen(self):
		self.AboutText = ""
		self.iface = "eth0"
		eth0 = about.getIfConfig('eth0')
		if 'addr' in eth0:
			self.AboutText += _("IP:") + "\t" + "\t" + eth0['addr'] + "\n"
			if 'netmask' in eth0:
				self.AboutText += _("Netmask:") + "\t" + "\t" + eth0['netmask'] + "\n"
			if 'hwaddr' in eth0:
				self.AboutText += _("MAC:") + "\t" + "\t" + eth0['hwaddr'] + "\n"
			self.iface = 'eth0'

		eth1 = about.getIfConfig('eth1')
		if 'addr' in eth1:
			self.AboutText += _("IP:") + "\t" + "\t" + eth1['addr'] + "\n"
			if 'netmask' in eth1:
				self.AboutText += _("Netmask:") + "\t" + "\t" + eth1['netmask'] + "\n"
			if 'hwaddr' in eth1:
				self.AboutText += _("MAC:") + "\t" + "\t" + eth1['hwaddr'] + "\n"
			self.iface = 'eth1'

		ra0 = about.getIfConfig('ra0')
		if 'addr' in ra0:
			self.AboutText += _("IP:") + "\t" + "\t" + ra0['addr'] + "\n"
			if 'netmask' in ra0:
				self.AboutText += _("Netmask:") + "\t" + "\t" + ra0['netmask'] + "\n"
			if 'hwaddr' in ra0:
				self.AboutText += _("MAC:") + "\t" + "\t" + ra0['hwaddr'] + "\n"
			self.iface = 'ra0'

		wlan0 = about.getIfConfig('wlan0')
		if 'addr' in wlan0:
			self.AboutText += _("IP:") + "\t" + "\t" + wlan0['addr'] + "\n"
			if 'netmask' in wlan0:
				self.AboutText += _("Netmask:") + "\t" + "\t" + wlan0['netmask'] + "\n"
			if 'hwaddr' in wlan0:
				self.AboutText += _("MAC:") + "\t" + "\t" + wlan0['hwaddr'] + "\n"
			self.iface = 'wlan0'

		wlan1 = about.getIfConfig('wlan1')
		if 'addr' in wlan1:
			self.AboutText += _("IP:") + "\t" + "\t" + wlan1['addr'] + "\n"
			if 'netmask' in wlan1:
				self.AboutText += _("Netmask:") + "\t" + "\t" + wlan1['netmask'] + "\n"
			if 'hwaddr' in wlan1:
				self.AboutText += _("MAC:") + "\t" + "\t" + wlan1['hwaddr'] + "\n"
			self.iface = 'wlan1'

		rx_bytes, tx_bytes = about.getIfTransferredData(self.iface)
		self.AboutText += "\n" + _("Bytes received:") + "\t" + "\t" + rx_bytes + "\n"
		self.AboutText += _("Bytes sent:") + "\t" + "\t" + tx_bytes + "\n"

		hostname = open('/proc/sys/kernel/hostname').read()
		self.AboutText += _("Hostname:") + "\t" + "\t" + hostname + "\n"		
		self["AboutScrollLabel"] = ScrollLabel(self.AboutText)


	def cleanup(self):
		if self.iStatus:
			self.iStatus.stopWlanConsole()

	def resetList(self):
		if self.iStatus:
			self.iStatus.getDataForInterface(self.iface, self.getInfoCB)

	def getInfoCB(self, data, status):
		self.LinkState = None
		if data is not None:
			if data is True:
				if status is not None:
					if self.iface == 'wlan0' or self.iface == 'wlan1' or self.iface == 'ra0':
						if status[self.iface]["essid"] == "off":
							essid = _("No Connection")
						else:
							essid = status[self.iface]["essid"]
						if status[self.iface]["accesspoint"] == "Not-Associated":
							accesspoint = _("Not-Associated")
							essid = _("No Connection")
						else:
							accesspoint = status[self.iface]["accesspoint"]
						if "BSSID" in self:
							self.AboutText += '{:<35}'.format(_('Accesspoint:')) + '\t' + accesspoint + '\n'
						if "ESSID" in self:
							self.AboutText += '{:<35}'.format(_('SSID:')) + '\t' + essid + '\n'

						quality = status[self.iface]["quality"]
						if "quality" in self:
							self.AboutText += '{:<35}'.format(_('Link Quality:')) + '\t' + quality + '\n'

						channel = str(status[self.iface]["channel"])
						if "channel" in self:
							self.AboutText += '{:<35}'.format(_('Channel:')) + '\t' + channel + '\n'

						frequency = status[self.iface]["frequency"]
						if "frequency" in self:
							self.AboutText += '{:<35}'.format(_('Frequency:')) + '\t' + frequency + '\n'

						frequency_norm = status[self.iface]["frequency_norm"]
						if frequency_norm is not None:
							self.AboutText += '{:<35}'.format(_('Frequency Norm:')) + '\t' + frequency_norm + '\n'

						if status[self.iface]["bitrate"] == '0':
							bitrate = _("Unsupported")
						else:
							bitrate = str(status[self.iface]["bitrate"])
						if "bitrate" in self:
							self.AboutText += '{:<35}'.format(_('Bitrate:')) + '\t' + bitrate + '\n'

						signal = str(status[self.iface]["signal"]) + " dBm"
						if "signal" in self:
							self.AboutText += '{:<35}'.format(_('Signal Strength:')) + '\t' + signal + '\n'

						if status[self.iface]["encryption"] == "off":
							if accesspoint == "Not-Associated":
								encryption = _("Disabled")
							else:
								encryption = _("Unsupported")
						else:
							encryption = _("Enabled")
						if "enc" in self:
							self.AboutText += '{:<35}'.format(_('Encryption:')) + '\t' + encryption + '\n'

						encryption_type = status[self.iface]["encryption_type"]
						if "encryption_type" in self:
							self.AboutText += '{:<35}'.format(_('Encryption Type:')) + '\t' + encryption_type + '\n'

						if status[self.iface]["essid"] == "off" or status[self.iface]["accesspoint"] == "Not-Associated" or status[self.iface]["accesspoint"] is False:
							self.LinkState = False
							self["statuspic"].setPixmapNum(1)
							self["statuspic"].show()
						else:
							self.LinkState = True
							iNetwork.checkNetworkState(self.checkNetworkCB)
						self["AboutScrollLabel"].setText(self.AboutText)

	def exit(self):
		self.timer.stop()
		self.close(True)

	def updateStatusbar(self):
		self["IFtext"].setText(_("Network:"))
		self["IF"].setText(iNetwork.getFriendlyAdapterName(self.iface))
		self["Statustext"].setText(_("Link:"))
		if iNetwork.isWirelessInterface(self.iface):
			try:
				self.iStatus.getDataForInterface(self.iface, self.getInfoCB)
			except:
				self["statuspic"].setPixmapNum(1)
				self["statuspic"].show()
		else:
			iNetwork.getLinkState(self.iface, self.dataAvail)

	def dataAvail(self, data):
		data = six.ensure_str(data)
		self.LinkState = None
		for line in data.splitlines():
			line = line.strip()
			if 'Link detected:' in line:
				if "yes" in line:
					self.LinkState = True
				else:
					self.LinkState = False
		if self.LinkState:
			iNetwork.checkNetworkState(self.checkNetworkCB)
		else:
			self["statuspic"].setPixmapNum(1)
			self["statuspic"].show()

	def checkNetworkCB(self, data):
		try:
			if iNetwork.getAdapterAttribute(self.iface, "up") is True:
				if self.LinkState is True:
					if data <= 2:
						self["statuspic"].setPixmapNum(0)
					else:
						self["statuspic"].setPixmapNum(1)
					self["statuspic"].show()
				else:
					self["statuspic"].setPixmapNum(1)
					self["statuspic"].show()
			else:
				self["statuspic"].setPixmapNum(1)
				self["statuspic"].show()
		except:
			self["statuspic"].setPixmapNum(0)
			self["statuspic"].show()

	def createSummary(self):
		return AboutSummary

class NetworkInstalledApp(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Installed Networkplugins"))
		self.skinName = ["SystemNetworkInfo", "About"]
		
		OpenNFRVersion = _("OpenNFR %s") % about.getImageVersionString()
		self["OpenNFRVersion"] = Label(OpenNFRVersion)
		
		self["AboutScrollLabel"] = ScrollLabel()

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
									{
										"cancel": self.close,
										"ok": self.close,
									})
									
		self.AboutText = _("List of Networkplugins with Installedinfo") + '\n\n'
		self.InstallCheck()

	def InstallCheck(self):
		self.Console = Console()
		self.Console.ePopen('/usr/bin/opkg list_installed ', self.checkNetworkState)

	def checkNetworkState(self, str, retval, extra_args):
		import subprocess
		import os
		os.system('ps -ef > /tmp/ps.txt')
		ftp_process = subprocess.getoutput("grep -i vsftpd /tmp/ps.txt")
		telnetd_process = subprocess.getoutput("grep -i telnetd /tmp/ps.txt")
		ipv6_process = subprocess.getoutput("cat /proc/sys/net/ipv6/conf/all/disable_ipv6")		                
		afp_process = subprocess.getoutput("grep -i afpd /tmp/ps.txt")                
		sabnzbd_process = subprocess.getoutput("grep -i SABnzbd /tmp/ps.txt")               
		nfs_process = subprocess.getoutput("grep -i nfsd /tmp/ps.txt")               
		openvpn_process = subprocess.getoutput("grep -i openvpn /tmp/ps.txt")                
		samba_process = subprocess.getoutput("grep -i smbd /tmp/ps.txt")              
		inadyn_process = subprocess.getoutput("grep -i inadyn-mt /tmp/ps.txt")
		ushare_process = subprocess.getoutput("grep -i ushare /tmp/ps.txt")               
		minidlna_process = subprocess.getoutput("grep -i minidlnad /tmp/ps.txt")
		str = six.ensure_str(str)
		xtext1 = _(": \t    Installed and running") + "\n"		
		xtext2 = _(": \t    Installed and not running") + "\n"		
		
		if ftp_process:	
			self.AboutText += _("FTP") + xtext1
		else:                                
			self.AboutText += _("FTP") + xtext2
		if telnetd_process:	
			self.AboutText += _("Telnet") + xtext1
		else:                                
			self.AboutText += _("Telnet") + xtext2
		if ipv6_process == "0":	
			self.AboutText += _("IPV6") + xtext1
		else:                                
			self.AboutText += _("IPV6") + xtext2               		
		if '-appletalk netatalk' in str:
			if afp_process:	
				self.AboutText += _("Appletalk Netatalk") + xtext1
			else:                                
				self.AboutText += _("Appletalk Netatalk") + xtext2
		if 'sabnzbd3' in str:
			if sabnzbd_process:	
				self.AboutText += _("SABnzbd") + xtext1
			else:                                
				self.AboutText += _("SABnzbd") + xtext2
		if '-nfs' in str:
			if nfs_process:	
				self.AboutText += _("NFS") + xtext1
			else:                                
				self.AboutText += _("NFS") + xtext2
		if 'openvpn' in str:
			if openvpn_process:	
				self.AboutText += _("OpenVPN") + xtext1
			else:                                
				self.AboutText += _("OpenVPN") + xtext2
		if '-smbfs-server' in str:
			if samba_process:	
				self.AboutText += _("Samba") + xtext1
			else:                                
				self.AboutText += _("Samba") + xtext2
		if 'inadyn-mt' in str:
			if inadyn_process:	
				self.AboutText += _("Inadyn") + xtext1
			else:                                
				self.AboutText += _("Inadyn") + xtext2
		if 'ushare' in str:
			if ushare_process:	
				self.AboutText += _("uShare") + xtext1
			else:                                
				self.AboutText += _("uShare") + xtext2
		if 'minidlna' in str:
			if minidlna_process:	
				self.AboutText += _("MiniDLNA") + xtext1
			else:                                
				self.AboutText += _("MiniDLNA") + xtext2
		self["AboutScrollLabel"].setText(self.AboutText)			

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.close,
				"ok": self.close,
			})
			
class AboutSummary(Screen):
	def __init__(self, session, parent):
		Screen.__init__(self, session, parent = parent)
		self["selected"] = StaticText("About")

class ViewGitLog(Screen):
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.skinName = "SoftwareUpdateChanges"
		self.setTitle(_("OE Changes"))
		self.logtype = 'oe'
		self["text"] = ScrollLabel()
		self['title_summary'] = StaticText()
		self['text_summary'] = StaticText()
		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("OK"))
		self["key_yellow"] = Button(_("Show E2 Log"))
		self["myactions"] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions'],
									{
										  'cancel': self.closeRecursive,
										  'green': self.closeRecursive,
										  "red": self.closeRecursive,
										  "yellow": self.changelogtype,
										  "left": self.pageUp,
										  "right": self.pageDown,
										  "down": self.pageDown,
										  "up": self.pageUp
									}, -1)
		self.onLayoutFinish.append(self.getlog)

	def changelogtype(self):
		if self.logtype == 'oe':
			self["key_yellow"].setText(_("Show OE Log"))
			self.setTitle(_("Enimga2 Changes"))
			self.logtype = 'e2'
		else:
			self["key_yellow"].setText(_("Show E2 Log"))
			self.setTitle(_("OE Changes"))
			self.logtype = 'oe'
		self.getlog()

	def pageUp(self):
		self["text"].pageUp()

	def pageDown(self):
		self["text"].pageDown()

	def getlog(self):
		fd = open('/etc/' + self.logtype + '-git.log', 'r')
		releasenotes = fd.read()
		fd.close()
		releasenotes = releasenotes.replace('\nopenvix: build', "\n\nopenvix: build")
		self["text"].setText(releasenotes)
		summarytext = releasenotes
		try:
			self['title_summary'].setText(summarytext[0] + ':')
			self['text_summary'].setText(summarytext[1])
		except:
			self['title_summary'].setText("")
			self['text_summary'].setText("")

	def unattendedupdate(self):
		self.close((_("Unattended upgrade without GUI and reboot system"), "cold"))

	def closeRecursive(self):
		self.close((_("Cancel"), ""))

class TranslationInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		# don't remove the string out of the _(), or it can't be "translated" anymore.

		# TRANSLATORS: Add here whatever should be shown in the "translator" about screen, up to 6 lines (use \n for newline)
		info = _("TRANSLATOR_INFO")

		if info == "TRANSLATOR_INFO":
			info = "(N/A)"

		infolines = _("").split("\n")
		infomap = {}
		for x in infolines:
			l = x.split(': ')
			if len(l) != 2:
				continue
			(type, value) = l
			infomap[type] = value
		print(infomap)

		self["TranslationInfo"] = StaticText(info)

		translator_name = infomap.get("Language-Team", "none")
		if translator_name == "none":
			translator_name = infomap.get("Last-Translator", "")

		self["TranslatorName"] = StaticText(translator_name)

		self["actions"] = ActionMap(["SetupActions"],
									{
										"cancel": self.close,
										"ok": self.close,
									})
