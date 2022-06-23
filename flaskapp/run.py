#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python imports
import os
import argparse as argp

# Internal imports
from app import app


def initArgParse():
	parser = argp.ArgumentParser()

	# Host database actions
	parser.add_argument('--reinit_hosts', required=False, action="store_true",
		help="Drops and reinitializes all hosts in the database from seed_data/hosts.json")

	return parser.parse_args()


if __name__ == '__main__':
	args = initArgParse()

	if args.reinit_hosts:
		hosts_path = os.path.join(app.config['SEED_DATA_PATH'], "hosts.json")
		print("Dropping and reinitializing hosts table from: \'%s\'" % hosts_path)
		utils.seedHosts(hosts_path, mode='overwrite')

	app.run()
