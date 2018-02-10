﻿# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
import Queue
import threading
from Plugins.Extensions.MediaPortal.resources.youtubelink import YoutubeLink
from Plugins.Extensions.MediaPortal.resources.menuhelper import MenuHelper
from Plugins.Extensions.MediaPortal.resources.twagenthelper import twAgentGetPage

FVCDE_Version = "FUNNY-VIDEOCLIPS.DE"

FVCDE_siteEncoding = 'utf-8'

class show_FVCDE_Genre(MenuHelper):

	def __init__(self, session):
		MenuHelper.__init__(self, session, 0, [[]], "http://www.funny-videoclips.de", "", self._defaultlistcenter)

		self['title'] = Label(FVCDE_Version)
		self['ContentTitle'] = Label("Genres")

		self.onLayoutFinish.append(self.mh_initMenu)

	def mh_parseData(self, data):
		entrys = [('', 'Die neuesten Videos')]
		menu = re.search('class="widget-title widgettitle">Lustige Videos</h4>(.*?)</ul>', data, re.S)
		if menu:
			entrys += re.findall('<li.*?href="(.*?)"\s*>(.*?)</a>', menu.group(1))

		return entrys

	def mh_callGenreListScreen(self):
		genreurl = self.mh_baseUrl+self.mh_genreUrl[0]+self.mh_genreUrl[1]
		self.session.open(FVCDE_FilmListeScreen, genreurl, self.mh_genreTitle)

