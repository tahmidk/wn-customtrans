# -*- coding: utf-8 -*-
#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
import re
import io
import os
import errno
from collections import OrderedDict

# Flask imports
from flask import flash
from flask import url_for

# Internal imports
from app import db

from app.models import SeriesTable
from app.models import DictionaryTable
from app.models import HostTable

from app.scripts.custom_errors import *
from app.scripts.hostmanager import Language
from app.scripts import hostmanager


# Some global constants
COMMON_DICT_FNAME = "common_dict.dict"
DICT_NAME_DIVIDER = r'|'
DICT_DEF_DIVIDER = r'-->'

def spliceDictName(dict_fname):
	"""-------------------------------------------------------------------
		Function:		[spliceDictName]
		Description:	Extracts data from a given dictionary (.dict) filename
		Input:
		  [dict_fname] 	Dictionary filename of the form <Series>_<Host>_<Code>.dict
		Return:			A 3-tuple in the form (Series, Host, Code)
						None if dict_fname is misformatted
		------------------------------------------------------------------
	"""
	dict_pattern = re.compile(r"(\w+)_(.+)_(.+)\.dict")
	match = dict_pattern.fullmatch(dict_fname)
	if match is not None:
		return (match[1], match[2], match[3])

	return None

def generateDictFilename(series_abbr, host_name, series_code):
	"""-------------------------------------------------------------------
		Function:		[generateDictFilename]
		Description:	Systematically generates a filename for a dictionary file
						given the host name, series abbreviation and code
		Input:
		  [series_abbr]	Series abbreviation
		  [host_name]	Name of the series host
		  [series_code]	Series code
		Return:			String representing the name of the dictionary file
						associated with the given series attributes
		------------------------------------------------------------------
	"""
	fname = "%s_%s_%s.dict" % (series_abbr, host_name, series_code)
	return fname

def createDictFile(dict_fname, series_title, series_abbr, series_link):
	"""-------------------------------------------------------------------
		Function:		[createDictFile]
		Description:	Creates and initializes a new dict file
		Input:
		  [dict_fname]	 Dictionary file path
		  [series_title] Series title
		  [series_abbr]	 Series abbreviation
		  [series_link]	 Link to the raws of this series
		Return:			None, renames physical file if it exists
		------------------------------------------------------------------
	"""
	dict_path = url_for('dict', filename=dict_fname)[1:]
	try:
		with io.open(dict_path, mode='w', encoding='utf8') as dict_file:
			dict_file.write("// series_title :  %s\n" % series_title)
			dict_file.write("// series_abbr  :  %s\n" % series_abbr)
			dict_file.write("// series_link  :  %s\n" % series_link)
			dict_file.write("\n\n//=============================[ Names ]==================================")
			dict_file.write(u'\n@name{{ナルト{0}うずまき, Naruto{0}Uzumaki}}\t\t// Main character of a popular manga'.format(DICT_NAME_DIVIDER))
			dict_file.write("\n\n//=============================[ Places ]=================================")
			dict_file.write("\n\n//=============================[ Skills ]=================================")
			dict_file.write("\n\n//============================[ Monsters ]================================")
			dict_file.write("\n\n//===========================[ Terminology ]==============================")
			dict_file.write(u'\n九尾の狐 %s Nine Tailed Fox' % DICT_DEF_DIVIDER)
			dict_file.write("\n\n//==============================[ Misc ]==================================")
			dict_file.write("\n\n// END OF FILE")
	except OSError as err:
		if err.errno == errno.EEXIST:
			# If renamed file already exists, ignore
			return
	except Exception as err:
		# OS error creating the file
		raise DictFileCreationException(dict_path)

def removeDictFile(dict_fname):
	dict_path = url_for('dict', filename=dict_fname)[1:]
	try:
		os.remove(dict_path)
	except Exception as err:
		raise DictFileDeletionException(dict_path)

def renameDictFile(old_dict_fname, new_dict_fname):
	"""-------------------------------------------------------------------
		Function:		[renameDictFile]
		Description:	Attempts to rename a dict file. If the old_path is invalid
						or DNE, a new dict with
		Input:
		  [old_dict_fname]	Name of the old dictionary file
		  [new_dict_fname] 	Name of the new dictionary file
		Return:			None, renames physical file if it exists
		------------------------------------------------------------------
	"""
	old_path = url_for('dict', filename=old_dict_fname)[1:]
	new_path = url_for('dict', filename=new_dict_fname)[1:]
	if os.path.exists(old_path):
		try:
			os.rename(old_path, new_path)
		except Exception as err:
			# OS error renaming the file
			raise DictFileRenameException(old_path)

def updateDictMetaHeader(dict_fname, new_title, new_abbr):
	"""-------------------------------------------------------------------
		Function:		[updateDictMetaHeader]
		Description:	Attempts to update metadata info usually found at the
						beginning of a standard dict file
		Input:
		  [new_title]	The new series title
		  [new_abbr] 	The new series abbreviation
		Return:			None, renames physical file if it exists
		------------------------------------------------------------------
	"""
	dict_path = url_for('dict', filename=dict_fname)[1:]
	try:
		with io.open(dict_path, mode='r+', encoding='utf8') as dict_file:
			contents = dict_file.readlines()
			contents[0] = re.sub(r'//\s*series_title\s*:\s*(\w+)', r'// series_title :  {0}'.format(new_title), contents[0])
			contents[1] = re.sub(r'//\s*series_abbr\s*:\s*(\w+)',  r'// series_abbr  :  {0}'.format(new_abbr), contents[1])
			dict_file.seek(0)
			dict_file.writelines(contents)
	except Exception as err:
		# Failed to rewrite metadata, but this isn't fatal
		return

