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
	if getDesktop(0).size().width() == 1920:
	    return [
		plugin,
		MultiContentEntryText(pos=(120, 1), size=(width-120, 31), font=0, text=plugin.name),
		MultiContentEntryText(pos=(120, 32), size=(width-120, 26), font=1, text=plugin.description),
		MultiContentEntryPixmapAlphaTest(pos=(10, 10), size=(100, 40), png = png)
	]

	if getDesktop(0).size().width() == 1280:
	    return [
		plugin,
		MultiContentEntryText(pos=(120, 5), size=(width-120, 25), font=0, text=plugin.name),
		MultiContentEntryText(pos=(120, 26), size=(width-120, 17), font=1, text=plugin.description),
		MultiContentEntryPixmapAlphaTest(pos=(10, 5), size=(100, 40), png = png)		
	]

def PluginCategoryComponent(name, png, width=440):
	if getDesktop(0).size().width() == 1920:
	    return [
		name,
		MultiContentEntryText(pos=(80, 10), size=(width-80, 32), font=0, text=name),
		MultiContentEntryPixmapAlphaTest(pos=(10, 5), size=(60, 50), png = png)
	]
        else:
	   return [
		name,
		MultiContentEntryText(pos=(80, 5), size=(width-80, 25), font=0, text=name),
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
	if getDesktop(0).size().width() == 1920:		
	   return [
		plugin,
		MultiContentEntryText(pos=(80, 0), size=(width-80, 32), font=0, text=name),
		MultiContentEntryText(pos=(80, 32), size=(width-80, 26), font=1, text=plugin.description),
		MultiContentEntryPixmapAlphaTest(pos=(10, 0), size=(60, 50), png = png)
	]
	else:
	   return [
		plugin,
		MultiContentEntryText(pos=(80, 5), size=(width-80, 25), font=0, text=name),
		MultiContentEntryText(pos=(80, 26), size=(width-80, 17), font=1, text=plugin.description),
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
