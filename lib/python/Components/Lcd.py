from boxbranding import getBoxType
from sys import maxint

from twisted.internet import threads
from enigma import eDBoxLCD, eTimer, eActionMap
import os
import commands

from config import config, ConfigSubsection, ConfigSelection, ConfigSlider, ConfigYesNo, ConfigNothing
from Components.SystemInfo import SystemInfo
from Tools.Directories import fileExists
from Screens.Screen import Screen
import Screens.Standby
import usb

class dummyScreen(Screen):
	skin = """<screen position="0,0" size="0,0" transparent="1">
	<widget source="session.VideoPicture" render="Pig" position="0,0" size="0,0" backgroundColor="transparent" zPosition="1"/>
	</screen>"""
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.close()

def IconCheck(session=None, **kwargs):
	if fileExists("/proc/stb/lcd/symbol_network") or fileExists("/proc/stb/lcd/symbol_usb"):
		global networklinkpoller
		networklinkpoller = IconCheckPoller()
		networklinkpoller.start()

class IconCheckPoller:
	def __init__(self):
		self.timer = eTimer()

	def start(self):
		if self.iconcheck not in self.timer.callback:
			self.timer.callback.append(self.iconcheck)
		self.timer.startLongTimer(0)

	def stop(self):
		if self.iconcheck in self.timer.callback:
			self.timer.callback.remove(self.iconcheck)
		self.timer.stop()

	def iconcheck(self):
		try:
			threads.deferToThread(self.JobTask)
		except:
			pass
		self.timer.startLongTimer(30)

	def JobTask(self):
		LinkState = 0
		if fileExists('/sys/class/net/wlan0/operstate'):
			LinkState = open('/sys/class/net/wlan0/operstate').read()
			if LinkState != 'down':
				LinkState = open('/sys/class/net/wlan0/operstate').read()
		elif fileExists('/sys/class/net/eth0/operstate'):
			LinkState = open('/sys/class/net/eth0/operstate').read()
			if LinkState != 'down':
				LinkState = open('/sys/class/net/eth0/carrier').read()
		LinkState = LinkState[:1]
		if fileExists("/proc/stb/lcd/symbol_network") and config.lcd.mode.value == '1':
			f = open("/proc/stb/lcd/symbol_network", "w")
			f.write(str(LinkState))
			f.close()
		elif fileExists("/proc/stb/lcd/symbol_network") and config.lcd.mode.value == '0':
			f = open("/proc/stb/lcd/symbol_network", "w")
			f.write('0')
			f.close()

		USBState = 0
		busses = usb.busses()
		for bus in busses:
			devices = bus.devices
			for dev in devices:
				if dev.deviceClass != 9 and dev.deviceClass != 2 and dev.idVendor > 0:
					USBState = 1
		if fileExists("/proc/stb/lcd/symbol_usb") and config.lcd.mode.value == '1':
			f = open("/proc/stb/lcd/symbol_usb", "w")
			f.write(str(USBState))
			f.close()
		elif fileExists("/proc/stb/lcd/symbol_usb") and config.lcd.mode.value == '0':
			f = open("/proc/stb/lcd/symbol_usb", "w")
			f.write('0')
			f.close()

		self.timer.startLongTimer(30)

