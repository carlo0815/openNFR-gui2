#################################################################################
# FULL BACKUP UYILITY FOR ENIGMA2, SUPPORTS THE MODELS OE-A 2.0  MOD by NFR		#
#																				#
#					MAKES A FULLBACK-UP READY FOR FLASHING.						#
#																				#
#################################################################################
from enigma import getEnigmaVersionString
from boxbranding import getBoxType, getMachineName, getMachineBrand, getBrandOEM, getMachineBuild, getImageFolder, getImageVersion, getImageBuild, getDriverDate, getMachineProcModel, getMachineUBINIZE, getMachineMKUBIFS, getMachineMtdKernel, getMachineKernelFile, getMachineRootFile, getImageFileSystem
from Screens.Screen import Screen
from Components.Button import Button
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.About import about
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from time import time, strftime, localtime
from os import path, system, makedirs, listdir, walk, statvfs
import os
import commands
import datetime
import zipfile
import os
from boxbranding import getBoxType, getMachineBrand, getMachineName, getDriverDate, getImageVersion, getImageBuild, getBrandOEM, getMachineBuild, getImageFolder, getMachineUBINIZE, getMachineMKUBIFS, getMachineMtdKernel, getMachineKernelFile, getMachineRootFile, getImageFileSystem

 
HaveGZkernel = True
if getBrandOEM() in ("fulan"):
	HaveGZkernel = False

VERSION = "Version 2.0 "

def Freespace(dev):
	statdev = statvfs(dev)
	space = (statdev.f_bavail * statdev.f_frsize) / 1024
	print "[FULL BACKUP] Free space on %s = %i kilobytes" %(dev, space)
	return space

