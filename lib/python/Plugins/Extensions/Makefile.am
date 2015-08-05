installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = TuxboxPlugins CutListEditor PicturePlayer MediaScanner MediaPlayer SocketMMI DVDBurn Modem Infopanel MenuSort CustomSubservices bmediacenter MainMenu2

if SPARK
SUBDIRS +=  NFR4XBoot_sh4
SUBDIRS +=  AccuWeather
elif VUSOLOSE
SUBDIRS +=  AccuWeather
else
SUBDIRS +=  NFR4XBoot_mips
SUBDIRS +=  AccuWeather
endif

if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

install_PYTHON = __init__.py
