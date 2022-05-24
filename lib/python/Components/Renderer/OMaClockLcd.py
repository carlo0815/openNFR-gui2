
import math
from Components.Renderer.Renderer import Renderer
from skin import parseColor
from enigma import eCanvas, eSize, gRGB, eRect
from Components.VariableText import VariableText
from Components.config import config
from past.utils import old_div
from boxbranding import getBoxType

LCDSIZE400 = []
LCDSIZE400 = False
LCDSIZE480 = False
LCDSIZE800 = False
LCDSIZE220 = False

if getBoxType() in ('twinboxlcd', 'gb800ueplus', 'gb800seplus', 'gbultraue', 'singleboxlcd', 'sf208', 'sf228', 'e4hd', 'e4hdultra', 'gbue4k'):
	LCDSIZE220 = True
elif getBoxType() in ('gbquadplus', 'gbquad4k'):
	LCDSIZE400 = True
elif getBoxType() in ('vusolo4k'):
	LCDSIZE480 = True
elif getBoxType() in ('vuultimo4k'):
	LCDSIZE800 = True
else:
	LCDSIZE400 = False
	LCDSIZE480 = False
	LCDSIZE220 = False
	LCDSIZE800 = False
#print "LCDSIZE400: ", LCDSIZE400

class OMaClockLcd(Renderer):
	def __init__(self):
		Renderer.__init__(self)
		self.fColor = gRGB(255, 255, 255, 0)
		self.fColors = gRGB(255, 0, 0, 0)
		self.fColorm = gRGB(255, 0, 0, 0)
		self.fColorh = gRGB(255, 255, 255, 0)
		self.bColor = gRGB(0, 0, 0, 255)
		self.forend = -1
		self.linewidth = 1

	GUI_WIDGET = eCanvas

	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, what) in self.skinAttributes:
			if (attrib == 'hColor'):
				self.fColorh = parseColor(what)
			elif (attrib == 'mColor'):
				self.fColorm = parseColor(what)
			elif (attrib == 'sColor'):
				self.fColors = parseColor(what)
			elif (attrib == 'linewidth'):
				self.linewidth = int(what)
			else:
				attribs.append((attrib, what))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	def calc(self, w, r, m, m1):
		a = (w * 6)
		z = (old_div(math.pi, 180))
		x = int(round((r * math.sin((a * z)))))
		y = int(round((r * math.cos((a * z)))))
		return ((m + x), (m1 - y))

	def hand(self, opt):
		if LCDSIZE400:
			width = 396
			height = 240
			l = 55
		elif LCDSIZE480:
			width = 475
			height = 316
			l = 66
		elif LCDSIZE800:
			width = 792
			height = 475
			l = 110
		elif LCDSIZE220:
			width = 218
			height = 176
			l = 35
		else:
			width = 218
			height = 176
			l = 35
		r = (old_div(width, 2))
		r1 = (old_div(height, 2))

		if opt == 'sec':
			if LCDSIZE400:
				l = l + 60
			elif LCDSIZE480:
				l = l + 72
			elif LCDSIZE800:
				l = l + 120
			elif LCDSIZE220:
				l = l + 50
			else:
				l = l + 50
			self.fColor = self.fColors
		elif opt == 'min':
			if LCDSIZE400:
				l = l + 50
			elif LCDSIZE480:
				l = l + 66
			elif LCDSIZE800:
				l = l + 100
			elif LCDSIZE220:
				l = l + 40
			else:
				l = l + 40
			self.fColor = self.fColorm
		else:
			self.fColor = self.fColorh
		(endX, endY,) = self.calc(self.forend, l, r, r1)
		self.line_draw(r, r1, endX, endY)

	def line_draw(self, x0, y0, x1, y1):
		steep = (abs((y1 - y0)) > abs((x1 - x0)))
		if steep:
			x0, y0 = y0, x0
			x1, y1 = y1, x1
		if (x0 > x1):
			x0, x1 = x1, x0
			y0, y1 = y1, y0
		if (y0 < y1):
			ystep = 1
		else:
			ystep = -1
		deltax = (x1 - x0)
		deltay = abs((y1 - y0))
		error = (old_div(-deltax, 2))
		y = y0
		for x in list(range(x0, (x1 + 1))):
			if steep:
				self.instance.fillRect(eRect(y, x, self.linewidth, self.linewidth), self.fColor)
			else:
				self.instance.fillRect(eRect(x, y, self.linewidth, self.linewidth), self.fColor)
			error = (error + deltay)
			if (error > 0):
				y = (y + ystep)
				error = (error - deltax)

	def changed(self, what):
		opt = (self.source.text).split(',')
		try:
			sopt = int(opt[0])
			if len(opt) < 2:
				opt.append('')
		except Exception as e:
			return

		if (what[0] == self.CHANGED_CLEAR):
			pass
		elif self.instance:
			self.instance.show()
			if (self.forend != sopt):
				self.forend = sopt
				self.instance.clear(self.bColor)
				self.hand(opt[1])

	def parseSize(self, str):
		(x, y) = str.split(',')
		return eSize(int(x), int(y))

	def postWidgetCreate(self, instance):
		for (attrib, value) in self.skinAttributes:
			if ((attrib == 'size') and self.instance.setSize(self.parseSize(value))):
				pass
		self.instance.clear(self.bColor)