def generateNameVariants(raws, trans, lang):
	return None

def processDictFile(dict_fname, series_lang):
	"""-------------------------------------------------------------------
		Function:		[processDictFile]
		Description:	Processes and splices the given dictionary file and
						builds an unordered list of 2-tuples
		Input:
		  [dict_path]	Dictionary file to process
		  [series_lang]	Series language
		Return:			Produces of list of 2-tuples in the form:
						(raw, (translation, comment))
		------------------------------------------------------------------
	"""
	dict_path = url_for('dict', filename=dict_fname)[1:]
	dict_list = []

	try:
		with io.open(dict_path, mode='r', encoding='utf8') as dict_file:
			name_pattern = re.compile(r"\s*@name\{(.+), (.+)\}.*")
			for line in dict_file:
				line = line.strip()
				line = line[:-1]	# Ignore newline '\n' at the end of the line

				# Skip comment lines and unformatted/misformatted lines
				name_match = name_pattern.fullmatch(line)
				if line[0:2] == "//" or len(line) == 0 or line.isspace():
					continue
				elif name_match is not None:
					# Process name tagged lines: '@name{name_raw, name_trans}', '@name{first_name_raw|last_name_raw, first_name_trans|last_name_trans}', etc...
					raw_component = name_match[1].strip().split(DICT_NAME_DIVIDER)
					trans_component = name_match[2].strip().split(DICT_NAME_DIVIDER)
					variants = generateNameVariants(
						raw_component,
						trans_component,
						series_lang)

					if variants is not None:
						for variant in variants:
							dict_list.append(variant)
				else:
					# Process single definition lines: 'X_raw --> X_trans // comment'
					if DICT_DEF_DIVIDER not in line:
						# This line is either misformatted or not a definition, skip
						continue

					divider_split = [entry.strip() for entry in line.split(DICT_DEF_DIVIDER)]
					if len(divider_split) != 2:
						# Misformatted definition along divider, skip
						continue

					raw_component = divider_split[0]
					trans_component = divider_split[1]
					if len(raw_component) == 0 or len(trans_component) == 0:
						# Empty definition on either side of the definition divider, skip
						continue

					# Split the translation component via // to seperate translation from comment
					trans_comment_split = [entry.strip() for entry in trans_component.split("//")]

					raw = raw_component
					translation = trans_comment_split[0]
					comment = None
					if len(trans_comment_split) > 1 and len(trans_comment_split[1]) > 0:
						# Non empty comment detected
						comment = trans_comment_split[1]
					dict_list.append( (raw, (translation, comment)) )
	except Exception as err:
		raise DictFileReadException(dict_path)

	return dict_list

def initSeriesDict(series_abbr):
	"""-------------------------------------------------------------------
		Function:		[initSeriesDict]
		Description:	Initializes the complete dictionary for the given series
						and orders it by length of <raw>
		Input:
		  [series_abbr]	The abbreviation of the series to init dict for
		Return:			OrderedDict in the form: dict[raw] = (trans, comment)
		------------------------------------------------------------------
	"""
	series_entry = SeriesTable.query.filter_by(abbr=series_abbr).first()
	title = series_entry.title
	abbr = series_entry.abbr
	code = series_entry.code

	dict_entry = DictionaryTable.query.filter_by(id=series_entry.dict_id).first()
	dict_fname = dict_entry.fname

	host_entry = HostTable.query.filter_by(id=series_entry.host_id).first()
	lang = host_entry.host_lang

	dict_path = url_for('dict', filename=dict_entry.fname)[1:]
	if not os.path.exists(dict_path) or os.path.getsize(dict_path) == 0:
		host_manager = hostmanager.createManager(host_entry.host_type)
		createDictFile( dict_fname, title, abbr, host_manager.generateSeriesUrl(code))

	# Parse the mappings into a list
	dict_list = []

	# First add standalone honorifics
	# with io.open(HONORIFICS_PATH, mode='r', encoding='utf8') as hon_file:
	# 	try:
	# 		honorifics = json.loads(hon_file.read())
	# 		for entry in honorifics[config_data.getSeriesLang(series)]:
	# 			if entry['standalone']:
	# 				dict_list.append((entry['h_raw'], entry['h_trans']))
	# 	except:
	# 		print("\n[Error] There seems to be a syntax issue with your "
	# 			+ "honorifics.json... Please correct it and try again")
	# 		sys.exit(1)

	# Process common_dict
	try:
		dict_list.extend(processDictFile(COMMON_DICT_FNAME, lang))
	except CustomException as err:
		flash(str(err), err.severity)

	# Process series specific dict
	try:
		dict_list.extend(processDictFile(dict_fname, lang))
	except CustomException as err:
		flash(str(err), err.severity)

	# Initialize the global. Need to sort such that longer strings are processed
	# before the shorter ones so sort by length of the string
	dict_list.sort(key= lambda x: len(x[0]), reverse=True)
	return OrderedDict(dict_list)