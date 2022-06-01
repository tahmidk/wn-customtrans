# -*- coding: utf-8 -*-
#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================
# Python imports
from lru import LRU
import multiprocessing as mp

# Internal imports
from app import views
from app.scripts import utils
from app.models import ChapterTable



# Class to manage chapter cache records
class ChapterCacheManager:
	def __init__(self, cache_size=20):
		self.__cache_size = cache_size
		self.__cache = LRU(cache_size)

	@staticmethod
	def generateCacheKey(chapter_entry):
		"""-------------------------------------------------------------------
			Function:		[generateCacheKey]
			Description:	Converts ChapterTable entry to a string hash for this manager
			Input:
			  [chapter_entry]	The chapter database entry to generate key for
			Return:			String hash identifying the given ChapterTable entry
			-------------------------------------------------------------------
		"""
		return f"series_{chapter_entry.volume.series.id}@{chapter_entry.number}"

	def addCacheRecord(self, chapter_entry, chapter_render):
		"""-------------------------------------------------------------------
			Function:		[addCacheRecord]
			Description:	Adds a chapter cache record to the cache for the given chapter
							Additionally generates caches for the next and previous chapter
							if enable_spatial_locality flag is set
			Input:
			  [chapter_entry]			The chapter database entry to generate cache for
			  [chapter_render]			The rendered chapter HTML
			Return:			True on success, False otherwise
			-------------------------------------------------------------------
		"""
		if not self.hasCacheRecord(chapter_entry):
			self.__cache[ChapterCacheManager.generateCacheKey(chapter_entry)] = chapter_render
			return True

		return False

	def removeCacheRecord(self, chapter_entry):
		"""-------------------------------------------------------------------
			Function:		[removeCacheRecord]
			Description:	Removes the cache record associated with the given chapter
							database entry
			Input:
			  [chapter_entry]	The chapter database entry whose cache needs deletion
			Return:			True on success, False otherwise
			-------------------------------------------------------------------
		"""
		if self.hasCacheRecord(chapter_entry):
			del self.__cache[ChapterCacheManager.generateCacheKey(chapter_entry)]
			return True
		return False

	def hasCacheRecord(self, chapter_entry):
		"""-------------------------------------------------------------------
			Function:		[hasCacheRecord]
			Description:	Check if given chapter entry is cached
			Input:
			  [chapter_entry]	The chapter database entry to check for a cache
			Return:			True if exists, False otherwise
			-------------------------------------------------------------------
		"""
		if chapter_entry != None:
			ch_key = ChapterCacheManager.generateCacheKey(chapter_entry)
			return self.__cache.has_key(ch_key)
		return False

	def getCacheRecord(self, chapter_entry):
		"""-------------------------------------------------------------------
			Function:		[getCacheRecord]
			Description:	Retrieves the cached rendered HTML associated with the
							given chapter entry
			Input:
			  [chapter_entry]	The chapter database entry for which cache should be fetched
			Return:			HTML render of chapter, None if cache miss
			-------------------------------------------------------------------
		"""
		if self.hasCacheRecord(chapter_entry):
			return self.__cache[ChapterCacheManager.generateCacheKey(chapter_entry)]
		return None

	def __regenerateCacheRecord(self, cache_key):
		"""-------------------------------------------------------------------
			Function:		[__regenerateCacheRecord]
			Description:	Private helper member to regenerate the cache record
							associated with the provided key with up-to-date series
							dictionary
			Input:
			  [cache_key]	Key of the cache record to regenerate
			Return:			True on success, False otherwise
			-------------------------------------------------------------------
		"""
		return True

	def regenerateAllCacheRecords(self):
		"""-------------------------------------------------------------------
			Function:		[regenerateAllCacheRecords]
			Description:	Regenerates the HTML of all existing cache records
			Input: 			None
			Return:			True on success, False otherwise
			-------------------------------------------------------------------
		"""
		for cache_key in self.__cache.keys():
			if not self.__regenerateCacheRecord(cache_key):
				# Unable to regenerate cache, clean the cache
				self.clearAllCacheRecords()
				return False
		return True

	def clearAllCacheRecords(self):
		"""-------------------------------------------------------------------
			Function:		[clearAllCacheRecords]
			Description:	Clears all existing cache records
			Input: 			None
			Return:			None
			-------------------------------------------------------------------
		"""
		self.__cache.clear()