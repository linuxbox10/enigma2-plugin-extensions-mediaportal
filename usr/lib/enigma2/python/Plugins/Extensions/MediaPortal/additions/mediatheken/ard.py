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
from Plugins.Extensions.MediaPortal.resources.keyboardext import VirtualKeyBoardExt

# Globals
suchCache = ""
dm = "dummy"
mainLink = "http://www.ardmediathek.de"
tDef = "Keine Informationen/Angaben"
isWeg = "Nicht (oder nicht mehr) auf den ARD-Servern vorhanden!"
placeHolder = ("---","99")
ardPic = "file://%s/ard.png" % (config.mediaportal.iconcachepath.value + "logos")

class ARDGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

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
		self['title'] = Label("ARD Mediathek")
		self['ContentTitle'] = Label("Auswahl des Genres")

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.genreliste = []
		self.genreliste.append(("Suche  -  TV", "1"))
		self.genreliste.append(("A bis Z  -  TV", "2"))
		self.genreliste.append(("Sendung verpasst!?  -  TV", "3"))
		self.genreliste.append(("Kategorien  -  TV", "4"))
		self.genreliste.append(("Tagesschau  -  TV", "11"))
		self.genreliste.append(placeHolder)
		self.genreliste.append(("Suche  -  Radio", "6"))
		self.genreliste.append(("A bis Z  -  Radio", "7"))
		self.genreliste.append(("Kategorien  -  Radio", "8"))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False
		CoverHelper(self['coverArt']).getCover(ardPic)

	def keyOK(self):
		if self.keyLocked:
			return
		self.gN = self['liste'].getCurrent()[0][0]
		self.gF = self['liste'].getCurrent()[0][1]
		if self.gF == "99":
			return
		elif self.gF == "1" or self.gF == "6": # Suche TV oder Radio
			self.session.openWithCallback(self.searchCallback, VirtualKeyBoardExt, title = (_(self.gN)), text = suchCache, is_dialog=True)
		else:
			self.session.open(ARDPreSelect,self.gN,self.gF)

	def searchCallback(self, callbackStr):
		self.gF = self['liste'].getCurrent()[0][1]
		if callbackStr is not None:
			global suchCache
			suchCache = callbackStr
			self.searchStr = callbackStr
			self.gN = "Suche... ' %s '" % self.searchStr
			self.searchStr = self.searchStr.replace(' ', '+')
			self.searchStr = self.searchStr.replace('ä', '%C3%A4')	#	Umlaute URI-konform wandeln, sonst Fehler zB. beim Suchen nach "Börse".
			self.searchStr = self.searchStr.replace('ö', '%C3%B6')
			self.searchStr = self.searchStr.replace('ü', '%C3%BC')
			self.searchStr = self.searchStr.replace('Ä', '%C3%84')
			self.searchStr = self.searchStr.replace('Ö', '%C3%96')
			self.searchStr = self.searchStr.replace('Ü', '%C3%9C')
			self.searchStr = self.searchStr.replace('ß', '%C3%9F')
			if self.gF == "1":
				url = mainLink+"/suche?searchText="+self.searchStr+"&source=tv&sort="	#	Hier kein "%s" verwenden! Fehler, wenn "%" in URI landet!
			elif self.gF == "6":
				url = mainLink+"/suche?searchText="+self.searchStr+"&source=radio&sort="
			self.session.open(ARDStreamScreen,url,self.gN,self.gF)

