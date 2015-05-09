installdir = $(pkglibdir)/python/Plugins/Extensions/Infopanel

SUBDIRS = meta icons locale Extra meta pics images

if SPARK
mv installdir/data_sh4 installdir/data
rm -r installdir/data_mips
SUBDIRS += data
else
mv installdir/data_mips installdir/data
rm -r installdir/data_sh4
SUBDIRS += data
endif

install_PYTHON = *.py

dist_install_DATA = \
	testIP



