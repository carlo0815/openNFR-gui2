from __future__ import print_function
from Components.Button import Button
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.PluginList import resolveFilename
from Components.Task import Task, Job, job_manager, Condition
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.TaskView import JobView
from Tools.Downloader import downloadWithProgress
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, SCOPE_PLUGINS
from Components.config import config, configfile, ConfigSubsection, ConfigText, ConfigSelection
from six.moves import urllib
from six.moves.urllib.request import urlopen, Request
import requests
import six
import os
import shutil
import math
import re
from boxbranding import getBoxType, getMachineBuild, getImageVersion, getBrandOEM, getMachineBrand, getImageArch

class NFR4XChooseOnLineImage(Screen):
	skin = '<screen name="NFR4XChooseOnLineImage" position="center,center" size="880,620" title="NFR4XBoot - Download OnLine Images" >\n\t\t\t  <widget source="list" render="Listbox" position="10,0" size="870,610" scrollbarMode="showOnDemand" transparent="1">\n\t\t\t\t  <convert type="TemplatedMultiContent">\n\t\t\t\t  {"template": [\n\t\t\t\t  MultiContentEntryText(pos = (0, 10), size = (830, 30), font=0, flags = RT_HALIGN_RIGHT, text = 0),\n\t\t\t\t  MultiContentEntryPixmapAlphaBlend(pos = (10, 0), size = (480, 60), png = 1),\n\t\t\t\t  MultiContentEntryText(pos = (0, 40), size = (830, 30), font=1, flags = RT_VALIGN_TOP | RT_HALIGN_RIGHT, text = 3),\n\t\t\t\t  ],\n\t\t\t\t  "fonts": [gFont("Regular", 28),gFont("Regular", 20)],\n\t\t\t\t  "itemHeight": 65\n\t\t\t\t  }\n\t\t\t\t  </convert>\n\t\t\t  </widget>\n\t\t  </screen>'

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self['list'] = List(self.list)
		self.updateList()
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
		 'back': self.close})

	def KeyOk1(self, res = None):
		config.usage.mbimageversion.save()
		mbimageValue = config.usage.mbimageversion.value
		if returnValue is not None:
			self.session.openWithCallback(self.quit, DownloadOnLineImage, returnValue, mbimageValue )
		return

	def KeyOk(self):
		global returnValue
		global mbimageValue
		self.sel = self['list'].getCurrent()
		returnValue = self.sel[2]
		if returnValue in ('opennfr', 'openhdf', 'openatv', 'pure2'): 
			from Screens.Setup import Setup
			MBImagelist = [("6.0", _("6.0")), ("6.1", _("6.1")), ("6.2", _("6.2")), ("6.3", _("6.3")), ("6.4", _("6.4")), ("6.5", _("6.5"))]
			if returnValue ==  'openatv':
				MBImagelist.remove(("6.0", _("6.0")))			
				MBImagelist.remove(("6.1", _("6.1")))
				MBImagelist.remove(("6.2", _("6.2")))
				MBImagelist.remove(("6.3", _("6.3")))
			elif returnValue ==  'openhdf':
				MBImagelist.remove(("6.0", _("6.0")))			
				MBImagelist.remove(("6.1", _("6.1")))
				MBImagelist.remove(("6.2", _("6.2")))
				MBImagelist.remove(("6.3", _("6.3")))
			elif returnValue ==  'opennfr':
				MBImagelist.remove(("6.0", _("6.0")))			
				MBImagelist.remove(("6.1", _("6.1")))
				MBImagelist.remove(("6.2", _("6.2")))
				MBImagelist.remove(("6.3", _("6.3")))
			elif returnValue ==  'pure2':
				MBImagelist.remove(("6.0", _("6.0")))
				MBImagelist.remove(("6.1", _("6.1")))
				MBImagelist.remove(("6.4", _("6.4")))	    
			if returnValue ==  'opendroid':    	    
				config.usage.mbimageversion = ConfigSelection(default="6.6", choices = MBImagelist)	    
			else:
				config.usage.mbimageversion = ConfigSelection(default="6.4", choices = MBImagelist)
			self.session.openWithCallback(self.KeyOk1, Setup, "multiboot")
			mbimageValue = config.usage.mbimageversion.value
		else:
			config.usage.mbimageversion = ConfigSelection(default="6.1", choices = [("0.0", _("0.0"))]) 
			config.usage.mbimageversion.value = "0.0"
			config.usage.mbimageversion.save()
			self.KeyOk1() 

	def updateList(self):
		self.list = []
		mypath = resolveFilename(SCOPE_PLUGINS)
		mypath = mypath + 'Extensions/NFR4XBoot/images/'
		mypixmap = mypath + 'opennfr.png'
		png = LoadPixmap(mypixmap)
		name = _('NFR')
		desc = _('Download latest NFR Image')
		idx = 'opennfr'
		res = (name,
		 png,
		 idx,
		 desc)
		self.list.append(res)
		mypixmap = mypath + 'openvix.png'
		png = LoadPixmap(mypixmap)
		name = _('OpenVIX')
		desc = _('Download latest OpenVIX Image')
		idx = 'openvix'
		res = (name,
		 png,
		 idx,
		 desc)
		self.list.append(res)
		mypixmap = mypath + 'openatv.png'
		png = LoadPixmap(mypixmap)
		name = _('OpenATV')
		desc = _('Download latest OpenATV Image')
		idx = 'openatv'
		res = (name,
		 png,
		 idx,
		 desc) 
		self.list.append(res)
		mypixmap = mypath + 'openhdf.png'
		png = LoadPixmap(mypixmap)
		name = _('OpenHDF')
		desc = _('Download latest OpenHDF Image')
		idx = 'openhdf'
		res = (name,
		 png,
		 idx,
		 desc)
		self.list.append(res)
		mypixmap = mypath + 'openeight.png'
		png = LoadPixmap(mypixmap)
		name = _('OpenEight')
		desc = _('Download latest OpenEight Image')
		idx = 'openeight'
		res = (name,
		 png,
		 idx,
		 desc)
		self.list.append(res)
		mypixmap = mypath + 'pure2.png'
		png = LoadPixmap(mypixmap)
		name = _('PurE2')
		desc = _('Download latest PurE2 Image')
		idx = 'pure2'
		res = (name,
		 png,
		 idx,
		 desc)
		self.list.append(res)		 
		self['list'].list = self.list

	def quit(self):
		self.close()


