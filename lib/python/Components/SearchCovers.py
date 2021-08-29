#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Plugins.Plugin import PluginDescriptor

from Components.ActionMap import *
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmap, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap
from Components.AVSwitch import AVSwitch
from Components.PluginComponent import plugins
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.GUIComponent import GUIComponent
from Components.Sources.List import List
from Components.MenuList import MenuList
from Components.FileList import FileList, FileEntryComponent

from Tools.Directories import SCOPE_CURRENT_SKIN, resolveFilename, fileExists
from Tools.LoadPixmap import LoadPixmap
from Tools.BoundFunction import boundFunction
from Tools.Directories import pathExists, fileExists, SCOPE_SKIN_IMAGE, resolveFilename

from enigma import RT_HALIGN_LEFT, eListboxPythonMultiContent, eServiceReference, eServiceCenter, gFont
from enigma import eListboxPythonMultiContent, eListbox, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, loadPNG, RT_WRAP, eConsoleAppContainer, eServiceCenter, eServiceReference, getDesktop, loadPic, loadJPG, RT_VALIGN_CENTER, gPixmapPtr, ePicLoad, eTimer

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard

from twisted.web.client import getPage
from twisted.web.client import downloadPage
from twisted.web import client, error as weberror
from twisted.internet import reactor
from twisted.internet import defer
from urllib import urlencode
import sys, os, re, shutil, time
from threading import Thread
from os import listdir as os_listdir, path as os_path
from re import compile
import re

try:
	from enigma import eMediaDatabase
	isDreamOS = True
except:
	try:
		file = open("/proc/stb/info/model", "r")
		dev = file.readline().strip()
		file.close()
		if dev == "dm7080":
			isDreamOS = True
		elif dev == "dm820":
			isDreamOS = True
		else:
			isDreamOS = False
	except:
			isDreamOS = False

def getCoverPath():
	blockList = ['hdd','cf','usb','sdcard']
	dirList = os_listdir("/media")
	coverPaths = ['/usr/share/enigma2/cover/', '/data/cover/', '/media/cf/cover/', '/media/usb/cover/', '/media/sdcard/cover/', '/media/hdd/cover/']

	if fileExists("/proc/mounts"):
		mountsFile = open("/proc/mounts" ,"r")
		for line in mountsFile:
			entry = line.split()
			if entry[2] in ["nfs", "nfs4", "smbfs", "cifs"]:
				if entry[1].startswith("/media/"):
					blockList.append(entry[1][7:])
		mountsFile.close()

	for dir in dirList:
		if dir in blockList:
			print(dir, blockList)
			continue
		if os_path.ismount("/media/%s" %(dir)) or (os_path.islink("/media/%s" %(dir)) and os_path.ismount(os_path.realpath("/media/%s" %(dir)))):
			path = "/media/%s/cover/" % (dir)
			coverPaths.append(path)
	return coverPaths

pname = "Find MovieList Covers"
pversion = "0.5 OpenNfr-mod"

config.movielist.cover = ConfigSubsection()
config.movielist.cover.themoviedb_coversize = ConfigSelection(default="w185", choices = ["w92", "w185", "w500", "original"])
config.movielist.cover.followsymlink = ConfigYesNo(default = False)
config.movielist.cover.getdescription = ConfigYesNo(default = False)
config.movielist.cover.bgtimer = ConfigYesNo(default = False)
config.movielist.cover.bgtime = ConfigInteger(3, (1,24))
config.movielist.cover.savestyle = ConfigSelection(default="movielist", choices = ["movielist", "opennfr"])
config.movielist.cover.coverpath = ConfigSelection(default = "/media/hdd/cover/", choices = getCoverPath())
config.movielist.cover.scanpath = ConfigText(default = "/media/hdd/movie/", fixed_size = False)

fileExtensionsRemove = "(.avi|.mkv|.divx|.f4v|.flv|.img|.iso|.m2ts|.m4v|.mov|.mp4|.mpeg|.mpg|.mts|.vob|.wmv)"

