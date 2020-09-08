#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Severity level to display if message is displayed as a flashed message
# Creates a strong tag with text
def strong(text):
	return "<strong>%s</strong>" % text
# Creates a monspace span with text
def mono(text):
	return "<span class=\"mono\">%s</span>" % text

SUCCESS = 'success'
WARNING = 'warning'
CRITICAL = 'danger'

SUCCESS_BOLD = strong("Success:")
WARNING_BOLD = strong("Warning:")
CRITICAL_BOLD = strong("Aborted:")


# CustomException super class
class CustomException(Exception):
	def __init__(self, msg, severity):
		super().__init__(msg)
		self.severity = severity

#=====================================================
#  Dictionary Handling Errors
#=====================================================
class SeriesEntryDNEException(CustomException):
	def __init__(self, series_abbr):
		msg = "%s The series entry %s is not registered" % \
			(CRITICAL_BOLD, strong(series_abbr))
		super().__init__(msg, CRITICAL)

class DictEntryDNEException(CustomException):
	def __init__(self, dict_fname):
		msg = "%s The dictionary entry %s is not registered" % \
			(CRITICAL_BOLD, mono(dict_fname))
		super().__init__(msg, CRITICAL)

class FileTooLargeException(CustomException):
	def __init__(self, filesize_str):
		msg = "%s The uploaded file is larger than %s" % \
			(CRITICAL_BOLD, mono(filesize_str))
		super().__init__(msg, CRITICAL)

class InvalidFilenameException(CustomException):
	def __init__(self, filename):
		msg = "%s The uploaded file \'%s\' has an invalid filename" % \
			(CRITICAL_BOLD, mono(filename))
		super().__init__(msg, CRITICAL)

class InvalidDictFileExtensionException(CustomException):
	def __init__(self, ext):
		msg = "%s Unexpected file extension \'%s\' uploaded" % \
			(CRITICAL_BOLD, mono(ext))
		super().__init__(msg, CRITICAL)

# Encountered when dictionary file could not be be created
class DictFileCreationException(CustomException):
	def __init__(self, dict_file):
		msg = "%s Error creating dictionary %s" % (CRITICAL_BOLD, mono(dict_file))
		super().__init__(msg, CRITICAL)

# Encountered when dictionary file could not be renamed
class DictFileRenameException(CustomException):
	def __init__(self, dict_file):
		msg = "%s Error renaming dictionary %s" % (CRITICAL_BOLD, mono(dict_file))
		super().__init__(msg, CRITICAL)

# Encountered when dictionary file could not be read
class DictFileReadException(CustomException):
	def __init__(self, dict_file):
		msg = "%s Encountered an error reading dictionary %s. Dictionary ignored" % \
			(WARNING_BOLD, mono(dict_file))
		super().__init__(msg, WARNING)

# Encountered when attempting to physically delete a dict file
class DictFileDeletionException(CustomException):
	def __init__(self, dict_file):
		msg = "Encountered an error while attempting to delete dictionary %s" % mono(dict_file)
		super().__init__(msg, CRITICAL)

# Encountered when dictionary file for a series does not exist
class DictFileDNEOnProcessException(CustomException):
	def __init__(self, dict_file):
		msg = "No dictionary found for this series. Created new dictionary %s" % mono(dict_file)
		super().__init__(msg, WARNING)

class DictFileEmptyOnProcessException(CustomException):
	def __init__(self, dict_file):
		msg = "Series dictionary was found to be empty. Reinitialized dictionary %s" % mono(dict_file)
		super().__init__(msg, WARNING)

#=====================================================
#  Web Issue Handling Errors
#=====================================================
# Encountered when Python fails to retrieve an html
class HtmlFetchException(CustomException):
	def __init__(self, url):
		msg = "%s Could not fetch html data from %s" % (CRITICAL_BOLD, mono(url))
		super().__init__(msg, CRITICAL)
