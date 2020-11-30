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
from wtforms import RadioField
from wtforms import SelectField
from wtforms import HiddenField
from wtforms import ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Regexp

# Internal imports
from app.models import SeriesTable
from app.models import HonorificsTable
from app.models import HostTable
from app.models import HonorificAffix
from app.scripts.dictionary import COMMON_DICT_ABBR
from app.scripts.custom_errors import mono
from app.scripts.hostmanager import Language

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
		Length(min=1, max=20),
		Regexp(r'^[^\W_]*$', message="Cannot contain spaces or special characters")
	]
	abbr = StringField('Abbreviation', validators=abbr_validators)

	# Field: series_host - The host configuration for this series
	series_host = QuerySelectField( "Host",
									query_factory=lambda: HostTable.query,
									get_label='host_name',
									allow_blank=False )

	# Field: series_code - The identifying code for this series
	series_code_validators = [
		DataRequired(),
	]
	series_code = StringField('Series Code', validators=series_code_validators)

	# Submit form
	submit = SubmitField('Register')

	# Custom validator for title
	def validate_title(self, title):
		title_data = title.data.strip()
		series_entry = SeriesTable.query.filter_by(title=title_data).first()
		if series_entry is not None:
			raise ValidationError("This title is already taken by another series")

	# Custom validator for abbreviation
	def validate_abbr(self, abbr):
		abbr_data = abbr.data.strip()
		if abbr_data == COMMON_DICT_ABBR:
			raise ValidationError("The abbreviation \'%s\' is illegal" % abbr_data)

		# Validation: this abbreviation must not already be taken
		series_entry = SeriesTable.query.filter_by(abbr=abbr_data).first()
		if series_entry is not None:
			raise ValidationError("The abbreviation \'%s\' is taken by another series" % abbr_data)

	# Custom validator for series code
	def validate_series_code(self, series_code):
		# Validation: the host-code combination must not already be in the database
		series_code_data = series_code.data.strip()
		host_entry = self.series_host.data
		series_entry = SeriesTable.query.filter_by(code=str(series_code_data), host_id=host_entry.id).first()
		if series_entry is not None:
			raise ValidationError("This host-code combination registered under %s" % series_entry.abbr)

		# Validation: the url must exist
		url = host_entry.host_url + series_code_data
		try:
			urlopen(url)
		# Page not found
		except HTTPError as e:
			raise ValidationError("%s does not exist" % mono(url))
		# Some error has occurred
		except Exception as e:
			raise ValidationError("No response from %s. Try again later" % mono(url))

class EditNovelForm(FlaskForm):
	'''
		This form is used when displaying the "Edit Novel" modal to the user
		in the /libraries route
	'''
	series_id = HiddenField("Series Id")

	# Field: title - The user's title for the novel to register
	title_validators = [
		DataRequired(),
		Length(min=1, max=80)
	]
	title = StringField('Title', validators=title_validators)

	# Field: abbr - The user's personal abbreviation for this novel
	abbr_validators = [
		DataRequired(),
		Length(min=1, max=20),
		Regexp(r'^[\w]+$', message="Cannot contain spaces or special characters")
	]
	abbr = StringField('Abbreviation', validators=abbr_validators)

	# Submit form
	submit = SubmitField('Save')

	# Custom validator for title
	def validate_title(self, title):
		# Submission invalid if there's another SeriesTable entry w/ a diff id but same title
		title_data = title.data.strip()
		not_id = SeriesTable.query.filter(SeriesTable.id != int(self.series_id.data))
		if not_id.filter_by(title=title_data).count() > 0:
			raise ValidationError("%s is already registered" % title_data)

	# Custom validator for abbreviation
	def validate_abbr(self, abbr):
		abbr_data = abbr.data.strip()
		if abbr_data == COMMON_DICT_ABBR:
			raise ValidationError("The abbreviation \'%s\' is illegal" % abbr_data)

		# Validation: this abbreviation must not already be taken
		not_id = SeriesTable.query.filter(SeriesTable.id != int(self.series_id.data))
		if not_id.filter_by(abbr=abbr_data).count() > 0:
			raise ValidationError("The abbreviation \'%s\' is taken by another series" % abbr_data)

