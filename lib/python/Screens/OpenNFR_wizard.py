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

config.opennfrwizard = ConfigSubsection()
config.opennfrwizard.enablehbbtv = ConfigYesNo(default=False)
config.opennfrwizard.enable3gmodems = ConfigYesNo(default=False)
#config.opennfrwizard.enableDLNAServer = ConfigYesNo(default=False)
#config.opennfrwizard.enableDLNABrowser = ConfigYesNo(default=False)
config.opennfrwizard.enableWifiDrivers = ConfigYesNo(default=False)
config.opennfrwizard.dsemudmessages = ConfigYesNo(default=False)
config.opennfrwizard.firmwaremicom = ConfigYesNo(default=False)
#config.opennfrwizard.enableDvbtDrivers = ConfigYesNo(default=False)


class OpenNFRWizardSetup(ConfigListScreen, Screen):
    __module__ = __name__
    def __init__(self, session, args = 0):
	Screen.__init__(self, session)
	self.skinName = ["Setup"]
		
        list = []
	list.append(getConfigListEntry(_('Enable HBBTV ?'), config.opennfrwizard.enablehbbtv))
	list.append(getConfigListEntry(_('Enable 3G / 4G Modems support ?'), config.opennfrwizard.enable3gmodems))
	list.append(getConfigListEntry(_('Enable Firmware Update Plugin ?'), config.opennfrwizard.firmwaremicom))
	#list.append(getConfigListEntry(_('Enable DLNA Server ?'), config.opennfrwizard.enableDLNAServer))
	#list.append(getConfigListEntry(_('Enable DLNA Browser ?'), config.opennfrwizard.enableDLNABrowser))
	list.append(getConfigListEntry(_('Enable WiFi drivers ?'), config.opennfrwizard.enableWifiDrivers))
	#list.append(getConfigListEntry(_('Enable DVB-T/S/C USB drivers ?'), config.opennfrwizard.enableDvbtDrivers))

        self["key_red"] = Label(_("Save"))
        self["key_green"] = Label(_("Exit"))
        	
        ConfigListScreen.__init__(self, list)
        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions'], {'red': self.run, 'green' : self.dontSaveAndExit,
         'cancel': self.dontSaveAndExit}, -1)

    def run(self):
	cmd = ""
	if config.opennfrwizard.enablehbbtv.value is True:
		cmd += "opkg install --force-overwrite tslib-conf libts-1.0-0 libsysfs2 libgmp10 libmpfr4 vuplus-opera-browser-util enigma2-plugin-extensions-inihbbtv;"
	else:
		cmd += "opkg remove --force-depends tslib-conf libts-1.0-0 libsysfs2 libgmp10 libmpfr4 vuplus-opera-browser-util enigma2-plugin-extensions-inihbbtv;"

	if config.opennfrwizard.enable3gmodems.value is True:
		cmd += "opkg install --force-overwrite enigma2-plugin-systemplugins-3gmodemmanager;"
	else:
		cmd += "opkg remove --force-depends ppp usbmodeswitch usbmodeswitch-data wvdial wvstreams libwvutils4.6 libwvstreams-extras libuniconf4.6 kernel-module-ppp-async kernel-module-ppp-deflate kernel-module-ppp-synctty kernel-module-ppp-generic kernel-module-slhc kernel-module-usbserial kernel-module-cdc-acm kernel-module-ppp-mppe kernel-module-pppoe kernel-module-pppox kernel-module-option kernel-module-bsd-comp usbutils enigma2-plugin-systemplugins-3gmodemmanager;"

	if config.opennfrwizard.firmwaremicom.value is True:
		cmd += "opkg install --force-overwrite enigma2-plugin-systemplugins-micomupgrade;"
	else:
		cmd += "opkg remove --force-depends enigma2-plugin-systemplugins-micomupgrade;"
		
	#if config.opennfrwizard.enableDLNAServer.value is True:
	#	cmd += "opkg install --force-overwrite minidlna;"
	#else:
	#	cmd += "opkg remove --force-depends minidlna;"
		
	#if config.opennfrwizard.enableDLNABrowser.value is True:
	#	cmd += "opkg install --force-overwrite djmount;"
	#else:
	#	cmd += "opkg remove --force-depends djmount;"
		
	if config.opennfrwizard.enableWifiDrivers is True:
		cmd += "opkg install --force-overwrite enigma2-plugin-drivers-network-usb-ath9k-htc enigma2-plugin-drivers-network-usb-carl9170 enigma2-plugin-drivers-network-usb-rt2800 enigma2-plugin-drivers-network-usb-rt2500 enigma2-plugin-drivers-network-usb-rtl8187 enigma2-plugin-drivers-network-usb-smsc75xx enigma2-plugin-drivers-network-usb-zd1211rw enigma2-plugin-drivers-network-usb-rtl8192cu enigma2-plugin-drivers-network-usb-rt73 enigma2-plugin-drivers-network-usb-r8712u;"
	else:
		cmd += "opkg remove --force-depends enigma2-plugin-drivers-network-usb-ath9k-htc enigma2-plugin-drivers-network-usb-carl9170 enigma2-plugin-drivers-network-usb-rt2800 enigma2-plugin-drivers-network-usb-rt2500 enigma2-plugin-drivers-network-usb-rtl8187 enigma2-plugin-drivers-network-usb-smsc75xx enigma2-plugin-drivers-network-usb-zd1211rw enigma2-plugin-drivers-network-usb-rtl8192cu enigma2-plugin-drivers-network-usb-rt73 enigma2-plugin-drivers-network-usb-r8712u;"
	  
	#if config.opennfrwizard.enableDvbtDrivers is True:
	#	cmd += "opkg install --force-overwrite enigma2-plugin-drivers-dvb-usb-af9035 enigma2-plugin-drivers-dvb-usb-dib0700 enigma2-plugin-drivers-dvb-usb-af9015 enigma2-plugin-drivers-dvb-usb-it913x enigma2-plugin-drivers-dvb-usb-pctv452e enigma2-plugin-drivers-dvb-usb-dib0700 enigma2-plugin-drivers-usbserial enigma2-plugin-drivers-dvb-usb-dw2102 enigma2-plugin-drivers-dvb-usb-as102;"
	#else:
	#	cmd += "opkg remove --force-depends enigma2-plugin-drivers-dvb-usb-af9035 enigma2-plugin-drivers-dvb-usb-dib0700 enigma2-plugin-drivers-dvb-usb-af9015 enigma2-plugin-drivers-dvb-usb-it913x enigma2-plugin-drivers-dvb-usb-pctv452e enigma2-plugin-drivers-dvb-usb-dib0700 enigma2-plugin-drivers-usbserial enigma2-plugin-drivers-dvb-usb-dw2102 enigma2-plugin-drivers-dvb-usb-as102;"
		
        for x in self['config'].list:
            x[1].save()

	config.opennfrwizard.save()
	self.session.open(Console, title = _("Please wait configuring OpenNFR Image"), cmdlist = [cmd], finishedCallback = None, closeOnSuccess = True)
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

