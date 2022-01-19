from __future__ import print_function
import sys, os
from time import time
if os.path.isfile("/usr/lib/enigma2/python/enigma.zip"):
	sys.path.append("/usr/lib/enigma2/python/enigma.zip")

from Tools.Profile import profile, profile_final
profile("PYTHON_START")

import Tools.RedirectOutput
import enigma
from boxbranding import getBoxType, getMachineProcModel, getMachineBuild, getBrandOEM
import eConsoleImpl
import eBaseImpl
enigma.eTimer = eBaseImpl.eTimer
enigma.eSocketNotifier = eBaseImpl.eSocketNotifier
enigma.eConsoleAppContainer = eConsoleImpl.eConsoleAppContainer
boxtype = getBoxType()
if os.path.isfile("/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/plugin.pyo") and boxtype in ('dm7080','dm820','dm520','dm525','dm900'):
	import pyo_patcher
if boxtype in ('dm500hd','dm500hdv2','dm520','dm525','dm7020hd','dm7020hdv2','dm7080','dm800','dm8000','dm800se','dm800sev2','dm820','dm900','dm920' ):
	os.system("cp /usr/lib/enigma2/python/Plugins/Extensions/Infopanel/images/dreambox /usr/share/bootlogo.mvi")		
from traceback import print_exc

profile("Geolocation")
import Tools.Geolocation
Tools.Geolocation.InitGeolocation()

profile("SetupDevices")
import Components.SetupDevices
Components.SetupDevices.InitSetupDevices()

profile("SimpleSummary")
from Screens import InfoBar
from Screens.SimpleSummary import SimpleSummary

from sys import stdout, exc_info

profile("Bouquets")
from Components.config import config, configfile, ConfigText, ConfigYesNo, ConfigInteger, ConfigDictionarySet, NoSave
config.misc.load_unlinked_userbouquets = ConfigYesNo(default=False)
def setLoadUnlinkedUserbouquets(configElement):
	enigma.eDVBDB.getInstance().setLoadUnlinkedUserbouquets(configElement.value)
config.misc.load_unlinked_userbouquets.addNotifier(setLoadUnlinkedUserbouquets)
enigma.eDVBDB.getInstance().reloadBouquets()

profile("ParentalControl")
import Components.ParentalControl
Components.ParentalControl.InitParentalControl()

profile("LOAD:Navigation")
from Navigation import Navigation

profile("LOAD:skin")
from skin import readSkin

profile("LOAD:Tools")
from Tools.Directories import InitFallbackFiles, resolveFilename, SCOPE_PLUGINS, SCOPE_ACTIVE_SKIN, SCOPE_CURRENT_SKIN, SCOPE_CONFIG
from Components.config import config, configfile, ConfigText, ConfigYesNo, ConfigInteger, ConfigSelection, NoSave
import Components.RecordingConfig
InitFallbackFiles()

profile("config.misc")
config.misc.boxtype = ConfigText(default = boxtype)
config.misc.blackradiopic = ConfigText(default = resolveFilename(SCOPE_CURRENT_SKIN, "black.mvi"))
config.misc.radiopic = ConfigText(default = resolveFilename(SCOPE_ACTIVE_SKIN, "radio.mvi"))
config.misc.nextWakeup = ConfigText(default = "-1,-1,0,0,-1,0") #wakeup time, timer begins, set by (0=rectimer,1=zaptimer, 2=powertimer or 3=plugin), go in standby, next rectimer, force rectimer
config.misc.isNextRecordTimerAfterEventActionAuto = ConfigYesNo(default=False)
config.misc.isNextPowerTimerAfterEventActionAuto = ConfigYesNo(default=False)
config.misc.SyncTimeUsing = ConfigSelection(default = "0", choices = [("0", "Transponder Time"), ("1", _("NTP"))])
config.misc.NTPserver = ConfigText(default = 'pool.ntp.org', fixed_size=False)

config.misc.startCounter = ConfigInteger(default=0) # number of e2 starts...
config.misc.standbyCounter = NoSave(ConfigInteger(default=0)) # number of standby
config.misc.DeepStandby = NoSave(ConfigYesNo(default=False)) # detect deepstandby

#demo code for use of standby enter leave callbacks
#def leaveStandby():
#	print "!!!!!!!!!!!!!!!!!leave standby"

#def standbyCountChanged(configelement):
#	print "!!!!!!!!!!!!!!!!!enter standby num", configelement.value
#	from Screens.Standby import inStandby
#	inStandby.onClose.append(leaveStandby)

#config.misc.standbyCounter.addNotifier(standbyCountChanged, initial_call = False)
####################################################

