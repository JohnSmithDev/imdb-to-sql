# Converts the IMDB database *.list into a SQLite datbase
# Ameer Ayoub <ameer.ayoub@gmail.com>
# @todo make the whole thing database agnostic so we can switch

import re
from types import StringType
import os
from numerals import rntoi
import time
import cPickle as pickle
from settings import Database, Options, DatabaseTypes

def get_schema_prefix(type_d):
	if type_d == DatabaseTypes.SQLITE:
		return "sqlite"
	elif type_d == DatabaseTypes.MYSQL:
		return "mysql"
	elif type_d == DatabaseTypes.POSTGRES:
		return "postgres"
	else:
		return None

dicts = {}
counts = {}

def mk(file_name):
	"""utility function that turns a list name into a openable file name/path"""
	return Options.list_dir+'/'+file_name+Options.file_extension

	
# Precompile the regexes
class ParseRegexes:
	# raw regex strings for reference e.g. regex buddy copy paste
	raw_acted_in = """"?([^"]*?)"?\s\(((\?{4}|\d+)/?(\w+)?).*?\)(\s*\((T?VG?)\))?
		(\s*\((\w*)\))?(\s*\{([^\(]*?)(\s*\(\#(\d+)\.(\d+)\))?\})?
		(\s*\[(.*)\])?(\s*\<(\d+)\>)?"""
	raw_name = """('.+')?\s*(([^,']*),)?\s*([^\(]+)(\((\w+)\))?"""
	raw_movies = """"?([^"]*?)"?\s\(((\?{4}|\d+)/?(\w+)?).*?\)(\s*\((T?VG?)\))?
		(\s*\{([^\(]*?)(\s*\(\#(\d+)\.(\d+)\))?\})?.*"""
	raw_aka_name = """\s*\(aka ([^\)]+)\)"""
	raw_aka_title_title = """\"?([^\"]*)\"?\s*\((\d{4}|\?{4})(/([\w]*))?\)\s*(\((T?VG?)\))?"""
	raw_title_genre = """\"?([^\"]*)\"?\s*\((\d{4}|\?{4})(/([\w]*))?\)\s*(\((T?VG?)\))?\s*(\w+)"""
	raw_aka_title_alias = """\(aka\s\"?([^\"]*)\"?\s\((\d{4}|\?{4})\)\s*\)\s*(\(([^\)]*)\))?\s*(\(([^\)]*)\))?"""
	# compiled regex patterns for use
	name = re.compile("""
		('.+')?\s*				# nickname (optional, group 1)
		(([^,']*),)?\s*			# last name (optional, group 3)
		([^\(]+)				# first name (required, group 4)
		(\((\w+)\))?			# actor number (optional, group 6)
		""", re.VERBOSE)
	acted_in = re.compile("""
		"?([^"]*?)"?\s			# title (required, group 1) surrounded by quotations if it's a tv show
		\(((\?{4}|\d+)/?(\w+)?).*?\)
								# the year (required, group 3), followed by `/ROMAN_NUMERAL` 
								# (optional, group 4) if multiple in same year
		(\s*\((T?VG?)\))?		# special code (optional, group 6), one of 'TV', 'V', 'VG'
		(\s*\{{1}([^{]*?)(\s*\(\#(\d+)\.(\d+)\)|\([\d-]*\))?\}{1})?
								# episode information: episode title (optional, group 8), within that
								# broadcast date (optional, group 9) or
								# episode series (optional, group 10) and episode number 
								# (optional, group 11) information. The episode series and number are
								# optional within the optional group.
		(\s*(\{{2}SUSPENDED\}{2}))?
								# additional information if suspended (optional, group 13)
		(\s*\(([\w ,.-]*)\))?	# information regarding part (optional, group 15), e.g. 'voice', 'likeness'
		(\s*\[(.*)\])?			# character name (optional, group 17) (surrounded by '[' and ']')
		(\s*\<(\d+)\>)?			# billing position (optional, group 19) (surrounded by '<' and '>')
		""", re.VERBOSE)
	movies = re.compile("""
		"?([^"]*?)"?\s			# title (required, group 1) surrounded by quotations if it's a tv show
		\(((\?{4}|\d+)/?(\w+)?).*?\)
								# the year (required, group 3), followed by `/ROMAN_NUMERAL` 
								# (optional, group 4) if multiple in same year
		(\s*\((T?VG?)\))?		# special code (optional, group 6), one of 'TV', 'V', 'VG'
		(\s*\{{1}([^{]*?)(\s*\(\#(\d+)\.(\d+)\)|\([\d-]*\))?\}{1})?
								# episode information: episode title (optional, group 8), within that
								# broadcast date (optional, group 9) or
								# episode series (optional, group 10) and episode number 
								# (optional, group 11) information. The episode series and number are
								# optional within the optional group.
		(\s*(\{{2}SUSPENDED\}{2}))?
								# additional information if suspended (optional, group 13)
		(\s*((\?{4})|(\d{4})(\-\d{4})?))
								# publish year/year range (optional, group 15)
		""", re.VERBOSE)
	aka_name = re.compile("""
		\s*\(aka ([^\)]+)\)		# alias name (required, group 1)
		""", re.VERBOSE)
	aka_title_alias = re.compile("""
		\(aka\s\"?([^\"]*)\"?\s	# title (required, group 1)
		\((\d{4}|\?{4})\)\s*\)\s*
								# year (required, group 2)
		(\(([^\)]*)\))?\s*		# location (required, group 4)
		(\(([^\)]*)\))?			# reason (optional, group 6)
		""", re.VERBOSE)
	aka_title_title = re.compile("""
		\"?([^\"]*)\"?\s*		# title (required, group 1)
		\((\d{4}|\?{4})			# year (required, group 2)
		(/([\w]*))?\)\s*		# number (optional, group 4)
		(\((T?VG?)\))?			# code (optional, group 6)
		""", re.VERBOSE)
	title_genre = re.compile("""
		\"?([^\"]*)\"?\s*		# title (required, group 1)
		\((\d{4}|\?{4})			# year (required, group 2)
		(/([\w]*))?\)\s*		# number (optional, group 4)
		(\((T?VG?)\))?\s*		# code (optional, group 6)
		(\s*\{{1}([^{]*?)(\s*\(\#(\d+)\.(\d+)\)|\([\d-]*\))?\}{1})?
								# episode information: episode title (optional, group 8), within that
								# broadcast date (optional, group 9) or
								# episode series (optional, group 10) and episode number 
								# (optional, group 11) information. The episode series and number are
								# optional within the optional group.
		(\s*(\{{2}SUSPENDED\}{2}))?
								# additional information if suspended (optional, group 13)
		(\s*([-.'$\w]+))			# genre (required, group 15)
		""", re.VERBOSE)
	title_rating = re.compile("""
		\s*						# leading whitespace
		([\d.*]*)\s*			# rating distribution  incl. *-mark for new movies (required, group 1)
		(\d*)\s*				# number of votes cast (required, group 2)
		([\d.]*)\s*				# average rating (required, group 3)
		"?([^"]*?)"?\s			# title (required, group 4) surrounded by quotations if it's a tv show
		\(((\?{4}|\d+)/?(\w+)?).*?\)
								# the year (required, group 6), followed by `/ROMAN_NUMERAL` 
								# (optional, group 7) if multiple in same year
		(\s*\((T?VG?)\))?		# special code (optional, group 9), one of 'TV', 'V', 'VG'
		(\s*\{{1}([^{]*?)(\s*\(\#(\d+)\.(\d+)\)|\([\d-]*\))?\}{1})?
								# episode information: episode title (optional, group 11), within that
								# broadcast date (optional, group 12) or
								# episode series (optional, group 13) and episode number 
								# (optional, group 14) information. The episode series and number are
								# optional within the optional group.
		""", re.VERBOSE)
	title_business = re.compile("""
		MV:\s+"?([^"]*?)"?\s			# title (required, group 1) surrounded by quotations if it's a tv show
		\(((\?{4}|\d+)/?(\w+)?).*?\)
								# the year (required, group 3), followed by `/ROMAN_NUMERAL` 
								# (optional, group 4) if multiple in same year
		(\s*\((T?VG?)\))?		# special code (optional, group 6), one of 'TV', 'V', 'VG'
		(\s*\{{1}([^{]*?)(\s*\(\#(\d+)\.(\d+)\)|\([\d-]*\))?\}{1})?
								# episode information: episode title (optional, group 8), within that
								# broadcast date (optional, group 9) or
								# episode series (optional, group 10) and episode number 
								# (optional, group 11) information. The episode series and number are
								# optional within the optional group.
		""", re.VERBOSE)
	data_business = re.compile("""
		(BT|GR|OW):				# prefix denoting business data category (required, group 1)
		(\s([A-Z]{3}))			# currency (required, group 3)
		(\s([0-9,]*))			# amount (required, group 5)
		(\s(\(([\w\s-]*)\)))?	# region (required for OW else optional, group 8)
		(\s(\(([\w\s]*)\)))?	# date (required for OW else optional, group 11)
		(\s(\(([\w\s,]*) screens\)))?
								# number of screens (optional, group 14)
		""", re.VERBOSE)
	location = re.compile("""
		"?([^"]*?)"?\s			# title (required, group 1) surrounded by quotations if it's a tv show
		\(((\?{4}|\d+)/?(\w+)?).*?\)
								# the year (required, group 3), followed by `/ROMAN_NUMERAL` 
								# (optional, group 4) if multiple in same year
		(\s*\((T?VG?)\))?		# special code (optional, group 6), one of 'TV', 'V', 'VG'
		(\s*\{{1}([^{]*?)(\s*\(\#(\d+)\.(\d+)\)|\([\d-]*\))?\}{1})?
								# episode information: episode title (optional, group 8), within that
								# broadcast date (optional, group 9) or
								# episode series (optional, group 10) and episode number 
								# (optional, group 11) information. The episode series and number are
								# optional within the optional group.
		(\s*(\{{2}SUSPENDED\}{2}))?
								# additional information if suspended (optional, group 13)
		(\s*(((.*?) - )?		# location name (optional, group 17)
		([^()]*)				# location (required, group 18)
		(\((.*?)\))?))			# location or scene description (optional, group 20)
		""", re.VERBOSE)
	bio_name = re.compile("""
		NM:\s+('.+')?\s*		# nickname (optional, group 1)
		(([^,']*),)?\s*			# last name (optional, group 3)
		([^\(]+)				# first name (required, group 4)
		(\((\w+)\))?			# actor number (optional, group 6)
		""", re.VERBOSE)
	bio_data = re.compile("""
		(DB|DD):				# prefix denoting bio data category (required, group 1)
		(((\s[\d]{1,2})?(\s(\w+))?(\s([\d]{4}))))
								# date as "dd MMMM yyyy" or "yyyy" (required, group 8)
		,([^()]+)?				# location (optional, group 7)
		(\((.*?)\))?			# cause of death (optional, group 9)
		""", re.VERBOSE)
	


