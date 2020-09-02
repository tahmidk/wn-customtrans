#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
import os
import io
import ssl
import re

from urllib.request import Request
from urllib.request import urlopen
from urllib.error import HTTPError

# Flask imports
from flask import url_for

# Internal imports
from app import db

from app.forms import RegisterNovelForm
from app.forms import EditNovelForm
from app.forms import RemoveNovelForm

from app.models import *

from app.scripts.hostmanager import *
from app.scripts.custom_errors import *
from app.scripts.dictionary import *



def fetchHtml(url, lang):
	"""-------------------------------------------------------------------
		Function:		[fetchHtml]
		Description:	Tries to prompt a response url and return the received
						HTML content as a UTF-8 decoded string
		Input:
		  [url]			The url to make the request to
		  [lang]		The page's language (Language Enum)
		Return: 		The HTML content of the given website address
		------------------------------------------------------------------
	"""
	try:
		headers = { 'User-Agent' : 'Mozilla/5.0' }
		request = Request(url, None, headers)
		response = urlopen(request, context=ssl._create_unverified_context())
	except:
		raise HtmlFetchException(url)

	# Read and decode the response according to series language
	source = response.read()
	if lang == Language.JP:
		data = source.decode('utf8')
	elif lang == Language.CN:
		data = source.decode('gbk')

	return data

def getLatestChapter(series_code, host_entry):
	"""-------------------------------------------------------------------
		Function:		[getLatestChapter]
		Description:	Fetches the latest chapter directly from the series's host
		Input:
		  [series_code]	The identifying series code
		  [host_entry] 	The HostTable entry associated with this series
		Return:			Latest chapter number
		------------------------------------------------------------------
	"""
	source_url = host_entry.host_url + series_code
	source_html = fetchHtml(source_url, host_entry.host_lang)
	html_parser = createManager(host_entry.host_type)
	res = html_parser.getLatestChapter(source_html)

	return res

def registerSeriesToDatabase(reg_form):
	"""-------------------------------------------------------------------
		Function:		[registerSeriesToDatabase]
		Description:	Pushes user series info to database initializing
						the associated dictionary as well
		Input:
		  [reg_form] 	The Flask novel registration form to process
		Return:			The new series as a db Table entry
						None if error encountered
		------------------------------------------------------------------
	"""
	# Rip relevant information
	series_title = str(reg_form.title.data)
	series_abbr = str(reg_form.abbr.data)
	series_code = str(reg_form.series_code.data)

	host_entry = HostTable.query.filter_by(host_type=Host(reg_form.series_host.data)).first()
	dict_fname = generateDictFilename(series_abbr, host_entry.host_name, series_code)
	dict_entry = None

	# Check for preexisting dictionary if this series is being re-registered
	for entry in DictionaryTable.query.all():
		dict_info = spliceDictName(entry.fname)
		if dict_info is not None:
			(_, host, code) = dict_info
			if host == host_entry.host_name and code == series_code:
				dict_entry = entry
				if dict_entry.fname != dict_fname:
					renameDictFile(dict_entry.fname, dict_fname)
					dict_entry.fname = dict_fname
				break

	# If an existing dictionary is not found, make a new entry
	if dict_entry is None:
		dict_entry = DictionaryTable(
			fname=dict_fname,
		)
	db.session.add(dict_entry)
	db.session.commit()

	# Check the physical file,
	dict_dir = url_for('user', filename='dicts')[1:]
	dict_path = url_for('dict', filename=dict_fname)[1:]
	if not os.path.exists(dict_path):
		# First traverse the dict files to see if there is a dict file with the same host-code combination
		# This implies the user has registered and removed this series before with the preserve dictionary
		# option enabled and is currently trying to reregister that same series
		dict_initialized = False
		for dict_file in os.listdir(dict_dir):
			if os.path.isfile(os.path.join(dict_dir, dict_file)):
				info = spliceDictName(dict_file)
				if info is not None:
					(_, host, code) = info
					if host == host_entry.host_name and code == series_code:
						# Found a dict file with matching host+code, rename it and use it for this series dict
						renameDictFile(dict_file, dict_fname)
						updateDictMetaHeader(dict_fname, series_title, series_abbr)
						dict_initialized = True
						break

		# Dict with this host+code combination wasn't found, create a new one from scratch
		if not dict_initialized:
			host_manager = createManager(host_entry.host_type)
			createDictFile(dict_fname, series_title, series_abbr, host_manager.generateSeriesUrl(series_code))

	# If the dict exists but is empty, repopulate it with the dictionary skeleton text
	if os.path.getsize(dict_path) == 0:
		host_manager = createManager(host_entry.host_type)
		createDictFile(dict_fname, series_title, series_abbr, host_manager.generateSeriesUrl(series_code))

	# Finally build the table for the series
	series_entry = SeriesTable(
		code=series_code,
		title=series_title,
		abbr=series_abbr,
		current_ch=0,
		latest_ch=getLatestChapter(series_code, host_entry),
		bookmarks=[],
		dict_id=dict_entry.id,
		host_id=host_entry.id,
	)
	db.session.add(series_entry)
	db.session.commit()

	return series_entry

