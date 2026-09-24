DROP TABLE IF EXISTS country_alliances CASCADE;
DROP TABLE IF EXISTS classes CASCADE;
DROP TABLE IF EXISTS ships CASCADE;
DROP TABLE IF EXISTS captains_retired CASCADE;
DROP TABLE IF EXISTS battles CASCADE;
DROP TABLE IF EXISTS outcomes CASCADE;

CREATE TABLE country_alliances(
	country VARCHAR(20) PRIMARY KEY,
	alliance VARCHAR(2) NOT NULL,
	entry DATE NOT NULL,
	leaving DATE
);

CREATE TABLE classes(
	id SERIAL PRIMARY KEY, 
	class VARCHAR(50) UNIQUE NOT NULL,
	type VARCHAR(2) NOT NULL,
	country VARCHAR(20) NOT NULL REFERENCES country_alliances(country),
	numGuns SMALLINT,
	bore FLOAT4,
	displacement INTEGER
);

COMMENT ON TABLE classes IS 'Таблица классов кораблей - могут быть названы в честь первого корабля проекта';
COMMENT ON COLUMN classes.type IS 'Тип корабля: линкор, линейный крейсер, тяжёлый крейсер, лёгкий крейсер, эсминец, авианосец,
подводная лодка - bs, bc, hc, lc, d, ac, sb';

CREATE TABLE ships(
	id SERIAL PRIMARY KEY, 
	name VARCHAR(50) UNIQUE NOT NULL,
	class INTEGER NOT NULL REFERENCES classes(id),
	launched DATE NOT NULL,
	captain VARCHAR(50) NOT NULL
);

CREATE TABLE captains_retired(
	captain VARCHAR(50) NOT NULL,
	ship INTEGER NOT NULL REFERENCES ships(id),
	retire_date DATE NOT NULL
);

COMMENT ON TABLE country_alliances IS 'Таблица со странами-участницами и их коалициями';
COMMENT ON COLUMN country_alliances.alliance IS 'un - Антигитлеровская коалиция, ax - Ось';

CREATE TABLE battles(
	id SERIAL PRIMARY KEY,
	name VARCHAR(50) NOT NULL,
	battle_end DATE NOT NULL,
	winner VARCHAR(20) REFERENCES country_alliances(country)
);

CREATE TABLE outcomes(
	battle INTEGER REFERENCES battles(id),
	ship INTEGER REFERENCES ships(id),
	result VARCHAR(10) NOT NULL
);