def cleanFile(text):
	cutlist = ['x264','720p','1080p','1080i','PAL','GERMAN','ENGLiSH','WS','DVDRiP','UNRATED','RETAIL','Web-DL','DL','LD','MiC','MD','DVDR','BDRiP','BLURAY','DTS','UNCUT','ANiME',
				'AC3MD','AC3','AC3D','TS','DVDSCR','COMPLETE','INTERNAL','DTSD','XViD','DIVX','DUBBED','LINE.DUBBED','DD51','DVDR9','DVDR5','h264','AVC',
				'WEBHDTVRiP','WEBHDRiP','WEBRiP','WEBHDTV','WebHD','HDTVRiP','HDRiP','HDTV','ITUNESHD','REPACK','SYNC']
	#text = text.replace('.wmv','').replace('.flv','').replace('.ts','').replace('.m2ts','').replace('.mkv','').replace('.avi','').replace('.mpeg','').replace('.mpg','').replace('.iso','').replace('.mp4','').replace('.jpg','').replace('.txt','')
	text = re.sub(fileExtensionsRemove + "$", '', text)
	for word in cutlist:
		text = re.sub('(\_|\-|\.|\+|\s)'+word+'(\_|\-|\.|\+|\s)','+', text, flags=re.I)
	text = text.replace('.',' ').replace('-',' ').replace('_',' ').replace('+','')
	return text

