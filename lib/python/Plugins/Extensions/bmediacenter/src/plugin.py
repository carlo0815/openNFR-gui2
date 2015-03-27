from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.ConfigList import ConfigList
from Components.config import *
from Components.Console import Console
from skin import loadSkin
from Components.Label import Label
from Screens.Screen import Screen
from Components.Pixmap import Pixmap
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import pathExists, fileExists
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from __init__ import _
import os
import commands
from enigma import getDesktop

config.plugins.mc_global = ConfigSubsection()
config.plugins.mc_global.vfd = ConfigSelection(default='off', choices=[('off', 'off'), ('on', 'on')])
config.plugins.mc_globalsettings.upnp_enable = ConfigYesNo(default=False)
#change to FullHD
if getDesktop(0).size().width() == 1920:
	loadSkin("/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/skins/defaultHD/skinHD.xml")
else:
	loadSkin("/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/skins/defaultHD/skin.xml")
try:
	from enigma import evfd
	config.plugins.mc_global.vfd.value = 'on'
	config.plugins.mc_global.save()
except Exception as e:
	print 'Media Center: Import evfd failed'
try:
	from Plugins.Extensions.DVDPlayer.plugin import *
	dvdplayer = True
except:
	print "Media Center: Import DVDPlayer failed"
        dvdplayer = False

