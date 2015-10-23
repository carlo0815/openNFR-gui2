from boxbranding import getImageVersion
from urllib import urlopen
import socket
import os
from glob import glob
from enigma import eTimer
from enigma import eConsoleAppContainer, eDVBDB

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
from Screens.Ipkg import Ipkg as Ipkg_1
from Components.config import config
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_ACTIVE_SKIN
from Tools.LoadPixmap import LoadPixmap
from Components.Ipkg import IpkgComponent
from Components.ScrollLabel import ScrollLabel
from os import popen, system, remove, listdir, chdir, getcwd, statvfs, mkdir, path, walk
from Components.ProgressBar import ProgressBar

language.addCallback(plugins.reloadPlugins)

def getVarSpaceKb():
    try:
        s = statvfs('/')
    except OSError:
        return (0, 0)

    return (float(s.f_bfree * (s.f_bsize / 1024)), float(s.f_blocks * (s.f_bsize / 1024)))

class PluginInstall(Screen):
	skin = """
               <screen name="PluginInstall" position="80,160" size="1100,450" title="Installiere Plugins">
				<widget name="list" position="5,0" size="560,300" itemHeight="49" foregroundColor="white" backgroundColor="black" transparent="1" scrollbarMode="showOnDemand" zPosition="2" enableWrapAround="1" />
				<widget name="status" position="580,43" size="518,300" font="Regular;16" halign="center" noWrap="1" transparent="1" />
				<eLabel name="" position="580,6" size="517,30" font="Regular; 22" text="Liste der zu Installierenden Plugins" zPosition="3" halign="center" />
				<widget name="text" position="580,345" size="519,60" zPosition="1" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />
				<widget name="key_green" render="Label" position="46,366" zPosition="2" size="190,22" valign="center" halign="left" font="Regular;21" transparent="1" backgroundColor="foreground" />
				<ePixmap position="5,365" size="35,27" pixmap="/usr/share/enigma2/skin_default/buttons/key_green.png" alphatest="blend" zPosition="2" />
				<widget name="key_blue" render="Label" position="360,366" zPosition="2" size="190,22" valign="center" halign="left" font="Regular;21" transparent="1" backgroundColor="foreground" />
				<ePixmap position="320,365" size="35,27" pixmap="/usr/share/enigma2/skin_default/buttons/key_blue.png" alphatest="blend" zPosition="2" />
				<eLabel name="new eLabel" position="570,0" size="2,400" zPosition="5" foregroundColor="unc0c0c0" backgroundColor="darkgrey" />
				<eLabel name="spaceused" text="% Flash Used..." position="45,414" size="150,20" font="Regular;19" halign="left" foregroundColor="white" backgroundColor="black" transparent="1" zPosition="5" />
				<widget name="spaceused" position="201,415" size="894,20" foregroundColor="white" backgroundColor="blue" zPosition="3" />
			</screen>"""
		  
	DOWNLOAD = 0
	PLUGIN_PREFIX = 'enigma2-plugin-'
	lastDownloadDate = None

	def __init__(self, session, type = 0, needupdate = True):
		Screen.__init__(self, session)
                global pluginfiles
		self.type = type
		self.needupdate = needupdate
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun)
		self.onShown.append(self.setWindowTitle)
                self.setuplist = []

		self.list = []
		self["list"] = PluginList(self.list)
		self.pluginlist = []
		self.expanded = []
		self.installedplugins = []
		self.plugins_changed = False
		self.reload_settings = False
		self.check_settings = False
		self.check_bootlogo = False
		self.install_settings_name = ''
		self.remove_settings_name = ''
		self['spaceused'] = ProgressBar()		
                self["status"] = ScrollLabel()
		self['key_green']  = Label(_('Install'))	
		self['key_blue']  = Label(_('Exit'))
		
		if self.type == self.DOWNLOAD:
			self["text"] = Label(_("Downloading plugin information. Please wait..."))
		self.run = 0
		self.remainingdata = ""
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.go,
			"back": self.requestClose,
			"green": self.install,
			"blue": self.close,
		})
		if os.path.isfile('/usr/bin/opkg'):
			self.ipkg = '/usr/bin/opkg'
			self.ipkg_install = self.ipkg + ' install --force-overwrite'
			self.ipkg_install1 = self.ipkg_install + ' --force-depends'
		else:
			self.ipkg = 'ipkg'
			self.ipkg_install = 'ipkg install --force-overwrite -force-defaults'
			self.ipkg_install1 = self.ipkg_install + ' --force-depends'

	def go(self):
		sel = self["list"].l.getCurrentSelection()
		if sel is None:
			return
                
		sel = sel[0]
		print "selection", sel
		if isinstance(sel, str): # category

			if sel in self.expanded:
			        
				self.expanded.remove(sel)
			else:
				self.expanded.append(sel)
			self.updateList()
			
		else:
		        pluginfiles = ""
			if self.type == self.DOWNLOAD:
			        if sel.name in self.setuplist:
                                        self.setuplist.remove("%s" % sel.name)
                                        if not self.setuplist:
                                               pluginfiles += "no Plugin select"
                                               self.listplugininfo(pluginfiles)
                                        else:
                                               print "Setupliste", self.setuplist 
                                               list = self.setuplist
                                               for item in list:
                                                      pluginfiles += item
                 	                              pluginfiles += "\n" 
                 	                              print "pluginfile1:", pluginfiles
                 	                              self.listplugininfo(pluginfiles)
                                                      self.list = []                                                 
			        else:
 			                self.setuplist.append("%s" % sel.name)
     			                print "Setupliste", self.setuplist
                                        list = self.setuplist
                                        for item in list:
                 	                       pluginfiles += item
                 	                       pluginfiles += "\n"
                 	                       print "pluginfile1:", pluginfiles
                 	                       self.listplugininfo(pluginfiles)
                                               self.list = []    			                

	def install(self):
	        PLUGIN_PREFIX = 'enigma2-plugin-'
		cmdList = []
		for item in self.setuplist:
			cmdList.append((IpkgComponent.CMD_INSTALL, { "package": PLUGIN_PREFIX + item }))
		self.session.open(Ipkg_1, cmdList = cmdList)
                

	def listplugininfo(self, pluginfiles):
		try:
		        pluginfiles.split("/n")	
		        self["status"].setText(pluginfiles)                                
		except:
			self["status"].setText("")



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
			self.doInstall(self.installFinished, pluginnames + ' ' + extra)
		else:
			self.resetPostInstall()

	def runInstall(self, val):
		if val:
			if self.type == self.DOWNLOAD:
				if pluginnames.startswith("enigma2-plugin-picons-"):
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
				elif pluginnames.startswith("enigma2-plugin-display-picon"):
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
				self.install_settings_name = pluginnames
				self.install_bootlogo_name = pluginnames
				if pluginnames.startswith('enigma2-plugin-settings-'):
					self.check_settings = True
					self.startIpkgListInstalled(self.PLUGIN_PREFIX + 'settings-*')
				elif pluginnames.startswith('enigma2-plugin-bootlogo-'):
					self.check_bootlogo = True
					self.startIpkgListInstalled(self.PLUGIN_PREFIX + 'bootlogo-*')
				else:
					self.runSettingsInstall()

	def doInstall(self, callback, pkgname):
	        if "mgcamd" in pkgname or "scam" in pkgname or "gbox" in pkgname:
		        self.session.openWithCallback(callback, Console, cmdlist = [self.ipkg_install1 + " " + self.PLUGIN_PREFIX + pkgname, "sync"], closeOnSuccess = True)	        
	        else: 
		        self.session.openWithCallback(callback, Console, cmdlist = [self.ipkg_install + " " + self.PLUGIN_PREFIX + pkgname, "sync"], closeOnSuccess = True)

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
		diskSpace = getVarSpaceKb()
		percFree = int(diskSpace[0] / diskSpace[1] * 100)
		percUsed = int((diskSpace[1] - diskSpace[0]) / diskSpace[1] * 100)
		self.setTitle('%s - %s: %s (%d%%)' % (_('Install plugins'),
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
			if plugin[3] == pluginnames:
				self.pluginlist.remove(plugin)
				break
		self.plugins_changed = True
		if pluginnames.startswith("enigma2-plugin-settings-"):
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
				if plugin[0] not in self.installedplugins:
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
							if self.type == self.DOWNLOAD:
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
		if config.usage.sort_pluginlist.value:
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
		
class IpkgInstaller(Screen):
	skin = """
		<screen name="IpkgInstaller" position="center,center" size="550,450" title="Install extensions" >
			<ePixmap pixmap="buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
			<widget name="list" position="5,50" size="540,360" />
			<ePixmap pixmap="div-h.png" position="0,410" zPosition="10" size="560,2" transparent="1" alphatest="on" />
			<widget source="introduction" render="Label" position="5,420" zPosition="10" size="550,30" halign="center" valign="center" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		</screen>"""

	def __init__(self, session, list):
		Screen.__init__(self, session)

		self.list = SelectionList()
		self["list"] = self.list
		for listindex in range(len(list)):
			self.list.addSelection(list[listindex], list[listindex], listindex, False)

		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Install"))
		self["key_yellow"] = StaticText()
		self["key_blue"] = StaticText(_("Invert"))
		self["introduction"] = StaticText(_("Press OK to toggle the selection."))

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"ok": self.list.toggleSelection,
			"cancel": self.close,
			"red": self.close,
			"green": self.install,
			"blue": self.list.toggleAllSelection
		}, -1)

	def install(self):
		list = self.list.getSelectionsList()
		cmdList = []
		for item in list:
			cmdList.append((IpkgComponent.CMD_INSTALL, { "package": item[1] }))
		self.session.open(Ipkg, cmdList = cmdList)

