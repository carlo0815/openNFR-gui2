# -*- coding: utf-8 -*-
from __future__ import print_function
from Plugins.Plugin import PluginDescriptor
from Components.Harddisk import harddiskmanager
from twisted.internet.protocol import Protocol, Factory
from Components.config import config
import os
from glob import glob
from Components.Console import Console
from time import sleep
import six

hotplugNotifier = []

def processHotplugData(self, v):
        self.Console = Console()
	print("hotplug:", v)
	action = v.get("ACTION")
	device = v.get("DEVPATH")
	physdevpath = v.get("PHYSDEVPATH")
	media_state = v.get("X_E2_MEDIA_STATUS")

	dev = device.split('/')[-1]

	if action == "add":
		error, blacklisted, removable, is_cdrom, partitions, medium_found = harddiskmanager.addHotplugPartition(dev, physdevpath)
	elif action == "remove":
	        usbmount = harddiskmanager.getMountpoint(dev)
	        if os.path.isfile("/tmp/usbsoftcam"):
	                fobj = open("/tmp/usbsoftcam")
	                for line in fobj:
	                    spath = line.rstrip()
	                fobj.close()
	        	if spath == usbmount:
                        	self.actcam = config.NFRSoftcam.actcam.value
                        	if ".usb" in self.actcam:
                        		self.Console.ePopen("killall %s" % self.actcam)
                        	for fdelete in glob ('/usr/emu/*.usb'):
					os.remove (fdelete)
                		for fdelete in glob ('/usr/keys/*'):
                			if os.path.islink(fdelete):
						os.unlink(fdelete)
				sleep(1.00)		
                        	harddiskmanager.removeHotplugPartition(dev)
                        	self.Console.ePopen("umount %s" % usbmount)		
			else:
                        	harddiskmanager.removeHotplugPartition(dev)
		else:
                       	harddiskmanager.removeHotplugPartition(dev)                        	
	elif media_state is not None:
		if media_state == '1':
			harddiskmanager.removeHotplugPartition(dev)
			harddiskmanager.addHotplugPartition(dev, physdevpath)
		elif media_state == '0':
			harddiskmanager.removeHotplugPartition(dev)

	for callback in hotplugNotifier:
		try:
			callback(dev, action or media_state)
		except AttributeError:
			hotplugNotifier.remove(callback)

class Hotplug(Protocol):
	def __init__(self):
		pass

	def connectionMade(self):
		print("HOTPLUG connection!")
		self.received = ""

	def dataReceived(self, data):
		print("hotplug:", data)
		self.received += data
		print("complete", self.received)

	def connectionLost(self, reason):
		print("HOTPLUG connection lost!")
		data = self.received.split('\0')[:-1]
		v = {}
		for x in data:
			i = x.find('=')
			var, val = x[:i], x[i+1:]
			v[var] = val
		processHotplugData(self, v)

def autostart(reason, **kwargs):
	if reason == 0:
		print("starting hotplug handler")
		from twisted.internet import reactor
		import os
		try:
			os.remove("/tmp/hotplug.socket")
		except OSError:
			pass
		factory = Factory()
		factory.protocol = Hotplug
		reactor.listenUNIX("/tmp/hotplug.socket", factory)

def Plugins(**kwargs):
	return PluginDescriptor(name = "Hotplug", description = "listens to hotplug events", where = PluginDescriptor.WHERE_AUTOSTART, needsRestart = True, fnc = autostart)
