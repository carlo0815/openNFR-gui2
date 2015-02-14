from MenuList import MenuList
from enigma import getDesktop
from Tools.Directories import resolveFilename, SCOPE_ACTIVE_SKIN, defaultPaths, SCOPE_SKIN
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from os import path
from Components.config import config
from enigma import eListboxPythonMultiContent, gFont
from Tools.LoadPixmap import LoadPixmap

def PluginEntryComponent(plugin, width=440):
	if plugin.icon is None:
		png = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/plugin.png"))
	else:
		png = plugin.icon

	return [
		plugin,
		MultiContentEntryText(pos=(120, 5), size=(width-120, 30), font=0, text=plugin.name),
		MultiContentEntryText(pos=(120, 33), size=(width-120, 24), font=1, text=plugin.description),
		MultiContentEntryPixmapAlphaTest(pos=(10, 5), size=(100, 40), png = png)
	]

def PluginCategoryComponent(name, png, width=440):
	return [
		name,
		MultiContentEntryText(pos=(80, 5), size=(width-80, 30), font=0, text=name),
		MultiContentEntryPixmapAlphaTest(pos=(10, 0), size=(60, 50), png = png)
	]

def PluginDownloadComponent(plugin, name, version=None, width=440):
	if plugin.icon is None:
		png = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/plugin.png"))
	else:
		png = plugin.icon
	if version:
		if "+git" in version:
			# remove git "hash"
			version = "+".join(version.split("+")[:2])
		elif version.startswith('experimental-'):
			version = version[13:]
		name += "  (" + version + ")"
	return [
		plugin,
		MultiContentEntryText(pos=(80, 5), size=(width-80, 28), font=0, text=name),
		MultiContentEntryText(pos=(80, 33), size=(width-80, 22), font=1, text=plugin.description),
		MultiContentEntryPixmapAlphaTest(pos=(10, 0), size=(60, 50), png = png)
	]


class PluginList(MenuList):
	def __init__(self, list, enableWrapAround=True):
		if getDesktop(0).size().width() == 1920:
				MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
				self.l.setFont(0, gFont("Regular", 28))
				self.l.setFont(1, gFont("Regular", 22))
				self.l.setItemHeight(60)
		else:
			MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
			self.l.setFont(0, gFont("Regular", 20))
			self.l.setFont(1, gFont("Regular", 14))
			self.l.setItemHeight(50)