def useSyncUsingChanged(configelement):
	if os.path.isfile("/usr/bin/dvbdate"):
		from Components.Console import Console
		Console = Console()
		Console.ePopen('/usr/bin/dvbdate')	
	if config.misc.SyncTimeUsing.value == "0":
		print("[Time By]: Transponder")
		enigma.eDVBLocalTimeHandler.getInstance().setUseDVBTime(True)
		enigma.eEPGCache.getInstance().timeUpdated()
	else:
		print("[Time By]: NTP")
		enigma.eDVBLocalTimeHandler.getInstance().setUseDVBTime(False)
		enigma.eEPGCache.getInstance().timeUpdated()
config.misc.SyncTimeUsing.addNotifier(useSyncUsingChanged)

def NTPserverChanged(configelement):
	if config.misc.NTPserver.value == "pool.ntp.org":
		return
	print("[NTPDATE] save /etc/default/ntpdate")
	f = open("/etc/default/ntpdate", "w")
	f.write('NTPSERVERS="' + config.misc.NTPserver.value + '"')
	f.close()
	os.chmod("/etc/default/ntpdate", 0o755)
	from Components.Console import Console
	Console = Console()
	Console.ePopen('/usr/bin/ntpdate-sync')
config.misc.NTPserver.addNotifier(NTPserverChanged, immediate_feedback = True)

profile("Twisted")
try:
	import twisted.python.runtime
	twisted.python.runtime.platform.supportsThreads = lambda: True

	import e2reactor
	e2reactor.install()

	from twisted.internet import reactor

	def runReactor():
		reactor.run(installSignalHandlers=False)
except ImportError:
	print("twisted not available")
	def runReactor():
		enigma.runMainloop()

profile("LOAD:Plugin")

# initialize autorun plugins and plugin menu entries
from Components.PluginComponent import plugins

profile("LOAD:Wizard")
from Screens.Wizard import wizardManager
from Screens.StartWizard import *
import Screens.Rc
from Tools.BoundFunction import boundFunction
from Plugins.Plugin import PluginDescriptor


profile("misc")
had = dict()

def dump(dir, p = ""):
	if isinstance(dir, dict):
		for (entry, val) in dir.items():
			dump(val, p + "(dict)/" + entry)
	if hasattr(dir, "__dict__"):
		for name, value in dir.__dict__.items():
			if str(value) not in had:
				had[str(value)] = 1
				dump(value, p + "/" + str(name))
			else:
				print(p + "/" + str(name) + ":" + str(dir.__class__) + "(cycle)")
	else:
		print(p + ":" + str(dir))

# + ":" + str(dir.__class__)

# display

profile("LOAD:ScreenGlobals")
from Screens.Globals import Globals
from Screens.SessionGlobals import SessionGlobals
from Screens.Screen import Screen

profile("Screen")
Screen.globalScreen = Globals()

# Session.open:
# * push current active dialog ('current_dialog') onto stack
# * call execEnd for this dialog
#   * clear in_exec flag
#   * hide screen
# * instantiate new dialog into 'current_dialog'
#   * create screens, components
#   * read, apply skin
#   * create GUI for screen
# * call execBegin for new dialog
#   * set in_exec
#   * show gui screen
#   * call components' / screen's onExecBegin
# ... screen is active, until it calls 'close'...
# Session.close:
# * assert in_exec
# * save return value
# * start deferred close handler ('onClose')
# * execEnd
#   * clear in_exec
#   * hide screen
# .. a moment later:
# Session.doClose:
# * destroy screen

class Session:
	def __init__(self, desktop = None, summary_desktop = None, navigation = None):
		self.desktop = desktop
		self.summary_desktop = summary_desktop
		self.nav = navigation
		self.delay_timer = enigma.eTimer()
		self.delay_timer.callback.append(self.processDelay)

		self.current_dialog = None

		self.dialog_stack = [ ]
		self.summary_stack = [ ]
		self.summary = None

		self.in_exec = False

		self.screen = SessionGlobals(self)

		for p in plugins.getPlugins(PluginDescriptor.WHERE_SESSIONSTART):
			try:
				p(reason=0, session=self)
			except:
				print("Plugin raised exception at WHERE_SESSIONSTART")
				import traceback
				traceback.print_exc()

	def processDelay(self):
		callback = self.current_dialog.callback

		retval = self.current_dialog.returnValue

		if self.current_dialog.isTmp:
			self.current_dialog.doClose()
