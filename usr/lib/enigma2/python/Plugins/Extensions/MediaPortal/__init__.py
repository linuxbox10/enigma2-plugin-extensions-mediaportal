﻿# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
	lang = language.getLanguage()[:2]
	os_environ["LANGUAGE"] = lang
	gettext.bindtextdomain("MediaPortal", resolveFilename(SCOPE_PLUGINS, "Extensions/MediaPortal/locale"))

def _(txt):
	t = gettext.dgettext("MediaPortal", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)