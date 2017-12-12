installdir = $(libdir)/enigma2/python/Plugins/Extensions/NFR4XBoot/ubi_reader/ubifs
SUBDIRS = nodes
install_PYTHON = *.py \
                 *.pyo
if HAVE_MB4K
install_DATA = *.txt
else
install_DATA = *.so
endif
