# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.Console import Console
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.Label import Label
import Components.config
from Components.MenuList import MenuList
from Components.config import config
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from os import path, walk
from enigma import eConsoleAppContainer, eDVBDB, eEnv
from skin import *
import os
import urllib2
import ssl
import socket
import time
import shlex, subprocess
from subprocess import Popen
from glob import glob


class IPTV_glob(Screen):
    def __init__(self, name, file):
        name = name
        file = file

    def file_filter(self, name):
        name_file = name.replace('/','_')
        name_file = name_file.replace(' ','_')
        name_file = name_file.replace('\r','')
        name_file = name_file.replace('\n','')
        name_file = name_file.replace('(','')
        name_file = name_file.replace(')','')
        return name_file

    def Convert_m3u(self, name, file):
        self.type = "TV"
        self.convert = True
        name_file_new = self.file_filter(name)
        name_file = name_file_new.lstrip('_etc_enigma2_')
        bouquetname = 'userbouquet.nfr%s.%s' %(name_file.lower(), self.type.lower())
        tmp = ''
        tmplist = []
        tmplist.append('#NAME IPTV %s (%s)' % (name_file,self.type) + '\n')
        tmplist.append('#SERVICE 1:64:0:0:0:0:0:0:0:0::%s Channels' % name_file + '\n')
        tmplist.append('#DESCRIPTION --- %s ---' % name_file + '\n')
        print "[openNFR_M3U_convert] Converting Bouquet %s" % name_file
        z = open(file, "r")
        l = z.readlines()
        z.close()
        if self.convert:
            l.pop(0) # remove first line
        else:
            for t in range(1,4): # remove first 3 lines
                l.pop(0)

        for line in l:
            if line == '':
                continue
            if line.startswith("#EXTINF:"):
                line = line.replace('#EXTINF:-1,','#DESCRIPTION: ')
                line = line.replace('#EXTINF:-1 ,','#DESCRIPTION: ')
                line = line.replace('#EXTINF:-1','#DESCRIPTION: ')
                line = line.replace('#EXTINF%3a0,','#DESCRIPTION: ')
                line = line.replace('#EXTINF:0,','#DESCRIPTION: ')
                line = line.replace('#EXTINF:-1 tvg-name=','#DESCRIPTION: ')
                line = line.replace('#EXTINF:-1 tvg-shift=2 ,','#DESCRIPTION: ')
                line = line.replace('#EXTINF:-1 group-title=','#DESCRIPTION: ')            
                line = line.replace('#EXTINF:','#DESCRIPTION: ')
                line = line.replace('tvg-name=','')
                line = line.replace('tvg-shift=2 ,','')
                line = line.replace('tvg-shift=2 tvg-logo=-TV ,','')
                line = line.replace('tvg-shift=2 tvg-logo=','')
                line = line.replace(' tvg-id="','')
                tmp = line
            else:
                if self.type.upper() == 'TV' and self.convert:
                    line = line.replace(':','%3a')
                    line = line.replace('|X-Forwarded-For=91.63.136.21','')
                    line = line.replace('rtmp%3a//$OPT%3artmp-raw=rtmp%3a','rtmp%3a')
                    line = line.replace('rtmp%3a//$OPT%3artmp-raw=rtmpe%3a','rtmpe%3a')
                    line = line.replace('rtp%3a//@','#SERVICE 1:0:1:1:1:0:820000:0:0:0:http%3a//127.0.0.1%3a4050/rtp/')
                    line = line.replace('rtp%3a//','#SERVICE 1:0:1:1:1:0:820000:0:0:0:http%3a//127.0.0.1%3a4050/rtp/')
                    line = line.replace('udp%3a//','#SERVICE 1:0:1:1:1:0:820000:0:0:0:http%3a//127.0.0.1%3a4050/udp/')                    
                    if line.startswith('rtmp') or line.startswith('rtsp') or line.startswith('mms'):
                        line = '#SERVICE 4097:0:1:0:0:0:0:0:0:0:' + line
                    if not line.startswith("#SERVICE 4097:0:1:0:0:0:0:0:0:0:rt"):
                        if line.startswith('http'):
                            line = '#SERVICE 4097:0:1:0:0:0:0:0:0:0:' + line
                    tmplist.append(line)
                    tmplist.append(tmp)
                elif self.type.upper() == 'RADIO' and self.convert:
                    line = line.replace(':','%3a')
                    line = line.replace('rtmp%3a//$OPT%3artmp-raw=rtmp%3a','rtmp%3a')
                    line = line.replace('rtmp%3a//$OPT%3artmp-raw=rtmpe%3a','rtmpe%3a')
                    line = line.replace('rtp%3a//@','#SERVICE 1:0:1:1:1:0:820000:0:0:0:http%3a//127.0.0.1%3a4050/rtp/')
                    if line.startswith('rtmp') or line.startswith('rtsp') or line.startswith('mms'):
                        line = '#SERVICE 4097:0:2:0:0:0:0:0:0:0:' + line
                    if not line.startswith("#SERVICE 4097:0:2:0:0:0:0:0:0:0:rt"):
                        if line.startswith('http'):
                            line = '#SERVICE 4097:0:2:0:0:0:0:0:0:0:' + line
                    tmplist.append(line)
                    tmplist.append(tmp)
                elif not self.convert:
                    tmplist.append(line)
                else:
                    print"[openNFR_M3U_convert] UNKNOWN TYPE: %s" %self.type


        # write bouquet file
        f = open('/etc/enigma2/' + bouquetname, 'w')
        for item in tmplist:
            if item.startswith(' '):
                continue
            else:    
                f.write("%s" % item)
        f.close()

        # check if bouquet exists in bouquet file
        ff = open('/etc/enigma2/bouquets.%s' % self.type.lower(), 'r+')
        bouquets = ff.readlines()

        found = False
        for ll in bouquets:
            if ll.find(bouquetname) > -1:
                found = True
                break

        if found:
            print "[openNFR_M3U_convert] Bouquetname exists, do nothing"
        else:
            print "[openNFR_M3U_convert] Bouquetname doesn't exists, adding it"
            nline = '#SERVICE: 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\n' % bouquetname
            ff.write(nline)
        ff.close            


