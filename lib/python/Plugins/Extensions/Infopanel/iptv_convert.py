# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Screens.Console import Console
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Console import Console
from Components.Sources.StaticText import StaticText
from Components.Label import Label
import Components.config
from Components.MenuList import MenuList
from Components.config import config
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
#from locale import _
from os import path, walk
from enigma import eConsoleAppContainer, eDVBDB, eEnv
from skin import *
import os
import urllib2
import ssl
import socket
from glob import glob

class IPTV(Screen):
    skin = """
        <screen name="IPTV" position="center,center" size="820,450" title="M3U Converter" >
	<ePixmap position="0,0" zPosition="-1" size="820,450" backgroundColor="#ff000000" />
	<widget name="text1" position="0,70" size="820,26" zPosition="2" foregroundColor="#FFE500" font="Regular;22" halign="center" transparent="1" />
	<widget name="IPTVList" position="90,130" size="310,200" zPosition="2" backgroundColor="#000000" scrollbarMode="showOnDemand" enableWrapAround="1" transparent="1" />
	<ePixmap name="red" pixmap="skin_default/buttons/red.png" position="10,400" zPosition="1" size="40,40" transparent="1" alphatest="on" />
	<ePixmap name="green" pixmap="skin_default/buttons/green.png" position="160,400" zPosition="1" size="40,40" transparent="1" alphatest="on" />
	<ePixmap name="yellow" pixmap="skin_default/buttons/yellow.png" position="320,400" zPosition="1" size="40,40" transparent="1" alphatest="on" />
	<widget name="key_red" position="55,407" zPosition="2" size="100,25" valign="center" halign="left" font="Regular;21" transparent="1" shadowColor="#000000" shadowOffset="-1,-1" />
	<widget name="key_green" position="205,407" zPosition="2" size="120,25" valign="center" halign="left" font="Regular;21" transparent="1" shadowColor="#000000" shadowOffset="-1,-1" />
	<widget name="key_yellow" position="365,407" zPosition="2" size="180,25" valign="center" halign="left" font="Regular;21" transparent="1" shadowColor="#000000" shadowOffset="-1,-1" />
	</screen>"""
            
    iptvlist =[]

    def __init__(self, session, args = None):

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
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
            "yellow": self.install,
        }, -1)
        self["key_red"] = Label(_("Close"))
        self["key_green"] = Label(_("Install"))
        self["key_yellow"] = Label(_("Install all"))
        self.onLayoutFinish.append(self.layoutFinished)
        
    def m3uliststart(self):
        self.m3ulist = []
        for fAdd in glob ('/etc/enigma2/*.m3u'):
			self.m3ulist.append(fAdd)

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
        name_file = self.file_filter(sel)
        self.Convert_m3u(sel, file)
        self.Remove_hooks()
        infotext = _('M3U Converter\n')
        infotext += _('IPTV m3u Files convert to bouquetslist')
        infotext += _('\n\n\n')
        infotext += _('Update Bouquets and Services')
        infotext += _('Press OK or EXIT to go back !')
        
        self.session.open(MessageBox,_(infotext), MessageBox.TYPE_INFO)

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
        
        
