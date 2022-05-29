# -*- coding: utf-8 -*-
#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
import re 								# Regex for personalized parsing HTML
import requests 						# HTTP request library
import pykakasi as pkk 					# Python Japanese romanization api
import bs4 as soup 						# Python HTML query tool
import datetime as dt 					# Date time format for chapter timestamps

from abc import ABC, abstractmethod		# Pythonic abstract inheritance
from enum import Enum					# Pythonic enumerators

# Internal imports
from app import app


# Describes the section where a line or image should appear
class LType(Enum):
	TITLE 	 	= 0	# Line is the chapter title
	PRESCRIPT 	= 1 # Lines just before the story content
	MAIN  	 	= 2 # Main content text
	POSTSCRIPT 	= 3 # Right after the story content, author's afterword

# Enum for the hosts
class Host(Enum):
	Syosetu  = 0
	Kakuyomu = 1

	@staticmethod
	def to_string(host):
		if host == Host.Syosetu:
			return "Host.Syosetu"
		if host == Host.Kakuyomu:
			return "Host.Kakuyomu"
		else:
			raise ValueError

	@staticmethod
	def to_enum(label):
		if label in ('Host.Syosetu', 0):
			return Host.Syosetu
		if label in ('Host.Kakuyomu', 1):
			return Host.Kakuyomu
		else:
			raise ValueError

# Language enumeration
class Language(Enum):
	JP = 1
	CN = 2

	@staticmethod
	def to_string(lang):
		if lang == Language.JP:
			return "Language.JP"
		elif lang == Language.CN:
			return "Language.CN"
		else:
			raise ValueError

	@staticmethod
	def to_enum(label):
		if label in ('Language.JP', 1):
			return Language.JP
		elif label in ('Language.CN', 2):
			return Language.CN
		else:
			raise ValueError

	@staticmethod
	def get_lang_code(lang):
		if lang == Language.JP:
			return "ja"
		elif lang == Language.CN:
			return "zh"
		else:
			raise ValueError



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
	elif host == Host.Kakuyomu:
		return KakuyomuManager()

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
			"type": 	"text",
			"seq": 		self.__seqnum,
			"line_id": 	self.__linenum,
			"ltype": 	ltype,
			"text":		line,
			"raw": 		line,
			"subtext": 	self.generateRomanization(line),
			"gt_link": 	self.generateGoogleTranslateLink(line)
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
			"type":		"image",
			"seq":		self.__seqnum,
			"img_id":	self.__imgnum,
			"ltype":	ltype,
			"img_src":	img['src']
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
		# Romanization only applies to Japanese
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
		lang_code = Language.get_lang_code(self.host_lang)
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
	def generateSeriesUrl(self, series_code):
		return f"{self.domain}/{series_code}"

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
	def generateChapterUrl(self, series_code, ch, page_table=None):
		return f"{self.generateSeriesUrl(series_code)}/{str(ch)}"

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
	def parsePageTableFromWeb(self, html):
		return [ch+1 for ch in range(self.getLatestChapter(html))]

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
	def getLatestChapter(self, html):
		pass

	"""-------------------------------------------------------------------
		Function:		[getVolumesData]
		Description:	Retrieves all volume/chapter information for the given series
		Input:
		  [html]		The base table of contents html for a given series
		Return:			A list constisting of all volumes data fit for a database
						entry under VolumeTable
		-------------------------------------------------------------------
	"""
	@abstractmethod
	def getVolumesData(self, html):
		pass


#==========================================================================
#	[SyosetuManager]
#	HostManager specialized for parsing and processing html chapters taken
# 	from the https://ncode.syosetu.com domain
#==========================================================================
class SyosetuManager(HostManager):
	def __init__(self):
		# Page table not needed for Syosetu domain
		super(SyosetuManager, self).__init__(
			"https://ncode.syosetu.com", Host.Syosetu, Language.JP)

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
						line = p.getText().strip()
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

	def getLatestChapter(self, html):
		html_soup = soup.BeautifulSoup(html, 'lxml')
		latest = len(html_soup.select(".novel_sublist2"))
		return latest

	def getVolumesData(self, html):
		volumes = list()
		html_soup = soup.BeautifulSoup(html, 'lxml')

		volume = dict()
		chapter_index = 1
		volume_index = 0
		volume["num"] = volume_index
		volume["title"] = "Volume %d" % volume_index
		volume["chapters"] = list()

		toc_container = html_soup.find('div', {'class': 'index_box'})
		for child_elem in toc_container.find_all(recursive=False):
			# Check if this element is a volume header
			if child_elem.has_attr('class') and "chapter_title" in child_elem["class"]:
				# Close off the current volume (if it's not empty) and start a new volume
				if len(volume["chapters"]) > 0:
					volumes.append(volume)

				volume = dict()
				volume_index += 1
				volume["num"] = volume_index
				volume["title"] = child_elem.text
				volume["chapters"] = list()
			else:
				# Otherwise, this element is a chapter div
				chapter_title_elem = child_elem.find('dd', {'class': 'subtitle'})
				chapter_title = chapter_title_elem.find('a').text
				date_posted_elem = child_elem.find('dt', {'class': 'long_update'})
				date_posted = date_posted_elem.text[1:17]
				volume["chapters"].append({
					"number": chapter_index,
					"title": chapter_title,
					"date_posted": dt.datetime.strptime(date_posted, "%Y/%m/%d %H:%M"),
				})
				chapter_index += 1

		if len(volume["chapters"]) > 0:
			volumes.append(volume)

		return volumes



