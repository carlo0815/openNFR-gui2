# -*- coding: utf-8 -*-
#
#  swapmanager
#
#  $Id: plugin.py,v 0.1 2010/04/18 15:49:00 dre Exp $
#
#  Coded by dre (c) 2010
#  Coding idea and design by dre
#  Support: www.dreambox-tools.info
#
#  This plugin is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
#  Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.

#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially 
#  distributed other than under the conditions noted above.
#

from Components.ActionMap import *
from Components.ChoiceList import ChoiceList
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.config import config, ConfigSelection, ConfigSubsection, ConfigInteger, getConfigListEntry, ConfigYesNo
from Plugins.Plugin import PluginDescriptor
from Screens.HelpMenu import HelpableScreen
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.Directories import fileExists

from enigma import loadPNG,  eConsoleAppContainer

import os

# for localized messages
#from . import _

choicelist = [("8192",_("8 MB")), ("16384",_("16 MB")), ("32768",_("32 MB")), ("65536",_("64 MB")), ("131072",_("128 MB")), ("262144",_("256 MB")), ("524288",_("512 MB")), ("1048576",_("1024 MB"))]
mountlist = [("/media/hdd",_("/media/hdd")), ("/media/cf",_("/media/cf")), ("/media/usb",_("/media/usb"))]
filenamelist = [("swap",_("swap")), ("swapfile",_("swapfile")), ("myswap",_("myswap"))]

config.plugins.swapmanager = ConfigSubsection()
config.plugins.swapmanager.mountpoint = ConfigSelection(choices = mountlist, default = "/media/hdd")
config.plugins.swapmanager.filename = ConfigSelection(choices = filenamelist, default = "swap")
config.plugins.swapmanager.filesize = ConfigSelection(choices = choicelist, default="8192")
config.plugins.swapmanager.activateonboot = ConfigYesNo(default=False)
config.plugins.swapmanager.mkswapcount = ConfigInteger(0)

def writeAttributes(attribute, value):
	try:
		buf = []
		script = open('/etc/init.d/swap', 'r')
		for line in script:
			for x in range(len(attribute)):
				if attribute[x] in line:
					attrib = line.strip().split('=')
					if attrib[0] == 'SWAP':
						line = attrib[0].strip() + '=' + str(value[x]) + '\n'
			buf.append(line)
		script.close()
	except IOError:
		print "IOError"
		pass
		return -1

	script = open('/etc/init.d/swap', 'w')	
	for line in buf:
		script.write(line)
	script.close()
	return 1

