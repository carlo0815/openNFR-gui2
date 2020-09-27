from __future__ import print_function
#!/usr/bin/env python
#coding=utf-8
# modifyDate: 20190718 ~ 20190723
# ????:karlchen1963, http://nachtfalke.bit
 
"""
	??:???? python ?????????????(?????SimpleHTTPServer??),
	????????,??????python(????2.6~2.7,???3.x),
	????????????,??:
	python SimpleHTTPServerWithUpload.py 1234       
	??1234????????,???,??? 8080
	???? http://localhost:1234 ??,localhost ?? 1234 ??????
"""

"""Simple HTTP Server With Upload.

This module builds on BaseHTTPServer by implementing the standard GET
and HEAD requests in a fairly straightforward manner.

"""


__version__ = "0.1"
__all__ = ["SimpleHTTPRequestHandler"]
__author__ = "bones7456 mod by karlchen1963"
__home_page__ = ""

import os, sys, platform
import posixpath
import http.server
import urllib.request, urllib.parse, urllib.error
import html
import six
import cgi
import shutil
import mimetypes
import re
import time
from io import BytesIO

print ("")
print ('----------------------------------------------------------------------->> ')
try:
	port = int(sys.argv[1])
except Exception as e:
	print ('-------->> Warning: Port is not given, will use deafult port: 8080 ')
	print ('-------->> if you want to use other port, please execute: ')
	print ('-------->> python SimpleHTTPServerWithUpload.py port ')
	print ("-------->> port is a integer and it's range: 1024 < port < 65535 ")
	port = 8080

if not 1024 < port < 65535:  port = 8080
serveraddr = ('', port)
print ('-------->> Now, listening at port ' + str(port) + ' ...')
print ('-------->> You can visit the URL:   http://localhost:' + str(port))
print ('----------------------------------------------------------------------->> ')
print ("")

def sizeof_fmt(num):
	for x in ['bytes','KB','MB','GB']:
		if num < 1024.0:
			return "%3.1f%s" % (num, x)
		num /= 1024.0
	return "%3.1f%s" % (num, 'TB')