class ImageBackup(Screen):
	skin = """
	<screen position="center,center" size="560,400" title="Image Backup">
		<ePixmap position="0,360"   zPosition="1" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap position="140,360" zPosition="1" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap position="280,360" zPosition="1" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
		<ePixmap position="420,360" zPosition="1" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
		<widget name="key_red" position="0,360" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_green" position="140,360" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_yellow" position="280,360" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_blue" position="420,360" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="info-hdd" position="10,30" zPosition="1" size="450,100" font="Regular;20" halign="left" valign="top" transparent="1" />
		<widget name="info-usb" position="10,150" zPosition="1" size="450,200" font="Regular;20" halign="left" valign="top" transparent="1" />
	</screen>"""
		
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		self.session = session
		self.MODEL = getBoxType()
		self.OEM = getBrandOEM()
		self.MACHINEBUILD = getMachineBuild()
		self.MODEL1 = getMachineProcModel()
		self.MACHINENAME = getMachineName()
		self.MACHINEBRAND = getMachineBrand()
		self.IMAGEFOLDER = getImageFolder()
		self.UBINIZE_ARGS = getMachineUBINIZE()
		self.MKUBIFS_ARGS = getMachineMKUBIFS()
		self.MTDKERNEL = getMachineMtdKernel()
		self.ROOTFSBIN = getMachineRootFile()
		self.KERNELBIN = getMachineKernelFile()
		self.ROOTFSTYPE = getImageFileSystem()
		print "[FULL BACKUP] BOX MACHINEBUILD = >%s<" %self.MACHINEBUILD
		print "[FULL BACKUP] BOX MACHINENAME = >%s<" %self.MACHINENAME
		print "[FULL BACKUP] BOX MACHINEBRAND = >%s<" %self.MACHINEBRAND
		print "[FULL BACKUP] BOX MODEL = >%s<" %self.MODEL
		print "[FULL BACKUP] OEM MODEL = >%s<" %self.OEM
		print "[FULL BACKUP] IMAGEFOLDER = >%s<" %self.IMAGEFOLDER
		print "[FULL BACKUP] UBINIZE = >%s<" %self.UBINIZE_ARGS
		print "[FULL BACKUP] MKUBIFS = >%s<" %self.MKUBIFS_ARGS
		print "[FULL BACKUP] MTDKERNEL = >%s<" %self.MTDKERNEL
		print "[FULL BACKUP] ROOTFSTYPE = >%s<" %self.ROOTFSTYPE
		print "[FULL BACKUP] KERNELBIN = >%s<" %self.KERNELBIN
		print "[FULL BACKUP] ROOTFSBIN = >%s<" %self.ROOTFSBIN		
		
		self["key_green"] = Button("USB")
		self["key_red"] = Button("HDD")
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")
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
		#// Not used
		pass	

	def testUBIFS(self):
		f = open("/proc/mounts", "r")
		mounts = f.readlines()
		f.close()
		for line in mounts:
			if "rootfs" in line and "ubifs" in line:
				return "ubifs"
		return "jffs2"

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
		self.TITLE = _("Full back-up on %s") % (self.DIRECTORY)
		self.START = time()
		self.DATE = strftime("%Y%m%d_%H%M", localtime(self.START))
		self.IMAGEVERSION = self.imageInfo() #strftime("%Y%m%d", localtime(self.START))
		if self.ROOTFSTYPE == "ubi":
			self.ROOTFSTYPE = self.testUBIFS()
			self.MKFS = "/usr/sbin/mkfs.%s" %self.ROOTFSTYPE
		else:
			self.MKFS = "/usr/sbin/mkfs.jffs2"
		self.UBINIZE = "/usr/sbin/ubinize"
		self.NANDDUMP = "/usr/sbin/nanddump"
		self.WORKDIR= "%s/bi" %self.DIRECTORY
		self.TARGET="XX"
		if getBrandOEM() in ("fulan"):
			self.ROOTFSBIN="e2jffs2.img"
			self.KERNELBIN="uImage"		
		else:
			self.MTDKERNEL="mtd1"
			self.ROOTFSBIN="rootfs.bin"
			self.KERNELBIN="kernel.bin"

		## TESTING IF ALL THE TOOLS FOR THE BUILDING PROCESS ARE PRESENT
		if not path.exists(self.MKFS):
			text = "%s not found !!" %self.MKFS
			self.session.open(MessageBox, _(text), type = MessageBox.TYPE_ERROR)
			return
		if not path.exists(self.NANDDUMP):
			text = "%s not found !!" %self.NANDDUMP
			self.session.open(MessageBox, _(text), type = MessageBox.TYPE_ERROR)
			return

		## TESTING WHICH KIND OF SATELLITE RECEIVER IS USED

		## TESTING THE Odin M9 Model
		if getBrandOEM() in ("fulan"):
			self.SHOWNAME = "%s %s" %(self.MACHINEBRAND, self.MODEL)
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/%s" %(self.DIRECTORY,self.IMAGEFOLDER)
			if getBrandOEM() in ('vuplus', 'gigablue'):
					self.MAINDEST1 = "%s/%s" %(self.DIRECTORY,self.OEM)
			elif self.MACHINEBRAND in ('Atemio'):
				self.MAINDEST1 = "%s/atemio" %(self.DIRECTORY)
			elif self.MACHINEBRAND in ('UNiBOX'):
				self.MAINDEST1 = "%s/unibox" %(self.DIRECTORY)
			else:
					self.MAINDEST1 = "%s/%s" %(self.DIRECTORY,self.IMAGEFOLDER)
			self.EXTRA = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		elif self.MODEL == "odinm9":
			self.TYPE = "ODINM9"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "ODIN %s" %self.MODEL
			self.MTDKERNEL = "mtd2"	
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/odinm9" % self.DIRECTORY
			self.MAINDEST1 = "%s/odinm9" % self.DIRECTORY
			self.EXTRAOLD = "%s/fullbackup_%s/%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE, self.MODEL)
			self.EXTRA = "%s/fullbackup_odinm9/%s" % (self.DIRECTORY, self.DATE)
			self.EXTRA1 = "%s/fullbackup_odinm9/%s" % (self.DIRECTORY, self.DATE)
		## TESTING THE Odin M7 Model
		elif self.MODEL == "odinm7" or self.MODEL1 == "odinm7":
			self.TYPE = "ODINM7"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "ODIN %s" %self.MODEL
			self.MTDKERNEL = "mtd3"	
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/en2" % self.DIRECTORY
			self.MAINDEST1 = "%s/en2" % self.DIRECTORY
			self.EXTRAOLD = "%s/fullbackup_%s/%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE, self.MODEL)
			self.EXTRA = "%s/fullbackup_odinm7/%s" % (self.DIRECTORY, self.DATE)
			self.EXTRA1 = "%s/fullbackup_odinm7/%s" % (self.DIRECTORY, self.DATE) 
		## TESTING THE Odin M6 Model
		elif self.MODEL == "odinm6":
			self.TYPE = "ODINM7"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "ODIN %s" %self.MODEL
			self.MTDKERNEL = "mtd3"	
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/en2" % self.DIRECTORY
			self.MAINDEST1 = "%s/en2" % self.DIRECTORY
			self.EXTRAOLD = "%s/fullbackup_%s/%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE, self.MODEL)
			self.EXTRA = "%s/fullbackup_odinm7/%s" % (self.DIRECTORY, self.DATE)
			self.EXTRA1 = "%s/fullbackup_odinm7/%s" % (self.DIRECTORY, self.DATE) 
		## TESTING THE E3 HD Model
		elif self.MODEL == "evoe3hd":
			self.TYPE = "E3HD"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "%s" %self.MODEL
			self.MTDKERNEL = "mtd1"	
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/e3hd" % self.DIRECTORY
			self.MAINDEST1 = "%s/e3hd" % self.DIRECTORY
			self.EXTRAOLD = "%s/fullbackup_%s/%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE, self.MODEL)
			self.EXTRA = "%s/fullbackup_e3hd/%s" % (self.DIRECTORY, self.DATE)
			self.EXTRA1 = "%s/fullbackup_e3hd/%s" % (self.DIRECTORY, self.DATE)
		## TESTING THE MK Digital Model
		elif self.MODEL == "xp1000":
			self.TYPE = "MAXDIGITAL"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "MaxDigital %s" %self.MODEL
			self.MTDKERNEL = "mtd1"	
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.EXTRA = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.TYPE, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.TYPE, self.DATE)
		## TESTING THE MK Model
		elif self.MODEL == "xp1000mk":
			self.TYPE = "MK"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "MK %s" %self.MODEL
			self.MTDKERNEL = "mtd1"	
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/xp1000" % self.DIRECTORY
			self.MAINDEST1 = "%s/xp1000" % self.DIRECTORY
			self.EXTRA = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.TYPE, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.TYPE, self.DATE)
		## TESTING THE OCTAGON Model
		elif self.MODEL == "xp1000" and self.MACHINENAME.lower() == "sf8 hd":
			self.TYPE = "OCTAGON"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "Octagon SF8 HD"
			self.MTDKERNEL = "mtd1"	
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.EXTRA = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.TYPE, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.TYPE, self.DATE)
		## TESTING Venton HDx Model
		elif self.MODEL == "uniboxhd1" or self.MODEL == "uniboxhd2" or self.MODEL == "uniboxhd3":
			self.TYPE = "VENTON"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "%s" %self.MODEL
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/venton-hdx" % self.DIRECTORY
			self.MAINDEST1 = "%s/venton-hdx" % self.DIRECTORY
			self.EXTRA = "%s/fullbackup_%s/%s/venton" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		elif self.MODEL == "ventonhdx" and self.MACHINENAME.lower() == "hd-5000":
			self.TYPE = "SEZAM"
			self.MODEL = "hdx"			
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "SEZAM 5000HD"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/%s" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/%s" % (self.DIRECTORY, self.MODEL)
			self.EXTRA = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		elif self.MODEL == "ventonhdx" and self.MACHINENAME.lower() == "premium twin":
			self.TYPE = "MICRACLE"
			self.MODEL = "twin"			
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "MICRACLE Primium Twin"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/miraclebox/%s" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/miraclebox" %self.DIRECTORY
			self.EXTRA = "%s/fullbackup_%s/%s/miraclebox" % (self.DIRECTORY, self.MODEL, self.DATE)	
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)	
		elif self.MODEL == "uniboxhde" and self.MACHINENAME.lower() == "hdeco+":
			self.TYPE = "VENTONECO"
			self.MODEL = "hde"
			self.MTDKERNEL = "mtd7"	
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 8160 -F"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "UNIBOX HDECO"
			self.MAINDESTOLD = "%s/unibox/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/unibox/%s" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/unibox" % self.DIRECTORY
			self.EXTRA = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		## TESTING INI HDe Model
		elif self.MODEL == "ini-1000de" or self.MODEL == "xpeedlx2" or self.MODEL == "xpeedlx1":
			self.TYPE = "GI"
			self.MODEL = "xpeedlx"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "GI XpeedLX"
			self.MTDKERNEL = "mtd2"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/%s" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/%s" % (self.DIRECTORY, self.MODEL)
			self.EXTRA = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		elif self.MODEL == "atemio5x00":
			self.TYPE = "ATEMIO"
			self.MODEL = "5x00"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "Atemio 5x00"
			self.MTDKERNEL = "mtd2"
			self.MAINDESTOLD = "%s/Atemio/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/Atemio/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/atemio" % self.DIRECTORY
			self.EXTRA = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		elif self.MODEL == "ini-9000de" or self.MODEL == "xpeedlx3":
			self.TYPE = "GI"
			self.MODEL = "xpeedlx3"
			self.MKUBIFS_ARGS = "-m 4096 -e 1040384 -c 1984"
			self.UBINIZE_ARGS = "-m 4096 -p 1024KiB"
			self.SHOWNAME = "GI XpeedLX3"
			self.MTDKERNEL = "mtd2"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/%s" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/%s" % (self.DIRECTORY, self.MODEL)
			self.EXTRA = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		elif self.MODEL == "ini-8000am" or self.MODEL == "atemionemesis":
			self.TYPE = "ATEMIO"
			self.MODEL = "atemionemesis"
			self.MODEL1 = "8x00"
			self.MKUBIFS_ARGS = "-m 4096 -e 1040384 -c 1984"
			self.UBINIZE_ARGS = "-m 4096 -p 1024KiB"
			self.SHOWNAME = "Atemio Nemesis"
			self.MTDKERNEL = "mtd2"
			self.MAINDESTOLD = "%s/Atemio/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/atemio/8x00" % self.DIRECTORY
			self.MAINDEST1 = "%s/atemio" % self.DIRECTORY
			self.EXTRA = "%s/fullbackup_%s/%s/" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		## TESTING Atemio 6x00 Model
		elif self.MODEL == "atemio6000":
			self.TYPE = "ATEMIO"
			self.MODEL = "atemio6000"
			self.MODEL1 = "6000"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "Atemio 6000"
			self.MTDKERNEL = "mtd2"
			self.MAINDESTOLD = "%s/Atemio/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/atemio/6000" % self.DIRECTORY
			self.MAINDEST1 = "%s/atemio" % self.DIRECTORY
			self.EXTRA = "%s/fullbackup_%s/%s/" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		elif self.MODEL == "atemio6100":
			self.TYPE = "ATEMIO"
			self.MODEL = "atemio6100"
			self.MODEL1 = "6100"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "Atemio 6100"
			self.MTDKERNEL = "mtd2"
			self.MAINDESTOLD = "%s/Atemio/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/atemio/6100" % self.DIRECTORY
			self.MAINDEST1 = "%s/atemio" % self.DIRECTORY
			self.EXTRA = "%s/fullbackup_%s/%s/" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		elif self.MODEL == "atemio6200":
			self.TYPE = "ATEMIO"
			self.MODEL = "atemio6200"
			self.MODEL1 = "6200"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "Atemio 6200"
			self.MTDKERNEL = "mtd2"
			self.MAINDESTOLD = "%s/Atemio/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/atemio/6200" % self.DIRECTORY
			self.MAINDEST1 = "%s/atemio" % self.DIRECTORY
			self.EXTRA = "%s/fullbackup_%s/%s/" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		## TESTING MUTANT Model
		elif self.MODEL == "mutant2400":
			self.TYPE = "MUT@NT"
			self.MODEL = "mutant2400"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 8192"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "Mutant 2400"
			self.MTDKERNEL = "mtd1"
			self.MAINDESTOLD = "%s/Mut@nt/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/hd2400" % self.DIRECTORY
			self.MAINDEST1 = "%s/hd2400" % self.DIRECTORY
			self.EXTRA = "%s/fullbackup_%s/%s/" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		elif self.MODEL == "quadbox2400":
			self.TYPE = "AX"
			self.MODEL = "quadbox2400"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 8192"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "QuadBox HD2400"
			self.MTDKERNEL = "mtd1"
			self.MAINDESTOLD = "%s/AX/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/hd2400" % self.DIRECTORY
			self.MAINDEST1 = "%s/hd2400" % self.DIRECTORY
			self.EXTRA = "%s/fullbackup_%s/%s/" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)	
		elif self.MODEL == "inihde" and self.MACHINENAME.lower() == "hd-1000":
			self.TYPE = "SEZAM"
			self.MODEL = "hde"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "SEZAM 1000HD"
			self.MTDKERNEL = "mtd2"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/%s" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/%s" % (self.DIRECTORY, self.MODEL)
			self.EXTRA = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		## TESTING Formuler F1
		elif self.MODEL == "formuler1":
			self.TYPE = "FORMULER"
			self.MODEL = "formuler1"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 8192"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "Formuler F1"
			self.MTDKERNEL = "mtd1"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/%s" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/%s" % (self.DIRECTORY, self.MODEL)
			self.EXTRA = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		elif self.MODEL == "formuler3":
			self.TYPE = "FORMULER"
			self.MODEL = "formuler3"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 8192"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "Formuler F3"
			self.MTDKERNEL = "mtd1"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/%s" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/%s" % (self.DIRECTORY, self.MODEL)
			self.EXTRA = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		## TESTING Technomate Model
		elif self.MODEL == "tmtwin":
			self.TYPE = "TECHNO"
			self.MODEL = "tmtwinoe"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096 -F"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "%s" %self.MODEL
			self.MTDKERNEL = "mtd6"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/update/%s/cfe" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/update" %self.DIRECTORY
			self.EXTRA = "%s/fullbackup_TECHNO/%s/update/%s" % (self.DIRECTORY, self.DATE, self.MODEL)
			self.EXTRA1 = "%s/fullbackup_TECHNO/%s" % (self.DIRECTORY, self.DATE)
		## TESTING Technomate Model
		elif self.MODEL == "tmsingle":
			self.TYPE = "TECHNO"
			self.MODEL = "tmsingle"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096 -F"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "%s" %self.MODEL
			self.MTDKERNEL = "mtd6"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/update/%s/cfe" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/update" %self.DIRECTORY 
			self.EXTRA = "%s/fullbackup_TECHNO/%s/update/%s" % (self.DIRECTORY, self.DATE, self.MODEL)
			self.EXTRA1 = "%s/fullbackup_TECHNO/%s" % (self.DIRECTORY, self.DATE)
		## TESTING Technomate Model
		elif self.MODEL == "tmnano":
			self.TYPE = "TECHNO"
			self.MODEL = "tmnanooe"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096 -F"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "%s" %self.MODEL
			self.MTDKERNEL = "mtd6"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/update/%s/cfe" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/update" %self.DIRECTORY
			self.EXTRA = "%s/fullbackup_TECHNO/%s/update/%s" % (self.DIRECTORY, self.DATE, self.MODEL)
			self.EXTRA1 = "%s/fullbackup_TECHNO/%s" % (self.DIRECTORY, self.DATE)
		## TESTING Technomate Model
		elif self.MODEL == "tm2t":
			self.TYPE = "TECHNO"
			self.MODEL = "tm2toe"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096 -F"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "%s" %self.MODEL
			self.MTDKERNEL = "mtd6"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/update/%s/cfe" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/update" %self.DIRECTORY
			self.EXTRA = "%s/fullbackup_TECHNO/%s/update/%s" % (self.DIRECTORY, self.DATE, self.MODEL)
			self.EXTRA1 = "%s/fullbackup_TECHNO/%s" % (self.DIRECTORY, self.DATE)
		## TESTING Iqon Model
		elif self.MODEL == "iqonios100hd":
			self.TYPE = "IQON"
			self.MODEL = "ios100"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096 -F"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "%s" %self.MODEL
			self.MTDKERNEL = "mtd6"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/update/%s/cfe" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/update" %self.DIRECTORY
			self.EXTRA = "%s/fullbackup_IQON/%s/update/%s" % (self.DIRECTORY, self.DATE, self.MODEL)
			self.EXTRA1 = "%s/fullbackup_IQON/%s" % (self.DIRECTORY, self.DATE)
		## TESTING Iqon Model
		elif self.MODEL == "iqonios200hd":
			self.TYPE = "IQON"
			self.MODEL = "ios200"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096 -F"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "%s" %self.MODEL
			self.MTDKERNEL = "mtd6"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/update/%s/cfe" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/update" %self.DIRECTORY
			self.EXTRA = "%s/fullbackup_IQON/%s/update/%s" % (self.DIRECTORY, self.DATE, self.MODEL)
			self.EXTRA1 = "%s/fullbackup_IQON/%s" % (self.DIRECTORY, self.DATE)
		## TESTING Iqon Model
		elif self.MODEL == "iqonios300hd":
			self.TYPE = "IQON"
			self.MODEL = "ios300"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096 -F"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "%s" %self.MODEL
			self.MTDKERNEL = "mtd6"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/update/%s/cfe" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/update" %self.DIRECTORY
			self.EXTRA = "%s/fullbackup_IQON/%s/update/%s" % (self.DIRECTORY, self.DATE, self.MODEL)
			self.EXTRA1 = "%s/fullbackup_IQON/%s" % (self.DIRECTORY, self.DATE)
		## TESTING Edison Model
		elif self.MODEL == "optimussos2":
			self.TYPE = "EDISION"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096 -F"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "%s" %self.MODEL
			self.MTDKERNEL = "mtd6"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/update/%s/cfe" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/update" %self.DIRECTORY
			self.EXTRA = "%s/fullbackup_EDISION/%s/update/%s" % (self.DIRECTORY, self.DATE, self.MODEL)
			self.EXTRA1 = "%s/fullbackup_EDISION/%s" % (self.DIRECTORY, self.DATE)
		## TESTING THE Gigablue 800 Solo Model
		elif self.MODEL == "gb800solo":
			self.TYPE = "GIGABLUE"
			self.MODEL = "solo"
			self.JFFS2OPTIONS="--eraseblock=0x20000 -n -l --pad=125829120"
			self.SHOWNAME = "GigaBlue %s" %self.MODEL
			self.MTDKERNEL = "mtd2"	
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/gigablue/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/gigablue" %self.DIRECTORY
			self.EXTRA =  "%s/fullbackup_%s/%s/gigablue" % (self.DIRECTORY, self.TYPE, self.DATE)
			self.EXTRA1 =  "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.TYPE, self.DATE)
		## TESTING THE Gigablue 800 SE Model
		elif self.MODEL == "gb800se":
			self.TYPE = "GIGABLUE"
			self.MODEL = "se"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "GigaBlue %s" %self.MODEL
			self.MTDKERNEL = "mtd2"	
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/gigablue/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/gigablue" %self.DIRECTORY
			self.EXTRA =  "%s/fullbackup_%s/%s/gigablue" % (self.DIRECTORY, self.TYPE, self.DATE)
			self.EXTRA1 =  "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.TYPE, self.DATE)
		## TESTING THE Gigablue 800 UE Model
		elif self.MODEL == "gb800ue":
			self.TYPE = "GIGABLUE"
			self.MODEL = "ue"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "GigaBlue %s" %self.MODEL
			self.MTDKERNEL = "mtd2"	
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/gigablue/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/gigablue" %self.DIRECTORY
			self.EXTRA =  "%s/fullbackup_%s/%s/gigablue" % (self.DIRECTORY, self.TYPE, self.DATE)
			self.EXTRA1 =  "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.TYPE, self.DATE)
		## TESTING THE Gigablue 800 SE Plus Model
		elif self.MODEL == "gb800seplus":
			self.TYPE = "GIGABLUE"
			self.MODEL = "seplus"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "GigaBlue %s" %self.MODEL
			self.MTDKERNEL = "mtd2"	
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/gigablue/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/gigablue" %self.DIRECTORY
			self.EXTRA =  "%s/fullbackup_%s/%s/gigablue" % (self.DIRECTORY, self.TYPE, self.DATE)
			self.EXTRA1 =  "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.TYPE, self.DATE)
		## TESTING THE Gigablue 800 UE Plus Model
		elif self.MODEL == "gb800ueplus":
			self.TYPE = "GIGABLUE"
			self.MODEL = "ueplus"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "GigaBlue %s" %self.MODEL
			self.MTDKERNEL = "mtd2"	
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/gigablue/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/gigablue" %self.DIRECTORY
			self.EXTRA =  "%s/fullbackup_%s/%s/gigablue" % (self.DIRECTORY, self.TYPE, self.DATE)
			self.EXTRA1 =  "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.TYPE, self.DATE)
		## TESTING THE Gigablue HD Quad Model
		elif self.MODEL == "gbquad":
			self.TYPE = "GIGABLUE"
			self.MODEL = "quad"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "GigaBlue %s" %self.MODEL
			self.MTDKERNEL = "mtd2"	
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/gigablue/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/gigablue" %self.DIRECTORY
			self.EXTRA =  "%s/fullbackup_%s/%s/gigablue" % (self.DIRECTORY, self.TYPE, self.DATE)
			self.EXTRA1 =  "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.TYPE, self.DATE)
		elif self.MODEL == "gbquadplus":
			self.TYPE = "GIGABLUE"
			self.MODEL = "quadplus"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4000"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "GigaBlue %s" %self.MODEL
			self.MTDKERNEL = "mtd2"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/gigablue/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/gigablue" %self.DIRECTORY
			self.EXTRA = "%s/fullbackup_%s/%s/gigablue" % (self.DIRECTORY, self.TYPE, self.DATE)
			self.EXTRA1 =  "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.TYPE, self.DATE)
		## TESTING THE VU+ MODELS
		elif self.MODEL == "vusolo" or self.MODEL == "vuduo" or self.MODEL == "vuuno" or self.MODEL == "vuultimo" or self.MODEL == "vusolo2" or self.MODEL == "vuduo2":
			self.TYPE = "VU"
			if self.MODEL == "vusolo2" or self.MODEL == "vuduo2":
				self.MTDKERNEL = "mtd2"
			self.SHOWNAME = "VU+ %s" %self.MODEL[2:]
			self.MAINDEST = "%s/vuplus/%s" %(self.DIRECTORY, self.MODEL[2:])
			self.MAINDEST1 = "%s/vuplus" %self.DIRECTORY
			self.EXTRA =  "%s/fullbackup_%s/%s/vuplus" % (self.DIRECTORY, self.MODEL[2:], self.DATE)
			self.EXTRA1 =  "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL[2:], self.DATE)
			if self.ROOTFSTYPE == "ubifs":
				self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096 -F"
				self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			else:
				self.MTDROOT = 0
				self.MTDBOOT = 2
				self.JFFS2OPTIONS = "--eraseblock=0x20000 -n -l"
		## TESTING THE WWIO BRE2ZE
		elif self.MODEL == "bre2ze":
			self.TYPE = "WWIO"
			self.MODEL = "bre2ze"
			self.MKUBIFS_ARGS = "-m 2048 -e 126976 -c 4096"
			self.UBINIZE_ARGS = "-m 2048 -p 128KiB"
			self.SHOWNAME = "WWIO Bre2ze"
			self.MTDKERNEL = "mtd2"
			self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
			self.MAINDEST = "%s/%s" % (self.DIRECTORY, self.MODEL)
			self.MAINDEST1 = "%s/%s" % (self.DIRECTORY, self.MODEL)
			self.EXTRA = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
			self.EXTRA1 = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		else:
			print "No supported receiver found!"
			return
		
		if self.MODEL == "gbquad" or self.MODEL == "gbquadplus" or self.MODEL == "gb800ue" or self.MODEL == "gb800ueplus":
			lcdwaitkey = '/usr/share/lcdwaitkey.bin'
			lcdwarning = '/usr/share/lcdwarning.bin'
			if path.exists(lcdwaitkey):
				system('cp %s %s/lcdwaitkey.bin' %(lcdwaitkey, self.MAINDEST))
			if path.exists(lcdwarning):
				system('cp %s %s/lcdwarning.bin' %(lcdwarning, self.MAINDEST))		

		self.message = "echo -e '\n"
		self.message += (_("Back-up Tool for a %s\n" %self.SHOWNAME)).upper()
		self.message += VERSION + '\n'
		self.message += "_________________________________________________\n\n"
		self.message += _("Please be patient, a backup will now be made,\n")
		if self.ROOTFSTYPE == "ubifs":
			self.message += _("because of the used filesystem the back-up\n")
			self.message += _("will take about 3-12 minutes for this system\n")
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
		system("mount --bind / /tmp/bi/root")

		if self.ROOTFSTYPE == "jffs2":
			cmd1 = "%s --root=/tmp/bi/root --faketime --output=%s/root.jffs2 %s" % (self.MKFS, self.WORKDIR, self.MKUBIFS_ARGS)
			cmd2 = None
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
			if getBrandOEM() == "fulan":
				cmd3 = "mv %s/root.ubifs %s/root.%s" %(self.WORKDIR, self.WORKDIR, self.ROOTFSTYPE)
			


		cmdlist = []
		cmdlist.append(self.message)
		cmdlist.append('echo "Create: root.%s\n"' %self.ROOTFSTYPE)
		cmdlist.append(cmd1)
		if cmd2:
			cmdlist.append(cmd2)
			if getBrandOEM() in ("fulan"):
				cmdlist.append(cmd3)
		cmdlist.append("chmod 644 %s/root.%s" %(self.WORKDIR, self.ROOTFSTYPE))
		cmdlist.append('echo " "')
		cmdlist.append('echo "Create: kerneldump"')
		cmdlist.append('echo " "')
		cmdlist.append("nanddump -a -f %s/vmlinux.gz /dev/%s" % (self.WORKDIR, self.MTDKERNEL))
		cmdlist.append('echo " "')
		if HaveGZkernel:
			cmdlist.append('echo "Check: kerneldump"')
		cmdlist.append("sync")
				
		self.session.open(Console, title = self.TITLE, cmdlist = cmdlist, finishedCallback = self.doFullBackupCB, closeOnSuccess = True)

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
		if getBrandOEM() in ("fulan"):
			system('mv %s/root.%s %s/%s' %(self.WORKDIR, self.ROOTFSTYPE, self.MAINDEST, self.ROOTFSBIN))
			system('mv %s/vmlinux.gz %s/%s' %(self.WORKDIR, self.MAINDEST, self.KERNELBIN))
			cmdlist.append('echo "rename this file to "force" to force an update without confirmation" > %s/noforce' %self.MAINDEST)
			cmdlist.append('cp -r %s %s' % (self.MAINDEST, self.EXTRA))
		elif self.TYPE == "WWIO" or self.TYPE == "ATEMIO" or self.TYPE == "VENTON" or self.TYPE == "VENTONECO" or self.TYPE == "SEZAM" or self.TYPE == "MICRACLE" or self.TYPE == "GI" or self.TYPE == "ODINM9"  or self.TYPE == "ODINM7" or self.TYPE == "E3HD" or self.TYPE == "MAXDIGITAL" or self.TYPE == "OCTAGON" or self.TYPE == "MK" or self.TYPE == "MUT@NT" or self.TYPE == "AX" or self.TYPE == "FORMULER":
			system('mv %s/root.%s %s/%s' %(self.WORKDIR, self.ROOTFSTYPE, self.MAINDEST, self.ROOTFSBIN))
			system('mv %s/vmlinux.gz %s/%s' %(self.WORKDIR, self.MAINDEST, self.KERNELBIN))
			cmdlist.append('echo "rename this file to "force" to force an update without confirmation" > %s/noforce' %self.MAINDEST)
			cmdlist.append('cp -r %s %s' % (self.MAINDEST, self.EXTRA))
		elif self.TYPE == "VU":
			if self.MODEL == "vusolo2" or self.MODEL == "vuduo2":
				self.ROOTFSBIN = "root_cfe_auto.bin"
			else:
				self.ROOTFSBIN = "root_cfe_auto.jffs2"
			system('mv %s/root.%s %s/%s' %(self.WORKDIR, self.ROOTFSTYPE, self.MAINDEST, self.ROOTFSBIN))
			self.KERNELBIN = "kernel_cfe_auto.bin"
			system('mv %s/vmlinux.gz %s/%s' %(self.WORKDIR, self.MAINDEST, self.KERNELBIN))
			cmdlist.append('echo "rename this file to "force" to force an update without confirmation" > %s/noforce' %self.MAINDEST)
			cmdlist.append('cp -r %s %s' % (self.MAINDEST, self.EXTRA))
		elif self.TYPE == "TECHNO" or self.TYPE == "IQON" or self.TYPE == "EDISION":
			self.ROOTFSBIN = "oe_rootfs.bin"
			system('mv %s/root.%s %s/%s' %(self.WORKDIR, self.ROOTFSTYPE, self.MAINDEST, self.ROOTFSBIN))
			self.KERNELBIN = "oe_kernel.bin"
			system('mv %s/vmlinux.gz %s/%s' %(self.WORKDIR, self.MAINDEST, self.KERNELBIN))
			cmdlist.append('echo "rename this file to "force" to force an update without confirmation" > %s/noforce' %self.MAINDEST)
			cmdlist.append('cp -r %s %s' % (self.MAINDEST, self.EXTRA))
		elif self.TYPE == "GIGABLUE":
			if self.ROOTFSTYPE == "jffs2":
				system('mv %s/root.jffs2 %s/rootfs.bin' %(self.WORKDIR, self.MAINDEST))
			else:
				system('mv %s/root.ubifs %s/rootfs.bin' %(self.WORKDIR, self.MAINDEST))
			system('mv %s/vmlinux.gz %s/kernel.bin' %(self.WORKDIR, self.MAINDEST))
			cmdlist.append('echo "rename this file to "force" to force an update without confirmation" > %s/noforce' %self.MAINDEST)
			if self.MODEL == "quad" or self.MODEL == "ue" or self.MODEL == "ueplus" or self.MODEL == "quadplus":
				lcdwaitkey = '/usr/share/lcdwaitkey.bin'
				lcdwarning = '/usr/share/lcdwarning.bin'
				if path.exists(lcdwaitkey):
					system('cp %s %s/lcdwaitkey.bin' %(lcdwaitkey, self.MAINDEST))
				if path.exists(lcdwarning):
					system('cp %s %s/lcdwarning.bin' %(lcdwarning, self.MAINDEST))				
			cmdlist.append('cp -r %s %s' % (self.MAINDEST, self.EXTRA))

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

		if file_found:
			cmdlist.append('echo "_________________________________________________\n"')
			cmdlist.append('echo "USB Image created on:" %s' %self.MAINDEST)
			cmdlist.append('echo "and there is made an extra copy on:"')
			cmdlist.append('echo %s' %self.EXTRA)
			cmdlist.append('echo "_________________________________________________\n"')
			cmdlist.append('echo " "')
			cmdlist.append('echo "\nPlease wait...almost ready! "')
			cmdlist.append('echo " "')
			cmdlist.append('echo "To restore the image:"')
			cmdlist.append('echo "Please check the manual of the receiver"')
			cmdlist.append('echo "on how to restore the image"')
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
				
				if getBrandOEM() in ("fulan"):
					cmdlist.append('mkdir -p %s/%s' % (self.TARGET, self.IMAGEFOLDER))
					cmdlist.append('cp -r %s %s/' % (self.MAINDEST, self.TARGET))
				elif self.TYPE == 'ATEMIO':
					cmdlist.append('mkdir -p %s/atemio/%s' % (self.TARGET, self.MODEL1))
					cmdlist.append('cp -r %s %s/atemio/' % (self.MAINDEST, self.TARGET))
				elif self.TYPE == 'VU':
					cmdlist.append('mkdir -p %s/vuplus_back/%s' % (self.TARGET, self.MODEL[2:]))
					cmdlist.append('cp -r %s %s/vuplus_back/' % (self.MAINDEST, self.TARGET))
				elif self.TYPE == 'VENTON':
					cmdlist.append('mkdir -p %s/venton/%s' % (self.TARGET, self.MODEL))
					cmdlist.append('cp -r %s %s/venton/' % (self.MAINDEST, self.TARGET))
				elif self.TYPE == 'VENTONECO':
					cmdlist.append('mkdir -p %s/unibox/%s' % (self.TARGET, self.MODEL))
					cmdlist.append('cp -r %s %s/unibox/' % (self.MAINDEST, self.TARGET))
				elif self.TYPE == 'SEZAM':
					cmdlist.append('mkdir -p %s/%s' % (self.TARGET, self.MODEL))
					cmdlist.append('cp -r %s %s/' % (self.MAINDEST, self.TARGET))
				elif self.TYPE == 'MICRACLE':
					cmdlist.append('mkdir -p %s/miraclebox/%s' % (self.TARGET, self.MODEL))
					cmdlist.append('cp -r %s %s/miraclebox/' % (self.MAINDEST, self.TARGET))					
				elif self.TYPE == 'GI':
					cmdlist.append('mkdir -p %s/%s' % (self.TARGET, self.MODEL))
					cmdlist.append('cp -r %s %s/' % (self.MAINDEST, self.TARGET))
				elif self.TYPE == 'GIGABLUE':
					cmdlist.append('mkdir -p %s/gigablue/%s' % (self.TARGET, self.MODEL))
					cmdlist.append('cp -r %s %s/gigablue/' % (self.MAINDEST, self.TARGET))
				elif self.TYPE == 'ODINM9':
					#cmdlist.append('mkdir -p %s/odinm9/%s' % (self.TARGET, self.MODEL))
					cmdlist.append('cp -r %s %s/' % (self.MAINDEST, self.TARGET))
				elif self.TYPE == 'ODINM7':
					#cmdlist.append('mkdir -p %s/' % (self.TARGET))
					cmdlist.append('cp -r %s %s/' % (self.MAINDEST, self.TARGET))
				elif self.TYPE == 'E3HD':
					#cmdlist.append('mkdir -p %s/' % (self.TARGET))
					cmdlist.append('cp -r %s %s/' % (self.MAINDEST, self.TARGET))
				elif self.TYPE == 'FORMULER':
					cmdlist.append('mkdir -p %s/formuler/%s' % (self.TARGET, self.MODEL))
					cmdlist.append('cp -r %s %s/formuler/' % (self.MAINDEST, self.TARGET))
				elif self.TYPE == 'MAXDIGITAL' or self.TYPE == 'OCTAGON' or self.TYPE == 'MK':
					cmdlist.append('mkdir -p %s/%s' % (self.TARGET, self.MODEL))
					cmdlist.append('cp -r %s %s/' % (self.MAINDEST, self.TARGET))
				elif self.TYPE == 'TECHNO':
					cmdlist.append('mkdir -p %s/update/%s/cfe' % (self.TARGET, self.MODEL))
					cmdlist.append('cp -r %s %s/update/%s/cfe' % (self.MAINDEST, self.TARGET, self.MODEL))
				elif self.TYPE == 'IQON':
					cmdlist.append('mkdir -p %s/update/%s/cfe' % (self.TARGET, self.MODEL))
					cmdlist.append('cp -r %s %s/update/%s/cfe' % (self.MAINDEST, self.TARGET, self.MODEL))
				elif self.TYPE == 'MUT@NT':
			                cmdlist.append('mkdir -p %s/update/%s/cfe' % (self.TARGET, self.MODEL))
			                cmdlist.append('cp -r %s %s/update/%s/cfe' % (self.MAINDEST, self.TARGET, self.MODEL))
			        elif self.TYPE == 'AX':
			                cmdlist.append('mkdir -p %s/update/%s/cfe' % (self.TARGET, self.MODEL))
			                cmdlist.append('cp -r %s %s/update/%s/cfe' % (self.MAINDEST, self.TARGET, self.MODEL))        
				elif self.TYPE == 'EDISION':
					cmdlist.append('mkdir -p %s/update/%s/cfe' % (self.TARGET, self.MODEL))
					cmdlist.append('cp -r %s %s/update/%s/cfe' % (self.MAINDEST, self.TARGET, self.MODEL))
				elif self.TYPE == 'WWIO':
					cmdlist.append('mkdir -p %s/%s' % (self.TARGET, self.MODEL))
					cmdlist.append('cp -r %s %s/' % (self.MAINDEST, self.TARGET))
				else:
					cmdlist.append('echo " "')

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
		cmdlist.append('echo " Time required for this process: %s"' %TIMELAP)
		cmdlist.append('echo "Start Zip Files from Backup please wait 1-4min!"')
		self.session.open(Console, title = self.TITLE, cmdlist = cmdlist,finishedCallback = self.doFullZip, closeOnSuccess = True)

	def doFullZip(self):
	        cmdlist = []
	        cmdlist.append(self.message)
		self.make_zipfile("opennfr-%s-%s-%s_usb.zip" % (getImageVersion(), self.MODEL, strftime("%Y-%m-%d", localtime(self.START))), self.MAINDEST1)
		cmdlist.append('echo "Build Zip Files is ready!"')
		self.session.open(Console, title = self.TITLE, cmdlist = cmdlist, closeOnSuccess = False)


	def make_zipfile(self, output_filename, source_dir):
		if getBrandOEM() in ("fulan"):
			output_zip = self.EXTRA + "/" + output_filename
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

					
	def imageInfo(self):
		AboutText = _("Full Image Backup ")
		AboutText += _("By openNFR") + "\n"
		AboutText += _("Support at") + " www.nachtfalke.biz\n\n"
		AboutText += _("[Image Info]\n")
		AboutText += _("Model: %s %s\n") % (getMachineBrand(), getMachineName())
		AboutText += _("Backup Date: %s\n") % strftime("%Y-%m-%d", localtime(self.START))

		if path.exists('/proc/stb/info/chipset'):
			if getBrandOEM() in ("fulan"):
				AboutText += _("Chipset: %s") % about.getChipSetString().lower().replace('\n','').replace('bcm','') + "\n"
			else:
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
