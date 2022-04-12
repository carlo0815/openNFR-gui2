from Plugins.Plugin import PluginDescriptor
from Components.config import config
import shlex
import subprocess
import os
from Components.Console import Console
from Components.About import about
AboutText = "127.0.0.1"
eth0 = about.getIfConfig('eth0')
if 'addr' in eth0:
	AboutText = eth0['addr']
eth1 = about.getIfConfig('eth1')
if 'addr' in eth1:
	AboutText = eth1['addr']
ra0 = about.getIfConfig('ra0')
if 'addr' in ra0:
	AboutText =ra0['addr']
wlan0 = about.getIfConfig('wlan0')
if 'addr' in wlan0:
	AboutText = wlan0['addr']
wlan1 = about.getIfConfig('wlan1')
if 'addr' in wlan1:
	AboutText = wlan1['addr']
port1 = config.Fileload.fileuploadport.value
port2 = config.Fileload.filedeleteport.value
xcmd = 'python3 -O /usr/lib/enigma2/python/Plugins/Extensions/FileLoad/upload.py %s %s %s' %(port1,port2,AboutText)
xcmd1 = 'python3 -O /usr/lib/enigma2/python/Plugins/Extensions/FileLoad/delete.py %s %s %s' %(port2,port1,AboutText)
xcmd2 = 'python3 -O /usr/lib/enigma2/python/Plugins/Extensions/FileLoad/upload.pyc %s %s %s' %(port1,port2,AboutText)
xcmd3 = 'python3 -O /usr/lib/enigma2/python/Plugins/Extensions/FileLoad/delete.pyc %s %s %s' %(port2,port1,AboutText)
cmd = shlex.split(xcmd)
cmd1 = shlex.split(xcmd1)
cmd2 = shlex.split(xcmd2)
cmd3 = shlex.split(xcmd3)
extScript = subprocess.Popen(cmd,shell=False)
extScript = subprocess.Popen(cmd1,shell=False)
extScript = subprocess.Popen(cmd2,shell=False)
extScript = subprocess.Popen(cmd3,shell=False)
def Plugins(**kwargs):
    return PluginDescriptor()
