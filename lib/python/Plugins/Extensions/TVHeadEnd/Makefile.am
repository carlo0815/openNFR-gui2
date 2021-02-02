installdir = $(pkglibdir)/python/Plugins/Extensions/TVHeadEnd

install_PYTHON = \
	__init__.py plugin.py TVHNimManager.py TVHSatconfig.py tvheadend.sh
  
  install-data-hook:
	@chmod +x $(DESTDIR)$(installdir)/tvheadend.sh