class BackgroundCoverScanner(Thread):

	def __init__(self, session):
		assert not BackgroundCoverScanner.instance, "only one MovieDataUpdater instance is allowed!"
		BackgroundCoverScanner.instance = self # set instance
		self.session = session
		self.scanning = False
		self.bgTimerRunning = False
		self.fileExtensions = [".avi",".mkv",".divx",".f4v",".flv",".img",".iso",".m2ts",".m4v",".mov",".mp4",".mpeg",".mpg",".mts",".vob",".wmv"]
		Thread.__init__(self)

	def startTimer(self):
		if config.movielist.cover.bgtimer.value:
			self.bgTimer = eTimer()
			if isDreamOS:
				self.bgTimer_conn = self.bgTimer.timeout.connect(self.getFileList)
			else:
				self.bgTimer.callback.append(self.getFileList)
			self.bgTimer.start(3600000 * int(config.movielist.cover.bgtime.value))
			self.bgTimerRunning = True
			print( "----------------------- S t a r t - T i m e r -------------------------")

	def stopTimer(self):
		if self.bgTimerRunning:
			if not config.movielist.cover.bgtimer.value:
				self.bgTimer.stop()
				self.bgTimerRunning = False
				print( "----------------------- S t o p - T i m e r -------------------------")

	def setCallbacks(self, callback_infos, callback_found, callback_notfound, callback_error, callback_menulist, callback_finished):
		# self.msgCallback, self.foundCallback, self.notFoundCallback, self.errorCallback, self.listCallback, self.msgDone
		self.callback_infos = callback_infos
		self.callback_found = callback_found
		self.callback_notfound = callback_notfound
		self.callback_error = callback_error
		self.callback_menulist = callback_menulist
		self.callback_finished = callback_finished

	def getFileList(self, background=True):
		self.background = background
		if not self.scanning:
			print( "----------------------- Cover Background Scanner -------------------------")
			print( "Scan Path: %s" % config.movielist.cover.scanpath.value)
			self.scanning = True
			if config.movielist.cover.savestyle.value == "opennfr":
				if not pathExists(config.movielist.cover.coverpath.value):
					shutil.os.mkdir(config.movielist.cover.coverpath.value)
			if not self.background:
				self.callback_infos("Scanning: '%s'" % str(config.movielist.cover.scanpath.value))
			data = []
			symlinks_dupe = []
			for root, dirs, files in os.walk(config.movielist.cover.scanpath.value, topdown=False, onerror=None, followlinks=config.movielist.cover.followsymlink.value):
				if not root.endswith('/'):
					root += "/"
				slink = os.path.realpath(root)
				if not slink in symlinks_dupe:
					symlinks_dupe.append(slink)
				else:
					break
				for file in files:
					filename_org = os.path.join(root, file)
					if any([file.endswith(x) for x in self.fileExtensions]):
						if config.movielist.cover.savestyle.value == "opennfr":
							filename = self.getMovieSaveFile(file)
							if not filename is None:
								filename = "%s%s.jpg" % (config.movielist.cover.coverpath.value, filename)
							else:
								continue
						else:
							filename = re.sub(fileExtensionsRemove + "$", '.jpg', filename_org)
						if not fileExists(filename):
							if os.path.isdir(filename_org):
								url = 'http://api.themoviedb.org/3/search/movie?api_key=8789cfd3fbab7dccf1269c3d7d867aff&query=%s&language=de' % file.replace(' ','%20')
								data.append(('dir', 'movie', filename, file, url, None, None))
							else:
								#cleanTitle = re.sub('\W.*?([0-9][0-9][0-9][0-9])', '', file)
								# Remove Year
								cleanTitle = re.sub('([0-9][0-9][0-9][0-9])', '', file)
								# Remove fileExtensions
								cleanTitle = cleanFile(cleanTitle)
								if re.search('[Ss][0-9]+[Ee][0-9]+', file) is not None:
									season = None
									episode = None
									seasonEpisode = re.findall('.*?[Ss]([0-9]+)[Ee]([0-9]+)', cleanTitle, re.S|re.I)
									if seasonEpisode:
										(season, episode) = seasonEpisode[0]
									name2 = re.sub('[Ss][0-9]+[Ee][0-9]+.*[a-zA-Z0-9_]+','', cleanTitle, flags=re.S|re.I)
									url = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s&language=de' % name2.replace(' ','%20')
									data.append(('file', 'serie', filename, name2, url, season, episode))
								else:
									url = 'http://api.themoviedb.org/3/search/movie?api_key=8789cfd3fbab7dccf1269c3d7d867aff&query=%s&language=de' % cleanTitle.replace(' ','%20')
									data.append(('file', 'movie', filename, cleanTitle, url, None, None))

					elif file.endswith('.ts'):
						metaName = None
						#cleanTitle = re.sub('^.*? - .*? - ', '', file)
						#cleanTitle = re.sub('[.]ts', '', cleanTitle)
						if fileExists(filename_org+".meta"):
							metaName = open(filename_org+".meta",'r').readlines()[1].rstrip("\n").rstrip("\t").rstrip("\r")
							if config.movielist.cover.savestyle.value == "opennfr":
								filename = "%s%s.jpg" % (config.movielist.cover.coverpath.value, metaName.replace(" ","_").replace(".","_"))
							else:
								filename = re.sub("\.ts$", '.jpg', filename_org)
							if not fileExists(filename):
								if metaName is not None:
									if re.search('[Ss][0-9]+[Ee][0-9]+', metaName) is not None:
									#if metaName is not None:
										cleanTitle = re.sub('[Ss][0-9]+[Ee][0-9]+.*[a-zA-Z0-9_]+','', metaName, flags=re.S|re.I)
										cleanTitle = cleanFile(cleanTitle)
										print( "cleanTitle:", cleanTitle)
										url = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s&language=de' % cleanTitle.replace(' ','%20')
										data.append(('file', 'serie', filename, cleanTitle, url, None, None))
									#else:
									#	url = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s&language=de' % cleanTitle.replace(' ','%20')
									#	data.append(('file', 'serie', filename, cleanTitle, url, None, None))
									else:
									#if metaName is not None:
										url = 'http://api.themoviedb.org/3/search/movie?api_key=8789cfd3fbab7dccf1269c3d7d867aff&query=%s&language=de' % metaName.replace(' ','%20')
										data.append(('file', 'movie', filename, metaName, url, None, None))
									#else:
									#	url = 'http://api.themoviedb.org/3/search/movie?api_key=8789cfd3fbab7dccf1269c3d7d867aff&query=%s&language=de' % cleanTitle.replace(' ','%20')
									#	data.append(('file', 'serie', filename, cleanTitle, url, None, None))

			self.count = len(data)
			if not self.background:
				self.callback_infos("Found %s File(s)." % self.count)
			if self.count != 0:
				self.scanForCovers(data)
			else:
				if not self.background:
					self.scanning = False
					self.callback_infos("No Movie(s) found!")
					self.callback_finished("Done")
				else:
					self.scanning = False
		else:
			print( "still scanning..")

	def getMovieSaveFile(self, moviename):
		if re.search('[Ss][0-9]+[Ee][0-9]+', moviename) is not None:
			tvseries = compile('(.*\w)[\s\.|-]+[S|s][0-9]+[E|e][0-9]+[\s\.|-].*?\.[ts|avi|mkv|divx|f4v|flv|img|iso|m2ts|m4v|mov|mp4|mpeg|mpg|mts|vob|wmv]')
			tvseriesalt = compile('^[S|s][0-9]+[E|e][0-9]+[\s\.\-](.*\w)\.[ts|avi|mkv|divx|f4v|flv|img|iso|m2ts|m4v|mov|mp4|mpeg|mpg|mts|vob|wmv]')
			if tvseries.match(moviename) is not None:
				return tvseries.match(moviename).groups()[0].replace(" ","_").replace(".","_")
			elif tvseriesalt.match(moviename) is not None:
				return tvseriesalt.match(moviename).groups()[0].replace(" ","_").replace(".","_")
			else:
				return None
		else:
			movietitle = compile('(.*\w)\.[ts|avi|mkv|divx|f4v|flv|img|iso|m2ts|m4v|mov|mp4|mpeg|mpg|mts|vob|wmv]')
			if movietitle.match(moviename) is not None:
				return movietitle.match(moviename).groups()[0].replace(" ","_").replace(".","_")
			else:
				return None

	def scanForCovers(self, data):
		self.start_time = time.clock()
		# filename', 'serie', filename, cleanTitle, url, season, episode
		self.guilist = []
		self.counting = 0
		self.found = 0
		self.notfound = 0
		self.error = 0
		ds = defer.DeferredSemaphore(tokens=2)
		downloads = [ds.run(self.download, url).addCallback(self.parseWebpage, which, type, filename, title, url, season, episode).addErrback(self.dataErrorInfo) for which, type, filename, title, url, season, episode in data]
		finished = defer.DeferredList(downloads).addErrback(self.dataErrorInfo)

	def download(self, url):
		return getPage(url, timeout=20, headers={'Accept': 'application/json'})

	def parseWebpage(self, data, which, type, filename, title, url, season, episode):
		self.counting += 1
		if not self.background:
			self.callback_infos("Cover(s): %s / %s - Scan: %s" % (str(self.counting), str(self.count), title))
		if type == "movie":
			list = []
			try:
				list = re.search('poster_path":"(.+?)".*?"original_title":"(.+?)"', str(data), re.S).groups(1)
			except:
				list = re.search('original_title":"(.+?)".*?"poster_path":"(.+?)"', str(data), re.S).groups(1)
			if list:
				self.guilist.append(((title, True, filename),))
				purl = "http://image.tmdb.org/t/p/%s%s" % (str(config.movielist.cover.themoviedb_coversize.value), str(list[0].replace('\\','')))
				downloadPage(purl, filename).addCallback(self.countFound).addErrback(self.dataErrorDownload)
			else:
				self.guilist.append(((title, False, filename),))
				self.notfound += 1
				if not self.background:
					self.callback_notfound(self.notfound)

			# get description
			if config.movielist.cover.getdescription.value:
				idx = []
				idx = re.findall('"id":(.*?),', data, re.S)
				if idx:
					iurl = "http://api.themoviedb.org/3/movie/%s?api_key=8789cfd3fbab7dccf1269c3d7d867aff&language=de" % idx[0]
					getPage(iurl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getInfos, id, type, filename).addErrback(self.dataError)

		elif type == "serie":
			list = []
			list = re.findall('<seriesid>(.*?)</seriesid>', data, re.S)
			if list:
				self.guilist.append(((title, True, filename),))
				purl = "http://www.thetvdb.com/banners/_cache/posters/%s-1.jpg" % list[0]
				downloadPage(purl, filename).addCallback(self.countFound).addErrback(self.dataErrorDownload)
			else:
				self.notfound += 1
				self.guilist.append(((title, False, filename),))
				if not self.background:
					self.callback_notfound(self.notfound)

			# get description
			if config.movielist.cover.getdescription.value:
				if season and episode:
					iurl = "http://www.thetvdb.com/api/2AAF0562E31BCEEC/series/%s/default/%s/%s/de.xml" % (list[0], str(int(season)), str(int(episode)))
					getPage(iurl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getInfos, id, type, filename).addErrback(self.dataError)
		else:
			self.notfound += 1
			if not self.background:
				self.callback_notfound(self.notfound)

		if not self.background:
			self.callback_menulist(self.guilist)
		self.checkDone()

	def checkDone(self):
		print( self.counting, self.count)
		if int(self.counting) == int(str(self.count)):
			elapsed_time = (time.clock() - self.start_time)
			if not self.background:
				self.callback_infos("Downloaded %s Cover(s) in %.1f sec." % (str(self.found), elapsed_time))
				self.callback_finished("Done")
			self.scanning = False
			print( "Found:", self.found)
			print( "Not Found:", self.notfound)
			print( "Errors:", self.error)
			print( "Total: %s / %s" % (self.counting, self.count))
			self.callback_finished(self.count)

	def countFound(self, data):
		self.found += 1
		if not self.background:
			self.callback_found(self.found)
			if int(self.counting) == int(str(self.count)):
				elapsed_time = (time.clock() - self.start_time)
				self.callback_infos("Downloaded %s Cover(s) in %.1f sec." % (str(self.found), elapsed_time))
		self.checkDone()

	def getInfos(self, data, id, type, filename):
		if type == "movie":
			infos = re.findall('"genres":\[(.*?)\].*?"overview":"(.*?)"', data, re.S)
			if infos:
				(genres, desc) = infos[0]
				self.writeTofile(decodeHtml(desc), filename)

		elif type == "serie":
			infos = re.findall('<Overview>(.*?)</Overview>', data, re.S)
			if infos:
				desc = infos[0]
				self.writeTofile(decodeHtml(desc), filename)

	def writeTofile(self, text, filename):
		if not fileExists(filename.replace('.jpg','.txt')):
			wFile = open(filename.replace('.jpg','.txt'),"w") 
			wFile.write(text) 
			wFile.close()

	def dataError(self, error):
		print( "ERROR:", error)
		self.checkDone()

	def dataErrorInfo(self, error):
		self.error += 1
		self.counting += 1
		print( "ERROR dataErrorInfo:", error)
		if not self.background:
			self.callback_error(self.error)
		self.checkDone()

	def dataErrorDownload(self, error):
		self.error += 1
		self.counting += 1
		if not self.background:
			self.callback_error(self.error)
		print( "ERROR:", error)
		self.checkDone()