class ARDPreSelect(MPScreen):

	def __init__(self,session,genreName,genreFlag):
		self.gN = genreName
		self.gF = genreFlag
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

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
		self['title'] = Label("ARD Mediathek")
		self['ContentTitle'] = Label("Auswahl des Genres")

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		if self.gF == "2" or self.gF == "7":
			self['name'].setText(self.gN+"\nAuswahl des Buchstabens")
			self.genreliste = []
			for c in xrange(26): # ABC, Radio & TV
				self.genreliste.append((chr(ord('A') + c), None))
			self.genreliste.insert(0, ('0-9', None))
		elif self.gF == "4" or self.gF == "8":
			self.genreliste = []
			if self.gF == "4": # Extra-Kategorien, Radio & TV
				self['name'].setText(self.gN+"\nAuswahl der Kategorie")
				self.genreliste.append(("TOP von Seite 1 - TV", "1"))
				self.genreliste.append(("Neueste Videos", "2"))
				self.genreliste.append(("Am besten bewertete Videos", "3"))
				self.genreliste.append(("Meistabgerufene Videos", "4"))
				self.genreliste.append(("Ausgewählte Filme", "5"))
				self.genreliste.append(("Ausgewählte Dokus", "6"))
				self.genreliste.append(placeHolder)
				self.genreliste.append(("Kinder & Familie", "7"))
				self.genreliste.append(('"Must see" - was die Redaktion schaut', "8"))
				self.genreliste.append(("Kurzes für Zwischendurch", "9"))
				self.genreliste.append(("Unterhaltung & Comedy", "10"))
				self.genreliste.append(("Wissen", "11"))
				self.genreliste.append(("Politik", "12"))
				self.genreliste.append(("Kultur", "13"))
				self.genreliste.append(("Ratgeber", "14"))
				self.genreliste.append(("Sport", "15"))
				self.genreliste.append(("Sportreportagen", "16"))
				self.genreliste.append(("Reise", "17"))
				self.genreliste.append(("Alle Filme", "18"))
				self.genreliste.append(("Alle Dokus & Reportagen", "19"))
			if self.gF == "8": # Extra-Kategorien, nur Radio
				self['name'].setText(self.gN+"\nAuswahl der Kategorie")
				self.genreliste.append(("Neueste Clips", "1"))
				self.genreliste.append(("Meistabgerufene Clips", "2"))
				self.genreliste.append(placeHolder)
				self.genreliste.append(("Tipps der Redaktion", "3"))
				self.genreliste.append(("Hörspiel", "4"))
		elif self.gF == "3":	# Sendung verpasst?
			self['name'].setText("Sendung verpasst!?\nAuswahl des Kalendertages")
			for q in range (0, 7):
				s2 = (datetime.date.today()+datetime.timedelta(days=-q)).strftime("%A %d. %B %Y")
				s3 = str(q)
				self.genreliste.append((s2,s3,dm,dm))
		elif self.gF == "11":
			self.genreliste = []
			self['name'].setText(self.gN+"\nAuswahl der Kategorie")
			self.genreliste.append(("Tagesschau", "1"))
			self.genreliste.append(("Tagesschau mit Gebärdensprache", "2"))
			self.genreliste.append(("Tagesthemen", "3"))
			self.genreliste.append(("Tagesschau24", "4"))

		self.keyLocked = False
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		CoverHelper(self['coverArt']).getCover(ardPic)

	def keyOK(self):
		if self.keyLocked:
			return
		auswahl = self['liste'].getCurrent()[0][0]
		extra = self['liste'].getCurrent()[0][1]
		if extra == "99":
			return
		elif self.gF == "3":
			self.session.open(ARDPreSelectSender,auswahl,self.gF,extra,dm)
		elif self.gF == "4":	# Kategorien TV
			if extra == '1': # TOP von Seite 1 - TV
				streamLink = "%s/tv" % mainLink
			elif extra == '2': # Neueste Videos
				streamLink = "%s/tv/Neueste-Videos/mehr?documentId=21282466" % mainLink
			elif extra == '3': # Am besten bewertete Videos
				streamLink = "%s/tv/Am-besten-bewertet/mehr?documentId=21282468" % mainLink
			elif extra == '4': # Meistabgerufene Videos
				streamLink = "%s/tv/Meistabgerufene-Videos/mehr?documentId=23644244" % mainLink
			elif extra == '5': # Ausgewählte Filme
				streamLink = "%s/tv/Ausgewählte-Filme/mehr?documentId=33649088" % mainLink
			elif extra == '6': # Ausgewählte Dokus
				streamLink = "%s/tv/Ausgewählte-Dokus/mehr?documentId=33649086" % mainLink
			elif extra == '7': # Kinder & Familie
				streamLink = "%s/tv/Kinder-Familie/mehr?documentId=21282542" % mainLink
			elif extra == '8': # "Must see" - was die Redaktion schaut
				streamLink = "%s/tv/mustsee" % mainLink
			elif extra == '9': # Kurzes für Zwischendurch
				streamLink = "%s/tv/Kurzes-für-Zwischendurch/mehr?documentId=45458112" % mainLink
			elif extra == '10': # Unterhaltung & Comedy
				streamLink = "%s/tv/unterhaltung" % mainLink
			elif extra == '11': # Wissen
				streamLink = "%s/tv/wissen" % mainLink
			elif extra == '12': # Politik
				streamLink = "%s/tv/politik" % mainLink
			elif extra == '13': # Kultur
				streamLink = "%s/tv/kultur" % mainLink
			elif extra == '14': # Ratgeber
				streamLink = "%s/tv/ratgeber" % mainLink
			elif extra == '15': # Sport
				streamLink = "%s/tv/sport" % mainLink
			elif extra == '16': # Sportreportagen
				streamLink = "%s/tv/Sportreportagen-dokus/Tipps?documentId=30366344" % mainLink
			elif extra == '17': # Reise
				streamLink = "%s/tv/reise" % mainLink
			elif extra == '18': # Alle Filme
				streamLink = "%s/tv/Alle-Filme/mehr?documentId=31610076" % mainLink
			elif extra == '19': # Alle Dokus & Reportagen
				streamLink = "%s/tv/Alle-Dokus-und-Reportagen/mehr?documentId=29897594" % mainLink
			self.session.open(ARDStreamScreen,streamLink,auswahl,self.gF)
		elif self.gF == "8": # Kategorien Radio
			if extra == '1': # Neueste Clips
				streamLink = "%s/radio/Neueste-Audios/mehr?documentId=21282450" % mainLink
			elif extra == '2': # Meistabgerufene Clips
				streamLink = "%s/radio/Meistabgerufene-Audios/mehr?documentId=21282452" % mainLink
			elif extra == '3': # Tipps der Redaktion
				streamLink = "%s/radio/Tipps-der-Redaktion/mehr?documentId=21301892" % mainLink
			elif extra == '4': # Hörspiel
				streamLink = "%s/radio/Hörspiele/mehr?documentId=21301890" % mainLink
			self.session.open(ARDStreamScreen,streamLink,auswahl,self.gF)
		elif self.gF == "11": # Tagesschau
			if extra == '1': # Tagesschau
				streamLink = "%s/tv/Tagesschau/Sendung?documentId=4326&bcastId=4326" % mainLink
			elif extra == '2': # Tagesschau mit Gebärdensprache
				streamLink = mainLink+"/tv/Tagesschau-mit-Geb%C3%A4rdensprache/Sendung?documentId=12722002&bcastId=12722002"
			elif extra == '3': # Tagesthemen
				streamLink = "%s/tv/Tagesthemen/Sendung?documentId=3914&bcastId=3914" % mainLink
			elif extra == '4': # Tagesschau24
				streamLink = "%s/tv/tagesschau24/Sendung?documentId=6753968&bcastId=6753968" % mainLink
			self.session.open(ARDStreamScreen,streamLink,auswahl,self.gF)
		else:
			if self.gF == "2" or self.gF == "7": # ABC (TV oder Radio)
				self.gN = auswahl
			else:
				self.gN = auswahl
				auswahl = extra
			self.session.open(ARDPostSelect,auswahl,self.gN,self.gF)

