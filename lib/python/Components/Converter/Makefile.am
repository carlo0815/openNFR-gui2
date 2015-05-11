installdir = $(pkglibdir)/python/Components/Converter

ifeq ($BOXTYPE, "spark")
  mv $(installdir)/bitratecalc.so_sh4 $(installdir)/bitratecalc.so
  rm -r $(installdir)/bitratecalc.so_mips
  touch $(installdir)/sh4_1.txt
else ifeq ($BOXTYPE, "spark7162")
  mv $(installdir)/bitratecalc.so_sh4 $(installdir)/bitratecalc.so
  rm -r $(installdir)/bitratecalc.so_mips
  touch $(installdir)/sh4_2.txt
else  
  mv $(installdir)/bitratecalc.so_mips $(installdir)/bitratecalc.so
  rm -r $(installdir)/bitratecalc.so_sh4
  touch $(installdir)/mips_1.txt
endif

dist_install_DATA = *.so
install_PYTHON = *.py
