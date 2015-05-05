from Screens.MessageBox import MessageBox
from boxbranding import getMachineBrand, getMachineName
from Screens.ParentalControlSetup import ProtectedScreen
from Components.config import config
from Tools.BoundFunction import boundFunction
from Screens.InputBox import PinInput

class FactoryReset(MessageBox, ProtectedScreen):
	def __init__(self, session):
		MessageBox.__init__(self, session, _("When you do a factory reset, you will lose ALL your configuration data\n"
			"(including bouquets, services, satellite data ...)\n"
			"After completion of factory reset, your %s %s will restart automatically!\n\n"
			"Really do a factory reset?") % (getMachineBrand(), getMachineName()), MessageBox.TYPE_YESNO, default = False)
		self.setTitle(_("Factory reset"))
		self.skinName = "MessageBox"

		if self.isProtected() and config.ParentalControl.servicepin[0].value:
			self.onFirstExecBegin.append(boundFunction(self.session.openWithCallback, self.pinEntered, PinInput, pinList=[x.value for x in config.ParentalControl.servicepin], triesEntry=config.ParentalControl.retries.servicepin, title=_("Please enter the correct pin code"), windowTitle=_("Enter pin code")))

	def isProtected(self):
		return config.ParentalControl.setuppinactive.value and (not config.ParentalControl.config_sections.main_menu.value or hasattr(self.session, 'infobar') and self.session.infobar is None) and config.ParentalControl.config_sections.manufacturer_reset.value

	def pinEntered(self, result):
		if result is None:
			self.closeProtectedScreen()
		elif not result:
			self.session.openWithCallback(self.close(), MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR, timeout=3)

	def closeProtectedScreen(self, result=None):
		self.close(None)