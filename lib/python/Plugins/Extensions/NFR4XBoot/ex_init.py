import sys, nfr4xboot
if len(sys.argv) < 3:
    pass
else:
    nfr4xboot.NFR4XBootMainEx(sys.argv[1], sys.argv[2], sys.argv[3])