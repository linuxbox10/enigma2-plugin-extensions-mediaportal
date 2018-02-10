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
default_cover = "file://%s/funk.png" % (config.mediaportal.iconcachepath.value + "logos")

headers = {
	'Authorization':'1efb06afc842521f5693b5ce4e5b6c4530ce4ea8c1c09ed618f91da39c11da92',
	'User-Agent':'okhttp/3.2.0',
	'Accept-Encoding':'gzip',
	'Host':' api.funk.net',
}

BASE_URL = 'https://api.funk.net/v1.1'

class funkGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("FUNK")
		self['ContentTitle'] = Label("Genre:")

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.genreliste.append(('Formate', 'formats'))
		self.genreliste.append(('Serien', 'series'))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))

	def keyOK(self):
		Name = self['liste'].getCurrent()[0][0]
		genreID = self['liste'].getCurrent()[0][1]
		self.session.open(funkSubGenreScreen, genreID, Name)

class funkSubGenreScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, genreID, Name):
		self.genreID = genreID
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok" : self.keyOK,
			"cancel" : self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("FUNK")
		self['ContentTitle'] = Label("Auswahl: %s" % self.Name)
		self['name'] = Label(_("Selection:"))

		self.keyLocked = True

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = BASE_URL + "/content/%s/?page=0&size=100" % self.genreID
		getPage(url, headers=headers).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		json_data = json.loads(data)
		for item in json_data["data"]:
			if item["attributes"].has_key('thumbnail') and not "8415ad90686d2c75aca239372903a45e" in item["attributes"]["thumbnail"]:
				image = str(item["attributes"]["thumbnail"]).strip() + "?width=600"
			elif item["attributes"].has_key('imageUrlLandscape') and not "8415ad90686d2c75aca239372903a45e" in item["attributes"]["imageUrlLandscape"]:
				image = "https://cdn.funk.net/v2/image/" + str(item["attributes"]["imageUrlLandscape"]).strip() + "?width=600"
			else:
				image = None
			title = str(item["attributes"]["name"])
			if item["attributes"].has_key('description'):
				descr = decodeHtml(str(item["attributes"]["description"]))
			else:
				descr = ""
			type = str(item["type"])
			if type == "format" : type = "formats"
			url = BASE_URL + "/content/" + type + "/" + str(item["id"]) + "?should_filter=false"
			self.filmliste.append((title, image, url, descr))
		self.filmliste.sort(key=lambda t : t[0].lower())
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 2, 1, None, None, 1, 1)
		self.showInfos()

	def showInfos(self):
		Title = self['liste'].getCurrent()[0][0]
		Image = self['liste'].getCurrent()[0][1]
		descr = self['liste'].getCurrent()[0][3]
		self['name'].setText(Title)
		self['handlung'].setText(descr)
		CoverHelper(self['coverArt']).getCover(Image)

	def keyOK(self):
		Name = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][2]
		self.session.open(funkSeriesScreen, url, Name)

class funkSeriesScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, url, Name):
		self.url = url
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok" : self.keyOK,
			"cancel" : self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("FUNK")
		self['ContentTitle'] = Label("Auswahl: %s" % self.Name)
		self['name'] = Label(_("Selection:"))

		self.keyLocked = True

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		getPage(self.url, headers=headers).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		json_data = json.loads(data)
		for item in json_data["includes"]:
			if item["attributes"].has_key('image'):
				image = str(item["attributes"]["image"]["url"]).strip() + "?width=600"
			else:
				image = None
			title = str(item["attributes"]["name"])
			if item["attributes"].has_key('description'):
				descr = decodeHtml(str(item["attributes"]["description"]))
			else:
				descr = ""
			if item["attributes"].has_key('duration'):
				duration = int(item["attributes"]["duration"])
				m, s = divmod(duration, 60)
				duration = "Laufzeit: %02d:%02d\n" % (m, s)
			else:
				duration = ""
			if item["attributes"].has_key('episodeNr'):
				episode = int(item["attributes"]["episodeNr"])
			else:
				episode = ""
			if item["attributes"].has_key('seasonNr'):
				season = int(item["attributes"]["seasonNr"])
			else:
				season = ""
			if season and episode:
				if (season and episode) > 0:
					epi = "Staffel: " + str(season) + " Episode: " + str(episode) + "\n"
				else:
					epi = ""
			else:
				epi = ""
			if item["attributes"].has_key('sourceId'):
				id = str(item["attributes"]["sourceId"])
			else:
				id = None
			if item["attributes"].has_key('downloadUrl'):
				downld = str(item["attributes"]["downloadUrl"])
			else:
				downld = None

			self.filmliste.append((title, image, id, descr, epi, duration, downld))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 2, 1, None, None, 1, 1)
		self.showInfos()

	def showInfos(self):
		Title = self['liste'].getCurrent()[0][0]
		Image = self['liste'].getCurrent()[0][1]
		descr = self['liste'].getCurrent()[0][3]
		epi = self['liste'].getCurrent()[0][4]
		dur = self['liste'].getCurrent()[0][5]
		self['name'].setText(Title)
		self['handlung'].setText(dur+epi+descr)
		CoverHelper(self['coverArt']).getCover(Image)

	def keyOK(self):
		if self.keyLocked:
			return
		id = self['liste'].getCurrent()[0][2]
		Title = self['liste'].getCurrent()[0][0]
		downld = self['liste'].getCurrent()[0][6]
		if id:
			from Plugins.Extensions.MediaPortal.resources import nexx
			videourl = nexx.getVideoUrl(id, downld)
		if videourl:
			if "m3u8" in videourl:
				if config.mediaportal.use_hls_proxy.value:
					self.session.open(SimplePlayer, [(Title, videourl)], showPlaylist=False, ltype='funk')
				else:
					message = self.session.open(MessageBoxExt, _("If you want to play this stream, you have to activate the HLS-Player in the MP-Setup"), MessageBoxExt.TYPE_INFO, timeout=5)
			else:
				self.session.open(SimplePlayer, [(Title, videourl)], showPlaylist=False, ltype='funk')