class IPTV(Screen):
    skin = """
          <screen name="IPTV" position="center,center" size="1280,720" title="M3U Converter" flags="wfNoBorder">
            <widget source="global.CurrentTime" render="Label" position="1125,12" size="100,28" font="Regular; 26" halign="right" backgroundColor="background" transparent="1" foregroundColor="cyan1">
              <convert type="ClockToText">Default</convert>
            </widget>
            <widget source="global.CurrentTime" render="Label" position="905,37" size="320,25" font="Regular;20" halign="right" backgroundColor="background" transparent="1" foregroundColor="cyan1">
              <convert type="ClockToText">Format:%A, %d.%m.%Y</convert>
            </widget>
            <ePixmap position="center,center" zPosition="-10" size="1280,720" pixmap="skin_default/menu/back2b.png" />
            <ePixmap pixmap="skin_default/menu/db.png" position="848,596" size="350,44" alphatest="blend" zPosition="1" />
            <ePixmap pixmap="skin_default/menu/nfr.png" position="950,430" size="150,150" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/menu/opennfr_info.png" position="837,95" size="379,216" alphatest="on" zPosition="1" />
            <eLabel backgroundColor="grey" position="66,602" size="715,1" zPosition="0" />
            <widget name="IPTVList" position="65,98" size="715,500" zPosition="1" scrollbarMode="showOnDemand" transparent="1" />
            <widget name="text1" position="64,608" size="715,25" font="Regular;20" transparent="0" foregroundColor="cyan1" halign="center" backgroundColor="backtop" />
            <widget source="Title" render="Label" position="65,17" size="720,43" font="Regular;35" backgroundColor="backtop" transparent="1" foregroundColor="cyan1" />
            <eLabel position="837,95" zPosition="3" size="375,214" backgroundColor="unff000000" />
            <widget source="session.VideoPicture" render="Pig" position="837,95" size="375,214" backgroundColor="transparent" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/red.png" position=" 70,670" size="30,30" alphatest="blend" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="360,670" size="30,30" alphatest="blend" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="650,670" size="30,30" alphatest="blend" />
             <ePixmap pixmap="skin_default/buttons/blue.png" position="940,670" size="30,30" alphatest="blend" />   
            <widget name="key_red" position="105,672" size="240,24" zPosition="1" font="Regular;20" halign="left" backgroundColor="black" transparent="1" />
            <widget name="key_green" position="395,672" size="240,24" zPosition="1" font="Regular;20" halign="left" backgroundColor="black" transparent="1" />
            <widget name="key_yellow" position="685,672" size="240,24" zPosition="1" font="Regular;20" halign="left" backgroundColor="black" transparent="1" />
            <widget name="key_blue" position="975,672" size="240,24" zPosition="1" font="Regular;20" halign="left" backgroundColor="black" transparent="1" />    
          </screen> """  
    iptvlist =[]

    def __init__(self, session, args = None):
        self.m3ulist = []
        self.session = session
        self.Console = Console()
        self.Version = args
        Screen.__init__(self, session)
        self.m3uliststart()
        self.iptvlist = self.m3ulist
        self.iptvname = ""
        self.IPTVInstalled = False
        self.countryPath = ""
        self.actual = None
        self.type = None
        self.iptvlist.sort()
        self["IPTVList"] = MenuList(self.iptvlist)
        self["country"] = Pixmap()
        self["text1"] = Label(_("Select M3U File from /etc/enigma2 to add into TV Bouquet"))
        
        self["actions"] = ActionMap(["OkCancelActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "EPGSelectActions"],
        {
            "ok": self.ok,
            "back": self.cancel,
            "red": self.cancel,
            "green": self.ok,
            "blue": self.dload,            
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
            "yellow": self.install,
        }, -1)
        self["key_red"] = Label(_("Close"))
        self["key_green"] = Label(_("Install"))
        self["key_yellow"] = Label(_("Install all"))
        self["key_blue"] = Label(_("Download IPTV-lists"))       
        self.onLayoutFinish.append(self.layoutFinished)
        
    def m3uliststart(self):
        self.m3ulist = []
        for fAdd in glob ('/etc/enigma2/*.m3u'):
			self.m3ulist.append(fAdd)
			
    def dload(self):
        self.session.openWithCallback(self.cancel, Iptvdownload)
        
    def up(self):
        self["IPTVList"].up()
    
    def down(self):
        self["IPTVList"].down()
    
    def left(self):
        self["IPTVList"].pageUp()
    
    def right(self):
        self["IPTVList"].pageDown()       


    def layoutFinished(self):
        pass
         
    def ok(self):
        self.IPTVInstalled = True
        self.type = "TV"
        url = None
        sel = self["IPTVList"].getCurrent()
        if sel == None:
            print"[openNFR_M3U_convert] Nothing to select !!"
            return
        print"[openNFR_M3U_convert] Current selection: %s" % sel
        file = sel     
        self.IPTV_glob = IPTV_glob(sel, file)
        name_file = self.IPTV_glob.file_filter(sel)
        self.IPTV_glob.Convert_m3u(sel, file)
        self.Remove_hooks()
        infotext = _('M3U Converter\n')
        infotext += _('IPTV m3u Files convert to bouquetslist')
        infotext += _('\n\n\n')
        infotext += _('Update Bouquets and Services')
        infotext += _('Press OK or EXIT to go back !')
        
        self.session.open(MessageBox,_(infotext), MessageBox.TYPE_INFO)

    def Remove_hooks(self):
        ff = open('/etc/enigma2/bouquets.%s' % self.type.lower(), 'r+')
        bouquets = ff.readlines()
        ff.close()

        ff = open('/etc/enigma2/bouquets.%s' % self.type.lower(), 'w+')
        for line in bouquets:
            if line.find('(') > -1 or line.find(')') > -1:
                print "[openNFR_M3U_convert] Removing line %s from bouquets.tv" % line
            else:
                ff.write(line)
        ff.close()
       
    def cancel(self):
        if self.IPTVInstalled is True:
            infobox = self.session.open(MessageBox,_("Reloading Bouquets and Services..."), MessageBox.TYPE_INFO, timeout=5)
            infobox.setTitle(_("Info"))
            eDVBDB.getInstance().reloadBouquets()
            eDVBDB.getInstance().reloadServicelist()
        self.close()
            
    def install(self):
        self.IPTVInstalled = True
        self.type = "TV"
        for l in self.iptvlist:
            self.convert = True
            name_file = self.file_filter(l)
            file = l         
            self.Convert_m3u(l, file)
            infotext = _('M3U Converter\n')
            infotext += _('IPTV m3u Files convert to bouquetslist')
            infotext += _('\n\n\n')
            infotext += _('Update Bouquets and Services')
            infotext += _('Press OK or EXIT to go back !')
        
        self.Remove_hooks()
        self.session.open(MessageBox,_(infotext), MessageBox.TYPE_INFO)
        
class Iptvdownload(Screen):
            
    iptvlist =[]

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self.skinName = ["Iptvdownload", "IPTV" ]
        tlist = ["German Provider Listen", "Kodinerds Listen", "Austria Provider Listen(ungetest)", "Schweizer Provider Listen(ungetest)"]
        self.session = session
        self.Console = Console()
        self.IPTVInstalled = False
        self.Version = args
        global kodi
        Screen.__init__(self, session)
        self["IPTVList"] = MenuList(tlist)
        self["country"] = Pixmap()
        self["text1"] = Label(_("Select IPTVlists to Download"))
        
        self["actions"] = ActionMap(["OkCancelActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "EPGSelectActions"],
        {
            "ok": self.ok,
            "back": self.cancel,
            "red": self.cancel,
            "green": self.ok,
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
        }, -1)
        self["key_red"] = Label(_("Close"))
        self["key_green"] = Label(_("Openlists"))
        self.onLayoutFinish.append(self.layoutFinished)
        
        
        self["IPTVList"] = []
    	self["IPTVList"] = MenuList(tlist)		
        pass    			

    def up(self):
        self["IPTVList"].up()
    
    def down(self):
        self["IPTVList"].down()
    
    def left(self):
        self["IPTVList"].pageUp()
    
    def right(self):
        self["IPTVList"].pageDown()
        
    def layoutFinished(self):
        pass     
           
    def ok(self):
        sel = self["IPTVList"].getCurrent()
        if sel == "German Provider Listen":
            self.session.openWithCallback(self.cancel, Iptvdownloadprov)
        elif sel == "Kodinerds Listen":
            self.session.openWithCallback(self.cancel, Iptvdownloadkodi)
        elif sel == "Austria Provider Listen(ungetest)":
            self.session.openWithCallback(self.cancel, Iptvdownloadprovaustria) 
        elif sel == "Schweizer Provider Listen(ungetest)":
            self.session.openWithCallback(self.cancel, Iptvdownloadprovsuisse)             
        else:    
            print"[openNFR_M3U_convert] Nothing Select use Default"
            self.session.openWithCallback(self.cancel, Iptvdownloadprov)    

    def cancel(self):
        self.close()
            
        
        
        
class Iptvdownloadprov(IPTV):
            
    iptvlist =[]

    def __init__(self, session, args = None):
        IPTV.__init__(self, session)
        self.skinName = IPTV.skin
        tlist = ["1+1entertain-tv", "telekom-entertain", "vodafone-radioliste", "vodafone-tv-radioliste", "vodafone-tvliste",]
        self.session = session
        self.Console = Console()
        self.IPTVInstalled = False
        self.Version = args
        Screen.__init__(self, session)
        self["IPTVList"] = MenuList(tlist)
        self["country"] = Pixmap()
        self["text1"] = Label(_("Select IPTVlist to download and add into TV Bouquet"))
        
        self["actions"] = ActionMap(["OkCancelActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "EPGSelectActions"],
        {
            "ok": self.ok,
            "back": self.cancel,
            "red": self.cancel,
            "green": self.ok,
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
        }, -1)
        self["key_red"] = Label(_("Close"))
        self["key_green"] = Label(_("Install"))
        self.onLayoutFinish.append(self.layoutFinished)
        
        
        self["IPTVList"] = []
    	self["IPTVList"] = MenuList(tlist)		
        pass    			

    def up(self):
        self["IPTVList"].up()
    
    def down(self):
        self["IPTVList"].down()
    
    def left(self):
        self["IPTVList"].pageUp()
    
    def right(self):
        self["IPTVList"].pageDown()
        
    def layoutFinished(self):
        pass     
           
    def ok(self):
        import commands
        resultpxy = commands.getoutput('/usr/bin/opkg list_installed udpxy')
        if 'udpxy' in resultpxy:
            print "udpxy is installed"
        else:
            os.system('/usr/bin/opkg install udpxy')            
        self.IPTVInstalled = True
        self.type = "TV"
        sel1 = self["IPTVList"].getCurrent() + ".m3u"
        if sel1 == None:
            print"[openNFR_M3U_convert] Nothing to select !!"
            return
        print"[openNFR_M3U_convert] Current selection: %s" % sel1
        name_file1 = sel1
        cmd = ""
        cmd += "opkg install --force-overwrite curl;"
        cmd += "curl --output /etc/enigma2/%s https://raw.githubusercontent.com/carlo0815/ProvLists/master/%s > /dev/null 2>&1;" % (name_file1,name_file1) 
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)        
        process.wait()
        sel = "/etc/enigma2/" + sel1
        file = sel
        self.IPTV_glob = IPTV_glob(sel, file)
        name_file = self.IPTV_glob.file_filter(sel)
        self.IPTV_glob.Convert_m3u(sel, file)         
        self.Remove_hooks()
        infotext = _('M3U Converter\n')
        infotext += _('IPTV m3u Files convert to bouquetslist')
        infotext += _('\n\n\n')
        infotext += _('Update Bouquets and Services')
        infotext += _('Press OK or EXIT to go back !')
        
        self.session.open(MessageBox,_(infotext), MessageBox.TYPE_INFO)		

    def Remove_hooks(self):
        ff = open('/etc/enigma2/bouquets.%s' % self.type.lower(), 'r+')
        bouquets = ff.readlines()
        ff.close()

        ff = open('/etc/enigma2/bouquets.%s' % self.type.lower(), 'w+')
        for line in bouquets:
            if line.find('(') > -1 or line.find(')') > -1:
                print "[openNFR_M3U_convert] Removing line %s from bouquets.tv" % line
            else:
                ff.write(line)
        ff.close()
       
    def cancel(self):
        if self.IPTVInstalled is True:
            infobox = self.session.open(MessageBox,_("Reloading Bouquets and Services..."), MessageBox.TYPE_INFO, timeout=5)
            infobox.setTitle(_("Info"))
            eDVBDB.getInstance().reloadBouquets()
            eDVBDB.getInstance().reloadServicelist()
        self.close()
            
    def install(self):
        self.IPTVInstalled = True
        self.type = "TV"
        for l in self.iptvlist:
            self.convert = True
            name_file = self.file_filter(l)
            file = l         
            self.Convert_m3u(l, file)
            infotext = _('M3U Converter\n')
            infotext += _('IPTV m3u Files convert to bouquetslist')
            infotext += _('\n\n\n')
            infotext += _('Update Bouquets and Services')
            infotext += _('Press OK or EXIT to go back !')
        
        self.Remove_hooks()
        self.session.open(MessageBox,_(infotext), MessageBox.TYPE_INFO)
        
class Iptvdownloadprovsuisse(IPTV):
            
    iptvlist =[]

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self.skinName = IPTV.skin 
        tlist = ["swisscom2017"]
        self.session = session
        self.Console = Console()
        self.IPTVInstalled = False
        self.Version = args
        Screen.__init__(self, session)
        self["IPTVList"] = MenuList(tlist)
        self["country"] = Pixmap()
        self["text1"] = Label(_("Select IPTVlist to download and add into TV Bouquet"))
        
        self["actions"] = ActionMap(["OkCancelActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "EPGSelectActions"],
        {
            "ok": self.ok,
            "back": self.cancel,
            "red": self.cancel,
            "green": self.ok,
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
        }, -1)
        self["key_red"] = Label(_("Close"))
        self["key_green"] = Label(_("Install"))
        self.onLayoutFinish.append(self.layoutFinished)
        
        
        self["IPTVList"] = []
    	self["IPTVList"] = MenuList(tlist)		
        pass    			

    def up(self):
        self["IPTVList"].up()
    
    def down(self):
        self["IPTVList"].down()
    
    def left(self):
        self["IPTVList"].pageUp()
    
    def right(self):
        self["IPTVList"].pageDown()
        
    def layoutFinished(self):
        pass     
           
    def ok(self):
        import commands
        resultpxy = commands.getoutput('/usr/bin/opkg list_installed udpxy')
        if 'udpxy' in resultpxy:
            print "udpxy is installed"
        else:
            os.system('/usr/bin/opkg install udpxy')            
        self.IPTVInstalled = True
        self.type = "TV"
        sel1 = self["IPTVList"].getCurrent() + ".m3u"
        if sel1 == None:
            print"[openNFR_M3U_convert] Nothing to select !!"
            return
        print"[openNFR_M3U_convert] Current selection: %s" % sel1
        name_file1 = sel1
        cmd = ""
        cmd += "opkg install --force-overwrite curl;"
        cmd += "curl --output /etc/enigma2/%s https://raw.githubusercontent.com/carlo0815/ProvLists/master/%s > /dev/null 2>&1;" % (name_file1,name_file1) 
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)        
        process.wait()
        sel = "/etc/enigma2/" + sel1
        file = sel 
        self.IPTV_glob = IPTV_glob(sel, file)
        name_file = self.IPTV_glob.file_filter(sel)
        self.IPTV_glob.Convert_m3u(sel, file)
        self.Remove_hooks()
        infotext = _('M3U Converter\n')
        infotext += _('IPTV m3u Files convert to bouquetslist')
        infotext += _('\n\n\n')
        infotext += _('Update Bouquets and Services')
        infotext += _('Press OK or EXIT to go back !')
        
        self.session.open(MessageBox,_(infotext), MessageBox.TYPE_INFO)		

    def Remove_hooks(self):
        ff = open('/etc/enigma2/bouquets.%s' % self.type.lower(), 'r+')
        bouquets = ff.readlines()
        ff.close()

        ff = open('/etc/enigma2/bouquets.%s' % self.type.lower(), 'w+')
        for line in bouquets:
            if line.find('(') > -1 or line.find(')') > -1:
                print "[openNFR_M3U_convert] Removing line %s from bouquets.tv" % line
            else:
                ff.write(line)
        ff.close()
       
    def cancel(self):
        if self.IPTVInstalled is True:
            infobox = self.session.open(MessageBox,_("Reloading Bouquets and Services..."), MessageBox.TYPE_INFO, timeout=5)
            infobox.setTitle(_("Info"))
            eDVBDB.getInstance().reloadBouquets()
            eDVBDB.getInstance().reloadServicelist()
        self.close()
            
    def install(self):
        self.IPTVInstalled = True
        self.type = "TV"
        for l in self.iptvlist:
            self.convert = True
            name_file = self.file_filter(l)
            file = l         
            self.Convert_m3u(l, file)
            infotext = _('M3U Converter\n')
            infotext += _('IPTV m3u Files convert to bouquetslist')
            infotext += _('\n\n\n')
            infotext += _('Update Bouquets and Services')
            infotext += _('Press OK or EXIT to go back !')
        
        self.Remove_hooks()
        self.session.open(MessageBox,_(infotext), MessageBox.TYPE_INFO)         
        
class Iptvdownloadprovaustria(IPTV):
            
    iptvlist =[]

    def __init__(self, session, args = None):
        IPTV.__init__(self, session)
        self.skinName = IPTV.skin 
        tlist = ["A1TV_Basis", "A1TV_Basis_HD", "A1TV_Radio-Sender", "A1TV_Plus_HD", "A1TV_Plus", "A1TV_ORF_Radio-Sender", "A1TV_HD"]
        self.session = session
        self.Console = Console()
        self.IPTVInstalled = False
        self.Version = args
        Screen.__init__(self, session)
        self["IPTVList"] = MenuList(tlist)
        self["country"] = Pixmap()
        self["text1"] = Label(_("Select IPTVlist to download and add into TV Bouquet"))
        
        self["actions"] = ActionMap(["OkCancelActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "EPGSelectActions"],
        {
            "ok": self.ok,
            "back": self.cancel,
            "red": self.cancel,
            "green": self.ok,
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
        }, -1)
        self["key_red"] = Label(_("Close"))
        self["key_green"] = Label(_("Install"))
        self.onLayoutFinish.append(self.layoutFinished)
        
        
        self["IPTVList"] = []
    	self["IPTVList"] = MenuList(tlist)		
        pass    			

    def up(self):
        self["IPTVList"].up()
    
    def down(self):
        self["IPTVList"].down()
    
    def left(self):
        self["IPTVList"].pageUp()
    
    def right(self):
        self["IPTVList"].pageDown()
        
    def layoutFinished(self):
        pass     
           
    def ok(self):
        import commands
        resultpxy = commands.getoutput('/usr/bin/opkg list_installed udpxy')
        if 'udpxy' in resultpxy:
            print "udpxy is installed"
        else:
            os.system('/usr/bin/opkg install udpxy')            
        self.IPTVInstalled = True
        self.type = "TV"
        sel1 = self["IPTVList"].getCurrent() + ".m3u"
        if sel1 == None:
            print"[openNFR_M3U_convert] Nothing to select !!"
            return
        print"[openNFR_M3U_convert] Current selection: %s" % sel1
        name_file1 = sel1
        cmd = ""
        cmd += "opkg install --force-overwrite curl;"
        cmd += "curl --output /etc/enigma2/%s https://raw.githubusercontent.com/carlo0815/ProvLists/master/%s > /dev/null 2>&1;" % (name_file1,name_file1) 
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)        
        process.wait()
        sel = "/etc/enigma2/" + sel1
        file = sel 
        self.IPTV_glob = IPTV_glob(sel, file)
        name_file = self.IPTV_glob.file_filter(sel)
        self.IPTV_glob.Convert_m3u(sel, file)
        self.Remove_hooks()
        infotext = _('M3U Converter\n')
        infotext += _('IPTV m3u Files convert to bouquetslist')
        infotext += _('\n\n\n')
        infotext += _('Update Bouquets and Services')
        infotext += _('Press OK or EXIT to go back !')
        
        self.session.open(MessageBox,_(infotext), MessageBox.TYPE_INFO)		

    def Remove_hooks(self):
        ff = open('/etc/enigma2/bouquets.%s' % self.type.lower(), 'r+')
        bouquets = ff.readlines()
        ff.close()

        ff = open('/etc/enigma2/bouquets.%s' % self.type.lower(), 'w+')
        for line in bouquets:
            if line.find('(') > -1 or line.find(')') > -1:
                print "[openNFR_M3U_convert] Removing line %s from bouquets.tv" % line
            else:
                ff.write(line)
        ff.close()
       
    def cancel(self):
        if self.IPTVInstalled is True:
            infobox = self.session.open(MessageBox,_("Reloading Bouquets and Services..."), MessageBox.TYPE_INFO, timeout=5)
            infobox.setTitle(_("Info"))
            eDVBDB.getInstance().reloadBouquets()
            eDVBDB.getInstance().reloadServicelist()
        self.close()
            
    def install(self):
        self.IPTVInstalled = True
        self.type = "TV"
        for l in self.iptvlist:
            self.convert = True
            name_file = self.file_filter(l)
            file = l         
            self.Convert_m3u(l, file)
            infotext = _('M3U Converter\n')
            infotext += _('IPTV m3u Files convert to bouquetslist')
            infotext += _('\n\n\n')
            infotext += _('Update Bouquets and Services')
            infotext += _('Press OK or EXIT to go back !')
        
        self.Remove_hooks()
        self.session.open(MessageBox,_(infotext), MessageBox.TYPE_INFO)        

class Iptvdownloadkodi(IPTV):
            
    iptvlist =[]

    def __init__(self, session, args = None):
        IPTV.__init__(self, session)
        self.skinName = IPTV.skin   
        tlist = ["iptv_clean_extra", "iptv_clean_full", "iptv_clean_int", "iptv_clean_radio", "iptv_clean_tv"]
        self.session = session        
        self.Console = Console()
        self.IPTVInstalled = False
        self.Version = args
        Screen.__init__(self, session)
        self["IPTVList"] = MenuList(tlist)
        self["country"] = Pixmap()
        self["text1"] = Label(_("Select IPTVlist to download and add into TV Bouquet"))
        
        self["actions"] = ActionMap(["OkCancelActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "EPGSelectActions"],
        {
            "ok": self.ok,
            "back": self.cancel,
            "red": self.cancel,
            "green": self.ok,
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
        }, -1)
        self["key_red"] = Label(_("Close"))
        self["key_green"] = Label(_("Install"))
        self.onLayoutFinish.append(self.layoutFinished)
        
        
        self["IPTVList"] = []
    	self["IPTVList"] = MenuList(tlist)		
        pass    			

    def up(self):
        self["IPTVList"].up()
    
    def down(self):
        self["IPTVList"].down()
    
    def left(self):
        self["IPTVList"].pageUp()
    
    def right(self):
        self["IPTVList"].pageDown()
        
    def layoutFinished(self):
        pass     
           
    def ok(self):
        self.IPTVInstalled = True
        self.type = "TV"
        sel1 = self["IPTVList"].getCurrent() + ".m3u"
        if sel1 == None:
            print"[openNFR_M3U_convert] Nothing to select !!"
            return
        print"[openNFR_M3U_convert] Current selection: %s" % sel1
        name_file1 = sel1
        cmd = ""
        cmd += "opkg install --force-overwrite curl;"
        cmd += "curl --output /etc/enigma2/%s https://raw.githubusercontent.com/jnk22/kodinerds-iptv/master/clean/%s > /dev/null 2>&1;" % (name_file1,name_file1)        
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)        
        process.wait()
        sel = "/etc/enigma2/" + sel1
        file = sel 
        self.IPTV_glob = IPTV_glob(sel, file)
        name_file = self.IPTV_glob.file_filter(sel)
        self.IPTV_glob.Convert_m3u(sel, file)
        self.Remove_hooks()
        infotext = _('M3U Converter\n')
        infotext += _('IPTV m3u Files convert to bouquetslist')
        infotext += _('\n\n\n')
        infotext += _('Update Bouquets and Services')
        infotext += _('Press OK or EXIT to go back !')
        
        self.session.open(MessageBox,_(infotext), MessageBox.TYPE_INFO)		

    def Remove_hooks(self):
        ff = open('/etc/enigma2/bouquets.%s' % self.type.lower(), 'r+')
        bouquets = ff.readlines()
        ff.close()

        ff = open('/etc/enigma2/bouquets.%s' % self.type.lower(), 'w+')
        for line in bouquets:
            if line.find('(') > -1 or line.find(')') > -1:
                print "[openNFR_M3U_convert] Removing line %s from bouquets.tv" % line
            else:
                ff.write(line)
        ff.close()
       
    def cancel(self):
        if self.IPTVInstalled is True:
            infobox = self.session.open(MessageBox,_("Reloading Bouquets and Services..."), MessageBox.TYPE_INFO, timeout=5)
            infobox.setTitle(_("Info"))
            eDVBDB.getInstance().reloadBouquets()
            eDVBDB.getInstance().reloadServicelist()
        self.close()
            
    def install(self):
        self.IPTVInstalled = True
        self.type = "TV"
        for l in self.iptvlist:
            self.convert = True
            name_file = self.file_filter(l)
            file = l         
            self.Convert_m3u(l, file)
            infotext = _('M3U Converter\n')
            infotext += _('IPTV m3u Files convert to bouquetslist')
            infotext += _('\n\n\n')
            infotext += _('Update Bouquets and Services')
            infotext += _('Press OK or EXIT to go back !')
        
        self.Remove_hooks()
        self.session.open(MessageBox,_(infotext), MessageBox.TYPE_INFO)       
                      
