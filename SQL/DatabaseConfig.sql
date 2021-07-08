--   +--------+
--~~ | Tables |
--   +--------+
create table action_types(
	id serial primary key,
	code varchar(10),
	description varchar(255),
	created timestamp without time zone
);
alter table action_types alter column created set default now()::timestamp;

CREATE TABLE activities(
    db_id serial primary key,
    achievement_count bigint,
    athlete text,
    athlete_count bigint,
    attribute_map text,
    average_speed numeric,
    average_watts numeric,
    comment_count bigint,
    commute boolean,
    device_watts text,
    discriminator text,
    distance numeric,
    elapsed_time bigint,
    elev_high numeric,
    elev_low numeric,
    end_latlng text,
    external_id text,
    flagged boolean,
    gear_id text,
    has_kudoed boolean,
    id bigint,
    kilojoules numeric,
    kudos_count bigint,
    manual boolean,
    map text,
    max_speed numeric,
    max_watts numeric,
    moving_time bigint,
    name text,
    photo_count bigint,
    private boolean,
    start_date timestamp without time zone,
    start_date_local timestamp without time zone,
    start_latlng text,
    swagger_types text,
    timezone text,
    total_elevation_gain numeric,
    total_photo_count bigint,
    trainer boolean,
    type text,
    upload_id bigint,
    weighted_average_watts numeric,
    workout_type numeric
)

--**** AT LEAST TEMPORARILY MADE THIS TABLE ALL VARCHAR(255)******
create table activities_streams(
    db_id serial primary key,
	time bigint,
	distance numeric,
	altitude numeric,
	velocity_smooth numeric,
	heartrate bigint,
	cadence bigint,
	watts bigint,
	moving boolean,
	grade_smooth numeric,
	lat varchar(100),
	lng varchar(100),
	activity_id bigint
)

create table error_codes(
	id serial primary key,
	code varchar(10),
	description varchar(255),
	created timestamp without time zone
);
alter table error_codes alter column created set default now()::timestamp;

create table logs(
	id serial primary key,
	timestamp timestamp without time zone,
	who varchar(255),
	status varchar(255),
	source varchar(255),
	action_type varchar(255),
	"resource" varchar(255),
	record_id varchar(255)
);
alter table logs alter column timestamp set default now()::timestamp;

create table logs_archive(
	id int primary key,
	timestamp timestamp without time zone,
	who varchar(30),
	error_code integer,
	action_type int,
	message varchar(100)
);
-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
--   +-------+
--~~ | Views |
--   +-------+
create view v_api_hits as


-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
--   +-----------+
--~~ | Functions |
--   +-----------+

-- Hits need to be < 100 / 15 minute interval
create function CalculateApiHits15mins()
  returns integer as $$
declare 
	hits integer:= 0;
	min_min integer:= 15;
	max_min integer:= 30;
	curr_min integer:= extract(minute from now());
BEGIN 
		if extract(minute from now()) >= 0 and extract(minute from now()) < 15 then 
			min_min := 0;
		end if;
		if extract(minute from now()) >= 15 and extract(minute from now()) < 30 then 
			min_min:= 15;
		end if;
		if extract(minute from now()) >= 30 and extract(minute from now()) < 45 then 
			min_min := 30;
		end if;
		if extract(minute from now()) >= 45 and extract(minute from now()) < 60 then  
			min_min:= 45;
		end if;	
	select count(*) into hits
	from logs
	where
		date(now()) = date(timestamp)
		and source = 'API'
		and extract(hour from now()) = extract(hour from timestamp)
		and extract(minute from now()) >= min_min
		and extract(minute from now()) < min_min + 15;
		
	return hits;
END $$
LANGUAGE plpgsql;

-- Hits need to be < 1,000/day
create function CalculateApiHits1day()
  returns integer as $$
declare 
	hits integer:= 0;
BEGIN 
	select count(*) into hits
	from logs
	where
		date(now()) = date(timestamp)
		and source = 'API';
		
	return hits;
END $$
LANGUAGE plpgsql;

-- For testing:
--insert into logs(status, action_type, db_table, db_column, db_value) values('test status 1', 'test action_type 1', 'test db_table 1', 'test db_column 1', 'test db_value 1');
--insert into logs(status, action_type, db_table, db_column, db_value) values('test status 2', 'test action_type 2', 'test db_table 2', 'test db_column 2', 'test db_value 2');
--insert into logs(status, action_type, db_table, db_column, db_value) values('test status 3', 'test action_type 3', 'test db_table 3', 'test db_column 3', 'test db_value 3');
-------------------------------------------------------------------------------------------
--   +-------------------+
--~~ | Stored Procedures |
--   +-------------------+
create or replace procedure sp_GetActivityIds ()
language plpgsql
as $$
begin
select id
from activities;
end; $$


confused???
    # Populate activities_old, meaning activities that are already in the db
    # *** the activities df has to have already been built before calling this
    def IdentifyOldActivities(self):
        self.CheckApiThreshold()
        
        self.conn = psycopg2.connect(host = "localhost", database = 'CyclingStats',
                              user = 'postgres', password = 'soccer18')
        with self.conn:
            with self.conn.cursor() as curs:
                for record in self.activities_df.itertuples():
                    # Make sure the Activity isnt already in the db
                    if record.id not in self.db_activity_ids_list: