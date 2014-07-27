from Plugins.SystemPlugins.Hotplug.plugin import hotplugNotifier
from Components.Button import Button
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.FileList import FileList
from Components.Task import Task, Job, job_manager, Condition
from Components.Sources.StaticText import StaticText
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.HelpMenu import HelpableScreen
from Screens.TaskView import JobView
from Tools.Downloader import downloadWithProgress
import urllib2
import os
from Plugins.Extensions.Infopanel.Extra import shutil
import math
from boxbranding import getBoxType,  getImageDistro, getMachineName, getMachineBrand
distro =  getImageDistro()

#############################################################################################################
imagePath = '/media/hdd/images'
flashPath = '/media/hdd/images/flash'
flashTmp = '/media/hdd/images/tmp'
ofgwritePath = '/usr/bin/ofgwrite'
#############################################################################################################



class doFlashImage(Screen):
	skin = """
	<screen position="center,center" size="560,500" title="Flash On the fly (select a image)">
		<ePixmap position="0,460"   zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/red.png" transparent="1" alphatest="on" />
		<ePixmap position="140,460" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/green.png" transparent="1" alphatest="on" />
		<ePixmap position="280,460" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/yellow.png" transparent="1" alphatest="on" />
		<ePixmap position="420,460" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/buttons/blue.png" transparent="1" alphatest="on" />
		<widget name="key_red" position="0,460" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_green" position="140,460" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_yellow" position="280,460" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_blue" position="420,460" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="imageList" position="10,10" zPosition="1" size="450,450" font="Regular;20" scrollbarMode="showOnDemand" transparent="1" />
	</screen>"""
		
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		Screen.setTitle(self, _("Flash On the fly (select a image)"))
		self["key_green"] = Button(_("Flash"))
		self["key_red"] = Button(_("Exit"))
		self["key_blue"] = Button("")
		self["key_yellow"] = Button("")
		#self.check_hdd()
		self.filename = None
		self.imagelist = []
		self.simulate = False
		self.imagePath = imagePath
		self["imageList"] = MenuList(self.imagelist)
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], 
		{
			"green": self.green,
			"yellow": self.yellow,
			"red": self.quit,
			"blue": self.blue,
			"cancel": self.quit,
		}, -2)
		self.onLayoutFinish.append(self.layoutFinished)
			

		
	def quit(self):
		self.close()	
		
	def blue(self):
		sel = self["imageList"].l.getCurrentSelection()
		if sel == None:
			print"Nothing to select !!"
			return
		self.filename = sel
		self.session.openWithCallback(self.RemoveCB, MessageBox, _("Do you really want to delete\n%s ?") % (sel), MessageBox.TYPE_YESNO)

	def RemoveCB(self, ret):
		if ret:
			if os.path.exists(self.imagePath + "/" + self.filename):
				os.remove(self.imagePath + "/" + self.filename)
			self.imagelist.remove(self.filename)
			self["imageList"].l.setList(self.imagelist)
		
	def box(self):
		box = getBoxType()
		machinename = getMachineName()
		if box == 'odinm6':
			box = getMachineName().lower()
		elif box == "inihde" and machinename.lower() == "xpeedlx":
			box = "xpeedlx"
		elif box == "xpeedlx1" or box == "xpeedlx2":
			box = "xpeedlx"
		elif box == "inihde" and machinename.lower() == "hd-1000":
			box = "sezam-1000hd"
		elif box == "ventonhdx" and machinename.lower() == "hd-5000":
			box = "sezam-5000hd"
		elif box == "ventonhdx" and machinename.lower() == "premium twin":
			box = "miraclebox-twin"
		elif box == "xp1000" and machinename.lower() == "sf8 hd":
			box = "sf8"
		elif box.startswith('et') and not box == "et10000":
			box = box[0:3] + 'x00'
		elif box == 'odinm9' and self.feed == "atv2":
			box = 'maram9'
		return box

	def green(self):
		sel = self["imageList"].l.getCurrentSelection()
		if sel == None:
			print"Nothing to select !!"
			return
		file_name = self.imagePath + "/" + sel
		self.filename = file_name
		box = self.box()
		self.hide()
		if sel == str(flashTmp):
			self.Start_Flashing()
		else:
			self.unzip_image(self.filename, flashPath)

	def askUnzipCB(self, ret):
		if ret:
			self.unzip_image(self.filename, flashPath)
		else:
			self.show()

	def unzip_image(self, filename, path):
		print "Unzip %s to %s" %(filename,path)
		self.session.openWithCallback(self.cmdFinished, Console, title = _("Unzipping files, Please wait ..."), cmdlist = ['unzip ' + filename + ' -d ' + path, "sleep 3"], closeOnSuccess = True)

	def cmdFinished(self):
		self.prepair_flashtmp(flashPath)
		self.Start_Flashing()

	def Start_Flashing(self):
		print "Start Flashing"
		if os.path.exists(ofgwritePath):
			text = _("Flashing: ")
			if self.simulate:
				text += _("Simulate (no write)")
				cmd = "%s -n -r -k %s > /dev/null 2>&1" % (ofgwritePath, flashTmp)
				self.close()
				message = "echo -e '\n"
				message += _('Show only found image and mtd partitions.\n')
				message += "'"
			else:
				text += _("root and kernel")
				cmd = "%s -r -k %s > /dev/null 2>&1" % (ofgwritePath, flashTmp)
				message = "echo -e '\n"
				message += _('ofgwrite will stop enigma2 now to run the flash.\n')
				message += _('Your STB will freeze during the flashing process.\n')
				message += _('Please: DO NOT reboot your STB and turn off the power.\n')
				message += _('The image or kernel will be flashing and auto booted in few minutes.\n')
				if self.box() == 'gb800solo':
					message += _('GB800SOLO takes about 20 mins !!\n')
				message += "'"
			self.session.open(Console, text,[message, cmd])

	def prepair_flashtmp(self, tmpPath):
		if os.path.exists(flashTmp):
			os.system('rm -rf ' + flashTmp)
		os.mkdir(flashTmp)
		kernel = True
		rootfs = True
		
		for path, subdirs, files in os.walk(tmpPath):
			for name in files:
				if name.find('kernel') > -1 and name.endswith('.bin') and kernel:
					binfile = os.path.join(path, name)
					dest = flashTmp + '/kernel.bin'
					shutil.copyfile(binfile, dest)
					kernel = False
				elif name.find('root') > -1 and (name.endswith('.bin') or name.endswith('.jffs2')) and rootfs:
					binfile = os.path.join(path, name)
					dest = flashTmp + '/rootfs.bin'
					shutil.copyfile(binfile, dest)
					rootfs = False
					
	def yellow(self):
			self.session.openWithCallback(self.DeviceBrowserClosed, DeviceBrowser, None, matchingPattern="^.*\.(zip|bin|jffs2)", showDirectories=True, showMountpoints=True, inhibitMounts=["/autofs/sr0/"])

	def DeviceBrowserClosed(self, path, filename, binorzip):
		if path:
			print path, filename, binorzip
			strPath = str(path)
			if strPath[-1] == '/':
				strPath = strPath[:-1]
			self.imagePath = strPath
			if os.path.exists(flashTmp):
				os.system('rm -rf ' + flashTmp)
			os.mkdir(flashTmp)
			if binorzip == 0:
				for files in os.listdir(self.imagePath):
					if files.endswith(".bin") or files.endswith('.jffs2'):
						self.prepair_flashtmp(strPath)
						break
				self.Start_Flashing()
			elif binorzip == 1:
				self.unzip_image(strPath + '/' + filename, flashPath)
			else:
				self.layoutFinished()
	
		else:
			self.imagePath = imagePath

	def layoutFinished(self):
		box = self.box()
		self.imagelist = []
		self["key_blue"].setText(_("Delete"))
		self["key_yellow"].setText(_("Devices"))
		for name in os.listdir(self.imagePath):
			if name.endswith(".zip"): # and name.find(box) > 1:
				self.imagelist.append(name)
		self.imagelist.sort()
		if os.path.exists(flashTmp):
			for file in os.listdir(flashTmp):
				if file.find(".bin") > -1:
					self.imagelist.insert( 0, str(flashTmp))
					break

		self["imageList"].l.setList(self.imagelist)


