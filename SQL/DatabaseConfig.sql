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

---------------------------------------
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
    workout_type numeric,
	isProcessed boolean DEFAULT false
)

---------------------------------------
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
	activity_id bigint,
	isProcessed boolean DEFAULT false
)

---------------------------------------
create table error_codes(
	id serial primary key,
	code varchar(10),
	description varchar(255),
	created timestamp without time zone
);
alter table error_codes alter column created set default now()::timestamp;

---------------------------------------
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

---------------------------------------
--

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
--   +------------------+
--~~ | Reporting Models |
--   +------------------+
CREATE TABLE rpt_activities
(
    "DbId" integer,
    "ActivityName" character varying COLLATE pg_catalog."default",
    "Type" character varying COLLATE pg_catalog."default",
    "StartDate" timestamp without time zone,
    "Hour" integer,
    "DayOfWeek" text COLLATE pg_catalog."default",
    "AthleteId" character varying COLLATE pg_catalog."default",
    "ElapsedTime_sec" integer,
    "MovingTime_sec" integer,
    "Distance_mile" numeric,
    "TotalElevationGain_ft" numeric,
    "AvgSpeed_mph" numeric,
    "MaxSpeed_mph" numeric,
    "Kilojoules" numeric,
    "AvgWatts" numeric,
    "WeightedAvgWatts" numeric,
    "MaxWatts" numeric,
    "ElevationHigh_ft" numeric,
    "ElevationLow_ft" numeric,
    "Timezone" character varying COLLATE pg_catalog."default",
    "Achievements" integer,
    "Athletes" integer,
    "Kudos" integer,
    "Photos" integer,
    "Comments" integer,
    "hasKudoed" boolean,
    "isPrivate" boolean,
    "ProcessedTimestamp" timestamp with time zone
)

---------------------------------------
--

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------
--   +-------+
--~~ | Views |
--   +-------+

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

---------------------------------------
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

---------------------------------------
-- Used for querying [activities] with a date range, no default values need a date
create or replace function GetActivities (_start_date date, _end_date date)
RETURNS TABLE (
    db_id integer,
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
    workout_type numeric,
    isprocessed boolean
)
language plpgsql
as $$
begin
	return query
	select *
	from activities a
	where a.start_date between _start_date and _end_date;
end; $$

---------------------------------------
-- Used for querying [activities_streams] with a date range, no default values need a date
create or replace function GetStreams (_start_date date, _end_date date)
RETURNS TABLE (
    db_id integer,
    "time" varchar(255),
    distance varchar(255),
    altitude varchar(255),
    velocity_smooth varchar(255),
    heartrate varchar(255),
    cadence varchar(255),
    watts varchar(255),
    moving varchar(255),
    grade_smooth varchar(255),
    lat varchar(255),
    lng varchar(255),
    activity_id varchar(255),
    isprocessed boolean
)
language plpgsql
as $$
begin
	return query
	select s.*
	from activities_streams s
	join activities a on s.activity_id::bigint = a.id::bigint
	where a.start_date between _start_date and _end_date;
end; $$ 

---------------------------------------
-- Used for querying [logs] within a date range, no default values need a date
create or replace function GetLogs (_start_date date, _end_date date)
RETURNS TABLE (
    id integer,
    "timestamp" timestamp without time zone,
    who character varying(255),
    status character varying(255),
    source character varying(255),
    action_type character varying(255),
    db_table character varying(255),
    db_column character varying(255),
    db_value character varying(255)
)
language plpgsql
as $$
begin
	return query
	select l.*
	from logs l
	where l."timestamp" between _start_date and _end_date;