mcpath = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/skins/defaultHD/images/'
class DMC_MainMenu(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self["text"] = Label(_("My Music"))
		self["left"] = Pixmap()
		self["middle"] = Pixmap()
		self["right"] = Pixmap()
		self.Console = Console()
		self.oldbmcService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()
		# Disable OSD Transparency
		try:
			self.can_osd_alpha = open("/proc/stb/video/alpha", "r") and True or False
		except:
			self.can_osd_alpha = False
		if self.can_osd_alpha:
			open("/proc/stb/video/alpha", "w").write(str("255"))
		open("/proc/sys/vm/drop_caches", "w").write(str("3"))
		list = []
		list.append((_("My Music"), "MC_AudioPlayer", "menu_music", "50"))
		list.append((_("My Music"), "MC_AudioPlayer", "menu_music", "50"))
		list.append((_("My Videos"), "MC_VideoPlayer", "menu_video", "50"))
		list.append((_("DVD Player"), "MC_DVDPlayer", "menu_video", "50"))
		list.append((_("My Pictures"), "MC_PictureViewer", "menu_pictures", "50"))
		list.append((_("Web Radio"), "MC_WebRadio", "menu_radio", "50"))
		list.append((_("VLC Player"), "MC_VLCPlayer", "menu_vlc", "50"))
		list.append((_("Weather Info"), "MC_WeatherInfo", "menu_weather", "50"))
		list.append((_("MUZU.TV"), "MUZU.TV", "menu_webmedia", "50"))
		list.append((_("Opera"), "Webbrowser", "menu_webbrowser", "50"))
		list.append((_("SHOUTcast"), "SHOUTcast", "menu_shoutcast", "50"))
		list.append((_("TSMedia"), "TSMedia", "menu_weblinks", "50"))
		list.append((_("Settings"), "MC_Settings", "menu_settings", "50"))
		list.append(("Exit", "Exit", "menu_exit", "50"))
		self["menu"] = List(list)
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"],
		{
			"cancel": self.Exit,
			"ok": self.okbuttonClick,
			"right": self.next,
			"upRepeated": self.prev,
			"down": self.next,
			"downRepeated": self.next,
			"leftRepeated": self.prev,
			"rightRepeated": self.next,
			"up": self.prev,
			"left": self.prev
		}, -1)
		if config.plugins.mc_global.vfd.value == "on":
			evfd.getInstance().vfd_write_string(_("My Music"))
		if config.plugins.mc_globalsettings.upnp_enable.getValue():
			if fileExists("/media/upnp") is False:
				os.mkdir("/media/upnp")
			os.system('djmount /media/upnp &')
	
	def checkNetworkState(self, str, retval, extra_args):
		if 'Collected errors' in str:
			self.session.openWithCallback(self.close, MessageBox, _("A background update check is in progress, please wait a few minutes and try again."), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
		elif not str:
			self.feedscheck = self.session.open(MessageBox,_('Please wait whilst feeds state is checked.'), MessageBox.TYPE_INFO, enable_input = False)
			self.feedscheck.setTitle(_('Checking Feeds'))
			cmd1 = "opkg update"
			self.CheckConsole = Console()
			self.CheckConsole.ePopen(cmd1, self.checkNetworkStateFinished)
		else:
			self.session.open(MessageBox,"Error: No Updateservice Avaible in Moment",  MessageBox.TYPE_INFO)

	def checkNetworkStateFinished(self, result, retval,extra_args=None):
		if 'bad address' in result:
			self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _("Your %s %s is not connected to the internet, please check your network settings and try again.") % (getMachineBrand(), getMachineName()), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
 		elif ('wget returned 1' or 'wget returned 255' or '404 Not Found') in result:
			self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _("Sorry feeds are down for maintenance, please try again later."), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
		else:
			self.session.openWithCallback(self.InstallPackage, MessageBox, _('Ready to install %s ?') % self.service_name, MessageBox.TYPE_YESNO)
			self.Exit()

	def InstallPackageFailed(self, val):
			self.feedscheck.close()
			self.close()			
			self.Exit()
	def InstallPackage(self, val):
		if val:
			self.doInstall(self.installComplete, self.service_name)
		else:
			self.feedscheck.close()
			self.close()			
			
	def doInstall(self, callback, pkgname):
		self.message = self.session.open(MessageBox,_("please wait..."), MessageBox.TYPE_INFO, enable_input = False)
		self.message.setTitle(_('Installing Service'))
		self.Console.ePopen('/usr/bin/opkg install ' + pkgname, callback)

	def installComplete(self,result = None, retval = None, extra_args = None):
		self.session.open(TryQuitMainloop, 3)

	def InstallCheckDVD(self):
	        self.service_name = 'enigma2-plugin-extensions-dvdplayer'
		self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.checkNetworkState)

	def InstallCheckVLC(self):
	        self.service_name = 'enigma2-plugin-extensions-vlcplayer'
		self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.checkNetworkState)

	def InstallCheckSHOUT(self):
	        self.service_name = 'enigma2-plugin-extensions-shoutcast'
		self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.checkNetworkState)

	def InstallCheckTSMedia(self):
	        self.service_name = 'enigma2-plugin-extensions-tsmedia-oe2.0'
		self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.checkNetworkState)

	def InstallCheckMUZU(self):
	        self.service_name = 'enigma2-plugin-extensions-muzutv'
		self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.checkNetworkState)
                
	def InstallCheckWebbrowser(self):
	        self.service_name = 'enigma2-plugin-extensions-hbbtv-opennfr-fullhd'
		self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.checkNetworkState)

	def next(self):
		self["menu"].selectNext()
		if self["menu"].getIndex() == 13:
			self["menu"].setIndex(1)
		#if self["menu"].getIndex() == 14:
		#	self["menu"].setIndex(1)
		self.update()
	def prev(self):
		self["menu"].selectPrevious()
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(12)
		self.update()
	def update(self):
		if self["menu"].getIndex() == 1:
			self["left"].instance.setPixmapFromFile(mcpath +"MenuIconSettingssw.png")
			self["middle"].instance.setPixmapFromFile(mcpath +"MenuIconMusic.png")
			self["right"].instance.setPixmapFromFile(mcpath +"MenuIconVideosw.png")
		elif self["menu"].getIndex() == 2:
			self["left"].instance.setPixmapFromFile(mcpath +"MenuIconMusicsw.png")
			self["middle"].instance.setPixmapFromFile(mcpath +"MenuIconVideo.png")
			self["right"].instance.setPixmapFromFile(mcpath +"MenuIconDVDsw.png")
		elif self["menu"].getIndex() == 3:
			self["left"].instance.setPixmapFromFile(mcpath +"MenuIconVideosw.png")
			self["middle"].instance.setPixmapFromFile(mcpath +"MenuIconDVD.png")
			self["right"].instance.setPixmapFromFile(mcpath +"MenuIconPicturesw.png")
		elif self["menu"].getIndex() == 4:
			self["left"].instance.setPixmapFromFile(mcpath +"MenuIconDVDsw.png")
			self["middle"].instance.setPixmapFromFile(mcpath +"MenuIconPicture.png")
			self["right"].instance.setPixmapFromFile(mcpath +"MenuIconRadiosw.png")
		elif self["menu"].getIndex() == 5:
			self["left"].instance.setPixmapFromFile(mcpath +"MenuIconPicturesw.png")
			self["middle"].instance.setPixmapFromFile(mcpath +"MenuIconRadio.png")
			self["right"].instance.setPixmapFromFile(mcpath +"MenuIconVLCsw.png")
		elif self["menu"].getIndex() == 6:
			self["left"].instance.setPixmapFromFile(mcpath +"MenuIconRadiosw.png")
			self["middle"].instance.setPixmapFromFile(mcpath +"MenuIconVLC.png")
			self["right"].instance.setPixmapFromFile(mcpath +"MenuIconWeathersw.png")
		elif self["menu"].getIndex() == 7:
			self["left"].instance.setPixmapFromFile(mcpath +"MenuIconVLCsw.png")
			self["middle"].instance.setPixmapFromFile(mcpath +"MenuIconWeather.png")
			self["right"].instance.setPixmapFromFile(mcpath +"MenuIconWebmediasw.png")
		elif self["menu"].getIndex() == 8:
			self["left"].instance.setPixmapFromFile(mcpath +"MenuIconWeathersw.png")
			self["middle"].instance.setPixmapFromFile(mcpath +"MenuIconWebmedia.png")
			self["right"].instance.setPixmapFromFile(mcpath +"MenuIconWebbrowsersw.png")
		elif self["menu"].getIndex() == 9:
			self["left"].instance.setPixmapFromFile(mcpath +"MenuIconWebmediasw.png")
			self["middle"].instance.setPixmapFromFile(mcpath +"MenuIconWebbrowser.png")
			self["right"].instance.setPixmapFromFile(mcpath +"MenuIconShoutcastsw.png")	
		elif self["menu"].getIndex() == 10:
			self["left"].instance.setPixmapFromFile(mcpath +"MenuIconWebbrowsersw.png")
			self["middle"].instance.setPixmapFromFile(mcpath +"MenuIconShoutcast.png")
			self["right"].instance.setPixmapFromFile(mcpath +"MenuIconWeblinkssw.png")			
		elif self["menu"].getIndex() == 11:
			self["left"].instance.setPixmapFromFile(mcpath +"MenuIconShoutcastsw.png")
			self["middle"].instance.setPixmapFromFile(mcpath +"MenuIconWeblinks.png")
			self["right"].instance.setPixmapFromFile(mcpath +"MenuIconSettingssw.png")			
		elif self["menu"].getIndex() == 12:
			self["left"].instance.setPixmapFromFile(mcpath +"MenuIconWeblinkssw.png")
			self["middle"].instance.setPixmapFromFile(mcpath +"MenuIconSettings.png")
			self["right"].instance.setPixmapFromFile(mcpath +"MenuIconMusicsw.png")				
			
		if config.plugins.mc_global.vfd.value == "on":
			evfd.getInstance().vfd_write_string(self["menu"].getCurrent()[0])
		self["text"].setText(self["menu"].getCurrent()[0])
	def okbuttonClick(self):
		from Screens.MessageBox import MessageBox
		selection = self["menu"].getCurrent()
		if selection is not None:
			if selection[1] == "MC_VideoPlayer":
				from MC_VideoPlayer import MC_VideoPlayer
				self.session.open(MC_VideoPlayer)
			elif selection[1] == "MC_DVDPlayer":
				if dvdplayer:
					self.session.open(DVDPlayer)
				else:
					self.InstallCheckDVD()
                                        self.session.open(MessageBox,"Error: DVD-Player Plugin not installed ...",  MessageBox.TYPE_INFO, timeout=5)
			elif selection[1] == "MC_PictureViewer":
				from MC_PictureViewer import MC_PictureViewer
				self.session.open(MC_PictureViewer)
			elif selection[1] == "MC_AudioPlayer":
				from MC_AudioPlayer import MC_AudioPlayer
				self.session.open(MC_AudioPlayer)
			elif selection[1] == "MC_WebRadio":
				from MC_AudioPlayer import MC_WebRadio
				self.session.open(MC_WebRadio)
			elif selection[1] == "MC_VLCPlayer":
				if pathExists("/usr/lib/enigma2/python/Plugins/Extensions/VlcPlayer/") == True:
					from MC_VLCPlayer import MC_VLCServerlist
					self.session.open(MC_VLCServerlist)
				else:
					self.session.open(MessageBox,"Error: VLC-Player Plugin not installed ...",  MessageBox.TYPE_INFO, timeout=5)
			        	self.InstallCheckVLC()

			elif selection[1] == "Webbrowser":
                                if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/HbbTV/") == True:
                                       from Plugins.Extensions.HbbTV.plugin import OperaBrowser
		                       global didOpen
		                       didOpen = True
			               url = 'http://www.nachtfalke.biz'
                                       self.session.open(OperaBrowser, url)
                                       global browserinstance
		                else:
