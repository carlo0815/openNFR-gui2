from Wizard import wizardManager
from Screens.WizardLanguage import WizardLanguage
from Screens.WizardUserInterfacePositioner import UserInterfacePositionerWizard
from Screens.VideoWizard import VideoWizard
from Screens.Rc import Rc
from Screens.Screen import Screen
from Plugins.Extensions.Infopanel.skin_setup import DefaulSkinchange
from boxbranding import getBoxType

from Components.Pixmap import Pixmap
from Components.config import *

from LanguageSelection import LanguageWizard
from Screens.Nfrstartwizard import NfrWizardSetupScreen
from boxbranding import getBoxType,  getImageDistro, getMachineName, getMachineBrand, getBrandOEM, getImageVersion
import os

config.misc.firstrun = ConfigBoolean(default = True)
config.misc.languageselected = ConfigBoolean(default = True)
config.misc.videowizardenabled = ConfigBoolean(default = True)
config.defaultskinSetup = ConfigSubsection()
config.defaultskinSetup.steps = ConfigSelection([('default Utopia',_("default Utopia")),('default SmokeR',_("default SmokeR"))], default='default Utopia')

class StartWizard(WizardLanguage, Rc):
	def __init__(self, session, silent = True, showSteps = False, neededTag = None):
		self.xmlfile = ["startwizard.xml"]
                WizardLanguage.__init__(self, session, showSteps = False)
		Rc.__init__(self)
		self["wizard"] = Pixmap()
		Screen.setTitle(self, _("Welcome..."))

	def markDone(self):
		# setup remote control, all stb have same settings except dm8000 which uses a different settings
		if getBoxType() == 'dm8000':
			config.misc.rcused.setValue(0)
		else:
                        config.misc.rcused.setValue(1)
		config.misc.rcused.save()
		
		config.misc.firstrun.setValue(0)
		config.misc.firstrun.save()
		configfile.save()
if config.defaultskinSetup.steps.value == "default SmokeR" or config.defaultskinSetup.steps.value == "default Utopia":
	print "skinselection allready selected"
else:
	wizardManager.registerWizard(DefaulSkinchange, config.defaultskinSetup.steps.value, priority = 0)
wizardManager.registerWizard(LanguageWizard, config.misc.languageselected.value, priority = 1)
wizardManager.registerWizard(VideoWizard, config.misc.videowizardenabled.value, priority = 1)
wizardManager.registerWizard(StartWizard, config.misc.firstrun.value, priority = 20)
wizardManager.registerWizard(NfrWizardSetupScreen, config.misc.firstrun.value, priority = 30)