# Enum Classes
# Naming conventions if `Table``Column`
class ActorsGender:
	MALE 	= "male"
	FEMALE 	= "female"

class MoviesType:
	TV 	= "TV production"
	V 	= "video production"
	VG 	= "video game"
	M 	= "movie/series"		# there's no code for this, this is default Movie
	@staticmethod
	def from_str(type_string):
		"""converts a type string to a type enum"""
		global type_enum
		if type_string == "V":
			return MoviesType.V
		elif type_string == "VG":
			return MoviesType.VG
		elif type_string == "TV":
			return MoviesType.TV
		else:
			return MoviesType.M


def mk_schema(name, use_dict = False):
	if use_dict:
		return "%s/%s.use_dict.sql" % (Options.schema_dir, name)
	else:
		return "%s/%s.sql" % (Options.schema_dir, name)
	

def mk_cache(name):
	return "%s/%s.cache" % (Options.cache_dir, name)


def mk_drop(name):
	return "%s/%s.drop.sql" % (Options.schema_dir, name)


def executescript(c, of, debug = False):
	"""Executes a SQL script by processing out comments and executing each sql
	command individually."""
	query_list = []
	query_list_candidates = of.readlines()
	for line in query_list_candidates:
		# process out comment lines
		if line.startswith("--"):
			pass
		else:
			if line.strip() != "":
				query_list.append(line.strip())
	query_list = " ".join(query_list).split(';')
	for query in query_list:
		if query.strip():
			if debug:
				print "executescript [status] : executing query:\n\t%s\n" % (query.strip())
			c.execute(query.strip())


