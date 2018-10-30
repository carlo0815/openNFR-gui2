#################################################################################
# FULL BACKUP UYILITY FOR ENIGMA2, SUPPORTS THE MODELS OE-A 2.0     			#
#	                         						                            #
#					MAKES A FULLBACK-UP READY FOR FLASHING.						#
#																				#
#################################################################################
from enigma import getEnigmaVersionString, eTimer
from Screens.Screen import Screen
from Screens.Setup import Setup
from Components.Console import Console
from Screens.Console import Console as ScreenConsole
from Components.Button import Button
from Components.Sources.StaticText import StaticText
from Components.SystemInfo import SystemInfo
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.About import about
from Components import Harddisk
from Screens.MessageBox import MessageBox
from os import path, system, mkdir, makedirs, listdir, remove, rename, statvfs, chmod, walk, symlink, unlink
from shutil import rmtree, move, copy
from time import localtime, time, strftime, mktime
import os
import commands
import datetime
import zipfile
from boxbranding import getBoxType, getImageType, getImageDistro, getDriverDate, getImageVersion, getImageBuild, getImageDevBuild, getImageFolder, getImageFileSystem, getBrandOEM, getMachineBrand, getMachineName, getMachineBuild, getMachineMake, getMachineMtdRoot, getMachineRootFile, getMachineMtdKernel, getMachineKernelFile, getMachineMKUBIFS, getMachineUBINIZE
import Components.Task
from Screens.TaskView import JobView
from Screens.Standby import TryQuitMainloop
from Tools.Notifications import AddPopupWithCallback
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigSelection, ConfigText, ConfigNumber, NoSave, ConfigClock, ConfigInteger 
from Components.Harddisk import harddiskmanager, getProcMounts
import shutil
import urllib

VERSION = "Version %s openNFR" % getImageVersion()
RAMCHEKFAILEDID = 'RamCheckFailedNotification'

hddchoises = []
for p in harddiskmanager.getMountedPartitions():
	if path.exists(p.mountpoint):
		d = path.normpath(p.mountpoint)
		if p.mountpoint != '/':
			hddchoises.append((p.mountpoint, d))
config.imagemanager = ConfigSubsection()
defaultprefix = getImageDistro() + '-' + getBoxType()
config.imagemanager.folderprefix = ConfigText(default=defaultprefix, fixed_size=False)
config.imagemanager.backuplocation = ConfigSelection(choices=hddchoises)
config.imagemanager.schedule = ConfigYesNo(default=False)
config.imagemanager.scheduletime = ConfigClock(default=0)  # 1:00
config.imagemanager.nextbackuptime = ConfigClock(default=0)  # 1:00
config.imagemanager.repeattype = ConfigSelection(default="daily", choices=[("daily-", _("Daily-")),("daily", _("Daily")), ("weekly", _("Weekly")), ("monthly", _("30 Days"))])
config.imagemanager.backupmax = ConfigInteger(default=0, limits=(0, 99))
config.imagemanager.backupretry = ConfigNumber(default=30)
config.imagemanager.backupretrycount = NoSave(ConfigNumber(default=0))
config.imagemanager.nextscheduletime = NoSave(ConfigNumber(default=0))
config.imagemanager.restoreimage = NoSave(ConfigText(default=getBoxType(), fixed_size=False))
config.imagemanager.autosettingsbackup = ConfigYesNo(default = True)

#GML - querying is enabled by default - that is what used to happen always
#
config.imagemanager.query = ConfigYesNo(default=True)

#GML -  If we do not yet have a record of an image backup, assume it has
#       never happened.
#
now = int(time())
config.imagemanager.lastbackup = ConfigNumber(default=0)

#GML - max no. of images to keep.  0 == keep them all
#
config.imagemanager.number_to_keep = ConfigNumber(default=0)

autoImageManagerTimer = None
HaveGZkernel = True

if getMachineBuild() in ('hd60','i55plus','osmio4k','sf8008','cc1','dags72604', 'u51','u52','u53','h9','vuzero4k','u5','u5pvr','sf5008','et13000','et1x000',"vuuno4k","vuuno4kse", "vuultimo4k", "vusolo4k", "spark", "spark7162", "hd51", "hd52", "sf4008", "dags7252", "gb7252", "vs1500","h7",'xc7439','8100s'):
	HaveGZkernel = False

def Freespace(dev):
	statdev = statvfs(dev)
	space = (statdev.f_bavail * statdev.f_frsize) / 1024
	print "[FULL BACKUP] Free space on %s = %i kilobytes" %(dev, space)
	return space
	
def ImageManagerautostart(reason, session=None, **kwargs):
	"""called with reason=1 to during /sbin/shutdown.sysvinit, with reason=0 at startup?"""
	global autoImageManagerTimer
	global _session
	now = int(time())
	if reason == 0:
		print "[ImageManager] AutoStart Enabled"
		if session is not None:
			_session = session
			if autoImageManagerTimer is None:
				autoImageManagerTimer = AutoImageManagerTimer(session)
	else:
		if autoImageManagerTimer is not None:
			print "[ImageManager] Stop"
			autoImageManagerTimer.stop()	
	
