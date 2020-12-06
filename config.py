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

	# Security
	SESSION_COOKIE_SECURE = True
	SECRET_KEY = 'e0d41ebf1910b2ba'
	SQLALCHEMY_DATABASE_NAME = 'database_wnct.db'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + SQLALCHEMY_DATABASE_NAME
	# Dictionary file upload constraints
	ALLOWED_DICT_EXTENSIONS = ['DICT', 'TXT']
	MAX_DICT_FILESIZE = 2 * 1024 * 1024

# Config used in production
class ProductionConfig(BaseConfig):
	SESSION_COOKIE_SECURE = False
	CONFIG_NAME = "production"

# Config used in development
class DevelopmentConfig(BaseConfig):
	CONFIG_NAME = "development"
	DEBUG = True

	DICTIONARIES_PATH = os.path.join(os.getcwd(), 'user', 'dev', 'dicts')

	SESSION_COOKIE_SECURE = False
	SQLALCHEMY_DATABASE_NAME = 'database_dev.db'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + SQLALCHEMY_DATABASE_NAME

# Config used in
class TestingConfig(BaseConfig):
	CONFIG_NAME = "testing"
	TESTING = True

	DICTIONARIES_PATH = os.path.join(os.getcwd(), 'user', 'test', 'dicts')

	SESSION_COOKIE_SECURE = False
	SQLALCHEMY_DATABASE_NAME = 'database_test.db'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + SQLALCHEMY_DATABASE_NAME