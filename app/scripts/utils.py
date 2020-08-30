#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
from urllib.request import Request
from urllib.request import urlopen
from urllib.error import HTTPError
from time import sleep
import ssl

# Internal imports
from app import db
from app.forms import RegisterNovelForm
from app.forms import EditNovelForm
from app.forms import RemoveNovelForm
from app.models import SeriesTable
from app.models import HostTable
from app.models import Language
from app.scripts import hostmanager
from app.scripts.hostmanager import Host


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
	except Exception as e:
		return None

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
	res = 0
	source_url = host_entry.host_url + series_code
	source_html = fetchHtml(source_url, host_entry.host_lang)
	if source_html is not None:
		html_parser = hostmanager.createManager(host_entry.host_type)
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
		------------------------------------------------------------------
	"""
	# Rip relevant information
	series_code = str(reg_form.series_code.data)
	series_title = str(reg_form.title.data)
	series_abbr = str(reg_form.abbr.data)

	host_entry = HostTable.query.filter_by(host_type=Host(reg_form.series_host.data)).first()

	# Check for preexisting dictionary if this series is being re-registered


	# Finally build the table for the series
	series_entry = SeriesTable(
		code=series_code,
		title=series_title,
		abbr=series_abbr,
		current_ch=0,
		latest_ch=getLatestChapter(series_code, host_entry),
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
						-1 on error
		------------------------------------------------------------------
	"""
	host_entry = HostTable.query.filter_by(id=series_entry.host_id).first()
	latest = getLatestChapter(series_entry.code, host_entry)
	if latest == 0:
		ret = -1
	else:
		ret = latest - series_entry.latest_ch;
		series_entry.latest_ch = latest
		db.session.add(series_entry)
		db.session.commit()

	return ret

def customTrans(series_entry, ch):
	"""-------------------------------------------------------------------
		Function:		[customTrans]
		Description:	Generates the pre-processed data necessary to populate
						the chapter template
		Input:
		  [series_entry]The series db entry to generate the customtrans chapter for
		  [ch]			The integer indicating the chapter number
		Return:
		------------------------------------------------------------------
	"""
	host_entry = HostTable.query.filter_by(id=series_entry.host_id).first()

	# First fetch the html
	host_manager = hostmanager.createManager(host_entry.host_type)
	chapter_url = host_manager.generateChapterUrl(series_entry.code, ch)
	chapter_html = fetchHtml(chapter_url, host_entry.host_lang)
	if chapter_html is None:
		return None

	# Parse out relevant content from the website source code
	chapter_content = host_manager.parseChapterContent(chapter_html)
	chapter_data = {
		"title": 		next(datum for datum in chapter_content if datum['ltype'] == hostmanager.LType.TITLE),
		"prescript": 	[datum for datum in chapter_content if datum['ltype'] == hostmanager.LType.PRESCRIPT],
		"main": 		[datum for datum in chapter_content if datum['ltype'] == hostmanager.LType.MAIN],
		"postscript": 	[datum for datum in chapter_content if datum['ltype'] == hostmanager.LType.POSTSCRIPT]
	}
	return chapter_data