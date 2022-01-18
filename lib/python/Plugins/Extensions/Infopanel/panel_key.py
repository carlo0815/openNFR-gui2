from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MenuList import MenuList
from Components.Button import Button
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ActionMap import NumberActionMap, ActionMap
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Tools.Directories import fileExists
from Components.Sources.List import List
from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
from Screens.Setup import Setup
from Components.config import config
import os
#config.plugins.infopanel_redkey = ConfigSubsection()





class OpenNFRBluePanel:
	def __init__(self):
		self["OpenNFRBluePanel"] = ActionMap( [ "InfobarExtensions" ],
			{
				"OpenNFRBluePanelShow": (self.showOpenNFRBluePanel),
			})

	def showOpenNFRBluePanel(self):
		if config.plugins.infopanel_bluekey.list.value == '0':
			from Plugins.Extensions.Infopanel.QuickMenu import QuickMenu
			self.session.openWithCallback(self.callEgAction, QuickMenu)
		elif config.plugins.infopanel_bluekey.list.value == '1':
			from Screens.InfoBar import InfoBarRedButton
			InfoBarRedButton.activateRedButton(self)			
		elif config.plugins.infopanel_bluekey.list.value == '2':
			from Plugins.Extensions.Infopanel.Manager import NFRCamManager
			self.session.openWithCallback(self.callEgAction, NFRCamManager)

		else:
			from Plugins.Extensions.Infopanel.plugin import Infopanel
			self.session.openWithCallback(self.callEgAction, Infopanel)

	def callEgAction(self, *args):
		if len(args):
			(actionmap, context, action) = args
			actionmap.action(context, action)
			
class OpenNFRBluePanelLong:
	def __init__(self):
		self["OpenNFRBluePanelLong"] = ActionMap( [ "InfobarExtensions" ],
			{
				"OpenNFRBluePanelLongShow": (self.showOpenNFRBluePanelLong),
			})

	def showOpenNFRBluePanelLong(self):
		if config.plugins.infopanel_bluekeylong.list.value == '0':
			from Plugins.Extensions.Infopanel.plugin import Infopanel
			self.session.openWithCallback(self.callEgAction, Infopanel)
		elif config.plugins.infopanel_bluekeylong.list.value == '1':
			from Screens.InfoBar import InfoBarRedButton
			InfoBarRedButton.activateRedButton(self)
		elif config.plugins.infopanel_bluekeylong.list.value == '2':
			from Plugins.Extensions.Infopanel.QuickMenu import QuickMenu
			self.session.openWithCallback(self.callEgAction, QuickMenu)
		else:
			from Plugins.Extensions.Infopanel.Manager import NFRCamManager
			self.session.openWithCallback(self.callEgAction, NFRCamManager)	

	def callEgAction(self, *args):
		if len(args):
			(actionmap, context, action) = args
			actionmap.action(context, action)
			
class OpenNFRREDPanel:
	def __init__(self):
		self["OpenNFRRedPanel"] = ActionMap( [ "InfobarExtensions" ],
			{
				"OpenNFRRedPanelShow": (self.showOpenNFRRedPanel),
			})

	def showOpenNFRRedPanel(self):
		if config.plugins.infopanel_redkey.list.value == '0':
			from Plugins.Extensions.Infopanel.Manager import NFRCamManager
			self.session.openWithCallback(self.callEgAction, NFRCamManager)	
		elif config.plugins.infopanel_redkey.list.value == '1':
			from Screens.InfoBar import InfoBarRedButton
			InfoBarRedButton.activateRedButton(self)
		elif config.plugins.infopanel_redkey.list.value == '2':
			from Plugins.Extensions.Infopanel.QuickMenu import QuickMenu
			self.session.openWithCallback(self.callEgAction, QuickMenu)
		else:
			from Plugins.Extensions.Infopanel.plugin import Infopanel
			self.session.openWithCallback(self.callEgAction, Infopanel)

	def callEgAction(self, *args):
		if len(args):
			(actionmap, context, action) = args
			actionmap.action(context, action)
			