class FVCDE_FilmListeScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, genreLink, genreName):
		self.genreLink = genreLink
		self.genreName = genreName
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions2", "MP_Actions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"upUp" : self.key_repeatedUp,
			"rightUp" : self.key_repeatedUp,
			"leftUp" : self.key_repeatedUp,
			"downUp" : self.key_repeatedUp,
			"upRepeated" : self.keyUpRepeated,
			"downRepeated" : self.keyDownRepeated,
			"rightRepeated" : self.keyRightRepeated,
			"leftRepeated" : self.keyLeftRepeated,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"1" : self.key_1,
			"3" : self.key_3,
			"4" : self.key_4,
			"6" : self.key_6,
			"7" : self.key_7,
			"9" : self.key_9,
			"0"	: self.closeAll
		}, -1)

		self.sortOrder = 0
		self.baseUrl = "http://www.funny-videoclips.de"
		self.genreTitle = ""
		self.sortParIMDB = ""
		self.sortParAZ = ""
		self.sortOrderStrAZ = ""
		self.sortOrderStrIMDB = ""
		self.sortOrderStrGenre = ""
		self['title'] = Label(FVCDE_Version)

		self['Page'] = Label(_("Page:"))

		self.filmQ = Queue.Queue(0)
		self.hanQ = Queue.Queue(0)
		self.picQ = Queue.Queue(0)
		self.updateP = 0
		self.eventL = threading.Event()
		self.eventP = threading.Event()
		self.keyLocked = True
		self.dokusListe = []
		self.page = 0
		self.pages = 0;
		self.newVids = 'Die neuesten Videos' in self.genreName

		self.setGenreStrTitle()

		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def setGenreStrTitle(self):
		genreName = "%s%s" % (self.genreTitle,self.genreName)
		self['ContentTitle'].setText(genreName)

	def loadPage(self):
		if self.page > 1:
			url = "%s/page/%d/" % (self.genreLink, self.page)
		else:
			url = self.genreLink

		if self.page:
			self['page'].setText("%d / %d" % (self.page,self.pages))

		self.filmQ.put(url)
		if not self.eventL.is_set():
			self.eventL.set()
			self.loadPageQueued()

	def loadPageQueued(self):
		self['name'].setText(_('Please wait...'))
		while not self.filmQ.empty():
			url = self.filmQ.get_nowait()
		twAgentGetPage(url).addCallback(self.loadPageData).addErrback(self.dataError)

	def dataError(self, error):
		self.eventL.clear()
		printl(error,self,"E")
		self.dokusListe.append((_("No videos found!"),"","",""))
		self.ml.setList(map(self._defaultlistleft, self.dokusListe))

	def loadPageData(self, data):
		self.dokusListe = []
		a = 0
		l = len(data)
		while a < l:
			if self.newVids:
				m = re.search('<article class="post-(.*?)</div></div>', data[a:], re.S)
				if m:
					a += m.end()
					d = re.search('<img.*?src="(.*?)".*?class="entry-header.*?href="(.*?)">(.*?)</a', m.group(1), re.S)
					if d:
						t = re.search('<p>(.*?)</p>', m.group(1))
						if t:
							desc = stripAllTags(decodeHtml(t.group(1))).strip()
						else:
							desc = None
						self.dokusListe.append((decodeHtml(d.group(3)), d.group(2), d.group(1), desc))
				else:
					break
			else:
				m = re.search('<article class="post-(.*?)</div></div>', data[a:], re.S)
				if m:
					a += m.end()
					d = re.search('class="entry-header.*?href="(.*?)"\srel="bookmark">(.*?)</a.*?<img\ssrc="(.*?)"', m.group(1), re.S)
					if d:
						t = re.search('class="entry-content".*?/>(.*?)</p>', m.group(1), re.S)
						if t:
							desc = stripAllTags(decodeHtml(t.group(1))).strip()
						else:
							desc = None
						self.dokusListe.append((decodeHtml(d.group(2)), d.group(1), d.group(3), desc))
				else:
					break

		if self.dokusListe:
			if not self.page:
				pages = 0
				try:
					m = re.search('pagination"><ul>(.*?)</ul></div>', data, re.S)
					for p in re.finditer('">(\w+)</', m.group(1)):
						page = int(p.group(1))
						if page > pages: pages = page
					self.pages = pages
					self.page = 1
				except:
					pass
				else:
					self['page'].setText("%d / %d" % (self.page,self.pages))

			self.ml.setList(map(self._defaultlistleft, self.dokusListe))
			self.th_ThumbsQuery(self.dokusListe, 0, 1, 2, None, None, self.page, self.pages, mode=1)
			self.loadPicQueued()
		else:
			self.dokusListe.append((_("No videos found!"),"","",""))
			self.ml.setList(map(self._defaultlistleft, self.dokusListe))
			if self.filmQ.empty():
				self.eventL.clear()
			else:
				self.loadPageQueued()

	def loadPic(self):

		if self.picQ.empty():
			self.eventP.clear()
			return

		if self.updateP:
			return

		while not self.picQ.empty():
			self.picQ.get_nowait()

		streamName = self['liste'].getCurrent()[0][0]
		self['name'].setText(streamName)
		streamPic = self['liste'].getCurrent()[0][2]
		desc = self['liste'].getCurrent()[0][3]
		self.getHandlung(desc)
		self.updateP = 1
		CoverHelper(self['coverArt'], self.ShowCoverFileExit).getCover(streamPic)

	def getHandlung(self, desc):
		if desc == None:
			self['handlung'].setText(_("No further information available!"))
			return
		self.setHandlung(desc)

	def setHandlung(self, data):
		self['handlung'].setText(decodeHtml(data))

	def ShowCoverFileExit(self):
		self.updateP = 0;
		self.keyLocked	= False
		if not self.filmQ.empty():
			self.loadPageQueued()
		else:
			self.eventL.clear()
			self.loadPic()

	def loadPicQueued(self):
		self.picQ.put(None)
		if not self.eventP.is_set():
			self.eventP.set()
		self.loadPic()

	def keyOK(self):
		if (self.keyLocked|self.eventL.is_set()):
			return
		self.session.open(
			FVCDEPlayer,
			self.dokusListe,
			playIdx = self['liste'].getSelectedIndex()
			)

	def keyUpRepeated(self):
		if self.keyLocked:
			return
		self['liste'].up()

	def keyDownRepeated(self):
		if self.keyLocked:
			return
		self['liste'].down()

	def key_repeatedUp(self):
		if self.keyLocked:
			return
		self.loadPicQueued()

	def keyLeftRepeated(self):
		if self.keyLocked:
			return
		self['liste'].pageUp()

	def keyRightRepeated(self):
		if self.keyLocked:
			return
		self['liste'].pageDown()

	def keyPageDown(self):
		self.keyPageDownFast(1)

	def keyPageUp(self):
		self.keyPageUpFast(1)

	def keyPageUpFast(self,step):
		if self.keyLocked:
			return
		oldpage = self.page
		if (self.page + step) <= self.pages:
			self.page += step
		else:
			self.page = 1
		if oldpage != self.page:
			self.loadPage()

	def keyPageDownFast(self,step):
		if self.keyLocked:
			return
		oldpage = self.page
		if (self.page - step) >= 1:
			self.page -= step
		else:
			self.page = self.pages
		if oldpage != self.page:
			self.loadPage()

	def key_1(self):
		self.keyPageDownFast(2)

	def key_4(self):
		self.keyPageDownFast(5)

	def key_7(self):
		self.keyPageDownFast(10)

	def key_3(self):
		self.keyPageUpFast(2)

	def key_6(self):
		self.keyPageUpFast(5)

	def key_9(self):
		self.keyPageUpFast(10)

class FVCDEPlayer(SimplePlayer):

	def __init__(self, session, playList, playIdx):
		SimplePlayer.__init__(self, session, playList, playIdx=playIdx, playAll=True, listTitle="FUNNY-VIDEOCLIPS.DE", ltype='funny-videoclips.de')

	def getVideo(self):
		dhVideoId = self.playList[self.playIdx][1]
		dhTitle = self.playList[self.playIdx][0]
		imgurl =  self.playList[self.playIdx][2]
		if not dhVideoId.startswith('http'):
			YoutubeLink(self.session).getLink(self.playStream, self.ytError, dhTitle, dhVideoId, imgurl=imgurl)
		else:
			getPage(dhVideoId).addCallback(self.parseStream).addErrback(self.dataError)

	def parseStream(self, data):
		m2 = re.search('//www.youtube.com/(embed|v)/(.*?)(\?|" |&amp)', data)
		if m2:
			dhVideoId = m2.group(2)
			dhTitle = self.playList[self.playIdx][0]
			imgurl =  self.playList[self.playIdx][2]
			YoutubeLink(self.session).getLink(self.playStream, self.ytError, dhTitle, dhVideoId, imgurl=imgurl)
		else:
			self.dataError("Kein Videostream gefunden!")

	def ytError(self, error):
		msg = "Title: %s\n%s" % (self.playList[self.playIdx][0], error)
		self.dataError(msg)