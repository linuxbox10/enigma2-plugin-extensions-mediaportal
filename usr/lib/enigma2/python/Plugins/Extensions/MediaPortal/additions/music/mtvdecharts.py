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
from Plugins.Extensions.MediaPortal.resources.mtvdelink import MTVdeLink

class MTVdeChartsGenreScreen(MPScreen):

	def __init__(self, session):

		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("MTV.de")
		self['ContentTitle'] = Label("Charts:")

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.genreliste = [('MTV.DE Hitlist Germany - Top100',"http://www.mtv.de/charts/c6mc86/single-top-100"),
				('MTV.DE Single Midweek Charts',"http://www.mtv.de/charts/n91ory/midweek-single-top-100"),
				('MTV.DE Single Top20',"http://www.mtv.de/charts/bcgxiq/single-top-20"),
				('MTV.DE Dance Charts',"http://www.mtv.de/charts/2ny5w9/dance-charts"),
				('MTV.DE Single Trending',"http://www.mtv.de/charts/9gtiy5/single-trending"),
				('MTV.DE Streaming Charts',"http://www.mtv.de/charts/h4oi23/top100-music-streaming"),
				('MTV.DE Deutschsprachige Single Charts Top15',"http://www.mtv.de/charts/jlyhaa/top-15-deutschsprachige-single-charts"),
				('MTV.DE Download Charts',"http://www.mtv.de/charts/pcbqpc/downloads-charts-single"),
				('MTV.DE Most Wanted 90\'s',"http://www.mtv.de/charts/xlad55/most-wanted-90"),
				('MTV.DE Most Wanted 2000\'s',"http://www.mtv.de/charts/h5hl40/most-wanted-2000"),
				('MTV.DE Top100 Jahrescharts 2017',"http://www.mtv.de/charts/czzmta/top-100-jahrescharts-2017"),
				('MTV.DE Top100 Jahrescharts 2016',"http://www.mtv.de/charts/yrk67s/top-100-jahrescharts-2016"),
				('MTV.DE Top100 Jahrescharts 2015',"http://www.mtv.de/charts/4z2jri/top-100-jahrescharts-2015"),
				('MTV.DE Top100 Jahrescharts 2014',"http://www.mtv.de/charts/ns9mkd/top-100-jahrescharts-2014"),
				('MTV.CH Videocharts',"http://www.mtv.ch/charts/206-mtv-ch-videocharts"),
				('MTV.DK Denmark Top5',"http://www.mtv.dk/hitlister/24-top-5-musikvideoer"),
				('MTV.SE Sweden Top5',"http://www.mtv.se/charts/23-top-5-musikvideor"),
				('MTV.NO Norway Most Clicked',"http://www.mtv.no/charts/195-mtv-norway-most-clicked")]

		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		MTVName = self['liste'].getCurrent()[0][0]
		MTVUrl = self['liste'].getCurrent()[0][1]
		self.session.open(MTVdeChartsSongListeScreen, MTVName, MTVUrl)

class MTVdeChartsSongListeScreen(MPScreen):

	def __init__(self, session, genreName, genreLink):
		self.genreLink = genreLink
		self.genreName = genreName
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0" : self.closeAll,
			"ok" : self.keyOK,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self.keyLocked = True
		self['title'] = Label("MTV.de")
		self['ContentTitle'] = Label("Charts: %s" % self.genreName)

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.json_url = None
		self.page = 0

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self['name'].setText(_('Please wait...'))
		self.keyLocked = True
		if self.page > 0:
			url = self.json_url + "/" + str(self.page)
		else:
			url = self.genreLink
		getPage(url).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		if "MTV.DE" in self.genreName:
			if not self.json_url:
				jsonurl = re.findall('class="module intl_m327" data-tfstatic="true" data-tffeed="(.*?)"', data, re.S)
				if jsonurl:
					self.json_url = jsonurl[0]
				self.page += 1
				self.loadPage()
			else:
				json_data = json.loads(data)
				for item in json_data["result"]["data"]["items"]:
					if item.has_key('videoUrl'):
						videourl = str(item["videoUrl"])
						pos = str(item["chartPosition"]["current"])
						title = str(item["title"])
						try:
							artist = str(item["artists"][0]["name"])
						except:
							artist = str(item["shortTitle"])
						image = str(item["images"][0]["url"])

						vidtitle = pos + ". " + artist + " - " + title
						self.filmliste.append((vidtitle,videourl,image))
				if "nextPageURL" in data:
					self.page += 1
					self.loadPage()
				else:
					self.ml.setList(map(self._defaultlistleft, self.filmliste))
					self.showInfos()
					self.keyLocked = False
		else:
			charts = re.findall('<div\sclass="chart-position">(.*?)</div>.*?data-object-id="(.*?)">', data, re.S)
			if charts:
				part = re.search('pagePlaylist(.*?)trackingParams', data, re.S)
				if part:
					for (pos, id) in charts:
						track = re.findall('"id":%s,"title":"(.*?)","subtitle":"(.*?)","video_type":"(.*?)","video_token":"(.*?)","riptide_image_id":(".*?"|null),' % id, part.group(1), re.S)
						if track:
							for (artist,title,type,token,image_id) in track:
								image = "http://images.mtvnn.com/%s/306x172" % image_id.replace('"','')
								title = str(pos) + ". " + artist + " - " + title
								self.filmliste.append((decodeHtml(title).replace('\\"','"'),token,image))
			self.ml.setList(map(self._defaultlistleft, self.filmliste))
			self.showInfos()
			self.keyLocked = False

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		coverUrl = self['liste'].getCurrent()[0][2]
		self['name'].setText(title)
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def keyOK(self):
		if self.keyLocked:
			return
		idx = self['liste'].getSelectedIndex()
		if config.mediaportal.use_hls_proxy.value:
			self.session.open(MTVdeChartsPlayer, self.filmliste, int(idx) , True, self.genreName)
		else:
			message = self.session.open(MessageBoxExt, _("If you want to play this stream, you have to activate the HLS-Player in the MP-Setup"), MessageBoxExt.TYPE_INFO, timeout=5)

class MTVdeChartsPlayer(SimplePlayer):

	def __init__(self, session, playList, playIdx=0, playAll=True, listTitle=None):
		SimplePlayer.__init__(self, session, playList, playIdx=playIdx, playAll=playAll, listTitle=listTitle, ltype='mtv')

	def getVideo(self):
		title = self.playList[self.playIdx][self.title_inr]
		token = self.playList[self.playIdx][1]
		imgurl = self.playList[self.playIdx][2]

		artist = ''
		p = title.find(' - ')
		if p > 0:
			artist = title[:p].strip()
			title = title[p+3:].strip()

		MTVdeLink(self.session).getLink(self.playStream, self.dataError, title, artist, token, imgurl)