def modification_date(filename):
	# t = os.path.getmtime(filename)
	# return datetime.datetime.fromtimestamp(t)
	return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getmtime(filename)))

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

	"""Simple HTTP request handler with GET/HEAD/POST commands. 
	This serves files from the current directory and any of its
	subdirectories.  The MIME type for files is determined by
	calling the .guess_type() method. And can reveive file uploaded
	by client.

	The GET/HEAD/POST requests are identical except that the HEAD
	request omits the actual contents of the file.

	"""

	server_version = "SimpleHTTPWithUpload/" + __version__

	def do_GET(self):
		"""Serve a GET request."""
		f = self.send_head()
		if f:
			self.copyfile(f, self.wfile)
			f.close()

	def do_HEAD(self):
		"""Serve a HEAD request."""
		f = self.send_head()
		if f:
			f.close()

	def do_POST(self):
		"""Serve a POST request."""
		r, info = self.deal_post_data()
		print (r, info, "by: ", self.client_address)
		f = BytesIO()
		f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
		f.write(b"<html>\n<title>Upload Result Page</title>\n")
		f.write(b'<table width="100%" id="table1" height="100%"><tr><td  bgcolor="#4d4d4d" height="15%"><img src="/usr/lib/enigma2/python/Plugins/Extensions/FileLoad/images/NF_Reloaded_Banner.png" width="948" height="130"></td></tr>')
		f.write(b"<tr><td  bgcolor='#4d4d4d' height='15%'><h2>Upload Result Page</h2>")
		f.write(b'<form ENCTYPE=\"multipart/form-data\" method=\"post\">')
		f.write(("<br><br/><input type=\"button\" value=\"Back\" onClick=\"location='%s'\"></form>" % self.headers['referer']).encode())
		f.write(b'<ul></td></tr>')
		f.write(b'<tr><td valign=top bgcolor="#346ca7" height="65%">')
		if r:
			f.write(b"<strong>Success:</strong>")
		else:
			f.write(b"<strong>Failed:</strong>")
		f.write(info.encode())
		f.write(("<br><a href=\"%s\">back</a>" % self.headers['referer']).encode())
		f.write(b"Mod By: OpenNFR Team")
		f.write(b"<a href=\"http://www.nachtfalke.biz\">")
		f.write(b"Nachtfalke</a>.</small></body>\n</html>\n")
		length = f.tell()
		f.seek(0)
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.send_header("Content-Length", str(length))
		self.end_headers()
		if f:
			self.copyfile(f, self.wfile)
			f.close()

	def deal_post_data(self):
		content_type = self.headers['content-type']
		if not content_type:
			return (False, "Content-Type header doesn't contain boundary")
		boundary = content_type.split("=")[1].encode()
		#boundary = self.headers.plisttext.split("=")[1]
		remainbytes = int(self.headers['content-length'])
		line = self.rfile.readline()
		remainbytes -= len(line)
		if not boundary in line:
			return (False, "Content NOT begin with boundary")
		line = self.rfile.readline().decode('utf-8')
		remainbytes -= len(line)
		fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line)
		if fn == [""]:
			nofile = False
		else:
			nofile = True    
		if not fn:
			return (False, "Can't find out file name...")
		path = self.translate_path(self.path)
		osType = platform.system()
		fn = os.path.join(path, fn[0])
		while os.path.exists(fn):
			fn += "_"
		line = self.rfile.readline()
		remainbytes -= len(line)
		line = self.rfile.readline()
		remainbytes -= len(line)
		try:
			if nofile == False:
				return (False, "No file selected! Please select a file and try again.")
			else:
				out = open(fn, 'wb')
		except IOError:
			return (False, "Can't create file to write, do you have permission to write?")

		preline = self.rfile.readline()
		remainbytes -= len(preline)
		while remainbytes > 0:
			line = self.rfile.readline()
			remainbytes -= len(line)
			if boundary in line:
				preline = preline[0:-1]
				if preline.endswith(b'\r'):
					preline = preline[0:-1]
				out.write(preline)
				out.close()
				return (True, "File '%s' upload success!" % fn)
			else:
				out.write(preline)
				preline = line
		return (False, "Unexpect Ends of data.")
		
	def send_head(self):
		"""Common code for GET and HEAD commands.

		This sends the response code and MIME headers.

		Return value is either a file object (which has to be copied
		to the outputfile by the caller unless the command was HEAD,
		and must be closed by the caller under all circumstances), or
		None, in which case the caller has nothing further to do.

		"""
		path = self.translate_path(self.path)
		f = None
		if os.path.isdir(path):
			if not self.path.endswith('/'):
			 	# redirect browser - doing basically what apache does
			 	self.send_response(301)
			 	self.send_header("Location", self.path + "/")
			 	self.end_headers()
			 	return None
			for index in "index.html", "index.htm":
				index = os.path.join(path, index)
				if os.path.exists(index):
					path = index
					break
			else:
				return self.list_directory(path)
		ctype = self.guess_type(path)
		try:
			# Always read in binary mode. Opening files in text mode may cause
			# newline translations, making the actual size of the content
			# transmitted *less* than the content-length!
			f = open(path, 'rb')
		except IOError:
			self.send_error(404, "File not found")
			return None
		self.send_response(200)
		self.send_header("Content-type", ctype)
		fs = os.fstat(f.fileno())
		self.send_header("Content-Length", str(fs[6]))
		self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
		self.end_headers()
		return f

	def list_directory(self, path):
		"""Helper to produce a directory listing (absent index.html).

		Return value is either a file object, or None (indicating an
		error).  In either case, the headers are sent, making the
		interface the same as for send_head().

		"""
		#http.Request.getRequestHostname = new_getRequestHostname
		import netifaces as ni
		ni.ifaddresses('eth0')
		url1 = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
		url = bytes(url1, encoding='UTF-8')
		try:
			list = os.listdir(path)
		except os.error:
			self.send_error(404, "No permission to list directory")
			return None
		list.sort(key=lambda a: a.lower())
		f = BytesIO()
		displaypath = html.escape(urllib.parse.unquote(self.path))
		f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
		f.write(('<html>\n<title>OpenNFR FileLoad %s</title>\n' % displaypath).encode())
		f.write(b'<body>')
		f.write(b'<table width="100%" id="table1" height="100%"><tr><td  bgcolor="#4d4d4d" height="15%"><img src="/usr/lib/enigma2/python/Plugins/Extensions/FileLoad/images/NF_Reloaded_Banner.png" width="948" height="130"></td></tr>')
		f.write(b"<tr><td  bgcolor='#4d4d4d' height='15%'><h2>Directory listing</h2>")
		f.write(b'<form ENCTYPE=\"multipart/form-data\" method=\"post\">')
		f.write(b'<input name=\"file\" type=\"file\"/>')
		f.write(b'<input type=\"submit\" value=\"upload\"/>')
		f.write(b"<input type=\"button\" value=\"HomePage\" onClick=\"location='/'\">")
		f.write(b"<br><br/><input type=\"button\" value=\"usr/emu\" onClick=\"location='/usr/emu/'\">")
		f.write(b"<input type=\"button\" value=\"usr/keys\" onClick=\"location='/usr/keys/'\">")
		f.write(b"<input type=\"button\" value=\"etc/init.d\" onClick=\"location='/etc/init.d/'\">")
		f.write(b"<input type=\"button\" value=\"/tmp\" onClick=\"location='/tmp/'\">")
		f.write(b"<input type=\"button\" value=\"/hdd\" onClick=\"location='/hdd/'\">")
		f.write(b"<br><br/><input type=\"button\" value=\"Back\" onClick=\"location='../'\"></form>")
		f.write(b"<input type=\"button\" value=\"delete\" target=\"_blank\" onClick=\"self.location.href='http://%s:8090'\">" % url)        
		f.write(b'</form>')
		f.write(b'<ul></td></tr>')
		f.write(b'<tr><td valign=top bgcolor="#346ca7" height="65%">')

		for name in list:
			fullname = os.path.join(path, name)
			colorName = displayname = linkname = name
			# Append / for directories or @ for symbolic links
			if os.path.isdir(fullname):
				colorName = '<span style="background-color: #0de7f7;">' + name + '/</span>'
				displayname = name
				linkname = name + "/"
			if os.path.islink(fullname):
				colorName = '<span style="background-color: #adadf0;">' + name + '@</span>'
				displayname = name
				# Note: a link to a directory displays with @ and links with /
			filename = os.getcwd() + '/' + displaypath + displayname
			f.write(('<table bgcolor="#346ca7"><tr><td width="60%%"><a style="color:black;" href="%s">%s</a></td><td width="20%%">%s</td><td width="20%%">%s</td></tr>'% (urllib.parse.quote(linkname), colorName, sizeof_fmt(os.path.getsize(filename)), modification_date(filename))).encode())
		f.write(b"</table></body></html>")
		f.write(b"</table></td></tr></table></body></html>")
		length = f.tell()
		f.seek(0)
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.send_header("Content-Length", str(length))
		self.end_headers()
		return f

	def translate_path(self, path):
		"""Translate a /-separated PATH to the local filename syntax.
        	
		Components that mean special things to the local file system
		(e.g. drive or directory names) are ignored.  (XXX They should
		probably be diagnosed.)

		"""
		# abandon query parameters
		path = path.split('?',1)[0]
		path = path.split('#',1)[0]
		path = posixpath.normpath(urllib.parse.unquote(path))
		words = path.split('/')
		words = filter(None, words)
		path = os.getcwd()
		for word in words:
			drive, word = os.path.splitdrive(word)
			head, word = os.path.split(word)
			if word in (os.curdir, os.pardir): continue
			path = os.path.join(path, word)
		return path

	def copyfile(self, source, outputfile):
		"""Copy all data between two file objects.

		The SOURCE argument is a file object open for reading
		(or anything with a read() method) and the DESTINATION
		argument is a file object open for writing (or
		anything with a write() method).

		The only reason for overriding this would be to change
		the block size or perhaps to replace newlines by CRLF
		-- note however that this the default server uses this
		to copy binary data as well.

		"""
		shutil.copyfileobj(source, outputfile)

	def guess_type(self, path):
		"""Guess the type of a file.

		Argument is a PATH (a filename).

		Return value is a string of the form type/subtype,
		usable for a MIME Content-type header.

		The default implementation looks the file's extension
		up in the table self.extensions_map, using application/octet-stream
		as a default; however it would be permissible (if
		slow) to look inside the data to make a better guess.

		"""

		base, ext = posixpath.splitext(path)
		if ext in self.extensions_map:
			return self.extensions_map[ext]
		ext = ext.lower()
		if ext in self.extensions_map:
			return self.extensions_map[ext]
		else:
			return self.extensions_map['']

	if not mimetypes.inited:
		mimetypes.init() # try to read system mime.types
	extensions_map = mimetypes.types_map.copy()
	extensions_map.update({
		'': 'application/octet-stream', # Default
		'.py': 'text/plain',
		'.c': 'text/plain',
		'.h': 'text/plain',
		})
 
#class ThreadingServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
	#pass

def test(HandlerClass = SimpleHTTPRequestHandler,
	ServerClass = http.server.HTTPServer):
	http.server.test(HandlerClass, ServerClass)

if __name__ == '__main__':
	os.chdir("/")  
	test()

	#???
	# srvr = BaseHTTPServer.HTTPServer(serveraddr, SimpleHTTPRequestHandler)

	#???
	#srvr = ThreadingServer(serveraddr, SimpleHTTPRequestHandler)
	#srvr.serve_forever()