#			dump(self.current_dialog)
			del self.current_dialog
		else:
			del self.current_dialog.callback

		self.popCurrent()
		if callback is not None:
			callback(*retval)

	def execBegin(self, first=True, do_show = True):
		assert not self.in_exec
		self.in_exec = True
		c = self.current_dialog

		# when this is an execbegin after a execend of a "higher" dialog,
		# popSummary already did the right thing.
		if first:
			self.instantiateSummaryDialog(c)

		c.saveKeyboardMode()
		c.execBegin()

		# when execBegin opened a new dialog, don't bother showing the old one.
		if c == self.current_dialog and do_show:
			c.show()

	def execEnd(self, last=True):
		assert self.in_exec
		self.in_exec = False

		self.current_dialog.execEnd()
		self.current_dialog.restoreKeyboardMode()
		self.current_dialog.hide()

		if last:
			self.current_dialog.removeSummary(self.summary)
			self.popSummary()

	def create(self, screen, arguments, **kwargs):
		# creates an instance of 'screen' (which is a class)
		try:
			return screen(self, *arguments, **kwargs)
		except:
			errstr = "Screen %s(%s, %s): %s" % (str(screen), str(arguments), str(kwargs), exc_info()[0])
			print(errstr)
			print_exc(file=stdout)
			enigma.quitMainloop(5)

	def instantiateDialog(self, screen, *arguments, **kwargs):
		return self.doInstantiateDialog(screen, arguments, kwargs, self.desktop)

	def deleteDialog(self, screen):
		screen.hide()
		screen.doClose()

	def deleteDialogWithCallback(self, callback, screen, *retval):
		screen.hide()
		screen.doClose()
		if callback is not None:
			callback(*retval)

	def instantiateSummaryDialog(self, screen, **kwargs):
		self.pushSummary()
		summary = screen.createSummary() or SimpleSummary
		arguments = (screen,)
		self.summary = self.doInstantiateDialog(summary, arguments, kwargs, self.summary_desktop)
		self.summary.show()
		screen.addSummary(self.summary)

	def doInstantiateDialog(self, screen, arguments, kwargs, desktop):
		# create dialog

		try:
			dlg = self.create(screen, arguments, **kwargs)
		except:
			print('EXCEPTION IN DIALOG INIT CODE, ABORTING:')
			print('-'*60)
			print_exc(file=stdout)
			enigma.quitMainloop(5)
			print('-'*60)

		if dlg is None:
			return

		# read skin data
		readSkin(dlg, None, dlg.skinName, desktop)

		# create GUI view of this dialog
		assert desktop is not None

		dlg.setDesktop(desktop)
		dlg.applySkin()

		return dlg

	def pushCurrent(self):
		if self.current_dialog is not None:
			self.dialog_stack.append((self.current_dialog, self.current_dialog.shown))
			self.execEnd(last=False)

	def popCurrent(self):
		if self.dialog_stack:
			(self.current_dialog, do_show) = self.dialog_stack.pop()
			self.execBegin(first=False, do_show=do_show)
		else:
			self.current_dialog = None

	def execDialog(self, dialog):
		self.pushCurrent()
		self.current_dialog = dialog
		self.current_dialog.isTmp = False
		self.current_dialog.callback = None # would cause re-entrancy problems.
		self.execBegin()

	def openWithCallback(self, callback, screen, *arguments, **kwargs):
		dlg = self.open(screen, *arguments, **kwargs)
		dlg.callback = callback
		return dlg

	def open(self, screen, *arguments, **kwargs):
		if self.dialog_stack and not self.in_exec:
			raise RuntimeError("modal open are allowed only from a screen which is modal!")
			# ...unless it's the very first screen.

		self.pushCurrent()
		dlg = self.current_dialog = self.instantiateDialog(screen, *arguments, **kwargs)
		dlg.isTmp = True
		dlg.callback = None
		self.execBegin()
		return dlg

	def close(self, screen, *retval):
		if not self.in_exec:
			print("close after exec!")
			return

		# be sure that the close is for the right dialog!
		# if it's not, you probably closed after another dialog
		# was opened. this can happen if you open a dialog
		# onExecBegin, and forget to do this only once.
		# after close of the top dialog, the underlying will
		# gain focus again (for a short time), thus triggering
		# the onExec, which opens the dialog again, closing the loop.
		assert screen == self.current_dialog

		self.current_dialog.returnValue = retval
		self.delay_timer.start(0, 1)
		self.execEnd()

	def pushSummary(self):
		if self.summary is not None:
			self.summary.hide()
		self.summary_stack.append(self.summary)
		self.summary = None

	def popSummary(self):
		if self.summary is not None:
			self.summary.doClose()
		self.summary = self.summary_stack.pop()
		if self.summary is not None:
			self.summary.show()

profile("Standby,PowerKey")
import Screens.Standby
from Screens.Menu import MainMenu, mdom
from GlobalActions import globalActionMap
from time import time

class PowerKey:
	""" PowerKey stuff - handles the powerkey press and powerkey release actions"""

	def __init__(self, session):
		self.session = session
		globalActionMap.actions["power_down"]=self.powerdown
		globalActionMap.actions["power_up"]=self.powerup
		globalActionMap.actions["power_long"]=self.powerlong
		globalActionMap.actions["deepstandby"]=self.shutdown # frontpanel long power button press
		globalActionMap.actions["discrete_off"]=self.standby
		globalActionMap.actions["sleeptimer"]=self.openSleepTimer
		globalActionMap.actions["powertimer_standby"]=self.sleepStandby
		globalActionMap.actions["powertimer_deepstandby"]=self.sleepDeepStandby		
		self.standbyblocked = 1

	def MenuClosed(self, *val):
		self.session.infobar = None

	def shutdown(self):
		wasRecTimerWakeup = False
		recordings = self.session.nav.getRecordings()
		if not recordings:
			next_rec_time = self.session.nav.RecordTimer.getNextRecordingTime()
		if recordings or (next_rec_time > 0 and (next_rec_time - time()) < 360):
			if os.path.exists("/tmp/was_rectimer_wakeup") and not self.session.nav.RecordTimer.isRecTimerWakeup():
				f = open("/tmp/was_rectimer_wakeup", "r")
				file = f.read()
				f.close()
				wasRecTimerWakeup = int(file) and True or False
			if self.session.nav.RecordTimer.isRecTimerWakeup() or wasRecTimerWakeup or self.session.nav.RecordTimer.isRecording():
				print("PowerOff (timer wakewup) - Recording in progress or a timer about to activate, entering standby!")
				lastrecordEnd = 0
				for timer in self.session.nav.RecordTimer.timer_list:
					if lastrecordEnd == 0 or lastrecordEnd >= timer.begin:
						print("Set after-event for recording %s to DEEP-STANDBY." % timer.name)
						timer.afterEvent = 2
						if timer.end > lastrecordEnd:
							lastrecordEnd = timer.end + 900
				from Screens.MessageBox import MessageBox
				self.session.openWithCallback(self.gotoStandby, MessageBox, _("Recording(s) are in progress or coming up in few seconds!\nEntering standby, after recording the box will shutdown."), type = MessageBox.TYPE_INFO, close_on_any_key = True, timeout = 10)
			else:
				print("PowerOff - Now!")
				self.session.open(Screens.Standby.TryQuitMainloop, 1)
		elif not Screens.Standby.inTryQuitMainloop and self.session.current_dialog and self.session.current_dialog.ALLOW_SUSPEND:
			print("PowerOff - Now!")
			self.session.open(Screens.Standby.TryQuitMainloop, 1)

	def powerlong(self):
		if Screens.Standby.inTryQuitMainloop or (self.session.current_dialog and not self.session.current_dialog.ALLOW_SUSPEND):
			return
		self.doAction(action = config.usage.on_long_powerpress.value)

	def doAction(self, action):
		if Screens.Standby.TVinStandby.getTVstate('standby'):
			Screens.Standby.TVinStandby.setTVstate('on')    
		self.standbyblocked = 1
		if action == "shutdown":
			self.shutdown()
		elif action == "show_menu":
			print("Show shutdown Menu")
			root = mdom.getroot()
			for x in root.findall("menu"):
				y = x.find("id")
				if y is not None:
					id = y.get("val")
					if id and id == "shutdown":
						self.session.infobar = self
						menu_screen = self.session.openWithCallback(self.MenuClosed, MainMenu, x)
						menu_screen.setTitle(_("Standby / restart"))
						return
		elif action == "standby":
			Screens.Standby.TVinStandby.skipHdmiCecNow(False)
			self.standby()
		elif action == "standby_noTVshutdown":
			Screens.Standby.TVinStandby.skipHdmiCecNow(True)
			self.standby()        
		elif action == "powertimerStandby":
			val = 3
			self.setSleepTimer(val)
		elif action == "powertimerDeepStandby":
			val = 4
			self.setSleepTimer(val)
		elif action == "sleeptimer":
			self.openSleepTimer()			

	def powerdown(self):
		self.standbyblocked = 0

	def powerup(self):
		if self.standbyblocked == 0:
			self.doAction(action = config.usage.on_short_powerpress.value)
	
	def gotoStandby(self, ret):
		self.standby()
	
	def standby(self):
		if not Screens.Standby.inStandby and self.session.current_dialog and self.session.current_dialog.ALLOW_SUSPEND and self.session.in_exec:
			self.session.open(Screens.Standby.Standby)
			
	def openSleepTimer(self):
		from Screens.SleepTimerEdit import SleepTimerEdit
		self.session.open(SleepTimerEdit)

	def setSleepTimer(self, val):
		from PowerTimer import PowerTimerEntry
		sleeptime = 15
		data = (int(time() + 60), int(time() + 120))
		self.addSleepTimer(PowerTimerEntry(checkOldTimers = True, *data, timerType = val, autosleepdelay = sleeptime))

	def addSleepTimer(self, timer):
		from Screens.PowerTimerEntry import TimerEntry
		self.session.openWithCallback(self.finishedAdd, TimerEntry, timer)

	def finishedAdd(self, answer):
		if answer[0]:
			entry = answer[1]
			simulTimerList = self.session.nav.PowerTimer.record(entry)

	def sleepStandby(self):
		self.doAction(action = "powertimerStandby")

	def sleepDeepStandby(self):
		self.doAction(action = "powertimerDeepStandby")
		
	def timerstdby(self):
		try:
			f = open("/tmp/was_timer_wakeup.txt", "r")
			file = f.read()
			f.close()
			if config.usage.recording_timer_start.value == True:
				if file == "True":
					from Screens.MessageBox import MessageBox
					self.session.openWithCallback(self.timergotostdby,MessageBox,_("Entering standby, after recording the box will go to shutdown or stay in Standby (Automatic or shutdown Choise in recordsconfigs)"), type = MessageBox.TYPE_INFO, timeout = 10)

			else:
				print("normal Start")	
		except:
			print("was_timer_wakeup not exist")	

	def timergotostdby(self, ret):
		self.session.open(Screens.Standby.Standby)