class DeviceBrowser(Screen, HelpableScreen):
	skin = """
		<screen name="DeviceBrowser" position="center,center" size="520,430" >
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/green.png" position="140,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="message" render="Label" position="5,50" size="510,150" font="Regular;16" />
			<widget name="filelist" position="5,210" size="510,220" scrollbarMode="showOnDemand" />
		</screen>"""

	def __init__(self, session, startdir, message="", showDirectories = True, showFiles = True, showMountpoints = True, matchingPattern = "", useServiceRef = False, inhibitDirs = False, inhibitMounts = False, isTop = False, enableWrapAround = False, additionalExtensions = None):
		Screen.__init__(self, session)

		HelpableScreen.__init__(self)
		Screen.setTitle(self, _("Please select medium"))

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText()
		self["message"] = StaticText(message)

		self.filelist = FileList(startdir, showDirectories = showDirectories, showFiles = showFiles, showMountpoints = showMountpoints, matchingPattern = matchingPattern, useServiceRef = useServiceRef, inhibitDirs = inhibitDirs, inhibitMounts = inhibitMounts, isTop = isTop, enableWrapAround = enableWrapAround, additionalExtensions = additionalExtensions)
		self["filelist"] = self.filelist

		self["FilelistActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"green": self.use,
				"red": self.exit,
				"ok": self.ok,
				"cancel": self.exit
			})

		hotplugNotifier.append(self.hotplugCB)
		self.onShown.append(self.updateButton)
		self.onClose.append(self.removeHotplug)

	def hotplugCB(self, dev, action):
		print "[hotplugCB]", dev, action
		self.updateButton()

	def updateButton(self):

		if self["filelist"].getFilename() or self["filelist"].getCurrentDirectory():
			self["key_green"].text = _("Flash")
		else:
			self["key_green"].text = ""

	def removeHotplug(self):
		print "[removeHotplug]"
		hotplugNotifier.remove(self.hotplugCB)

	def ok(self):
		if self.filelist.canDescent():
			if self["filelist"].showMountpoints == True and self["filelist"].showDirectories == False:
				self.use()
			else:
				self.filelist.descent()

	def use(self):
		print "[use]", self["filelist"].getCurrentDirectory(), self["filelist"].getFilename()
		if self["filelist"].getFilename() is not None and self["filelist"].getCurrentDirectory() is not None:
			if self["filelist"].getFilename().endswith(".bin") or self["filelist"].getFilename().endswith(".jffs2"):
				self.close(self["filelist"].getCurrentDirectory(), self["filelist"].getFilename(), 0)
			elif self["filelist"].getFilename().endswith(".zip"):
				self.close(self["filelist"].getCurrentDirectory(), self["filelist"].getFilename(), 1)
			else:
				return

	def exit(self):
		self.close(False, False, -1)