class TimerImageManager(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Image Manager"))
		global autoImageManagerTimer
		global _session
		now = int(time())
		print "[ImageManager] AutoStart Enabled"
		if session is not None:
			_session = session
			if autoImageManagerTimer is None:
				autoImageManagerTimer = AutoImageManagerTimer(session)
	

		self['lab1'] = Label()
		self["backupstatus"] = Label()
		self["key_green"] = Button(_("Standart Backup"))
		self["key_yellow"] = Button(_("Timer backup"))
		self["key_blue"] = Button(_("Max. backup 0=deactivated"))

		self.BackupRunning = False
		self.onChangedEntry = []
		self.oldlist = None
		self.emlist = []
		self['list'] = MenuList(self.emlist)
		self.populate_List()
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.backupRunning)
		self.activityTimer.start(10)

		self.Console = Console()

		if BackupTime > 0:
		        now = int(time())
			t = localtime(BackupTime)
			backuptext = _("Next Backup: ") + strftime(_("%a %e %b  %-H:%M"), t)
		else:
			backuptext = _("Next Backup: ")
		self["backupstatus"].setText(str(backuptext))
		if not self.selectionChanged in self["list"].onSelectionChanged:
			self["list"].onSelectionChanged.append(self.selectionChanged)
			
	def getJobName(self, job):
		return "%s: %s (%d%%)" % (job.getStatustext(), job.name, int(100 * job.progress / float(job.end)))

	def showJobView(self, job):
		Components.Task.job_manager.in_background = False
		self.session.openWithCallback(self.JobViewCB, JobView, job, cancelable=False, backgroundable=False, afterEventChangeable=False, afterEvent="close")

	def JobViewCB(self, in_background):
		Components.Task.job_manager.in_background = in_background			

	def createSummary(self):
		from Screens.PluginBrowser import PluginBrowserSummary

		return PluginBrowserSummary

	def selectionChanged(self):
		item = self["list"].getCurrent()
		desc = self["backupstatus"].text
		if item:
			name = item
		else:
			name = ""
		for cb in self.onChangedEntry:
			cb(name, desc)

	def backupRunning(self):
		self.populate_List()
		self.BackupRunning = False
		for job in Components.Task.job_manager.getPendingJobs():
			if job.name.startswith(_("Image Manager")):
				self.BackupRunning = True
		if self.BackupRunning:
			self["key_green"].setText(_("View Progress"))
		else:
			self["key_green"].setText(_("Standart Backup"))
		self.activityTimer.startLongTimer(5)

	def refreshUp(self):
		self.refreshList()
		if self['list'].getCurrent():
			self["list"].instance.moveSelection(self["list"].instance.moveUp)

	def refreshDown(self):
		self.refreshList()
		if self['list'].getCurrent():
			self["list"].instance.moveSelection(self["list"].instance.moveDown)

	def refreshList(self):
		images = listdir(self.BackupDirectory)
		self.oldlist = images
		del self.emlist[:]
		for fil in images:
			if fil.endswith('.zip') or path.isdir(path.join(self.BackupDirectory, fil)):
				self.emlist.append(fil)
		self.emlist.sort()
		self.emlist.reverse()
		self["list"].setList(self.emlist)
		self["list"].show()

	def getJobName(self, job):
		return "%s: %s (%d%%)" % (job.getStatustext(), job.name, int(100 * job.progress / float(job.end)))

	def showJobView(self, job):
		Components.Task.job_manager.in_background = False
		self.session.openWithCallback(self.JobViewCB, JobView, job, cancelable=False, backgroundable=True, afterEventChangeable=False, afterEvent="close")

	def JobViewCB(self, in_background):
		Components.Task.job_manager.in_background = in_background

	def populate_List(self):
		imparts = []
		for p in harddiskmanager.getMountedPartitions():
			if path.exists(p.mountpoint):
				d = path.normpath(p.mountpoint)
				if p.mountpoint != '/':
					imparts.append((p.mountpoint, d))
		config.imagemanager.backuplocation.setChoices(imparts)

		if config.imagemanager.backuplocation.value.endswith('/'):
			mount = config.imagemanager.backuplocation.value, config.imagemanager.backuplocation.value[:-1]
		else:
			mount = config.imagemanager.backuplocation.value + '/', config.imagemanager.backuplocation.value
		hdd = '/media/hdd/', '/media/hdd'
		if mount not in config.imagemanager.backuplocation.choices.choices:
			if hdd in config.imagemanager.backuplocation.choices.choices:
				self['myactions'] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions', "MenuActions", "HelpActions"],
											  {
											  "ok": self.GreenPressed,
											  'cancel': self.close,
											  'green': self.GreenPressed,
											  'yellow': self.createSetup,
											  'blue': self.createMaxSetup,
											  "up": self.refreshUp,
											  "down": self.refreshDown,
											  }, -1)

				self.BackupDirectory = '/media/hdd/imagebackups/'
				config.imagemanager.backuplocation.value = '/media/hdd/'
				config.imagemanager.backuplocation.save()
				self['lab1'].setText(_("The chosen location is /media/hdd"))
			else:
				self['myactions'] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions', "MenuActions"],
											  {
											  'cancel': self.close,
											  'yellow': self.createSetup,
											  'blue': self.createMaxSetup,
											  }, -1)

				self['lab1'].setText(_("Device: None available"))
		else:
			self['myactions'] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions', "MenuActions", "HelpActions"],
										  {
										  'cancel': self.close,
										  'green': self.GreenPressed,
										  'yellow': self.createSetup,
										  'blue': self.createMaxSetup,										  
										  "up": self.refreshUp,
										  "down": self.refreshDown,
										  "ok": self.GreenPressed,
										  }, -1)

			self.BackupDirectory = config.imagemanager.backuplocation.value + 'imagebackups/'
			s = statvfs(config.imagemanager.backuplocation.value)
			free = (s.f_bsize * s.f_bavail) / (1024 * 1024)
			self['lab1'].setText(_("Device: ") + config.imagemanager.backuplocation.value + ' ' + _('Free space:') + ' ' + str(free) + _('MB'))

		try:
			if not path.exists(self.BackupDirectory):
				mkdir(self.BackupDirectory, 0755)
			if path.exists(self.BackupDirectory + config.imagemanager.folderprefix.value + '-' + getImageType() + '-swapfile_backup'):
				system('swapoff ' + self.BackupDirectory + config.imagemanager.folderprefix.value + '-' + getImageType() + '-swapfile_backup')
				remove(self.BackupDirectory + config.imagemanager.folderprefix.value + '-' + getImageType() + '-swapfile_backup')
			self.refreshList()
		except:
			self['lab1'].setText(_("Device: ") + config.imagemanager.backuplocation.value + "\n" + _("there is a problem with this device, please reformat and try again."))

	def createSetup(self):
		self.session.openWithCallback(self.setupDone, Setup, 'timerimagemanager', 'Extensions/Infopanel')
		
	def createMaxSetup(self):
		self.session.openWithCallback(self.setupMaxDone, Setup, 'maxbackup', 'Extensions/Infopanel')		

	def setupMaxDone(self, test=None):
		print "set Max Backupt to:", config.imagemanager.backupmax.value
		pass
		
	def setupDone(self, test=None):
		if config.imagemanager.folderprefix.value == '':
			config.imagemanager.folderprefix.value = defaultprefix
			config.imagemanager.folderprefix.save()
		self.populate_List()
		self.doneConfiguring()

	def doneConfiguring(self):
		now = int(time())
		if config.imagemanager.schedule.value:
			if autoImageManagerTimer is not None:
				print "[ImageManager] Backup Schedule Enabled at", strftime("%c", localtime(now))
				autoImageManagerTimer.backupupdate()
		else:
			if autoImageManagerTimer is not None:
				global BackupTime
				BackupTime = 0
				print "[ImageManager] Backup Schedule Disabled at", strftime("%c", localtime(now))
				autoImageManagerTimer.backupstop()
		if BackupTime > 0:
			t = localtime(BackupTime)
			backuptext = _("Next Backup: ") + strftime(_("%a %e %b  %-H:%M"), t)
		else:
			backuptext = _("Next Backup: ")
		self["backupstatus"].setText(str(backuptext))


	def GreenPressed(self):
		self.session.open(ImageBackup)
                #backup = None
		#self.BackupRunning = False
		#for job in Components.Task.job_manager.getPendingJobs():
	#		if job.name.startswith(_("Image Manager")):
	#			backup = job
	#			self.BackupRunning = True
	#	if self.BackupRunning and backup:
	#		self.showJobView(backup)
	#	else:
	#		self.keyBackup()

	def keyBackup(self):
		message = _("Are you ready to create a backup image ?")
		ybox = self.session.openWithCallback(self.doBackup, MessageBox, message, MessageBox.TYPE_YESNO)
		ybox.setTitle(_("Backup Confirmation"))

	def doBackup(self, answer):
		if answer is True:
			self.ImageBackup = ImageBackup(self.session)
			Components.Task.job_manager.AddJob(self.ImageBackup.createBackupJob())
			self.BackupRunning = True
			self["key_green"].setText(_("View Progress"))
			self["key_green"].show()
			for job in Components.Task.job_manager.getPendingJobs():
				if job.name.startswith(_("Image Manager")):
					break
			self.showJobView(job)


class AutoImageManagerTimer:
	def __init__(self, session):
		self.session = session
		self.backuptimer = eTimer()
		self.backuptimer.callback.append(self.BackuponTimer)
		self.backupactivityTimer = eTimer()
		self.backupactivityTimer.timeout.get().append(self.backupupdatedelay)
		now = int(time())
		global BackupTime
		if config.imagemanager.schedule.value:
			print "[ImageManager] Backup Schedule Enabled at ", strftime("%c", localtime(now))
			if now > 1262304000:
				self.backupupdate()
			else:
				print "[ImageManager] Backup Time not yet set."
				BackupTime = 0
				self.backupactivityTimer.start(36000)
		else:
                        BackupTime = 0
			print "[ImageManager] Backup Schedule Disabled at", strftime("(now=%c)", localtime(now))
			self.backupactivityTimer.stop()

	def backupupdatedelay(self):
		self.backupactivityTimer.stop()
		self.backupupdate()

	def getBackupTime(self):
		backupclock = config.imagemanager.scheduletime.value
#		nowt = time()
#		now = localtime(nowt)
#		return int(mktime((now.tm_year, now.tm_mon, now.tm_mday, backupclock[0], backupclock[1], 0, now.tm_wday, now.tm_yday, now.tm_isdst)))
#GML
# Work out the time of the *NEXT* backup - which is the configured clock
# time on the nth relevant day after the last recorded backup day.
# The last backup time will have been set as 12:00 on the day it
# happened. All we use is the actual day from that value.
		if not config.imagemanager.lastbackup.value:
	                now = int(time())
	                config.imagemanager.lastbackup.value = now
	                config.imagemanager.lastbackup.save()
                lastbkup_t = int(config.imagemanager.lastbackup.value)
	        print "lastbkup_t:", lastbkup_t
		if config.imagemanager.repeattype.value == "daily":
			nextbkup_t = lastbkup_t + 24*3600
		elif config.imagemanager.repeattype.value == "weekly":
			nextbkup_t = lastbkup_t + 7*24*3600
		elif config.imagemanager.repeattype.value == "monthly":
			nextbkup_t = lastbkup_t + 30*24*3600
		elif config.imagemanager.repeattype.value == "daily-":
			nextbkup_t = lastbkup_t + 600                        		
		nextbkup = localtime(nextbkup_t)
		print "nextbackup:", int(mktime((nextbkup.tm_year, nextbkup.tm_mon, nextbkup.tm_mday, backupclock[0], backupclock[1], 0, nextbkup.tm_wday, nextbkup.tm_yday, nextbkup.tm_isdst)))
		return int(mktime((nextbkup.tm_year, nextbkup.tm_mon, nextbkup.tm_mday, backupclock[0], backupclock[1], 0, nextbkup.tm_wday, nextbkup.tm_yday, nextbkup.tm_isdst)))

	def backupupdate(self, atLeast=0):
		self.backuptimer.stop()
		global BackupTime
		BackupTime = self.getBackupTime()
		now = int(time())
		if BackupTime > 0:
			if BackupTime < now + atLeast:
#				if config.imagemanager.repeattype.value == "daily":
#					BackupTime += 24 * 3600
#					while (int(BackupTime) - 30) < now:
#						BackupTime += 24 * 3600
#				elif config.imagemanager.repeattype.value == "weekly":
#					BackupTime += 7 * 24 * 3600
#					while (int(BackupTime) - 30) < now:
#						BackupTime += 7 * 24 * 3600
#				elif config.imagemanager.repeattype.value == "monthly":
#					BackupTime += 30 * 24 * 3600
#					while (int(BackupTime) - 30) < now:
#						BackupTime += 30 * 24 * 3600
#			next = BackupTime - now
#			self.backuptimer.startLongTimer(next)
# Backup missed - run it 60s from now
				self.backuptimer.startLongTimer(60)
				print "[ImageManager] Backup Time overdue - running in 60s"
			else:
# Backup in future - set the timer...
				delay = BackupTime - now
				self.backuptimer.startLongTimer(delay)
		else:
			BackupTime = -1

		print "[ImageManager] Backup Time set to", strftime("%c", localtime(BackupTime)), strftime("(now=%c)", localtime(now))
		return BackupTime

	def backupstop(self):
		self.backuptimer.stop()

	def BackuponTimer(self):
		self.backuptimer.stop()
		now = int(time())
		wake = self.getBackupTime()
		# If we're close enough, we're okay...
		atLeast = 0
		if wake - now < 60:
			print "[ImageManager] Backup onTimer occured at", strftime("%c", localtime(now))
			from Screens.Standby import inStandby

#GML			if not inStandby:
#    - add check for querying
			if not inStandby and config.imagemanager.query.value:
				message = _("Your %s %s is about to run a full image backup, this can take about 6 minutes to complete,\ndo you want to allow this?") % (getMachineBrand(), getMachineName())
				ybox = self.session.openWithCallback(self.doBackup, MessageBox, message, MessageBox.TYPE_YESNO, timeout=30)
				ybox.setTitle('Scheduled Backup.')
			else:
#GML				print "[ImageManager] in Standby, so just running backup", strftime("%c", localtime(now))
				print "[ImageManager] in Standby or no querying, so just running backup", strftime("%c", localtime(now))
				self.doBackup(True)
		else:
			print '[ImageManager] Where are not close enough', strftime("%c", localtime(now))
			self.backupupdate(60)

	def doBackup(self, answer):
		now = int(time())
		if answer is False:
			if config.imagemanager.backupretrycount.value < 2:
				print '[ImageManager] Number of retries', config.imagemanager.backupretrycount.value
				print "[ImageManager] Backup delayed."
				repeat = config.imagemanager.backupretrycount.value
				repeat += 1
				config.imagemanager.backupretrycount.setValue(repeat)
				BackupTime = now + (int(config.imagemanager.backupretry.value) * 60)
				print "[ImageManager] Backup Time now set to", strftime("%c", localtime(BackupTime)), strftime("(now=%c)", localtime(now))
				self.backuptimer.startLongTimer(int(config.imagemanager.backupretry.value) * 60)
			else:
				atLeast = 60
				print "[ImageManager] Enough Retries, delaying till next schedule.", strftime("%c", localtime(now))
				self.session.open(MessageBox, _("Enough Retries, delaying till next schedule."), MessageBox.TYPE_INFO, timeout=10)
				config.imagemanager.backupretrycount.setValue(0)
				self.backupupdate(atLeast)
		else:
			print "[ImageManager] Running Backup", strftime("%c", localtime(now))
			self.ImageBackup = ImageBackup(self.session)
			Components.Task.job_manager.AddJob(self.ImageBackup.createBackupJob())
			
#GML - Note that fact that the job has been *scheduled*.
#      We do *not* just note successful completion, as that would
#      result in a loop on issues such as disk-full.
#      Also all that we actually want to know is the day, not the time, so
#      we actually remember midday, which avoids problems around DLST changes
#      for backups scheduled within an hour of midnight.
#
			sched = localtime(time())
			sched_t = int(mktime((sched.tm_year, sched.tm_mon, sched.tm_mday, 12, 0, 0, sched.tm_wday, sched.tm_yday, sched.tm_isdst)))
			config.imagemanager.lastbackup.value = sched_t
			config.imagemanager.lastbackup.save()