class fmlcMenuList(GUIComponent, object):
	GUI_WIDGET = eListbox
	
	def __init__(self):
		GUIComponent.__init__(self)
		self.l = eListboxPythonMultiContent()
		self.l.setFont(0, gFont('Regular', 22))
		self.l.setItemHeight(30)
		self.l.setBuildFunc(self.buildList)

	def buildList(self, entry):
		width = self.l.getItemSize().width()
		(name, coverFound, filename) = entry
		res = [ None ]

		if coverFound:
			truePath = "/usr/share/enigma2/skin_default/extensions/cover_yes.png"
			res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 10, 1, 25, 25, loadPNG(truePath)))
		else:
			falsePath = "/usr/share/enigma2/skin_default/extensions/cover_no.png"
			res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 10, 1, 25, 25, loadPNG(falsePath)))

		res.append((eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 1280, 30, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, str(name)))
		return res

	def getCurrent(self):
		cur = self.l.getCurrentSelection()
		return cur and cur[0]

	def postWidgetCreate(self, instance):
		instance.setContent(self.l)
		self.instance.setWrapAround(True)

	def preWidgetRemove(self, instance):
		instance.setContent(None)

	def setList(self, list):
		self.l.setList(list)

	def moveToIndex(self, idx):
		self.instance.moveSelectionTo(idx)

	def getSelectionIndex(self):
		return self.l.getCurrentSelectionIndex()

	def getSelectedIndex(self):
		return self.l.getCurrentSelectionIndex()

	def selectionEnabled(self, enabled):
		if self.instance is not None:
			self.instance.setSelectionEnable(enabled)

	def pageUp(self):
		if self.instance is not None:
			self.instance.moveSelection(self.instance.pageUp)

	def pageDown(self):
		if self.instance is not None:
			self.instance.moveSelection(self.instance.pageDown)

	def up(self):
		if self.instance is not None:
			self.instance.moveSelection(self.instance.moveUp)

	def down(self):
		if self.instance is not None:
			self.instance.moveSelection(self.instance.moveDown)