#==========================================================================
#	[KakuyomuManager]
#	HostManager specialized for parsing and processing html chapters taken
# 	from the https://kakuyomu.jp domain
#==========================================================================
class KakuyomuManager(HostManager):
	def __init__(self):
		# Page table not needed for Kakuyomu domain
		super(KakuyomuManager, self).__init__(
			"https://kakuyomu.jp", Host.Kakuyomu, Language.JP)

	def parseChapterContent(self, html):
		super(KakuyomuManager, self).parseChapterContent(html)

		content = []
		# Filter out <ruby> tags that mess up translation
		html = re.sub(r'<ruby>(.*?)<rb>(.*?)</rb>(.*?)</ruby>', r'\2', html)
		html_soup = soup.BeautifulSoup(html, 'lxml')

		# Handle the title
		title = html_soup.select_one("p.widget-episodeTitle").text
		content.append(self.generateLineData(LType.TITLE, title))

		# Fetch the main section content
		main = html_soup.select_one("div.widget-episodeBody")
		if main is not None:
			for p in main.find_all('p', recursive=False):
				line = p.getText().strip()
				content.append(self.generateLineData(LType.MAIN, line))

		return content

	# Erratic chapter codes, so page table needed
	def parsePageTableFromWeb(self, series_code):
		# Fetch the HTML of the table of contents
		url = self.generateSeriesUrl(series_code)
		try:
			cookies = { 'over18': 'yes' }
			headers = { 'User-Agent': 'Mozilla/5.0' }
			response = requests.get(url,
				cookies=cookies,
				headers=headers,
				verify=False)

			if not response.status_code == 200:
				raise Exception

			toc_html = response.text
		except:
			raise HtmlFetchException(url)

		# Generate the page table
		page_table = []
		html_soup = soup.BeautifulSoup(toc_html, 'lxml')
		for ch in html_soup.select('a.widget-toc-episode-episodeTitle'):
			ch_link = ch.get('href')
			ch_code_match = re.search(r"episodes\/(\d+)", ch_link)
			page_table.append(ch_code_match.group(1) if ch_code_match else "")

		return page_table

	def generateSeriesUrl(self, series_code):
		return f"{self.domain}/works/{series_code}"

	def generateChapterUrl(self, series_code, ch, page_table=None):
		chapter = page_table[ch-1] if page_table != None else ch
		return f"{self.generateSeriesUrl(series_code)}/episodes/{chapter}"

	def getLatestChapter(self, html):
		html_soup = soup.BeautifulSoup(html, 'lxml')
		latest = len(html_soup.select(".widget-toc-episode"))
		return latest

	def getVolumesData(self, html):
		volumes = list()
		html_soup = soup.BeautifulSoup(html, 'lxml')

		volume = dict()
		chapter_index = 1
		volume_index = 0
		volume["num"] = volume_index
		volume["title"] = "Volume %d" % volume_index
		volume["chapters"] = list()

		toc_container = html_soup.find('ol', {'class': 'widget-toc-items'})
		for child_elem in toc_container.find_all(recursive=False):
			# Check if this element is a volume header
			if child_elem.has_attr('class') and "widget-toc-chapter" in child_elem["class"]:
				# Close off the current volume (if it's not empty) and start a new volume
				if len(volume["chapters"]) > 0:
					volumes.append(volume)

				volume = dict()
				volume_index += 1
				volume["num"] = volume_index
				volume["title"] = child_elem.select_one("span").text
				volume["chapters"] = list()
			else:
				# Otherwise, this element is a chapter div
				chapter_title_elem = child_elem.find('span', {'class': 'widget-toc-episode-titleLabel'})
				chapter_title = chapter_title_elem.text
				date_posted_elem = child_elem.find('time', {'class': 'widget-toc-episode-datePublished'})
				date_posted = date_posted_elem.get("datetime")
				volume["chapters"].append({
					"number": chapter_index,
					"title": chapter_title,
					"date_posted": dt.datetime.strptime(date_posted, "%Y-%m-%dT%H:%M:%SZ")
				})
				chapter_index += 1

		if len(volume["chapters"]) > 0:
			volumes.append(volume)

		return volumes