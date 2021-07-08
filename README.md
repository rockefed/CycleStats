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