class ARDPreSelectSender(MPScreen):

	def __init__(self,session,genreName,genreFlag,sender,such):
		self.gN = genreName
		self.gF = genreFlag
		self.sender = sender
		self.such = such
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

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
		self['title'] = Label("ARD Mediathek")
		self['ContentTitle'] = Label("Auswahl des Genres")

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.genreliste = []
		if self.gF == "3":	# Sendung verpasst!?
			self['name'].setText("Sendung verpasst!?\nAuswahl des Senders")
			self.genreliste.append(("Das Erste", "208"))
			self.genreliste.append(("BR", "2224"))
			self.genreliste.append(("HR", "5884"))
			self.genreliste.append(("MDR", "5882"))
			self.genreliste.append(("MDR Thüringen", "1386988"))
			self.genreliste.append(("MDR Sachsen-Anhalt", "1386898"))
			self.genreliste.append(("MDR Sachsen", "1386804"))
			self.genreliste.append(("NDR", "5906"))
			self.genreliste.append(("RB", "5898"))
			self.genreliste.append(("RBB", "5874"))
			self.genreliste.append(("RBB Brandenburg", "21518356"))
			self.genreliste.append(("RBB Berlin", "21518358"))
			self.genreliste.append(("SR", "5870"))
			self.genreliste.append(("SWR", "5310"))
			self.genreliste.append(("SWR Rheinland-Pfalz", "5872"))
			self.genreliste.append(("SWR Baden-Württemberg", "5904"))
			self.genreliste.append(("WDR", "5902"))
			self.genreliste.append(("tagesschau24", "5878"))
			self.genreliste.append(("ARD alpha", "5868"))
			self.genreliste.append(("ONE", "673348"))
			self.genreliste.append(("KiKA", "5886"))

		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False
		CoverHelper(self['coverArt']).getCover(ardPic)

	def keyOK(self):
		if self.keyLocked:
			return
		auswahl = self['liste'].getCurrent()[0][0]
		extra = self['liste'].getCurrent()[0][1]
		if extra == "99":
			return
		if self.gF == "3":
			url = "%s/tv/sendungVerpasst?tag=%s&kanal=%s" % (mainLink,self.sender,extra)	# "self.sender" kein Tippfehler!
		self.session.open(ARDStreamScreen,url,auswahl,self.gF)

