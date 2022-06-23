#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Internal imports
from app import db
from app.models import SettingsTable


class UserSettings:
	# Defined themes
	chapter_themes = [
		"light",
		"dark",
		"blueblazar",
		"pharoah",
		"ubuntu",
		"phosphorescent",
	]

	dictionary_edit_themes = [
		"light",
		"dark"
	]

	def __init__(self, settings_entry):
		self.__settings = settings_entry

	def get_settings(self):
		return self.__settings

	# Setting: Chapter Theme
	def get_chapter_theme(self):
		return self.__settings.theme_chapter

	def set_chapter_theme(self, theme):
		if theme in UserSettings.chapter_themes:
			self.__settings.theme_chapter = theme
			db.session.add(self.__settings)
			db.session.commit()
			return True

		return False

	# Setting: Dictionary Edit Theme
	def get_dictionary_edit_theme(self):
		return self.__settings.theme_dictionary_edit

	def set_dictionary_edit_theme(self, theme):
		if theme in UserSettings.dictionary_edit_themes:
			self.__settings.theme_dictionary_edit = theme
			db.session.add(self.__settings)
			db.session.commit()
			return True

		return False