class RemoveNovelForm(FlaskForm):
	'''
		Confirmaton form used when user tries to remove a novel from library
		in the /libraries route
	'''
	opt_keep_dict = BooleanField("Keep the dictionary associated with this series?", default=True)

	submit = SubmitField('Remove')

class AddHonorificForm(FlaskForm):
	'''
		This form is used when displaying the "Add Honorific" modal to the user
		in the /honorifics route
	'''

	# Field: hraw - The raw honorific entry in its native language
	hraw_validators = [
		DataRequired(),
		Length(min=1, max=30)
	]
	hraw = StringField('Raw', validators=hraw_validators)

	# Field: hraw - The raw honorific entry in its native language
	htrans_validators = [
		DataRequired(),
		Length(min=1, max=30)
	]
	htrans = StringField('Translation', validators=htrans_validators)

	# Field: lang - The native language of the raw honorific provided
	lang_selection = sorted([(l.value, l.name) for l in Language])
	lang = SelectField("Language", choices=lang_selection, coerce=int, default=lang_selection[0])

	# Field: affix - Treat this honorific as a suffix or prefix?
	affix_validators = [
		DataRequired(),
	]
	affix = RadioField('Affix', validators=affix_validators, coerce=int, default=HonorificAffix.SUFFIX.value,
		choices=[(HonorificAffix.PREFIX.value, 'Prefix'), (HonorificAffix.SUFFIX.value, 'Suffix')])

	# Field: opt_with_dash - Option to append a dash character between subject and honorific
	opt_with_dash = BooleanField("Append dash", default=True)

	# Field: opt_standalone - Option to indicate that this honorific can potentially be found
	# w/out being attached to a subject
	opt_standalone = BooleanField("Standalone", default=False)

	# Submit form
	submit = SubmitField('Save')

	# Custom validator for hraw
	def validate_hraw(self, hraw):
		hraw_data = hraw.data.strip()
		honorifics_entry = HonorificsTable.query.filter_by(raw=hraw_data).first()
		if honorifics_entry is not None:
			raise ValidationError("%s is already registered" % hraw_data)

class EditHonorificForm(FlaskForm):
	'''
		This form is used when displaying the "Edit Honorific" modal to the user
		in the /honorifics route
	'''
	# The id of the honorific being edited
	hon_id = HiddenField("Id")

	# Field: hraw - The raw honorific entry in its native language
	hraw_validators = [
		DataRequired(),
		Length(min=1, max=30)
	]
	hraw = StringField('Raw', validators=hraw_validators)

	# Field: hraw - The raw honorific entry in its native language
	htrans_validators = [
		DataRequired(),
		Length(min=1, max=30)
	]
	htrans = StringField('Translation', validators=htrans_validators)

	# Field: lang - The native language of the raw honorific provided
	lang_selection = sorted([(l.value, l.name) for l in Language])
	lang = SelectField("Language", choices=lang_selection, coerce=int)

	# Field: affix - Treat this honorific as a suffix or prefix?
	affix_validators = [
		DataRequired(),
	]
	affix = RadioField('Affix', validators=affix_validators, coerce=int,
		choices=[(HonorificAffix.PREFIX.value, 'Prefix'), (HonorificAffix.SUFFIX.value, 'Suffix')])

	# Field: opt_with_dash - Option to append a dash character between subject and honorific
	opt_with_dash = BooleanField("Append dash")

	# Field: opt_standalone - Option to indicate that this honorific can potentially be found
	# w/out being attached to a subject
	opt_standalone = BooleanField("Standalone")

	# Submit form
	submit = SubmitField('Save')

	# Custom validator for hraw
	def validate_hraw(self, hraw):
		# Submission invalid if there's another HonorificTable entry w/ a diff id but same hraw
		hraw_data = hraw.data.strip()
		not_id = HonorificsTable.query.filter(HonorificsTable.id != int(self.hon_id.data))
		if not_id.filter_by(raw=hraw_data).count() > 0:
			raise ValidationError("%s is already registered" % hraw_data)