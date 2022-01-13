create table dim_athlete(
	athlete_id int unique,
	first_name nvarchar(100),
	last_name nvarchar(100)
);
insert into dim_athlete(athlete_id, first_name, last_name) values(0, '', '');
create table dim_date(
	date_id int unique,
	[day_num] int,
	[day_of_week_abbrev] nvarchar(4),
	[day_of_week_name] nvarchar(9),
	[week_num] int,
	[month_num] int,
	[month_abbrev] nvarchar(3),
	[month_name] nvarchar(8),
	[quarter_num] int,
	[quarter_name] nvarchar(11)
);
insert into dim_date(date_id, day_num, day_of_week_abbrev, day_of_week_name, week_num, month_num, month_abbrev, month_name, quarter_num, quarter_name) values(-1, -1, '', '', -1, -1, '', '', -1, '');
create table dim_time(
	time_id int unique,
	time_id_txt_trail nvarchar(6),
	hour_num int,
	hour_num_txt nvarchar(6),
	hour_num_txt_trail nvarchar(6),
	min_num int,
	min_num_txt nvarchar(6),
	min_num_txt_trail nvarchar(6),
	sec_num int,
	sec_num_txt nvarchar(6),
	sec_num_txt_trail nvarchar(6),
	time_of_day nvarchar(8)
);
insert into dim_time(time_id, time_id_txt_trail, hour_num, hour_num_txt, hour_num_txt_trail, min_num, min_num_txt, min_num_txt_trail, sec_num, sec_num_txt, sec_num_txt_trail, time_of_day) values(-1, '', -1, '', '', -1, '', '', -1, '', '', '');
create table dim_activity_type(
	activity_type_id int identity(-1,1),
	activity_type_name nvarchar(50),
	is_outdoors bit,
	is_seasonal bit
);
insert into dim_activity_type(activity_type_name, is_outdoors, is_seasonal) values('', 0, 0);
insert into dim_activity_type(activity_type_name, is_outdoors, is_seasonal) values('Workout', 0, 0);
insert into dim_activity_type(activity_type_name, is_outdoors, is_seasonal) values('Walk', 0, 0);
insert into dim_activity_type(activity_type_name, is_outdoors, is_seasonal) values('Weight Train', 0, 0);
insert into dim_activity_type(activity_type_name, is_outdoors, is_seasonal) values('Outdoor Ride', 1, 1);
insert into dim_activity_type(activity_type_name, is_outdoors, is_seasonal) values('Virtual Ride', 0, 0);
insert into dim_activity_type(activity_type_name, is_outdoors, is_seasonal) values('Run', 0, 0);
insert into dim_activity_type(activity_type_name, is_outdoors, is_seasonal) values('Rock Climb', 0, 0);
insert into dim_activity_type(activity_type_name, is_outdoors, is_seasonal) values('Soccer', 0, 0);
insert into dim_activity_type(activity_type_name, is_outdoors, is_seasonal) values('Swim', 0, 0);
insert into dim_activity_type(activity_type_name, is_outdoors, is_seasonal) values('Mountain Bike', 0, 0);
insert into dim_activity_type(activity_type_name, is_outdoors, is_seasonal) values('', 0, 0);
create table dim_gear(
	gear_id int identity(1,1),
	gear_name nvarchar(50)
);
insert into dim_gear(gear_name) values('');
create table dim_data_source(
	data_source_id int identity(-1,1),
	data_source_name nvarchar(50)
);
insert into dim_data_source(data_source_name) values('');
create table dim_units(
	units_id int identity(-1,1),
	units_name nvarchar(8),
	is_imperial bit,
	is_metric bit,
	dist_miles bit,
	dist_kilometers bit,
	vert_feet bit,
	vert_meters bit
);
insert into dim_units(units_name, is_imperial, is_metric, dist_miles, dist_kilometers, vert_feet, vert_meters) values ('', 0, 0, 0, 0, 0, 0)
insert into dim_units(units_name, is_imperial, is_metric, dist_miles, dist_kilometers, vert_feet, vert_meters) values ('Imperial', 1, 0, 1, 0, 1, 0)
insert into dim_units(units_name, is_imperial, is_metric, dist_miles, dist_kilometers, vert_feet, vert_meters) values ('Metric', 0, 1, 0, 1, 0, 1)
create table fact_activities(
	activity_id int unique not null,
	[db_id] int,
	activity_name nvarchar(1000),
	activity_type_id int,
	date_id int,
	time_id int,
	gear_id int,
	data_source_id int,
	athlete_id int,
	units_id int,
	avg_speed decimal(3,3),
	avg_watts decimal(3,3),
	wght_avg_watts decimal(5,1),
	ct_comments int, 
	tot_dist decimal(18,3),
	tot_vert decimal(18,3),
	tot_time_secs int,
	tot_kiojoules decimal(6,1),
	tot_photos int,
	tot_kudoes int,
	high_vert decimal(6,1),
	low_vert decimal(6,1),
	max_speed decimal(3,1),
	max_watts decimal(5,1),
	kudoed bit,
	is_private bit
	);