profile("Scart")
from Screens.Scart import Scart

class AutoScartControl:
	def __init__(self, session):
		self.force = False
		self.current_vcr_sb = enigma.eAVSwitch.getInstance().getVCRSlowBlanking()
		if self.current_vcr_sb and config.av.vcrswitch.value:
			self.scartDialog = session.instantiateDialog(Scart, True)
		else:
			self.scartDialog = session.instantiateDialog(Scart, False)
		config.av.vcrswitch.addNotifier(self.recheckVCRSb)
		enigma.eAVSwitch.getInstance().vcr_sb_notifier.get().append(self.VCRSbChanged)

	def recheckVCRSb(self, configelement):
		self.VCRSbChanged(self.current_vcr_sb)

	def VCRSbChanged(self, value):
		#print "vcr sb changed to", value
		self.current_vcr_sb = value
		if config.av.vcrswitch.value or value > 2:
			if value:
				self.scartDialog.showMessageBox()
			else:
				self.scartDialog.switchToTV()

profile("Load:CI")
from Screens.Ci import CiHandler

profile("Load:VolumeControl")
from Components.VolumeControl import VolumeControl

from time import time, localtime, strftime
from Tools.StbHardware import setFPWakeuptime, setRTCtime

def autorestoreLoop():
	# Check if auto restore settings fails, just start the wizard (avoid a endless loop) 
	count = 0
	if os.path.exists("/media/hdd/images/config/autorestore"):
		f = open("/media/hdd/images/config/autorestore", "r")
		try:
			count = int(f.read())
		except:
			count = 0;
		f.close()
		if count >= 3:
			return False
	count += 1
	f = open("/media/hdd/images/config/autorestore", "w")
	f.write(str(count))
	f.close()
	return True		

