#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
from tempfile import TemporaryFile

# Internal imports
from app import app
from app import db
from app.models import SeriesTable
from app.models import HostTable
from app.models import Language
from app.scripts.hostmanager import Host


test_series = [
	{
		"title": "This is a Sample Novel Title",
		"abbr": "ThisAbbrFifteen",
		"current": 7,
		"latest": 100,
		"code": "n7057gi"
	},
	{
		"title": "The Most Beautiful Girl in School asks the Main Character 'What is Love'?",
		"abbr": "BBDntHurtMe",
		"current": 0,
		"latest": 45,
		"code": "n9946fx"
	},
	{
		"title": "The Adventurer Contracted to the Strongest Deity Crushes Flags",
		"abbr": "FlagCrush",
		"current": 145,
		"latest": 1206,
		"code": "n3404fh"
	},
	{
		"title": "When My Childhood Friend Becomes JK",
		"abbr": "CHJK",
		"current": 2,
		"latest": 28,
		"code": "n4893gi"
	},
	{
		"title": "The Strongest Incompetent Reaches for the Top",
		"abbr": "WhiteRabbit",
		"current": 1,
		"latest": 10,
		"code": "n0737ga"
	},
	{
		"title": "Surrounded By Four",
		"abbr": "Surrounded",
		"current": 0,
		"latest": 0,
		"code": "n9450ge"
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

	for series in test_series:
		# Create dictionary entry in database
		dict_fname = "%s_%s.dict" % (series['abbr'], series['code'])
		# Create series entry in database
		series_entry = SeriesTable(
			code=series['code'],
			title=series['title'],
			abbr=series['abbr'],
			current_ch=series['current'],
			latest_ch=series['latest'],
			bookmarks=[1, 3],
			host_id=host_entry.id
		)
		db.session.add(series_entry)
		db.session.commit()

if __name__ == '__main__':
	reinitDatabase()
	app.run()