def updateSeries(series_entry):
	"""-------------------------------------------------------------------
		Function:		[updateSeries]
		Description:	Updates a specific series
		Input:
		  [reg_form] 	The Flask novel registration form to process
		Return:			Number of chapter updates on success
		------------------------------------------------------------------
	"""
	host_entry = HostTable.query.filter_by(id=series_entry.host_id).first()
	latest = getLatestChapter(series_entry.code, host_entry)
	ret = latest - series_entry.latest_ch;
	series_entry.latest_ch = latest
	db.session.add(series_entry)
	db.session.commit()

	return ret

def applyDictionaryToContent(content, series_dict):
	"""-------------------------------------------------------------------
		Function:		[applyDictionaryToContent]
		Description:	Applies the
		Input:
		  [series_abbr] The abbreviation of the series
		  [content]		Formatted chapter content gotten from hostmanager
		Return:
		------------------------------------------------------------------
	"""
	# Helper function that generates a placeholder element with the given id
	def generatePlaceholder(id):
		return "<span class=\"placeholder\" id=\"p%d\">placeholder</span>" % id

	# Preprocess line using dictionary entities
	series_dict_list = list(series_dict.items())
	for i in range(0, len(content)):
		if content[i]["type"] == "text":
			for j in range(0, len(series_dict)):
				(def_raw, (def_trans, def_comment)) = series_dict_list[j]
				if def_raw in content[i]["text"]:
					content[i]["text"] = content[i]["text"].replace(def_raw, generatePlaceholder(j+1))

def customTrans(series_entry, ch):
	"""-------------------------------------------------------------------
		Function:		[customTrans]
		Description:	Generates the pre-processed data necessary to populate
						the chapter template
		Input:
		  [series_entry]The series db entry to generate the customtrans chapter for
		  [ch]			The integer indicating the chapter number
		Return: 		Returns a tuple consisting of the chapter data and
						the series dictionary structure
		------------------------------------------------------------------
	"""
	host_entry = HostTable.query.filter_by(id=series_entry.host_id).first()

	# First fetch the html
	host_manager = createManager(host_entry.host_type)
	chapter_url = host_manager.generateChapterUrl(series_entry.code, ch)
	chapter_html = fetchHtml(chapter_url, host_entry.host_lang)

	# Parse out relevant content from the website source code
	chapter_content = host_manager.parseChapterContent(chapter_html)
	series_dict = initSeriesDict(series_entry.abbr)
	applyDictionaryToContent(chapter_content, series_dict)

	# Done, pack all the data together and return it to the client
	chapter_data = {
		"title": 		next(datum for datum in chapter_content if datum['ltype'] == LType.TITLE),
		"prescript": 	[datum for datum in chapter_content if datum['ltype'] == LType.PRESCRIPT],
		"main": 		[datum for datum in chapter_content if datum['ltype'] == LType.MAIN],
		"postscript": 	[datum for datum in chapter_content if datum['ltype'] == LType.POSTSCRIPT],
		"dictionary":	[{"trans":t, "comment":c} for (_, (t, c)) in series_dict.items()]
	}
	return chapter_data