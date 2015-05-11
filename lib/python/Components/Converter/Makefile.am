installdir = $(pkglibdir)/python/Components/Converter

ifeq ($BOXTYPE, "spark")
  mv $(installdir)/bitratecalc.so_sh4 $(installdir)/bitratecalc.so
  rm -r $(installdir)/bitratecalc.so_mips
else
  ifeq ($BOXTYPE, "spark7162")
    mv $(installdir)/bitratecalc.so_sh4 $(installdir)/bitratecalc.so
    rm -r $(installdir)/bitratecalc.so_mips
  else  
    mv $(installdir)/bitratecalc.so_mips $(installdir)/bitratecalc.so
    rm -r $(installdir)/bitratecalc.so_sh4
  endif  
endif

dist_install_DATA = *.so
install_PYTHON = *.py