class FindMovieList(Screen):
	skin = """
		<screen position="40,80" size="1200,600" title=" " >
			<widget name="info" position="10,10" size="820,30" font="Regular;24" foregroundColor="#00fff000"/>
			<widget name="path" position="10,50" size="820,30" font="Regular;24" foregroundColor="#00fff000"/>
			<widget name="found" position="850,10" size="300,22" font="Regular;20" foregroundColor="#00fff000"/>
			<widget name="notfound" position="850,40" size="300,22" font="Regular;20" foregroundColor="#00fff000"/>
			<widget name="error" position="850,70" size="300,22" font="Regular;20" foregroundColor="#00fff000"/>
			<widget name="list" position="10,90" size="800,480" scrollbarMode="showOnDemand"/>
			<widget name="cover" position="850,110" size="300,420" alphatest="blend"/>
			<widget name="key_red" position="40,570" size="250,25" halign="center" transparent="1" font="Regular;20"/>
			<widget name="key_green" position="330,570" size="250,22" halign="center" transparent="1" font="Regular;20"/>
			<widget name="key_blue" position="890,570" size="250,22" halign="center" transparent="1" font="Regular;20"/>
			<eLabel position="40,596" size="250,4" zPosition="-10" backgroundColor="#20f23d21" />
			<eLabel position="330,596" size="250,4" zPosition="-10" backgroundColor="#20389416" />			
			<eLabel position="890,596" size="250,4" zPosition="-10" backgroundColor="#200064c7" />
		</screen>"""

	def __init__(self, session, service):
		Screen.__init__(self, session)
		self.session = session
		self.service = service
		BackgroundCoverScanner(session)
		bg_func = BackgroundCoverScanner.instance
		bg_func.startTimer()
		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"cancel":	self.cancel,
			"green" :	self.getFileList,
			"blue"	:	self.setScanPath,
			"left"  :	self.keyLeft,
			"right" :	self.keyRight,
			"up"    :	self.keyUp,
			"down"  :	self.keyDown,
			"ok"	:	self.keyOk
		}, -1)

		#self['title'] 
		self.title = "%s v%s" % (pname, pversion)
		self['info'] = Label("")
		self['path'] = Label("Scan Path: %s" % config.movielist.cover.scanpath.value)
		self['found'] = Label("Download:")
		self['notfound'] = Label("Not Found:")
		self['error'] = Label("Download Error:")
		self['cover'] = Pixmap()
		self['key_red'] = Label("Exit")
		self['key_green'] = Label("Search Cover(s)")
		self['key_yellow'] = Label("")
		self['key_blue'] = Label("Set Scan Path")
		self['list'] = fmlcMenuList()
		
		self.fileScanner = BackgroundCoverScanner.instance
		self.fileScanner.setCallbacks(self.msgCallback, self.foundCallback, self.notFoundCallback, self.errorCallback, self.listCallback, self.msgDone)
		self.scanning = False
		self.first = False
		self.onLayoutFinish.append(self._onLayoutFinish)

	def _onLayoutFinish(self):
		self['info'].setText("Press 'Green' for scanning your MovieList and search Cover(s).")

	def msgCallback(self, txt):
		self['info'].setText(txt)

	def foundCallback(self, txt):
		self['found'].setText("Download: %s" % str(txt))

	def notFoundCallback(self, txt):
		self['notfound'].setText("Not Found: %s" % str(txt))
	
	def errorCallback(self, txt):
		self['error'].setText("Download Error: %s" % str(txt))

	def listCallback(self, list):
		self['list'].setList(list)
		if not self.first:
			self.first = True
			self.getCover()

	def msgDone(self, txt):
		self.first = True

	def __onClose(self):
		self.fileScanner.setCallbacks(None, None, None, None, None, None)

	def getFileList(self):
		self['found'].setText("Download:")
		self['notfound'].setText("Not Found:")
		self['error'].setText("Download Error:")
		self.fileScanner.getFileList(False)

	def getCover(self):
		check = self['list'].getCurrent()
		if check == None:
			return
		filename = self['list'].getCurrent()[2]
		self.showCover(filename)

	def showCover(self, poster_path):
		self.picload = ePicLoad()
		if not fileExists(poster_path):
			poster_path = "/usr/share/enigma2/skin_default/extensions/no_coverbg.png"
		if fileExists(poster_path):
			self["cover"].instance.setPixmap(gPixmapPtr())
			scale = AVSwitch().getFramebufferScale()
			size = self["cover"].instance.size()
			self.picload.setPara((size.width(), size.height(), scale[0], scale[1], False, 1, "#00000000"))
			if isDreamOS:
				if self.picload.startDecode(poster_path, False) == 0:
					ptr = self.picload.getData()
					if ptr != None:
						self["cover"].instance.setPixmap(ptr)
						self["cover"].show()
			else:
				if self.picload.startDecode(poster_path, 0, 0, False) == 0:
					ptr = self.picload.getData()
					if ptr != None:
						self["cover"].instance.setPixmap(ptr)
						self["cover"].show()
			del self.picload

	def keyOk(self):
		pass
		
	def setScanPath(self):
		self.session.openWithCallback(self.selectedMediaFile, FindMovieListScanPath, config.movielist.cover.scanpath.value)

	def selectedMediaFile(self, res):
		if res is not None:
			config.movielist.cover.scanpath.value = res
			config.movielist.cover.scanpath.save()
			configfile.save()
			self['path'].setText("Scan Path: %s" % config.movielist.cover.scanpath.value)
	
	def keyLeft(self):
		check = self['list'].getCurrent()
		if check == None:
			return
		self['list'].pageUp()
		self.getCover()

	def keyRight(self):
		check = self['list'].getCurrent()
		if check == None:
			return
		self['list'].pageDown()
		self.getCover()

	def keyDown(self):
		check = self['list'].getCurrent()
		if check == None:
			return
		self['list'].down()
		self.getCover()

	def keyUp(self):
		check = self['list'].getCurrent()
		if check == None:
			return
		self['list'].up()
		self.getCover()

	def cancel(self):
		self.close()

