from boxbranding import getMachineBrand, getMachineName
from Screens.Screen import Screen
from Components.Harddisk import harddiskmanager
from Screens.WizardUserInterfacePositioner import UserInterfacePositionerWizard
from Plugins.Extensions.OpenWebif.plugin import OpenWebifConfig
from Screens.OpenNFR_wizard import OpenNFRWizardSetup
from boxbranding import getBoxType, getImageDistro, getMachineName, getMachineBrand, getBrandOEM, getImageVersion
from Plugins.Extensions.Infopanel.SpinnerSelector import SpinnerSelector
from Plugins.Extensions.Infopanel.bootvideo import BootvideoSetupScreen
from Plugins.Extensions.Infopanel.bootlogo import BootlogoSetupScreen, RadiologoSetupScreen
from Plugins.Extensions.Infopanel.outofflash import *
from Components.ConfigList import ConfigListScreen
from Components.config import *
from Components.Sources.StaticText import StaticText


config.wizardsetup								= ConfigSubsection()
config.wizardsetup.pluginmoveoutwizard						= ConfigYesNo(default = False)
config.wizardsetup.pluginwizard							= ConfigYesNo(default = False)
config.wizardsetup.spinnerselect						= ConfigYesNo(default = False)
config.wizardsetup.bootlogo							= ConfigYesNo(default = False) 
config.wizardsetup.bootvideo							= ConfigYesNo(default = False)
config.wizardsetup.spinnermoveout						= ConfigYesNo(default = False)
config.wizardsetup.bootlogomoveout						= ConfigYesNo(default = False) 
config.wizardsetup.bootvideomoveout						= ConfigYesNo(default = False)  
config.wizardsetup.UserInterfacePositionerWizard				= ConfigYesNo(default = False) 
config.wizardsetup.OpenWebifConfig						= ConfigYesNo(default = False)
config.wizardsetup.OpenNFRaddonsWizardSetup					= ConfigYesNo(default = False)


class NfrWizardSetupScreen(Screen, ConfigListScreen):
	skin = """
	<screen position="c-300,c-250" size="600,500" title="openNFR Wizard setup">
		<widget name="config" position="25,25" size="550,350" />
		<ePixmap pixmap="buttons/red.png" position="20,e-45" size="140,40" alphatest="on" />
		<ePixmap pixmap="buttons/green.png" position="160,e-45" size="140,40" alphatest="on" />
		<ePixmap pixmap="buttons/yellow.png" position="300,e-45" size="140,40" alphatest="on" />
		<ePixmap pixmap="buttons/blue.png" position="440,e-45" size="140,40" alphatest="on" />
		<widget source="key_red" render="Label" position="20,e-45" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget source="key_green" render="Label" position="160,e-45" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget source="key_yellow" render="Label" position="300,e-45" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		<widget source="key_blue" render="Label" position="440,e-45" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
	</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("openNFR Wizard setup"))
		from Components.ActionMap import ActionMap

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["key_yellow"] = StaticText(_(""))
		self["key_blue"] = StaticText(_(""))
		self["actions"] = ActionMap(["SetupActions", "ColorActions", "MenuActions"],
		{
			"ok": self.keyGo,
			"save": self.keyGo,
			"cancel": self.keyCancel,
			"green": self.keyGo,
			"red": self.keyCancel,
		}, -2)

		self.onChangedEntry = [ ]
		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
		self.createSetup()

	def createSetup(self):
		self.list = []
		self.list.append(getConfigListEntry(_("PLugin-Install-Wizard"), config.wizardsetup.pluginwizard))
		if config.wizardsetup.pluginwizard.value:
			self.list.append(getConfigListEntry(_("Spinner Setup"), config.wizardsetup.spinnerselect))
			self.list.append(getConfigListEntry(_("Spinner Move out of Flash"), config.wizardsetup.spinnermoveout))			
			self.list.append(getConfigListEntry(_("Bootlogo Setup"), config.wizardsetup.bootlogo))
			self.list.append(getConfigListEntry(_("Bootlogo Move out of Flash"), config.wizardsetup.bootlogomoveout))
			self.list.append(getConfigListEntry(_("Bootvideo Setup"), config.wizardsetup.bootvideo))
			self.list.append(getConfigListEntry(_("Bootvideo Move out of Flash"), config.wizardsetup.bootvideomoveout))
		else:
			config.wizardsetup.spinnerselect.value = False
			config.wizardsetup.bootlogo.value = False
			config.wizardsetup.bootvideo.value = False
			config.wizardsetup.spinnermoveout.value = False
			config.wizardsetup.bootlogomoveout.value = False
			config.wizardsetup.bootvideomoveout.value = False	
                	
		self.list.append(getConfigListEntry(_("Position setup"), config.wizardsetup.UserInterfacePositionerWizard))
		self.list.append(getConfigListEntry(_("OpenWebif Setup"), config.wizardsetup.OpenWebifConfig))
		self.list.append(getConfigListEntry(_("OpenNFR-Addons Setup"), config.wizardsetup.OpenNFRaddonsWizardSetup))
		self.list.append(getConfigListEntry(_("Plugins Move out of Flash"), config.wizardsetup.pluginmoveoutwizard))
		self["config"].list = self.list
		self["config"].l.setList(self.list)


	# for summary:
	def changedEntry(self):
		if self["config"].getCurrent()[0] == _("Enabled"):
			self.createSetup()
		for x in self.onChangedEntry:
			x()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.createSetup()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.createSetup()

	def keyGo(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()
		self.wiz_ard()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()
		
	def wiz_ard(self):
                if config.wizardsetup.pluginmoveoutwizard == True:
                        if harddiskmanager.HDDCount() == 0:
                        	print "no Device found for moveout"
                        else:	                                	
                		self.session.open(MovePlugins)
		if config.wizardsetup.OpenNFRaddonsWizardSetup.value == True:
                	self.session.open(OpenNFRWizardSetup)                  		
                if config.wizardsetup.UserInterfacePositionerWizard.value == True:
			self.session.open(UserInterfacePositionerWizard)                 		
		if config.wizardsetup.OpenWebifConfig.value == True:
                	self.session.open(OpenWebifConfig)                		
		if config.wizardsetup.bootvideomoveout.value == True and config.wizardsetup.pluginwizard.value == True:
                       	if harddiskmanager.HDDCount() == 0:
                       		print "no Device found for moveout"
                       	else:	                        	
				self.session.open(MoveVideos)                       		
		if config.wizardsetup.bootvideo.value == True and config.wizardsetup.pluginwizard.value == True:
			self.session.open(BootvideoSetupScreen)                		
		if config.wizardsetup.bootlogomoveout.value == True and config.wizardsetup.pluginwizard.value == True:
                       	if harddiskmanager.HDDCount() == 0:
                       		print "no Device found for moveout"
                       	else:	                        	
				self.session.open(MoveSpinner)                		
		if config.wizardsetup.bootlogo.value == True and config.wizardsetup.pluginwizard.value == True:
			self.session.open(BootlogoSetupScreen)                 		
		if config.wizardsetup.spinnermoveout.value == True and config.wizardsetup.pluginwizard.value == True:
                       	if harddiskmanager.HDDCount() == 0:
                       		print "no Device found for moveout"
                       	else:	
				self.session.open(MoveSpinner)                		
		if config.wizardsetup.spinnerselect.value == True and config.wizardsetup.pluginwizard.value == True:
			SpinnerSelector(self.session)
	        if config.wizardsetup.pluginwizard.value == True:
	                from Plugins.Extensions.Infopanel.PluginWizard import PluginInstall
			self.session.open(PluginInstall)                                  
		self.close()
                