class PluginDeinstall(Screen):
	skin = """
               <screen name="PluginDeinstall" position="80,160" size="1100,450" title="Deinstalliere Plugins">
				<widget name="list" position="5,0" size="560,300" itemHeight="49" foregroundColor="white" backgroundColor="black" transparent="1" scrollbarMode="showOnDemand" zPosition="2" enableWrapAround="1" />
				<widget name="status" position="580,43" size="518,300" font="Regular;16" halign="center" noWrap="1" transparent="1" />
				<eLabel name="" position="580,6" size="517,30" font="Regular; 22" text="Liste der zu Deinstallierenden Plugins" zPosition="3" halign="center" />
				<widget name="text" position="580,345" size="519,60" zPosition="1" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />
				<widget name="key_green" render="Label" position="46,366" zPosition="2" size="190,22" valign="center" halign="left" font="Regular;21" transparent="1" backgroundColor="foreground" />
				<ePixmap position="5,365" size="35,27" pixmap="/usr/share/enigma2/skin_default/buttons/key_green.png" alphatest="blend" zPosition="2" />
				<widget name="key_blue" render="Label" position="360,366" zPosition="2" size="190,22" valign="center" halign="left" font="Regular;21" transparent="1" backgroundColor="foreground" />
				<ePixmap position="320,365" size="35,27" pixmap="/usr/share/enigma2/skin_default/buttons/key_blue.png" alphatest="blend" zPosition="2" />
				<eLabel name="new eLabel" position="570,0" size="2,400" zPosition="5" foregroundColor="unc0c0c0" backgroundColor="darkgrey" />
				<eLabel name="spaceused" text="% Flash Used..." position="45,414" size="150,20" font="Regular;19" halign="left" foregroundColor="white" backgroundColor="black" transparent="1" zPosition="5" />
				<widget name="spaceused" position="201,415" size="894,20" foregroundColor="white" backgroundColor="blue" zPosition="3" />
			</screen>"""
               
	REMOVE = 1		  
	DOWNLOAD = 0
	PLUGIN_PREFIX = 'enigma2-plugin-'
	lastDownloadDate = None

	def __init__(self, session, type = 1, needupdate = True):
		Screen.__init__(self, session)
                global pluginfiles
		self.type = type
		self.needupdate = needupdate
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun)
		self.onShown.append(self.setWindowTitle)
                self.setuplist = []

		self.list = []
		self["list"] = PluginList(self.list)
		self.pluginlist = []
		self.expanded = []
		self.installedplugins = []
		self.plugins_changed = False
		self.reload_settings = False
		self.check_settings = False
		self.check_bootlogo = False
		self.install_settings_name = ''
		self.remove_settings_name = ''
		self['spaceused'] = ProgressBar()		
                self["status"] = ScrollLabel()
		self['key_green']  = Label(_('Deinstall'))	
		self['key_blue']  = Label(_('Exit'))
		
		if self.type == self.DOWNLOAD:
			self["text"] = Label(_("Downloading plugin information. Please wait..."))
		self.run = 0
		self.remainingdata = ""
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.go,
			"back": self.requestClose,
			"green": self.install,
			"blue": self.close,
			
		})
		if os.path.isfile('/usr/bin/opkg'):
			self.ipkg = '/usr/bin/opkg'
			self.ipkg_install = self.ipkg + ' install --force-overwrite'
			self.ipkg_remove =  self.ipkg + ' remove --autoremove --force-depends'
		else:
			self.ipkg = 'ipkg'
			self.ipkg_install = 'ipkg install --force-overwrite -force-defaults'
			self.ipkg_remove =  self.ipkg + ' remove --autoremove --force-depends'

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
		        pluginfiles = ""
			if self.type == self.DOWNLOAD:
			        if sel.name in self.setuplist:
                                        self.setuplist.remove("%s" % sel.name)
                                        if not self.setuplist:
                                               pluginfiles += "no Plugin select"
                                               self.listplugininfo(pluginfiles)
                                        else:
                                               list = self.setuplist
                                               for item in list:
                                                      pluginfiles += item
                 	                              pluginfiles += "\n" 
                 	                              self.listplugininfo(pluginfiles)
                                                      self.list = []                                                 
			        else:
 			                self.setuplist.append("%s" % sel.name)
                                        list = self.setuplist
                                        for item in list:
                 	                       pluginfiles += item
                 	                       pluginfiles += "\n"
                 	                       self.listplugininfo(pluginfiles)
                                               self.list = []    
                                               
                       	elif self.type == self.REMOVE:
			        if sel.name in self.setuplist:
                                        self.setuplist.remove("%s" % sel.name)
                                        if not self.setuplist:
                                               pluginfiles += "no Plugin select"
                                               self.listplugininfo(pluginfiles)
                                        else:
                                               list = self.setuplist
                                               for item in list:
                                                      pluginfiles += item
                 	                              pluginfiles += "\n" 
                 	                              self.listplugininfo(pluginfiles)
                                                      self.list = []                                                 
			        else:
 			                self.setuplist.append("%s" % sel.name)
                                        list = self.setuplist
                                        for item in list:
                 	                       pluginfiles += item
                 	                       pluginfiles += "\n"
                 	                       self.listplugininfo(pluginfiles)
                                               self.list = []                         
                                               			                

	def install(self):
	        PLUGIN_PREFIX = 'enigma2-plugin-'
		cmdList = []
		for item in self.setuplist:
			cmdList.append((IpkgComponent.CMD_REMOVE, { "package": PLUGIN_PREFIX + item }))
		self.session.open(Ipkg_1, cmdList = cmdList)
	
		
	def listplugininfo(self, pluginfiles):
		try:
		        pluginfiles.split("/n")	
		        self["status"].setText(pluginfiles)                                
		except:
			self["status"].setText("")



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
			self.doInstall(self.installFinished, pluginnames + ' ' + extra)
		else:
			self.resetPostInstall()

	def runInstall(self, val):
		if val:
			if self.type == self.DOWNLOAD:
				if pluginnames.startswith("enigma2-plugin-picons-"):
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
				elif pluginnames.startswith("enigma2-plugin-display-picon"):
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
				self.install_settings_name = pluginnames
				self.install_bootlogo_name = pluginnames
				if pluginnames.startswith('enigma2-plugin-settings-'):
					self.check_settings = True
					self.startIpkgListInstalled(self.PLUGIN_PREFIX + 'settings-*')
				elif pluginnames.startswith('enigma2-plugin-bootlogo-'):
					self.check_bootlogo = True
					self.startIpkgListInstalled(self.PLUGIN_PREFIX + 'bootlogo-*')
				else:
					self.runSettingsInstall()
			elif self.type == self.REMOVE:
				self.doRemove(self.installFinished, pluginnames + " --force-remove --force-depends")

	def doRemove(self, callback, pkgname):
		self.session.openWithCallback(callback, Console, cmdlist = [self.ipkg_remove + Ipkg.opkgExtraDestinations() + " " + self.PLUGIN_PREFIX + pkgname, "sync"], closeOnSuccess = True)
					
	def doInstall(self, callback, pkgname):
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
			if plugin[3] == pluginnames:
				self.pluginlist.remove(plugin)
				break
		self.plugins_changed = True
		if pluginnames.startswith("enigma2-plugin-settings-"):
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
				if plugin[0] not in self.installedplugins:
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
							if self.type == self.DOWNLOAD:
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
		if config.usage.sort_pluginlist.value:
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
			
