# -*- coding: utf-8 -*-
from Components.Pixmap import Pixmap
from Components.GUIComponent import GUIComponent
from Components.config import config

class PixmapExt(Pixmap):

	def execBegin(self):
		GUIComponent.execBegin(self)
		self.instance.setShowHideAnimation(config.mediaportal.animation_coverart.value)