# Embedded file name: /usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/GlobalFunctions.py
from enigma import eRect, eServiceReference, iServiceInformation, iPlayableService, getDesktop
from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Tools.Directories import resolveFilename, pathExists, fileExists, SCOPE_MEDIA
from Components.Sources.List import List
from Components.ServicePosition import ServicePositionGauge
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Sources.StaticText import StaticText
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *
from Components.FileList import FileList
from _ctypes import *
import os, re
from os import path as os_path

class Showiframe:

	def __init__(self):
		lib = '/usr/lib/'
		if fileExists(lib + 'libshowiframe.so.0.0.0'):
			self.showiframe = dlopen(lib + 'libshowiframe.so.0.0.0')
		try:
			self.showSinglePic = dlsym(self.showiframe, 'showSinglePic')
			self.finishShowSinglePic = dlsym(self.showiframe, 'finishShowSinglePic')
		except OSError as e:
			self.showSinglePic = dlsym(self.showiframe, '_Z13showSinglePicPKc')
			self.finishShowSinglePic = dlsym(self.showiframe, '_Z19finishShowSinglePicv')

	def showStillpicture(self, pic):
		call_function(self.showSinglePic, (pic,))

	def finishStillPicture(self):
		call_function(self.finishShowSinglePic, ())