class DownloadOnLineImage(Screen):
	skin = '\n\t<screen position="center,center" size="560,500" title="NFR4XBoot - Download Image">\n\t\t<ePixmap position="0,460"   zPosition="1" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />\n\t\t<ePixmap position="140,460" zPosition="1" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />\n\t\t<widget name="key_red" position="0,460" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n\t\t<widget name="key_green" position="140,460" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n\t\t<widget name="imageList" position="10,10" zPosition="1" size="550,450" font="Regular;20" scrollbarMode="showOnDemand" transparent="1" />\n\t</screen>'

	def __init__(self, session, distro, mbimageversion):
		Screen.__init__(self, session)
		self.session = session
		global ImageVersion				   
		ImageVersion = mbimageversion
		distri = getBrandOEM() 
		boxname = getBoxType()
		if boxname == "twinboxlcdci5":
			boxname = "twinboxlcd"
		if boxname == 'sf8008t':
			boxname = "sf8008"
		if boxname == 'sf8008s':
			boxname = "sf8008"                         	                         	
		Screen.setTitle(self, _('NFR4XBoot - Download Image'))
		self['key_green'] = Button(_('Install'))
		self['key_red'] = Button(_('Exit'))
		self.filename = None
		self.imagelist = []
		self.simulate = False
		self.imagePath = '/media/nfr4xboot/NFR4XBootUpload'
		global BRANDOEM
		global BRANDOEMDROID
		global MASCHINEBUILD       		
		BRANDOEM = getBrandOEM()
		BRANDOEMDROID = getBrandOEM()
		MASCHINEBUILD = boxname						   
		if boxname in ('ax51', 'triplex'):
			BRANDOEM = 'ax'
		elif boxname in ('gb800seplus', 'gbquadplus', 'gbquad4k', 'gbue4k', 'gbultraue', 'gbx1', 'gbx2', 'gbx3'):
			BRANDOEM = 'gigablue'
		elif boxname in ('mutant51'):
			BRANDOEM = 'mutant'
		elif boxname in ('sf128', 'sf208', 'sf3038', 'sf4008', 'sf8008', 'sf8008m'):
			BRANDOEM = 'octagon'
		elif boxname in ('osmega'):
			BRANDOEM = 'xcore' 
		if boxname in ('gb800seplus', 'gbquadplus', 'gbquad4k', 'gbue4k', 'gbultraue', 'gbx1', 'gbx2', 'gbx3'):
			BRANDOEMDROID = 'GigaBlue'
			MASCHINEBUILD = boxname
		elif boxname in ('formuler1', 'formuler3', 'formuler4', 'formuler4turbo'):
			BRANDOEMDROID = 'Formuler'
			MASCHINEBUILD = boxname
		elif boxname in ('atemio6000', 'atemio6100', 'atemio6200', 'atemionemesis'):
			BRANDOEMDROID = 'Atemio'
			MASCHINEBUILD = boxname
		elif boxname in ('xpeedlx3'):
			BRANDOEMDROID = 'GoldenInterstar'
			MASCHINEBUILD = boxname
		elif boxname in ('sf98', 'sf108', 'sf128', 'sf138', 'sf208', 'sf228', 'sf3038', 'sf4008', 'sf8008', 'sf8008m'):
			BRANDOEMDROID = 'Octagon'
			MASCHINEBUILD = boxname
		elif boxname in ('mutant51', 'ax51'):
			BRANDOEMDROID = 'Mut@nt'
			MASCHINEBUILD = 'HD51'
		elif boxname in ('optimussos1plus', 'optimussos2plus', 'optimussos3plus', 'optimussos1', 'optimussos2', 'osmega', 'osmini'):
			BRANDOEMDROID = 'Edision'
			MASCHINEBUILD = boxname
		elif boxname in ('vusolo4k'):
			BRANDOEMDROID = 'VU+'  
			MASCHINEBUILD = boxname			
		self.distro = distro
		if self.distro == 'opennfr':
			self.feed = 'opennfr'
			self.feedurl = 'http://dev.nachtfalke.biz/nfr/feeds/%s/images' %ImageVersion
		elif self.distro == 'openatv':
			self.feed = 'openatv'
			self.feedurl = 'http://images.mynonpublic.com/openatv/%s' %ImageVersion
		elif self.distro == 'openvix':
			self.feed = 'openvix'
			self.feedurl = 'http://openvix.co.uk'
		elif self.distro == 'pure2':
			self.feed = 'pure2'
			self.feedurl = 'http://pur-e2.club/OU/images/index.php?dir=%s' %ImageVersion 
		elif self.distro == 'openhdf':
			self.feed = 'openhdf'
			if ImageVersion == "6.5":
				hdfImageVersion = "v65"
			else:
				hdfImageVersion = "v64"                                            
			self.feedurl = 'http://%s.hdfreaks.cc/%s' % (hdfImageVersion, boxname)
			self.feedurl1 = 'http://%s.hdfreaks.cc' % hdfImageVersion
		elif self.distro == 'openeight':
			self.feed = 'openeight'
			self.feedurl = 'http://openeight.de'
		else:
			self.feed = 'opennfr'
			self.feedurl = 'http://dev.nachtfalke.biz/nfr/feeds/6.4/images'
		self['imageList'] = MenuList(self.imagelist)
		self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'green': self.green,
		'red': self.quit,
		'cancel': self.quit}, -2)
		self.onLayoutFinish.append(self.layoutFinished)
		return

	def quit(self):
		self.close()

	def box(self):
		box = getBoxType()
		if box == "twinboxlcdci5":
			box = "twinboxlcd" 	
		urlbox = getBoxType()
		if urlbox == "twinboxlcdci5":
			urlbox = "twinboxlcd" 	
		if self.distro == 'openatv' or self.distro == 'opennfr' or self.distro == 'openhdf':
			if box in ('xpeedlx1', 'xpeedlx2'):
				box = 'xpeedlx'
			if box in ('sf8008t', 'sf8008s'):
				box = 'sf8008'				
			req = urllib.request.Request(self.feedurl)
			reg1 = requests.get(self.feedurl)
			stb = 'no Image for this Box on this Side'
			from bs4 import BeautifulSoup
			soup = BeautifulSoup(reg1.text, 'html.parser')
			try:
				for link in soup.find_all('a'):
					lefts = link.get('href')
					if box in lefts:
						stb = '1'
						break
			except:
				stb = 'no Image for this Box on this Side'
		if self.distro == 'openvix':
			if box in ('xpeedlx1', 'xpeedlx2'):
				box = 'xpeedlx'
			if box in ('sf8008t', 'sf8008s'):
				box = 'sf8008'
				urlbox = box	
			self.feedurl1 = self.feedurl + "/openvix-builds/"
			reg1 = requests.get(self.feedurl1)
			from bs4 import BeautifulSoup                        
			soup = BeautifulSoup(reg1.text, 'html.parser')  			
			#req = urllib.request.Request(self.feedurl1)
			stb = 'no Image for this Box on this Side'
			try:
				for link in soup.find_all('a'):
					lefts = link.get('href')
					if box in lefts:
						stb = '1'
						break
			except:
				stb = 'no Image for this Box on this Side'  				
		if self.distro == 'pure2':
			if box in ('sf8008t', 'sf8008s'):
				box = 'sf8008'	
			self.feedurl1 = self.feedurl + "/" + BRANDOEM
			reg1 = requests.get(self.feedurl1)
			from bs4 import BeautifulSoup                        
			soup = BeautifulSoup(reg1.text, 'html.parser') 
			stb = 'no Image for this Box on this Side'
			try:
				for link in soup.find_all('a'):
					lefts = link.get('href')
					if box in lefts:
						stb = '1'
						break
			except:
 				stb = 'no Image for this Box on this Side'  					
		elif self.distro == 'openeight':
			if box in ('sf208', 'sf228', 'sf108', 'sf3038', 'sf98', 'sf128', 'sf138', 'sf4008'):
				if box in ('sf4008'):
					box = 'sf4008'
					urlbox = getBoxType()               
					stb = '1'			
				elif box in ('sf228'):
					box = 'sf228'
					urlbox = getBoxType()               
					stb = '1'
				elif box in ('sf208'):
					box = 'sf208'
					urlbox = getBoxType()               
					stb = '1'
				elif box in ('sf98'):
					box = 'sf98'
					urlbox = getBoxType()               
					stb = '1'
				elif box in ('sf3038'):
					box = 'sf3038'
					urlbox = getBoxType()               
					stb = '1'
				elif box in ('sf108'):
					box = 'sf108'
					urlbox = getBoxType() 
					stb = '1' 
				elif box in ('sf128'):
					box = 'sf128'
					urlbox = getBoxType() 
					stb = '1'
				elif box in ('sf138'):
					box = 'sf138'
					urlbox = getBoxType() 
					stb = '1'			
			else:   
				stb = 'no Image for this Box on this Side'    
		return (box, urlbox, stb)

	def green(self, ret = None):
		sel = self['imageList'].l.getCurrentSelection()
		if sel == None:
			print('Nothing to select !!')
			return
		else:
			file_name = self.imagePath + '/' + sel
			self.filename = file_name
			self.sel = sel
			box = self.box()
			self.hide()
			if self.distro == 'openvix':
				url = self.feedurl + '/openvix-builds/' + box[0] + '/' + sel 
			elif self.distro == 'openeight':
				url = self.feedurl + '/images/' + box[0] + '/' + sel
			elif self.distro == 'openhdf':
				url = self.feedurl + '/' + sel
			elif self.distro == 'pure2':
				url = 'http://pur-e2.club/OU/images/' + ImageVersion + '/' + BRANDOEM + '/' + sel     
			else:
				url = self.feedurl + '/' + box[0] + '/' + sel
			print('[NFR4XBoot] Image download url: ', url)
			try:
				user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'		
				headers={'User-Agent':user_agent,} 
				req = urllib.request.Request(url, None, headers)			
				u = urllib.request.urlopen(req)
			except:
				self.session.open(MessageBox, _('The URL to this image is not correct !!'), type=MessageBox.TYPE_ERROR)
				self.close()

			f = open(file_name, 'wb')
			f.close()
			try:
				file_size = int(u.getheader('Content-Length'))
				print('Downloading: %s Bytes: %s' % (sel, file_size))
				job = ImageDownloadJob(url, file_name, sel)
				job.afterEvent = 'close'
				job_manager.AddJob(job)
				job_manager.failed_jobs = []
				self.session.openWithCallback(self.ImageDownloadCB, JobView, job, backgroundable=False, afterEventChangeable=False)
				return
			except:
				self.session.open(MessageBox, _('The URL to this image is not correct !!'), type=MessageBox.TYPE_ERROR)
				self.close()    	

	def ImageDownloadCB(self, ret):
		if ret:
			return
		elif job_manager.active_job:
			job_manager.active_job = None
			self.close()
			return
		else:
			if len(job_manager.failed_jobs) == 0:
				self.session.openWithCallback(self.startInstall, MessageBox, _('Do you want to install this image now?'), default=False)
			else:
				self.session.open(MessageBox, _('Download Failed !!'), type=MessageBox.TYPE_ERROR)
			return

	def startInstall(self, ret = None):
		if ret:
			from Plugins.Extensions.NFR4XBoot.plugin import NFR4XBootImageInstall
			self.session.openWithCallback(self.quit, NFR4XBootImageInstall)
		else:
			self.close()

	def layoutFinished(self):
		box = self.box()[0]
		urlbox = self.box()[1]
		stb = self.box()[2]
		print('[NFR4XBoot] FEED URL: ', self.feedurl)
		print('[NFR4XBoot] BOXTYPE: ', box)
		print('[NFR4XBoot] URL-BOX: ', urlbox)        
		self.imagelist = []
		if stb != '1':
			url = self.feedurl
		if self.distro in ('openatv', 'openeight'):
			url = '%s/index.php?open=%s' % (self.feedurl, box)
		elif self.distro == 'openvix':
			url = '%s/openvix-builds/%s' % (self.feedurl, box)
		elif self.distro == 'opennfr':
			url = '%s/%s' % (self.feedurl, box)
		elif self.distro == 'openhdf':
			url = '%s/%s' % (self.feedurl1, box)
		elif self.distro == 'pure2':
			url = '%s' % (self.feedurl1)               
		else:
			url = self.feedurl
		print('[NFR4XBoot] URL: ', url)
		user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'		
		headers={'User-Agent':user_agent,} 
		req = urllib.request.Request(url, None, headers)
		try:
			response = urllib.request.urlopen(req)
		except urllib.error.URLError as e:
			print('URL ERROR: %s' % e)
			self.imagelist.append(stb)
			self['imageList'].l.setList(self.imagelist)
			return

		try:
			the_page = response.read()
		except urllib.error.URLError as e:
			print('HTTP download ERROR: %s' % e.code)
			return

		lines = the_page.split(b'\n')
        
		tt = len(box)
		if stb == '1':
			box1 = box.encode()	
			urlbox1 = urlbox.encode()
			for line in lines:
				if self.feed == "openeight":
					if line.find(b"/images/%s/" % box1) > -1:
						t = line.find(b'/images/%s/' % box1)
						self.imagelist.append(line[t+tt+9:t+tt+tt+40].decode())
				elif line.find(b"<a href='%s/" % box1) > -1:
					t = line.find(b"<a href='%s/" % box1)
					if self.feed in 'openatv':
						self.imagelist.append(line[t + tt + 10:t + tt + tt + 39].decode())
				elif line.find(b"<a href='%s/" % urlbox1) > -1:
					ttt = len(urlbox1)
					t = line.find(b"<a href='%s/" % urlbox1) 
					t5 = line.find(b".zip'")
					self.imagelist.append(line[t + ttt + 10 :t5 + 4].decode())                        
				elif line.find(b'href="openvix-') > -1:
					t4 = line.find(b'openvix-')
					t5 = line.find(b'.zip"')
					self.imagelist.append(line[t4 :t5+4].decode())
				elif line.find(b'file=openvixhd-') > -1:
					t4 = line.find(b'file=')
					self.imagelist.append(line[t4 + 5:-2].decode())
				elif line.find(b'<a href="download.php?file=' + box1 + b'/') > -1:
					t4 = line.find(b'file=' + box1)
					t5 = line.find(b'.zip" class="')
					self.imagelist.append(line[t4 + len(box1) + 6:t5 + 4].decode())
				elif line.find(b'<a class="autoindex_a" href="/OU/images/index.php?dir=' + ImageVersion.encode() + b'/' + BRANDOEM.encode() + b"/&amp;file=" + box1) > -1:
					t4 = line.find(box1 + b'-PurE2')
					t5 = line.find(b'.zip"')
					self.imagelist.append(line[t4 :t5+4].decode())
				elif line.find(b'href="opennfr-') > -1:
					t4 = line.find(b'opennfr-')
					t5 = line.find(b'.zip"')
					self.imagelist.append(line[t4 :t5+4].decode())
				elif line.find(b'href="openhdf-') > -1:
					t4 = line.find(b'openhdf-')
					t5 = line.find(b'.zip"')
					self.imagelist.append(line[t4 :t5+4].decode())
		else:
			self.imagelist.append(stb)
		if "" in self.imagelist:
			self.imagelist.remove('')
		print("self.imagelist:", self.imagelist)                        		
		self['imageList'].l.setList(self.imagelist)


