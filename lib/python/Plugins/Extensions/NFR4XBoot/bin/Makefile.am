installdir = $(libdir)/enigma2/python/Plugins/Extensions/NFR4XBoot/bin
dist_install_DATA = \
	nfr4xinitnoboot 
	
if HAVE_MB4K	
	dist_install_DATA += \	
	nfr4xinitboot
else
	dist_install_DATA += \	
	nfr4xbm  \
	nfr4xinitboot \
	fbclear  \
	sfdisk
install-data-hook:
	@chmod +x $(DESTDIR)$(installdir)/sfdisk
endif 	

	