class ARDPostSelect(MPScreen, ThumbsHelper):

	def __init__(self,session,auswahl,genreName,genreFlag):
		self.auswahl = auswahl
		self.gN = genreName
		self.gF = genreFlag
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self.keyLocked = True
		self['title'] = Label("ARD Mediathek")
		self['ContentTitle'] = Label("Auswahl der Inhalte")

		self['Page'] = Label(_("Page:"))
		self.genreliste = []
		self.page = 1
		self.sendungen = ""
		self.lastpage = 1	# Alles hier hat nur 1 Seite
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		if self.gF == "2":	# ABC - TV
			url = "%s/tv/sendungen-a-z?buchstabe=%s&mcontent=page.1" % (mainLink,self.auswahl)
		if self.gF == "7":	# ABC - Radio
			url = "%s/radio/sendungen-a-z?buchstabe=%s&mcontent=page.1" % (mainLink,self.auswahl)
		getPage(url).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		self.genreliste = []
		self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
		self.sendungen = re.findall('<div class="box" .*?textWrapper.*?<a\shref="(.*?)".*?headline">(.*?)<', data, re.S)
		if self.sendungen:
			for (url,title) in self.sendungen:
				url = mainLink+url.replace("&amp;","&")
				if "|" in title:
					title = title.replace("|","-")
				self.genreliste.append((decodeHtml(title),url))
			self.keyLocked = False
		else:
			self.genreliste.append((isWeg,None))
		self.ml.setList(map(self._defaultlistleft, self.genreliste))
		self.th_ThumbsQuery(self.genreliste, 0, 1, None, None, '<meta name="gsaimg512" content="(.*?)"', self.page, self.lastpage, mode=1)
		if self['liste'].getCurrent()[0][0] != isWeg:
			self.showInfos()

	def showInfos(self):
		if self.keyLocked:
			return
		if self.gF != "10":
			url = self['liste'].getCurrent()[0][1]
			if url:
				getPage(url).addCallback(self.handlePicAndTxt).addErrback(self.dataError)

	def handlePicAndTxt(self, data):
		if self.keyLocked:
			return
		handlung = ''
		streamPic = None
		gefunden = re.findall('<meta name="description" content="(.*?)"/.*?<meta name="author" content="(.*?)".*?<meta name="gsaimg512" content="(.*?)"/>.*?<div class="box">.*?textWrapper.*?dachzeile">(.*?)[<|\s]', data, re.S)
		if gefunden:
			for (itxt,sender,streamPic,ausgaben) in gefunden:
				itxttmp = itxt.split("|")
				itxt = itxttmp[-1]
				itxt = decodeHtml(itxt)
				itxt = itxt.lstrip()
				if itxt == "":
					itxt = tDef
				if not ausgaben:
					ausgaben = tDef
				url = self['liste'].getCurrent()[0][1]
				if "/tv/" in url:
					media = "TV"
				elif "/radio/" in url:
					media = "Radio"
				else:
					media = "?"
				handlung = "Media: %s\nGenre: %s\nSender: %s\nClips: %s" % (media,self.gN,sender,ausgaben)
		streamHandlung = handlung+"\n\n"+itxt
		self['handlung'].setText(streamHandlung)
		streamName = self['liste'].getCurrent()[0][0]
		self['name'].setText("Sendung / Thema\n"+streamName)
		if streamPic:
			CoverHelper(self['coverArt']).getCover(streamPic)

	def keyOK(self):
		if self.keyLocked:
			return
		if self['liste'].getCurrent()[0][0] == isWeg:
			self.close()
		streamLink = self['liste'].getCurrent()[0][1]
		if streamLink == None:
			return
		self.session.open(ARDStreamScreen,streamLink,self.gN,self.gF)