#                                       self.session.openWithCallback(self.browserCallback, BrowserRemoteControl, url)
			                self.session.open(MessageBox,"Error: WebBrowser Plugin not installed ...",  MessageBox.TYPE_INFO, timeout=5)
					self.InstallCheckWebbrowser()
                        elif selection[1] == "SHOUTcast":
			        if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/SHOUTcast/") == True:
                                        from Plugins.Extensions.SHOUTcast.plugin import SHOUTcastWidget
                                        self.session.open(SHOUTcastWidget)
                                else:
					self.session.open(MessageBox,"Error: SHOUTcast Plugin not installed ...",  MessageBox.TYPE_INFO, timeout=5)                                  			
					self.InstallCheckSHOUT()
 			elif selection[1] == "MC_WeatherInfo":
				from MC_WeatherInfo import MC_WeatherInfo
				self.session.open(MC_WeatherInfo)
			elif selection[1] == "MC_Settings":
				from MC_Settings import MC_Settings
				self.session.open(MC_Settings)
			elif selection[1] == "MUZU.TV":
			        if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/MUZUtv/") == True:
                                        from Plugins.Extensions.MUZUtv.plugin import muzuMain
                                        self.session.open(muzuMain)
                                else:
					self.session.open(MessageBox,"Error: MUZUtv Plugin not installed ...",  MessageBox.TYPE_INFO, timeout=5)                                  			
					self.InstallCheckMUZU()
			elif selection[1] == "TSMedia":
			        if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/TSmedia/") == True:
                                        from Plugins.Extensions.TSmedia.plugin import TSmediabootlogo
                                        self.session.open(TSmediabootlogo)
                                else:
					self.session.open(MessageBox,"Error: TSmedia Plugin not installed ...",  MessageBox.TYPE_INFO, timeout=5)                                  			
					self.InstallCheckTSMedia()				
			else:
				self.session.open(MessageBox,("Error: Could not find plugin %s\ncoming soon ... :)") % (selection[1]),  MessageBox.TYPE_INFO)
	def error(self, error):
		from Screens.MessageBox import MessageBox
		self.session.open(MessageBox,("UNEXPECTED ERROR:\n%s") % (error),  MessageBox.TYPE_INFO)
	def Exit(self):
		self.session.nav.stopService()
		# Restore OSD Transparency Settings
		open("/proc/sys/vm/drop_caches", "w").write(str("3"))
		if self.can_osd_alpha:
			try:
				if config.plugins.mc_global.vfd.value == "on":
					trans = commands.getoutput('cat /etc/enigma2/settings | grep config.av.osd_alpha | cut -d "=" -f2')
				else:
					trans = commands.getoutput('cat /etc/enigma2/settings | grep config.osd.alpha | cut -d "=" -f2')
				open("/proc/stb/video/alpha", "w").write(str(trans))
			except:
				print "Set OSD Transparacy failed"
		if config.plugins.mc_global.vfd.value == "on":
			evfd.getInstance().vfd_write_string(_("Media Center"))
		os.system('umount /media/upnp')
		self.session.nav.playService(self.oldbmcService)
		self.close()

