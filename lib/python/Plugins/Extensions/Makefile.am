installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = TuxboxPlugins CutListEditor PicturePlayer MediaScanner MediaPlayer SocketMMI DVDBurn Modem Infopanel AccuWeather MenuSort CustomSubservices bmediacenter MainMenu2

if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

if SPARK
mv installdir/NFR4XBoot_sh4 installdir/NFR4XBoot
rm -r installdir/NFR4XBoot_mips
SUBDIRS += NFR4XBoot
else
mv installdir/NFR4XBoot_mips installdir/NFR4XBoot
rm -r installdir/NFR4XBoot_sh4
SUBDIRS += NFR4XBoot
endif

install_PYTHON = __init__.py
