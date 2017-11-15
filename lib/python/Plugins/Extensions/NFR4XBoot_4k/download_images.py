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
import urllib2
import os
import shutil
import math
from boxbranding import getBoxType, getMachineBuild, getImageVersion, getBrandOEM

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
	if returnValue in ('opennfr', 'openhdf', 'openatv-6.0', 'opendroid'): 	
            from Screens.Setup import Setup
	    MBImagelist = [("6.0", _("6.0")), ("6.1", _("6.1"))]
	    if returnValue ==  'opennfr':
	        MBImagelist.append(("5.3", _("5.3")))
	    elif returnValue ==  'opendroid':
	        MBImagelist.append(("6.3", _("6.3")))
	        MBImagelist.append(("6.4", _("6.4")))
	        MBImagelist.remove(("6.0", _("6.0")))
	        MBImagelist.remove(("6.1", _("6.1")))                                 	        
	    elif returnValue ==  'openhdf':
	        MBImagelist.remove(("6.0", _("6.0")))
                MBImagelist.append(("6.2", _("6.2")))
                MBImagelist.append(("5.5", _("5.5")))
	    if returnValue ==  'opendroid':
                config.usage.mbimageversion = ConfigSelection(default="6.3", choices = MBImagelist)	    
	    else:
                config.usage.mbimageversion = ConfigSelection(default="6.1", choices = MBImagelist)
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
        mypixmap = mypath + 'egami.png'
        png = LoadPixmap(mypixmap)
        name = _('Egami')
        desc = _('Download latest Egami Image')
        idx = 'egami'
        res = (name,
         png,
         idx,
         desc)
        self.list.append(res)
        mypixmap = mypath + 'openatv.png'
        png = LoadPixmap(mypixmap)
        name = _('OpenATV-6.0')
        desc = _('Download latest OpenATV Image')
        idx = 'openatv-6.0'
        res = (name,
         png,
         idx,
         desc) 
        self.list.append(res)
        mypixmap = mypath + 'openpli.png'
        png = LoadPixmap(mypixmap)
        name = _('OpenPLi')
        desc = _('Download latest OpenPLi Image')
        idx = 'openpli'
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
        mypixmap = mypath + 'satdreamgr.png'
        png = LoadPixmap(mypixmap)
        name = _('SatDreamgr')
        desc = _('Download latest SatDreamgr Image')
        idx = 'satdreamgr'
        res = (name,
         png,
         idx,
         desc)
        self.list.append(res)
        mypixmap = mypath + 'hdmu.png'
        png = LoadPixmap(mypixmap)
        name = _('Hdmu')
        desc = _('Download latest SatDreamgr Image')
        idx = 'hdmu'
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
        mypixmap = mypath + 'opendroid.png'
        png = LoadPixmap(mypixmap)
        name = _('Opendroid')
        desc = _('Download latest Opendroid Image')
        idx = 'opendroid'
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
        if boxname in ('ax51'):
            BRANDOEM = 'ax'
        elif boxname in ('gb800seplus', 'gbquadplus', 'gbquad4k', 'gbue4k', 'gbultraue', 'gbx1', 'gbx2', 'gbx3'):
            BRANDOEM = 'gigablue'
        elif boxname in ('mutant51'):
            BRANDOEM = 'mutant'
        elif boxname in ('sf128', 'sf208', 'sf3038', 'sf4008'):
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
        elif boxname in ('sf98', 'sf108', 'sf128', 'sf138', 'sf208', 'sf228', 'sf3038', 'sf4008'):
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
        if self.distro == 'egami':
            self.feed = 'egami'
            self.feedurl = 'http://image.egami-image.com'
        elif self.distro == 'opennfr':
            self.feed = 'opennfr'
            self.feedurl = 'http://dev.nachtfalke.biz/nfr/feeds/%s/images' %ImageVersion
        elif self.distro == 'openatv-6.0':
            self.feed = 'openatv'
            self.feedurl = 'http://images.mynonpublic.com/openatv/%s' %ImageVersion
        elif self.distro == 'openvix':
            self.feed = 'openvix'
            self.feedurl = 'http://openvix.co.uk'
        elif self.distro == 'pure2':
            self.feed = 'pure2'
            self.feedurl = 'http://pur-e2.club/OU/images/?dir=6.1' 
        elif self.distro == 'opendroid':
            self.feed = 'opendroid'
            self.feedurl = 'http://images.opendroid.org/%s' %ImageVersion                          
        elif self.distro == 'openpli':
            self.feed = 'openpli'
            self.feedurl = 'http://openpli.org/download'
        elif self.distro == 'hdmu':
            self.feed = 'hdmu'
            self.feedurl = 'http://www.hdmedia-universe.com/board/pages.php?pageid=1&'            
        elif self.distro == 'openhdf':
            self.feed = 'openhdf'
            if ImageVersion == "5.5":
                hdfImageVersion = "v55"
            elif ImageVersion == "6.1":
                hdfImageVersion = "v60"
            elif ImageVersion == "6.2":
                hdfImageVersion = "v62"
            else:
                hdfImageVersion = "v61"                                            
            self.feedurl = 'http://%s.hdfreaks.cc/%s' % (hdfImageVersion, boxname)
            self.feedurl1 = 'http://%s.hdfreaks.cc' % hdfImageVersion		
        elif self.distro == 'openeight':
            self.feed = 'openeight'
            self.feedurl = 'http://openeight.de'
        elif self.distro == 'satdreamgr':
            if distri == "vuplus":
                distri = "vu"           
            self.feed = 'satdreamgr'
            self.feedurl = 'http://sgcpm.com/satdreamgr-images-experimental/%s/%s' % (distri, boxname)         
        else:
            self.feed = 'opennfr'
            self.feedurl = 'http://dev.nachtfalke.biz/nfr/feeds/6.0/images'
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
        urlbox = getBoxType() 
        if self.distro == 'openatv-6.0' or self.distro == 'opennfr' or self.distro == 'openhdf' or self.distro == 'satdreamgr':
            req = urllib2.Request(self.feedurl)
            stb = 'no Image for this Box on this Side'
            try:
                    response = urllib2.urlopen(req)
                    tmp = response.readlines()
                    for line in tmp:
                        if '<a href="' in line:
                            if box in line:
                                stb = '1'
                                break
            except:
                    stb = 'no Image for this Box on this Side'
        if self.distro == 'egami':
            if box == "ax51":
                if box in ('ax51'):
                    box = 'ax51'
                    urlbox = 'hd51'
                    stb = '1'
            else:
                self.feedurl1 = self.feedurl + "/index.php?open=" + box
                req = urllib2.Request(self.feedurl1)
                stb = 'no Image for this Box on this Side'
                try:
                        response = urllib2.urlopen(req)
                        tmp = response.readlines()
                        for line in tmp:
                            if '<a href="' in line:
                                if box in line:
                                    stb = '1'
                                    break
                except:
                        stb = 'no Image for this Box on this Side'                       
        if self.distro == 'hdmu':
            self.feedurl1 = self.feedurl + "box=" + box
            req = urllib2.Request(self.feedurl1)
            stb = 'no Image for this Box on this Side'
            try:
                    response = urllib2.urlopen(req)
                    tmp = response.readlines()
                    for line in tmp:
                        if '<a href="' in line:
                            if box and "images/arm" in line:
                                stb = '1'
                                break
            except:
                    stb = 'no Image for this Box on this Side'
        if self.distro == 'pure2':
            self.feedurl1 = self.feedurl + "/" + BRANDOEM
            req = urllib2.Request(self.feedurl1)
            stb = 'no Image for this Box on this Side'
            try:
                    response = urllib2.urlopen(req)
                    tmp = response.readlines()
                    for line in tmp:
                        if '<a href="' in line:
                            if box in line:
                                stb = '1'
                                break
            except:
                    stb = 'no Image for this Box on this Side'
        if self.distro == 'opendroid':
            if box == "ax51":
	            box = "mutant51"
	    self.feedurl1 = self.feedurl + "/" + BRANDOEMDROID + '/index.php?dir=' + MASCHINEBUILD 
            req = urllib2.Request(self.feedurl1)
            stb = 'no Image for this Box on this Side'
            try:
                    response = urllib2.urlopen(req)
                    tmp = response.readlines()
                    for line in tmp:
                        if "<a href='" in line:
                            if box in line:
                                stb = '1'
                                break
            except:
                    stb = 'no Image for this Box on this Side'                                                                
        if self.distro == 'openvix':
            if box in ('vusolo4k', 'mutant51', 'gbquad4k'):
                if box in ('vusolo4k'):
                    box = 'vusolo4k'
                    urlbox = 'Vu+Solo4K'
                    stb = '1'
                elif box in ('mutant51'):
                    box = 'mutant51'
                    urlbox = 'Mutant-HD51'
                    stb = '1'
                elif box in ('gbquad4k'):
                    box = 'gbquad4k'
                    urlbox = 'GiGaBlue-UHD-QUAD-4K'
                    stb = '1'
            else:   
                stb = 'no Image for this Box on this Side' 
        elif self.distro == 'openpli':
            if box in ('vusolo4k', 'mutant51', 'ax51'):
                if box in ('vusolo4k'):
                    box = 'vusolo4k'
                    urlbox = 'vuplus/Solo+4K/' 
                    stb = '1'
                elif box in ('vuultimo4k'):
                    box = 'vuultimo4k'
                    urlbox = 'vuplus/Ultimo+4K/' 
                    stb = '1'                                             
                elif box in ('mutant51', 'ax51'):
                    box = 'hd51'
                    urlbox = 'mutant/hd51/' 
                    stb = '1'
                                    
            else:   
                stb = 'no Image for this Box on this Side'                
        elif self.distro == 'openeight':
            if box in ('sf4008'):
               box = 'sf4008'
               urlbox = getBoxType()               
               stb = '1'
                               
            else:   
                stb = 'no Image for this Box on this Side'
                  
        return (box, urlbox, stb)

    def green(self, ret = None):
        sel = self['imageList'].l.getCurrentSelection()
        if sel == None:
            print 'Nothing to select !!'
            return
        else:
            file_name = self.imagePath + '/' + sel
            self.filename = file_name
            self.sel = sel
            box = self.box()
            self.hide()
            if self.distro == 'openvix':
                url = self.feedurl + '/openvix-builds/' + box[1] + '/' + sel 
            elif self.distro == 'openpli':
                url = 'http://downloads.pli-images.org/builds/' + box[0] + '/' + sel
            elif self.distro == 'pure2':
                url = 'http://pur-e2.club/OU/images/6.1/' + BRANDOEM + '/' + sel
            elif self.distro == 'opendroid':
                url = self.feedurl + '/' + BRANDOEMDROID + '/' + MASCHINEBUILD + '/' + sel                       
	    elif self.distro == 'openhdf':
		url = self.feedurl + '/' + sel
	    elif self.distro == 'satdreamgr':
		url = self.feedurl + '/' + sel
	    elif self.distro == 'hdmu':
	        self.feedurl2 = 'www.hdmedia-universe.com/images/'
	        url = 'http://www.hdmedia-universe.com/images/arm/' + box[0] + '/' + sel
	    elif self.distro == 'egami':
	        if box[0] == "ax51":
	            url = 'http://image.egami-image.com/hd51/' + sel
		else: 
                    url = 'http://image.egami-image.com/' + box[0] + '/' + sel                    		
            else:
                url = self.feedurl + '/' + box[0] + '/' + sel
            print '[NFR4XBoot] Image download url: ', url
            try:
                u = urllib2.urlopen(url)
            except:
                self.session.open(MessageBox, _('The URL to this image is not correct !!'), type=MessageBox.TYPE_ERROR)
                self.close()

            f = open(file_name, 'wb')
            f.close()
            try:
                meta = u.info()
                file_size = int(meta.getheaders('Content-Length')[0])
                print 'Downloading: %s Bytes: %s' % (sel, file_size)
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
        print '[NFR4XBoot] FEED URL: ', self.feedurl
        print '[NFR4XBoot] BOXTYPE: ', box
        print '[NFR4XBoot] URL-BOX: ', urlbox        
        self.imagelist = []
        if stb != '1':
            url = self.feedurl
        elif self.distro in ('openmips', 'openatv-6.0', 'openeight'):
            url = '%s/index.php?open=%s' % (self.feedurl, box)
        elif self.distro == 'egami':
	    url = '%s/index.php?open=%s' % (self.feedurl, urlbox)
        elif self.distro == 'openvix':
            url = '%s/openvix-builds/%s' % (self.feedurl, urlbox)
        elif self.distro == 'opendroid':
            url = '%s/%s/index.php?dir=%s' % (self.feedurl, BRANDOEMDROID, MASCHINEBUILD)
        elif self.distro == 'openpli':
            url = '%s/%s' % (self.feedurl, urlbox)
        elif self.distro == 'opennfr':
            url = '%s/%s' % (self.feedurl, box)
        elif self.distro == 'openhdf':
            url = '%s/%s' % (self.feedurl1, box)
        elif self.distro == 'hdmu':
            url = '%sbox=%s' % (self.feedurl, box)
        elif self.distro == 'pure2':
            url = '%s' % (self.feedurl1)                        
	else:
            url = self.feedurl
        print '[NFR4XBoot] URL: ', url
        req = urllib2.Request(url)
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError as e:
            print 'URL ERROR: %s' % e
            return
        try:
            the_page = response.read()
        except urllib2.HTTPError as e:
            print 'HTTP download ERROR: %s' % e.code
            return
        if self.distro == 'openpli':
            lines1 = the_page.split('\n')
            for line1 in lines1:
                if '<a href="http://downloads.openpli.org/builds/' in line1:
                    lines = the_page.split('_usb.zip<')
        else:
            lines = the_page.split('\n')
        tt = len(box)
        if stb == '1':
            for line in lines:
                if self.feed == "openeight":
                    if line.find("/images/%s/" % box) > -1:
                    		t = line.find('/images/%s/' % box)
                    		self.imagelist.append(line[t+tt+9:t+tt+tt+40])
                    elif line.find("<a href='%s/" % box) > -1:
                    		t = line.find("<a href='%s/" % box)
                    		t2 = line.find("'>egami")
                    		if self.feed in 'openatv':
                    			self.imagelist.append(line[t + tt + 10:t + tt + tt + 39])
                    		elif self.feed in 'egami':
                    			self.imagelist.append(line[t + tt + 10:t2])
                    		elif self.feed in 'openmips':
                    			line = line[t + tt + 10:t + tt + tt + 40]
                    			self.imagelist.append(line)
                elif line.find("<a href='%s/" % urlbox) > -1:
                    ttt = len(urlbox)
                    t = line.find("<a href='%s/" % urlbox) 
                    t5 = line.find(".zip'")
                    self.imagelist.append(line[t + ttt + 10 :t5 + 4])                        
                elif line.find('href="openvix-') > -1:
                    t4 = line.find('openvix-')
                    t5 = line.find('.zip"')
                    self.imagelist.append(line[t4 :t5+4])
                elif line.find('file=openvixhd-') > -1:
                    t4 = line.find('file=')
                    self.imagelist.append(line[t4 + 5:-2])
                elif line.find('<a href="download.php?file=' + box + '/') > -1:
                    t4 = line.find('file=' + box)
                    t5 = line.find('.zip" class="')
                    self.imagelist.append(line[t4 + len(box) + 6:t5 + 4])
                elif line.find('<a href="6.1/' + BRANDOEM + "/" + box) > -1:
                        t4 = line.find(box + '-PurE2')
                        t5 = line.find('.zip"')
                        self.imagelist.append(line[t4 :t5+4])
                elif line.find("<a href='" + MASCHINEBUILD + "/opendroid") > -1:
                        t4 = line.find('opendroid-' + ImageVersion + '-' + box)
                        t5 = line.find(".zip'")
                        self.imagelist.append(line[t4 :t5+4])                                              
                elif line.find('href="opennfr-') > -1:
                    t4 = line.find('opennfr-')
                    t5 = line.find('.zip"')
                    self.imagelist.append(line[t4 :t5+4])                    
                elif line.find('<a href="http://www.hdmedia-universe.com/images/') > -1:
                    t4 = line.find('HDMU_')
                    t5 = line.find('.zip"')
                    if line[t4 :t5+4] != '':
                        self.imagelist.append(line[t4 :t5+4])  
                elif line.find('href="http://downloads.openpli.org' ) > -1:
                    t4 = line.find('<a href="http://downloads.openpli.org/builds/')
                    t5 = line.find('.zip"')
                    self.imagelist.append(line[t4+  len(box) + 46:t5+4])    
                elif line.find('href="openhdf-') > -1:
                    t4 = line.find('openhdf-')
                    t5 = line.find('.zip"')
                    self.imagelist.append(line[t4 :t5+4])   
                elif line.find('href="Satdreamgr-') > -1:
                    t4 = line.find('Satdreamgr-')
                    t5 = line.find('.zip"')
                    self.imagelist.append(line[t4 :t5+4])
                elif line.find("<a href='") > -1:
                    t4 = line.find('egami-')
                    t5 = line.find('.zip"')
                    self.imagelist.append(line[t4 :t5+4])                    
        else:
            self.imagelist.append(stb)
        if "" in self.imagelist:
            self.imagelist.remove('')	
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
        print '[ImageDownloadTask] downloading', self.url, 'to', self.path

    def abort(self):
        print '[ImageDownloadTask] aborting', self.url
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
