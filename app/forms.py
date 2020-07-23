#=======================================================================
#  Copyright (c) 2020, Tahmid Khan
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause license found in the LICENSE file
#=======================================================================

# Flask imports
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Regexp

# Other imports
from urllib.request import urlopen
from urllib.error import HTTPError

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
		Regexp(r'^[\w]+$', message="Cannot contain spaces or special characters")
	]
	abbr = StringField('Abbreviation', validators=abbr_validators)

	# Field: code - The ncode for this
	series_code_validators = [
		DataRequired(),
		Length(min=7, max=7)
	]
	series_code = StringField('Series Code', validators=series_code_validators)

	# Submit form
	submit = SubmitField('Register')

	# Custom validator for series code to make sure url exists
	def validate_series_code(self, series_code):
		url = "https://ncode.syosetu.com/" + series_code.data
		try:
			urlopen(url)
		# Page not found
		except HTTPError as e:
			raise ValidationError("<pre class=\"errurl\">%s</pre> does not exist" % url)
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
		Length(min=1, max=15)
	]
	abbr = StringField('Abbreviation', validators=abbr_validators)

	# Submit form
	submit = SubmitField('Submit')