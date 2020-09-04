#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================
import os

class BaseConfig(object):
	CONFIG_NAME = "unset"
	DEBUG = False
	TESTING = False

	# Important paths
	SEED_DATA_PATH = os.path.join(os.getcwd(), 'seed_data')
	DICTIONARIES_PATH = os.path.join(os.getcwd(), 'user', 'default', 'dicts')

	SECRET_KEY = 'e0d41ebf1910b2ba'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///database_wnct.db'
	SESSION_COOKIE_SECURE = True

# Config used in production
class ProductionConfig(BaseConfig):
	CONFIG_NAME = "production"

# Config used in development
class DevelopmentConfig(BaseConfig):
	CONFIG_NAME = "development"
	DEBUG = True

	SQLALCHEMY_DATABASE_URI = 'sqlite:///database_dev.db'
	SESSION_COOKIE_SECURE = False

# Config used in
class TestingConfig(BaseConfig):
	CONFIG_NAME = "testing"
	TESTING = True

	SQLALCHEMY_DATABASE_URI = 'sqlite:///database_test.db'
	SESSION_COOKIE_SECURE = False