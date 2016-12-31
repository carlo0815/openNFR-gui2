from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import os
from os.path import isfile
import gettext
import platform
archcheck = platform.uname()

PluginLanguageDomain = 'NetworkBrowser'
PluginLanguagePath = 'SystemPlugins/NetworkBrowser/locale'
scantest = '/usr/lib/enigma2/python/Plugins/SystemPlugins/NetworkBrowser/netscantest'
if isfile(scantest):
    os.system("rm -f /usr/lib/enigma2/python/Plugins/SystemPlugins/NetworkBrowser/netscan.so")
    if archcheck[4] == "mips":
        os.system("rm -f /usr/lib/enigma2/python/Plugins/SystemPlugins/NetworkBrowser/netscantest")
        os.system("cp /usr/lib/enigma2/python/Plugins/SystemPlugins/NetworkBrowser/netscan/netscan.so.mips /usr/lib/enigma2/python/Plugins/SystemPlugins/NetworkBrowser/netscan.so")      
    elif archcheck[4] == "arm":
        os.system("rm -f /usr/lib/enigma2/python/Plugins/SystemPlugins/NetworkBrowser/netscantest")
        os.system("cp /usr/lib/enigma2/python/Plugins/SystemPlugins/NetworkBrowser/netscan/netscan.so.arm /usr/lib/enigma2/python/Plugins/SystemPlugins/NetworkBrowser/netscan.so ")

def localeInit():
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))



def _(txt):
    if gettext.dgettext(PluginLanguageDomain, txt):
        return gettext.dgettext(PluginLanguageDomain, txt)
    else:
        print '[' + PluginLanguageDomain + '] fallback to default translation for ' + txt
        return gettext.gettext(txt)


language.addCallback(localeInit())