class FindMovieListScanPath(Screen):
	skin = """
		<screen position="40,80" size="1200,600" title=" " >
			<widget name="media" position="10,10" size="540,30" valign="top" font="Regular;22" />
			<widget name="folderlist" position="10,45" zPosition="1" size="540,300" scrollbarMode="showOnDemand"/>
			<widget name="key_red" position="40,570" size="250,25" halign="center" transparent="1" font="Regular;20"/>
			<widget name="key_green" position="330,570" size="250,22" halign="center" transparent="1" font="Regular;20"/>
			<eLabel position="40,596" size="250,4" zPosition="-10" backgroundColor="#20f23d21" />
			<eLabel position="330,596" size="250,4" zPosition="-10" backgroundColor="#20389416" />
		</screen>
		"""

	def __init__(self, session, initDir, plugin_path = None):
		Screen.__init__(self, session)
		
		if not os.path.isdir(initDir):
			initDir = "/media/hdd/movie/"

		self["folderlist"] = FileList(initDir, inhibitMounts = False, inhibitDirs = False, showMountpoints = False, showFiles = False)
		self["media"] = Label()
		self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions", "EPGSelectActions"],
		{
			"back": self.cancel,
			"left": self.left,
			"right": self.right,
			"up": self.up,
			"down": self.down,
			"ok": self.ok,
			"green": self.green,
			"red": self.cancel
		}, -1)
		self.title=_("Choose Download folder")
		try:
			self["title"] = StaticText(self.title)
		except:
			print( 'self["title"] was not found in skin')

		self["key_red" ]= Label(_("Cancel"))
		self["key_green"] = Label(_("Ok"))

	def cancel(self):
		self.close(None)

	def green(self):
		directory = self["folderlist"].getSelection()[0]
		if (directory.endswith("/")):
			self.fullpath = self["folderlist"].getSelection()[0]
		else:
			self.fullpath = self["folderlist"].getSelection()[0] + "/"
		self.close(self.fullpath)

	def up(self):
		self["folderlist"].up()
		self.updateFile()

	def down(self):
		self["folderlist"].down()
		self.updateFile()

	def left(self):
		self["folderlist"].pageUp()
		self.updateFile()

	def right(self):
		self["folderlist"].pageDown()
		self.updateFile()

	def ok(self):
		if self["folderlist"].canDescent():
			self["folderlist"].descent()
			self.updateFile()

	def updateFile(self):
		currFolder = self["folderlist"].getSelection()[0]
		self["media"].setText(currFolder)

