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

from app.models import *

from app.scripts.hostmanager import Host, Language
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

honorifics = [
	{
		"lang": Language.JP,
		"raw": "さん",
		"trans": "san",
		"standalone": False
	},
	{
		"lang": Language.JP,
		"raw": "氏",
		"trans": "san",
		"standalone": False
	},
	{
		"lang": Language.JP,
		"raw": "くん",
		"trans": "kun",
		"standalone": False
	},
	{
		"lang": Language.JP,
		"raw": "クン",
		"trans": "kun",
		"standalone": False
	},
	{
		"lang": Language.JP,
		"raw": "君",
		"trans": "kun",
		"standalone": False
	},
	{
		"lang": Language.JP,
		"raw": "さま",
		"trans": "sama",
		"standalone": False
	},
	{
		"lang": Language.JP,
		"raw": "様",
		"trans": "sama",
		"standalone": False
	},
	{
		"lang": Language.JP,
		"raw": "サマ",
		"trans": "sama",
		"standalone": False
	},
	{
		"lang": Language.JP,
		"raw": "殿",
		"trans": "dono",
		"standalone": False
	},
	{
		"lang": Language.JP,
		"raw": "たん",
		"trans": "tan",
		"standalone": False
	},
	{
		"lang": Language.JP,
		"raw": "ちゃん",
		"trans": "chan",
		"standalone": False
	},
	{
		"lang": Language.JP,
		"raw": "ねーちゃん",
		"trans": "neechan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "姉ちゃん",
		"trans": "neechan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "お姉様",
		"trans": "oneesama",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "お姉さま",
		"trans": "oneesama",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "おねーさん",
		"trans": "oneesan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "お姉さん",
		"trans": "oneesan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "お姉ちゃん",
		"trans": "oneechan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "おねーちゃん",
		"trans": "oneechan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "おねえちゃん",
		"trans": "oneechan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "おねぇちゃん",
		"trans": "oneechan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "姉さま",
		"trans": "neesama",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "姉さん",
		"trans": "neesan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "姉様",
		"trans": "anesama",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "あねさま",
		"trans": "anesama",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "姉",
		"trans": "ane",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "おにーちゃん",
		"trans": "oniichan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "おにぃちゃん",
		"trans": "oniichan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "おにいちゃん",
		"trans": "oniichan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "お兄ちゃん",
		"trans": "oniichan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "お兄さん",
		"trans": "oniisan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "おにーさん",
		"trans": "oniisan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "おにぃさん",
		"trans": "oniisan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "兄ちゃん",
		"trans": "niichan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "にーちゃん",
		"trans": "niichan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "兄さん",
		"trans": "niisan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "にーさん",
		"trans": "niisan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "兄さま",
		"trans": "niisama",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "兄様",
		"trans": "anisama",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "兄貴",
		"trans": "aniki",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "兄",
		"trans": "ani",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "王女",
		"trans": "ojou",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "王女様",
		"trans": "ojousama",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "お嬢様",
		"trans": "ojousama",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "お嬢さん",
		"trans": "ojousan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "王子",
		"trans": "ouji",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "王子様",
		"trans": "oujisama",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "嬢",
		"trans": "jou",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "姫",
		"trans": "hime",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "姫様",
		"trans": "himesama",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "姫さま",
		"trans": "himesama",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "お姫様",
		"trans": "ohimesama",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "先生",
		"trans": "sensei",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "せんせー",
		"trans": "sensei",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "先輩",
		"trans": "senpai",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "センパイ",
		"trans": "senpai",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "せんぱい",
		"trans": "senpai",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "後輩",
		"trans": "kouhai",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "嬢ちゃん",
		"trans": "jouchan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "母さん",
		"trans": "kaasan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "おかーさん",
		"trans": "okaasan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "お母さん",
		"trans": "okaasan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "父さん",
		"trans": "otousan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "おっさん",
		"trans": "ossan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "おじいちゃん",
		"trans": "ojichan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "お祖父ちゃん",
		"trans": "ojichan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "おじさん",
		"trans": "ojisan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "お祖母ちゃん",
		"trans": "obachan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "お祖母さん",
		"trans": "obasan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "婆さん",
		"trans": "baasan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "ばーさん",
		"trans": "baasan",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "兄妹",
		"trans": "siblings",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "兄弟",
		"trans": "siblings",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "姉弟",
		"trans": "siblings",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "姉妹",
		"trans": "sisters",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "義姉",
		"trans": "step-sister",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "義姉弟",
		"trans": "step-siblings",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "主任",
		"trans": "chief",
		"standalone": True
	},
	{
		"lang": Language.JP,
		"raw": "達",
		"trans": "and co'",
		"standalone": False
	},
	{
		"lang": Language.JP,
		"raw": "たち",
		"trans": "and co'",
		"standalone": False
	}
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

	# Register all honorifics
	for honorific in honorifics:
		honorific_entry = HonorificsTable(
			lang=honorific["lang"],
			raw=honorific["raw"],
			trans=honorific["trans"],
			opt_standalone=honorific["standalone"],
		)
		db.session.add(honorific_entry)
		db.session.commit()

	# Add the common dictionary
	dict_entry = DictionaryTable(
		fname="common_dict.dict",
	)
	db.session.add(dict_entry)
	db.session.commit()

	for series in test_series:
		series_host = HostTable.query.filter_by(host_type=series['host']).first();
		# Submit dictionary to database
		dict_fname = "%s_%s_%s.dict" % (series['abbr'], series_host.host_name, series['code'])
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