def runScreenTest():
	config.misc.startCounter.value += 1

	profile("readPluginList")
	plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))

	profile("Init:Session")
	nav = Navigation(config.misc.nextWakeup.value)
	#nav = Navigation(config.misc.isNextRecordTimerAfterEventActionAuto.value, config.misc.isNextPowerTimerAfterEventActionAuto.value)
	session = Session(desktop = enigma.getDesktop(0), summary_desktop = enigma.getDesktop(1), navigation = nav)

	CiHandler.setSession(session)

	profile("wizards")
	screensToRun = []
	RestoreSettings = None
	import hashlib
	import os
	from os import path
	from pathlib import Path
	import fileinput, sys	
	def md5_update_from_file(filename, hash):
		assert Path(filename).is_file()
		with open(str(filename), "rb") as f:
			for chunk in iter(lambda: f.read(4096), b""):
				hash.update(chunk)
		return hash


	def md5_file(filename):
		return md5_update_from_file(filename, hashlib.md5()).hexdigest()

	def md5_update_from_dir(directory, hash):
		assert Path(directory).is_dir()
		for path in sorted(Path(directory).iterdir()):
			hash.update(path.name.encode())
			if path.is_file():
				hash = md5_update_from_file(path, hash)
			elif path.is_dir():
				hash = md5_update_from_dir(path, hash)
		return hash


	def md5_dir(directory):
		return md5_update_from_dir(directory, hashlib.md5()).hexdigest()	
	
	
	sha256hash = ()
	myfilecheck = "/usr/lib/enigma2/python/Plugins/Extensions/Infopanel"
	sha256save = "/var/lib/opkg/info/enigma2-plugin-extensions-infopanel.sha256"
	if config.misc.firstrun.value == True:
		myfile = Path(sha256save)
		if os.path.isfile(sha256save):
			os.remove(sha256save)
		myfile.touch(exist_ok=True)
		sha256hash = md5_dir(myfilecheck)
		sha_f = open(sha256save, "a")
		sha_f.write(sha256hash)
		sha_f.close()
	else:
		if os.path.isfile(sha256save): 
			sha256hash = md5_dir(myfilecheck)
			try:
				sha256read = open(sha256save,'r')
				sha256hash1 = sha256read.read()
				print("sha256hash1:", sha256hash1)
				print("sha256hash:", sha256hash)				
				if sha256hash == sha256hash1:
					print("all ok with Infopanel")
				else:
					print("Sorry, but you change our Infopanel so we had to disable it!!")
					sub_menu_sort = NoSave(ConfigDictionarySet())
					sub_menu_sort.value = config.usage.menu_sort_weight.getConfigValue("mainmenu", "submenu")
					m_weight = sub_menu_sort.getConfigValue('Infopanel', "sort")
					m_weight1 = sub_menu_sort.getConfigValue('Infopanel', "hidden")
					sub_menu_sort.changeConfigValue('Infopanel', "hidden", "1")				
					config.usage.menu_sort_weight.save()
					configfile.save()			
				
				sha256read.close()
			
			except:
				print("Sorry, but you change our Infopanel so we had to disable it!!")
				sub_menu_sort = NoSave(ConfigDictionarySet())
				sub_menu_sort.value = config.usage.menu_sort_weight.getConfigValue("mainmenu", "submenu")
				m_weight = sub_menu_sort.getConfigValue('Infopanel', "sort")
				m_weight1 = sub_menu_sort.getConfigValue('Infopanel', "hidden")
				sub_menu_sort.changeConfigValue('Infopanel', "hidden", "1")				
				config.usage.menu_sort_weight.save()
				configfile.save()                                        
		else:
			print("Sorry, but you change our Infopanel so we had to disable it!!")
			sub_menu_sort = NoSave(ConfigDictionarySet())
			sub_menu_sort.value = config.usage.menu_sort_weight.getConfigValue("mainmenu", "submenu")
			m_weight = sub_menu_sort.getConfigValue('Infopanel', "sort")
			m_weight1 = sub_menu_sort.getConfigValue('Infopanel', "hidden")
			sub_menu_sort.changeConfigValue('Infopanel', "hidden", "1")				
			config.usage.menu_sort_weight.save()
			configfile.save()                                                  
                                                                            	
	if os.path.exists("/media/hdd/images/config/settings") and config.misc.firstrun.value:
		if autorestoreLoop():
			RestoreSettings = True
			from Plugins.SystemPlugins.SoftwareManager.BackupRestore import RestoreScreen
			os.system("rm /media/hdd/images/config/settings")
			session.open(RestoreScreen, runRestore = True)
		else:
			os.system("rm /media/hdd/images/config/settings")
			screensToRun = [ p.__call__ for p in plugins.getPlugins(PluginDescriptor.WHERE_WIZARD) ]
			screensToRun += wizardManager.getWizards()
	else:
		if os.path.exists("/media/hdd/images/config/autorestore"):
			os.system('rm -f /media/hdd/images/config/autorestore')
		screensToRun = [ p.__call__ for p in plugins.getPlugins(PluginDescriptor.WHERE_WIZARD) ]
		screensToRun += wizardManager.getWizards()
	
	screensToRun.append((100, InfoBar.InfoBar))
	screensToRun.sort()
	print(screensToRun)

	enigma.ePythonConfigQuery.setQueryFunc(configfile.getResolvedKey)

	def runNextScreen(session, screensToRun, *result):
		config.easysetup = ConfigSubsection()
		config.easysetup.restart = ConfigBoolean(default = False)
		if config.easysetup.restart.value == True:
			print("restart after Wizard2")
			config.easysetup.restart.setValue(False)
			config.easysetup.restart.save()
			enigma.quitMainloop(3)
		if result:
			print("[mytest.py] quitMainloop #3")
			enigma.quitMainloop(*result)
			return

		screen = screensToRun[0][1]
		args = screensToRun[0][2:]
		if screensToRun:
			session.openWithCallback(boundFunction(runNextScreen, session, screensToRun[1:]), screen, *args)
		else:
			session.open(screen, *args)

	if not RestoreSettings:
		runNextScreen(session, screensToRun)

	profile("Init:VolumeControl")
	vol = VolumeControl(session)
	profile("Init:PowerKey")
	power = PowerKey(session)
	power.timerstdby()        
	if boxtype in ('alien5', 'osninopro', 'osnino', 'osninoplus', 'alphatriple', 'spycat4kmini', 'tmtwin4k', 'mbmicrov2', 'revo4k', 'force3uhd', 'wetekplay', 'wetekplay2', 'wetekhub', 'dm7020hd', 'dm7020hdv2', 'osminiplus', 'osmega', 'sf3038', 'spycat', 'e4hd', 'e4hdhybrid', 'mbmicro', 'et7500', 'mixosf5', 'mixosf7', 'mixoslumi', 'gi9196m', 'maram9', 'ixussone', 'ixusszero', 'uniboxhd1', 'uniboxhd2', 'uniboxhd3', 'sezam5000hd', 'mbtwin', 'sezam1000hd', 'mbmini', 'atemio5x00', 'beyonwizt3', '9910lx', '9911lx', '9920lx') or getBrandOEM() in ('fulan') or getMachineBuild() in ('u41', 'dags7362', 'dags73625', 'dags5', 'ustym4kpro', 'beyonwizv2', 'viper4k', 'sf8008', 'sf8008m', 'cc1', 'gbmv200'):
		profile("VFDSYMBOLS")
	import Components.VfdSymbols
	Components.VfdSymbols.SymbolsCheck(session)
		
	# we need session.scart to access it from within menu.xml
	session.scart = AutoScartControl(session)

	profile("Init:Trashcan")
	import Tools.Trashcan
	Tools.Trashcan.init(session)

	profile("Init:AutoVideoMode")
	import Screens.VideoMode
	Screens.VideoMode.autostart(session)

	profile("RunReactor")
	profile_final()

	if boxtype in ('sf8', 'classm', 'axodin', 'axodinc', 'starsatlx', 'genius', 'evo'):
		f = open("/dev/dbox/oled0", "w")
		f.write('-E2-')
		f.close()

	print("lastshutdown=%s		(True = last shutdown was OK)" % config.usage.shutdownOK.value)
	print("NOK shutdown action=%s" % config.usage.shutdownNOK_action.value)
	print("bootup action=%s" % config.usage.boot_action.value)
	
	if not config.usage.shutdownOK.value and not config.usage.shutdownNOK_action.value == 'normal' or not config.usage.boot_action.value == 'normal':
		print("last shutdown = %s" % config.usage.shutdownOK.value)
		import Screens.PowerLost
		Screens.PowerLost.PowerLost(session)

	config.usage.shutdownOK.setValue(False)
	config.usage.shutdownOK.save()
	if not RestoreSettings:
		configfile.save()
	
	# kill showiframe if it is running (sh4 hack...)
	if getMachineBuild() in ('spark', 'spark7162'):
		os.system("killall -9 showiframe")
	
	runReactor()
	print("[mytest.py] normal shutdown")
	
	config.misc.startCounter.save()
	config.usage.shutdownOK.setValue(True)
	config.usage.shutdownOK.save()	

	profile("wakeup")
	#get currentTime
	nowTime = time()
	if not config.misc.SyncTimeUsing.value == "0" or getBoxType().startswith('gb') or getMachineProcModel().startswith('ini'):
		print("dvb time sync disabled... so set RTC now to current linux time!", strftime("%Y/%m/%d %H:%M", localtime(nowTime)))
		setRTCtime(nowTime)
		
	wakeupList = [
		x for x in ((session.nav.RecordTimer.getNextRecordingTime(), 0, session.nav.RecordTimer.isNextRecordAfterEventActionAuto()),
					(session.nav.RecordTimer.getNextZapTime(), 1),
					(plugins.getNextWakeupTime(), 2),
					(session.nav.PowerTimer.getNextPowerManagerTime(), 3, session.nav.PowerTimer.isNextPowerManagerAfterEventActionAuto()))
		if x[0] != -1
	]
	wakeupList.sort()
	recordTimerWakeupAuto = False
	if wakeupList and wakeupList[0][1] != 3:
		startTime = wakeupList[0]
		if (startTime[0] - nowTime) < 270: # no time to switch box back on
			wptime = nowTime + 30  # so switch back on in 30 seconds
		else:
			if getBoxType().startswith("gb"):
				wptime = startTime[0] - 120 # Gigaboxes already starts 2 min. before wakeup time
			else:
				wptime = startTime[0] - 240
		if startTime[1] == 3:
			nextPluginName = " (%s)" % nextPluginName				
		#if not config.misc.SyncTimeUsing.value == "0" or getBoxType().startswith('gb'):
		#	print "dvb time sync disabled... so set RTC now to current linux time!", strftime("%Y/%m/%d %H:%M", localtime(nowTime))
		#	setRTCtime(nowTime)
		print("set wakeup time to", strftime("%Y/%m/%d %H:%M", localtime(wptime)))
		setFPWakeuptime(wptime)
		recordTimerWakeupAuto = startTime[1] == 0 and startTime[2]
		print('recordTimerWakeupAuto',recordTimerWakeupAuto)
	config.misc.isNextRecordTimerAfterEventActionAuto.value = recordTimerWakeupAuto
	config.misc.isNextRecordTimerAfterEventActionAuto.save()


	PowerTimerWakeupAuto = False
	if wakeupList and wakeupList[0][1] == 3:
		startTime = wakeupList[0]
		if (startTime[0] - nowTime) < 60: # no time to switch box back on
			wptime = nowTime + 30  # so switch back on in 30 seconds
		else:
			if getBoxType().startswith("gb"):
				wptime = startTime[0] + 120 # Gigaboxes already starts 2 min. before wakeup time
			else:
				wptime = startTime[0]
		#if not config.misc.SyncTimeUsing.value == "0" or getBoxType().startswith('gb'):
		#	print "dvb time sync disabled... so set RTC now to current linux time!", strftime("%Y/%m/%d %H:%M", localtime(nowTime))
		#	setRTCtime(nowTime)
		print("set wakeup time to", strftime("%Y/%m/%d %H:%M", localtime(wptime+60)))
		setFPWakeuptime(wptime)
		PowerTimerWakeupAuto = startTime[1] == 3 and startTime[2]
		print('PowerTimerWakeupAuto',PowerTimerWakeupAuto)
	config.misc.isNextPowerTimerAfterEventActionAuto.value = PowerTimerWakeupAuto
	config.misc.isNextPowerTimerAfterEventActionAuto.save()

	profile("stopService")
	session.nav.stopService()
	profile("nav shutdown")
	session.nav.shutdown()

	profile("configfile.save")
	configfile.save()
	from Screens import InfoBarGenerics
	InfoBarGenerics.saveResumePoints()

	return 0

