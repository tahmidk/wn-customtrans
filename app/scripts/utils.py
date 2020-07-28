#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
from tempfile import TemporaryFile
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
from app.models import DictionariesTable
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
		html_parser = hostmanager.createParser(host_entry.host_type)
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

	# Check database for preexisting dictionary if this series is being re-registered
	dict_entry = DictionariesTable.query.filter_by(series_code=series_code).first()
	if dict_entry is None:
		# No dict exists, create a new one
		dict_fname = "%s_%s.dict" % (series_abbr, series_code)
		with TemporaryFile(mode='w+', encoding='utf-8') as tmp_dict:
			tmp_dict.write("// Title: %s\n" % series_title)
			tmp_dict.write("// Abbr: %s\n" % series_abbr)
			tmp_dict.write("// Series Link: %s%s\n" % (host_entry.host_url, series_code))
			tmp_dict.write("\n// Example comment (starts w/ \'//\''). Example entries below...")
			tmp_dict.write(u'\n@name{ナルト, Naruto}')
			tmp_dict.write(u'\n@name{うずまき, Uzumaki}')
			tmp_dict.write(u'\n九尾の狐 --> Nine Tailed Fox')
			tmp_dict.write("\n\n// END OF FILE")
			tmp_dict.seek(0)

			dict_entry = DictionariesTable(
				filename=dict_fname,
				series_code=series_code,
				data=tmp_dict.read()
			)
			db.session.add(dict_entry)
			db.session.commit()

	# Finally build the table for the series
	series_entry = SeriesTable(
		code=series_code,
		title=series_title,
		abbr=series_abbr,
		current_ch=0,
		latest_ch=getLatestChapter(series_code, host_entry),
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
	import pdb; pdb.set_trace()
	host_entry = HostTable.query.filter_by(id=series_entry.host_id).first()

	# Write the raw file
	host_manager = hostmanager.createManager(host_entry.host_type)
	url = host_manager.generateChapterUrl(series_entry.code, ch)
	html = fetchHtml(url, host_entry.host_lang)
	if html is None:
		return None

	# Parse out relevant content from the website source code
	title = host_manager.parseTitle(html)
	content = [(hostmanager.LType.TITLE, title)] + host_manager.parseContent(html)

	return None