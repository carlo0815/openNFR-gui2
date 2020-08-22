# -*- coding: utf-8 -*-
from Components.ActionMap import *
from Components.config import *
from Components.ConfigList import *
from Components.UsageConfig import *
from Components.Label import Label
from Components.UsageConfig import *
from Screens.Screen import Screen
from Components.Sources.StaticText import StaticText
from Components.Network import iNetwork
from Components.Ipkg import IpkgComponent
from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
from Screens.Console import Console
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
from os import popen, system, remove, listdir, chdir, getcwd, statvfs, mkdir, path, walk
from enigma import eListboxPythonMultiContent, gFont
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
import shutil
from Components.ConfigList import ConfigListScreen
from traceback import print_exc
from Tools.Import import my_import

config.opennfrwizard = ConfigSubsection()
config.opennfrwizard.enablewebinterface = ConfigYesNo(default=False)
config.opennfrwizard.enablemediacenter = ConfigYesNo(default=False)
config.opennfrwizard.enableskalliskin = ConfigYesNo(default=False)
config.opennfrwizard.enablemainmenu2 = ConfigYesNo(default=False)

config.opennfrupdate = ConfigSubsection()
config.opennfrupdate.enablecheckupdate = ConfigYesNo(default=True)

def getVarSpaceKb():
	try:
		s = statvfs('/')
	except OSError:
		return (0, 0)

	return (float(s.f_bfree * (s.f_bsize / 1024)), float(s.f_blocks * (s.f_bsize / 1024)))

class OpenNFRWizardSetup(ConfigListScreen, Screen):
	__module__ = __name__
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		self.skinName = ["Setup"]
		self['spaceused'] = ProgressBar()
		self["status"] = ScrollLabel()
		self.onShown.append(self.setWindowTitle)

		list = []
		list.append(getConfigListEntry(_('Enable OpenNfr MediaCenter ?'), config.opennfrwizard.enablemediacenter))
		list.append(getConfigListEntry(_('Enable OpenNfr Skalli-FullHD-Mod  Skin mod by Blasser ?'), config.opennfrwizard.enableskalliskin))
		list.append(getConfigListEntry(_('Enable OpenNfr MainMenu2 ?'), config.opennfrwizard.enablemainmenu2))		
		list.append(getConfigListEntry(_('Enable OpenNfr Webinterface ?'), config.opennfrwizard.enablewebinterface)) 

		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Save"))
		self['label1'] = Label(_('IF you install this Plugins with not enough Flashmemory it comes to trouble\nThe image could be destroyed!\n\nWebInterface 3.6MB\nBMediacenter 6.4MB\nSkalli 4.5MB\nMainmenu2 3.6MB'))
		self['label2'] = Label(_('% Flash Used....'))
		self['label3'] = Label(_('Warning!!!  If you select No, Existing Installations will be deleted!!'))

		ConfigListScreen.__init__(self, list) 
		self['actions'] = ActionMap(['OkCancelActions',
		'ColorActions'], {'red': self.dontSaveAndExit, 'green' : self.run,
		'cancel': self.dontSaveAndExit}, -1)

	def ConvertSize(self, size):
		size = int(size)
		if size >= 1073741824:
			Size = '%0.2f TB' % (size / 1073741824.0)
		elif size >= 1048576:
			Size = '%0.2f GB' % (size / 1048576.0)
		elif size >= 1024:
			Size = '%0.2f MB' % (size / 1024.0)
		else:
			Size = '%0.2f KB' % size
		return str(Size)

	def setWindowTitle(self):
		diskSpace = getVarSpaceKb()
		percFree = int(diskSpace[0] / diskSpace[1] * 100)
		percUsed = int((diskSpace[1] - diskSpace[0]) / diskSpace[1] * 100)
		self.setTitle('%s - %s: %s (%d%%)' % (_('Setup'),
		_('Free'),
		self.ConvertSize(int(diskSpace[0])),
		percFree))
		self['spaceused'].setValue(percUsed)

	def run(self):
		cmd = "opkg update;"
		if config.opennfrwizard.enablemediacenter.value is True:
			cmd += "opkg install --force-overwrite enigma2-plugin-extensions-bmediacenter;"	
		else:	
			cmd += "opkg remove --force-depends enigma2-plugin-extensions-bmediacenter;"
			if  os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter"):
				shutil.rmtree("/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter")

			if config.opennfrwizard.enableskalliskin.value is True:
				cmd += "opkg install --force-overwrite enigma2-plugin-skins-skallihd-fullhd;"
			else:
				cmd += "opkg remove --force-depends enigma2-plugin-skins-skallihd-fullhd;"
			if  os.path.exists("/usr/share/enigma2/SkalliHD-NFR-FullHD"):
				shutil.rmtree("/usr/share/enigma2/SkalliHD-NFR-FullHD")

			if config.opennfrwizard.enablemainmenu2.value is True:	
				cmd += "opkg install --force-overwrite enigma2-plugin-extensions-mainmenu2;"
			else:
				cmd += "opkg remove --force-depends enigma2-plugin-extensions-mainmenu2;"
			if  os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/MainMenu2"):
				shutil.rmtree("/usr/lib/enigma2/python/Plugins/Extensions/MainMenu2")
			if config.opennfrwizard.enablewebinterface.value is True:
				cmd += "opkg install --force-overwrite enigma2-plugin-extensions-webinterface-nfrmod;"
			else:
				cmd += "opkg remove --force-depends enigma2-plugin-extensions-webinterface-nfrmod;"
			if  os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface"):
				shutil.rmtree("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface")
				config.opennfrwizard.save()
				self.session.open(Console, title = _("Please wait configuring OpenNFR Image"), cmdlist = [cmd], finishedCallback = self.reloadPlugin, closeOnSuccess = True)

	def reloadPlugin(self):
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		self.close()

	def dontSaveAndExit(self):
		for x in self['config'].list:
			x[1].cancel()

			self.close()

