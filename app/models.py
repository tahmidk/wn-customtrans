from app import db

class SeriesTable(db.Model):
	code = db.Column(db.String(7), primary_key=True)
	title = db.Column(db.String(80), nullable=False)
	abbr = db.Column(db.String(15), unique=True, nullable=False)
	current_ch = db.Column(db.Integer, nullable=False)
	latest_ch = db.Column(db.Integer, nullable=False)
	# Foreign key for associated dictionary file
	dict_id = db.Column(db.Integer, nullable=False)

	def __repr__(self):
		return "Novel(code=%s, abbr=%s, current_ch=%s, latest_ch=%s)" % \
			(self.code, self.abbr, self.current_ch, self.latest_ch)

class DictionaryFile(db.Model):
	dict_id = db.Column(db.Integer, primary_key=True)
	file_name = db.Column(db.String, nullable=False)
	file_data = db.Column(db.LargeBinary, nullable=False)