def main(session, **kwargs):
	session.open(DMC_MainMenu)
def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("Media Center"), main, "dmc_mainmenu", 44)]
	return []
def Plugins(**kwargs):
	if config.plugins.mc_globalsettings.showinmainmenu.value == True and config.plugins.mc_globalsettings.showinextmenu.value == True:
		return [
			PluginDescriptor(name = "Media Center", description = "Media Center Plugin for your OpenNFR-Image", icon="plugin.png", where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main),
			PluginDescriptor(name = "Media Center", description = "Media Center Plugin for your OpenNFR-Image", where = PluginDescriptor.WHERE_MENU, fnc = menu),
			PluginDescriptor(name = "Media Center", description = "Media Center Plugin for your OpenNFR-Image", icon="plugin.png", where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]	
	elif config.plugins.mc_globalsettings.showinmainmenu.value == True and config.plugins.mc_globalsettings.showinextmenu.value == False:
		return [
			PluginDescriptor(name = "Media Center", description = "Media Center Plugin for your OpenNFR-Image", icon="plugin.png", where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main),
			PluginDescriptor(name = "Media Center", description = "Media Center Plugin for your OpenNFR-Image", where = PluginDescriptor.WHERE_MENU, fnc = menu)]
	elif config.plugins.mc_globalsettings.showinmainmenu.value == False and config.plugins.mc_globalsettings.showinextmenu.value == True:
		return [
			PluginDescriptor(name = "Media Center", description = "Media Center Plugin for your OpenNFR-Image", icon="plugin.png", where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main),
			PluginDescriptor(name = "Media Center", description = "Media Center Plugin for your OpenNFR-Image", icon="plugin.png", where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]
	else:
		return [
			PluginDescriptor(name = "Media Center", description = "Media Center Plugin for your OpenNFR-Image", icon="plugin.png", where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main)]
