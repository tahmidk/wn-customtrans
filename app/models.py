#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Flask imports
from sqlalchemy.ext.mutable import MutableList

# Python imports
from enum import Enum

# Internal imports
from app import db
from app.scripts.hostmanager import Host
from app.scripts.hostmanager import Language


# Honorific affix descriptor
class HonorificAffix(Enum):
    PREFIX = 1
    SUFFIX = 2


# Database models
class SeriesTable(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	code = db.Column(db.String(7), nullable=False)
	title = db.Column(db.String(80), unique=True, nullable=False)
	abbr = db.Column(db.String(15), unique=True, nullable=False)
	current_ch = db.Column(db.Integer, nullable=False)
	latest_ch = db.Column(db.Integer, nullable=False)
	bookmarks = db.Column(MutableList.as_mutable(db.PickleType), nullable=False)
	# Foreign key for the associated dictionary
	dict_id = db.Column(db.Integer, nullable=False)
	# Foreign key for the host website
	host_id = db.Column(db.Integer, nullable=False)

	def __repr__(self):
		return "Novel(code=%s, abbr=%s, current_ch=%s, latest_ch=%s)" % \
			(self.code, self.abbr, self.current_ch, self.latest_ch)

class DictionaryTable(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	fname = db.Column(db.String, unique=True, nullable=False)
	enabled = db.Column(db.Boolean, default=True)

	def __repr__(self):
		return "Dict(fname=%s, enabled=%s)" % (self.fname, self.enabled)

class HonorificsTable(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	lang = db.Column(db.Enum(Language), nullable=False)
	raw = db.Column(db.String, unique=True, nullable=False)
	trans = db.Column(db.String, nullable=False)
	affix = db.Column(db.Enum(HonorificAffix), default=HonorificAffix.SUFFIX)
	opt_with_dash = db.Column(db.Boolean, default=True)
	opt_standalone = db.Column(db.Boolean, default=False)
	enabled = db.Column(db.Boolean, default=True)

	def __repr__(self):
		return "Honorific(raw=%s, trans=%s, lang=%s)" % \
			(self.raw, self.trans, self.lang)

class HostTable(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	host_type = db.Column(db.Enum(Host), unique=True, nullable=False)
	host_name = db.Column(db.String, unique=True, nullable=False)
	host_lang = db.Column(db.Enum(Language), nullable=False)
	host_url = db.Column(db.String, unique=True, nullable=False)
	host_search_engine = db.Column(db.String)

	def __repr__(self):
		return "Host(id=%s, host_name=%s, host_lang=%s, host_url=%s)" % \
			(self.id, self.host_name, self.host_lang, self.host_url)

class ConfigurationTable(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	opt_use_common = db.Column(db.Boolean, default=True)