class SwapOverviewScreen(Screen,ConfigListScreen, HelpableScreen):
	skin= """
		<screen name="SwapOverviewScreen" position="center,center" size="520,360" title="Swap Manager - Overview">
			<widget name="config" position="10,10" size="500,150" scrollbarMode="showOnDemand" />
			<widget name="swapstatus_label" position="10,250" size="250,30" foregroundColor="white" font="Regular;20" />
			<widget name="swapstatus_status" position="260,250" size="250,30" halign="right" foregroundColor="white" font="Regular;20" />
			<widget name="ButtonRedtext" position="30,280" size="230,40" valign="center" halign="left" zPosition="10" font="Regular;18" transparent="1" />
			<widget name="ButtonRed" pixmap="skin_default/buttons/red.png" position="10,290" zPosition="10" size="16,16" transparent="1" alphatest="on" />
			<widget name="ButtonGreentext" position="280,280" size="230,40" valign="center" halign="left" zPosition="10" font="Regular;18" transparent="1" />
			<widget name="ButtonGreen" pixmap="skin_default/buttons/green.png" position="260,290" zPosition="10" size="16,16" transparent="1" alphatest="on" />
			<widget name="ButtonYellowtext" position="30,320" size="230,40" valign="center" halign="left" zPosition="10" font="Regular;18" transparent="1" />
			<widget name="ButtonYellow" pixmap="skin_default/buttons/yellow.png" position="10,330" zPosition="10" size="16,16" transparent="1" alphatest="on" />
			<widget name="ButtonBluetext" position="280,320" size="230,40" valign="center" halign="left" zPosition="10" font="Regular;18" transparent="1" />
			<widget name="ButtonBlue" pixmap="skin_default/buttons/blue.png" position="260,330" zPosition="10" size="16,16" transparent="1" alphatest="on" />
		</screen>"""
	
	def __init__(self,session,args=0):
		Screen.__init__(self,session)
		HelpableScreen.__init__(self)
		self.session = session

		self["WizardActions"] = HelpableActionMap(self, "WizardActions",
		{
			"back":		(self.close, _("Close plugin")),
		}, -1)

		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
		{
			"red":		(self.deleteSwap,_("Delete swap file")),
			"green":	(self.activateSwap,_("Activate swap")),
			"yellow":	(self.deactivateSwap,_("Deactivate swap")),
			"blue":		(self.createSwap,_("Create swap file")),
		}, -1)			

		self["swapstatus_label"] = Label()
		self["swapstatus_status"] = Label()
		
		self["swapstatus_label"].setText(_("Swap status:"))

		self["ButtonRed"] = Pixmap()
		self["ButtonRedtext"] = Label(_("Delete swap file"))
		self["ButtonGreen"] = Pixmap()
		self["ButtonGreentext"] = Label(_("Activate swap"))
		self["ButtonYellow"] = Pixmap()
		self["ButtonYellowtext"] = Label(_("Deactivate swap"))
		self["ButtonBlue"] = Pixmap()
		self["ButtonBluetext"] = Label(_("Create swap file"))

		self.list = []

		self.list.append(getConfigListEntry(_("Mount point:"), config.plugins.swapmanager.mountpoint))
		self.list.append(getConfigListEntry(_("Filename:"), config.plugins.swapmanager.filename))
		self.list.append(getConfigListEntry(_("Filesize:"), config.plugins.swapmanager.filesize))
		self.list.append(getConfigListEntry(_("Activate boot on startup:"), config.plugins.swapmanager.activateonboot))

		config.plugins.swapmanager.mountpoint.addNotifier(self.saveSettings)
		config.plugins.swapmanager.filename.addNotifier(self.saveSettings)
		config.plugins.swapmanager.filesize.addNotifier(self.saveSettings)
		config.plugins.swapmanager.activateonboot.addNotifier(self.updateScript)

		ConfigListScreen.__init__(self, self.list)

		self["config"].setList(self.list)

		self.searchSwap()

	def searchSwap(self):
		if fileExists("%s/%s" %(config.plugins.swapmanager.mountpoint.value, config.plugins.swapmanager.filename.value)):
			#hide create button
			self["ButtonBlue"].hide()
			self["ButtonBluetext"].hide()
			self.checkActivationStatus()
		else:
			#hide delete button
			self["ButtonRed"].hide()
			self["ButtonRedtext"].hide()
			#hide activate button
			self["ButtonGreen"].hide()
			self["ButtonGreentext"].hide()
			#hide deactivate button
			self["ButtonYellow"].hide()
			self["ButtonYellowtext"].hide()
			#show create button
			self["ButtonBlue"].show()
			self["ButtonBluetext"].show()
			#hide labels with swap status
			self["swapstatus_label"].hide()
			self["swapstatus_status"].hide()

	def checkActivationStatus(self):
		self["swapstatus_label"].show()
		self["swapstatus_status"].show()
		self["swapstatus_status"].setText(_("Swap is not activated"))
		#hide deactivate button
		self["ButtonYellow"].hide()
		self["ButtonYellowtext"].hide()
		#show activate button
		self["ButtonGreen"].show()
		self["ButtonGreentext"].show()
		#show delete button
		self["ButtonRed"].show()
		self["ButtonRedtext"].show()

		try:
			self.pathfile = "%s/%s" %(config.plugins.swapmanager.mountpoint.value, config.plugins.swapmanager.filename.value)
			swapFile = open('/proc/swaps', 'r')
			for line in swapFile:
				if line[0] != '#' and line != '\n' and line[0] != 'F':
					val = line.split(' ')
					if val[0].strip() == self.pathfile:
						self["swapstatus_status"].setText(_("Swap is activated"))
						#hide activate button
						self["ButtonGreen"].hide()
						self["ButtonGreentext"].hide()
						#hide delete button
						self["ButtonRed"].hide()
						self["ButtonRedtext"].hide()
						#show deactivate button
						self["ButtonYellow"].show()
						self["ButtonYellowtext"].show()
						break
			
		except IOError:
			print "didn't read /proc/swaps"

		swapFile.close()

	def deleteSwap(self):
		self.pathfile = "%s/%s" %(config.plugins.swapmanager.mountpoint.value, config.plugins.swapmanager.filename.value)
		cmd = "rm -f %s" %(self.pathfile)
		self.result = os.system(cmd)
		if (int(self.result)/256)==0:
			config.plugins.swapmanager.mkswapcount.value = 0
			config.plugins.swapmanager.mkswapcount.save()
			info = self.session.open(MessageBox,_("The swap file has been deleted"), MessageBox.TYPE_INFO, timeout=5)
			info.setTitle(_("SwapManager"))
			self.searchSwap()
		else:
			error = self.session.open(MessageBox,_("There was an error during the deletion of the swap file"), MessageBox.TYPE_ERROR, timeout=5)
			error.setTitle(_("SwapManager"))

	def activateSwap(self):
		self.pathfile = "%s/%s" %(config.plugins.swapmanager.mountpoint.value, config.plugins.swapmanager.filename.value)
		if not config.plugins.swapmanager.mkswapcount.value:
			cmd = "mkswap %s" %(self.pathfile)
			self.result = os.system(cmd)
			if (int(self.result)/256)!=0:
				error = self.session.open(MessageBox,_("There was an error during mkswap"), MessageBox.TYPE_ERROR, timeout=5)
				error.setTitle(_("SwapManager"))
			else:
				config.plugins.swapmanager.mkswapcount.value = 1
				config.plugins.swapmanager.mkswapcount.save()

		if config.plugins.swapmanager.mkswapcount.value:
			cmd = "swapon %s" %(self.pathfile)
			self.result = os.system(cmd)
			if (int(self.result)/256)==0:
				info = self.session.open(MessageBox,_("The swap has been activated"), MessageBox.TYPE_INFO, timeout=5)
				info.setTitle(_("SwapManager"))
				os.system("echo 0 > /proc/sys/vm/swappiness")
				self.checkActivationStatus()
			else:
				error = self.session.open(MessageBox,_("There was an error during the activation"), MessageBox.TYPE_ERROR, timeout=5)
				error.setTitle(_("SwapManager"))

	def deactivateSwap(self):
		self.pathfile = "%s/%s" %(config.plugins.swapmanager.mountpoint.value, config.plugins.swapmanager.filename.value)
		cmd = "swapoff %s" %(self.pathfile)
		self.result = os.system(cmd)
		if (int(self.result)/256)==0:
			info = self.session.open(MessageBox,_("The swap has been deactivated"), MessageBox.TYPE_INFO, timeout=5)
			info.setTitle(_("SwapManager"))
			self.checkActivationStatus()
		else:
			error = self.session.open(MessageBox,_("There was an error during the deactivation"), MessageBox.TYPE_ERROR, timeout=5)
			error.setTitle(_("SwapManager"))

	def createSwap(self):
		self.size = int(config.plugins.swapmanager.filesize.value)
		self.pathfile = "%s/%s" %(config.plugins.swapmanager.mountpoint.value, config.plugins.swapmanager.filename.value)
		self.mount = "%s" %(config.plugins.swapmanager.mountpoint.value)
		if (os.path.ismount(self.mount)):
			cmd = "dd if=/dev/zero of=%s bs=1024 count=%d" %(self.pathfile, self.size)
			self.result = os.system(cmd)
			if (int(self.result)/256)==0:
				info = self.session.open(MessageBox,_("The swap file has been created"), MessageBox.TYPE_INFO, timeout=5)
				info.setTitle(_("SwapManager"))
				self.searchSwap()
			else:
				error = self.session.open(MessageBox,_("There was an error during the creation of the swap file"), MessageBox.TYPE_ERROR, timeout=5)
				error.setTitle(_("SwapManager"))
		else:
			error = self.session.open(MessageBox,_("Could not create swap because the selected device is not mounted."), MessageBox.TYPE_ERROR, timeout=5)
			error.setTitle(_("SwapManager"))

	def saveSettings(self,configElement):
		for x in self.list:
			x[1].save()
		self.searchSwap()

	def updateScript(self, configElement):
		self.run = 0
		self.cmdlist = []
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		if configElement.value == False:
			self.cmdlist.append("update-rc.d -f swap remove")
		elif configElement.value == True:
			self.pathfile = "%s/%s" %(config.plugins.swapmanager.mountpoint.value, config.plugins.swapmanager.filename.value)
			self.returncode = writeAttributes(['SWAP'], [self.pathfile])
			if self.returncode == -1:
				info = self.session.open(MessageBox,_("/etc/init.d/swap not found or write error!"), MessageBox.TYPE_ERROR, timeout=5)
				info.setTitle(_("SwapManager"))
			elif self.returncode == 1:
				self.cmdlist.append("update-rc.d swap defaults 19")
		self.container.execute(self.cmdlist[self.run])
		config.plugins.swapmanager.activateonboot.save()
		
	def dataAvail(self, str):
		print str

	def runFinished(self, retval):
		print "[SwapManager - Command executed] %d" %(retval)
		self.run += 1
		if self.run < len(self.cmdlist):
			self.container.execute(self.cmdlist[self.run])
		else:
			self.run = 0
			self.cmdlist = []

def main(session, **kwargs):
	session.open(SwapOverviewScreen)

def Plugins(**kwargs):
	list = [PluginDescriptor(name="SwapManager",
		description="A plugin to manage a swap",where = [PluginDescriptor.WHERE_PLUGINMENU], icon="plugin.png",fnc=main)]
	return list
