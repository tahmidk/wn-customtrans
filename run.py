#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
import io

# Internal imports
from flask import url_for

from app import app
from app import db

from app.models import SeriesTable
from app.models import DictionaryTable
from app.models import HostTable
from app.models import Language

from app.scripts.hostmanager import Host
from app.scripts.hostmanager import createManager


test_series = [
	{
		"title": "This is a Sample Novel Title",
		"abbr": "ThisAbbrFifteen",
		"current": 7,
		"latest": 100,
		"code": "n7057gi",
		"host": Host.Syosetu
	},
	{
		"title": "The Most Beautiful Girl in School asks the Main Character 'What is Love'?",
		"abbr": "BBDntHurtMe",
		"current": 0,
		"latest": 45,
		"code": "n9946fx",
		"host": Host.Syosetu
	},
	{
		"title": "The Adventurer Contracted to the Strongest Deity Crushes Flags",
		"abbr": "FlagCrush",
		"current": 145,
		"latest": 1206,
		"code": "n3404fh",
		"host": Host.Syosetu
	},
	{
		"title": "When My Childhood Friend Becomes JK",
		"abbr": "CHJK",
		"current": 2,
		"latest": 28,
		"code": "n4893gi",
		"host": Host.Syosetu
	},
	{
		"title": "The Strongest Incompetent Reaches for the Top",
		"abbr": "WhiteRabbit",
		"current": 1,
		"latest": 10,
		"code": "n0737ga",
		"host": Host.Syosetu
	},
	{
		"title": "Surrounded By Four",
		"abbr": "Surrounded",
		"current": 0,
		"latest": 0,
		"code": "n9450ge",
		"host": Host.Syosetu
	},
]
hosts = [
	{
		"host_type": Host.Syosetu,
		"host_name": "Syosetu",
		"host_lang": Language.JP,
		"host_url": "https://ncode.syosetu.com/"
	}
]

def reinitDatabase():
	db.drop_all()
	db.create_all()

	# Register all hosts
	for host in hosts:
		host_entry = HostTable(
			host_type=host['host_type'],
			host_name=host['host_name'],
			host_lang=host['host_lang'],
			host_url=host['host_url']
		)
		db.session.add(host_entry)
		db.session.commit()

	# Add the common dictionary
	dict_entry = DictionaryTable(
		fname="common_dict.dict",
	)
	db.session.add(dict_entry)
	db.session.commit()

	for series in test_series:
		series_host = HostTable.query.filter_by(host_type=series['host']).first();
		# Create dictionary entry in database
		dict_fname = "%s_%s_%s.dict" % (series['abbr'], series_host.host_name, series['code'])
		# dict_path = 'user/default/' + dict_fname
		# dict_url = url_for('static', filename=dict_path)
		# with io.open(dict_url, mode='w', encoding='utf8') as dict_file:
		# 	host_manager = createManager(series_host.host_type)

		# 	dict_file.write("// Series Title :  %s\n" % series['title'])
		# 	dict_file.write("// Abbreviation :  %s\n" % series['abbr'])
		# 	dict_file.write("// Series Link  :  %s\n" % host_manager.generateSeriesUrl(series))
		# 	dict_file.write("\n\n//=============================[ Names ]==================================")
		# 	dict_file.write(u'\n@name{ナルト, Naruto}')
		# 	dict_file.write(u'\n@name{うずまき, Uzumaki}')
		# 	dict_file.write("\n\n//=============================[ Places ]=================================")
		# 	dict_file.write("\n\n//=============================[ Skills ]=================================")
		# 	dict_file.write("\n\n//============================[ Monsters ]================================")
		# 	dict_file.write("\n\n//===========================[ Terminology ]==============================")
		# 	dict_file.write(u'\n九尾の狐 --> Nine Tailed Fox')
		# 	dict_file.write("\n\n//==============================[ Misc ]==================================")
		# 	dict_file.write("\n\n// END OF FILE")

		# Submit dictionary to database
		dict_entry = DictionaryTable(
			fname=dict_fname,
		)
		db.session.add(dict_entry)
		db.session.commit()

		# Create series entry in database
		series_entry = SeriesTable(
			code=series['code'],
			title=series['title'],
			abbr=series['abbr'],
			current_ch=series['current'],
			latest_ch=series['latest'],
			bookmarks=[1, 3],
			dict_id=dict_entry.id,
			host_id=host_entry.id
		)
		db.session.add(series_entry)
		db.session.commit()

if __name__ == '__main__':
	reinitDatabase()
	app.run()