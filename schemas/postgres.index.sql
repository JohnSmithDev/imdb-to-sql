-- people_x_movies
CREATE INDEX "PEOPLE_X_PRODUCTIONS_IDPRODUCTIONS_INDEX" ON people_x_productions USING btree (idproductions);
CREATE INDEX "PEOPLE_X_PRODUCTIONS_IDPEOPLE_INDEX" ON people_x_productions USING btree (idpeople);

-- people
CREATE INDEX "PEOPLE_LASTNAME_INDEX" ON people USING btree (lastname);
CREATE INDEX "PEOPLE_FIRSTNAME_INDEX" ON people USING btree (firstname);
CREATE INDEX "PEOPLE_NICKNAME_INDEX" ON people USING btree (nickname);
CREATE INDEX "PEOPLE_GENDER_INDEX" ON people USING btree (gender);

-- productions
CREATE INDEX "PRODUCTIONS_TITLE_INDEX" on productions USING btree (title);
CREATE INDEX "PRODUCTIONS_YEAR_INDEX" on productions USING btree (year);
CREATE INDEX "PRODUCTIONS_NUMBER_INDEX" on productions USING btree (number);
CREATE INDEX "PRODUCTIONS_TYPE_INDEX" on productions USING btree (productions_type);
CREATE INDEX "PRODUCTIONS_EPISODE_TITLE_INDEX" on productions USING btree (episode_title);
CREATE INDEX "PRODUCTIONS_SEASON_INDEX" on productions USING btree (season);
CREATE INDEX "PRODUCTIONS_EPISODE_NUMBER_INDEX" on productions USING btree (episode_number);

-- productions ratings
CREATE INDEX "PRODUCTIONS_RATINGS_IDPRODUCTIONS_INDEX" on productions_ratings USING btree (idproductions);

-- productions business
CREATE INDEX "PRODUCTIONS_BUSINESS_IDPRODUCTIONS_INDEX" on productions_business USING btree (idproductions);
CREATE INDEX "PRODUCTIONS_BUSINESS_BUSINESS_TYPE_INDEX" on productions_business USING btree (business_type);
CREATE INDEX "PRODUCTIONS_BUSINESS_CURRENCY_INDEX" on productions_business USING btree (currency);
CREATE INDEX "PRODUCTIONS_BUSINESS_REGION_INDEX" on productions_business USING btree (region);

-- productions locations
CREATE INDEX "PRODUCTIONS_LOCATIONS_IDPRODUCTIONS_INDEX" on productions_locations USING btree (idproductions);
CREATE INDEX "PRODUCTIONS_LOCATIONS_LOCATION_INDEX" on productions_locations USING btree (location);

-- biographies
CREATE INDEX "BIOGRAPHIES_IDPEOPLE_INDEX" on biographies USING btree (idpeople);
CREATE INDEX "BIOGRAPHIES_BIOGRAPHY_TYPE_INDEX" on biographies USING btree (biography_type);
CREATE INDEX "BIOGRAPHIES_BIOGRAPHY_LOCATION_INDEX" on biographies USING btree (biography_location);
CREATE INDEX "BIOGRAPHIES_CAUSE_OF_DEATH_INDEX" on biographies USING btree (cause_of_death);
