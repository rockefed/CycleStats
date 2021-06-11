CREATE TABLE activities
(
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

create table activity_streams(
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

create table logs(
	id serial primary key,
	timestamp timestamp without time zone,
	who varchar(30),
	error_code integer,
	action_type int,
	message varchar(100)
);

create table logs_archive(
	id int primary key,
	timestamp timestamp without time zone,
	who varchar(30),
	error_code integer,
	action_type int,
	message varchar(100)
);

create table error_codes(
	id serial primary key,
	code varchar(10),
	description varchar(255),
	created timestamp without time zone
);
alter table error_codes alter column created set default now()::timestamp;

create table action_types(
	id serial primary key,
	code varchar(10),
	description varchar(255),
	created timestamp without time zone
);
alter table action_types alter column created set default now()::timestamp;