installdir = $(pkglibdir)/python/Plugins/Extensions/Infopanel/data


dist_install_DATA = \
	iperf.7z \
	screenshot.sh  \
	PluginHDDi.sh \
	PluginHDDu.sh  \
	PluginUSBi.sh  \
	PluginUSBu.sh
	
install-data-hook:
	@chmod +x $(DESTDIR)$(installdir)/screenshot.sh
	@chmod +x $(DESTDIR)$(installdir)/PluginHDDi.sh
	@chmod +x $(DESTDIR)$(installdir)/PluginHDDu.sh
	@chmod +x $(DESTDIR)$(installdir)/PluginUSBi.sh
	@chmod +x $(DESTDIR)$(installdir)/PluginUSBu.sh
