installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = TuxboxPlugins CutListEditor PicturePlayer MediaScanner MediaPlayer SocketMMI DVDBurn Modem Infopanel AccuWeather MenuSort CustomSubservices bmediacenter MainMenu2

if VUSOLO4K
SUBDIRS +=  NFR4XBoot_4k
else
SUBDIRS +=  NFR4XBoot_mips
endif


if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

if VUSOLO4K
SUBDIRS += MiniTV
endif

install_PYTHON = __init__.py
