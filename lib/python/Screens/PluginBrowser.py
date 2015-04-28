from Screens.ParentalControlSetup import ProtectedScreen
from boxbranding import getImageVersion
from urllib import urlopen
import socket
import os

from enigma import eConsoleAppContainer, eDVBDB
from Screens.InputBox import PinInput
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.PluginComponent import plugins
from Components.PluginList import PluginList, PluginEntryComponent, PluginCategoryComponent, PluginDownloadComponent
from Components.Label import Label
from Components.Language import language
from Components.Button import Button
from Components.Harddisk import harddiskmanager
from Components.Sources.StaticText import StaticText
from Components import Ipkg
from Components.config import config, ConfigSubsection, ConfigYesNo, getConfigListEntry, configfile, ConfigText
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_ACTIVE_SKIN
from Tools.LoadPixmap import LoadPixmap
from Plugins.Extensions.Infopanel.PluginWizard import PluginInstall
from Plugins.Extensions.Infopanel.PluginWizard import PluginDeinstall
from os import popen, system, remove, listdir, chdir, getcwd, statvfs, mkdir, path, walk
from Components.ProgressBar import ProgressBar
from Tools.BoundFunction import boundFunction
language.addCallback(plugins.reloadPlugins)

config.misc.pluginbrowser = ConfigSubsection()
config.misc.pluginbrowser.plugin_order = ConfigText(default="")

def getVarSpaceKb():
    try:
        s = statvfs('/')
    except OSError:
        return (0, 0)

    return (float(s.f_bfree * (s.f_bsize / 1024)), float(s.f_blocks * (s.f_bsize / 1024)))


class PluginBrowserSummary(Screen):
	def __init__(self, session, parent):
		Screen.__init__(self, session, parent = parent)
		self["entry"] = StaticText("")
		self["desc"] = StaticText("")
		self.onShow.append(self.addWatcher)
		self.onHide.append(self.removeWatcher)

	def addWatcher(self):
		self.parent.onChangedEntry.append(self.selectionChanged)
		self.parent.selectionChanged()

	def removeWatcher(self):
		self.parent.onChangedEntry.remove(self.selectionChanged)

	def selectionChanged(self, name, desc):
		self["entry"].text = name
		self["desc"].text = desc


