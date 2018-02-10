﻿# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.resources.imports import *
from twagenthelper import twDownloadPage

glob_icon_num = 0
glob_last_cover = [None, None]

class CoverHelper:

	COVER_PIC_PATH = "/tmp/.Icon%d.jpg"
	NO_COVER_PIC_PATH = "/images/no_coverArt.png"

	def __init__(self, cover, callback=None, nc_callback=None):
		self._cover = cover
		self.picload = ePicLoad()
		self._no_picPath = "%s%s/%s%s" % (mp_globals.pluginPath, mp_globals.skinsPath, mp_globals.currentskin, self.NO_COVER_PIC_PATH)
		if not fileExists(self._no_picPath):
			self._no_picPath = "%s%s%s%s" % (mp_globals.pluginPath, mp_globals.skinsPath, mp_globals.skinFallback, self.NO_COVER_PIC_PATH)
		self._callback = callback
		self._nc_callback = nc_callback
		self.downloadPath = None
		self.err_nocover = True
		self.logofix = False

	def downloadPage(self, url, path, agent=None, cookieJar=None):
		if not agent:
			agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
		return twDownloadPage(url, path, timeout=15, agent=agent, cookieJar=cookieJar)

	def closeFile(self, result, f):
		f.close()
		return result

	def checkFilesize(self, data):
		if not data:
			raise Exception("Size error")
		else:
			return data

	def getCover(self, url, download_cb=None, agent=None, cookieJar=None):
		global glob_icon_num
		global glob_last_cover
		self.logofix = False
		if url:
			if url.startswith('http'):
				if glob_last_cover[0] == url and glob_last_cover[1]:
					self.showCoverFile(glob_last_cover[1])
					if download_cb:
						download_cb(glob_last_cover[1])
				else:
					glob_icon_num = (glob_icon_num + 1) % 2
					glob_last_cover[0] = url
					glob_last_cover[1] = None
					self.downloadPath = self.COVER_PIC_PATH % glob_icon_num
					d = self.downloadPage(url, self.downloadPath, agent=agent, cookieJar=cookieJar)
					d.addCallback(self.showCover)
					if download_cb:
						d.addCallback(self.cb_getCover, download_cb)
					d.addErrback(self.dataErrorP)
			elif url.startswith('file://'):
				logopath = (config.mediaportal.iconcachepath.value + "logos")
				if logopath in url:
					self.logofix = True
				self.showCoverFile(url[7:])
				if download_cb:
					download_cb(url[7:])
			else:
				self.showCoverNone()
				if download_cb:
					download_cb(self._no_picPath)
		else:
			self.showCoverNone()
			if download_cb:
				download_cb(self._no_picPath)

	def cb_getCover(self, result, download_cb):
		download_cb(result)

	def dataErrorP(self, error):
		printl(error,self,'E')
		self.showCoverNone()

	def showCover(self, picfile):
		if picfile == 'cancelled':
			return self.dataErrorP(picfile)
		else:
			self.showCoverFile(picfile)
		glob_last_cover[1] = picfile
		return picfile

	def showCoverNone(self):
		if not self.err_nocover:
			return
		else:
			self.err_nocover = False

		if self._nc_callback:
			self._cover.hide()
			self._nc_callback()
		else:
			self.showCoverFile(self._no_picPath)

		return(self._no_picPath)

	def showCoverFile(self, picPath, showNoCoverart=True):
		if fileExists(picPath):
			try:
				self._cover.instance.setPixmap(gPixmapPtr())
				scale = AVSwitch().getFramebufferScale()
				size = self._cover.instance.size()
				if mp_globals.fakeScale and not self.logofix:
					self.picload.setPara((size.width(), size.height(), scale[0], scale[1], False, 1, "#00000000"))
				else:
					self.picload.setPara((size.width(), size.height(), scale[0], scale[1], False, 1, "#FF000000"))
				self.updateCover(picPath)
			except AttributeError:
				pass
		else:
			printl("Coverfile not found: %s" % picPath, self, "E")
			if showNoCoverart and picPath != self._no_picPath:
				self.showCoverFile(self._no_picPath)

		if self._callback:
			self._callback()

	def updateCover(self, picPath):
		if mp_globals.isDreamOS:
			res = self.picload.startDecode(picPath, False)
		else:
			res = self.picload.startDecode(picPath, 0, 0, False)

		if not res:
			ptr = self.picload.getData()
			if ptr != None:
				w = ptr.size().width()
				h = ptr.size().height()
				ratio = float(w) / float(h)
				if self._nc_callback and ratio > 1.05:
					self.showCoverNone()
				else:
					self._cover.instance.setPixmap(ptr)
					self._cover.show()
				return

		self.showCoverNone()