profile("Init:skin")
import skin
skin.loadSkinData(enigma.getDesktop(0))

profile("InputDevice")
import Components.InputDevice
Components.InputDevice.InitInputDevices()
import Components.InputHotplug

profile("AVSwitch")
import Components.AVSwitch
Components.AVSwitch.InitAVSwitch()
Components.AVSwitch.InitiVideomodeHotplug()

profile("RecordingConfig")
import Components.RecordingConfig
Components.RecordingConfig.InitRecordingConfig()

profile("UsageConfig")
import Components.UsageConfig
Components.UsageConfig.InitUsageConfig()

profile("TimeZones")
import Components.Timezones
Components.Timezones.InitTimeZones()

profile("Init:DebugLogCheck")
import Screens.LogManager
Screens.LogManager.AutoLogManager()

profile("Init:OnlineCheckState")
import Components.OnlineUpdateCheck
Components.OnlineUpdateCheck.OnlineUpdateCheck()

profile("Init:NTPSync")
import Components.NetworkTime
Components.NetworkTime.AutoNTPSync()

profile("keymapparser")
import keymapparser
keymapparser.readKeymap(config.usage.keymap.value)
keymapparser.readKeymap(config.usage.keytrans.value)

profile("Network")
import Components.Network, Components.Wol
Components.Wol.Init()
Components.Network.InitNetwork()