class ImageDownloadJob(Job):

	def __init__(self, url, filename, file):
		Job.__init__(self, _('Downloading %s' % file))
		ImageDownloadTask(self, url, filename)


class DownloaderPostcondition(Condition):

	def check(self, task):
		return task.returncode == 0

	def getErrorMessage(self, task):
		return self.error_message


class ImageDownloadTask(Task):

	def __init__(self, job, url, path):
		Task.__init__(self, job, _('Downloading'))
		self.postconditions.append(DownloaderPostcondition())
		self.job = job
		self.url = url
		self.path = path
		self.error_message = ''
		self.last_recvbytes = 0
		self.error_message = None
		self.download = None
		self.aborted = False
		return

	def run(self, callback):
		self.callback = callback
		self.download = downloadWithProgress(self.url, self.path)
		self.download.addProgress(self.download_progress)
		self.download.start().addCallback(self.download_finished).addErrback(self.download_failed)
		print('[ImageDownloadTask] downloading', self.url, 'to', self.path)

	def abort(self):
		print('[ImageDownloadTask] aborting', self.url)
		if self.download:
			self.download.stop()
		self.aborted = True

	def download_progress(self, recvbytes, totalbytes):
		if recvbytes - self.last_recvbytes > 10000:
			self.progress = int(100 * (float(recvbytes) / float(totalbytes)))
			self.name = _('Downloading') + ' ' + '%d of %d kBytes' % (recvbytes / 1024, totalbytes / 1024)
			self.last_recvbytes = recvbytes

	def download_failed(self, failure_instance = None, error_message = ''):
		self.error_message = error_message
		if error_message == '' and failure_instance is not None:
			self.error_message = failure_instance.getErrorMessage()
		Task.processFinished(self, 1)
		return

	def download_finished(self, string = ''):
		if self.aborted:
			self.finish(aborted=True)
		else:
			Task.processFinished(self, 0)