def create_tables(c, drop_all = False):
	""" Create Tables
	As per schema (refer to imdb.db.png (image) or imdb.mwb (mysql workbench))
	Things that are chars are instead integers which we can use an in program
	defined enum (integers) since chars are unavailable in sqlite and text would
	be unnecessary."""
	print "create_tables [status]: create tables triggered."
	autoincrement = " autoincrement"
	global Options, Database
	if drop_all:
		print "create_tables [status]: dropping tables initiated."
		if Database.type == DatabaseTypes.SQLITE:
			drop_sql = open(mk_drop("sqlite")).read()
		elif Database.type == DatabaseTypes.MYSQL:
			drop_sql = open(mk_drop("mysql")).read()
		elif Database.type == DatabaseTypes.POSTGRES:
			drop_sql = open(mk_drop("postgres")).read()
		drop_list = drop_sql.split(";")
		for line in drop_list:
			query = line.strip()
			if query:
				c.execute(line)
		print "create_tables [status]: dropping tables complete."
	if Database.type == DatabaseTypes.SQLITE:
		dbf = open(mk_schema("sqlite", Options.use_dict))
		query_list = dbf.read()
		c.executescript(query_list)
	elif Database.type == DatabaseTypes.MYSQL:
		dbf = open(mk_schema("mysql", Options.use_dict))
		executescript(c, dbf)
	elif Database.type == DatabaseTypes.POSTGRES:
		dbf = open(mk_schema("postgres", Options.use_dict))
		executescript(c, dbf)

def quote_escape(string):
	if string:
		return string.replace("\"", "\"\"").replace("\'", "\'\'").replace("\\", "/")
	else:
		return None

# @todo optimize the query building functions by using lists/join
def build_select_query(name, param_dict):
	if not param_dict:
		print "build_select_query: error param dictionary is empty!"
		return None
	select_query = "SELECT id" + name + " FROM " + name + " WHERE "
	for k,v in param_dict.items():
		if v:
			if isinstance(v, StringType):
				if str(v) == "          " or str(v) == "-1":
					select_query += k + " IS NULL AND "
				else:
					select_query += k + "=\'" + quote_escape(v) + "\' AND "
			else:
				select_query += k + "=" + str(v) + " AND "
	# remove trailing AND
	select_query = select_query[:-4] + "LIMIT 1"
	if Options.query_debug:
		print select_query
	return select_query


def build_insert_query(name, param_dict, quote_keys = False):
	global Database
	if not param_dict:
		print "build_insert_query: [error] param dictionary is empty!"
		return None
	insert_query_front = "INSERT INTO " + name + " ("
	insert_query_end = ") VALUES ("
	for k,v in param_dict.items():
		if v:
			if str(v) != "          " and str(v) != "-1":
				if quote_keys:
					insert_query_front += "`" + k + "`, "
				else:
					insert_query_front += k + ", "
				if isinstance(v, StringType):
					# surround with quotes if string
					insert_query_end += "\'" + quote_escape(v) + "\', "
				else:
					insert_query_end +=  str(v)  + ", "
	# remove the trailing comma/spaces with [:-2]
	insert_query = insert_query_front[:-2] + insert_query_end[:-2] + ")"
	if Database.encoding:
		# preconvert to db encoding to avoid db errors, especially from postgres / utf-8
		insert_query = insert_query.decode(Database.encoding, errors='ignore')
	if Options.query_debug:
		print insert_query
	return insert_query

	
