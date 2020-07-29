# -*- coding: utf-8 -*-
#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
import pykakasi as pkk 					# Python Japanese romanization api
from abc import ABC, abstractmethod		# Pythonic abstract inheritance
from enum import Enum 					# Pythonic enumerators
import bs4 as soup 						# Python HTML query tool
import re 								# Regex for personalized parsing HTML


# Describes the section where a line or image should appear
class LType(Enum):
	TITLE 	 	= 0	# Line is the chapter title
	PRESCRIPT 	= 1 # Lines just before the story content
	MAIN  	 	= 2 # Main content text
	POSTSCRIPT 	= 3 #Right after the story content, author's afterword

# Enum for the hosts
class Host(Enum):
	Syosetu = 0
	Biquyun = 1
	Shu69 	= 2

# Language enumeration
class Language(Enum):
    JP = 1
    CN = 2


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
	def __init__(self, domain, host_type, host_lang):
		self.domain = domain
		self.host_type = host_type
		self.host_lang = host_lang
		# Some private data fields used internally
		self.__seqnum = 1
		self.__linenum = 1
		self.__imgnum = 1

	# Accessor methods for public fields
	def getBaseUrl(self):
		return self.domain

	def getHostType(self):
		return self.host_type

	def getHostLang(self):
		return self.host_lang

	"""-------------------------------------------------------------------
		Function:		[generateLineData]
		Description:	Generates a structured dict containing all the data
						necessary for Flask to recreate this line
		Input:
		  [ltype]		LType describing location of this text
		  [line]		String representing the line content
		Return:			Structured line data
		-------------------------------------------------------------------
	"""
	def generateLineData(self, ltype, line):
		data = {
			"type": "text",
			"seq": self.__seqnum,
			"line_id": self.__linenum,
			"ltype": ltype,
			"text":	line,
			"subtext": self.generateRomanization(line),
			"gt_link": self.generateGoogleTranslateLink(line)
		}
		self.__seqnum += 1
		self.__linenum += 1
		return data

	"""-------------------------------------------------------------------
		Function:		[parseTitle]
		Description:	Generates a structured dict containing all the data
						necessary for Flask to recreate this image
		Input:
		  [ltype]		LType describing location of this img
		  [img] 		The lxml image gotten from bs4
		Return:			The string representing the chapter title
		-------------------------------------------------------------------
	"""
	def generateImgData(self, ltype, img):
		data = {
			"type": "image",
			"seq": self.__seqnum,
			"img_id": self.__imgnum,
			"ltype": ltype,
			"img_src": img['src']
		}
		self.__seqnum += 1
		self.__imgnum += 1
		return data


	"""-------------------------------------------------------------------
		Function:		[generateRomanization]
		Description:	Generate html element for the romanization of the
						provided text (JP only)
		Input:
		  [text]		The source untranslated string to romanize
		Return:			string romanizationof the text
		------------------------------------------------------------------
	"""
	def generateRomanization(self, text):
		# We only romanize Japanese
		if self.host_lang == Language.JP:
			romanizer = pkk.kakasi()
			romanizer.setMode("H","a") 			# Enable Hiragana to ascii
			romanizer.setMode("K","a") 			# Enable Katakana to ascii
			romanizer.setMode("J","a") 			# Enable Japanese to ascii
			romanizer.setMode("r","Hepburn") 	# Use Hepburn Roman table
			romanizer.setMode("s", True) 		# Add spaces
			romanizer.setMode("C", True) 		# Capitalize

			converter = romanizer.getConverter()
			return converter.do(text)

		# Other languages, leave as is
		return text

	"""-------------------------------------------------------------------
		Function:		[generateGoogleTranslateLink]
		Description:	Generates link to google translate the given untranslated
						line to English
		Input:
		  [line]		The source untranslated string to generate the link for
		Return:			a Google Translate url
		------------------------------------------------------------------
	"""
	def generateGoogleTranslateLink(self, line):
		if self.host_lang == Language.JP:
			lang_code = "ja"
		elif self.host_lang == Language.CN:
			lang_code = "zh-CN"

		line = line.replace("\"", "\'")
		link = "https://translate.google.com/?hl=en&tab=TT&authuser=0#view=home&op=translate&sl=%s&tl=en&text=%s" \
			% (lang_code, line)
		return link

	"""-------------------------------------------------------------------
		Function:		[generateSeriesUrl]
		Description:	Generates the url to access the series table of contents
						on the host website this object represents
		Input:
		  [series_code] The series code
		Return:			The url to access chapter ch of the given series
		-------------------------------------------------------------------
	"""
	@abstractmethod
	def generateSeriesUrl(self, series_code): pass

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
		Function:		[parseContent]
		Description:	Parses all chapter content from the HTML source code
		Input:
		  [html]		The HTML source code in string form	for a given chap
		Return:			A list constisting of structured data on a line-by-line
						basis taken from the html
		-------------------------------------------------------------------
	"""
	@abstractmethod
	def parseChapterContent(self, html):
		# Need to reset all sequence numbers
		self.__seqnum = 1
		self.__linenum = 1
		self.__imgnum = 1

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
		-------------------------------------------------------------------
	"""
	@abstractmethod
	def parsePageTableFromWeb(self, html): pass


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
#	HostManager specialized for parsing and processing html chapters taken
# 	from the https://ncode.syosetu.com domain
#==========================================================================
class SyosetuManager(HostManager):
	def __init__(self):
		# Page table not needed for Syosetu domain
		super(SyosetuManager, self).__init__(
			"https://ncode.syosetu.com/",
			Host.Syosetu,
			Language.JP)

	def parseChapterContent(self, html):
		super(SyosetuManager, self).parseChapterContent(html)

		content = []
		# Filter out <ruby> tags that mess up translation
		html = re.sub(r'<ruby>(.*?)<rb>(.*?)</rb>(.*?)</ruby>', r'\2', html)
		html_soup = soup.BeautifulSoup(html, 'lxml')

		# Helper function that helps process a certain section of the chapter
		def processSection(section_div, ltype):
			if section_div is not None:
				for p in section_div.find_all('p', recursive=False):
					images = p.find_all('img')
					if len(images) > 0:
						for img in images:
							content.append(self.generateImgData(ltype, img))
					else:
						# Skip breaks and blanks
						line = p.getText().strip()
						if re.fullmatch(r'\s*<br\s*/>\s*', line) or re.fullmatch(r'\s*', line):
							continue
						content.append(self.generateLineData(ltype, line))

		# Handle the title
		title = re.findall(r'<p class="novel_subtitle">(.*?)</p>', html)[0]
		content.append(self.generateLineData(LType.TITLE, title))

		# Fetch the 3 section contents
		prescript = html_soup.find('div', {'class': 'novel_view', 'id': 'novel_p'})
		main = html_soup.find('div', {'class': 'novel_view', 'id': 'novel_honbun'})
		afterword = html_soup.find('div', {'class': 'novel_view', 'id': 'novel_a'})

		# Process each section in order
		processSection(prescript, LType.PRESCRIPT)
		processSection(main, LType.MAIN)
		processSection(afterword, LType.POSTSCRIPT)

		return content

	# Syosetu domain has chapter codes corresponding to the chapter number
	#   https://ncode.syosetu.com/<ncode>/1 = Chapter 1
	#   https://ncode.syosetu.com/<ncode>/2 = Chapter 2
	#   ...
	# So page table is trivial
	def parsePageTableFromWeb(self, html):
		return range(1, self.getLatestChapter(html)+1)

	def generateSeriesUrl(self, series_code):
		return self.domain + series_code + "/"

	def generateChapterUrl(self, series_code, ch):
		return self.generateSeriesUrl(series_code) + str(ch)

	def getLatestChapter(self, html):
		pattern = re.compile(r"<dl class=\"novel_sublist2\">")
		latest = len(pattern.findall(html))
		return latest



