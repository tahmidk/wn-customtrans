#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Python Imports
from urllib.request import urlopen
from urllib.error import HTTPError

# Flask imports
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms import BooleanField
from wtforms import SelectField
from wtforms import ValidationError
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Regexp

# Internal imports
from app.models import SeriesTable
from app.models import HostTable
from app.scripts.hostmanager import Host
from app.scripts.custom_errors import mono


# Global constants
COMMON_DICT_ABBR = "Common"


class RegisterNovelForm(FlaskForm):
	'''
		This form is used when displaying the "Register Novel" modal to the user
		in the /libraries route
	'''

	# Field: title - The user's title for the novel to register
	title_validators = [
		DataRequired(),
		Length(min=1, max=80)
	]
	title = StringField('Title', validators=title_validators)

	# Field: abbr - The user's personal abbreviation for this novel
	abbr_validators = [
		DataRequired(),
		Length(min=1, max=15),
		Regexp(r'^[^\W_]*$', message="Cannot contain spaces or special characters")
	]
	abbr = StringField('Abbreviation', validators=abbr_validators)

	# Field: series_host - The host configuration for this series
	host_entries = HostTable.query.all()
	host_selection = [(host.host_type.value, host.host_name) for host in host_entries]
	series_host = SelectField("Host", choices=host_selection, coerce=int, default=host_selection[0])

	# Field: series_code - The identifying code for this series
	series_code_validators = [
		DataRequired(),
	]
	series_code = StringField('Series Code', validators=series_code_validators)

	# Submit form
	submit = SubmitField('Register', )

	# Custom validator for series code
	def validate_abbr(self, abbr):
		if abbr.data == COMMON_DICT_ABBR:
			raise ValidationError("The abbreviation \'%s\' is illegal" % abbr.data)

		# Validation: this abbreviation must not already be taken
		series_entry = SeriesTable.query.filter_by(abbr=abbr.data).first()
		if series_entry is not None:
			raise ValidationError("The abbreviation \'%s\' is taken by another series" % abbr.data)

	# Custom validator for series code
	def validate_series_code(self, series_code):
		# Validation: the host-code combination must not already be in the database
		host_entry = HostTable.query.filter_by(host_type=Host(self.series_host.data)).first()
		series_entry = SeriesTable.query.filter_by(code=str(series_code.data), host_id=host_entry.id).first()
		if series_entry is not None:
			raise ValidationError("This host-code combination registered under %s" % series_entry.abbr)

		# Validation: the url must exist
		url = host_entry.host_url + series_code.data
		try:
			urlopen(url)
		# Page not found
		except HTTPError as e:
			raise ValidationError("%s does not exist" % mono(url))
		# Some error has occurred
		except Exception as e:
			raise ValidationError("No response from <pre class=\"errurl\">%s</pre>. Try again later" % url)

class EditNovelForm(FlaskForm):
	'''
		This form is used when displaying the "Edit Novel" modal to the user
		in the /libraries route
	'''

	# Field: title - The user's title for the novel to register
	title_validators = [
		DataRequired(),
		Length(min=1, max=80)
	]
	title = StringField('Title', validators=title_validators)

	# Field: abbr - The user's personal abbreviation for this novel
	abbr_validators = [
		DataRequired(),
		Length(min=1, max=15),
		Regexp(r'^[\w]+$', message="Cannot contain spaces or special characters")
	]
	abbr = StringField('Abbreviation', validators=abbr_validators)

	# Submit form
	submit = SubmitField('Save')

class RemoveNovelForm(FlaskForm):
	'''
		Confirmaton form used when user tries to remove a novel from library
		in the /libraries route
	'''
	opt_keep_dict = BooleanField("Keep the dictionary associated with this series?", default=True)

	submit = SubmitField('Remove')
