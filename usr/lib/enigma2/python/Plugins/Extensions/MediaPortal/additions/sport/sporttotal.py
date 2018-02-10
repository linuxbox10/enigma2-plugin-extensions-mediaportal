﻿# -*- coding: utf-8 -*-
###############################################################################################
#
#    MediaPortal for Dreambox OS
#
#    Coded by MediaPortal Team (c) 2013-2018
#
#  This plugin is open source but it is NOT free software.
#
#  This plugin may only be distributed to and executed on hardware which
#  is licensed by Dream Property GmbH. This includes commercial distribution.
#  In other words:
#  It's NOT allowed to distribute any parts of this plugin or its source code in ANY way
#  to hardware which is NOT licensed by Dream Property GmbH.
#  It's NOT allowed to execute this plugin and its source code or even parts of it in ANY way
#  on hardware which is NOT licensed by Dream Property GmbH.
#
#  This applies to the source code as a whole as well as to parts of it, unless
#  explicitely stated otherwise.
#
#  If you want to use or modify the code or parts of it,
#  you have to keep OUR license and inform us about the modifications, but it may NOT be
#  commercially distributed other than under the conditions noted above.
#
#  As an exception regarding execution on hardware, you are permitted to execute this plugin on VU+ hardware
#  which is licensed by satco europe GmbH, if the VTi image is used on that hardware.
#
#  As an exception regarding modifcations, you are NOT permitted to remove
#  any copy protections implemented in this plugin or change them for means of disabling
#  or working around the copy protections, unless the change has been explicitly permitted
#  by the original authors. Also decompiling and modification of the closed source
#  parts is NOT permitted.
#
#  Advertising with this plugin is NOT allowed.
#  For other uses, permission from the authors is necessary.
#
###############################################################################################

from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

default_cover = "file://%s/sporttotal.png" % (config.mediaportal.iconcachepath.value + "logos")

class sporttotalGenreScreen(MPScreen):

	def __init__(self, session):

		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("sporttotal.tv")
		self['ContentTitle'] = Label("Livespiele:")

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self['name'].setText(_('Please wait...'))
		url = "http://www.sporttotal.tv/live"
		getPage(url).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		info = re.findall('class="table-link"\sdata-href="(.*?)".*?class="date">(.*?)</.*?class="staffelname">(.*?)</.*?class="teams">(.*?)</', data, re.S)
		if info:
			self.genreliste = []
			for (url, date, season, teams) in info:
				match = "%s: %s, %s" % (season.strip(), date.strip(), teams.strip())
				url = 'http://www.sporttotal.tv' + url
				self.genreliste.append((decodeHtml(match), url))
		else:
			self.genreliste.append((_("Currently no streams available"), None))
		self.ml.setList(map(self._defaultlistleft, self.genreliste))
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		self['name'].setText('')

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		if url:
			getPage(url).addCallback(self.getStream).addErrback(self.dataError)

	def getStream(self, data):
		streams = re.findall('file:\s"(.*?)",', data, re.S)
		if not streams:
			streams = re.findall('<source\ssrc="(.*?)"\stype="', data, re.S)
		if streams:
			name = self['liste'].getCurrent()[0][0]
			self.session.open(SimplePlayer, [(name, streams[0])], showPlaylist=False, ltype='sporttotal', forceGST=True)