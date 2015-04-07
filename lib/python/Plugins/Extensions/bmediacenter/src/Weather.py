from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Label import Label
from Components.Pixmap import Pixmap
from Tools.Directories import fileExists
from urllib import quote
from urllib2 import Request, urlopen, URLError, HTTPError
from xml.dom import minidom, Node
from enigma import loadPic, eTimer, gFont, getDesktop
from Components.config import config, ConfigSubsection, ConfigYesNo
config.plugins.YahooWeather = ConfigSubsection()
config.plugins.YahooWeather.compactskin = ConfigYesNo(default=True)
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import os, gettext
PluginLanguageDomain = 'YahooWeather'
PluginLanguagePath = 'Extensions/BMediaCenter/locale'

def localeInit():
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


def _(txt):
    if gettext.dgettext(PluginLanguageDomain, txt):
        return gettext.dgettext(PluginLanguageDomain, txt)
    else:
        print '[' + PluginLanguageDomain + '] fallback to default translation for ' + txt
        return gettext.gettext(txt)


language.addCallback(localeInit())
try:
    from Search_Id import *
except:
    pass

import gettext

def _(txt):
    t = gettext.dgettext('YahooWeather', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


class MeteoMain(Screen):

    def __init__(self, session):
        from enigma import addFont
        addFont('/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Font/weather.ttf', 'weather', 87, 1)
        if config.plugins.YahooWeather.compactskin.value == True:
            path = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Skin/WeatherCompact.xml'
            with open(path, 'r') as f:
                self.skin = f.read()
                f.close()
        else:
            path = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Skin/Weather.xml'
            with open(path, 'r') as f:
                self.skin = f.read()
                f.close()
        Screen.__init__(self, session)
        self.skinName = ['YahooWeather']
        self['lab1'] = Label(_('Retrieving data ...'))
        self['5day'] = Label(_('5 Day Weather Forecast'))
        self['lab1b'] = Label('')
        self['lab2'] = Label('')
        self['lab3'] = Label('')
        self['lab4'] = Label('')
        self['lab4b'] = Label('')
        self['lab5'] = Pixmap()
        self['lab6'] = Label('')
        self['lab7'] = Label('')
        self['lab7b'] = Label('')
        self['lab8'] = Label('')
        self['lab8b'] = Label('')
        self['lab9'] = Label('')
        self['lab9b'] = Label('')
        self['lab10'] = Label('')
        self['lab10b'] = Label('')
        self['lab11'] = Label('')
        self['lab11b'] = Label('')
        self['lab12'] = Label('')
        self['lab12b'] = Label('')
        self['lab13'] = Label('')
        self['lab14'] = Label('')
        self['lab14b'] = Label('')
        self['lab15'] = Label('')
        self['lab15b'] = Label('')
        self['lab16'] = Label('')
        self['lab17'] = Pixmap()
        self['lab18'] = Label('')
        self['lab19'] = Label('')
        self['lab19b'] = Label('')
        self['lab20'] = Label('')
        self['lab20b'] = Label('')
        self['lab21'] = Label('')
        self['lab22'] = Pixmap()
        self['lab23'] = Label('')
        self['lab24'] = Label('')
        self['lab24b'] = Label('')
        self['lab25'] = Label('')
        self['lab25b'] = Label('')
        self['lab26'] = Label('')
        self['lab26b'] = Label('')
        self['lab27'] = Label('')
        self['lab27b'] = Label('')
        self['lab28'] = Pixmap()
        self['lab28a'] = Label('')
        self['Key_Red'] = Label(_('Change city'))
        self['Key_Green'] = Label(_('Change skin'))
        self['3lab22'] = Pixmap()
        self['3lab19'] = Label('')
        self['3lab19b'] = Label('')
        self['3lab20'] = Label('')
        self['3lab20b'] = Label('')
        self['3lab18'] = Label('')
        self['3lab21'] = Label('')
        self['4lab22'] = Pixmap()
        self['4lab19'] = Label('')
        self['4lab19b'] = Label('')
        self['4lab20'] = Label('')
        self['4lab20b'] = Label('')
        self['4lab18'] = Label('')
        self['4lab21'] = Label('')
        self['5lab22'] = Pixmap()
        self['5lab19'] = Label('')
        self['5lab19b'] = Label('')
        self['5lab20'] = Label('')
        self['5lab20b'] = Label('')
        self['5lab18'] = Label('')
        self['5lab21'] = Label('')
        self['daydate0'] = Label('')
        self['daydate1'] = Label('')
        self['daydate2'] = Label('')
        self['daydate3'] = Label('')
        self['daydate4'] = Label('')
        self['actions'] = ActionMap(['WizardActions', 'ColorActions', 'MenuActions'], {'red': self.key_red,
         'menu': self.key_red,
         'green': self.key_green,
         'back': self.exit,
         'ok': self.exit})
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.startConnection)
        self.onShow.append(self.startShow)
        self.onClose.append(self.delTimer)
        self.bhv = 2
    def exit(self):
        self.session.nav.stopService()
        self.close()        

    def startShow(self):
        self.activityTimer.start(0, False)

    def startConnection(self):
        self.activityTimer.stop()
        self.updateInfo()

    def updateInfo(self):
        myurl = self.get_Url()
        req = Request(myurl)
        try:
            handler = urlopen(req)
        except HTTPError as e:
            maintext = 'Error: connection failed !'
        except URLError as e:
            maintext = 'Error: Page not available !'
        else:
            dom = minidom.parse(handler)
            handler.close()
            maintext = ''
            tmptext = ''
            if dom:
                weather_data = {}
                weather_data['title'] = dom.getElementsByTagName('title')[0].firstChild.data
                txt = str(weather_data['title'])
                if txt.find('Error') != -1 or self.bhv < 2:
                    self['lab1'].setText(_('Sorry, wrong WOEID'))
                    return
                ns_data_structure = {'location': ('city', 'region', 'country'),
                 'units': ('temperature', 'distance', 'pressure', 'speed'),
                 'wind': ('chill', 'direction', 'speed'),
                 'atmosphere': ('humidity', 'visibility', 'pressure', 'rising'),
                 'astronomy': ('sunrise', 'sunset'),
                 'condition': ('text', 'code', 'temp', 'date')}
                for tag, attrs in ns_data_structure.items():
                    weather_data[tag] = self.xml_get_ns_yahoo_tag(dom, 'http://xml.weather.yahoo.com/ns/rss/1.0', tag, attrs)

                weather_data['geo'] = {}
                weather_data['geo']['lat'] = dom.getElementsByTagName('geo:lat')[0].firstChild.data
                weather_data['geo']['long'] = dom.getElementsByTagName('geo:long')[0].firstChild.data
                weather_data['condition']['title'] = dom.getElementsByTagName('item')[0].getElementsByTagName('title')[0].firstChild.data
                weather_data['html_description'] = dom.getElementsByTagName('item')[0].getElementsByTagName('description')[0].firstChild.data
                forecasts = []
                for forecast in dom.getElementsByTagNameNS('http://xml.weather.yahoo.com/ns/rss/1.0', 'forecast'):
                    forecasts.append(self.xml_get_attrs(forecast, ('day', 'date', 'low', 'high', 'text', 'code')))

                weather_data['forecasts'] = forecasts
                dom.unlink()
                maintext = 'Data provider: '
                self['lab1b'].setText(_('Yahoo Weather'))
                city = '%s' % str(weather_data['location']['city'])
                self['lab2'].setText(city)
                txt = str(weather_data['condition']['date'])
                parts = txt.strip().split(' ')
                txt = _('Last Updated:') + ' %s %s %s %s %s' % (parts[1],
                 parts[2],
                 parts[3],
                 parts[4],
                 parts[5])
                self['lab3'].setText(txt)
                txt = str(weather_data['condition']['temp'])
                self['lab4'].setText(txt)
                self['lab4b'].setText('\xc2\xb0C')
                icon = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Icon/%s.png' % str(weather_data['condition']['code'])
                myicon = self.checkIcon(icon)
                png = loadPic(myicon, 219, 160, 0, 0, 0, 0)
                self['lab5'].instance.setPixmap(png)
                txt = self.extend_name(str(weather_data['condition']['text']))
                self['lab6'].setText(txt)
                self['lab7'].setText(_('Humidity   :'))
                txt = str(weather_data['atmosphere']['humidity']) + ' %'
                self['lab7b'].setText(txt)
                self['lab8'].setText(_('Pressure   :'))
                txt = str(weather_data['atmosphere']['pressure']) + ' mb'
                self['lab8b'].setText(txt)
                self['lab9'].setText(_('Visibility :'))
                txt = str(weather_data['atmosphere']['visibility']) + ' km'
                self['lab9b'].setText(txt)
                self['lab10'].setText(_('Sunrise    :'))
                txt = str(weather_data['astronomy']['sunrise'])
                self['lab10b'].setText(txt)
                self['lab11'].setText(_('Sunset     :'))
                txt = str(weather_data['astronomy']['sunset'])
                self['lab11b'].setText(txt)
                self['lab12'].setText(_('Wind       :'))
                direction = self.wind_direction(str(weather_data['wind']['direction']))
                txt = _('Wind') + ' ' + _('From') + ' %s : %s kmh' % (direction, str(weather_data['wind']['speed']))
                self['lab12b'].setText(txt)
                txt = self.extend_day(str(weather_data['forecasts'][0]['day']))
                self['lab13'].setText(txt)
                self['lab14'].setText(_('Max :'))
                txt = str(weather_data['forecasts'][0]['high']) + '\xc2\xb0C'
                self['lab14b'].setText(txt)
                self['lab15'].setText(_('Min :'))
                txt = str(weather_data['forecasts'][0]['low']) + '\xc2\xb0C'
                self['lab15b'].setText(txt)
                txt = self.extend_name(str(weather_data['forecasts'][0]['text']))
                self['lab16'].setText(txt)
                txt = str(weather_data['forecasts'][0]['date'])
                self['daydate0'].setText(txt)
                if getDesktop(0).size().width() == 1920:                
                    icon = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Icon/WeatherIcons/%s.png' % str(weather_data['forecasts'][0]['code'])
                    myicon = self.checkIcon(icon)
                    png = loadPic(myicon, 100, 100, 0, 0, 0, 0)
		else:
                    icon = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Icon/%s.png' % str(weather_data['forecasts'][0]['code'])
                    myicon = self.checkIcon(icon)		
 	            png = loadPic(myicon, 81, 59, 0, 0, 0, 0)				
                self['lab17'].instance.setPixmap(png)
                txt = self.extend_day(str(weather_data['forecasts'][1]['day']))
                self['lab18'].setText(txt)
                self['lab19'].setText(_('Max :'))
                txt = str(weather_data['forecasts'][1]['high']) + '\xc2\xb0C'
                self['lab19b'].setText(txt)
                self['lab20'].setText(_('Min :'))
                txt = str(weather_data['forecasts'][1]['low']) + '\xc2\xb0C'
                self['lab20b'].setText(txt)
                txt = self.extend_name(str(weather_data['forecasts'][1]['text']))
                self['lab21'].setText(txt)
                txt = str(weather_data['forecasts'][1]['date'])
                self['daydate1'].setText(txt)
                if getDesktop(0).size().width() == 1920:                
                    icon = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Icon/WeatherIcons/%s.png' % str(weather_data['forecasts'][1]['code'])
                    myicon = self.checkIcon(icon)
                    png = loadPic(myicon, 100, 100, 0, 0, 0, 0)
		else:
                    icon = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Icon/%s.png' % str(weather_data['forecasts'][1]['code'])
                    myicon = self.checkIcon(icon)		
 	            png = loadPic(myicon, 81, 59, 0, 0, 0, 0)					
                self['lab22'].instance.setPixmap(png)
                txt = self.extend_day(str(weather_data['forecasts'][2]['day']))
                self['3lab18'].setText(txt)
                self['3lab19'].setText(_('Max :'))
                txt = str(weather_data['forecasts'][2]['high']) + '\xc2\xb0C'
                self['3lab19b'].setText(txt)
                self['3lab20'].setText(_('Min :'))
                txt = str(weather_data['forecasts'][2]['low']) + '\xc2\xb0C'
                self['3lab20b'].setText(txt)
                txt = self.extend_name(str(weather_data['forecasts'][2]['text']))
                self['3lab21'].setText(txt)
                txt = str(weather_data['forecasts'][2]['date'])
                self['daydate2'].setText(txt)
                if getDesktop(0).size().width() == 1920:                
                    icon = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Icon/WeatherIcons/%s.png' % str(weather_data['forecasts'][2]['code'])
                    myicon = self.checkIcon(icon)
                    png = loadPic(myicon, 100, 100, 0, 0, 0, 0)
		else:
                    icon = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Icon/%s.png' % str(weather_data['forecasts'][2]['code'])
                    myicon = self.checkIcon(icon)		
 	            png = loadPic(myicon, 81, 59, 0, 0, 0, 0)	
                self['3lab22'].instance.setPixmap(png)
                txt = self.extend_day(str(weather_data['forecasts'][3]['day']))
                self['4lab18'].setText(txt)
                self['4lab19'].setText(_('Max :'))
                txt = str(weather_data['forecasts'][3]['high']) + '\xc2\xb0C'
                self['4lab19b'].setText(txt)
                self['4lab20'].setText(_('Min :'))
                txt = str(weather_data['forecasts'][3]['low']) + '\xc2\xb0C'
                self['4lab20b'].setText(txt)
                txt = self.extend_name(str(weather_data['forecasts'][3]['text']))
                self['4lab21'].setText(txt)
                txt = str(weather_data['forecasts'][3]['date'])
                self['daydate3'].setText(txt)
                if getDesktop(0).size().width() == 1920:                
                    icon = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Icon/WeatherIcons/%s.png' % str(weather_data['forecasts'][3]['code'])
                    myicon = self.checkIcon(icon)
                    png = loadPic(myicon, 100, 100, 0, 0, 0, 0)
		else:
                    icon = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Icon/%s.png' % str(weather_data['forecasts'][3]['code'])
                    myicon = self.checkIcon(icon)		
 	            png = loadPic(myicon, 81, 59, 0, 0, 0, 0)	
                self['4lab22'].instance.setPixmap(png)
                txt = self.extend_day(str(weather_data['forecasts'][4]['day']))
                self['5lab18'].setText(txt)
                self['5lab19'].setText(_('Max :'))
                txt = str(weather_data['forecasts'][4]['high']) + '\xc2\xb0C'
                self['5lab19b'].setText(txt)
                self['5lab20'].setText(_('Min :'))
                txt = str(weather_data['forecasts'][4]['low']) + '\xc2\xb0C'
                self['5lab20b'].setText(txt)
                txt = self.extend_name(str(weather_data['forecasts'][4]['text']))
                self['5lab21'].setText(txt)
                txt = str(weather_data['forecasts'][4]['date'])
                self['daydate4'].setText(txt)
                if getDesktop(0).size().width() == 1920:                
                    icon = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Icon/WeatherIcons/%s.png' % str(weather_data['forecasts'][4]['code'])
                    myicon = self.checkIcon(icon)
                    png = loadPic(myicon, 100, 100, 0, 0, 0, 0)
		else:
                    icon = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Icon/%s.png' % str(weather_data['forecasts'][4]['code'])
                    myicon = self.checkIcon(icon)		
 	            png = loadPic(myicon, 81, 59, 0, 0, 0, 0)	
                self['5lab22'].instance.setPixmap(png)
                self['lab23'].setText(city)
                self['lab24'].setText(_('Latitude :'))
                txt = str(weather_data['geo']['lat']) + '\xc2\xb0'
                self['lab24b'].setText(txt)
                self['lab25'].setText(_('Longitude :'))
                txt = str(weather_data['geo']['long']) + '\xc2\xb0'
                self['lab25b'].setText(txt)
                self['lab26'].setText(_('Region    :'))
                txt = str(weather_data['location']['region'])
                self['lab26b'].setText(txt)
                txt = str(weather_data['location']['country'])
                self['lab27'].setText(_('Country   :') + ' ' + txt)
                myicon = '/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Skin/1color.png'
                png = loadPic(myicon, 250, 30, 0, 0, 0, 0)
                self['lab28'].instance.setPixmap(png)
                self['lab28a'].setText(':')
            else:
                maintext = 'Error getting XML document!'

        self['lab1'].setText(maintext)

    def xml_get_ns_yahoo_tag(self, dom, ns, tag, attrs):
        element = dom.getElementsByTagNameNS(ns, tag)[0]
        return self.xml_get_attrs(element, attrs)

    def xml_get_attrs(self, xml_element, attrs):
        result = {}
        for attr in attrs:
            result[attr] = xml_element.getAttribute(attr)

        return result

    def wind_direction(self, degrees):
        try:
            degrees = int(degrees)
        except ValueError:
            return ''

        if degrees < 23 or degrees >= 338:
            return _('North')
        if degrees < 68:
            return _('NEast')
        if degrees < 113:
            return _('East')
        if degrees < 158:
            return _('SEast')
        if degrees < 203:
            return _('South')
        if degrees < 248:
            return _('SWest')
        if degrees < 293:
            return _('West')
        if degrees < 338:
            return _('NWest')

    def extend_day(self, day):
        if day == 'Mon':
            return _('Monday')
        elif day == 'Tue':
            return _('Tuesday')
        elif day == 'Wed':
            return _('Wednesday')
        elif day == 'Thu':
            return _('Thursday')
        elif day == 'Fri':
            return _('Friday')
        elif day == 'Sat':
            return _('Saturday')
        elif day == 'Sun':
            return _('Sunday')
        else:
            return day

    def extend_name(self, name):
        if name == 'Sunny':
            return _('Sunny')
        elif name == 'Partly Cloudy':
            return _('Partly Cloudy')
        elif name == 'PM Showers':
            return _('PM Showers')
        elif name == 'AM Clouds/PM Sun':
            return _('AM Clouds/PM Sun')
        elif name == 'Showers':
            return _('Showers')
        elif name == 'Cloudy/Wind':
            return _('Cloudy/Wind')
        elif name == 'Mostly Cloudy':
            return _('Mostly Cloudy')
        elif name == 'Cloudy':
            return _('Cloudy')
        elif name == 'Showers/Wind Early':
            return _('Showers/Wind Early')
        elif name == 'Showers Early':
            return _('Showers Early')
        elif name == 'AM Showers/Wind':
            return _('AM Showers/Wind')
        elif name == 'PM Showers/Wind':
            return _('PM Showers/Wind')
        elif name == 'AM Showers':
            return _('AM Showers')
        elif name == 'Light Rain':
            return _('Light Rain')
        elif name == 'Light Rain Late':
            return _('Light Rain Late')
        elif name == 'PM Light Rain':
            return _('PM Light Rain')
        elif name == 'AM Light Rain':
            return _('AM Light Rain')
        elif name == 'Heavy Rain':
            return _('Heavy Rain')
        elif name == 'Fair':
            return _('Fair')
        elif name == 'Light Rain/Wind':
            return _('Light Rain/Wind')
        elif name == 'Rain':
            return _('Rain')
        elif name == 'Mostly Sunny':
            return _('Mostly Sunny')
        elif name == 'Thunderstorms':
            return _('Thunderstorms')
        elif name == 'AM Thunderstorms':
            return _('AM Thunderstorms')
        elif name == 'PM Thunderstorms':
            return _('PM Thunderstorms')
        elif name == 'Scattered Thunderstorms':
            return _('Scattered Thunderstorms')
        elif name == 'Rain/Snow':
            return _('Rain/Snow')
        elif name == 'Snow':
            return _('Snow')
        elif name == 'Fog':
            return _('Fog')
        elif name == 'Foggy':
            return _('Foggy')
        elif name == 'Mostly Clear':
            return _('Mostly Clear')
        elif name == 'Haze':
            return _('Haze')
        elif name == 'Light Snow':
            return _('Light Snow')
        elif name == 'PM Light Snow':
            return _('PM Light Snow')
        elif name == 'AM Light Snow':
            return _('AM Light Snow')
        elif name == 'Snow Showers':
            return _('Snow Showers')
        elif name == 'AM Snow Showers':
            return _('AM Snow Showers')
        elif name == 'PM Snow Showers':
            return _('PM Snow Showers')
        elif name == 'Unknown':
            return _('Unknown')
        elif name == 'Light Drizzle':
            return _('Light Drizzle')
        elif name == 'Drizzle':
            return _('Drizzle')
        elif name == 'AM Thunderstorms/wind':
            return _('AM Thunderstorms/wind')
        elif name == 'PM Thunderstorms/wind':
            return _('PM Thunderstorms/wind')
        elif name == 'Clear':
            return _('Clear')
        elif name == 'Fair/Windy':
            return _('Fair/Windy')
        elif name == 'Sunny/Wind':
            return _('Sunny/Wind')
        elif name == 'PM Light Snow/Wind':
            return _('PM Light Snow/Wind')
        elif name == 'AM Light Snow/Wind':
            return _('AM Light Snow/Wind')
        elif name == 'Snow Showers/Wind':
            return _('Snow Showers/Wind')
        elif name == 'PM Snow Showers/Wind':
            return _('PM Snow Showers/Wind')
        elif name == 'AM Snow Showers/Wind':
            return _('AM Snow Showers/Wind')
        elif name == 'Rain/Snow Early':
            return _('Rain/Snow Early')
        elif name == 'PM Rain/Snow':
            return _('PM Rain/Snow')
        elif name == 'AM Rain/Snow':
            return _('AM Rain/Snow')
        elif name == 'PM Rain/Snow Showers':
            return _('PM Rain/Snow Showers')
        elif name == 'AM Rain/Snow Showers':
            return _('AM Rain/Snow Showers')
        elif name == 'AM Rain':
            return _('AM Rain')
        elif name == 'Few Showers':
            return _('Few Showers')
        elif name == 'Drizzle/Windy':
            return _('Drizzle/Windy')
        elif name == 'Ice to Rain/Wind':
            return _('Ice to Rain/Wind')
        elif name == 'Partly Cloudy/Wind':
            return _('Partly Cloudy/Wind')
        elif name == 'PM Light Rain':
            return _('PM Light Rain')
        elif name == 'AM Light Rain':
            return _('AM Light Rain')
        elif name == 'Heavy Snow':
            return _('Heavy Snow')
        else:
            return name

    def checkIcon(self, localfile):
        if fileExists(localfile):
            pass
        else:
            url = localfile.replace('/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Icon', 'http://www.mysite.net/weapic/weabig')
            handler = urlopen(url)
            if handler:
                content = handler.read()
                fileout = open(localfile, 'wb')
                fileout.write(content)
                handler.close()
                fileout.close()
        return localfile

    def get_Url(self):
        url = 'http://weather.yahooapis.com/forecastrss?w='
        url2 = '721943'
        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Config/Location_id'):
            url2 = open('/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter/Config/Location_id').read()
        url = url + url2 + '&u=c'
        return url

    def delTimer(self):
        del self.activityTimer

    def key_red(self):
        self.session.open(WeatherSearch)

    def key_green(self):
        if config.plugins.YahooWeather.compactskin.value == True:
            config.plugins.YahooWeather.compactskin.setValue(False)
            self.session.open(MessageBox, _('Yahoo Weather') + _('\nSkin Compact: off'), MessageBox.TYPE_INFO, timeout=5)
        elif config.plugins.YahooWeather.compactskin.value == False:
            config.plugins.YahooWeather.compactskin.setValue(True)
            self.session.open(MessageBox, _('Yahoo Weather') + _('\nSkin Compact: on'), MessageBox.TYPE_INFO, timeout=5)
        config.plugins.YahooWeather.compactskin.save()
