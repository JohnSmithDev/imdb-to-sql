SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;




--
-- Name: people; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--
CREATE TABLE people (
    idpeople integer NOT NULL,
    lastname text,
    firstname text,
    nickname text,
    gender text,
    number integer
);

--
-- Name: people_idpeople_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE people_idpeople_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: people_idpeople_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE people_idpeople_seq OWNED BY people.idpeople;

--
-- Name: idpeople; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE people ALTER COLUMN idpeople SET DEFAULT nextval('people_idpeople_seq'::regclass);

--
-- Name: people_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--
ALTER TABLE ONLY people
    ADD CONSTRAINT people_pkey PRIMARY KEY (idpeople);




--
-- Name: people_x_productions; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--
CREATE TABLE people_x_productions (
    idpeople_x_productions integer NOT NULL,
	idproductions integer NOT NULL,
    idpeople integer NOT NULL,
    "character" text,
    billing_position integer, 
	special_information text
);

--
-- Name: people_x_productions_idpeople_x_productions_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE people_x_productions_idpeople_x_productions_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: people_x_productions_idpeople_x_productions_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE people_x_productions_idpeople_x_productions_seq OWNED BY people_x_productions.idpeople_x_productions;

--
-- Name: idpeople_x_productions; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE people_x_productions ALTER COLUMN idpeople_x_productions SET DEFAULT nextval('people_x_productions_idpeople_x_productions_seq'::regclass);

--
-- Name: people_x_productions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--
ALTER TABLE ONLY people_x_productions
    ADD CONSTRAINT people_x_productions_pkey PRIMARY KEY (idpeople_x_productions);

	


--
-- Name: productions; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--
CREATE TABLE productions (
    idproductions integer NOT NULL,
	title text,
    year integer,
    number integer,
    productions_type text, 
	episode_title text,
    season integer,
    episode_number integer
);

--
-- Name: productions_idproductions_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE productions_idproductions_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: productions_idproductions_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE productions_idproductions_seq OWNED BY productions.idproductions;

--
-- Name: idproductions; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE productions ALTER COLUMN idproductions SET DEFAULT nextval('productions_idproductions_seq'::regclass);

--
-- Name: productions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--
ALTER TABLE ONLY productions
    ADD CONSTRAINT productions_pkey PRIMARY KEY (idproductions);

	


-- Name: productions_ratings; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--
--
CREATE TABLE productions_ratings (
    idproductions_ratings integer NOT NULL,
    idproductions integer NOT NULL,
	distribution text, 
	votes int, 
	rating double precision
);

--
-- Name: productions_ratings_idproductions_ratings_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE productions_ratings_idproductions_ratings_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: productions_ratings_idproductions_ratings_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE productions_ratings_idproductions_ratings_seq OWNED BY productions_ratings.idproductions_ratings;

--
-- Name: idproductions_ratings; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE productions_ratings ALTER COLUMN idproductions_ratings SET DEFAULT nextval('productions_ratings_idproductions_ratings_seq'::regclass);

--
-- Name: productions_ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--
ALTER TABLE ONLY productions_ratings
    ADD CONSTRAINT productions_ratings_pkey PRIMARY KEY (idproductions_ratings);




-- Name: productions_business; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--
--
CREATE TABLE productions_business (
    idproductions_business integer NOT NULL,
    idproductions integer NOT NULL,
	business_type text,
	amount bigint,
	currency text,
	region text,
	date text,
	screens integer
);

--
-- Name: productions_business_idproductions_business_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE productions_business_idproductions_business_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: productions_business_idproductions_business_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE productions_business_idproductions_business_seq OWNED BY productions_business.idproductions_business;

--
-- Name: idproductions_business; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE productions_business ALTER COLUMN idproductions_business SET DEFAULT nextval('productions_business_idproductions_business_seq'::regclass);

--
-- Name: productions_business_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--
ALTER TABLE ONLY productions_business
    ADD CONSTRAINT productions_business_pkey PRIMARY KEY (idproductions_business);

	


-- Name: productions_locations; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--
--
CREATE TABLE productions_locations (
    idproductions_locations integer NOT NULL,
    idproductions integer NOT NULL,
	location_name text,
	location text,
	location_info text
);

--
-- Name: productions_locations_idproductions_locations_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE productions_locations_idproductions_locations_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: productions_locations_idproductions_locations_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE productions_locations_idproductions_locations_seq OWNED BY productions_locations.idproductions_locations;

--
-- Name: idproductions_locations; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE productions_locations ALTER COLUMN idproductions_locations SET DEFAULT nextval('productions_locations_idproductions_locations_seq'::regclass);

--
-- Name: productions_locations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--
ALTER TABLE ONLY productions_locations
    ADD CONSTRAINT productions_locations_pkey PRIMARY KEY (idproductions_locations);

	


-- Name: biographies; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--
--
CREATE TABLE biographies (
    idbiographies integer NOT NULL,
    idpeople integer,
	biography_type text,
	biography_date text,
	biography_location text,
	cause_of_death text
);

--
-- Name: biographies_idbiographies_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE biographies_idbiographies_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: biographies_idbiographies_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE biographies_idbiographies_seq OWNED BY biographies.idbiographies;

--
-- Name: idbiographies; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE biographies ALTER COLUMN idbiographies SET DEFAULT nextval('biographies_idbiographies_seq'::regclass);

--
-- Name: biographies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--
ALTER TABLE ONLY biographies
    ADD CONSTRAINT biographies_pkey PRIMARY KEY (idbiographies);




--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--
REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;