end; $$ 
---------------------------------------
--
-- Used for querying [logs] within a date range, no default values need a date
create or replace function GetProcessedActivities(_start_date date, _end_date date)
RETURNS TABLE (
    "DbId" integer,
    "ActivityName" character varying,
    "Type" character varying,
    "StartDate" timestamp without time zone,
    "Hour" integer,
    "DayOfWeek" text,
    "AthleteId" character varying,
    "ElapsedTime_sec" integer,
    "MovingTime_sec" integer,
    "Distance_mile" numeric,
    "TotalElevationGain_ft" numeric,
    "AvgSpeed_mph" numeric,
    "MaxSpeed_mph" numeric,
    "Kilojoules" numeric,
    "AvgWatts" numeric,
    "WeightedAvgWatts" numeric,
    "MaxWatts" numeric,
    "ElevationHigh_ft" numeric,
    "ElevationLow_ft" numeric,
    "Timezone" character varying,
    "Achievements" integer,
    "Athletes" integer,
    "Kudos" integer,
    "Photos" integer,
    "Comments" integer,
    "hasKudoed" boolean,
    "isPrivate" boolean,
    "ProcessedTimestamp" timestamp with time zone
)
language plpgsql
as $$
begin
	return query
	select r.*
	from rpt_activities r
	where r."StartDate" between _start_date and _end_date;
end; $$ 

-------------------------------------------------------------------------------------------
--   +-------------------+
--~~ | Stored Procedures |
--   +-------------------+
-- Used to prevent duplicate inserts
create or replace procedure sp_GetActivityIds ()
language plpgsql
as $$
begin
select id
from activities;
end; $$

---------------------------------------
-- used to process raw activity records into something more usable for reporting
create or replace procedure sp_ProcessActivities()
language plpgsql
as $$
begin
insert into rpt_activities
select
	a.db_id as "DbId",
	a.name::varchar as "ActivityName",
	a.type::varchar as "Type",
	a.start_date as "StartDate",
	EXTRACT(HOUR FROM a.start_date)::integer as "Hour", --hour start
	CASE
		WHEN EXTRACT(DOW FROM a.start_date) = 0 THEN 'Sunday'
		WHEN EXTRACT(DOW FROM a.start_date) = 1 THEN 'Monday'
		WHEN EXTRACT(DOW FROM a.start_date) = 2 THEN 'Tuesday'
		WHEN EXTRACT(DOW FROM a.start_date) = 3 THEN 'Wednesday'
		WHEN EXTRACT(DOW FROM a.start_date) = 4 THEN 'Thursday'
		WHEN EXTRACT(DOW FROM a.start_date) = 5 THEN 'Friday'
		WHEN EXTRACT(DOW FROM a.start_date) = 6 THEN 'Saturday'
		ELSE '-1'
		END as "DayOfWeek", 
	SUBSTRING(a.athlete, 8, 8)::varchar as "AthleteId", 
	a.elapsed_time::integer as "ElapsedTime_sec",
	a.moving_time::integer as "MovingTime_sec",
	ROUND(a.distance::numeric / 1600, 1) as "Distance_mile", -- m --> mi
	ROUND(a.total_elevation_gain::numeric * 3.28, 1) as "TotalElevationGain_ft", -- m --> ft
	ROUND(a.average_speed::numeric * 2.24, 1) as "AvgSpeed_mph", -- m/s --> mph
	ROUND(a.max_speed::numeric * 2.24, 1) as "MaxSpeed_mph", -- m/s --> mph
	a.kilojoules as "Kilojoules",
	a.average_watts::numeric as "AvgWatts", 
	a.weighted_average_watts::numeric as "WeightedAvgWatts",
	a.max_watts::numeric as "MaxWatts",
	ROUND(a.elev_high::numeric * 3.28, 1) as "ElevationHigh_ft",
	ROUND(a.elev_low::numeric * 3.28, 1) as "ElevationLow_ft",
	a.timezone::varchar as "Timezone",
	a.achievement_count::integer as "Achievements",
	a.athlete_count::integer as "Athletes",
	a.kudos_count::integer as "Kudos",
	a.total_photo_count::integer as "Photos",
	a.comment_count::integer as "Comments",
	a.has_kudoed::boolean as "hasKudoed",
	a.private::boolean as "isPrivate",
	now() as "ProcessedTimestamp"
from activities a
where a.isProcessed = false;

update activities set
	isProcessed = true
where db_id in (select "DbId" from rpt_activities r);

commit;
end; $$

---------------------------------------
--