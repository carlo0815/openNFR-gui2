from os import fchmod, fsync, path, rename, unlink
from tempfile import NamedTemporaryFile

try:
	from subprocess import Popen, PIPE
	haveSubprocess = True
except ImportError:
	from os import popen
	haveSubprocess = False

def runPipe(cmd):
	if haveSubprocess:
		p = Popen(cmd, stdout=PIPE, close_fds=True)
		output = p.stdout.read()
		p.stdout.close()
		return p.wait(), output.splitlines()
	else:
		p = popen(' '.join(cmd), 're')
		output = p.read()
		rc = p.close()
		return (rc >> 8 if rc is not None else 0), output.splitlines()

def saveFile(filename, data, mode=0644):
	tmpFilename = None
	try:
		f = NamedTemporaryFile(prefix='.%s.' % path.basename(filename), dir=path.dirname(filename), delete=False)
		tmpFilename = f.name
		if isinstance(data, list):
			for x in data:
				f.write(x)
		else:
			f.write(data)
		f.flush()
		fsync(f.fileno())
		fchmod(f.fileno(), mode)
		f.close()
		rename(tmpFilename, filename)
	except Exception as e:
		print 'saveFile: failed to write to %s: %s' % (filename, e)
		if tmpFilename and path.exists(tmpFilename):
			unlink(tmpFilename)
		return False

	return True
