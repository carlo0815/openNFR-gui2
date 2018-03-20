installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = CutListEditor PicturePlayer MediaScanner MediaPlayer SocketMMI DVDBurn Modem Infopanel AccuWeather MenuSort bmediacenter MainMenu2

if HAVE_NOMB4K
SUBDIRS +=  TuxboxPlugins
else 
SUBDIRS +=  NFR4XBoot TuxboxPlugins
endif

if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

if VUSOLO4K
SUBDIRS += MiniTV QuadPip
endif

if VUULTIMO4K
SUBDIRS += MiniTV QuadPip
endif

if GB7252
SUBDIRS += QuadPip
endif

if S8100
SUBDIRS += MiniTV
endif

install_PYTHON = __init__.py