class ARDStreamScreen(MPScreen, ThumbsHelper):

	def __init__(self, session,streamLink,genreName,genreFlag):
		self.streamLink = streamLink
		self.gN = genreName
		self.gF = genreFlag
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"yellow" : self.keyYellow,
			"blue" : self.keyBlue,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
			}, -1)

		self.keyLocked = True
		self['title'] = Label("ARD Mediathek")
		if self.gF == "4":
			self['ContentTitle'] = Label("Auswahl des Videos")
		else:
			self['ContentTitle'] = Label("Auswahl des Clips")
		self['name'] = Label(_("Please wait..."))
		if self.gF == "1" or self.gF == "6":
			self['F3'] = Label("Relevanz")
		else:
			self['F4'] = Label("Mehr...")

		self['Page'] = Label(_("Page:"))
		self.future = 0
		self.page = 1
		self.lastpage = 1
		self.suchTrigger = "date"
		self.blueTrigger = 0
		self.blueURL = ""
		self.blueMemory = [0,0,0]
		self.blueIdx = 0
		self.folgen = ""
		self.filmliste = []
		self.sendung = ""
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		if self.blueTrigger == 0:
			if self.gF == "1" or self.gF =="6":	# Suche
				url = self.streamLink+self.suchTrigger+"&mresults=page."+str(self.page)	# Kein "%s" hier verwenden!! Gewandelte Umlaute aus searchCallBack enthalten "%"!
			elif self.gF == "4" or self.gF == "8":	# Kategorien
				url = "%s&mcontent=page.%s" % (self.streamLink,self.page)
			elif self.gF == "3":
				url = self.streamLink
			else:
				url = "%s&mcontents=page.%s" % (self.streamLink,self.page)

			if self.gN == "TOP von Seite 1 - TV":
				url = self.streamLink
			elif self.gN == '"Must see" - was die Redaktion schaut':
				url = "%s?m37862988=page.%s" % (self.streamLink,self.page)
			elif self.gN == 'Unterhaltung & Comedy':
				url = "%s?m39803570=page.%s" % (self.streamLink,self.page)
			elif self.gN == 'Wissen':
				url = "%s?m39348662=page.%s" % (self.streamLink,self.page)
			elif self.gN == 'Politik':
				url = "%s?m39593042=page.%s" % (self.streamLink,self.page)
			elif self.gN == 'Kultur':
				url = "%s?m39594746=page.%s" % (self.streamLink,self.page)
			elif self.gN == 'Reise':
				url = "%s?m39618186=page.%s" % (self.streamLink,self.page)
			elif self.gN == 'Ratgeber':
				url = "%s?m39712440=page.%s" % (self.streamLink,self.page)
			elif self.gN == 'Sport':
				url = "%s?m30348620=page.%s" % (self.streamLink,self.page)
			elif self.gN == 'Sportreportagen':
				url = "%s&m27307124=page.%s" % (self.streamLink,self.page)
		else:	# Zweiter Durchlauf, wenn "Mehr.." gedrückt wurde (StreamLink wird zur StreamLink-Liste)
			self['F4'].setText("Zurück")
			self.blueMemory[0] = self.page
			self.page = 1
			url = self.blueURL+"&mpage=page.moreclips"
		getPage(url).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		if self.gN == "Sport":
			data = re.search('(.*?)Ausgewählte Dokus', data, re.S).group(1)
		self.filmliste = []
		if self.blueTrigger == 0:
			if self.page == 1:	# Gleich bei Seite 1 die maximale Seite merken. Danach nicht nochmal berechnen
				if "Loader-source" in data:
					try:
						max = re.findall('Loader-source.*?<a.*?>\s+(.*?)\s+</a>', data, re.S)[-2]	# Der vorletzte Treffer ist die letzte Seite
					except IndexError:	#	Gab kein [-2]
						max = "x"
					max = filter(lambda x: x.isdigit(), max)	#	Ziffer enthalten?
					if max == "":	# Keine Ziffer gefunden
						self.lastpage = 1
					else:
						self.lastpage = int(max)
				else: # Kein "Loader-source"; ergo: Gibt nur eine Seite
					self.lastpage = 1
		else:	#	"Mehr..."
			self.blueMemory[1] = self.lastpage
			self.lastpage = 1
		self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))

		if self.blueTrigger == 1:
			self.blueIdx = 0
		else:
			self.blueIdx = self.blueMemory[2]
			self.blueMemory[2] = 0
		if (self.gF == "4" and self.gN == "TOP von Seite 1 - TV"): # TOP von Seite 1
			if self.blueTrigger == 0:
				self.folgen = re.findall('ModStageMediaPanel.*?textWrapper.*?href="(.*?)" class="textLink">.*?headline">(.*?)</', data, re.S)
			else:	#	"Mehr..." im 2. Durchlauf
				self.folgen = re.findall('<div class="teaser" data-ctrl-.*?textWrapper.*?href="(.*?)" class="textLink">.*?headline">(.*?)</', data, re.S)
		elif self.gF == "11":	#	Tagesschau/themen
			self.folgen = re.findall('data-ctrl-contentsoptionalLayouter-entry.*?textWrapper.*?href="(.*?)" class="textLink">.*?headline">(.*?)</', data, re.S)
		else:
			self.folgen = re.findall('<div class="teaser" data-ctrl-.*?textWrapper.*?href="(.*?)" class="textLink">.*?headline">(.*?)</', data, re.S)
		if self.folgen:
			for (url,title) in self.folgen:
				if not "Livestream" in url and not "http:" in url and "bcastId" in url:
					url = mainLink+url.replace("&amp;","&")
					sub = re.search('documentId=(.*?)($|&)', url, re.S)
					if sub:
						iD = sub.group(1)
						self.filmliste.append((decodeHtml(title),url,iD))
						self.ml.setList(map(self._defaultlistleft, self.filmliste))
						self.ml.moveToIndex(self.blueIdx)
			self.keyLocked = False
		else:
			self.filmliste.append((isWeg, None, None, None))
			self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.th_ThumbsQuery(self.filmliste, 0, 1, None, None, '<meta name="gsaimg512" content="(.*?)"', self.page,self.lastpage, mode=1)
		if self['liste'].getCurrent()[0][0] != isWeg:
			self.showInfos()

	def showInfos(self):
		if self.keyLocked:
			return
		self['name'].setText('')
		self.blueURL = self['liste'].getCurrent()[0][1]
		if self.blueURL:
			getPage(self.blueURL).addCallback(self.handlePicAndTxt).addErrback(self.dataError)

	def handlePicAndTxt(self, data):
		if self.keyLocked:
			return
		handlung = ''
		streamPic = None
		self.future = 0
		if not "dcterms.date" in data:
			self.future = 1
			ergebnis = re.findall('<meta name="description" content="(.*?)"/>.*?author" content="(.*?)"/.*?<meta name="gsaimg512" content="(.*?)"/>.*?dcterms.title" content="(.*?)"/>.*?og:site_name" content="(.*?)"/>.*?<p class="subtitle">(.*?)</', data, re.S)
		if "dcterms.isPartOf" in data and self.future == 0:
			ergebnis = re.findall('<meta name="description" content="(.*?)"/>.*?author" content="(.*?)"/.*?<meta name="gsaimg512" content="(.*?)"/>.*?dcterms.isPartOf" content="(.*?)"/>.*?dcterms.date" content="(.*?)"/>.*?<p class="subtitle">(.*?)</', data, re.S)
		else:
			if self.future == 0:
				ergebnis = re.findall('<meta name="description" content="(.*?)"/>.*?author" content="(.*?)"/.*?<meta name="gsaimg512" content="(.*?)"/>.*?dcterms.title" content="(.*?)"/>.*?dcterms.date" content="(.*?)"/>.*?<p class="subtitle">(.*?)</', data, re.S)
		if ergebnis:
			for (itxt,sender,streamPic,sendung,uhr,meta) in ergebnis:
				self.sendung = sendung
				if not itxt or len(itxt) == 0:
					itxt = tDef
				else:
					title = self['liste'].getCurrent()[0][0]
					if title in itxt:
						itxttmp = itxt.split(title+":")
						itxt = itxttmp[-1].lstrip()
						itxt = decodeHtml(itxt)
						if itxt == "":
							itxt = tDef
					else:
						itxt = decodeHtml(itxt)
				if "ARD" in uhr:	#	Fakeeintrag um Absturz zu verhindern
					uhr = " - Liegt in der Zukunft!"
				else:
					uhr = uhr.split("T")
					uhr = uhr[-1]
					uhr = ", "+uhr[:5]+" Uhr"
				meta = meta.split(" | ")
				airtime = meta[0]
				dur = meta[1]
			url = self['liste'].getCurrent()[0][1]
			handlung = "Genre: %s\nSender: %s\nClip-Datum: %s%s\nDauer: %s" % (self.gN,sender,airtime,uhr,dur)
		streamHandlung = handlung+"\n\n"+itxt
		self['handlung'].setText(streamHandlung)
		streamName = self['liste'].getCurrent()[0][0]
		self['name'].setText("Sendung / Thema\n"+decodeHtml(self.sendung))
		if streamPic:
			CoverHelper(self['coverArt']).getCover(streamPic)

	def keyYellow(self):
		if self.keyLocked:
			return
		if self.gF == "1" or self.gF =="6":
			if self.suchTrigger == "date":
				self['F3'].setText("Datum")
				self.suchTrigger = "score"
			elif self.suchTrigger == "score":
				self['F3'].setText("Relevanz")
				self.suchTrigger = "date"
		else:
			return
		self.loadPage()

	def keyBlue(self):
		if self.keyLocked:
			return
		if self.blueTrigger == 0:
			self.blueMemory[2] = self['liste'].getSelectedIndex()
			self.blueTrigger = 1
		elif self.blueTrigger == 1:
			self['F4'].setText("Mehr...")
			self.page = self.blueMemory[0]
			self.lastpage = self.blueMemory[1]
			self.blueTrigger = 0
		self.loadPage()

	def keyOK(self):
		if self.keyLocked:
			return
		self.streamName = self['liste'].getCurrent()[0][0]
		if self.streamName == isWeg:
			self.close()
		self['name'].setText(_("Please wait..."))
		url = self['liste'].getCurrent()[0][1]
		if url == None:
			streamName = self['liste'].getCurrent()[0][0]
			self['name'].setText(streamName)
			return
		else:
			getPage(url).addCallback(self.get_Link).addErrback(self.dataError)

	def get_Link(self, data):
		fsk = re.search('<div class="box fsk.*?"teasertext">\s+(.*?)\s+</p>', data, re.S)
		if fsk:
			message = self.session.open(MessageBoxExt, _(fsk.group(1)), MessageBoxExt.TYPE_INFO, timeout=7)
			streamName = self['liste'].getCurrent()[0][0]
			self['name'].setText(streamName)
			return
		else:
			mediaid = self['liste'].getCurrent()[0][2]
			url = mainLink+"/play/media/"+mediaid+"?devicetype=tablet&features=flash"
			getPage(url).addCallback(self.getStreams).addErrback(self.dataError)

	def getStreams(self, data):
		q = 0
		h = 0
		stream = ""
		qualitycheck = re.findall('"_quality":(.*?),.*?_width":(.*?),"_height":(.*?),"_stream":"(.*?)"', data, re.S)
		if qualitycheck:
			for (quality,width,height,url) in qualitycheck:
				if int(quality) >= q:
					q = int(quality)
					if int(height) > h:
						h = int(height)
						stream = url
		else:
			qualitycheck = re.findall('"_quality":(.*?),.*?_stream":"(.*?)"', data, re.S)
			if qualitycheck:
				stream = qualitycheck[-1][1]
		if stream.startswith('//'):
			stream = 'http:' + stream
		if stream != "":
			streamName = self['liste'].getCurrent()[0][0]
			self['name'].setText(streamName)
			self.session.open(SimplePlayer, [(self.streamName, stream)], showPlaylist=False, ltype='ard')