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

class WebIfConfigScreen(ConfigListScreen, Screen):
	skin = """
		<screen name="WebIfConfigScreen" position="center,center" size="560,400" title="Webinterface: Main Setup">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="config" position="5,50" size="550,360" scrollbarMode="showOnDemand" zPosition="1"/>
		</screen>"""

	def __init__(self, session, args=0):
		Screen.__init__(self, session)
		ConfigListScreen.__init__(self, [])
		self.createSetup()

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		# SKIN Compat HACK!
		self["key_yellow"] = StaticText("")
		# EO SKIN Compat HACK!
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"red": self.cancel,
			"green": self.save,
			"save": self.save,
			"cancel": self.cancel,
			"ok": self.save,
		}, -2)

		self.onLayoutFinish.append(self.layoutFinished)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.createSetup()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.createSetup()

	def createSetup(self):
		list = [ getConfigListEntry(_("Start Webinterface"), config.plugins.Webinterface.enabled), ]

		if config.plugins.Webinterface.enabled.value:
			list.extend( [
				getConfigListEntry(_("Show Setup in Extensions menu"), config.plugins.Webinterface.show_in_extensionsmenu),
				getConfigListEntry(_("Enable /media"), config.plugins.Webinterface.includemedia),
				getConfigListEntry(_("Allow zapping via Webinterface"), config.plugins.Webinterface.allowzapping),
				getConfigListEntry(_("Autowrite timer"), config.plugins.Webinterface.autowritetimer),
				getConfigListEntry(_("Load movie-length"), config.plugins.Webinterface.loadmovielength),
				getConfigListEntry(_("Enable HTTP Access"), config.plugins.Webinterface.http.enabled)
			])

			if config.plugins.Webinterface.http.enabled.value == True:
				list.extend([
					getConfigListEntry(_("HTTP Port"), config.plugins.Webinterface.http.port),
					getConfigListEntry(_("Enable HTTP Authentication"), config.plugins.Webinterface.http.auth)
				])

			list.append( getConfigListEntry(_("Enable HTTPS Access"), config.plugins.Webinterface.https.enabled) )
			if config.plugins.Webinterface.https.enabled.value == True:
				list.extend([
					getConfigListEntry(_("HTTPS Port"), config.plugins.Webinterface.https.port),
					getConfigListEntry(_("Enable HTTPS Authentication"), config.plugins.Webinterface.https.auth)
				])

			#Auth for Streaming (127.0.0.1 Listener)
			list.append(getConfigListEntry(_("Enable Streaming Authentication"), config.plugins.Webinterface.streamauth))
			list.append(getConfigListEntry(_("Simple Anti-Hijack Measures (may break clients)"), config.plugins.Webinterface.anti_hijack))
			list.append(getConfigListEntry(_("Token-based security (may break clients)"), config.plugins.Webinterface.extended_security))
		self["config"].list = list
		self["config"].l.setList(list)

	def layoutFinished(self):
		self.setTitle(_("Webinterface: Main Setup"))

	def save(self):
		print "[Webinterface] Saving Configuration"
		for x in self["config"].list:
			x[1].save()
		self.close()


	def cancel(self):
		print "[Webinterface] Cancel setup changes"
		for x in self["config"].list:
			x[1].cancel()
		self.close()
