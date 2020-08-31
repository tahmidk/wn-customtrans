#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Severity level to display if message is displayed as a flashed message
WARNING = 'warning'
CRITICAL = 'danger'

# CustomException super class
class CustomException(Exception):
	def __init__(self, msg, severity):
		super().__init__(msg)
		self.severity = severity

#=====================================================
#  Dictionary Handling Errors
#=====================================================
# Encountered when dictionary file could not be be created
class DictFileCreationException(CustomException):
	def __init__(self, dict_file):
		msg = "Aborted: Error creating dictionary \'%s\'" % dict_file
		super().__init__(msg, CRITICAL)

# Encountered when dictionary file could not be renamed
class DictFileRenameException(CustomException):
	def __init__(self, dict_file):
		msg = "Aborted: Error renaming dictionary \'%s\'" % dict_file
		super().__init__(msg, CRITICAL)

# Encountered when dictionary file could not be read
class DictFileReadException(CustomException):
	def __init__(self, dict_file):
		msg = "Encountered an error reading dictionary \'%s\'. Dictionary ignored" % dict_file
		super().__init__(msg, WARNING)

# Encountered when attempting to physically delete a dict file
class DictFileDeletionException(CustomException):
	def __init__(self, dict_file):
		msg = "Encountered an error while attempting to delete dictionary \'%s\'" % dict_file
		super().__init__(msg, CRITICAL)

# Encountered when dictionary file for a series does not exist
class DictFileDNEOnProcessException(CustomException):
	def __init__(self, dict_file):
		msg = "No dictionary found for this series. Created new dictionary \'%s\'" % dict_file
		super().__init__(msg, WARNING)

class DictFileEmptyOnProcessException(CustomException):
	def __init__(self, dict_file):
		msg = "Series dictionary was found to be empty. Reinitialized dictionary \'%s\'" % dict_file
		super().__init__(msg, WARNING)

#=====================================================
#  Web Issue Handling Errors
#=====================================================
# Encountered when Python fails to retrieve an html
class HtmlFetchException(CustomException):
	def __init__(self, url):
		msg = "Aborted: Could not fetch html data from \'%s\'" % url
		super().__init__(msg, CRITICAL)