profile("LCD")
import Components.Lcd
Components.Lcd.InitLcd()
Components.Lcd.IconCheck()
# Disable internal clock vfd for ini5000 until we can adjust it for standby
if boxtype in ('uniboxhd1', 'uniboxhd2', 'uniboxhd3', 'sezam5000hd', 'mbtwin', 'beyonwizt3'):
	try:
		f = open("/proc/stb/fp/enable_clock", "r").readline()[:-1]
		if f != '0':
			f = open("/proc/stb/fp/enable_clock", "w")
			f.write('0')
			f.close()
	except:
		print("Error disable enable_clock for ini5000 boxes")

if boxtype in ('dm7080', 'dm820', 'dm900', 'gb7252'):
	f=open("/proc/stb/hdmi-rx/0/hdmi_rx_monitor", "r")
	check=f.read()
	f.close()
	if check.startswith("on"):
		f=open("/proc/stb/hdmi-rx/0/hdmi_rx_monitor", "w")
		f.write("off")
		f.close()
	f=open("/proc/stb/audio/hdmi_rx_monitor", "r")
	check=f.read()
	f.close()
	if check.startswith("on"):
		f=open("/proc/stb/audio/hdmi_rx_monitor", "w")
		f.write("off")
		f.close()

profile("UserInterface")
import Screens.UserInterfacePositioner
Screens.UserInterfacePositioner.InitOsd()

profile("EpgCacheSched")
import Components.EpgLoadSave
Components.EpgLoadSave.EpgCacheSaveCheck()
Components.EpgLoadSave.EpgCacheLoadCheck()

profile("RFMod")
import Components.RFmod
Components.RFmod.InitRFmod()

profile("Init:CI")
import Screens.Ci
Screens.Ci.InitCiConfig()

profile("RcModel")
import Components.RcModel

#from enigma import dump_malloc_stats
#t = eTimer()
#t.callback.append(dump_malloc_stats)
#t.start(1000)

# first, setup a screen
try:
	runScreenTest()

	plugins.shutdown()

	Components.ParentalControl.parentalControl.save()
except:
	print('EXCEPTION IN PYTHON STARTUP CODE:')
	print('-'*60)
	print_exc(file=stdout)
	enigma.quitMainloop(5)
	print('-'*60)