class ImageBackup(Screen):
	skin = """
	<screen position="center,center" size="560,400" title="Image Backup">
		<ePixmap position="0,360"   zPosition="1" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap position="140,360" zPosition="1" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap position="280,360" zPosition="1" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
		<ePixmap position="420,360" zPosition="1" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
		<widget source="key_red" render="Label" position="0,360" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget source="key_green" render="Label" position="140,360" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget source="key_yellow" render="Label" position="280,360" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget source="key_blue" render="Label" position="420,360" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="info-hdd" position="10,30" zPosition="1" size="450,100" font="Regular;20" halign="left" valign="top" transparent="1" />
		<widget name="info-usb" position="10,150" zPosition="1" size="450,200" font="Regular;20" halign="left" valign="top" transparent="1" />
	</screen>"""
		
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		global closed
                closed = False
                self.session = session
		self.selection = 0
		self.MODEL = getBoxType()
		self.OEM = getBrandOEM()
		self.MACHINEBUILD = getMachineBuild()
		self.MACHINENAME = getMachineName()
		self.MACHINEBRAND = getMachineBrand()
		self.IMAGEFOLDER = getImageFolder()
		self.UBINIZE_ARGS = getMachineUBINIZE()
		self.MKUBIFS_ARGS = getMachineMKUBIFS()
		self.MTDKERNEL = getMachineMtdKernel()
		self.MTDROOTFS = getMachineMtdRoot()
                self.ROOTFSBIN = getMachineRootFile()
		self.KERNELBIN = getMachineKernelFile()
		self.ROOTFSTYPE = getImageFileSystem()
		if self.MACHINEBUILD in ("hd51","vs1500","h7","8100s"):
			self.MTDBOOT = "mmcblk0p1"
			self.EMMCIMG = "disk.img"
		elif self.MACHINEBUILD in ("xc7439"):
			self.MTDBOOT = "mmcblk1p1"
			self.EMMCIMG = "emmc.img"
		elif self.MACHINEBUILD in ("cc1","sf8008","ustym4kpr"):
			self.MTDBOOT = "none"
			self.EMMCIMG = "usb_update.bin"
		else:
			self.MTDBOOT = "none"
                        self.EMMCIMG = "none"
		self.list = self.list_files("/boot")
                print "[FULL BACKUP] BOX MACHINEBUILD = >%s<" %self.MACHINEBUILD
		print "[FULL BACKUP] BOX MACHINENAME = >%s<" %self.MACHINENAME
		print "[FULL BACKUP] BOX MACHINEBRAND = >%s<" %self.MACHINEBRAND
		print "[FULL BACKUP] BOX MODEL = >%s<" %self.MODEL
		print "[FULL BACKUP] OEM MODEL = >%s<" %self.OEM
		print "[FULL BACKUP] IMAGEFOLDER = >%s<" %self.IMAGEFOLDER
		print "[FULL BACKUP] UBINIZE = >%s<" %self.UBINIZE_ARGS
		print "[FULL BACKUP] MKUBIFS = >%s<" %self.MKUBIFS_ARGS
		print "[FULL BACKUP] MTDKERNEL = >%s<" %self.MTDKERNEL
		print "[FULL BACKUP] MTDROOTFS = >%s<" %self.MTDROOTFS
                print "[FULL BACKUP] ROOTFSTYPE = >%s<" %self.ROOTFSTYPE
		
		self["key_green"] = Button("USB")
		self["key_red"] = Button("HDD")
		self["key_blue"] = Button(_("Exit"))
		if SystemInfo["HaveMultiBoot"]:
			self["key_yellow"] = Button(_("STARTUP"))
			self["info-multi"] = Label(_("You can select with yellow the OnlineFlash Image\n or select Recovery to create a USB Disk Image for clean Install."))
		else:
			self["key_yellow"] = Button("")
			self["info-multi"] = Label(" ")
		self["info-usb"] = Label(_("USB = Do you want to make a back-up on USB?\nThis will take between 4 and 15 minutes depending on the used filesystem and is fully automatic.\nMake sure you first insert an USB flash drive before you select USB."))
		self["info-hdd"] = Label(_("HDD = Do you want to make an USB-back-up image on HDD? \nThis only takes 2 or 10 minutes and is fully automatic."))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], 
		{
			"blue": self.quit,
			"yellow": self.yellow,
			"green": self.green,
			"red": self.red,
			"cancel": self.quit,
		}, -2)
		
	def createBackupJob(self):
                if SystemInfo["HaveMultiBoot"]:
			with open("/boot/STARTUP", 'r') as myfile:
				data=myfile.read().replace('\n', '')
			myfile.close()
			cmdline = data.split("=",3)[3].split(" ",1)[0]
			cmdline = cmdline.lstrip("/dev/")
			self.MTDROOTFS = cmdline
			self.MTDKERNEL = cmdline[:-1] + str(int(cmdline[-1:]) -1)
		print "BackupTime:", BackupTime
		job = Components.Task.Job(_("Image Manager"))

		task = Components.Task.PythonTask(job, _("Backing Up..."))
		task.work = self.doFullBackup1
		task.weighting = 5

		return job
		
	def doFullBackup1(self):
	        closed = True
	        global closed
        	self.doFullBackup("/hdd")
		
                
	def check_hdd(self):
		if not path.exists("/media/hdd"):
			self.session.open(MessageBox, _("No /hdd found !!\nPlease make sure you have a HDD mounted.\n"), type = MessageBox.TYPE_ERROR)
			return False
		if Freespace('/media/hdd') < 300000:
			self.session.open(MessageBox, _("Not enough free space on /hdd !!\nYou need at least 300Mb free space.\n"), type = MessageBox.TYPE_ERROR)
			return False
		return True
		

	def check_usb(self, dev):
		if Freespace(dev) < 300000:
			self.session.open(MessageBox, _("Not enough free space on %s !!\nYou need at least 300Mb free space.\n" % dev), type = MessageBox.TYPE_ERROR)
			return False
		return True
		
	def quit(self):
		self.close()
		
	def red(self):
		if self.check_hdd():
			self.doFullBackup("/hdd")

	def green(self):
		USB_DEVICE = self.SearchUSBcanidate()
		if USB_DEVICE == 'XX':
			text = _("No USB-Device found for fullbackup !!\n\n\n")
			text += _("To back-up directly to the USB-stick, the USB-stick MUST\n")
			text += _("contain a file with the name: \n\n")
			text += _("backupstick or backupstick.txt")
			self.session.open(MessageBox, text, type = MessageBox.TYPE_ERROR)
		else:
			if self.check_usb(USB_DEVICE):
				self.doFullBackup(USB_DEVICE)

	def yellow(self):
		if SystemInfo["HaveMultiBoot"]:
			self.selection = self.selection + 1
			if self.selection == len(self.list):
				self.selection = 0
			self["key_yellow"].setText(_(self.list[self.selection]))
			if self.MACHINEBUILD in ("hd51","vs1500","h7"):
				if self.list[self.selection] == "Recovery":
					cmdline = self.read_startup("/boot/STARTUP").split("=",3)[3].split(" ",1)[0]
				else:
					cmdline = self.read_startup("/boot/" + self.list[self.selection]).split("=",3)[3].split(" ",1)[0]
			elif self.MACHINEBUILD in ("8100s"):
				if self.list[self.selection] == "Recovery":
					cmdline = self.read_startup("/boot/STARTUP").split("=",4)[4].split(" ",1)[0]
				else:
					cmdline = self.read_startup("/boot/" + self.list[self.selection]).split("=",4)[4].split(" ",1)[0]
			elif self.MACHINEBUILD in ("cc1","sf8008","ustym4kpro"):
			        if self.list[self.selection] == "Recovery":
				        cmdline = self.read_startup("/boot/STARTUP").split("=",1)[1].split(" ",1)[0]
			        else:
                                        cmdline = self.read_startup("/boot/" + self.list[self.selection]).split("=",1)[1].split(" ",1)[0]
                        else:
				if self.list[self.selection] == "Recovery":
					cmdline = self.read_startup("/boot/cmdline.txt").split("=",1)[1].split(" ",1)[0]
				else:
					cmdline = self.read_startup("/boot/" + self.list[self.selection]).split("=",1)[1].split(" ",1)[0]
			cmdline = cmdline.lstrip("/dev/")
			self.MTDROOTFS = cmdline
			self.MTDKERNEL = cmdline[:-1] + str(int(cmdline[-1:]) -1)
			print "[FULL BACKUP] Multiboot rootfs ", self.MTDROOTFS
                        print "[FULL BACKUP] Multiboot kernel ", self.MTDKERNEL

	def read_startup(self, FILE):
		self.file = FILE
		with open(self.file, 'r') as myfile:
			data=myfile.read().replace('\n', '')
		myfile.close()
		return data

	def list_files(self, PATH):
		files = []
		if SystemInfo["HaveMultiBoot"]:
			self.path = PATH
			for name in listdir(self.path):
				if path.isfile(path.join(self.path, name)):
					if self.MACHINEBUILD in ("hd51","vs1500","h7"):
						cmdline = self.read_startup("/boot/" + name).split("=",3)[3].split(" ",1)[0]
					elif self.MACHINEBUILD in ("8100s"):
						cmdline = self.read_startup("/boot/" + name).split("=",4)[4].split(" ",1)[0]
					else:
						cmdline = self.read_startup("/boot/" + name).split("=",1)[1].split(" ",1)[0]
					if cmdline in Harddisk.getextdevices("ext4"):
						files.append(name)
			if getMachineBuild() not in ("gb7252"):
				files.append("Recovery")
                return files

	def SearchUSBcanidate(self):
		for paths, subdirs, files in walk("/media"):
			for dir in subdirs:
				if not dir == 'hdd' and not dir == 'net':
					for file in listdir("/media/" + dir):
						if file.find("backupstick") > -1:
							print "USB-DEVICE found on: /media/%s" % dir
							return "/media/" + dir			
			break
		return "XX"

	def doFullBackup(self, DIRECTORY):
                self.DIRECTORY = DIRECTORY
                self.BackupDirectory5 = "%s/fullbackup_%s/"  % (self.DIRECTORY, self.MODEL)
                if not path.exists("%s/fullbackup_%s/"  % (self.DIRECTORY, self.MODEL)):
                        mkdir("%s/fullbackup_%s/"  % (self.DIRECTORY, self.MODEL))
                images = listdir(self.BackupDirectory5)
                lenimages = 0
                for fil in images:
	        	if path.isdir(path.join(self.BackupDirectory5, fil)):
		                lenimages = lenimages + 1
                	else:
                                lenimages = lenimages
                if lenimages < config.imagemanager.backupmax.value or config.imagemanager.backupmax.value == 0:
                	print "imageanzahl noch nicht erreicht"
                else:
                	datum=[]
                	for i in images:
                		xi = self.BackupDirectory5 + i
				datum+=[os.path.getmtime(xi)]
                		datum.sort()
			for m in images:
				xm = self.BackupDirectory5 + m
				deleteimage = config.imagemanager.backupmax.value - 1 
				if os.path.getmtime(xm) in datum[:-deleteimage]:
					shutil.rmtree(xm)
				else:
					print "hold image"	
                self.TITLE = _("Full back-up on %s") % (self.DIRECTORY)
		self.START = time()
		self.DATE = strftime("%Y%m%d_%H%M", localtime(self.START))
		self.IMAGEVERSION = self.imageInfo() #strftime("%Y%m%d", localtime(self.START))
		if "ubi" in self.ROOTFSTYPE.split():
			self.MKFS = "/usr/sbin/mkfs.ubifs"
		elif "tar.bz2" in self.ROOTFSTYPE.split() or SystemInfo["HaveMultiBoot"] or self.MACHINEBUILD in ('u51','u52','u53','u5','u5pvr','h9',"cc1","sf8008"):
				self.MKFS = "/bin/tar"
				self.BZIP2 = "/usr/bin/bzip2"
		else:
			self.MKFS = "/usr/sbin/mkfs.jffs2"
		self.UBINIZE = "/usr/sbin/ubinize"
		self.NANDDUMP = "/usr/sbin/nanddump"
		self.WORKDIR= "%s/bi" %self.DIRECTORY
		self.TARGET="XX"

		## TESTING IF ALL THE TOOLS FOR THE BUILDING PROCESS ARE PRESENT
		if not path.exists(self.MKFS):
			text = "%s not found !!" %self.MKFS
			self.session.open(MessageBox, _(text), type = MessageBox.TYPE_ERROR)
			return
		if not path.exists(self.NANDDUMP):
			text = "%s not found !!" %self.NANDDUMP
			self.session.open(MessageBox, _(text), type = MessageBox.TYPE_ERROR)
			return

		self.SHOWNAME = "%s %s" %(self.MACHINEBRAND, self.MODEL)
		self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
		self.MAINDEST = "%s/%s" %(self.DIRECTORY,self.IMAGEFOLDER)
		self.IMAGEFOLDER1 = self.IMAGEFOLDER.split('/')[0]
		self.MAINDEST1 = "%s/%s" % (self.DIRECTORY, self.IMAGEFOLDER1)
		self.EXTRA = "%s/fullbackup_%s/%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE, self.IMAGEFOLDER)
		self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		self.EXTRAOLD = "%s/fullbackup_%s/%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE, self.MODEL)


		self.message = "echo -e '\n"
		self.message += (_("Back-up Tool for a %s\n" %self.SHOWNAME)).upper()
		self.message += VERSION + '\n'
		self.message += "_________________________________________________\n\n"
		self.message += _("Please be patient, a backup will now be made,\n")
		if self.ROOTFSTYPE == "ubi":
			self.message += _("because of the used filesystem the back-up\n")
			self.message += _("will take about 3-12 minutes for this system\n")
		elif SystemInfo["HaveMultiBoot"] and self.list[self.selection] == "Recovery":
			self.message += _("because of the used filesystem the back-up\n")
			self.message += _("will take about 30 minutes for this system\n")
		elif "tar.bz2" in self.ROOTFSTYPE.split() or SystemInfo["HaveMultiBoot"] or self.MACHINEBUILD in ('u51','u52','u53','u5','u5pvr','h9',"cc1","sf8008"):
				self.message += _("because of the used filesystem the back-up\n")
				self.message += _("will take about 1-4 minutes for this system\n")
		else:
			self.message += _("this will take between 2 and 9 minutes\n")
		self.message += "\n_________________________________________________\n\n"
		self.message += "'"

		## PREPARING THE BUILDING ENVIRONMENT
		system("rm -rf %s" %self.WORKDIR)
		if not path.exists(self.WORKDIR):
			makedirs(self.WORKDIR)
		if not path.exists("/tmp/bi/root"):
			makedirs("/tmp/bi/root")
		system("sync")
		if SystemInfo["HaveMultiBoot"]:
			system("mount /dev/%s /tmp/bi/root" %self.MTDROOTFS)
		else:
			system("mount --bind / /tmp/bi/root")

		if "jffs2" in self.ROOTFSTYPE.split():
			cmd1 = "%s --root=/tmp/bi/root --faketime --output=%s/root.jffs2 %s" % (self.MKFS, self.WORKDIR, self.MKUBIFS_ARGS)
			cmd2 = None
			cmd3 = None
		elif "tar.bz2" in self.ROOTFSTYPE.split() or SystemInfo["HaveMultiBoot"] or self.MACHINEBUILD in ("u51","u52","u53","u5","u5pvr","cc1","sf8008","ustym4kpro"):
			cmd1 = "%s -cf %s/rootfs.tar -C /tmp/bi/root --exclude ./var/nmbd --exclude ./var/lib/samba/private/msg.sock ." % (self.MKFS, self.WORKDIR)
			cmd2 = "%s %s/rootfs.tar" % (self.BZIP2, self.WORKDIR)
                        cmd3 = None
		else:
			f = open("%s/ubinize.cfg" %self.WORKDIR, "w")
			f.write("[ubifs]\n")
			f.write("mode=ubi\n")
			f.write("image=%s/root.ubi\n" %self.WORKDIR)
			f.write("vol_id=0\n")
			f.write("vol_type=dynamic\n")
			f.write("vol_name=rootfs\n")
			f.write("vol_flags=autoresize\n")
			f.close()
			ff = open("%s/root.ubi" %self.WORKDIR, "w")
			ff.close()
			cmd1 = "%s -r /tmp/bi/root -o %s/root.ubi %s" % (self.MKFS, self.WORKDIR, self.MKUBIFS_ARGS)
			cmd2 = "%s -o %s/root.ubifs %s %s/ubinize.cfg" % (self.UBINIZE, self.WORKDIR, self.UBINIZE_ARGS, self.WORKDIR)
			cmd3 = "mv %s/root.ubifs %s/root.%s" %(self.WORKDIR, self.WORKDIR, self.ROOTFSTYPE)

		cmdlist = []
		cmdlist.append(self.message)
		cmdlist.append('echo "Create: %s\n"' %self.ROOTFSBIN)
		cmdlist.append(cmd1)
		if cmd2:
			cmdlist.append(cmd2)
		if cmd3:
			cmdlist.append(cmd3)
		cmdlist.append("chmod 644 %s/%s" %(self.WORKDIR, self.ROOTFSBIN))
		
		if self.MODEL in ("gbquad4k","gbue4k"):
			cmdlist.append('echo " "')
			cmdlist.append('echo "Create: boot dump"')
			cmdlist.append('echo " "')
			cmdlist.append("dd if=/dev/mmcblk0p1 of=%s/boot.bin" % self.WORKDIR)
			cmdlist.append('echo " "')
			cmdlist.append('echo "Create: rescue dump"')
			cmdlist.append('echo " "')
			cmdlist.append("dd if=/dev/mmcblk0p3 of=%s/rescue.bin" % self.WORKDIR)

		if self.MACHINEBUILD  in ("h9","i55plus"):
			cmdlist.append('echo " "')
			cmdlist.append('echo "Create: fastboot dump"')
			cmdlist.append("dd if=/dev/mtd0 of=%s/fastboot.bin" % self.WORKDIR)
			cmdlist.append('echo "Create: bootargs dump"')
			cmdlist.append("dd if=/dev/mtd1 of=%s/bootargs.bin" % self.WORKDIR)
			cmdlist.append('echo "Create: baseparam dump"')
			cmdlist.append("dd if=/dev/mtd2 of=%s/baseparam.bin" % self.WORKDIR)
			cmdlist.append('echo "Create: pq_param dump"')
			cmdlist.append("dd if=/dev/mtd3 of=%s/pq_param.bin" % self.WORKDIR)
			cmdlist.append('echo "Create: logo dump"')
			cmdlist.append("dd if=/dev/mtd4 of=%s/logo.bin" % self.WORKDIR)

		if self.MACHINEBUILD  in ("cc1","sf8008","ustym4kpro"):
			cmdlist.append('echo " "')
			cmdlist.append('echo "Create: fastboot dump"')
			cmdlist.append("dd if=/dev/mmcblk0p1 of=%s/fastboot.bin" % self.WORKDIR)
			cmdlist.append('echo "Create: bootargs dump"')
			cmdlist.append("dd if=/dev/mmcblk0p2 of=%s/bootargs.bin" % self.WORKDIR)
			cmdlist.append('echo "Create: boot dump"')
			cmdlist.append("dd if=/dev/mmcblk0p3 of=%s/boot.img" % self.WORKDIR)
			cmdlist.append('echo "Create: baseparam.dump"')
			cmdlist.append("dd if=/dev/mmcblk0p4 of=%s/baseparam.img" % self.WORKDIR)
			cmdlist.append('echo "Create: pq_param dump"')
			cmdlist.append("dd if=/dev/mmcblk0p5 of=%s/pq_param.bin" % self.WORKDIR)
			cmdlist.append('echo "Create: logo dump"')
			cmdlist.append("dd if=/dev/mmcblk0p6 of=%s/logo.img" % self.WORKDIR)
			cmdlist.append('echo "Create: deviceinfo dump"')
			cmdlist.append("dd if=/dev/mmcblk0p7 of=%s/deviceinfo.bin" % self.WORKDIR)
			cmdlist.append('echo "Create: apploader dump"')
			cmdlist.append("dd if=/dev/mmcblk0p8 of=%s/apploader.bin" % self.WORKDIR)
			cmdlist.append('echo "Create: rootfs dump"')
			cmdlist.append("dd if=/dev/zero of=%s/rootfs.ext4 seek=524288 count=0 bs=1024" % (self.WORKDIR))
			cmdlist.append("mkfs.ext4 -F -i 4096 %s/rootfs.ext4 -d /tmp/bi/root" % (self.WORKDIR))
		
		cmdlist.append('echo " "')
		cmdlist.append('echo "Create: kerneldump"')
		cmdlist.append('echo " "')
		if SystemInfo["HaveMultiBoot"]:
			cmdlist.append("dd if=/dev/%s of=%s/kernel.bin" % (self.MTDKERNEL ,self.WORKDIR))
		elif self.MTDKERNEL == "mmcblk0p1" or self.MTDKERNEL == "mmcblk0p3" or self.MTDKERNEL == "mmcblk0p10" or self.MTDKERNEL == "mmcblk0p9":
			cmdlist.append("dd if=/dev/%s of=%s/%s" % (self.MTDKERNEL ,self.WORKDIR, self.KERNELBIN))
		else:
			cmdlist.append("nanddump -a -f %s/vmlinux.gz /dev/%s" % (self.WORKDIR, self.MTDKERNEL))
		cmdlist.append('echo " "')

		if HaveGZkernel:
			cmdlist.append('echo "Check: kerneldump"')
		cmdlist.append("sync")

		if ( SystemInfo["HaveMultiBootHD"] or SystemInfo["HaveMultiBootCY"]) and self.list[self.selection] == "Recovery":
			GPT_OFFSET=0
			GPT_SIZE=1024
			BOOT_PARTITION_OFFSET = int(GPT_OFFSET) + int(GPT_SIZE)
			BOOT_PARTITION_SIZE=3072
			KERNEL_PARTITION_OFFSET = int(BOOT_PARTITION_OFFSET) + int(BOOT_PARTITION_SIZE)
			KERNEL_PARTITION_SIZE=8192
			ROOTFS_PARTITION_OFFSET = int(KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			ROOTFS_PARTITION_SIZE=1048576
  		        SECOND_KERNEL_PARTITION_OFFSET = int(ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
			SECOND_ROOTFS_PARTITION_OFFSET = int(SECOND_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			THRID_KERNEL_PARTITION_OFFSET = int(SECOND_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
			THRID_ROOTFS_PARTITION_OFFSET = int(THRID_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			FOURTH_KERNEL_PARTITION_OFFSET = int(THRID_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
			FOURTH_ROOTFS_PARTITION_OFFSET = int(FOURTH_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			EMMC_IMAGE = "%s/disk.img"%self.WORKDIR
			EMMC_IMAGE_SIZE=3817472
			IMAGE_ROOTFS_SIZE=196608
			cmdlist.append('echo " "')
			cmdlist.append('echo "Create: Recovery Fullbackup disk.img"')
			cmdlist.append('echo " "')
			cmdlist.append('dd if=/dev/zero of=%s bs=1024 count=0 seek=%s' % (EMMC_IMAGE, EMMC_IMAGE_SIZE))
			cmdlist.append('parted -s %s mklabel gpt' %EMMC_IMAGE)
			PARTED_END_BOOT = int(BOOT_PARTITION_OFFSET) + int(BOOT_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart boot fat16 %s %s' % (EMMC_IMAGE, BOOT_PARTITION_OFFSET, PARTED_END_BOOT ))
			PARTED_END_KERNEL1 = int(KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart kernel1 %s %s' % (EMMC_IMAGE, KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL1 ))
			PARTED_END_ROOTFS1 = int(ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart rootfs1 ext2 %s %s' % (EMMC_IMAGE, ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS1 ))
			PARTED_END_KERNEL2 = int(SECOND_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart kernel2 %s %s' % (EMMC_IMAGE, SECOND_KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL2 ))
			PARTED_END_ROOTFS2 = int(SECOND_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart rootfs2 ext2 %s %s' % (EMMC_IMAGE, SECOND_ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS2 ))
			PARTED_END_KERNEL3 = int(THRID_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart kernel3 %s %s' % (EMMC_IMAGE, THRID_KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL3 ))
			PARTED_END_ROOTFS3 = int(THRID_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart rootfs3 ext2 %s %s' % (EMMC_IMAGE, THRID_ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS3 ))
			PARTED_END_KERNEL4 = int(FOURTH_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart kernel4 %s %s' % (EMMC_IMAGE, FOURTH_KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL4 ))
			PARTED_END_ROOTFS4 = int(EMMC_IMAGE_SIZE) - 1024
			cmdlist.append('parted -s %s unit KiB mkpart rootfs4 ext2 %s %s' % (EMMC_IMAGE, FOURTH_ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS4 ))
			cmdlist.append('dd if=/dev/zero of=%s/boot.img bs=1024 count=%s' % (self.WORKDIR, BOOT_PARTITION_SIZE ))
			cmdlist.append('mkfs.msdos -S 512 %s/boot.img' %self.WORKDIR)
			cmdlist.append("echo \"boot emmcflash0.kernel1 \'brcm_cma=440M@328M brcm_cma=192M@768M root=/dev/mmcblk0p3 rw rootwait %s_4.boxmode=1\'\" > %s/STARTUP" % (getMachineBuild(), self.WORKDIR))
			cmdlist.append("echo \"boot emmcflash0.kernel1 \'brcm_cma=440M@328M brcm_cma=192M@768M root=/dev/mmcblk0p3 rw rootwait %s_4.boxmode=1\'\" > %s/STARTUP_1" % (getMachineBuild(), self.WORKDIR))
			cmdlist.append("echo \"boot emmcflash0.kernel2 \'brcm_cma=440M@328M brcm_cma=192M@768M root=/dev/mmcblk0p5 rw rootwait %s_4.boxmode=1\'\" > %s/STARTUP_2" % (getMachineBuild(), self.WORKDIR))
			cmdlist.append("echo \"boot emmcflash0.kernel3 \'brcm_cma=440M@328M brcm_cma=192M@768M root=/dev/mmcblk0p7 rw rootwait %s_4.boxmode=1\'\" > %s/STARTUP_3" % (getMachineBuild(), self.WORKDIR))
			cmdlist.append("echo \"boot emmcflash0.kernel4 \'brcm_cma=440M@328M brcm_cma=192M@768M root=/dev/mmcblk0p9 rw rootwait %s_4.boxmode=1\'\" > %s/STARTUP_4" % (getMachineBuild(), self.WORKDIR))
			cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP ::' % (self.WORKDIR, self.WORKDIR))
			cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP_1 ::' % (self.WORKDIR, self.WORKDIR))
			cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP_2 ::' % (self.WORKDIR, self.WORKDIR))
			cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP_3 ::' % (self.WORKDIR, self.WORKDIR))
			cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP_4 ::' % (self.WORKDIR, self.WORKDIR))
			cmdlist.append('dd conv=notrunc if=%s/boot.img of=%s bs=1024 seek=%s' % (self.WORKDIR, EMMC_IMAGE, BOOT_PARTITION_OFFSET ))
			cmdlist.append('dd conv=notrunc if=/dev/%s of=%s bs=1024 seek=%s' % (self.MTDKERNEL, EMMC_IMAGE, KERNEL_PARTITION_OFFSET ))
			cmdlist.append('dd if=/dev/%s of=%s bs=1024 seek=%s' % (self.MTDROOTFS, EMMC_IMAGE, ROOTFS_PARTITION_OFFSET ))
		
		elif SystemInfo["HaveMultiBootDS"] and self.list[self.selection] == "Recovery":
			cmdlist.append('echo " "')
			cmdlist.append('echo "Create: Recovery Fullbackup %s"'% (self.EMMCIMG))
			cmdlist.append('echo " "')
			f = open("%s/emmc_partitions.xml" %self.WORKDIR, "w")
			f.write('<?xml version="1.0" encoding="GB2312" ?>\n')
			f.write('<Partition_Info>\n')
			f.write('<Part Sel="1" PartitionName="fastboot" FlashType="emmc" FileSystem="none" Start="0" Length="1M" SelectFile="fastboot.bin"/>\n')
			f.write('<Part Sel="1" PartitionName="bootargs" FlashType="emmc" FileSystem="none" Start="1M" Length="1M" SelectFile="bootargs.bin"/>\n')
			f.write('<Part Sel="1" PartitionName="bootimg" FlashType="emmc" FileSystem="none" Start="2M" Length="1M" SelectFile="boot.img"/>\n')
			f.write('<Part Sel="1" PartitionName="baseparam" FlashType="emmc" FileSystem="none" Start="3M" Length="3M" SelectFile="baseparam.img"/>\n')
			f.write('<Part Sel="1" PartitionName="pqparam" FlashType="emmc" FileSystem="none" Start="6M" Length="4M" SelectFile="pq_param.bin"/>\n')
			f.write('<Part Sel="1" PartitionName="logo" FlashType="emmc" FileSystem="none" Start="10M" Length="4M" SelectFile="logo.img"/>\n')
			f.write('<Part Sel="1" PartitionName="deviceinfo" FlashType="emmc" FileSystem="none" Start="14M" Length="4M" SelectFile="deviceinfo.bin"/>\n')
			f.write('<Part Sel="1" PartitionName="loader" FlashType="emmc" FileSystem="none" Start="26M" Length="32M" SelectFile="apploader.bin"/>\n')
			f.write('<Part Sel="1" PartitionName="kernel" FlashType="emmc" FileSystem="none" Start="66M" Length="32M" SelectFile="kernel.bin"/>\n')
			f.write('<Part Sel="1" PartitionName="rootfs" FlashType="emmc" FileSystem="ext3/4" Start="98M" Length="7000M" SelectFile="rootfs.ext4"/>\n')
			f.write('</Partition_Info>\n')
			f.close()
			cmdlist.append('mkupdate -s 00000003-00000001-01010101 -f %s/emmc_partitions.xml -d %s/%s' % (self.WORKDIR,self.WORKDIR,self.EMMCIMG))
		self.session.open(ScreenConsole, title = self.TITLE, cmdlist = cmdlist, finishedCallback = self.doFullBackupCB, closeOnSuccess = True)
                
	def doFullBackupCB(self):
		if HaveGZkernel:
			ret = commands.getoutput(' gzip -d %s/vmlinux.gz -c > /tmp/vmlinux.bin' % self.WORKDIR)
			if ret:
				text = "Kernel dump error\n"
				text += "Please Flash your Kernel new and Backup again"
				system('rm -rf /tmp/vmlinux.bin')
				self.session.open(MessageBox, _(text), type = MessageBox.TYPE_ERROR)
				return

		cmdlist = []
		cmdlist.append(self.message)
		if HaveGZkernel:
			cmdlist.append('echo "Kernel dump OK"')
			cmdlist.append("rm -rf /tmp/vmlinux.bin")
		cmdlist.append('echo "_________________________________________________"')
		cmdlist.append('echo "Almost there... "')
		cmdlist.append('echo "Now building the USB-Image"')

		system('rm -rf %s' %self.MAINDEST)
		if not path.exists(self.MAINDEST):
			makedirs(self.MAINDEST)
		if not path.exists(self.EXTRA):
			makedirs(self.EXTRA)

		f = open("%s/imageversion" %self.MAINDEST, "w")
		f.write(self.IMAGEVERSION)
		f.close()

		if self.ROOTFSBIN == "rootfs.tar.bz2":
			system('mv %s/rootfs.tar.bz2 %s/rootfs.tar.bz2' %(self.WORKDIR, self.MAINDEST))
		else:
			system('mv %s/root.%s %s/%s' %(self.WORKDIR, self.ROOTFSTYPE, self.MAINDEST, self.ROOTFSBIN))
		if SystemInfo["HaveMultiBoot"]:
			system('mv %s/kernel.bin %s/kernel.bin' %(self.WORKDIR, self.MAINDEST))
		elif self.MTDKERNEL.startswith('mmcblk0'):
			system('mv %s/%s %s/%s' %(self.WORKDIR, self.KERNELBIN, self.MAINDEST, self.KERNELBIN))
		else:
			system('mv %s/vmlinux.gz %s/%s' %(self.WORKDIR, self.MAINDEST, self.KERNELBIN))

		if SystemInfo["HaveMultiBoot"] and self.list[self.selection] == "Recovery":
			system('mv %s/%s %s/%s' %(self.WORKDIR,self.EMMCIMG, self.MAINDEST,self.EMMCIMG))
		elif self.MODEL in ("vuultimo4k","vusolo4k", "vuduo2", "vusolo2", "vusolo", "vuduo", "vuultimo", "vuuno"):
			cmdlist.append('echo "This file forces a reboot after the update." > %s/reboot.update' %self.MAINDEST)
		elif self.MODEL in ("vuzero" , "vusolose", "vuuno4k", "vuzero4k"):
			cmdlist.append('echo "This file forces the update." > %s/force.update' %self.MAINDEST)
		elif self.MODEL in ('viperslim','evoslimse','evoslimt2c', "novaip" , "zgemmai55" , "sf98", "xpeedlxpro",'evoslim','vipert2c'):
			cmdlist.append('echo "This file forces the update." > %s/force' %self.MAINDEST)
		else:
			cmdlist.append('echo "rename this file to "force" to force an update without confirmation" > %s/noforce' %self.MAINDEST)

		if self.MODEL in ("gbquad4k","gbue4k"):
			system('mv %s/boot.bin %s/boot.bin' %(self.WORKDIR, self.MAINDEST))
			system('mv %s/rescue.bin %s/rescue.bin' %(self.WORKDIR, self.MAINDEST))
			system('cp -f /usr/share/gpt.bin %s/gpt.bin' %(self.MAINDEST))

		if self.MACHINEBUILD in ("h9","i55plus"):
			system('mv %s/fastboot.bin %s/fastboot.bin' %(self.WORKDIR, self.MAINDEST))
			system('mv %s/pq_param.bin %s/pq_param.bin' %(self.WORKDIR, self.MAINDEST))
			system('mv %s/bootargs.bin %s/bootargs.bin' %(self.WORKDIR, self.MAINDEST))
			system('mv %s/baseparam.bin %s/baseparam.bin' %(self.WORKDIR, self.MAINDEST))
			system('mv %s/logo.bin %s/logo.bin' %(self.WORKDIR, self.MAINDEST))

		if self.MODEL in ("gbquad", "gbquadplus", "gb800ue", "gb800ueplus", "gbultraue", "gbultraueh", "twinboxlcd", "twinboxlcdci", "singleboxlcd", "sf208", "sf228"):
			lcdwaitkey = '/usr/share/lcdwaitkey.bin'
			lcdwarning = '/usr/share/lcdwarning.bin'
			if path.exists(lcdwaitkey):
				system('cp %s %s/lcdwaitkey.bin' %(lcdwaitkey, self.MAINDEST))
			if path.exists(lcdwarning):
				system('cp %s %s/lcdwarning.bin' %(lcdwarning, self.MAINDEST))
		if self.MODEL in ("e4hdultra","protek4k"):
			lcdwarning = '/usr/share/lcdflashing.bmp'
			if path.exists(lcdwarning):
				system('cp %s %s/lcdflashing.bmp' %(lcdwarning, self.MAINDEST))
		if self.MODEL == "gb800solo":
			burnbat = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
			f = open("%s/burn.bat" % (burnbat), "w")
			f.write("flash -noheader usbdisk0:gigablue/solo/kernel.bin flash0.kernel\n")
			f.write("flash -noheader usbdisk0:gigablue/solo/rootfs.bin flash0.rootfs\n")
			f.write('setenv -p STARTUP "boot -z -elf flash0.kernel: ')
			f.write("'rootfstype=jffs2 bmem=106M@150M root=/dev/mtdblock6 rw '")
			f.write('"\n')
			f.close()

		cmdlist.append('cp -r %s/* %s/' % (self.MAINDEST, self.EXTRA))
		if self.MACHINEBUILD in ("h9","i55plus"):
			cmdlist.append('cp -f /usr/share/fastboot.bin %s/fastboot.bin' %(self.EXTRAROOT))
			cmdlist.append('cp -f /usr/share/bootargs.bin %s/bootargs.bin' %(self.EXTRAROOT))

		cmdlist.append("sync")
		file_found = True

		if not path.exists("%s/%s" % (self.MAINDEST, self.ROOTFSBIN)):
			print 'ROOTFS bin file not found'
			file_found = False

		if not path.exists("%s/%s" % (self.MAINDEST, self.KERNELBIN)):
			print 'KERNEL bin file not found'
			file_found = False

		if path.exists("%s/noforce" % self.MAINDEST):
			print 'NOFORCE bin file not found'
			file_found = False

		if SystemInfo["HaveMultiBoot"] and not self.list[self.selection] == "Recovery":
			cmdlist.append('echo "_________________________________________________\n"')
			cmdlist.append('echo "Multiboot Image created on:" %s' %self.MAINDEST)
			cmdlist.append('echo "and there is made an extra copy on:"')
			cmdlist.append('echo %s' %self.EXTRA)
			cmdlist.append('echo "_________________________________________________\n"')
			cmdlist.append('echo " "')
			cmdlist.append('echo "\nPlease wait...almost ready! "')
			cmdlist.append('echo " "')
			cmdlist.append('echo "To restore the image:"')
			cmdlist.append('echo "Use FlashLocal in Quickmenu"')
		elif file_found:
			cmdlist.append('echo "_________________________________________________\n"')
			cmdlist.append('echo "USB Image created on:" %s' %self.MAINDEST)
			cmdlist.append('echo "and there is made an extra copy on:"')
			cmdlist.append('echo %s' %self.EXTRA)
			cmdlist.append('echo "_________________________________________________\n"')
			cmdlist.append('echo " "')
			cmdlist.append('echo "\nPlease wait...almost ready! "')
			cmdlist.append('echo " "')
			cmdlist.append('echo "To restore the image:"')
			cmdlist.append('echo "Use FlashLocal in Quickmenu"')
		else:
			cmdlist.append('echo "_________________________________________________\n"')
			cmdlist.append('echo "Image creation failed - "')
			cmdlist.append('echo "Probable causes could be"')
			cmdlist.append('echo "     wrong back-up destination "')
			cmdlist.append('echo "     no space left on back-up device"')
			cmdlist.append('echo "     no writing permission on back-up device"')
			cmdlist.append('echo " "')

		if self.DIRECTORY == "/hdd":
			self.TARGET = self.SearchUSBcanidate()
			print "TARGET = %s" % self.TARGET
			if self.TARGET == 'XX':
				cmdlist.append('echo " "')
			else:
				cmdlist.append('echo "_________________________________________________\n"')
				cmdlist.append('echo " "')
				cmdlist.append('echo "There is a valid USB-flash drive detected in one "')
				cmdlist.append('echo "of the USB-ports, therefor an extra copy of the "')
				cmdlist.append('echo "back-up image will now be copied to that USB- "')
				cmdlist.append('echo "flash drive. "')
				cmdlist.append('echo "This only takes about 1 or 2 minutes"')
				cmdlist.append('echo " "')

				cmdlist.append('mkdir -p %s/%s' % (self.TARGET, self.IMAGEFOLDER))
				cmdlist.append('cp -r %s %s/' % (self.MAINDEST, self.TARGET))
				if self.MACHINEBUILD in ("h9","i55plus"):
					cmdlist.append('cp -f /usr/share/fastboot.bin %s/fastboot.bin' %(self.TARGET))
					cmdlist.append('cp -f /usr/share/bootargs.bin %s/bootargs.bin' %(self.TARGET))

				cmdlist.append("sync")
				cmdlist.append('echo "Backup finished and copied to your USB-flash drive"')
			
		cmdlist.append("umount /tmp/bi/root")
		cmdlist.append("rmdir /tmp/bi/root")
		cmdlist.append("rmdir /tmp/bi")
		cmdlist.append("rm -rf %s" % self.WORKDIR)
		cmdlist.append("sleep 5")
		END = time()
		DIFF = int(END - self.START)
		TIMELAP = str(datetime.timedelta(seconds=DIFF))
		cmdlist.append('echo "Time required for this process: %s"' %TIMELAP)
		cmdlist.append('echo "Start Zip Files from Backup please wait 1-4min!"')
		self.session.open(ScreenConsole, title = self.TITLE, cmdlist = cmdlist,finishedCallback = self.doFullZip, closeOnSuccess = True)
		
	def doFullZip(self):
	        cmdlist = []
	        cmdlist.append(self.message)
		self.make_zipfile("opennfr-%s-%s-%s_usb.zip" % (getImageVersion(), self.MODEL, strftime("%Y-%m-%d", localtime(self.START))), self.MAINDEST1)
		cmdlist.append('echo "Build Zip Files is ready!"')
		if closed:
		        now = int(time())
	                config.imagemanager.lastbackup.value = now
	                config.imagemanager.lastbackup.save()		
		        self.session.open(ScreenConsole, title = self.TITLE, cmdlist = cmdlist, finishedCallback = self.close, closeOnSuccess = True)
		else:
		        self.session.open(ScreenConsole, title = self.TITLE, cmdlist = cmdlist, closeOnSuccess = True)
                if closed:
                        self.close()
	def make_zipfile(self, output_filename, source_dir):
		if getBrandOEM() in ("fulan"):
			output_zip = self.EXTRA1 + "/" + output_filename
		else:
			output_zip = self.EXTRA1 + "/" + output_filename
		relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
		with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zip:
			for root, dirs, files in os.walk(source_dir):
				# add directory (needed for empty dirs)
				zip.write(root, os.path.relpath(root, relroot))
				for file in files:
					filename = os.path.join(root, file)
					if os.path.isfile(filename): # regular files only
						arcname = os.path.join(os.path.relpath(root, relroot), file)
						zip.write(filename, arcname)
                if closed:
                	self.close()

	def imageInfo(self):
		AboutText = _("Full Image Backup ")
		AboutText += _("By openNFR Image Team") + "\n"
		AboutText += _("Support at") + " www.nachtfalke.biz\n\n"
		AboutText += _("[Image Info]\n")
		AboutText += _("Model: %s %s\n") % (getMachineBrand(), getMachineName())
		AboutText += _("Backup Date: %s\n") % strftime("%Y-%m-%d", localtime(self.START))

		if path.exists('/proc/stb/info/chipset'):
			AboutText += _("Chipset: BCM%s") % about.getChipSetString().lower().replace('\n','').replace('bcm','') + "\n"

		AboutText += _("CPU: %s") % about.getCPUString() + "\n"
		AboutText += _("Cores: %s") % about.getCpuCoresString() + "\n"

		AboutText += _("Version: %s") % getImageVersion() + "\n"
		AboutText += _("Build: %s") % getImageBuild() + "\n"
		AboutText += _("Kernel: %s") % about.getKernelVersionString() + "\n"

		string = getDriverDate()
		year = string[0:4]
		month = string[4:6]
		day = string[6:8]
		driversdate = '-'.join((year, month, day))
		AboutText += _("Drivers:\t%s") % driversdate + "\n"

		AboutText += _("Last update:\t%s") % getEnigmaVersionString() + "\n\n"

		AboutText += _("[Enigma2 Settings]\n")
		AboutText += commands.getoutput("cat /etc/enigma2/settings")
		AboutText += _("\n\n[User - bouquets (TV)]\n")
		try:
			f = open("/etc/enigma2/bouquets.tv","r")
			lines = f.readlines()
			f.close()
			for line in lines:
				if line.startswith("#SERVICE:"):
					bouqet = line.split()
					if len(bouqet) > 3:
						bouqet[3] = bouqet[3].replace('"','')
						f = open("/etc/enigma2/" + bouqet[3],"r")
						userbouqet = f.readline()
						AboutText += userbouqet.replace('#NAME ','')
						f.close()
		except:
			AboutText += "Error reading bouquets.tv"
			
		AboutText += _("\n[User - bouquets (RADIO)]\n")
		try:
			f = open("/etc/enigma2/bouquets.radio","r")
			lines = f.readlines()
			f.close()
			for line in lines:
				if line.startswith("#SERVICE:"):
					bouqet = line.split()
					if len(bouqet) > 3:
						bouqet[3] = bouqet[3].replace('"','')
						f = open("/etc/enigma2/" + bouqet[3],"r")
						userbouqet = f.readline()
						AboutText += userbouqet.replace('#NAME ','')
						f.close()
		except:
			AboutText += "Error reading bouquets.radio"

		AboutText += _("\n[Installed Plugins]\n")
		AboutText += commands.getoutput("opkg list_installed | grep enigma2-plugin-")

		return AboutText 