class OpenNFRREDPanelLong:
	def __init__(self):
		self["OpenNFRRedPanelLong"] = ActionMap( [ "InfobarExtensions" ],
			{
				"OpenNFRRedPanelLongShow": (self.showOpenNFRRedPanelLong),
			})

	def showOpenNFRRedPanelLong(self):
		if config.plugins.infopanel_redkeylong.list.value == '0':
			from Screens.InfoBar import InfoBarRedButton
			InfoBarRedButton.activateRedButton(self)	
		elif config.plugins.infopanel_redkeylong.list.value == '1':
			from Plugins.Extensions.Infopanel.Manager import NFRCamManager
			self.session.openWithCallback(self.callEgAction, NFRCamManager)
		elif config.plugins.infopanel_redkeylong.list.value == '2':
			from Plugins.Extensions.Infopanel.QuickMenu import QuickMenu
			self.session.openWithCallback(self.callEgAction, QuickMenu)
		else:
			from Plugins.Extensions.Infopanel.plugin import Infopanel
			self.session.openWithCallback(self.callEgAction, Infopanel)

	def callEgAction(self, *args):
		if len(args):
			(actionmap, context, action) = args
			actionmap.action(context, action)			
                        
class OpenNFRGreenPanelLong:
	def __init__(self):
		self["OpenNFRGreenPanelLong"] = ActionMap( [ "InfobarExtensions" ],
			{
				"OpenNFRGreenPanelLongShow": (self.showOpenNFRGreenPanelLong),
			})

	def showOpenNFRGreenPanelLong(self):
		if config.plugins.infopanel_greenkeylong.list.value == '0':
			from Screens.About import NetworkInstalledApp
			self.session.openWithCallback(self.callEgAction, NetworkInstalledApp)		
		elif config.plugins.infopanel_greenkeylong.list.value == '1':
			from Plugins.Extensions.Infopanel.Manager import NFRCamManager
			self.session.openWithCallback(self.callEgAction, NFRCamManager)	
		elif config.plugins.infopanel_greenkeylong.list.value == '2':
			from Screens.InfoBar import InfoBarRedButton
			InfoBarRedButton.activateRedButton(self)
		elif config.plugins.infopanel_greenkeylong.list.value == '3':
			from Plugins.Extensions.Infopanel.QuickMenu import QuickMenu
			self.session.openWithCallback(self.callEgAction, QuickMenu)
		else:
			from Plugins.Extensions.Infopanel.plugin import Infopanel
			self.session.openWithCallback(self.callEgAction, Infopanel)

	def callEgAction(self, *args):
		if len(args):
			(actionmap, context, action) = args
			actionmap.action(context, action)	
			
class OpenNFRYellowPanelLong:
	def __init__(self):
		self["OpenNFRYellowPanelLong"] = ActionMap( [ "InfobarExtensions" ],
			{
				"OpenNFRYellowPanelLongShow": (self.showOpenNFRYellowPanelLong),
			})

	def showOpenNFRYellowPanelLong(self):
		if config.plugins.infopanel_yellowkeylong.list.value == '0':
			from Plugins.Extensions.Infopanel.Manager import NFRCamManager
			self.session.openWithCallback(self.callEgAction, NFRCamManager)	
		elif config.plugins.infopanel_yellowkeylong.list.value == '1':
			from Screens.InfoBar import InfoBarRedButton
			InfoBarRedButton.activateRedButton(self)
		elif config.plugins.infopanel_yellowkeylong.list.value == '2':
			from Plugins.Extensions.Infopanel.QuickMenu import QuickMenu
			self.session.openWithCallback(self.callEgAction, QuickMenu)
		else:
			from Plugins.Extensions.Infopanel.plugin import Infopanel
			self.session.openWithCallback(self.callEgAction, Infopanel)

	def callEgAction(self, *args):
		if len(args):
			(actionmap, context, action) = args
			actionmap.action(context, action)						