def unpack_dict(param_dict):
	return tuple(sorted(param_dict.items()))
	

def select_or_insert(connection_cursor, name, param_dict, skip_lookup = False, supress_output = False):
	"""selects or inserts a row into the database, returning the appropriate id field
	note this makes the assumption the id name is id`table_name` which is the case for the schema
	defined above"""
	global dicts, counts
	row = None
	unpacked = unpack_dict(param_dict)
	select_query = build_select_query(name, param_dict)
	if not skip_lookup:
		if Options.use_dict:
			if name in dicts:
				if unpacked in dicts[name]:
					return dicts[name][unpacked]
			else:
				# run query anyway because not in dicts
				connection_cursor.execute(select_query)
				row = connection_cursor.fetchone()
		else:
			connection_cursor.execute(select_query)
			row = connection_cursor.fetchone()
	if row:
		return row[0]
	else:
		# be careful if you use multi threading here later, will have to lock
		rv = 0
		if Options.use_dict:
			if name in dicts:
				dicts[name][unpacked] = counts[name]
				param_dict["id"+name] = counts[name]
				rv = counts[name]
				counts[name] += 1
		connection_cursor.execute(build_insert_query(name, param_dict))
		if Options.use_dict and not supress_output:
			if name in dicts:
				return rv
		if not supress_output:
			connection_cursor.execute(select_query)
			row = connection_cursor.fetchone()
			if row:
				return row[0]
			else:
				print "select_or_insert: [error] could not insert : ", param_dict
				return None
		else:
			return None


def select(connection_cursor, name, param_dict, dict_only = False):
	"""selects a row from the database, returning the appropriate id field
	note this makes the assumption the id name is id`table_name` which is the 
	case for the schema defined above"""
	global dicts
	unpacked = unpack_dict(param_dict)
	if Options.use_dict:
		if name in dicts:
			if unpacked in dicts[name]:
				return dicts[name][unpacked]
			elif dict_only:
				return None
	select_query = build_select_query(name, param_dict)
	connection_cursor.execute(select_query)
	row = connection_cursor.fetchone()
	if row:
		return row[0]
	else:
		return None

		
def save_dict(name):
	global dicts, counts
	pfd_path = mk_cache("%s.dict"%(name))
	pfc_path = mk_cache("%s.count"%(name))
	pfd = pickle.Pickler(open(pfd_path, "wb"))
	pfd.fast = True
	pfd.dump(dicts[name])	
	pfc = pickle.Pickler(open(pfc_path, "wb"))
	pfc.fast = True
	pfc.dump(counts[name])
	

def load_dict(name, force_load = False):
	global dicts, counts
	if len(dicts[name]) > 0 and not force_load:
		return False
	else:
		pfd_path = mk_cache("%s.dict"%(name))
		pfc_path = mk_cache("%s.count"%(name))
		if os.path.exists(pfd_path) and os.path.exists(pfc_path):
			pfd = pickle.Unpickler(open(pfd_path, "rb"))
			dicts[name] = pfd.load()
			pfc = pickle.Unpickler(open(pfc_path, "rb"))
			counts[name] = pfc.load()
			return True
		else:
			return False


def connect_db(db, create_tables_enabled = False):
	# Create tables enabled is there to provide a hard switch to stopping
	# tables from being created, in the case of getting a connection to do
	# indexing we don't want to accidently clear the database
	# Initialize Database
	conn = None
	c = None
	if db.type == DatabaseTypes.SQLITE:
		sqlite3 = __import__("sqlite3")
		exists = os.path.exists(Database.database)
		# Since it's sqlite we just remove the old file, if this was an actual
		# db we would drop from all the tables
		if db.clear_old_db and exists:
			os.remove(db.database)
		conn = sqlite3.connect(db.database)
		c = conn.cursor()
		if (db.clear_old_db or not exists) and create_tables_enabled:
			create_tables(c)
	elif db.type == DatabaseTypes.MYSQL:
		MySQLdb = __import__("MySQLdb")
		conn = MySQLdb.connect(host = db.host, db = db.database, user = db.user, passwd = db.password)
		c = conn.cursor()
		if create_tables_enabled:		
			create_tables(c, drop_all = db.clear_old_db)
	elif db.type == DatabaseTypes.POSTGRES:
		psycopg2 = __import__("psycopg2")
		conn = psycopg2.connect(host = db.host, database = db.database, user = db.user, password = db.password)
		c = conn.cursor()
		if create_tables_enabled:
			create_tables(c, drop_all = db.clear_old_db)
	else:
		print "__main__ [error]: unknown database type #%d." % (db.type)
		quit()
	return conn, c


