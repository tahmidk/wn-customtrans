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
import html
import errno
from collections import OrderedDict

# Flask imports
from flask import flash
from flask import url_for

# Internal imports
from app import app
from app import db

from app.models import *

from app.scripts.custom_errors import *
from app.scripts.hostmanager import Language
from app.scripts import hostmanager



#===============================================================
#  Globals
#===============================================================
# Standard name for the common dictionary file
COMMON_DICT_FNAME = "common_dict.dict"
COMMON_DICT_TITLE = "Common Dictionary"
COMMON_DICT_ABBR = "Common"
# Comments can be at most 100 characters
COMMENT_MAX_LEN = 100
# Common tokens used to seperate first and last names in raw chapters
NAME_SEPERATORS = ["", " ", "・", "＝"]
# Syntactic seperator used to seperate first, last names in the @name dictionary syntax
DICT_NAME_DIVIDER = r'|'
# Syntactic seperator used for individual definitions in the dictionary syntac
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
		Return:			None
		------------------------------------------------------------------
	"""
	if not os.path.exists(app.config['DICTIONARIES_PATH']):
		os.makedirs(app.config['DICTIONARIES_PATH'])

	dict_path = os.path.join(app.config['DICTIONARIES_PATH'], dict_fname)
	try:
		with io.open(dict_path, mode='w', encoding='utf8') as dict_file:
			dict_file.write("// series_title :  %s\n" % series_title)
			dict_file.write("// series_abbr  :  %s\n" % series_abbr)
			dict_file.write("// series_link  :  %s\n" % series_link)
			dict_file.write("\n\n//=============================[ Names ]==================================")
			dict_file.write("\n\n//=============================[ Places ]=================================")
			dict_file.write("\n\n//=============================[ Skills ]=================================")
			dict_file.write("\n\n//============================[ Monsters ]================================")
			dict_file.write("\n\n//===========================[ Terminology ]==============================")
			dict_file.write("\n\n//==============================[ Misc ]==================================")
			dict_file.write("%s// END OF FILE" % ('\n'*15))
	except Exception as err:
		# OS error creating the file
		raise DictFileCreationException(dict_fname)

def removeDictFile(dict_fname):
	"""-------------------------------------------------------------------
		Function:		[removeDictFile]
		Description:	Attempts to remove a dict file
		Input:
		  [dict_fname]	Name of the dictionary file to delete
		Return:			True on success, False otherwise
		------------------------------------------------------------------
	"""
	dict_path = os.path.join(app.config['DICTIONARIES_PATH'], dict_fname)
	if os.path.exists(dict_path):
		try:
			os.remove(dict_path)
			return True
		except Exception as err:
			raise DictFileDeletionException(dict_fname)

	return False

def renameDictFile(old_dict_fname, new_dict_fname):
	"""-------------------------------------------------------------------
		Function:		[renameDictFile]
		Description:	Attempts to rename a dict file
		Input:
		  [old_dict_fname]	Name of the old dictionary file
		  [new_dict_fname] 	Name of the new dictionary file
		Return:			True on success, False otherwise
		------------------------------------------------------------------
	"""
	old_path = os.path.join(app.config['DICTIONARIES_PATH'], old_dict_fname)
	new_path = os.path.join(app.config['DICTIONARIES_PATH'], new_dict_fname)
	if os.path.exists(old_path):
		try:
			os.rename(old_path, new_path)
			return True
		except Exception as err:
			# OS error renaming the file
			raise DictFileRenameException(old_dict_fname)

	return False

def saveContentToDict(dict_fname, content):
	"""-------------------------------------------------------------------
		Function:		[saveContentToDict]
		Description:	Attempts to update the contents of the given dict file
						using the contents passed in as the second argument. It
						also creates the file first if it doesn't exist
		Input:
		  [dict_fname]  The name of the dict file to save to
		  [content]		A string representing the content to save
		Return:			True on success, False otherwise
		------------------------------------------------------------------
	"""
	dict_path = os.path.join(app.config['DICTIONARIES_PATH'], dict_fname)
	try:
		with io.open(dict_path, mode='w+', encoding='utf8') as dict_file:
			dict_file.write(content)
		return True
	except Exception as err:
		# Failed to rewrite metadata, but this isn't fatal
		return False

def updateDictMetaHeader(dict_fname, new_title, new_abbr):
	"""-------------------------------------------------------------------
		Function:		[updateDictMetaHeader]
		Description:	Attempts to update metadata info usually found at the
						beginning of a standard dict file
		Input:
		  [dict_fname]  The name of the dict file to update
		  [new_title]	The new series title
		  [new_abbr] 	The new series abbreviation
		Return:			True on success, False otherwise
		------------------------------------------------------------------
	"""
	dict_path = os.path.join(app.config['DICTIONARIES_PATH'], dict_fname)
	try:
		with io.open(dict_path, mode='r+', encoding='utf8') as dict_file:
			contents = dict_file.readlines()
			contents[0] = re.sub(
				r'\s*//\s*series_title\s*:\s*(\w+)',
				r'// series_title :  {0}'.format(new_title), contents[0])
			contents[1] = re.sub(
				r'\s*//\s*series_abbr\s*:\s*(\w+)',
				r'// series_abbr  :  {0}'.format(new_abbr), contents[1])
			dict_file.seek(0)
			dict_file.writelines(contents)

		return True
	except Exception as err:
		# Failed to rewrite metadata, but this isn't fatal
		return False

def generateNameVariants(rn, tn, comment, lang):
	"""-------------------------------------------------------------------
		Function:		[generateNameVariants]
		Description:	Generates all variants of rName --> tName dictionary
						entries using the honorifics indicated in honorifics.json
		Input:
		  [rn]		List consisting of the raw components of the name
		  [tn] 		List consisting of the translated components of the name
		  [comment]	The user comment associated with ALL variants generated by this func
		  [lang] 	Enum.Language representing language of the raw component
		Return:			List of tuples of raw name variants to translated name
						variants in the form (raw_variant, (trans_variant, comment))
						None if definition is invalid
		------------------------------------------------------------------
	"""
	# rn and tn should be one-to-one and equal size
	if len(rn) != len(tn):
		return None

	variants = []
	name_len = len(rn)
	honorifics = HonorificsTable.query.filter_by(
		lang=lang,
		enabled=True )

	# First generate non-honorific individual entries
	# e.g. for @name{X|Y, Naruto|Uzumaki}, generate X --> Naruto and Y --> Uzumaki
	individual_variants = [(rn[i], (tn[i], comment)) for i in range(0, name_len)]

	# Next generate non-honorific combined variants using name seperators commonly found in raw chapters
	# e.g. for @name{X|Y, Naruto|Uzumaki}, generate XY --> Naruto Uzumaki, X Y --> Naruto Uzumaki, etc...
	combined_variants = [(sep.join(rn), (' '.join(tn), comment)) for sep in NAME_SEPERATORS ]

	# Finally generate all honorific variants of this name entry
	honorific_variants = []
	for honorific_entry in honorifics:
		# Extract honorifics data
		h_raw = honorific_entry.raw
		h_trans = honorific_entry.trans

		# Helper function to generate honorific'ed name translations
		def gen_trans(t_name):
			if honorific_entry.affix == HonorificAffix.SUFFIX:
				# Process suffixed honorific translation
				t_processed = ("-" if honorific_entry.opt_with_dash else " ").join([t_name, h_trans])
			else:
				# Process prefixed honorific translation
				t_processed = "%s %s" % (h_trans, t_name)
			return t_processed

		# Process the honorific
		rn_processed = [r_name + h_raw for r_name in rn]
		tn_processed = [gen_trans(t_name) for t_name in tn]
		honorific_variants.extend([(rn_processed[i], (tn_processed[i], comment)) for i in range(0, name_len)])

	all_variants = individual_variants + combined_variants + honorific_variants
	return all_variants

def sanitizeDictEntry(entry):
	"""-------------------------------------------------------------------
		Function:		[sanitizeDictEntry]
		Description:	Sanitizes all components of a dictionary entry and
						returns an html safe version of the entry
		Input:
		  [entry]	Dictionary entry in the form (raw, (translation, comment))
		Return:			Entry with html-sanitized components
		------------------------------------------------------------------
	"""
	(raw, (translation, comment)) = entry
	raw = html.escape(raw)
	translation = html.escape(translation)
	return (raw, (translation, comment))

def processDictFile(dict_fname, series_lang):
	"""-------------------------------------------------------------------
		Function:		[processDictFile]
		Description:	Processes and splices the given dictionary file and
						builds an unordered list of 2-tuples
		Input:
		  [dict_fname]	Dictionary file to process
		  [series_lang]	Series language
		Return:			Produces of list of 2-tuples in the form:
						(raw, (translation, comment))
		------------------------------------------------------------------
	"""
	dict_path = os.path.join(app.config['DICTIONARIES_PATH'], dict_fname)
	dict_list = []

	# Sanity checks
	if not os.path.exists(dict_path):
		raise DictFileDNEOnProcessException(dict_fname)
	if os.path.getsize(dict_path) == 0:
		raise DictFileEmptyOnProcessException(dict_fname)

	# Helper function to flash misformatted lines
	def flashMisformattedLine(line, linenum, reason):
		line = strong("\"%s\"" % line)
		location = mono("[%s:%d]" % (dict_fname, linenum))
		line_0 = line if len(line) < 40 else "%s...\"" % line[:36]
		flash("%s Ignored misformatted line %s at %s... %s" %
			(WARNING_BOLD, line_0, location, reason), "warning")

	# Helper function to validate name tags
	def processNameTag(r, t, c):
		# Validity check: the raw component should be one-to-one with the translation component
		if len(r) != len(t):
			reason = "Misbalanced name tag (left:%d, right:%d)" % (len(r), len(t))
			return (False, reason)

		# Validity check: No empty strings in the components
		if '' in r or '' in t:
			reason = "Cannot have empty entries within a name tag"
			return (False, reason)

		# Generate and append name variants to the dict
		variants = generateNameVariants(r, t, c, series_lang)
		if variants is not None:
			dict_list.extend(variants)
		return (True, "")

	# Helper function to validate singular definitions
	def processDefinition(r, t, c):
		# Validity check: Neither raw nor translation components are empty strings
		if len(r) == 0 or len(t) == 0:
			reason = "Cannot have empty entries within a definition"
			return (False, reason)

		dict_list.append((r, (t, c)))
		return (True, "")

	try:
		with io.open(dict_path, mode='r', encoding='utf8') as dict_file:
			name_pattern = re.compile(r"\s*@name\{(.+),(.+)\}\s*(\/\/.*)?")
			defn_pattern = re.compile(r"([^\-\-\>]*)-->([^\/\/]*)(\/\/.*)?")
			dict_contents = dict_file.readlines()
			for index in range(0, len(dict_contents)):
				reason = None
				line = dict_contents[index]
				line = line.strip()
				# Double quotations in the google translate anchor mess up the link
				line = line.replace("\"", "\'")

				# Skip comment lines and unformatted/misformatted lines
				if line[0:2] == "//" or len(line) == 0 or line.isspace():
					continue

				# Match an @name line
				name_match = name_pattern.match(line)
				if name_match is not None:
					# Process name tagged lines: '@name{name_raw, name_trans}',
					#  '@name{first_name_raw|last_name_raw, first_name_trans|last_name_trans}', etc...
					(r, t, c) = (name_match[1], name_match[2], name_match[3])
					raw_component = r.strip().split(DICT_NAME_DIVIDER)
					trans_component = t.strip().split(DICT_NAME_DIVIDER)
					# Start comment from index 2 to ignore the '//'
					comment = c[2:COMMENT_MAX_LEN+2].strip() if c is not None else None

					(valid_name, reason) = processNameTag(raw_component, trans_component, comment)
					if valid_name:
						continue

				# Match a regular definition
				defn_match = defn_pattern.match(line)
				if defn_match is not None:
					(r, t, c) = (defn_match[1], defn_match[2], defn_match[3])
					raw_component = r.strip()
					trans_component = t.strip()
					# Start comment from index 2 to ignore the '//'
					comment = c[2:COMMENT_MAX_LEN+2].strip() if c is not None else None

					(valid_def, reason) = processDefinition(raw_component, trans_component, comment)
					if valid_def:
						continue

				# All else fails: misformatted line
				reason = "Unrecognized syntactical construct" if (reason is None) else reason
				flashMisformattedLine(line, index+1, reason)
	except Exception as err:
		raise DictFileReadException(dict_fname)

	# Finally, sanitize user input to prevent HTML code injection
	dict_list = [sanitizeDictEntry(entry) for entry in dict_list]
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

	dict_entry = series_entry.dictionary
	dict_fname = dict_entry.fname

	host_entry = HostTable.query.filter_by(id=series_entry.host_id).first()
	lang = host_entry.host_lang

	# Parse the mappings into a list
	dict_list = []

	# First add standalone honorifics
	standalone_honorifics = HonorificsTable.query.filter_by(
		lang=lang,
		opt_standalone=True,
		enabled=True )
	for honorific_entry in standalone_honorifics:
		dict_list.append((honorific_entry.raw, (honorific_entry.trans, None)))

	# Next, process the common_dict
	try:
		common_dict_entry = DictionaryTable.query.filter_by(fname=COMMON_DICT_FNAME).first()
		if common_dict_entry.enabled:
			dict_list.extend(processDictFile(COMMON_DICT_FNAME, lang))
	except CustomException as err:
		flash(str(err), err.severity)

	# Finally, process the series specific dict
	try:
		if dict_entry.enabled:
			dict_list.extend(processDictFile(dict_fname, lang))
	except (DictFileDNEOnProcessException, DictFileEmptyOnProcessException) as err:
		host_manager = hostmanager.createManager(host_entry.host_type)
		createDictFile( dict_fname, title, abbr, host_manager.generateSeriesUrl(code))
		flash(str(err), err.severity)
	except CustomException as err:
		flash(str(err), err.severity)

	# Initialize the global. Need to sort such that longer strings are processed
	# before the shorter ones so sort by length of the string
	dict_list.sort(key=lambda x: len(x[0]), reverse=True)
	return OrderedDict(dict_list)
