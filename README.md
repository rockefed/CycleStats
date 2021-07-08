# CycleStats
 
## Pre-Reqs
stravaio library: To interact with the Strava API
Postgres server: To store Strava data locally
Postman [web/client]: To get and refresh the Developer Access Token
Python 3.x+: To pull the Strava data and to store it in the Postgres db
Strava API Aplication: Enable retrievable of your Strava data and create an Access Token
Strava API Developer Access Token: Enable retrieving of Activities which require a permission of activities:write which is enabled via a DAT
Strava: have Activity [workout] data

## Dependencies
tkinter
tkcalendar
stravio# CycleStats
 
<<<<<<< HEAD
## Pre-Reqs
stravaio library: To interact with the Strava API
Postgres server: To store Strava data locally
Postman [web/client]: To get and refresh the Developer Access Token
Python 3.x+: To pull the Strava data and to store it in the Postgres db
Strava API Aplication: Enable retrievable of your Strava data and create an Access Token
Strava API Developer Access Token: Enable retrieving of Activities which require a permission of activities:write which is enabled via a DAT
Strava: have Activity [workout] data

## Dependencies
tkinter
tkcalendar
stravio
psycopg2
datetime
random
time
os

## Setup
1) Run CycleStatsDbScript.sql in Postgres to build the database
2) Create the following User Environmental Variables on Windows
	a) POSTGRES_DB
	b) POSTGRES_PASSWORD
	c) POSTGRES_USER
3) Install necessary dependencies to Python environment
4) 
=======
Simple little program with a Tkinter GUI that allows cyclists who have a Strava account to pull down their information and store it in a Postrgres db. 

At least at the onset of this project, I'd recommend having the Postman Client, Jupyter Notebooks, certain packages, and PostgreSql with the Admin4 tool.


1) Setup your Strava account so it has access to the API. 
2) Follow this tutorial to get necessary activities::read_all permissions
3) Install the above programs
4) Build the Postgres db
5) Install necessary Python packages [stravaIO, pandas, numpy, psycopg2, datetime]
6) Run code
7) [Optional] Automate the Activities and Streams calls to a regular cadence.
>>>>>>> 2373e060e9eed631d680a63f0f1b991dd1b72a36

psycopg2
datetime
random
time
os

## Setup
1) Run CycleStatsDbScript.sql in Postgres to build the database
2) Create the following User Environmental Variables on Windows
	a) POSTGRES_DB
	b) POSTGRES_PASSWORD
	c) POSTGRES_USER
3) Install necessary dependencies to Python environment
4) 