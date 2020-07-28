# -*- coding: utf-8 -*-
#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
from abc import ABC, abstractmethod		# Pythonic abstract inheritance
from enum import Enum 					# Pythonic enumerators
import bs4 as soup 						# Python HTML query tool
import re 								# Regex for personalized parsing HTML


# There are different types of content lines
class LType(Enum):
	TITLE 	 = 0	# Line is the chapter title
	PRE  	 = 1 	# Lines just before the story content
	REG  	 = 2 	# Just a regular text story line
	POST 	 = 3	# Right after the story content, author's afterword
	REG_IMG  = 4 	# Image embedded in the story content section
	POST_IMG = 5	# Image embedded in afterword section

# Enum for the hosts
class Host(Enum):
	Syosetu = 0
	Biquyun = 1
	Shu69 	= 2

def createManager(host):
	"""-------------------------------------------------------------------
		Function:		[createManager]
		Description:	Given a host name, creates and returns the
						appropriate HostManager
		Input:
		  [host]		Host enum
		Return:			Concrete HostManager-derived object
		-------------------------------------------------------------------
	"""
	if host == Host.Syosetu:
		return SyosetuManager()
	elif host == Host.Biquyun:
		return BiquyunManager()
	elif host == Host.Shu69:
		return Shu69Manager()

	return None

#==========================================================================
#	[HostManager]
#	Generic abstract super class requiring children to implement a
#	parseTitle and parseContent method. All host managers MUST inherit from
# 	this class.
#==========================================================================
class HostManager(ABC):
	def __init__(self, base_url, host_type):
		self.base_url = base_url
		self.host_type = host_type

	# Accessor methods
	def getBaseUrl():
		return self.base_url

	def getHostType():
		return self.host_type

	"""-------------------------------------------------------------------
		Function:		[parseTitle]
		Description:	Parses the title from the HTML source code
		Input:
		  [html]		The HTML source code in string form	for a given chap
		Return:			The string representing the chapter title
		-------------------------------------------------------------------
	"""
	@abstractmethod
	def parseTitle(self, html):	pass

	"""-------------------------------------------------------------------
		Function:		[parseContent]
		Description:	Parses the chapter content from the HTML source code
		Input:
		  [html]		The HTML source code in string form	for a given chap
		Return:			A list constisting of each line of content from the
						chapter in the form (LType, line)
		-------------------------------------------------------------------
	"""
	@abstractmethod
	def parseContent(self, html): pass

	"""-------------------------------------------------------------------
		Function:		[parsePageTableFromWeb]
		Description:	Parses out codes corresponding to all chapters in the
						given HTML table of contents from the series index
						webpage
		Input:
		  [html]		The HTML source code in string form	of the table of
		  				contents for a given series
		Return:			A list where the string at index i represents the url
						chapter code of the (i+1)th chapter of this series

		Note: 	Not required by all managers. Only if chapters of the series
				have chapter codes in the URL that DOES NOT monotonically
				increment by 1 from one chapter to the next
		-------------------------------------------------------------------
	"""
	@abstractmethod
	def parsePageTableFromWeb(self, html): pass

	"""-------------------------------------------------------------------
		Function:		[generateChapterUrl]
		Description:	Generates the url to access chapter ch of the given
						series from the host website this
						manager object represents
		Input:
		  [series_code] The series code
		  [ch] 			The integer chapter to download
		Return:			The url to access chapter ch of the given series
		-------------------------------------------------------------------
	"""
	@abstractmethod
	def generateChapterUrl(self, series_code, ch): pass

	"""-------------------------------------------------------------------
		Function:		[getLatestChapter]
		Description:	Retrieves the latest chapter number for the given series
		Input:
		  [html]		The base table of contents html for a given series
		Return:			A list constisting of each line of content from the
						chapter
		-------------------------------------------------------------------
	"""
	@abstractmethod
	def getLatestChapter(self, html): pass

