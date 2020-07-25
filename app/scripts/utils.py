#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
from tempfile import TemporaryFile

# Internal imports
from app import db
from app.forms import RegisterNovelForm
from app.forms import EditNovelForm
from app.forms import RemoveNovelForm
from app.models import SeriesTable
from app.models import DictionariesTable
from app.models import HostTable


def getLatestChapter(series_code):
	return 0

def registerSeriesToDatabase(reg_form):
	# Rip relevant information
	series_code = str(reg_form.series_code.data)
	series_title = str(reg_form.title.data)
	series_abbr = str(reg_form.abbr.data)

	host_entry = HostTable.query.filter_by(host_name="Syosetu").first()

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
		latest_ch=getLatestChapter(series_code),
		dict_id=dict_entry.id,
		host_id=host_entry.id,
	)
	db.session.add(series_entry)
	db.session.commit()

	return series_entry