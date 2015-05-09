# Embedded file name: /usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/__init__.py
import Plugins.Plugin
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigInteger, ConfigSubList, ConfigSubDict, ConfigText, configfile, ConfigYesNo
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import os, gettext
PluginLanguageDomain = 'OpenNFR-2Mainmenu'
PluginLanguagePath = 'Extensions/Mainmenu2/locale'
config.plugins.um_globalsettings = ConfigSubsection()
config.plugins.um_globalsettings.networkinterface = ConfigYesNo(default=False)
config.plugins.um_globalsettings.telnetcommand = ConfigYesNo(default=False)
config.plugins.um_globalsettings.softwareupdate = ConfigYesNo(default=False)
config.plugins.um_globalsettings.softwaremanagersetup = ConfigYesNo(default=False)
config.plugins.um_globalsettings.Skin = ConfigYesNo(default=False)
config.plugins.um_globalsettings.Mediacenter = ConfigYesNo(default=False)
config.plugins.um_globalsettings.Weather = ConfigYesNo(default=False)

def localeInit():
    lang = language.getLanguage()[:2]
    os.environ['LANGUAGE'] = lang
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))

def _(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t

localeInit()
language.addCallback(localeInit)
