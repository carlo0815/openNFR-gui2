installdir = $(pkglibdir)/python/Plugins/Extensions/TVHeadEnd

install_PYTHON = \
	__init__.py plugin.py TVHNimManager.py TVHSatconfig.py 
	
dist_install_DATA = \
	tvheadend.sh \ 
	tvheadend1.sh \ 
	redlogo.png \ 
	opennfr_info.png \ 
	alliance.png  	
  
install-data-hook:
	@chmod +x $(DESTDIR)$(installdir)/tvheadend.sh
	@chmod +x $(DESTDIR)$(installdir)/tvheadend1.sh
	