class PluginBrowser(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Plugin Browser"))
		self.firsttime = True

		self["key_red"] = Button(_("Remove plugins"))
		self["key_green"] = Button(_("Download plugins"))
		self["key_yellow"] = Button(_("PluginInstallWizard"))
		self["key_blue"] = Button(_("PluginDeinstallWizard"))		

		self.list = []
		self["list"] = PluginList(self.list)
		if config.usage.sort_pluginlist.getValue():
			self["list"].list.sort()

		self["actions"] = ActionMap(["WizardActions", "MenuActions"],
		{
			"ok": self.save,
			"back": self.close,
			"menu": self.openSetup,
		})
		self["PluginDownloadActions"] = ActionMap(["ColorActions"],
		{
			"red": self.delete,
			"green": self.download,
			"yellow": self.wizardinstall,
			"blue": self.wizarddeinstall			
		})
		self["DirectionActions"] = ActionMap(["DirectionActions"],
 		{
 			"moveUp": self.moveUp,
 			"moveDown": self.moveDown
 		})

		self.onFirstExecBegin.append(self.checkWarnings)
		self.onShown.append(self.updateList)
		self.onChangedEntry = []
		self["list"].onSelectionChanged.append(self.selectionChanged)
		self.onLayoutFinish.append(self.saveListsize)
		if self.isProtected() and config.ParentalControl.servicepin[0].value:
			self.onFirstExecBegin.append(boundFunction(self.session.openWithCallback, self.pinEntered, PinInput, pinList=[x.value for x in config.ParentalControl.servicepin], triesEntry=config.ParentalControl.retries.servicepin, title=_("Please enter the correct pin code"), windowTitle=_("Enter pin code")))

	def isProtected(self):
		return config.ParentalControl.setuppinactive.value and (not config.ParentalControl.config_sections.main_menu.value or hasattr(self.session, 'infobar') and self.session.infobar is None) and config.ParentalControl.config_sections.timer_menu.value

	def pinEntered(self, result):
		if result is None:
			self.closeProtectedScreen()
		elif not result:
			self.session.openWithCallback(self.close(), MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR, timeout=3)

	def closeProtectedScreen(self, result=None):
		self.close(None)
		
	def openSetup(self):
		from Screens.Setup import Setup
		self.session.open(Setup, "pluginbrowsersetup")
		
	def wizardinstall(self):
		self.session.open(PluginInstall)
                
	def wizarddeinstall(self):
		self.session.open(PluginDeinstall)               		

	def saveListsize(self):
		listsize = self["list"].instance.size()
		self.listWidth = listsize.width()
		self.listHeight = listsize.height()

	def createSummary(self):
		return PluginBrowserSummary

	def selectionChanged(self):
		item = self["list"].getCurrent()
		if item:
			p = item[0]
			name = p.name
			desc = p.description
		else:
			name = "-"
			desc = ""
		for cb in self.onChangedEntry:
			cb(name, desc)

	def checkWarnings(self):
		if len(plugins.warnings):
			text = _("Some plugins are not available:\n")
			for (pluginname, error) in plugins.warnings:
				text += _("%s (%s)\n") % (pluginname, error)
			plugins.resetWarnings()
			self.session.open(MessageBox, text = text, type = MessageBox.TYPE_WARNING)

	def save(self):
		self.run()

	def run(self):
		plugin = self["list"].l.getCurrentSelection()[0]
		plugin(session=self.session)

	def moveUp(self):
		self.move(-1)

	def moveDown(self):
		self.move(1)

	def move(self, direction):
			if len(self.list) > 1:
					currentIndex = self["list"].getSelectionIndex()
					swapIndex = (currentIndex + direction) % len(self.list)
					if currentIndex == 0 and swapIndex != 1:
							self.list = self.list[1:] + [self.list[0]]
					elif swapIndex == 0 and currentIndex != 1:
							self.list = [self.list[-1]] + self.list[:-1]
					else:
							self.list[currentIndex], self.list[swapIndex] = self.list[swapIndex], self.list[currentIndex]
					self["list"].l.setList(self.list)
					if direction == 1:
							self["list"].down()
					else:
							self["list"].up()
					plugin_order = []
					for x in self.list:
							plugin_order.append(x[0].path[24:])
					config.misc.pluginbrowser.plugin_order.value = ",".join(plugin_order)
					config.misc.pluginbrowser.plugin_order.save()	

	def updateList(self):
			self.list = []
			pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)[:]
			for x in config.misc.pluginbrowser.plugin_order.value.split(","):
					plugin = list(plugin for plugin in pluginlist if plugin.path[24:] == x)
					if plugin:
							self.list.append(PluginEntryComponent(plugin[0], self.listWidth))
							pluginlist.remove(plugin[0])
			self.list = self.list + [PluginEntryComponent(plugin, self.listWidth) for plugin in pluginlist]
			self["list"].l.setList(self.list)


	def delete(self):
		self.session.openWithCallback(self.PluginDownloadBrowserClosed, PluginDownloadBrowser, PluginDownloadBrowser.REMOVE)

	def download(self):
		self.session.openWithCallback(self.PluginDownloadBrowserClosed, PluginDownloadBrowser, PluginDownloadBrowser.DOWNLOAD, self.firsttime)
		self.firsttime = False

	def PluginDownloadBrowserClosed(self):
		self.updateList()
		self.checkWarnings()

	def openExtensionmanager(self):
		if fileExists(resolveFilename(SCOPE_PLUGINS, "SystemPlugins/SoftwareManager/plugin.py")):
			try:
				from Plugins.SystemPlugins.SoftwareManager.plugin import PluginManager
			except ImportError:
				self.session.open(MessageBox, _("The software management extension is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )
			else:
				self.session.openWithCallback(self.PluginDownloadBrowserClosed, PluginManager)

class PluginDownloadBrowser(Screen):
	DOWNLOAD = 0
	REMOVE = 1
	PLUGIN_PREFIX = 'enigma2-plugin-'
	lastDownloadDate = None

	def __init__(self, session, type = 0, needupdate = True):
		Screen.__init__(self, session)

		self.type = type
		self.needupdate = needupdate

		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun)
		self.onShown.append(self.setWindowTitle)

		self.list = []
		self["list"] = PluginList(self.list)
		self.pluginlist = []
		self.expanded = []
		self.installedplugins = []
		self.plugins_changed = False
		self.reload_settings = False
		self.check_settings = False
		self.check_bootlogo = False
		self['spaceused'] = ProgressBar()		
		self.install_settings_name = ''
		self.remove_settings_name = ''

		if self.type == self.DOWNLOAD:
			self["text"] = Label(_("Downloading plugin information. Please wait..."))
		elif self.type == self.REMOVE:
			self["text"] = Label(_("Getting plugin information. Please wait..."))

		self.run = 0
		self.remainingdata = ""
		self["actions"] = ActionMap(["WizardActions"],
		{
			"ok": self.go,
			"back": self.requestClose,
		})
		if os.path.isfile('/usr/bin/opkg'):
			self.ipkg = '/usr/bin/opkg'
			self.ipkg_install = self.ipkg + ' install --force-overwrite'
			self.ipkg_remove =  self.ipkg + ' remove --autoremove --force-depends'
			self.ipkg_install1 = self.ipkg_install + ' --force-depends'
		else:
			self.ipkg = 'ipkg'
			self.ipkg_install = 'ipkg install --force-overwrite -force-defaults'
			self.ipkg_remove =  self.ipkg + ' remove --autoremove --force-depends'
			self.ipkg_install1 = self.ipkg_install + ' --force-depends'

	def go(self):
		sel = self["list"].l.getCurrentSelection()

		if sel is None:
			return

		sel = sel[0]
		if isinstance(sel, str): # category
			if sel in self.expanded:
				self.expanded.remove(sel)
			else:
				self.expanded.append(sel)
			self.updateList()
		else:
			if self.type == self.DOWNLOAD:
				mbox=self.session.openWithCallback(self.runInstall, MessageBox, _("Do you really want to download the plugin \"%s\"?") % sel.name)
				mbox.setTitle(_("Download plugins"))
			elif self.type == self.REMOVE:
				mbox=self.session.openWithCallback(self.runInstall, MessageBox, _("Do you really want to remove the plugin \"%s\"?") % sel.name, default = False)
				mbox.setTitle(_("Remove plugins"))

	def requestClose(self):
		if self.plugins_changed:
			plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		if self.reload_settings:
			self["text"].setText(_("Reloading bouquets and services..."))
			eDVBDB.getInstance().reloadBouquets()
			eDVBDB.getInstance().reloadServicelist()
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		self.container.appClosed.remove(self.runFinished)
		self.container.dataAvail.remove(self.dataAvail)
		self.close()

	def resetPostInstall(self):
		try:
			del self.postInstallCall
		except:
			pass

	def installDestinationCallback(self, result):
		if result is not None:
			dest = result[1]
			if dest.startswith('/'):
				# Custom install path, add it to the list too
				dest = os.path.normpath(dest)
				extra = '--add-dest %s:%s -d %s' % (dest,dest,dest)
				Ipkg.opkgAddDestination(dest)
			else:
				extra = '-d ' + dest
			self.doInstall(self.installFinished, self["list"].l.getCurrentSelection()[0].name + ' ' + extra)
		else:
			self.resetPostInstall()

	def runInstall(self, val):
		if val:
			if self.type == self.DOWNLOAD:
				if self["list"].l.getCurrentSelection()[0].name.startswith("picons-"):
					supported_filesystems = frozenset(('vfat','ext4', 'ext3', 'ext2', 'reiser', 'reiser4', 'jffs2', 'ubifs', 'rootfs'))
					candidates = []
					import Components.Harddisk
					mounts = Components.Harddisk.getProcMounts()
					for partition in harddiskmanager.getMountedPartitions(False, mounts):
						if partition.filesystem(mounts) in supported_filesystems:
							candidates.append((partition.description, partition.mountpoint))
					if candidates:
						from Components.Renderer import Picon
						self.postInstallCall = Picon.initPiconPaths
						self.session.openWithCallback(self.installDestinationCallback, ChoiceBox, title=_("Install picons on"), list=candidates)
					return
				elif self["list"].l.getCurrentSelection()[0].name.startswith("display-picon"):
					supported_filesystems = frozenset(('vfat','ext4', 'ext3', 'ext2', 'reiser', 'reiser4', 'jffs2', 'ubifs', 'rootfs'))
					candidates = []
					import Components.Harddisk
					mounts = Components.Harddisk.getProcMounts()
					for partition in harddiskmanager.getMountedPartitions(False, mounts):
						if partition.filesystem(mounts) in supported_filesystems:
							candidates.append((partition.description, partition.mountpoint))
					if candidates:
						from Components.Renderer import LcdPicon
						self.postInstallCall = LcdPicon.initLcdPiconPaths
						self.session.openWithCallback(self.installDestinationCallback, ChoiceBox, title=_("Install lcd picons on"), list=candidates)
					return
				self.install_settings_name = self["list"].l.getCurrentSelection()[0].name
				self.install_bootlogo_name = self["list"].l.getCurrentSelection()[0].name
				if self["list"].l.getCurrentSelection()[0].name.startswith('settings-'):
					self.check_settings = True
					self.startIpkgListInstalled(self.PLUGIN_PREFIX + 'settings-*')
				elif self["list"].l.getCurrentSelection()[0].name.startswith('bootlogo-'):
					self.check_bootlogo = True
					self.startIpkgListInstalled(self.PLUGIN_PREFIX + 'bootlogo-*')
				else:
					self.runSettingsInstall()
			elif self.type == self.REMOVE:
				self.doRemove(self.installFinished, self["list"].l.getCurrentSelection()[0].name + " --force-remove --force-depends")

	def doRemove(self, callback, pkgname):
		self.session.openWithCallback(callback, Console, cmdlist = [self.ipkg_remove + Ipkg.opkgExtraDestinations() + " " + self.PLUGIN_PREFIX + pkgname, "sync"], closeOnSuccess = True)

	def doInstall(self, callback, pkgname):
	        if "mgcamd" in pkgname or "scam" in pkgname or "gbox" in pkgname:
	                print "install mgcamd1"
		        self.session.openWithCallback(callback, Console, cmdlist = [self.ipkg_install1 + " " + self.PLUGIN_PREFIX + pkgname, "sync"], closeOnSuccess = True)	        
	        else: 
		        self.session.openWithCallback(callback, Console, cmdlist = [self.ipkg_install + " " + self.PLUGIN_PREFIX + pkgname, "sync"], closeOnSuccess = True)

	def runSettingsRemove(self, val):
		if val:
			self.doRemove(self.runSettingsInstall, self.remove_settings_name)

	def runBootlogoRemove(self, val):
		if val:
			self.doRemove(self.runSettingsInstall, self.remove_bootlogo_name + " --force-remove --force-depends")

	def runSettingsInstall(self):
		self.doInstall(self.installFinished, self.install_settings_name)

	def ConvertSize(self, size):
		size = int(size)
		if size >= 1073741824:
			Size = '%0.2f TB' % (size / 1073741824.0)
		elif size >= 1048576:
			Size = '%0.2f GB' % (size / 1048576.0)
		elif size >= 1024:
			Size = '%0.2f MB' % (size / 1024.0)
		else:
			Size = '%0.2f KB' % size
		return str(Size)

	def setWindowTitle(self):
	    if self.type == self.DOWNLOAD:
		diskSpace = getVarSpaceKb()
		percFree = int(diskSpace[0] / diskSpace[1] * 100)
		percUsed = int((diskSpace[1] - diskSpace[0]) / diskSpace[1] * 100)
		self.setTitle('%s - %s: %s (%d%%)' % (_('Install plugins'),
		 _('Free'),
		 self.ConvertSize(int(diskSpace[0])),
		 percFree))
		self['spaceused'].setValue(percUsed)
	    elif self.type == self.REMOVE:
 		diskSpace = getVarSpaceKb()
		percFree = int(diskSpace[0] / diskSpace[1] * 100)
		percUsed = int((diskSpace[1] - diskSpace[0]) / diskSpace[1] * 100)
		self.setTitle('%s - %s: %s (%d%%)' % (_('Remove plugins'),
		 _('Free'),
		 self.ConvertSize(int(diskSpace[0])),
		 percFree))
		self['spaceused'].setValue(percUsed)                       
                        			
	def startIpkgListInstalled(self, pkgname = PLUGIN_PREFIX + '*'):
		self.container.execute(self.ipkg + Ipkg.opkgExtraDestinations() + " list_installed '%s'" % pkgname)

	def startIpkgListAvailable(self):
		self.container.execute(self.ipkg + Ipkg.opkgExtraDestinations() + " list '" + self.PLUGIN_PREFIX + "*'")

	def startRun(self):
		listsize = self["list"].instance.size()
		self["list"].instance.hide()
		self.listWidth = listsize.width()
		self.listHeight = listsize.height()
		if self.type == self.DOWNLOAD:
			self.container.execute(self.ipkg + " update")
		elif self.type == self.REMOVE:
			self.run = 1
			self.startIpkgListInstalled()

	def installFinished(self):
		if hasattr(self, 'postInstallCall'):
			try:
				self.postInstallCall()
			except Exception, ex:
				print "[PluginBrowser] postInstallCall failed:", ex
			self.resetPostInstall()
		try:
			os.unlink('/tmp/opkg.conf')
		except:
			pass
		for plugin in self.pluginlist:
			if plugin[3] == self["list"].l.getCurrentSelection()[0].name:
				self.pluginlist.remove(plugin)
				break
		self.plugins_changed = True
		if self["list"].l.getCurrentSelection()[0].name.startswith("settings-"):
			self.reload_settings = True
		self.expanded = []
		self.updateList()
		self["list"].moveToIndex(0)

	def runFinished(self, retval):
		if self.check_settings:
			self.check_settings = False
			self.runSettingsInstall()
			return
		if self.check_bootlogo:
			self.check_bootlogo = False
			self.runSettingsInstall()
			return
		self.remainingdata = ""
		if self.run == 0:
			self.run = 1
			if self.type == self.DOWNLOAD:
				self.startIpkgListInstalled()
		elif self.run == 1 and self.type == self.DOWNLOAD:
			self.run = 2
			from Components import opkg
			pluginlist = []
			self.pluginlist = pluginlist
			for plugin in opkg.enumPlugins(self.PLUGIN_PREFIX):
				if plugin[0] not in self.installedplugins and ((not config.pluginbrowser.po.getValue() and not plugin[0].endswith('-po')) or config.pluginbrowser.po.getValue()) and ((not config.pluginbrowser.src.getValue() and not plugin[0].endswith('-src')) or config.pluginbrowser.src.getValue()):
					pluginlist.append(plugin + (plugin[0][15:],))
			if pluginlist:
				pluginlist.sort()
				self.updateList()
				self["list"].instance.show()
			else:
				self["text"].setText(_("No new plugins found"))
		else:
			if self.pluginlist:
				self.updateList()
				self["list"].instance.show()
			else:
				if self.type == self.DOWNLOAD:
					self["text"].setText(_("Sorry feeds are down for maintenance"))

	def dataAvail(self, str):
		if self.type == self.DOWNLOAD and ('wget returned 1' or 'wget returned 255' or '404 Not Found') in str:
			self.run = 3
			return

		#prepend any remaining data from the previous call
		str = self.remainingdata + str
		#split in lines
		lines = str.split('\n')
		#'str' should end with '\n', so when splitting, the last line should be empty. If this is not the case, we received an incomplete line
		if len(lines[-1]):
			#remember this data for next time
			self.remainingdata = lines[-1]
			lines = lines[0:-1]
		else:
			self.remainingdata = ""

		if self.check_settings:
			self.check_settings = False
			self.remove_settings_name = str.split(' - ')[0].replace(self.PLUGIN_PREFIX, '')
			self.session.openWithCallback(self.runSettingsRemove, MessageBox, _('You already have a channel list installed,\nwould you like to remove\n"%s"?') % self.remove_settings_name)
			return

		if self.check_bootlogo:
			self.check_bootlogo = False
			self.remove_bootlogo_name = str.split(' - ')[0].replace(self.PLUGIN_PREFIX, '')
			self.session.openWithCallback(self.runBootlogoRemove, MessageBox, _('You already have a bootlogo installed,\nwould you like to remove\n"%s"?') % self.remove_bootlogo_name)
			return

		if self.run == 1:
			for x in lines:
				plugin = x.split(" - ", 2)
				# 'opkg list_installed' only returns name + version, no description field
				if len(plugin) >= 2:
					if not plugin[0].endswith('-dev') and not plugin[0].endswith('-staticdev') and not plugin[0].endswith('-dbg') and not plugin[0].endswith('-doc'):
						if plugin[0] not in self.installedplugins:
							if self.type == self.DOWNLOAD and ((not config.pluginbrowser.po.getValue() and not plugin[0].endswith('-po')) or config.pluginbrowser.po.getValue()) and ((not config.pluginbrowser.src.getValue() and not plugin[0].endswith('-src')) or config.pluginbrowser.src.getValue()):
								self.installedplugins.append(plugin[0])
							else:
								if len(plugin) == 2:
									plugin.append('')
								plugin.append(plugin[0][15:])
								self.pluginlist.append(plugin)
			self.pluginlist.sort()

	def updateList(self):
		list = []
		expandableIcon = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/expandable-plugins.png"))
		expandedIcon = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/expanded-plugins.png"))
		verticallineIcon = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/verticalline-plugins.png"))

		self.plugins = {}
		for x in self.pluginlist:
			split = x[3].split('-', 1)
			if len(split) < 2:
				continue
			if not self.plugins.has_key(split[0]):
				self.plugins[split[0]] = []

			self.plugins[split[0]].append((PluginDescriptor(name = x[3], description = x[2], icon = verticallineIcon), split[1], x[1]))

		temp = self.plugins.keys()
		if config.usage.sort_pluginlist.getValue():
			temp.sort()
		for x in temp:
			if x in self.expanded:
				list.append(PluginCategoryComponent(x, expandedIcon, self.listWidth))
				list.extend([PluginDownloadComponent(plugin[0], plugin[1], plugin[2], self.listWidth) for plugin in self.plugins[x]])
			else:
				list.append(PluginCategoryComponent(x, expandableIcon, self.listWidth))
		self.list = list
		self["list"].l.setList(list)
		self["text"] = Label(_("Downloading plugin information complete."))
