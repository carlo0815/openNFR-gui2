from Tools.Profile import profile
from Tools.BoundFunction import boundFunction
from enigma import eServiceReference
# workaround for required config entry dependencies.
import Screens.MovieSelection

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Label import Label
from Components.Pixmap import MultiPixmap

profile("LOAD:enigma")
import enigma
from boxbranding import getBoxType, getMachineBrand,getBrandOEM

boxtype = getBoxType()

profile("LOAD:InfoBarGenerics")
from Screens.InfoBarGenerics import InfoBarShowHide, \
	InfoBarNumberZap, InfoBarChannelSelection, InfoBarMenu, InfoBarRdsDecoder, \
	InfoBarEPG, InfoBarSeek, InfoBarInstantRecord, InfoBarRedButton, InfoBarTimerButton, InfoBarVmodeButton, \
	InfoBarAudioSelection, InfoBarAdditionalInfo, InfoBarNotifications, InfoBarDish, InfoBarUnhandledKey, \
	InfoBarSubserviceSelection, InfoBarShowMovies, InfoBarLongKeyDetection, \
	InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, \
	InfoBarSummarySupport, InfoBarMoviePlayerSummarySupport, InfoBarTimeshiftState, InfoBarTeletextPlugin, InfoBarExtensions, \
	InfoBarSubtitleSupport, InfoBarSleepTimer, InfoBarPowersaver, InfoBarPiP, InfoBarPlugins, InfoBarServiceErrorPopupSupport, InfoBarJobman, InfoBarZoom, InfoBarHdmi, \
	setResumePoint, delResumePoint
from Screens.Hotkey import InfoBarHotkey

profile("LOAD:InitBar_Components")
from Components.ActionMap import HelpableActionMap
from Components.Timeshift import InfoBarTimeshift
from Components.config import config
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase

profile("LOAD:HelpableScreen")
from Screens.HelpMenu import HelpableScreen

profile("LOAD: OpenNFRBluePanel")
from Plugins.Extensions.Infopanel.panel_key import OpenNFRBluePanel

profile("LOAD: OpenNFRRedPanel")
from Plugins.Extensions.Infopanel.panel_key import OpenNFRREDPanel
	