#==========================================================================
#	[SyosetuManager]
#	HostManager specialized for parsing html chapters taken from the
#	https://ncode.syosetu.com domain
#==========================================================================
class SyosetuManager(HostManager):
	def __init__(self):
		# Page table not needed for Syosetu domain
		super(SyosetuManager, self).__init__(
			"https://ncode.syosetu.com/",
			Host.Syosetu)

	def parseTitle(self, html):
		title = re.findall(r'<p class="novel_subtitle">(.*?)</p>', html)
		return title[0]

	def parseContent(self, html):
		content = []
		# Filter out <ruby> tags that mess up translation
		html = re.sub(r'<ruby>(.*?)<rb>(.*?)</rb>(.*?)</ruby>', r'\2', html)
		html_soup = soup.BeautifulSoup(html, 'lxml')

		def processAndAppendLine(ltype, l):
			# Turn break tags into new lines
			if re.fullmatch(r'\s*<br\s*/>\s*', l):
				content.append((ltype, '\n'))
			# Skip blanks
			elif re.fullmatch(r'\s*', l):
				return
			else:
				content.append((ltype, l))
			content.append((ltype, '\n'))

		# Get prescript content if it exists
		prescript = html_soup.find('div', {'class': 'novel_view', 'id': 'novel_p'})
		if prescript is not None:
			for p in prescript.find_all('p', recursive=False):
				processAndAppendLine(LType.PRE, p.getText())

		# Get main content
		main = html_soup.find('div', {'class': 'novel_view', 'id': 'novel_honbun'})
		if main is not None:
			for p in main.find_all('p', recursive=False):
				images = p.find_all('img')
				if len(images) > 0:
					for img in images:
						content.append((LType.REG_IMG, "https:" + img['src']))
				else:
					processAndAppendLine(LType.REG, p.getText())
		else:
			print("[Error] Main content section not found in html...")
			sys.exit(1)

		# Get afterword content if it exists
		afterword = html_soup.find('div', {'class': 'novel_view', 'id': 'novel_a'})
		if afterword is not None:
			for p in afterword.find_all('p', recursive=False):
				images = p.find_all('img')
				if len(images) > 0:
					for img in images:
						content.append((LType.POST_IMG, "https:" + img['src']))
				else:
					processAndAppendLine(LType.POST, p.getText())

		return content

	# Syosetu domain has chapter codes corresponding to the chapter number
	#   https://ncode.syosetu.com/<ncode>/1 = Chapter 1
	#   https://ncode.syosetu.com/<ncode>/2 = Chapter 2
	#   ...
	# So page table is trivial
	def parsePageTableFromWeb(self, html):
		return range(1, self.getLatestChapter(html)+1)

	def generateChapterUrl(self, series_code, ch):
		return self.base_url + series_code + "/" + str(ch)

	def getLatestChapter(self, html):
		pattern = re.compile(r"<dl class=\"novel_sublist2\">")
		latest = len(pattern.findall(html))
		return latest

#==========================================================================
#	[BiquyunManager]
#	HostManager specialized for parsing html chapters taken from the
#	https://www.biquyun.com/ domain
#==========================================================================
class BiquyunManager(HostManager):
	def __init__(self):
		# Page table needed for Biquyun domain
		super(BiquyunManager, self).__init__(
			"https://www.biquyun.com/",
			Host.Biquyun)

	def parseTitle(self, html):
		title = re.findall(r'<div class="bookname">\r\n\t\t\t\t\t<h1>(.*?)\
			</h1>', html)
		return title[0]

	def parseContent(self, html):
		content = []

		# Parse lines and make them readable before adding them to content
		lines = re.findall(r'&nbsp;&nbsp;&nbsp;&nbsp;(.*?)<', html)
		for line in lines:
			content.append((LType.REG, line))
			content.append((LType.REG, u'\n'))

		return content

	# Erratic chapter codes, so page table needed
	def parsePageTableFromWeb(self, html):
		# Note: this parsing scheme may be outdated for the Biquyun domain
		page_table = re.findall(r'<a href="/.*?/(.*?)\.html">', html)
		return page_table

	def generateChapterUrl(self, series_code, ch):
		return self.base_url + series_code + "/" + parsePageTableFromWeb()[ch-1]

	def getLatestChapter(self, html):
		return len(self.parsePageTableFromWeb(html))

#==========================================================================
#	[Shu69Manager]
#	HostManager specialized for parsing html chapters taken from the
#	https://www.69shu.org/book/ domain
#==========================================================================
class Shu69Manager(HostManager):
	def __init__(self):
		# Page table needed for Biquyun domain
		super(Shu69Manager, self).__init__(
			"https://www.69shu.org/book/",
			Host.Shu69)

	def parseTitle(self, html):
		html_soup = soup.BeautifulSoup(html, 'lxml')
		title_div = html_soup.find('div', {'class': 'h1title'})
		title = title_div.h1.string if title_div.h1 is not None else "NOTITLE"
		return title

	def parseContent(self, html):
		content = []

		# Parse lines and make them readable before adding them to content
		lines = re.findall(r'&nbsp;&nbsp;&nbsp;&nbsp;(.*?)<', html)
		for line in lines:
			content.append((LType.REG, line))
			content.append((LType.REG, u'\n'))

		return content

	# Erratic chapter codes, so page table needed
	def parsePageTableFromWeb(self, html):
		page_table = []

		html_soup = soup.BeautifulSoup(html, 'lxml')
		ch_list = html_soup.find('ul', {'class': 'chapterlist'})
		for ch_elem in ch_list.find_all('li', {'class': ''}):
			if ch_elem.a is not None:
				ch_html = ch_elem.a.get('href')
				page_table.append(ch_html)

		return page_table

	def generateChapterUrl(self, series_code, ch):
		return self.base_url + series_code + "/" + parsePageTableFromWeb()[ch-1]

	def getLatestChapter(self, html):
		return len(self.parsePageTableFromWeb(html))