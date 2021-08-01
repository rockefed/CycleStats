# CycleStats

## Pre-Reqs
- stravaio library: To interact with the Strava API
- Postgres server: To store Strava data locally
- Postman [web/client]: To get and refresh the Developer Access Token
- Python 3.x+: To pull the Strava data and to store it in the Postgres db
- Strava API Aplication: Enable retrievable of your Strava data and create an Access Token
- Strava API Developer Access Token: Enable retrieving of Activities which require a permission of activities:write which is enabled via a DAT
- Strava: have Activity [workout] data

## Dependencies
- tkinter
- tkcalendar
- stravio
- psycopg2
- datetime
- random
- time
- os

## Setup
1) Download and install PostgreSQL server and create database named [CycleStats]
2) Run CycleStatsDbScript.sql in Postgres to build the database
3) Create the following User Environmental Variables on Windows and set accordingly
	a) POSTGRES_DB
	b) POSTGRES_PASSWORD
	c) POSTGRES_USER
3) Install necessary dependencies to Python environment
4) Create a Postman account and [optional] download and install the desktop application
5) Login to Strava website and create "My API Application" 
6) Get an API key with write level permission on the activities endpoint (required a lot of googling)
7) Update the access token by refreshing it via Postman
8) Run the Python application
9) Make sure connection information is correct and paste the access token from Postman to the appropriate field in the app
10) Make sure to Connect first, then can update the db via the API, process the activities table, and or export data from the db to a CSV