class LCD:
	def __init__(self):
		pass

	def setBright(self, value):
		value *= 255
		value /= 10
		if value > 255:
			value = 255
		eDBoxLCD.getInstance().setLCDBrightness(value)

	def setContrast(self, value):
		value *= 63
		value /= 20
		if value > 63:
			value = 63
		eDBoxLCD.getInstance().setLCDContrast(value)

	def setInverted(self, value):
		if value:
			value = 255
		eDBoxLCD.getInstance().setInverted(value)

	def setFlipped(self, value):
		eDBoxLCD.getInstance().setFlipped(value)
		
	def setScreenShot(self, value):
 		eDBoxLCD.getInstance().setDump(value)

	def isOled(self):
		return eDBoxLCD.getInstance().isOled()

	def setMode(self, value):
		if fileExists("/proc/stb/lcd/show_symbols"):
			print 'setLCDMode',value
			f = open("/proc/stb/lcd/show_symbols", "w")
			f.write(value)
			f.close()
		if config.lcd.mode.value == "0":
			if fileExists("/proc/stb/lcd/symbol_hdd"):
				f = open("/proc/stb/lcd/symbol_hdd", "w")
				f.write("0")
				f.close()
			if fileExists("/proc/stb/lcd/symbol_hddprogress"):
				f = open("/proc/stb/lcd/symbol_hddprogress", "w")
				f.write("0")
				f.close()
			if fileExists("/proc/stb/lcd/symbol_network"):
				f = open("/proc/stb/lcd/symbol_network", "w")
				f.write("0")
				f.close()
			if fileExists("/proc/stb/lcd/symbol_signal"):
				f = open("/proc/stb/lcd/symbol_signal", "w")
				f.write("0")
				f.close()
			if fileExists("/proc/stb/lcd/symbol_timeshift"):
				f = open("/proc/stb/lcd/symbol_timeshift", "w")
				f.write("0")
				f.close()
			if fileExists("/proc/stb/lcd/symbol_tv"):
				f = open("/proc/stb/lcd/symbol_tv", "w")
				f.write("0")
				f.close()
			if fileExists("/proc/stb/lcd/symbol_usb"):
				f = open("/proc/stb/lcd/symbol_usb", "w")
				f.write("0")
				f.close()

	def setPower(self, value):
		if fileExists("/proc/stb/power/vfd"):
			print 'setLCDPower',value
			f = open("/proc/stb/power/vfd", "w")
			f.write(value)
			f.close()
		elif fileExists("/proc/stb/lcd/vfd"):
			print 'setLCDPower',value
			f = open("/proc/stb/lcd/vfd", "w")
			f.write(value)
			f.close()

	def setShowoutputresolution(self, value):
		if fileExists("/proc/stb/lcd/show_outputresolution"):
			print 'setLCDShowoutputresolution',value
			f = open("/proc/stb/lcd/show_outputresolution", "w")
			f.write(value)
			f.close()

	def setfblcddisplay(self, value):
		print 'setfblcddisplay',value
		f = open("/proc/stb/fb/sd_detach", "w")
		f.write(value)
		f.close()

	def setRepeat(self, value):
		if fileExists("/proc/stb/lcd/scroll_repeats"):
			print 'setLCDRepeat',value
			f = open("/proc/stb/lcd/scroll_repeats", "w")
			f.write(value)
			f.close()

	def setScrollspeed(self, value):
		if fileExists("/proc/stb/lcd/scroll_delay"):
			print 'setLCDScrollspeed',value
			f = open("/proc/stb/lcd/scroll_delay", "w")
			f.write(str(value))
			f.close()

	def setLEDNormalState(self, value):
		eDBoxLCD.getInstance().setLED(value, 0)

	def setLEDDeepStandbyState(self, value):
		eDBoxLCD.getInstance().setLED(value, 1)

	def setLEDBlinkingTime(self, value):
		eDBoxLCD.getInstance().setLED(value, 2)
		

	def setLCDMiniTVMode(self, value):
		print 'setLCDMiniTVMode',value
		if fileExists("/proc/stb/lcd/mode"):
			f = open('/proc/stb/lcd/mode', "w")
			f.write(value)
			f.close()
		elif fileExists("/proc/stb/lcd/live_enable"):
			f = open('/proc/stb/lcd/live_enable', "w")
			f.write(value)
			f.close()
		else:
			pass
		
	def setLCDMiniTVMode4k(self, value):
		print 'setLCDMiniTVMode4k',value
		f = open('/proc/stb/lcd/live_enable', "w")
		f.write(value)
		f.close()		

	def setLCDMiniTVPIPMode(self, value):
		try:
			f = open('/proc/stb/lcd/live_decoder', "w")
			f.write(value)
			f.close()
			print 'setLCDMiniTVPIPMode',value
		except:
			pass

	def setLCDMiniTVFPS(self, value):
		print 'setLCDMiniTVFPS',value
		try:
			f = open('/proc/stb/lcd/fps', "w")
			f.write("%d \n" % value)
			f.close()
		except:
			pass	

def leaveStandby():
	config.lcd.bright.apply()
	config.lcd.ledbrightness.apply()
	config.lcd.ledbrightnessdeepstandby.apply()