class InfoBar(InfoBarBase, InfoBarShowHide,
	InfoBarNumberZap, InfoBarChannelSelection, InfoBarMenu, InfoBarEPG, InfoBarRdsDecoder, OpenNFRBluePanel, OpenNFRREDPanel, 
	InfoBarInstantRecord, InfoBarAudioSelection, InfoBarRedButton, InfoBarTimerButton, InfoBarVmodeButton,
	HelpableScreen, InfoBarAdditionalInfo, InfoBarNotifications, InfoBarDish, InfoBarUnhandledKey,
	InfoBarSubserviceSelection, InfoBarTimeshift, InfoBarSeek, InfoBarCueSheetSupport, InfoBarLongKeyDetection,
	InfoBarSummarySupport, InfoBarTimeshiftState, InfoBarTeletextPlugin, InfoBarExtensions,
	InfoBarPiP, InfoBarPlugins, InfoBarSleepTimer, InfoBarPowersaver, InfoBarSubtitleSupport, InfoBarServiceErrorPopupSupport, InfoBarJobman, InfoBarZoom, InfoBarHdmi,
	Screen, InfoBarHotkey):

	ALLOW_SUSPEND = True
	instance = None

	def __init__(self, session):
		Screen.__init__(self, session)
		self["actions"] = HelpableActionMap(self, "InfobarActions",
			{
				"showMovies": (self.showMovies, _("Play recorded movies...")),
				"showRadio": (self.showRadio, _("Show the radio player...")),
				"showTv": (self.TvRadioToggle, _("Show the tv player...")),
				"openBouquetList": (self.openBouquetList, _("open bouquetlist")),
				"openTimerList": (self.openTimerList, _("Open Timer List...")),
				"openSleepTimer": (self.openSleepTimer, _("Show/Add Sleep Timers")),
				"showMediaPlayer": (self.showMediaPlayer, _("Show the media player...")),
				"showPluginBrowser": (self.showPluginBrowser, _("Show the plugins...")),
				"showSetup": (self.showSetup, _("Show setup...")),
				"showWWW": (self.showWWW, _("Open WebBrowser...")),
				"showLanSetup": (self.showLanSetup, _("Show LAN Setup...")),
				"showFormat": (self.showFormat, _("Show Format Setup...")),
				"volumeUp": (self._volUp, _("...")), 
				"volumeDown": (self._volDown, _("...")), 

			}, prio=2)

		self.radioTV = 0
		self.allowPiP = True

		for x in HelpableScreen, \
				InfoBarBase, InfoBarShowHide, \
				InfoBarNumberZap, InfoBarChannelSelection, InfoBarMenu, InfoBarEPG, InfoBarRdsDecoder, OpenNFRBluePanel, OpenNFRREDPanel, \
				InfoBarInstantRecord, InfoBarAudioSelection, InfoBarRedButton, InfoBarTimerButton, InfoBarUnhandledKey, InfoBarVmodeButton,\
				InfoBarAdditionalInfo, InfoBarNotifications, InfoBarDish, InfoBarSubserviceSelection, InfoBarLongKeyDetection, \
				InfoBarTimeshift, InfoBarSeek, InfoBarCueSheetSupport, InfoBarSummarySupport, InfoBarTimeshiftState, \
				InfoBarTeletextPlugin, InfoBarExtensions, InfoBarPiP, InfoBarSubtitleSupport, InfoBarJobman, InfoBarZoom, InfoBarHdmi, \
				InfoBarPlugins, InfoBarSleepTimer, InfoBarPowersaver, InfoBarServiceErrorPopupSupport, InfoBarHotkey:
			x.__init__(self)

		self.helpList.append((self["actions"], "InfobarActions", [("showMovies", _("Watch recordings..."))]))
		self.helpList.append((self["actions"], "InfobarActions", [("showRadio", _("Listen to the radio..."))]))

		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
			{
				enigma.iPlayableService.evUpdatedEventInfo: self.__eventInfoChanged
			})

		self.current_begin_time=0
		assert InfoBar.instance is None, "class InfoBar is a singleton class and just one instance of this class is allowed!"
		InfoBar.instance = self

		if config.misc.initialchannelselection.getValue():
			self.onShown.append(self.showMenu)

	def showMenu(self):
		self.onShown.remove(self.showMenu)
		config.misc.initialchannelselection.value = False
		config.misc.initialchannelselection.save()
		self.mainMenu()

	def _volUp(self):
		print "_volUp"
		from Components.VolumeControl import VolumeControl
		VolumeControl.instance.volUp()

	def _volDown(self):
		print "_volDown"
		from Components.VolumeControl import VolumeControl
		VolumeControl.instance.volDown()

	def __onClose(self):
		InfoBar.instance = None

	def standbyCountChanged(self, value):
		if config.ParentalControl.servicepinactive.value:
			from Components.ParentalControl import parentalControl
			if parentalControl.isProtected(self.cur_service):
				self.close()

	def __eventInfoChanged(self):
		if self.execing:
			service = self.session.nav.getCurrentService()
			old_begin_time = self.current_begin_time
			info = service and service.info()
			ptr = info and info.getEvent(0)
			self.current_begin_time = ptr and ptr.getBeginTime() or 0
			if config.usage.show_infobar_on_event_change.getValue():
				if old_begin_time and old_begin_time != self.current_begin_time:
					self.doShow()

	def serviceStarted(self):  #override from InfoBarShowHide
		new = self.servicelist.newServicePlayed()
		if self.execing:
			InfoBarShowHide.serviceStarted(self)
			self.current_begin_time=0
		elif not self.__checkServiceStarted in self.onShown and new:
			self.onShown.append(self.__checkServiceStarted)

	def __checkServiceStarted(self):
		self.serviceStarted()
		self.onShown.remove(self.__checkServiceStarted)

	def openBouquetList(self):
		if config.usage.tvradiobutton_mode.getValue() == "MovieList":
			self.showTvChannelList(True)
			self.showMovies()
		elif config.usage.tvradiobutton_mode.getValue() == "ChannelList":
			self.showTvChannelList(True)
		elif config.usage.tvradiobutton_mode.getValue() == "BouquetList":
			self.showTvChannelList(True)
			self.servicelist.showFavourites()

	def TvRadioToggle(self):
		if getBrandOEM() == 'gigablue':
			self.toogleTvRadio()
		else:
			self.showTv()

	def toogleTvRadio(self): 
		if self.radioTV == 1:
			self.radioTV = 0
			self.showTv() 
		else: 
			self.radioTV = 1
			self.showRadio() 

	def showTv(self):
		if config.usage.tvradiobutton_mode.getValue() == "MovieList":
			self.showTvChannelList(True)
			self.showMovies()
		elif config.usage.tvradiobutton_mode.getValue() == "BouquetList":
			self.showTvChannelList(True)
			self.servicelist.showFavourites()
		else:
			self.showTvChannelList(True)

	def showRadio(self):
		if config.usage.e1like_radio_mode.getValue():
			if config.usage.tvradiobutton_mode.getValue() == "BouquetList":
				self.showRadioChannelList(True)
				self.servicelist.showFavourites()
			else:
				self.showRadioChannelList(True)
		else:
			self.rds_display.hide() # in InfoBarRdsDecoder
			from Screens.ChannelSelection import ChannelSelectionRadio
			self.session.openWithCallback(self.ChannelSelectionRadioClosed, ChannelSelectionRadio, self)

	def ChannelSelectionRadioClosed(self, *arg):
		self.rds_display.show()  # in InfoBarRdsDecoder

	def showMovies(self, defaultRef=None):
		self.lastservice = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		if self.lastservice and ':0:/' in self.lastservice.toString():
			self.lastservice = enigma.eServiceReference(config.movielist.curentlyplayingservice.getValue())
		self.session.openWithCallback(self.movieSelected, Screens.MovieSelection.MovieSelection, defaultRef, timeshiftEnabled = self.timeshiftEnabled())

	def movieSelected(self, service):
		ref = self.lastservice
		del self.lastservice
		if service is None:
			if ref and not self.session.nav.getCurrentlyPlayingServiceOrGroup():
				self.session.nav.playService(ref)
		else:
			from Components.ParentalControl import parentalControl
			if parentalControl.isServicePlayable(service, self.openMoviePlayer):
				self.openMoviePlayer(service)

	def openMoviePlayer(self, ref):
		self.session.open(MoviePlayer, ref, slist=self.servicelist, lastservice=self.session.nav.getCurrentlyPlayingServiceOrGroup())

	def openTimerList(self):
		from Screens.TimerEdit import TimerEditList
		self.session.open(TimerEditList)

	def openSleepTimer(self):
		from Screens.SleepTimerEdit import SleepTimerEdit
		self.session.open(SleepTimerEdit)
		
	def showMediaPlayer(self):
		try:
			from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer
			self.session.open(MediaPlayer)
			no_plugin = False
		except Exception, e:
			self.session.open(MessageBox, _("The MediaPlayer plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )
			
	def showPluginBrowser(self):
		from Screens.PluginBrowser import PluginBrowser
		self.session.open(PluginBrowser)
		
	def showSetup(self):
		from Screens.Menu import MainMenu, mdom
		root = mdom.getroot()
		for x in root.findall("menu"):
			y = x.find("id")
			if y is not None:
				id = y.get("val")
				if id and id == "setup":
					self.session.infobar = self
					self.session.open(MainMenu, x)
					return

	def showLanSetup(self):
		from Screens.NetworkSetup import NetworkAdapterSelection
		self.session.open(NetworkAdapterSelection)
			
	def showWWW(self):
		try:
			from Plugins.Extensions.HbbTV.plugin import OperaBrowser
			self.session.open(OperaBrowser)
			no_plugin = False
		except Exception, e:
			self.session.open(MessageBox, _("The WebBrowser plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )

	def showFormat(self):
		try:
			from Screens.VideoMode import VideoSetup
			self.session.open(VideoSetup)
			no_plugin = False
		except Exception, e:
			self.session.open(MessageBox, _("The VideoMode plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )
			
			
class MoviePlayer(InfoBarBase, InfoBarShowHide,
		InfoBarMenu, InfoBarEPG,
		InfoBarSeek, InfoBarShowMovies, InfoBarInstantRecord, InfoBarAudioSelection, HelpableScreen, InfoBarNotifications,
		InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarLongKeyDetection,
		InfoBarMoviePlayerSummarySupport, InfoBarSubtitleSupport, Screen, InfoBarTeletextPlugin, InfoBarHdmi,
		InfoBarServiceErrorPopupSupport, InfoBarExtensions, InfoBarPlugins, InfoBarPiP, InfoBarZoom, InfoBarHotkey):

	ENABLE_RESUME_SUPPORT = True
	ALLOW_SUSPEND = True

	instance = None

	def __init__(self, session, service, slist = None, lastservice = None):
		Screen.__init__(self, session)

		self["key_yellow"] = Label()
		self["key_blue"] = Label()
		self["key_green"] = Label()

		self["eventname"] = Label()
		self["state"] = Label()
		self["speed"] = Label()
		self["statusicon"] = MultiPixmap()

		self["actions"] = HelpableActionMap(self, "MoviePlayerActions",
			{
				"leavePlayer": (self.leavePlayer, _("leave movie player...")),
				"leavePlayerOnExit": (self.leavePlayerOnExit, _("leave movie player..."))
			})

		self.allowPiP = True

		for x in HelpableScreen, InfoBarShowHide, InfoBarMenu, InfoBarEPG, \
				InfoBarBase, InfoBarSeek, InfoBarShowMovies, InfoBarInstantRecord, \
				InfoBarAudioSelection, InfoBarNotifications, InfoBarLongKeyDetection, \
				InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, \
				InfoBarMoviePlayerSummarySupport, InfoBarSubtitleSupport, \
				InfoBarTeletextPlugin, InfoBarServiceErrorPopupSupport, InfoBarExtensions, \
				InfoBarPlugins, InfoBarPiP, InfoBarZoom, InfoBarHotkey:
			x.__init__(self)

		self.onChangedEntry = [ ]
		self.servicelist = slist
		self.lastservice = lastservice or session.nav.getCurrentlyPlayingServiceOrGroup()
		session.nav.playService(service)
		self.cur_service = service
		self.returning = False
		self.onClose.append(self.__onClose)
		self.onShow.append(self.doButtonsCheck)

		assert MoviePlayer.instance is None, "class InfoBar is a singleton class and just one instance of this class is allowed!"
		MoviePlayer.instance = self

	def doButtonsCheck(self):
		if config.vixsettings.ColouredButtons.getValue():
			self["key_yellow"].setText(_("Search"))
			self["key_green"].setText(_("Timers"))
		self["key_blue"].setText(_("Extensions"))

	def __onClose(self):
		MoviePlayer.instance = None
		from Screens.MovieSelection import playlist
		del playlist[:]
		self.session.nav.playService(self.lastservice)

	def standbyCountChanged(self, value):
		if config.ParentalControl.servicepinactive.value:
			from Components.ParentalControl import parentalControl
			if parentalControl.isProtected(self.cur_service):
				self.close()		
		
	def handleLeave(self, how):
		self.is_closing = True
		if how == "ask":
			if config.usage.setup_level.index < 2: # -expert
				list = (
					(_("Yes"), "quit"),
					(_("No"), "continue")
				)
			else:
				list = (
					(_("Yes"), "quit"),
					(_("Yes, returning to movie list"), "movielist"),
					(_("Yes, and delete this movie"), "quitanddelete"),
					(_("No"), "continue"),
					(_("No, but restart from begin"), "restart")
				)

			from Screens.ChoiceBox import ChoiceBox
			self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("Stop playing this movie?"), list = list)
		else:
			self.leavePlayerConfirmed([True, how])

	def leavePlayer(self):
		setResumePoint(self.session)
		self.handleLeave(config.usage.on_movie_stop.getValue())

	def leavePlayerOnExit(self):
		if self.shown:
			self.hide()
		elif self.session.pipshown and "popup" in config.usage.pip_hideOnExit.getValue():
			if config.usage.pip_hideOnExit.getValue() == "popup":
				self.session.openWithCallback(self.hidePipOnExitCallback, MessageBox, _("Disable Picture in Picture"), simple=True)
			else:
				self.hidePipOnExitCallback(True)
		elif config.usage.leave_movieplayer_onExit.getValue() == "popup":
			self.session.openWithCallback(self.leavePlayerOnExitCallback, MessageBox, _("Exit movie player?"), simple=True)
		elif config.usage.leave_movieplayer_onExit.getValue() == "without popup":	
			self.leavePlayerOnExitCallback(True)

	def leavePlayerOnExitCallback(self, answer):
		if answer:
			setResumePoint(self.session)
			self.handleLeave("quit")

	def hidePipOnExitCallback(self, answer):
		if answer:
			self.showPiP()

	def deleteConfirmed(self, answer):
		if answer:
			self.leavePlayerConfirmed((True, "quitanddeleteconfirmed"))

	def leavePlayerConfirmed(self, answer):
		answer = answer and answer[1]
		if answer is None:
			return
		if answer in ("quitanddelete", "quitanddeleteconfirmed"):
			ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
			serviceHandler = enigma.eServiceCenter.getInstance()
			if answer == "quitanddelete":
				msg = ''
				if config.usage.movielist_trashcan.getValue():
					import Tools.Trashcan
					try:
						trash = Tools.Trashcan.createTrashFolder(ref.getPath())
						Screens.MovieSelection.moveServiceFiles(ref, trash)
						# Moved to trash, okay
						self.close()
						return
					except Exception, e:
						print "[InfoBar] Failed to move to .Trash folder:", e
						msg = _("Cannot move to trash can") + "\n" + str(e) + "\n"
				info = serviceHandler.info(ref)
				name = info and info.getName(ref) or _("this recording")
				msg += _("Do you really want to delete %s?") % name
				self.session.openWithCallback(self.deleteConfirmed, MessageBox, msg)
				return

			elif answer == "quitanddeleteconfirmed":
				offline = serviceHandler.offlineOperations(ref)
				if offline.deleteFromDisk(0):
					self.session.openWithCallback(self.close, MessageBox, _("You cannot delete this!"), MessageBox.TYPE_ERROR)
					return

		if answer in ("quit", "quitanddeleteconfirmed"):
			self.close()
		elif answer == "movielist":
			ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
			self.returning = True
			self.session.openWithCallback(self.movieSelected, Screens.MovieSelection.MovieSelection, ref)
			self.session.nav.stopService()
		elif answer == "restart":
			self.doSeek(0)
			self.setSeekState(self.SEEK_STATE_PLAY)
		elif answer in ("playlist","playlistquit","loop"):
			( next_service, item , length ) = self.getPlaylistServiceInfo(self.cur_service)
			if next_service is not None:
				if config.usage.next_movie_msg.getValue():
					self.displayPlayedName(next_service, item, length)
				self.session.nav.playService(next_service)
				self.cur_service = next_service
			else:
				if answer == "playlist":
					self.leavePlayerConfirmed([True,"movielist"])
				elif answer == "loop" and length > 0:
					self.leavePlayerConfirmed([True,"loop"])
				else:
					self.leavePlayerConfirmed([True,"quit"])
		elif answer in "repeatcurrent":
			if config.usage.next_movie_msg.value:
				(item, length) = self.getPlaylistServiceInfo(self.cur_service)
				self.displayPlayedName(self.cur_service, item, length)
			self.session.nav.stopService()
			self.session.nav.playService(self.cur_service)

	def doEofInternal(self, playing):
		if not self.execing:
			return
		if not playing :
			return
		ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		if ref:
			delResumePoint(ref)
		self.handleLeave(config.usage.on_movie_eof.getValue())

	def up(self):
		slist = self.servicelist
		if slist and slist.dopipzap:
			if "keep" not in config.usage.servicelist_cursor_behavior.value:
				slist.moveUp()
			self.session.execDialog(slist)
		else:
			self.showMovies()

	def down(self):
		slist = self.servicelist
		if slist and slist.dopipzap:
			if "keep" not in config.usage.servicelist_cursor_behavior.value:
				slist.moveDown()
			self.session.execDialog(slist)
		else:
			self.showMovies()

	def right(self):
		# XXX: gross hack, we do not really seek if changing channel in pip :-)
		slist = self.servicelist
		if slist and slist.dopipzap:
			# XXX: We replicate InfoBarChannelSelection.zapDown here - we shouldn't do that
			if slist.inBouquet():
				prev = slist.getCurrentSelection()
				if prev:
					prev = prev.toString()
					while True:
						if config.usage.quickzap_bouquet_change.getValue() and slist.atEnd():
							slist.nextBouquet()
						else:
							slist.moveDown()
						cur = slist.getCurrentSelection()
						if not cur or (not (cur.flags & 64)) or cur.toString() == prev:
							break
			else:
				slist.moveDown()
			slist.zap(enable_pipzap = True)
		else:
			InfoBarSeek.seekFwd(self)

	def left(self):
		slist = self.servicelist
		if slist and slist.dopipzap:
			# XXX: We replicate InfoBarChannelSelection.zapUp here - we shouldn't do that
			if slist.inBouquet():
				prev = slist.getCurrentSelection()
				if prev:
					prev = prev.toString()
					while True:
						if config.usage.quickzap_bouquet_change.getValue():
							if slist.atBegin():
								slist.prevBouquet()
						slist.moveUp()
						cur = slist.getCurrentSelection()
						if not cur or (not (cur.flags & 64)) or cur.toString() == prev:
							break
			else:
				slist.moveUp()
			slist.zap(enable_pipzap = True)
		else:
			InfoBarSeek.seekBack(self)
			
	def showPiP(self):
		slist = self.servicelist
		if self.session.pipshown:
			if slist and slist.dopipzap:
				slist.togglePipzap()
			if self.session.pipshown:
				del self.session.pip
				self.session.pipshown = False
		else:
			from Screens.PictureInPicture import PictureInPicture
			self.session.pip = self.session.instantiateDialog(PictureInPicture)
			self.session.pip.show()
			if self.session.pip.playService(slist.getCurrentSelection()):
				self.session.pipshown = True
				self.session.pip.servicePath = slist.getCurrentServicePath()
			else:
				self.session.pipshown = False
				del self.session.pip

	def movePiP(self):
		if self.session.pipshown:
			InfoBarPiP.movePiP(self)
			
	def swapPiP(self):
		pass

	def showMovies(self):
		ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		if ref and ':0:/' not in ref.toString():
			self.playingservice = ref # movie list may change the currently playing
		else:
			self.playingservice = enigma.eServiceReference(config.movielist.curentlyplayingservice.getValue())
		self.session.openWithCallback(self.movieSelected, Screens.MovieSelection.MovieSelection, ref)

	def movieSelected(self, service):
		if service is not None:
			self.cur_service = service
			self.is_closing = False
			self.session.nav.playService(service)
			self.returning = False
		elif self.returning:
			self.close()
		else:
			self.is_closing = False
			ref = self.playingservice
			del self.playingservice
			# no selection? Continue where we left off
			if ref and not self.session.nav.getCurrentlyPlayingServiceOrGroup():
				self.session.nav.playService(ref)

	def getPlaylistServiceInfo(self, service):
		from MovieSelection import playlist
		for i, item in enumerate(playlist):
			if item == service:
				if config.usage.on_movie_eof.value == "repeatcurrent":
					return i+1, len(playlist)
				i += 1
				if i < len(playlist):
					return playlist[i], i+1, len(playlist)
				elif config.usage.on_movie_eof.getValue() == "loop":
					return playlist[0], 1, len(playlist)
		return None, 0, 0

	def displayPlayedName(self, ref, index, n):
		from Tools import Notifications
		Notifications.AddPopup(text = _("%s/%s: %s") % (index, n, self.ref2HumanName(ref)), type = MessageBox.TYPE_INFO, timeout = 5)

	def ref2HumanName(self, ref):
		return enigma.eServiceCenter.getInstance().info(ref).getName(ref)
