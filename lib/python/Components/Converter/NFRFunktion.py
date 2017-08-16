from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService, iPlayableServicePtr, eServiceReference, eServiceCenter, eTimer, getBestPlayableServiceReference
from Components.Element import cached
from Components.config import config
import NavigationInstance

class NFRFunktion(Converter, object):
	PLUGINS = 10
	PLUGINS1 = 11
	PLUGINS2 = 12
	PLUGINS3 = 13                 	

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "Plugins":
			self.type = self.PLUGINS
		elif type == "Plugins1":
			self.type = self.PLUGINS1	
		elif type == "Plugins2":
			self.type = self.PLUGINS2

	@cached
	def getText(self):
		if self.type ==  self.PLUGINS:
			return config.usage.show_plugins_in_servicelist.value
		elif self.type ==  self.PLUGINS1:
			return config.usage.show_plugins1_in_servicelist.value
		elif self.type ==  self.PLUGINS2:
			return config.usage.show_plugins2_in_servicelist.value
	text = property(getText)

