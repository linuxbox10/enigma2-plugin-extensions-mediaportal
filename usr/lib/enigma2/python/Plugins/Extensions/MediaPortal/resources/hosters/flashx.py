# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.packer import unpack, detect
import requests

def flashx(self, data, id):
	s = requests.Session()
	url = "https://www.flashx.tv/embed.php?c="+id

	headers = {'Host': 'www.flashx.tv',
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language': 'en-US,en;q=0.5',
		'Connection': 'keep-alive',
		'Upgrade-Insecure-Requests': '1',
		'Cookie': ''}

	ok = s.get(url, headers=headers)
	link1 = re.findall('(www.flashx.tv/scripts/coders.js\?.*?)"', ok.text)
	link2 = re.findall('(www.flashx.tv/counter.cgi\?c.*?)"', ok.text)
	if link1 and link2:
		link1 = "https://"+str(link1[0])
		link2 = "https://"+str(link2[0])
		okl1 = s.get(link1, headers=headers, allow_redirects=True)
		okl2 = s.get(link2, headers=headers, allow_redirects=True)
		url = "https://www.flashx.tv/playvideo-"+id+".html?playvid"
		ok3 = s.get(url, headers=headers, allow_redirects=True)
		stream = re.findall("src: '(.*?)'", ok3.text)
		if stream:
			print stream
			stream_url = str(stream[-1])
			self._callback(stream_url)
		else:
			self.stream_not_found()