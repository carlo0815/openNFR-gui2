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
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import os
from enigma import eListboxPythonMultiContent, gFont
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Screens.Standby import *

config.opennfrwizard = ConfigSubsection()
config.opennfrwizard.enablewebinterface = ConfigYesNo(default=False)
config.opennfrwizard.enablemediacenter = ConfigYesNo(default=False)
config.opennfrwizard.enableskalliskin = ConfigYesNo(default=False)
config.opennfrwizard.enablemainmenu2 = ConfigYesNo(default=False)
config.opennfrwizard.enablehbbtv = ConfigYesNo(default=False)
config.opennfrwizard.enable3gmodems = ConfigYesNo(default=False)
config.opennfrwizard.enableWifiDrivers = ConfigYesNo(default=False)
config.opennfrwizard.dsemudmessages = ConfigYesNo(default=False)
config.opennfrwizard.firmwaremicom = ConfigYesNo(default=False)



class OpenNFRWizardSetup(ConfigListScreen, Screen):
    __module__ = __name__
    def __init__(self, session, args = 0):
	Screen.__init__(self, session)
	self.skinName = ["Setup"]
		
        list = []
	list.append(getConfigListEntry(_('Enable OpenNfr Webinterface ?'), config.opennfrwizard.enablewebinterface))
	list.append(getConfigListEntry(_('Enable OpenNfr MediaCenter ?'), config.opennfrwizard.enablemediacenter))
	list.append(getConfigListEntry(_('Enable OpenNfr Skalli Skin mod bei Blasser ?'), config.opennfrwizard.enableskalliskin))
	list.append(getConfigListEntry(_('Enable OpenNfr MainMenu2 ?'), config.opennfrwizard.enablemainmenu2))		
	list.append(getConfigListEntry(_('Enable HBBTV ?'), config.opennfrwizard.enablehbbtv))

        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Save"))
        self['label1'] = Label(_('Bei Install dieser Plugins kann es bei zu wenig Flashspeicher zu Problemen kommen \n\nDas Image koennte platzen!'))
		 
        ConfigListScreen.__init__(self, list) 
        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions'], {'green': self.run, 'red' : self.dontSaveAndExit,
         'cancel': self.dontSaveAndExit}, -1)

    def run(self):
	cmd = ""
	webinstall = "0"
	if config.opennfrwizard.enablewebinterface.value is True:
	        webinstall = "1"
                cmd += "opkg install --force-overwrite enigma2-plugin-extensions-webinterface-nfrmod;"
	else:
		cmd += "opkg remove --force-depends enigma2-plugin-extensions-webinterface-nfrmod;"

	if config.opennfrwizard.enablemediacenter.value is True:
		cmd += "opkg install --force-overwrite enigma2-plugin-extensions-bmediacenter;"
	else:
		cmd += "opkg remove --force-depends enigma2-plugin-extensions-bmediacenter;"

	if config.opennfrwizard.enableskalliskin.value is True:
		cmd += "opkg install --force-overwrite enigma2-plugin-skins-skallihd-fullhd;"
	else:
		cmd += "opkg remove --force-depends enigma2-plugin-skins-skallihd-fullhd;"

	if config.opennfrwizard.enablemainmenu2 is True:
		cmd += "opkg install --force-overwrite enigma2-plugin-extensions-mainmenu2;"
	else:
		cmd += "opkg remove --force-depends enigma2-plugin-extensions-mainmenu2;"	
	
	if config.opennfrwizard.enablehbbtv.value is True:
		cmd += "opkg install --force-overwrite tslib-conf libts-1.0-0 libsysfs2 libgmp10 libmpfr4 vuplus-opera-browser-util enigma2-plugin-extensions-hbbtv-opennfr-fullhd;"
	else:
		cmd += "opkg remove --force-depends tslib-conf libts-1.0-0 libsysfs2 libgmp10 libmpfr4 vuplus-opera-browser-util enigma2-plugin-extensions-hbbtv-opennfr-fullhd;"

        for x in self['config'].list:
            x[1].save()

	config.opennfrwizard.save()
	self.session.open(Console, title = _("Please wait configuring OpenNFR Image"), cmdlist = [cmd], finishedCallback = None, closeOnSuccess = True)
	plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))

	if webinstall == "1":
		quitMainloop(3)
	else:
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
