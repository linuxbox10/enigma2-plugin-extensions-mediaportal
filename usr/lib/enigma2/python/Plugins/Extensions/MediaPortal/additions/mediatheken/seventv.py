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

from Plugins.Extensions.MediaPortal.plugin import _, grabpage, downloadPage
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.twagenthelper import twAgentGetPage

BASE_URL = "http://www.7tv.de"
sevenAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
sevenCookies = CookieJar()
default_cover = "file://%s/seventv.png" % (config.mediaportal.iconcachepath.value + "logos")

logos = ["dmax", "tlc"]

def getlogos():
	ds = defer.DeferredSemaphore(tokens=5)

	icon_url = getIconUrl()

	logo_hashes = grabpage(icon_url+"logos/hashes")
	if logo_hashes:
		logo_data = re.findall('(.*?)\s\*(.*?\.png)', logo_hashes)
	else:
		logo_data = None

	for logo in logos:
		logo_path = "%s/%s.png" % (config.mediaportal.iconcachepath.value + "logos", logo)
		url = icon_url+"logos/" + logo + ".png"
		if not fileExists(logo_path):
			if logo_data:
				for a,b in logo_data:
					if b == logo+'.png':
						ds.run(downloadPage, url, logo_path)
		else:
			if logo_data:
				for a,b in logo_data:
					if b == logo+'.png':
						remote_hash = a
						local_hash = hashlib.md5(open(logo_path, 'rb').read()).hexdigest()
						if remote_hash != local_hash:
							ds.run(downloadPage, url, logo_path)

class sevenFirstScreen(MPScreen, ThumbsHelper):

	def __init__(self, session):
		getlogos()
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"	: self.keyOK,
			"cancel": self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("7TV")
		self['ContentTitle'] = Label(_("Stations:"))
		self['name'] = Label(_("Selection:"))

		self.keyLocked = True
		self.senderliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		twAgentGetPage(BASE_URL, agent=sevenAgent, cookieJar=sevenCookies).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		stations = re.findall('<li class="brandgrid-item"><a class="brandgrid-link brandgrid-[A-Za-z0-9\s]+" title="[A-Za-z0-9\s]+" href="/[A-Za-z0-9\s]+">(.*?)</a></li>', data, re.S)
		self.senderliste.append(("ProSieben", "ProSieben", "seventv"))
		self.senderliste.append(("SAT.1", "SAT.1", "seventv"))
		self.senderliste.append(("kabel eins", "kabel%20eins", "seventv"))
		self.senderliste.append(("sixx", "sixx", "seventv"))
		self.senderliste.append(("ProSieben MAXX", "ProSieben%20MAXX", "seventv"))
		self.senderliste.append(("SAT.1 Gold", "SAT.1%20Gold", "seventv"))
		self.senderliste.append(("kabel eins Doku", "kabel%20eins%20Doku", "seventv"))
		if "DMAX" in stations:
			self.senderliste.append(("DMAX", "DMAX", "dmax"))
		if "TLC" in stations:
			self.senderliste.append(("TLC", "TLC",  "tlc"))
		if "Eurosport" in stations:
			self.senderliste.append(("Eurosport", "Eurosport", "seventv"))
		self.ml.setList(map(self._defaultlistcenter, self.senderliste))
		self.keyLocked = False
		self.th_ThumbsQuery(self.senderliste, 0, 1, 2, None, None, 1, 1, mode=1)
		self.showInfos()

	def showInfos(self):
		Image = "file://%s/%s.png" % (config.mediaportal.iconcachepath.value + "logos", self['liste'].getCurrent()[0][2])
		CoverHelper(self['coverArt']).getCover(Image)
		Name = self['liste'].getCurrent()[0][0]
		self['name'].setText(_("Selection:") + " " + Name)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		global default_cover
		default_cover = "file://%s/%s.png" % (config.mediaportal.iconcachepath.value + "logos", self['liste'].getCurrent()[0][2])
		self.session.open(sevenGenreScreen, Link, Name)

class sevenGenreScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
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

		self['title'] = Label("7TV")
		self['ContentTitle'] = Label(_("Selection:"))
		self['name'] = Label(_("Selection:") + " " + self.Name)

		self.genreliste = []
		self.keyLocked = True
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = BASE_URL + "/queue/format/(brand)/" + self.Link
		twAgentGetPage(url, agent=sevenAgent, cookieJar=sevenCookies).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		json_data = json.loads(data)
		for node in json_data["facet"]:
			self.genreliste.append((str(node).upper(), str(node).upper().replace('#','0-9')))
		self.genreliste.sort(key=lambda t : t[0].lower())
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		Name = self['liste'].getCurrent()[0][0]
		self['name'].setText(_("Selection:") + " " + self.Name + ":" + Name)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(sevenSubGenreScreen, Link, Name, self.Link)

class sevenSubGenreScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, TopLink):
		self.Link = Link
		self.Name = Name
		self.TopLink = TopLink
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"	: self.keyOK,
			"cancel": self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("7TV")
		self['ContentTitle'] = Label(_("Selection:"))
		self['name'] = Label(_("Selection:") + " " + self.Name)

		self.keyLocked = True
		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = BASE_URL + "/queue/format/(brand)/" + self.TopLink + "/(letter)/" + self.Link
		twAgentGetPage(url, agent=sevenAgent, cookieJar=sevenCookies).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		sevendata = json.loads(data.replace('\u0096','-'))
		for node in sevendata["entries"]:
			url = BASE_URL + "/" + str(node["url"])
			image = str(node["images"][0]["url"])
			self.filmliste.append((str(node["title"]), url, image))
		self.filmliste.sort(key=lambda t : t[0].lower())
		self.ml.setList(map(self._defaultlistcenter, self.filmliste))
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, 1, 1, mode=1)
		self.showInfos()

	def showInfos(self):
		Image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(Image)
		Name = self['liste'].getCurrent()[0][0]
		self['name'].setText(_("Selection:") + " " + self.Name + ":" + Name)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		Name = self.Name + ":" + self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		Image = self['liste'].getCurrent()[0][2]
		if Link:
			self.session.open(sevenStreamScreen, Link, Name, Image)

