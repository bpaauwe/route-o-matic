CREATE TABLE routes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	title TEXT NOT NULL,
	date TEXT,
	owner TEXT NOT NULL,
	description TEXT,
	route TEXT,
	footer TEXT,
	info TEXT,
	map_url, TEXT,
	map, BLOB,
	distance REAL,
	duration TEXT,
	rating INTEGER,
	public INTEGER
	);
