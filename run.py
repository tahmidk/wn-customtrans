#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
import io
import os
import argparse as argp

# Internal imports
from flask import url_for

from app import app
from app import db

from app.models import *

import app.scripts.utils as utils
import app.scripts.dictionary as dictionary
from app.scripts.hostmanager import Host, Language


@app.before_first_request
def initializeDatabase():
	"""-------------------------------------------------------------------
		Function:		[initializeHosts]
		Description:	Initializes
		Input:			None
		Return: 		None, initializes the database on app start
		------------------------------------------------------------------
	"""
	# HostTable can't be empty on execution of the flask app
	if len(HostTable.query.all()) == 0:
		hosts_path = os.path.join(app.config['SEED_DATA_PATH'], "hosts.json")
		print("No hosts found in the database... Seeding hosts from disk: \'%s\'" % hosts_path)
		utils.seedHosts(hosts_path, mode='overwrite')

	# DictionaryTable should minimally have the common dictionary registered
	if DictionaryTable.query.filter_by(fname=dictionary.COMMON_DICT_FNAME).first() is None:
		# Add the common dictionary
		dict_entry = DictionaryTable(
			fname=dictionary.COMMON_DICT_FNAME,
		)
		db.session.add(dict_entry)
		db.session.commit()

	# In development and testing, we need series and honorifics to be seeded
	# with test values
	if app.config["ENV"] in ["development", "testing"]:
		print("Reseeding series and honorifics entries")
		utils.seedHonorifics(
			os.path.join(app.config['SEED_DATA_PATH'], "honorifics.json"),
			mode='overwrite')
		utils.seedSeries(
			os.path.join(app.config['SEED_DATA_PATH'], "test_series.json"),
			mode='overwrite')


# By running
if __name__ == '__main__':
	parser = argp.ArgumentParser()
	parser.add_argument('--reinit_hosts', required=False, action="store_true",
		help="Drops and reinitializes the host table from seed_data/hosts.json")
	args = parser.parse_args()

	db_path = os.path.join("app", app.config['SQLALCHEMY_DATABASE_NAME'])
	if not os.path.isfile(db_path):
		db.create_all()
		initializeDatabase()
	elif os.stat(db_path).st_size == 0:
		os.remove(db_path)
		db.create_all()
		initializeDatabase()

	# Special admin level argument to update database
	if args.reinit_hosts:
		hosts_path = os.path.join(app.config['SEED_DATA_PATH'], "hosts.json")
		print("Dropping and reinitializing hosts table from: \'%s\'" % hosts_path)
		utils.seedHosts(hosts_path, mode='overwrite')

	app.run()