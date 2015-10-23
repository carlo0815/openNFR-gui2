from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MenuList import MenuList
from Components.Button import Button
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ActionMap import NumberActionMap, ActionMap
from Components.config import *
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Tools.Directories import fileExists
from Components.PluginList import *
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
			from Plugins.Extensions.Infopanel.Manager import *
			from Plugins.Extensions.Infopanel.Softcam import *
			self.session.openWithCallback(self.callEgAction, NFRCamManager)	
		elif config.plugins.infopanel_bluekey.list.value == '1':
                        from Plugins.Extensions.Infopanel.QuickMenu import QuickMenu
                        self.session.openWithCallback(self.callEgAction, QuickMenu)
		else:
                        from Plugins.Extensions.Infopanel.plugin import *
                        self.session.openWithCallback(self.callEgAction,Infopanel)

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
			from Plugins.Extensions.Infopanel.Manager import *
			from Plugins.Extensions.Infopanel.Softcam import *
			self.session.openWithCallback(self.callEgAction, NFRCamManager)	
		elif config.plugins.infopanel_redkey.list.value == '1':
                        from Plugins.Extensions.Infopanel.QuickMenu import QuickMenu
                        self.session.openWithCallback(self.callEgAction, QuickMenu)
		else:
                        from Plugins.Extensions.Infopanel.plugin import *
                        self.session.openWithCallback(self.callEgAction,Infopanel)

	def callEgAction(self, *args):
		if len(args):
			(actionmap, context, action) = args
			actionmap.action(context, action)
                        