if __name__ == "__main__":
	if Options.show_time:
		start = time.clock()
	if Options.use_native:
		parse = __import__("native.parse").parse
	if Options.use_dict:
		dicts["people"] = {}
		dicts["productions"] = {}
		dicts["ratings"] = {}
		dicts["business"] = {}
		dicts["locations"] = {}
		dicts["biographies"] = {}
		counts["people"] = 1
		counts["productions"] = 1
		counts["ratings"] = 1
		counts["business"] = 1
		counts["locations"] = 1
		counts["biographies"] = 1
	
	process_flags = { 
		"people": False,
		"productions": False,
		"ratings": True, 
		"business": True, 
		"locations": True, 
		"biographies": True
	}
	
	conn, c = connect_db(Database, create_tables_enabled = True)
	
	if Options.use_native:
		print "__main__ [status]: using native c parsing code."
	else:
		print "__main__ [status]: using python regex parsing code."
	# Read in data from raw list files
	
	#
	# Actors/Actresses List File
	# Dependencies : None
	# Updates : Actors, Movies, Series
	#
	if process_flags["people"] or Options.proc_all:
		files_to_process = ["actresses", "actors"]
		for file in files_to_process:
			current_file = mk(file)
			current_gender = ActorsGender.MALE if file=="actors" else ActorsGender.FEMALE
			f = open(current_file)
			# Skip over the information at the beginning and get to the actual data list
			line_number = 1 
			line = f.readline()
			while(line and line != "----			------\n"):
				line = f.readline()
				line_number += 1
			new_actor = True
			for line in f:
				if Options.show_progress and (line_number%Options.progress_count == 0):
					print "__main__ [status]: processing line", line_number
				if Options.commit_count != -1 and (line_number%Options.commit_count == 0):
					conn.commit()
				line_number += 1
				if line == "\n":
					new_actor = True
					continue
				elif line == "-----------------------------------------------------------------------------\n":
					# this is the last valid line before there is a bunch of junk
					break
				if new_actor:
					# reset all names to defaults
					current_lastname = ""
					current_firstname = ""
					current_nickname = ""
					current_number = 1
					# use regex to parse out name parts
					name = line.split('\t')[0]
					m = re.match(ParseRegexes.name, name)
					if not m:
						print("__main__ [error]: while processing " + current_file + "[" + str(line_number) + "]: " + "invalid name : " + name)
					else:
						current_nickname = m.group(1).strip() if m.group(1) else None
						current_lastname = m.group(3).strip() if m.group(3) else None
						current_firstname = m.group(4).strip() # only required field
						current_number = (rntoi(m.group(6)) + 1) if m.group(6) else 1
					current_actor = select_or_insert(c, "people", {"lastname" : current_lastname, "firstname" : current_firstname, "nickname": current_nickname, "gender": current_gender, "number": current_number}, skip_lookup = True)
				# process line
				if new_actor:
					new_actor = False
					to_process = line.split('\t')[-1].strip() # use the rest of the line if we read in actor data
				else:
					to_process = line.strip()
				good = False
				n = None
				n = re.match(ParseRegexes.acted_in, to_process)
				if n:
					good = True
					title = n.group(1).strip()
					try:
						if n.group(3).strip() == "????":
							year = -1
						else:					
							year = int(n.group(3)) # there always has to be a year
					except ValueError:
						print("__main__ [error]: while processing " + current_file + "[" + str(line_number) + "]: " +
						"year not valid integer value: " + to_process)
						quit()
					number = (rntoi(n.group(4)) + 1) if n.group(4) else 1 # in roman numerals, needs to be converted
					special_code = MoviesType.from_str(n.group(6))
					broadcast_date = n.group(9).replace("(", "").replace(")","") if n.group(9) else "          "
					episode_title = n.group(8).strip() if n.group(8) else broadcast_date
					episode_series = int(n.group(10)) if n.group(10) else -1
					episode_number = int(n.group(11)) if n.group(11) else -1
					special_information = n.group(15).strip() if n.group(15) else None
					character_name = n.group(17).strip() if n.group(17) else None
					billing_position = int(n.group(19)) if n.group(19) else None
				if good:
					current_production = select_or_insert(c, "productions", {"title": title, "year": year, "number": number, "productions_type": special_code, "episode_title": episode_title, "season": episode_series, "episode_number": episode_number})
					# insert into the db the acted in information
					select_or_insert(c, "people_x_productions", {"idproductions": current_production, "idpeople": current_actor, "character": character_name, "billing_position": billing_position, "special_information": special_information}, skip_lookup = True, supress_output = True)
				else:
					print("__main__ [error]: while processing" + current_file + "[" + str(line_number) + "]: " + "invalid info: " + to_process)
					if Options.use_native:
						print "parsed as: ", n
				# raw_input("Press Enter to continue...")
			f.close()
			conn.commit()
			print "__main__ [status]: processing of", current_file, "complete. (last pid:", current_production, ")"
		if Options.use_cache and Options.use_dict:
			save_dict("people")
			save_dict("productions")
	
	
	#
	# Productions List
	# Dependencies : Productions
	# Updates : Productions
	#
	if process_flags["productions"] or Options.proc_all:
		current_file = mk("movies")
		if Options.use_cache and Options.use_dict:
			load_dict("productions")
		f = open(current_file)
		line_number = 1 
		# Skip over the information at the beginning and get to the actual data list
		line = f.readline()
		while(line and line != "===========\n"):
			line = f.readline()
			line_number += 1
		f.readline() # skip over the blank line inbetween movie list and header
		line_number += 1
		for line in f:
			if Options.show_progress and (line_number%Options.progress_count == 0):
				print "__main__ [status]: processing line", line_number
			if Options.commit_count != -1 and (line_number%Options.commit_count == 0):
				conn.commit()
			line_number += 1
			if line == 	"--------------------------------------------------------------------------------\n":
				# this is the last valid line before there is a bunch of junk
				break
			m = re.match(ParseRegexes.movies, line)
			if not m:
				print("__main__ [error]: while processing " + current_file + "[" + str(line_number) + "]: " +
				"invalid movie : " + line)
			else:
				title = m.group(1).strip()
				try:
					if m.group(3).strip() == "????":
						year = -1
					else:					
						year = int(m.group(3)) # there always has to be a year
				except ValueError:
					print("__main__ [error]: while processing " + current_file + "[" + str(line_number) + "]: " +
					"year not valid integer value: " + line)
					quit()
				number = (rntoi(m.group(4)) + 1) if m.group(4) else 1 # in roman numerals, needs to be converted
				special_code = MoviesType.from_str(m.group(6))
				broadcast_date = m.group(9).replace("(", "").replace(")","") if m.group(9) else "          "
				episode_title = m.group(8).strip() if m.group(8) else broadcast_date
				episode_series = int(m.group(10)) if m.group(10) else -1
				episode_number = int(m.group(11)) if m.group(11) else -1
				current_production = select_or_insert(c, "productions", {"title": title, "year": year, "number": number, "productions_type": special_code, "episode_title": episode_title, "season": episode_series, "episode_number": episode_number}, supress_output = True)
			# raw_input("Press Enter to continue...")
		f.close()
		conn.commit()
		if Options.use_cache and Options.use_dict:
			save_dict("movies")
			save_dict("series")
		print "__main__ [status]: processing of", current_file, "complete. (last pid:", current_production, ")"

		
	#
	# Productions Ratings
	# Dependencies : Productions
	# Updates : None
	#
	if process_flags["ratings"] or Options.proc_all:
		current_file = mk("ratings")
		if Options.use_cache and Options.use_dict:
			print "__main__ [status]: loading productions cache file."
			if load_dict("productions"):
				print "__main__ [status]: loaded productions dictionary cache file."
			else:
				print "__main__ [warning]: failed to load productions dictionary cache file."
		f = open(current_file)
		# Skip over the information at the beginning and get to the actual data list
		line_number = 1 
		line = f.readline()
		while(line and line != "MOVIE RATINGS REPORT\n"):
			line = f.readline()
			line_number += 1
		line = f.readline() # read over the seperator line
		line = f.readline() # read over the seperator line
		line_number += 1
		for line in f:
			if Options.show_progress and (line_number%Options.progress_count == 0):
				print "__main__ [status]: processing line", line_number
			if Options.commit_count != -1 and (line_number%Options.commit_count == 0):
				conn.commit()
			line_number += 1
			if line == "\n":
				continue
			elif line == "------------------------------------------------------------------------------\n":
					# this is the last valid line before there is a bunch of junk
					break
			else:
				# reset all info to defaults
				current_title = ""
				current_year = -1
				current_number = 1
				current_special_code = MoviesType.M
				current_distribution = ""
				current_votes = -1
				current_rating = -1
				episode_title = ""
				episode_series = -1
				episode_number = -1
				# use regex to parse out movie title parts
				title = line.strip()
				m = re.match(ParseRegexes.title_rating, title)
				if m:
					current_title = m.group(4).strip()
					if m.group(6) and m.group(6).strip() == "????":
						current_year = -1
					elif m.group(6):
						current_year = int(m.group(6))
					current_number = (rntoi(m.group(7)) + 1) if m.group(7) else 1
					current_special_code = MoviesType.from_str(m.group(9))
					broadcast_date = m.group(12).replace("(", "").replace(")","") if m.group(12) else "          "
					episode_title = m.group(11).strip() if m.group(11) else broadcast_date
					episode_series = int(m.group(13)) if m.group(13) else -1
					episode_number = int(m.group(14)) if m.group(14) else -1
					current_distribution = m.group(1).strip() if m.group(1) else None
					current_votes = m.group(2)
					current_rating = m.group(3)
					dict_only_search = True if Options.use_dict else False
					current_production = select(c, "productions", {"title": current_title, "year": current_year, "number": current_number, "productions_type": current_special_code, "episode_title": episode_title, "season": episode_series, "episode_number": episode_number}, dict_only_search)
					if current_production:
						select_or_insert(c, "productions_ratings", {"idproductions": current_production, "distribution": current_distribution, "votes": current_votes, "rating": current_rating}, skip_lookup = True, supress_output = True)
					else:
						pass
						# print("__main__ [error]: while processing %s [%d]: production/rating lookup failed: %s" % (current_file, line_number, title))
				else:
					print("__main__ [error]: while processing %s [%d]: invalid title/rating: %s" % (current_file, line_number, title))
			# raw_input("Press Enter to continue...")
		f.close()
		conn.commit()
		if Options.use_cache and Options.use_dict:
			save_dict("ratings")
		print "__main__ [status]: processing of", current_file, "complete. (last pid:", current_production, ")"

		
	#
	# Productions Business Data
	# Dependencies : Productions
	# Updates : None
	#
	if process_flags["business"] or Options.proc_all:
		current_file = mk("business")
		if Options.use_cache and Options.use_dict:
			print "__main__ [status]: loading productions cache file."
			if load_dict("productions"):
				print "__main__ [status]: loaded productions dictionary cache file."
			else:
				print "__main__ [warning]: failed to load productions dictionary cache file."
		f = open(current_file)
		# Skip over the information at the beginning and get to the actual data list
		line_number = 1 
		line = f.readline()
		while(line and line != "BUSINESS LIST\n"):
			line = f.readline()
			line_number += 1
		line = f.readline() # read over the seperator line
		line = f.readline() # read over the seperator line
		line_number += 1
		current_movie = None
		new_movie = True
		is_valid = True
		for line in f:
			if Options.show_progress and (line_number%Options.progress_count == 0):
				print "__main__ [status]: processing line", line_number
			if Options.commit_count != -1 and (line_number%Options.commit_count == 0):
				conn.commit()
			line_number += 1
			if line == "-------------------------------------------------------------------------------\n":
				new_movie = True
				continue
			elif line == "\n":
				continue
			if new_movie:
				# reset all info to defaults
				current_title = ""
				current_year = -1
				current_number = 1
				current_special_code = MoviesType.M
				episode_title = ""
				episode_series = -1
				episode_number = -1
				type = ""
				currency = ""
				amount = -1
				region = ""
				date = ""
				screens = -1
				episode_title = ""
				episode_series = -1
				episode_number = -1
				# use regex to parse out movie title parts
				title = line.strip()
				m = re.match(ParseRegexes.title_business, title)
				if m:
					current_title = m.group(1).strip()
					if m.group(3) and m.group(3).strip() == "????":
						current_year = -1
					elif m.group(3):
						current_year = int(m.group(3))
					current_number = (rntoi(m.group(4)) + 1) if m.group(4) else 1
					current_special_code = MoviesType.from_str(m.group(6))
					broadcast_date = m.group(9).replace("(", "").replace(")","") if m.group(9) else "          "
					episode_title = m.group(8).strip() if m.group(8) else broadcast_date
					episode_series = int(m.group(10)) if m.group(10) else -1
					episode_number = int(m.group(11)) if m.group(11) else -1
					dict_only_search = True if Options.use_dict else False
					current_production = select(c, "productions", {"title": current_title, "year": current_year, "number": current_number, "productions_type": current_special_code, "episode_title": episode_title, "season": episode_series, "episode_number": episode_number}, dict_only_search)
				if current_production:
					is_valid = True
					new_movie = False
					continue
				else:
					is_valid = False
					new_movie = False
					continue
			# process line
			if is_valid:
				to_process = line.strip()
				n = re.match(ParseRegexes.data_business, to_process)
				if n:
					type = n.group(1).strip()
					currency = n.group(3).strip() if n.group(3) else "USD"
					amount = int(re.sub(",", "", n.group(5)))
					amount = -1 if amount > 9223372036854775807 else amount
					region = n.group(8).strip() if n.group(8) else None
					date = n.group(11).strip() if n.group(11) else "31 December 2100"
					screens = int(re.sub(",", "", n.group(14))) if n.group(14) else -1
					if type == "BT":
						type = "budget"
					elif type == "GR":
						type = "box office gross"
					elif type == "OW":
						type = "opening weekend box office take"
					select_or_insert(c, "productions_business", {"idproductions": current_production, "business_type": type, "currency": currency, "amount": amount, "region": region, "date": date, "screens": screens}, skip_lookup = True, supress_output = True)
				else:
					pass
			# raw_input("Press Enter to continue...")
		f.close()
		conn.commit()
		if Options.use_cache and Options.use_dict:
			save_dict("business")
		print "__main__ [status]: processing of", current_file, "complete. (last pid:", current_production, ")"

		
	#
	# Productions Locations
	# Dependencies : Productions
	# Updates : None
	#
	if process_flags["locations"] or Options.proc_all:
		current_file = mk("locations")
		if Options.use_cache and Options.use_dict:
			print "__main__ [status]: loading productions cache file."
			if load_dict("productions"):
				print "__main__ [status]: loaded productions dictionary cache file."
			else:
				print "__main__ [warning]: failed to load productions dictionary cache file."
		f = open(current_file)
		# Skip over the information at the beginning and get to the actual data list
		line_number = 1 
		line = f.readline()
		while(line and line != "LOCATIONS LIST\n"):
			line = f.readline()
			line_number += 1
		line = f.readline() # read over the seperator line
		line = f.readline() # read over the seperator line
		line_number += 1
		for line in f:
			if Options.show_progress and (line_number%Options.progress_count == 0):
				print "__main__ [status]: processing line", line_number
			if Options.commit_count != -1 and (line_number%Options.commit_count == 0):
				conn.commit()
			line_number += 1
			if line == "\n":
				continue
			elif line == "-------------------------------------------------------------------------------\n":
					# this is the last valid line before there is a bunch of junk
					break
			else:
				# reset all info to defaults
				current_title = ""
				current_year = -1
				current_number = 1
				current_special_code = MoviesType.M
				episode_title = "          "
				episode_series = -1
				episode_number = -1
				location_name = ""
				location = ""
				location_info = ""
				# use regex to parse out movie title parts
				title = line.strip()
				m = re.match(ParseRegexes.location, title)
				if m:
					current_title = m.group(1).strip()
					if m.group(3) and m.group(3).strip() == "????":
						current_year = -1
					elif m.group(3):
						current_year = int(m.group(3))
					current_number = (rntoi(m.group(4)) + 1) if m.group(4) else 1
					current_special_code = MoviesType.from_str(m.group(6))
					broadcast_date = m.group(9).replace("(", "").replace(")","") if m.group(9) else "          "
					episode_title = m.group(8).strip() if m.group(8) else broadcast_date
					episode_series = int(m.group(10)) if m.group(10) else -1
					episode_number = int(m.group(11)) if m.group(11) else -1
					location_name = m.group(17).strip() if m.group(17) else None
					location = m.group(18).strip() if m.group(18) else None
					location_info = m.group(20).strip() if m.group(20) else None
					dict_only_search = True if Options.use_dict else False
					current_production = select(c, "productions", {"title": current_title, "year": current_year, "number": current_number, "productions_type": current_special_code, "episode_title": episode_title, "season": episode_series, "episode_number": episode_number}, dict_only_search)
					if current_production:
						select_or_insert(c, "productions_locations", {"idproductions": current_production, "location_name": location_name, "location": location, "location_info": location_info}, skip_lookup = True, supress_output = True)
					else:
						print("__main__ [error]: while processing %s [%d]: production/location lookup failed: %s" % (current_file, line_number, title))
				else:
					print("__main__ [error]: while processing %s [%d]: invalid title/location: %s" % (current_file, line_number, title))
			# raw_input("Press Enter to continue...")
		f.close()
		conn.commit()
		if Options.use_cache and Options.use_dict:
			save_dict("locations")
		print "__main__ [status]: processing of", current_file, "complete. (last pid:", current_production, ")"
	
	
	#
	# People's Biography Data
	# Dependencies : People
	# Updates : None
	#
	if process_flags["biographies"] or Options.proc_all:
		current_file = mk("biographies")
		if Options.use_cache and Options.use_dict:
			print "__main__ [status]: loading people cache file."
			if load_dict("people"):
				print "__main__ [status]: loaded people dictionary cache file."
			else:
				print "__main__ [warning]: failed to load people dictionary cache file."
		f = open(current_file)
		# Skip over the information at the beginning and get to the actual data list
		line_number = 1 
		line = f.readline()
		while(line and line != "BIOGRAPHY LIST\n"):
			line = f.readline()
			line_number += 1
		line = f.readline() # read over the seperator line
		line = f.readline() # read over the seperator line
		line_number += 1
		current_person = None
		new_bio = True
		is_valid = True
		for line in f:
			if Options.show_progress and (line_number%Options.progress_count == 0):
				print "__main__ [status]: processing line", line_number
			if Options.commit_count != -1 and (line_number%Options.commit_count == 0):
				conn.commit()
			line_number += 1
			if line == "-------------------------------------------------------------------------------\n":
				new_bio = True
				continue
			elif line == "\n":
				continue
			if new_bio:
				# reset all names to defaults
				current_lastname = ""
				current_firstname = ""
				current_nickname = ""
				current_number = 1
				# use regex to parse out name parts
				name = line.strip()
				m = re.match(ParseRegexes.bio_name, name)
				if not m:
					print("__main__ [error]: while processing " + current_file + "[" + str(line_number) + "]: " +
					"invalid name : " + name)
				else:
					current_nickname = m.group(1).strip() if m.group(1) else None
					current_lastname = m.group(3).strip() if m.group(3) else None
					current_firstname = m.group(4).strip()
					current_number = (rntoi(m.group(6)) + 1) if m.group(6) else 1
				# search for actor/actress
				# try male default
				current_person = None
				dict_only_search = True if Options.use_dict else False
				current_person = select(c, "people", {"lastname" : current_lastname, "firstname" : current_firstname, "nickname": current_nickname, "gender": ActorsGender.MALE, "number": current_number}, dict_only_search)
				if not current_person:
					# try female
					current_person = select(c, "people", {"lastname" : current_lastname, "firstname" : current_firstname, "nickname": current_nickname, "gender": ActorsGender.FEMALE, "number": current_number}, dict_only_search)
				new_bio = False
				if current_person:
					is_valid = True
					continue
				else:
					is_valid = False
					continue
			# process line
			if is_valid:
				current_type = None
				current_date = None
				current_location = None
				current_cod = None
				to_process = line.strip()
				n = re.match(ParseRegexes.bio_data, to_process)
				if n:
					current_type = n.group(1).strip()
					current_date = n.group(8).strip()
					current_location = n.group(9).strip() if n.group(9) else None
					current_cod = n.group(11).strip() if n.group(11) else None
					if current_type == "DB":
						current_type = "born"
					elif current_type == "DD":
						current_type = "died"
					select_or_insert(c, "biographies", {"idpeople": current_person, "biography_type": current_type, "biography_date": current_date, "biography_location": current_location, "cause_of_death": current_cod}, skip_lookup = True)
				else:
					pass
		f.close()
		conn.commit()
		if Options.use_cache and Options.use_dict:
			save_dict("biographies")
		print "__main__ [status]: processing of", current_file, "complete."
		
		
		
	c.close()
	conn.close()
	if Options.show_time:
		print "__main__ [status]: total time:", time.clock() - start, "seconds."
