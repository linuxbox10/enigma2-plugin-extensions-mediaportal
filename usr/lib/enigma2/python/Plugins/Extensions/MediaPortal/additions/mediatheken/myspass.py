# -*- coding: utf-8 -*-
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
default_cover = "file://%s/myspass.png" % (config.mediaportal.iconcachepath.value + "logos")

class myspassGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self.keyLocked = True
		self['title'] = Label("MySpass.de")
		self['ContentTitle'] = Label("Sendungen A-Z:")

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = "http://www.myspass.de/ganze-folgen/"
		getPage(url).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		ganze = re.findall('class="myspassTeaser _seasonId seasonlistItem.*?<a\shref="(/shows/.*?)".*?\s(?:data-original|img\ssrc)="(.*?\.jpg)".*?alt="(.*?)"', data, re.S)
		if ganze:
			self.genreliste = []
			for (link, image, name) in ganze:
				link = "http://www.myspass.de%s" % link
				image = "http://www.myspass.de%s" % image
				self.genreliste.append((decodeHtml(name), link, image))
			# remove duplicates
			self.genreliste = list(set(self.genreliste))
			self.genreliste.sort(key=lambda t : t[0].lower())
		if len(self.genreliste) == 0:
			self.genreliste.append((_("No shows found!"), None, None))
		self.ml.setList(map(self._defaultlistleft, self.genreliste))
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		Image = self['liste'].getCurrent()[0][2]
		Title = self['liste'].getCurrent()[0][0]
		self['name'].setText(Title)
		CoverHelper(self['coverArt']).getCover(Image)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Url = self['liste'].getCurrent()[0][1]
		if Url:
			self.session.open(myspassStaffelListeScreen, Name, Url)

class myspassStaffelListeScreen(MPScreen):

	def __init__(self, session, myspassName, myspassUrl):
		self.myspassName = myspassName
		self.myspassUrl = myspassUrl
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("MySpass.de")
		self['ContentTitle'] = Label("Staffeln:")

		self.staffelliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		getPage(self.myspassUrl).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		self.data = data
		parse = re.search('data-category="full_episode".*?data-target="#episodes_season__category_">(.*?)</ul>', data, re.S)
		if parse:
			staffeln = re.findall('data-query=".*?.*?formatId=(\d+).*?seasonId=(\d+)&amp(.*?)data-target.*?>\t{0,5}\s{0,15}(.*?)</li', parse.group(1), re.S)
			if staffeln:
				self.staffelliste = []
				for (formatid, seasonid, pages, name) in staffeln:
					self.staffelliste.append((decodeHtml(name).strip(), seasonid))
		if len(self.staffelliste) == 0:
			self.staffelliste.append((_('No seasons found!'), None))
		self.ml.setList(map(self._defaultlistleft, self.staffelliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		season = self['liste'].getCurrent()[0][0]
		seasonid = self['liste'].getCurrent()[0][1]
		if seasonid:
			self.session.open(myspassFolgenListeScreen, season, seasonid, self.data)

class myspassFolgenListeScreen(MPScreen):

	def __init__(self, session, season, seasonid, data):
		self.season = season
		self.seasonid = seasonid
		self.data = data
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self.keyLocked = True
		self['title'] = Label("MySpass.de")
		self['ContentTitle'] = Label(self.season + " Episoden:")

		self.folgenliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPageData)

	def loadPageData(self):
		data = re.search('.*?div class="full_episode_seasonlist full_episode_seasonId%s" data-view="list(.*?)</tbody>' % self.seasonid, self.data, re.S).group(1)
		folgen = re.findall('data-href=".*?--\/(\d+)\/"\s+title="(.*?)".*?<b>(.*?)</b></td><td>(.*?)</td><td>.*?\s+(\d+:\d+(?::\d+|))\s+', data, re.S|re.I)
		if folgen:
			for (id, description, episode, title, runtime) in folgen:
				link = "http://www.myspass.de/includes/apps/video/getvideometadataxml.php?id=%s" % id
				image = "http://www.myspass.de/myspass/media/images/videos/%s/%s_640x360.jpg" % (id[-2:], id)
				title = "Episode " + episode + " - " + decodeHtml(title)
				self.folgenliste.append((title, link, image, description, runtime))
			self.ml.setList(map(self._defaultlistleft, self.folgenliste))
			self.keyLocked = False
			self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		descr = self['liste'].getCurrent()[0][3]
		runtime = self['liste'].getCurrent()[0][4]
		self['name'].setText(title)
		self['handlung'].setText("Laufzeit: "+runtime+"\n\n"+descr)
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		self.myname = self['liste'].getCurrent()[0][0]
		self.mylink = self['liste'].getCurrent()[0][1]
		getPage(self.mylink).addCallback(self.get_link).addErrback(self.dataError)

	def get_link(self, data):
		stream_url = re.search('<url_flv><.*?CDATA\[(.*?)\]\]></url_flv>', data, re.S)
		if stream_url:
			self.session.open(SimplePlayer, [(self.myname, stream_url.group(1))], showPlaylist=False, ltype='myspass')