class InstallWizardIpkgUpdater(Screen):
	def __init__(self, session, info, cmd, pkg = None):
		Screen.__init__(self, session)

		self["statusbar"] = StaticText(info)

		self.pkg = pkg
		self.state = 0
		
		self.ipkg = IpkgComponent()
		self.ipkg.addCallback(self.ipkgCallback)

		self.ipkg.startCmd(cmd, pkg)

	def ipkgCallback(self, event, param):
		if event == IpkgComponent.EVENT_DONE:
			plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
			self.close()

class OpenNFRWizardupdatecheck(ConfigListScreen, Screen):
	__module__ = __name__
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		self.skinName = ["Setup"]
		self['spaceused'] = ProgressBar()
		self["status"] = ScrollLabel()
		self.onShown.append(self.setWindowTitle)

		list = []
		list.append(getConfigListEntry(_('Enable OpenNfr Image-Update-Check?'), config.opennfrupdate.enablecheckupdate))

		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Save"))

		ConfigListScreen.__init__(self, list) 
		self['actions'] = ActionMap(['OkCancelActions',
		'ColorActions'], {'red': self.dontSaveAndExit, 'green' : self.run,
		'cancel': self.dontSaveAndExit}, -1)

	def ConvertSize(self, size):
		size = int(size)
		if size >= 1073741824:
			Size = '%0.2f TB' % (size / 1073741824.0)
		elif size >= 1048576:
			Size = '%0.2f GB' % (size / 1048576.0)
		elif size >= 1024:
			Size = '%0.2f MB' % (size / 1024.0)
		else:
			Size = '%0.2f KB' % size
		return str(Size)

	def setWindowTitle(self):
		diskSpace = getVarSpaceKb()
		percFree = int(diskSpace[0] / diskSpace[1] * 100)
		percUsed = int((diskSpace[1] - diskSpace[0]) / diskSpace[1] * 100)
		self.setTitle('%s - %s: %s (%d%%)' % (_('Setup'),
		_('Free'),
		self.ConvertSize(int(diskSpace[0])),
		percFree))
		self['spaceused'].setValue(percUsed)

	def run(self):
		config.opennfrupdate.save()
		self.close()

	def dontSaveAndExit(self):
		for x in self['config'].list:
			x[1].cancel()

			self.close()