#==========================================================================
#	[BiquyunManager]
#	HostManager specialized for parsing and processing html chapters taken
# 	from the https://www.biquyun.com/ domain
#==========================================================================
class BiquyunManager(HostManager):
	def __init__(self):
		# Page table needed for Biquyun domain
		super(BiquyunManager, self).__init__(
			"https://www.biquyun.com/",
			Host.Biquyun,
			Language.CN)

	def parseTitle(self, html):
		title = re.findall(r'<div class="bookname">\r\n\t\t\t\t\t<h1>(.*?)\
			</h1>', html)
		return title[0]

	def parseChapterContent(self, html):
		super(BiquyunManager, self).parseChapterContent(html)

		content = []

		# Parse lines and make them readable before adding them to content
		lines = re.findall(r'&nbsp;&nbsp;&nbsp;&nbsp;(.*?)<', html)
		for line in lines:
			content.append((LType.MAIN, line))
			content.append((LType.MAIN, u'\n'))

		return content

	# Erratic chapter codes, so page table needed
	def parsePageTableFromWeb(self, html):
		# Note: this parsing scheme may be outdated for the Biquyun domain
		page_table = re.findall(r'<a href="/.*?/(.*?)\.html">', html)
		return page_table

	def generateSeriesUrl(self, series_code):
		return self.domain + series_code + "/"

	def generateChapterUrl(self, series_code, ch):
		return self.generateSeriesUrl(series_code) + parsePageTableFromWeb()[ch-1]

	def getLatestChapter(self, html):
		return len(self.parsePageTableFromWeb(html))



#==========================================================================
#	[Shu69Manager]
#	HostManager specialized for parsing and processing html chapters taken
# 	from the https://www.69shu.org/book/ domain
#==========================================================================
class Shu69Manager(HostManager):
	def __init__(self):
		# Page table needed for Biquyun domain
		super(Shu69Manager, self).__init__(
			"https://www.69shu.org/book/",
			Host.Shu69,
			Language.CN)

	def parseChapterContent(self, html):
		super(Shu69Manager, self).parseChapterContent(html)

		content = []

		html_soup = soup.BeautifulSoup(html, 'lxml')
		title_div = html_soup.find('div', {'class': 'h1title'})
		title = title_div.h1.string if title_div.h1 is not None else "NOTITLE"


		# Parse lines and make them readable before adding them to content
		lines = re.findall(r'&nbsp;&nbsp;&nbsp;&nbsp;(.*?)<', html)
		for line in lines:
			content.append((LType.MAIN, line))
			content.append((LType.MAIN, u'\n'))

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

	def generateSeriesUrl(self, series_code):
		return self.domain + series_code + "/"

	def generateChapterUrl(self, series_code, ch):
		return self.generateSeriesUrl(series_code) + parsePageTableFromWeb()[ch-1]

	def getLatestChapter(self, html):
		return len(self.parsePageTableFromWeb(html))