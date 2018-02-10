# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.messageboxext import MessageBoxExt
import requests

def openloadApi(self, data, id):
	session = requests.session()
	t = session.get('https://api.openload.co/1/file/dlticket', params={'file': id, 'login': 'c255c81fad52a08f', 'key': 'lc7xiQ46'})
	ticket = re.findall('"ticket":"(.*?)"', t.text)
	if ticket:
		ticket = str(ticket[0])
		ok = session.get('https://api.openload.co/1/file/dl', params={'file': id, 'ticket': ticket})
		stream = re.findall('url":"(.*?)"', ok.text)
		if stream:
			stream_url = str(stream[0].replace('\\',''))
			self._callback(stream_url)
		else:
			self.stream_not_found()
	elif re.search('IP address not authorized', data):
		message = self.session.open(MessageBoxExt, _("IP address not authorized. Visit https://openload.co/pair"), MessageBoxExt.TYPE_ERROR)
	else:
		stream_url = re.findall('"url":"(.*?)"', data)
		if stream_url:
			self._callback(stream_url[0].replace('\\',''))
		else:
			self.stream_not_found()