def decodeHtml(text):
	text = text.replace('&auml;','ÃƒÂ¤')
	text = text.replace('\u00e4','ÃƒÂ¤')
	text = text.replace('&#228;','ÃƒÂ¤')
	text = text.replace('&Auml;','Ãƒâ€ž')
	text = text.replace('\u00c4','Ãƒâ€ž')
	text = text.replace('&#196;','Ãƒâ€ž')
	text = text.replace('&ouml;','ÃƒÂ¶')
	text = text.replace('\u00f6','ÃƒÂ¶')
	text = text.replace('&#246;','ÃƒÂ¶')
	text = text.replace('&ouml;','Ãƒâ€“')
	text = text.replace('&Ouml;','Ãƒâ€“')
	text = text.replace('\u00d6','Ãƒâ€“')
	text = text.replace('&#214;','Ãƒâ€“')
	text = text.replace('&uuml;','ÃƒÂ¼')
	text = text.replace('\u00fc','ÃƒÂ¼')
	text = text.replace('&#252;','ÃƒÂ¼')
	text = text.replace('&Uuml;','ÃƒÅ“')
	text = text.replace('\u00dc','ÃƒÅ“')
	text = text.replace('&#220;','ÃƒÅ“')
	text = text.replace('&szlig;','ÃƒÅ¸')
	text = text.replace('\u00df','ÃƒÅ¸')
	text = text.replace('&#223;','ÃƒÅ¸')
	text = text.replace('&amp;','&')
	text = text.replace('&quot;','\"')
	text = text.replace('&gt;','>')
	text = text.replace('&apos;',"'")
	text = text.replace('&acute;','\'')
	text = text.replace('&ndash;','-')
	text = text.replace('&bdquo;','"')
	text = text.replace('&rdquo;','"')
	text = text.replace('&ldquo;','"')
	text = text.replace('&lsquo;','\'')
	text = text.replace('&rsquo;','\'')
	text = text.replace('&#034;','"')
	text = text.replace('&#34;','"')
	text = text.replace('&#038;','&')
	text = text.replace('&#039;','\'')
	text = text.replace('&#39;','\'')
	text = text.replace('&#160;',' ')
	text = text.replace('\u00a0',' ')
	text = text.replace('\u00b4','\'')
	text = text.replace('\u003d','=')
	text = text.replace('\u0026','&')
	text = text.replace('&#174;','')
	text = text.replace('&#225;','a')
	text = text.replace('&#233;','e')
	text = text.replace('&#243;','o')
	text = text.replace('&#8211;',"-")
	text = text.replace('&#8212;',"Ã¢â‚¬â€")
	text = text.replace('&mdash;','Ã¢â‚¬â€')
	text = text.replace('\u2013',"Ã¢â‚¬â€œ")
	text = text.replace('&#8216;',"'")
	text = text.replace('&#8217;',"'")
	text = text.replace('&#8220;',"'")
	text = text.replace('&#8221;','"')
	text = text.replace('&#8222;',',')
	text = text.replace('\u014d','Ã…Â')
	text = text.replace('\u016b','Ã…Â«')
	text = text.replace('\u201a','\"')
	text = text.replace('\u2018','\"')
	text = text.replace('\u201e','\"')
	text = text.replace('\u201c','\"')
	text = text.replace('\u201d','\'')
	text = text.replace('\u2019s','Ã¢â‚¬â„¢')
	text = text.replace('\u00e0','ÃƒÂ ')
	text = text.replace('\u00e7','ÃƒÂ§')
	text = text.replace('\u00e8','ÃƒÂ©')
	text = text.replace('\u00e9','ÃƒÂ©')
	text = text.replace('\u00c1','ÃƒÂ')
	text = text.replace('\u00c6','Ãƒâ€ ')
	text = text.replace('\u00e1','ÃƒÂ¡')
	text = text.replace('&#xC4;','Ãƒâ€ž')
	text = text.replace('&#xD6;','Ãƒâ€“')
	text = text.replace('&#xDC;','ÃƒÅ“')
	text = text.replace('&#xE4;','ÃƒÂ¤')
	text = text.replace('&#xF6;','ÃƒÂ¶')
	text = text.replace('&#xFC;','ÃƒÂ¼')
	text = text.replace('&#xDF;','ÃƒÅ¸')
	text = text.replace('&#xE9;','ÃƒÂ©')
	text = text.replace('&#xB7;','Ã‚Â·')
	text = text.replace("&#x27;","'")
	text = text.replace("&#x26;","&")
	text = text.replace("&#xFB;","ÃƒÂ»")
	text = text.replace("&#xF8;","ÃƒÂ¸")
	text = text.replace("&#x21;","!")
	text = text.replace("&#x3f;","?")
	text = text.replace('&#8230;','...')
	text = text.replace('\u2026','...')
	text = text.replace('&hellip;','...')
	text = text.replace('&#8234;','')
	return text

def autostart(session, **kwargs):
	BackgroundCoverScanner(session)
	bg_func = BackgroundCoverScanner.instance
	bg_func.startTimer()

def main(session, service, **kwargs):
	session.open(FindMovieList, service)

def main2(session, **kwargs):
	session.open(FindMovieList, None)

def Plugins(**kwargs):
	return [PluginDescriptor(name="Find MovieList Covers", description="Search Covers", where = PluginDescriptor.WHERE_MOVIELIST, fnc=main),
			PluginDescriptor(name="Find MovieList Covers", description="Search Covers", where = PluginDescriptor.WHERE_PLUGINMENU, fnc=main2),
			PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart)
			]