def standbyCounterChanged(configElement):
	from Screens.Standby import inStandby
	inStandby.onClose.append(leaveStandby)
	config.lcd.standby.apply()
	config.lcd.ledbrightnessstandby.apply()
	config.lcd.ledbrightnessdeepstandby.apply()

def InitLcd():
	if getBoxType() in ('lunix','purehdse','vipert2c','evoslimse','evoslimt2c','valalinux','tmtwin4k','tmnanom3','mbmicrov2','revo4k','force3uhd','force2nano','evoslim','wetekplay', 'wetekplay2', 'wetekhub', 'ultrabox', 'novaip', 'dm520', 'dm525', 'purehd', 'mutant11', 'xpeedlxpro', 'zgemmai55', 'sf98', 'et7x00mini', 'xpeedlxcs2', 'xpeedlxcc', 'e4hd', 'e4hdhybrid', 'mbmicro', 'beyonwizt2', 'amikomini', 'dynaspark', 'amiko8900', 'sognorevolution', 'arguspingulux', 'arguspinguluxmini', 'arguspinguluxplus', 'sparkreloaded', 'sabsolo', 'sparklx', 'gis8120', 'gb800se', 'gb800solo', 'gb800seplus', 'gbultrase', 'gbipbox', 'tmsingle', 'tmnano2super', 'iqonios300hd', 'iqonios300hdv2', 'optimussos1plus', 'optimussos1', 'vusolo', 'et4x00', 'et5x00', 'et6x00', 'et7000', 'et7100', 'mixosf7', 'mixoslumi', 'gbx1', 'gbx2', 'gbx3', 'gbx3h'):
		detected = False
	else:
		detected = eDBoxLCD.getInstance().detected()
	SystemInfo["Display"] = detected
	config.lcd = ConfigSubsection();

	if fileExists("/proc/stb/lcd/mode"):
		f = open("/proc/stb/lcd/mode", "r")
		can_lcdmodechecking = f.read().strip().split(" ")
		f.close()
	elif fileExists("/proc/stb/lcd/live_enable"):
		f = open("/proc/stb/lcd/live_enable", "r")
		can_lcdmodechecking = f.read().strip().split(" ")
		f.close()
        else:
		can_lcdmodechecking = False
	SystemInfo["LCDMiniTV"] = can_lcdmodechecking

	if detected:
		ilcd = LCD()
		if can_lcdmodechecking and getBoxType() not in ('vusolo4k', 'e4hdultra'):
			def setLCDModeMinitTV(configElement):
				try:
					print 'setLCDModeMinitTV',configElement.value
					f = open("/proc/stb/lcd/mode", "w")
					f.write(configElement.value)
					f.close()
				except:
					pass
			def setMiniTVFPS(configElement):
				try:
					print 'setMiniTVFPS',configElement.value
					f = open("/proc/stb/lcd/fps", "w")
					f.write("%d \n" % configElement.value)
					f.close()
				except:
					pass
			def setLCDModePiP(configElement):
				pass
			
			def setLCDScreenshot(configElement):
 				ilcd.setScreenShot(configElement.value);			

			if getBoxType() in ('gbquad4k', 'gbue4k'):
				config.lcd.modepip = ConfigSelection(choices={
						"0": _("off"),
						"4": _("PIP"),
						"6": _("PIP with OSD")},
						default = "0")		
			else:
				config.lcd.modepip = ConfigSelection(choices={
						"0": _("off"),
						"5": _("PIP"),
						"7": _("PIP with OSD")},
						default = "0")

			if config.misc.boxtype.value in ( 'gbquad', 'gbquadplus', 'gbquad4k', 'gbue4k'):
				config.lcd.modepip.addNotifier(setLCDModePiP)
			else:
				config.lcd.modepip = ConfigNothing()
				
			config.lcd.screenshot = ConfigYesNo(default=False)
 			config.lcd.screenshot.addNotifier(setLCDScreenshot)	

			if getBoxType() in ('gbquad4k', 'gbue4k'):
				#  (0:normal, 1:video0, 2:fb, 3:vide0+fb, 4:video1, 5:vide0+video1, 6:video1+fb, 7:video0+video1+fb)
				config.lcd.modeminitv = ConfigSelection(default = "0", choices=[
						("0", _("normal")),
						("1", _("MiniTV - video0")),
						("3", _("MiniTV with OSD - video0+fb")),
						("2", _("OSD - fb")),
						("4", _("MiniTV - video1")),
						("6", _("MiniTV with OSD - video1+fb")),
						("5", _("MiniTV - video0+video1")),
						("7", _("MiniTV with OSD - video0+video1+fb"))]) 
			else:
				config.lcd.modeminitv = ConfigSelection(choices={
						"0": _("normal"),
						"1": _("MiniTV"),
						"2": _("OSD"),
						"3": _("MiniTV with OSD")},
						default = "0")

			config.lcd.fpsminitv = ConfigSlider(default=30, limits=(0, 30))
			config.lcd.modeminitv.addNotifier(setLCDModeMinitTV)
			config.lcd.screenshot = ConfigNothing()
			config.lcd.fpsminitv.addNotifier(setMiniTVFPS)
		elif can_lcdmodechecking:
			def setLCDModeMinitTV4k(configElement):
				try:
					print 'setLCDModeMinitTV',configElement.value
					f = open("/proc/stb/lcd/live_enable", "w")
					f.write(configElement.value)
					f.close()
				except:
					pass
			def setMiniTVFPS(configElement):
				pass
			def setLCDModePiP(configElement):
				try:
					print 'setMiniTVPIP',configElement.value
					f = open("/proc/stb/lcd/live_decoder", "w")
					f.write(configElement.value)
					f.close()
				except:
					pass
				pass
			
			def setLCDScreenshot(configElement):
 				ilcd.setScreenShot(configElement.value);
				
			if getBoxType() in ('e4hdultra'):
				config.lcd.modepip = ConfigSelection(choices={
						"0": _("off"),
						"1": _("on"),},
						default = "0")
			if config.misc.boxtype.value in ('e4hdultra'):
				config.lcd.modepip.addNotifier(setLCDModePiP)
			else:
				config.lcd.modepip = ConfigNothing()
				
			config.lcd.screenshot = ConfigYesNo(default=False)
 			config.lcd.screenshot.addNotifier(setLCDScreenshot)					
			if getBoxType() in ('e4hdultra'):
				config.lcd.modeminitv4k = ConfigSelection(choices={
						"disable": _("normal"),
						"enable": _("MiniTV")},
						default = "disable")
			else:
				config.lcd.modeminitv4k = ConfigSelection(choices={
						"disable": _("normal"),
						"enable": _("MiniTV")},
						default = "0")
			
			config.lcd.modeminitv4k.addNotifier(setLCDModeMinitTV4k)
			config.lcd.screenshot = ConfigNothing()
	
		else:
			config.lcd.modeminitv = ConfigNothing()
			config.lcd.modeminitv4k = ConfigNothing()
			config.lcd.screenshot = ConfigNothing()
			config.lcd.fpsminitv = ConfigNothing()

		config.lcd.scroll_speed = ConfigSelection(default = "300", choices = [
			("500", _("slow")),
			("300", _("normal")),
			("100", _("fast"))])
		config.lcd.scroll_delay = ConfigSelection(default = "10000", choices = [
			("10000", "10 " + _("seconds")),
			("20000", "20 " + _("seconds")),
			("30000", "30 " + _("seconds")),
			("60000", "1 " + _("minute")),
			("300000", "5 " + _("minutes")),
			("noscrolling", _("off"))])
	
		def setLCDbright(configElement):
			ilcd.setBright(configElement.value);

		def setLCDcontrast(configElement):
			ilcd.setContrast(configElement.value);

		def setLCDinverted(configElement):
			ilcd.setInverted(configElement.value);

		def setLCDflipped(configElement):
			ilcd.setFlipped(configElement.value);

		def setLCDmode(configElement):
			ilcd.setMode(configElement.value);

		def setLCDpower(configElement):
			ilcd.setPower(configElement.value);

		def setfblcddisplay(configElement):
			ilcd.setfblcddisplay(configElement.value);

		def setLCDshowoutputresolution(configElement):
			ilcd.setShowoutputresolution(configElement.value);
			
		def setLCDminitvmode(configElement):
			ilcd.setLCDMiniTVMode(configElement.value)
			
		def setLCDminitvmode4k(configElement):
			ilcd.setLCDMiniTVMode4k(configElement.value)			

		def setLCDminitvpipmode(configElement):
			ilcd.setLCDMiniTVPIPMode(configElement.value)

		def setLCDminitvfps(configElement):
			ilcd.setLCDMiniTVFPS(configElement.value)			

		def setLCDrepeat(configElement):
			ilcd.setRepeat(configElement.value);

		def setLCDscrollspeed(configElement):
			ilcd.setScrollspeed(configElement.value);

		if fileExists("/proc/stb/lcd/symbol_hdd"):
			f = open("/proc/stb/lcd/symbol_hdd", "w")
			f.write("0")
			f.close()
		if fileExists("/proc/stb/lcd/symbol_hddprogress"):
			f = open("/proc/stb/lcd/symbol_hddprogress", "w")
			f.write("0")
			f.close()

		def setLEDnormalstate(configElement):
			ilcd.setLEDNormalState(configElement.value);

		def setLEDdeepstandby(configElement):
			ilcd.setLEDDeepStandbyState(configElement.value);

		def setLEDblinkingtime(configElement):
			ilcd.setLEDBlinkingTime(configElement.value);

		def setPowerLEDstandbystate(configElement):
			if fileExists("/proc/stb/power/standbyled"):
				f = open("/proc/stb/power/standbyled", "w")
				f.write(configElement.value)
				f.close()

		config.usage.lcd_standbypowerled = ConfigSelection(default = "on", choices = [("off", _("Off")), ("on", _("On"))])
		config.usage.lcd_standbypowerled.addNotifier(setPowerLEDstandbystate)
		

		if getBoxType() in ('dm900', 'dm920', 'e4hdultra'):
			standby_default = 4
		elif getBoxType() in ('spycat4kmini', 'osmega'):
			standby_default = 10
		else:
			standby_default = 0

		ilcd = LCD()

		if not ilcd.isOled():
			config.lcd.contrast = ConfigSlider(default=5, limits=(0, 20))
			config.lcd.contrast.addNotifier(setLCDcontrast);
		else:
			config.lcd.contrast = ConfigNothing()
			standby_default = 1

		if getBoxType() in ('mixosf5', 'mixosf5mini', 'gi9196m', 'gi9196lite', 'zgemmas2s', 'zgemmash1', 'zgemmash2'):
			config.lcd.standby = ConfigSlider(default=standby_default, limits=(0, 4))
			config.lcd.bright = ConfigSlider(default=4, limits=(0, 4))
		else:
			config.lcd.standby = ConfigSlider(default=standby_default, limits=(0, 10))
			config.lcd.bright = ConfigSlider(default=5, limits=(0, 10))
		config.lcd.standby.addNotifier(setLCDbright);
		config.lcd.standby.apply = lambda : setLCDbright(config.lcd.standby)
		config.lcd.bright.addNotifier(setLCDbright);
		config.lcd.bright.apply = lambda : setLCDbright(config.lcd.bright)
		config.lcd.bright.callNotifiersOnSaveAndCancel = True

		config.lcd.invert = ConfigYesNo(default=False)
		config.lcd.invert.addNotifier(setLCDinverted);

		config.lcd.flip = ConfigYesNo(default=False)
		config.lcd.flip.addNotifier(setLCDflipped);
		
		if SystemInfo["LcdLiveTV"]:
			def lcdLiveTvChanged(configElement):
				if getBoxType() in ('e4hdultra'):
					open(SystemInfo["LcdLiveTV"], "w").write(configElement.value and "disable" or "enable")
				else:
					open(SystemInfo["LcdLiveTV"], "w").write(configElement.value and "0" or "1")
				from Screens.InfoBar import InfoBar
				InfoBarInstance = InfoBar.instance
				InfoBarInstance and InfoBarInstance.session.open(dummyScreen)
				setLCDLiveTv(configElement.value)
				configElement.save()

			config.lcd.showTv = ConfigYesNo(default = False)
			config.lcd.showTv.addNotifier(lcdLiveTvChanged)
			#try Ultimo4k
			if "live_enable" in SystemInfo["LcdLiveTV"]:
				config.misc.standbyCounter.addNotifier(standbyCounterChangedLCDLiveTV, initial_call = False)

		if SystemInfo["LCDMiniTV4k"]:
		        SystemInfo["LCDMiniTV"] = False
			if getBoxType() in ('e4hdultra'):
				config.lcd.minitvmode4k = ConfigSelection([("disable", _("normal")), ("enable", _("MiniTV"))], "disable")
				config.lcd.minitvmode4k.addNotifier(setLCDminitvmode4k)
			else:
				config.lcd.minitvmode4k = ConfigSelection([("disable", _("normal")), ("enable", _("MiniTV"))], "0")
				config.lcd.minitvmode4k.addNotifier(setLCDminitvmode4k)
				
		if SystemInfo["LCDMiniTV"] and config.misc.boxtype.value not in ( 'gbquad', 'gbquadplus', 'gbquad4k', 'gbue4k'):
			config.lcd.minitvmode = ConfigSelection([("0", _("normal")), ("1", _("MiniTV")), ("2", _("OSD")), ("3", _("MiniTV with OSD"))], "0")
			config.lcd.minitvmode.addNotifier(setLCDminitvmode)
			config.lcd.minitvpipmode = ConfigSelection([("0", _("off")), ("5", _("PIP")), ("7", _("PIP with OSD"))], "0")
			config.lcd.minitvpipmode.addNotifier(setLCDminitvpipmode)
			config.lcd.minitvfps = ConfigSlider(default=30, limits=(0, 30))
			config.lcd.minitvfps.addNotifier(setLCDminitvfps)		

		if getBoxType() in ('mixosf5', 'mixosf5mini', 'gi9196m', 'gi9196lite', 'zgemmas2s', 'gi9196lite', 'zgemmash1', 'zgemmash2'):
			config.lcd.scrollspeed = ConfigSlider(default = 150, increment = 10, limits = (0, 500))
			config.lcd.scrollspeed.addNotifier(setLCDscrollspeed);
			config.lcd.repeat = ConfigSelection([("0", _("None")), ("1", _("1X")), ("2", _("2X")), ("3", _("3X")), ("4", _("4X")), ("500", _("Continues"))], "3")
			config.lcd.repeat.addNotifier(setLCDrepeat);
			config.lcd.hdd = ConfigNothing()
			config.lcd.mode = ConfigNothing()
		elif fileExists("/proc/stb/lcd/scroll_delay") and getBoxType() not in ('ixussone', 'ixusszero'):
			config.lcd.hdd = ConfigSelection([("0", _("No")), ("1", _("Yes"))], "1")
			config.lcd.scrollspeed = ConfigSlider(default = 150, increment = 10, limits = (0, 500))
			config.lcd.scrollspeed.addNotifier(setLCDscrollspeed);
			config.lcd.repeat = ConfigSelection([("0", _("None")), ("1", _("1X")), ("2", _("2X")), ("3", _("3X")), ("4", _("4X")), ("500", _("Continues"))], "3")
			config.lcd.repeat.addNotifier(setLCDrepeat);
			config.lcd.mode = ConfigSelection([("0", _("No")), ("1", _("Yes"))], "1")
			config.lcd.mode.addNotifier(setLCDmode);
		else:
			config.lcd.mode = ConfigNothing()
			config.lcd.repeat = ConfigNothing()
			config.lcd.scrollspeed = ConfigNothing()
			config.lcd.hdd = ConfigNothing()

		if fileExists("/proc/stb/power/vfd") or fileExists("/proc/stb/lcd/vfd"):
			config.lcd.power = ConfigSelection([("0", _("No")), ("1", _("Yes"))], "1")
			config.lcd.power.addNotifier(setLCDpower);
		else:
			config.lcd.power = ConfigNothing()

		if fileExists("/proc/stb/fb/sd_detach"):
			config.lcd.fblcddisplay = ConfigSelection([("1", _("No")), ("0", _("Yes"))], "1")
			config.lcd.fblcddisplay.addNotifier(setfblcddisplay);
		else:
			config.lcd.fblcddisplay = ConfigNothing()

		if fileExists("/proc/stb/lcd/show_outputresolution"):
			config.lcd.showoutputresolution = ConfigSelection([("0", _("No")), ("1", _("Yes"))], "1")
			config.lcd.showoutputresolution.addNotifier(setLCDshowoutputresolution);
		else:
			config.lcd.showoutputresolution = ConfigNothing()

		if getBoxType() == 'vuultimo':
			config.lcd.ledblinkingtime = ConfigSlider(default = 5, increment = 1, limits = (0,15))
			config.lcd.ledblinkingtime.addNotifier(setLEDblinkingtime);
			config.lcd.ledbrightnessdeepstandby = ConfigSlider(default = 1, increment = 1, limits = (0,15))
			config.lcd.ledbrightnessdeepstandby.addNotifier(setLEDnormalstate);
			config.lcd.ledbrightnessdeepstandby.addNotifier(setLEDdeepstandby);
			config.lcd.ledbrightnessdeepstandby.apply = lambda : setLEDdeepstandby(config.lcd.ledbrightnessdeepstandby)
			config.lcd.ledbrightnessstandby = ConfigSlider(default = 1, increment = 1, limits = (0,15))
			config.lcd.ledbrightnessstandby.addNotifier(setLEDnormalstate);
			config.lcd.ledbrightnessstandby.apply = lambda : setLEDnormalstate(config.lcd.ledbrightnessstandby)
			config.lcd.ledbrightness = ConfigSlider(default = 3, increment = 1, limits = (0,15))
			config.lcd.ledbrightness.addNotifier(setLEDnormalstate);
			config.lcd.ledbrightness.apply = lambda : setLEDnormalstate(config.lcd.ledbrightness)
			config.lcd.ledbrightness.callNotifiersOnSaveAndCancel = True
		else:
			def doNothing():
				pass
			config.lcd.ledbrightness = ConfigNothing()
			config.lcd.ledbrightness.apply = lambda : doNothing()
			config.lcd.ledbrightnessstandby = ConfigNothing()
			config.lcd.ledbrightnessstandby.apply = lambda : doNothing()
			config.lcd.ledbrightnessdeepstandby = ConfigNothing()
			config.lcd.ledbrightnessdeepstandby.apply = lambda : doNothing()
			config.lcd.ledblinkingtime = ConfigNothing()
	else:
		def doNothing():
			pass
		config.lcd.contrast = ConfigNothing()
		config.lcd.bright = ConfigNothing()
		config.lcd.standby = ConfigNothing()
		config.lcd.bright.apply = lambda : doNothing()
		config.lcd.standby.apply = lambda : doNothing()
		config.lcd.power = ConfigNothing()
		config.lcd.fblcddisplay = ConfigNothing()
		config.lcd.mode = ConfigNothing()
		config.lcd.repeat = ConfigNothing()
		config.lcd.scrollspeed = ConfigNothing()
		config.lcd.scroll_speed = ConfigSelection(choices = [("300", _("normal"))])
		config.lcd.scroll_delay = ConfigSelection(choices = [("noscrolling", _("off"))])
		config.lcd.showoutputresolution = ConfigNothing()
		config.lcd.ledbrightness = ConfigNothing()
		config.lcd.ledbrightness.apply = lambda : doNothing()
		config.lcd.ledbrightnessstandby = ConfigNothing()
		config.lcd.ledbrightnessstandby.apply = lambda : doNothing()
		config.lcd.ledbrightnessdeepstandby = ConfigNothing()
		config.lcd.ledbrightnessdeepstandby.apply = lambda : doNothing()
		config.lcd.ledblinkingtime = ConfigNothing()

	config.misc.standbyCounter.addNotifier(standbyCounterChanged, initial_call = False)
def setLCDLiveTv(value):
	if "live_enable" in SystemInfo["LcdLiveTV"]:
		open(SystemInfo["LcdLiveTV"], "w").write(value and "enable" or "disable")
	else:
		open(SystemInfo["LcdLiveTV"], "w").write(value and "0" or "1")
	if not value:
		from Screens.InfoBar import InfoBar
		InfoBarInstance = InfoBar.instance
		InfoBarInstance and InfoBarInstance.session.open(dummyScreen)

def leaveStandbyLCDLiveTV():
	if config.lcd.showTv.value:
		setLCDLiveTv(True)

def standbyCounterChangedLCDLiveTV(dummy):
	if config.lcd.showTv.value:
		from Screens.Standby import inStandby
		if leaveStandbyLCDLiveTV not in inStandby.onClose:
			inStandby.onClose.append(leaveStandbyLCDLiveTV)
		setLCDLiveTv(False)