class sevenStreamScreen(MPScreen):

	def __init__(self, session, Link, Name, Image):
		self.Link = Link
		self.Name = Name
		self.Image = Image
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"	: self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("7TV")
		self['name'] = Label(_("Selection:") + " " + self.Name)

		self.keyLocked = True
		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self, x=0):
		if x == 0:
			url = self.Link + "/ganze-folgen"
			self['ContentTitle'].setText(_("Episodes:"))
		else:
			url = self.Link + "/alle-clips"
			self['ContentTitle'].setText(_("Clips:"))
		print url
		twAgentGetPage(url, agent=sevenAgent, cookieJar=sevenCookies).addCallback(self.parseData, x).addErrback(self.dataError)

	def parseData(self, data, x):
		articles = re.findall("<article class(.*?)</article>", data, re.S)
		if articles:
			for node in articles:
				episodes = re.findall('href="(.*?)".*?data-src="(.*?)".*?teaser-title">(.*?)</h5>', node, re.S)
				if episodes:
					for (url, img, title) in episodes:
						url = BASE_URL + url
						img = img.replace('300x160','620x348')
						self.filmliste.append((title, url, img))
		if len(self.filmliste) == 0:
			if x == 1:
				CoverHelper(self['coverArt']).getCover(self.Image)
				self.filmliste.append((_('Currently no episodes/clips available!'), None, None))
				self.ml.setList(map(self._defaultlistleft, self.filmliste))
			else:
				self.loadPage(1)
		else:
			self.ml.setList(map(self._defaultlistleft, self.filmliste))
			self.keyLocked = False
			self.showInfos()

	def showInfos(self):
		self['handlung'].setText("")
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		Cover = self['liste'].getCurrent()[0][2]
		self['name'].setText(_("Selection:") + " " + self.Name + ":" + Name)
		CoverHelper(self['coverArt']).getCover(Cover)
		if Link:
			twAgentGetPage(Link, agent=sevenAgent, cookieJar=sevenCookies).addCallback(self.parseInfos).addErrback(self.dataError)

	def parseInfos(self, data):
		resources = re.findall('contentResources =\s\[(.*?}}})(?:\]|,{"tvShowTitle|,{"sourceCompany)', data, re.S)
		if resources:
			json_data = json.loads(resources[0])
			descr = "\n" + str(json_data["teaser"]["description"])
		else:
			descr = ""
		duration = re.findall('name="video_duration" content="(.*?)">', data, re.S)
		date = re.findall('name="date" content="(.*?)">', data, re.S)
		season = re.findall('property="video:series_number" content="(.*?)">', data, re.S)
		episode = re.findall('property="video:episode_number" content="(.*?)">', data, re.S)

		if duration:
			runtime = "Laufzeit: " + duration[0] + "\n"
		else:
			runtime = ""

		if date:
			date = "Datum: " + date[0] + "\n"
		else:
			date = ""

		if season and episode:
			epi = "Staffel: " + season[0] + " Episode: " + episode[0] + "\n"
		else:
			epi = ""

		self['handlung'].setText(date+runtime+epi+descr)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		Link = self['liste'].getCurrent()[0][1]
		if Link:
			twAgentGetPage(Link, agent=sevenAgent, cookieJar=sevenCookies).addCallback(self.parseData2, Link).addErrback(self.dataError)

	def parseData2(self, data, client_location):
		self.client_location = client_location
		cid = re.findall('"cid":(\d+),', data, re.S)
		if cid:
			self.video_id = cid[0]
			self.access_token = 'hbbtv'
			self.client_name = 'hbbtv'
			json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s?access_token=%s&client_location=%s&client_name=%s' % (self.video_id, self.access_token, client_location, self.client_name)
			twAgentGetPage(json_url, agent=sevenAgent, cookieJar=sevenCookies).addCallback(self.parseData3).addErrback(self.dataError)

	def parseData3(self, data):
		json_data = json.loads(data)
		self.salt = '01ree6eLeiwiumie7ieV8pahgeiTui3B'
		self.source_id = 0
		if json_data["is_protected"]:
			message = self.session.open(MessageBoxExt, _("This episode/clip can't be played it's protected with DRM."), MessageBoxExt.TYPE_INFO, timeout=5)
			return
		else:
			for stream in json_data['sources']:
				if stream['mimetype'] == 'video/mp4':
					if int(self.source_id) < int(stream['id']):
						self.source_id = stream['id']
		client_id_1 = self.salt[:2] + hashlib.sha1(''.join([str(self.video_id), self.salt, self.access_token, self.client_location, self.salt, self.client_name]).encode('utf-8')).hexdigest()
		json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources?access_token=%s&client_location=%s&client_name=%s&client_id=%s' % (self.video_id, self.access_token, self.client_location, self.client_name, client_id_1)
		twAgentGetPage(json_url, agent=sevenAgent, cookieJar=sevenCookies).addCallback(self.parseData4).addErrback(self.dataError)

	def parseData4(self, data):
		json_data = json.loads(data)
		server_id = json_data['server_id']
		client_id = self.salt[:2] + hashlib.sha1(''.join([self.salt, self.video_id, self.access_token, server_id, self.client_location, str(self.source_id), self.salt, self.client_name]).encode('utf-8')).hexdigest()
		json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources/url?%s' % (self.video_id, urllib.urlencode({'access_token': self.access_token, 'client_id': client_id, 'client_location': self.client_location, 'client_name': self.client_name, 'server_id': server_id, 'source_ids': str(self.source_id),}))
		twAgentGetPage(json_url, agent=sevenAgent, cookieJar=sevenCookies).addCallback(self.parseData5).addErrback(self.dataError)

	def parseData5(self, data):
		json_data = json.loads(data)
		max_id = 0
		for stream in json_data["sources"]:
			url = stream["url"]
			try:
				sid=re.findall('-tp([0-9]+).mp4', url, re.S)[0]
				id = int(sid)
				if max_id < id:
					max_id = id
					stream_url = str(url)
			except:
				stream_url = str(url)
		mp_globals.player_agent = sevenAgent
		Name = self['liste'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(Name, stream_url)], showPlaylist=False, ltype='7tv')