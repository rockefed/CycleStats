# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 16:33:48 2021

@author: rocke
"""

from tkinter import *
from tkcalendar import Calendar, DateEntry
from stravaio import strava_oauth2
from stravaio import StravaIO
import pandas as pd
import numpy as np
import psycopg2
import datetime
import random
import time
import os

window = Tk()

window.title("Cycle Stats")
window.geometry('600x400')


#############################################
#######################
## Cycle Stats Class ##
#######################

class CyclingStats:
    def __init__(self, host, db, usr, pwd, token):
        # Postgres db conn info
        self.conn = None
        self.host = host,
        self.database = db,
        self.user = usr,
        self.password = pwd
        self.client = None
        self.conn_string = None
        
        # Logging
        self.verbose = False # for terminal logging (db logging is handled via the db)
        self.insert_log_sql = 'INSERT INTO logs(who, status, source, action_type, db_table, db_column, db_value) VALUES(%s,%s,%s,%s,%s,%s,%s);'
        self.insert_log_params = (None, None, None, None, None, None, None)
        
        # Activities dataframe
        self.cols_activities = ['achievement_count', 'athlete', 'athlete_count', 'attribute_map', 'average_speed', 'average_watts', 'comment_count', 'commute', 'device_watts', 'discriminator', 'distance', 'elapsed_time', 'elev_high', 'elev_low', 'end_latlng', 'external_id', 'flagged', 'gear_id', 'has_kudoed', 'id', 'kilojoules',
 'kudos_count', 'manual', 'map', 'max_speed', 'max_watts', 'moving_time', 'name', 'photo_count', 'private', 'start_date', 'start_date_local', 'start_latlng',
 'swagger_types', 'timezone', 'total_elevation_gain', 'total_photo_count', 'trainer', 'type', 'upload_id', 'weighted_average_watts',  'workout_type']
        
        # Strava API stuff
        self.api_calls_15min = 0
        self.api_calls_1day = 0
        self.api_call_lim_15min = 100
        self.api_call_lim_1day = 1000
        #self.access_token = '80c2c3d18002535b07ff8846d8bdf58f56cbd285' # TODO: this should be checked + refreshed auto
        self.access_token = token
        
        # ATHLETE
        self.athlete_id = None
        self.athlete_name = ''
        self.athlete = None 
        self.athlete_dict = None
        
        # ACTIVITIES
        self.activities = [] # List of JSON for strava athletes activities
        self.activities_df = None # Activities dataframe
        self.activities_ids_master = [] # Master list of activities ids, parsed from the API
        self.select_sql_activity_id = 'SELECT id from activities;' # Getting the Activities Ids from the DB to prevent dups
        self.db_activity_ids = None # returns a 2d tuple
        self.db_activity_ids_list = [] # the tuple is parsed to a 1d list
        self.insert_sql = 'INSERT INTO Activities(achievement_count, athlete, athlete_count, attribute_map, average_speed, average_watts, comment_count, commute, device_watts, discriminator, distance, elapsed_time, elev_high, elev_low, end_latlng, external_id, flagged, gear_id, has_kudoed, id, kilojoules, kudos_count, manual, map, max_speed, max_watts, moving_time, name, photo_count, private, start_date, start_date_local, start_latlng, swagger_types, timezone, total_elevation_gain, total_photo_count, trainer, type, upload_id, weighted_average_watts, workout_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id;;'
        self.insert_params = (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        
        # STREAMS
        self.streams = [] # Stream obj with to_dict which can be used to make a pandas df
        self.streams_dict = None
        self.streams_df = None # Streams dataframe, only ones that arent in the db
        self.select_sql_stream_activity_id = 'select distinct cast(activity_id as bigint) from activities_streams;' # Getting the Streams Activities Ids from the DB to prevent dups
        self.db_stream_activity_ids = None # returns a 2d tuple
        self.db_stream_activity_ids_list = [] # the tuple is parsed to a 1d list
        self.streams_missing = [] # Comparing activities_ids_master to _db_stream_activity_ids_list & popping them too
        self.insert_activities_streams_sql = 'INSERT INTO Activities_Streams(time, distance, altitude, velocity_smooth, heartrate, cadence, watts, moving, grade_smooth, lat, lng, activity_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning db_id;'
        self.insert_activities_streams_params = (None, None, None, None, None, None, None, None, None, None, None, None)
        self.curr_activity_id = None # Streams have to be called 1 at a time
        
    #######################################################################################
    # API Limit Handling & Logging
    #######################################################################################      
    # This is ultimately going to have to query a View
    def CheckApiThreshold(self):        
        self.conn = psycopg2.connect(self.conn_string)
        
        with self.conn:
            with self.conn.cursor() as curs:
                curs.execute("select CalculateApiHits15mins();")
                self.api_calls_15min = curs.fetchall()
                curs.execute("select CalculateApiHits1day();")
                self.api_calls_1day = curs.fetchall()
                
                if self.verbose: print("API Calls in past 15min: {0}".format(self.api_calls_15min[0][0]))
                if self.verbose: print("API Calls in past 1day: {0}".format(self.api_calls_1day[0][0])) 
                
        # Terminate the app if over the limit
        if (self.api_calls_15min[0][0] >= self.api_call_lim_15min) | (self.api_calls_1day[0][0] >= self.api_call_lim_1day):
            print("You exceeded the API limit for now, exiting.")
            self.exit()
            
        self.CloseDb()
        return self.api_calls_15min, self.api_calls_1day
                
    # Every interaction with the API & db should be logged, will introduce lookup tables & FKs eventually
    def DbLog(self, _who, _status, _source, _action_type, _db_table, _db_column, _db_value, is_connected = False, _curs = None):
        self.insert_log_params = (_who, _status, _source, _action_type, _db_table, _db_column, _db_value)
        if is_connected == False:
            self.ConnectDb()
            
            with self.conn:
                with self.conn.cursor() as curs:
                    
                    curs.execute(self.insert_log_sql, self.insert_log_params)

            self.CloseDb()
        else:
            _curs.execute(self.insert_log_sql, self.insert_log_params)
        
    #######################################################################################
    # Master Methods
    #######################################################################################
    ## These just provide a one-click to do anything instead of having to call multiple methods
    ## The only methods that should really be called after its stable
    # Method that will ultimately try to do the full suite of connections, updates, and inserts
    def OneClick(self):
        if self.verbose == False:
            self.verbose = True
            self.CheckApiThreshold()
            self.verbose = False
            
        # Connections
        self.DbConnString()
        self.ConnectStravaApi()
        # Athlete
        self.GetAthlete()
        # Activities
        self.GetActivities()
        self.ParseActivities()
        self.GetDbActivityIds()
        self.ParseDbActivityIds()
        self.CompileMasterActivitiesIdList()
        self.InsertActivities()
        # Streams
        self.GetDbStreamActivityIds()
        self.ParseDbStreamActivityIds()
        self.DetermineMissingStreams()
        self.GetStreams() # This calls ParseStream() and InsertStreams()
    
    #######################################################################################
    # Connections
    #######################################################################################
    
    # Makes a string to connect to the Postgres db based on values used to create the class
    def DbConnString(self):
        self.conn_string = "host = '{0}' dbname = '{1}' user = '{2}' password = '{3}'".format(self.host[0], self.database[0], self.user[0], self.password)
    
    def RefreshAccessToken(self):
        pass# TODO
    
    def ConnectStravaApi(self):
        self.client = StravaIO(access_token = self.access_token) 

    # Don't use this until figure out how to pass vars into the params
    def ConnectDb(self):
        self.conn = psycopg2.connect(self.conn_string)

    def CloseDb(self):
        self.conn.close()

    #######################################################################################
    # Athlete
    #######################################################################################       
        
    # Gets the current athlete
    def GetAthlete(self):
        self.CheckApiThreshold()
        self.athlete = self.client.get_logged_in_athlete()
        self.athlete_dict = self.athlete.to_dict()
        self.ParseAthlete()
        self.DbLog(self.athlete_name, 'Success', 'API', 'GET', 'athlete', '', str(self.athlete_id))
        
    def ParseAthlete(self):
        self.athlete_name = self.athlete_dict['firstname'] + ' ' + self.athlete_dict['lastname']
        self.athlete_id = self.athlete_dict['id']
        
    #######################################################################################
    # Activities
    #######################################################################################
    
    # Pulls a list of activities for the current athlete from the Strava API
    def GetActivities(self):
        self.CheckApiThreshold()
        self.list_activities = self.client.get_logged_in_athlete_activities()
        self.DbLog(self.athlete_name, 'Success', 'API', 'GET', 'activities', '', '')
                   
    # Parses the list of activities into a pandas dataframe
    def ParseActivities(self):
        # Parse out each activities and store each record in a list
        for obj in self.list_activities:
            record = [obj.achievement_count, obj.athlete, obj.athlete_count, obj.attribute_map, obj.average_speed, obj.average_watts, obj.comment_count, obj.commute, obj.device_watts, obj.discriminator, obj.distance, obj.elapsed_time, obj.elev_high, obj.elev_low, obj.end_latlng, obj.external_id, obj.flagged, obj.gear_id, obj.has_kudoed, obj.id, obj.kilojoules, obj.kudos_count, obj.manual, obj.map, obj.max_speed, obj.max_watts, obj.moving_time, obj.name, obj.photo_count, obj.private, obj.start_date, obj.start_date_local, obj.start_latlng, obj.swagger_types, obj.timezone, obj.total_elevation_gain, obj.total_photo_count, obj.trainer, obj.type, obj.upload_id, obj.weighted_average_watts, obj.workout_type]
 
            self.activities.append(record)
            
        # Build a dataframe from the activities
        self.activities_df = pd.DataFrame(self.activities, columns=self.cols_activities)
    
    # Pull Activity Ids from db to make sure dups arent inserted
    def GetDbActivityIds(self):
        self.conn = psycopg2.connect(self.conn_string)
        with self.conn:
            with self.conn.cursor() as curs:
                curs.execute(self.select_sql_activity_id)
                self.db_activity_ids = curs.fetchall()
        
        self.CloseDb()
        self.DbLog(self.athlete_name, 'Success', 'DB', 'SELECT', 'activities', 'Id', '')
    
    # These are returned as a tuple, parsing them into a 1d list to compare against db Activity Ids 
    #to make sure dups aren't inserted
    def ParseDbActivityIds(self): 
        for rec in self.db_activity_ids:
             self.db_activity_ids_list.append(rec[0])                       
        
    def CompileMasterActivitiesIdList(self):
        for record in self.activities_df.itertuples():
            self.activities_ids_master.append(record.id)
        
    # Insert activities from the Strava API into the Postgres CyclingStats db
    def InsertActivities(self):
        self.CheckApiThreshold()

        self.ConnectDb()
        
        with self.conn:
            
            with self.conn.cursor() as curs:
                
                # TODO: need to make sure at max __ records to not go over api limit
                for record in self.activities_df.itertuples():
                    
                    # Make sure the Activity isnt already in the db
                    if record.id not in self.db_activity_ids_list:
                        self.insert_params = (record.achievement_count, str(record.athlete), record.athlete_count, str(record.attribute_map), record.average_speed, record.average_watts, record.comment_count, record.commute, str(record.device_watts), str(record.discriminator), record.distance, record.elapsed_time, record.elev_high, record.elev_low, str(record.end_latlng), str(record.external_id), record.flagged, str(record.gear_id), record.has_kudoed, record.id, record.kilojoules, record.kudos_count, record.manual, str(record.map), record.max_speed, record.max_watts, record.moving_time, str(record.name), record.photo_count, record.private, record.start_date, record.start_date_local, str(record.start_latlng), str(record.swagger_types), str(record.timezone), record.total_elevation_gain, record.total_photo_count, record.trainer, str(record.type), record.upload_id, record.weighted_average_watts, record.workout_type)
                        curs.execute(self.insert_sql, self.insert_params)
                        self.DbLog(self.athlete_name, 'Success', 'DB', 'INSERT', 'activities', 'id', record.id, True, curs)
                        if self.verbose == True: print('Inserted Activity {0} successfully'.format(str(record.id)))
                        self.insert_params = (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
                    
                    else:
                        if self.verbose == True: print('Activity {0} already in the database'.format(str(record.id)))
        
        self.CloseDb()
        
    #######################################################################################
    # Activity Streams
    #######################################################################################
    
    # Pull Activity Ids from db to make sure dups arent inserted
    def GetDbStreamActivityIds(self):
        self.conn = psycopg2.connect(self.conn_string)
        
        with self.conn:
            with self.conn.cursor() as curs:
                curs.execute(self.select_sql_stream_activity_id)
                self.db_stream_activity_ids = curs.fetchall()
        self.CloseDb()
        self.DbLog(self.athlete_name, 'Success', 'DB', 'SELECT', 'streams', 'Activity_id', '')
    
    # These are returned as a tuple, parsing them into a 1d list to compare against db Stream Activity Ids 
    #to make sure dups aren't inserted
    def ParseDbStreamActivityIds(self): 
        for rec in self.db_stream_activity_ids:
             self.db_stream_activity_ids_list.append(rec[0])
    
    def DetermineMissingStreams(self):
        for act_id in self.activities_ids_master:
            if act_id not in self.db_stream_activity_ids_list:
                self.streams_missing.append(act_id)
    
    # Pull a list of Streams based on activities_df.id
    def GetStreams(self):
        for act_id in self.streams_missing:
            self.stream = self.client.get_activity_streams(act_id, athlete_id = self.athlete_id)
            self.DbLog(self.athlete_name, 'Success', 'API', 'GET', 'Streams', '', '') 
            self.ParseStream(_activity_id = act_id)
            self.InsertStreams()
            
            self.stream = None
            self.streams_dict = None
            self.streams_df = None
            
            #self.streams_missing.remove(act_id) # So can pick up where left off after 15 mins
        
    def ParseStream(self, _activity_id):
        self.streams_dict = cs.stream.to_dict()
        self.streams_df = pd.DataFrame(cs.streams_dict)
        self.streams_df['activity_id'] = _activity_id
        
        if 'time' not in self.streams_df.columns: self.streams_df['time'] = ''
        if 'distance' not in self.streams_df.columns: self.streams_df['distance'] = '-1'
        if 'altitude' not in self.streams_df.columns: self.streams_df['altitude'] = '-1'
        if 'velocity_smooth' not in self.streams_df.columns: self.streams_df['velocity_smooth'] = '-1'
        if 'heartrate' not in self.streams_df.columns: self.streams_df['heartrate'] = '-1'
        if 'cadence' not in self.streams_df.columns: self.streams_df['cadence'] = '-1'
        if 'watts' not in self.streams_df.columns: self.streams_df['watts'] = '-1'
        if 'moving' not in self.streams_df.columns: self.streams_df['moving'] = ''
        if 'grade_smooth' not in self.streams_df.columns: self.streams_df['grade_smooth'] = '-1'
        if 'lat' not in self.streams_df.columns: self.streams_df['lat'] = ''
        if 'lng' not in self.streams_df.columns: self.streams_df['lng'] = ''
    
    def InsertStreams(self):      
        self.conn = psycopg2.connect(self.conn_string)
        
        with self.conn:
            with self.conn.cursor() as curs:
                for record in self.streams_df.itertuples():
                    self.insert_activities_streams_params = (str(record.time), str(record.distance), str(record.altitude), str(record.velocity_smooth), str(record.heartrate), str(record.cadence), str(record.watts), str(record.moving), str(record.grade_smooth), str(record.lat), str(record.lng), str(record.activity_id))
                    curs.execute(self.insert_activities_streams_sql, self.insert_activities_streams_params)
                    
                    self.curr_stream_id = curs.fetchone()[0]
                    self.DbLog(self.athlete_name, 'Success', 'DB', 'INSERT', 'streams', 'db_id', self.curr_stream_id, True, _curs = curs)
                    self.curr_stream_id = None
                        
                    # Reset the params, just in case
                    self.insert_activities_streams_params = (None, None, None, None, None, None, None, None, None, None, None, None)
                
                if self.verbose == True: print('Inserted Activity Stream for Activity {0}.'.format(str(record.activity_id)))
  
        self.insert_activities_streams_params = (None, None, None, None, None, None, None, None, None, None, None, None)
        self.CloseDb()
        
    #######################################################################################
    # Exports
    #######################################################################################
    def ExportActivities(self, start_date, end_date):      
        self.conn = psycopg2.connect(self.conn_string)
        sql = "select * from GetActivities('{0}', '{1}')".format(start_date, end_date)
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()
    
    def ExportStreams(self, start_date, end_date):      
        self.conn = psycopg2.connect(self.conn_string)
        sql = "select * from GetStreams('{0}', '{1}')".format(start_date, end_date)
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()
    
    def ExportLogs(self, start_date, end_date):      
        self.conn = psycopg2.connect(self.conn_string)
        sql = "select * from GetLogs('{0}', '{1}')".format(start_date, end_date)
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()
    
    def ExportProcessedActivities(self, start_date, end_date):      
        self.conn = psycopg2.connect(self.conn_string)
        sql = "select * from GetProcessedActivities('{0}', '{1}')".format(start_date, end_date)
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

#############################################
#######################
## UI Functionalilty ##
#######################
def clicked():
    pass

# must be run prior to interacting with api or db
def Connect():
    global cs    
    try:
        cs = CyclingStats(str(txt_db_host.get()), txt_db.get(), txt_db_user.get(), txt_db_pw.get(), txt_access_token.get())
        cs.DbConnString()
        status_text.set("Connected to PostGreSQL CyclingStats database")
    except Exception as e:
        status_text.set(e.args)

def PullAllDataFromApi():
    try:
        status_text.set("Pulling data from Strava API")
        cs.OneClick()
        status_text.set("CyclingStats database is up-to-date with the Strava API")
    except Exception as e:
        status_text.set(e.args)
    
def CheckApiCalls():
    _per_mins, _per_day = cs.CheckApiThreshold()

    per_mins.set(_per_mins)
    per_day.set(_per_day)
    
def ProcessActivities():
    pass

def ExportActivities(start_date, end_date):
    status_text.set("Exporting Activities to a CSV")
    text = cs.ExportActivities(start_date, end_date)
    df = pd.DataFrame(text, columns = ["db_id", "achievement_count", "athlete", "athlete_count", "attribute_map", "average_speed", "average_watts", "comment_count", "commute", "device_watts", "discriminator", "distance", "elapsed_time", "elev_high"," elev_low", "end_latlng", "external_id", "flagged", "gear_id", "has_kudoed", "id", "kilojoules", "kudos_count", "manual", "map", "max_speed", "max_watts", "moving_time", "name", "photo_count", "private", "start_date", "start_date_local", "start_latlng", "swagger_types", "timezone", "total_elevation_gain", "total_photo_count", "trainer", "type", "upload_id", "weighted_average_watts", "workout_type", "isprocessed"])
    df.to_csv('Activities_{0}_to_{1}.csv'.format(start_date, end_date))
    status_text.set("Successfully exported Activities to a CSV")
    
def ExportStreams(start_date, end_date):
    status_text.set("Exporting Streams to a CSV")
    text = cs.ExportStreams(start_date, end_date)
    df = pd.DataFrame(text, columns = ["db_id", "time", "distance", "altitude", "velocity_smooth", "heartrate", "cadence", "watts", "moving", "grade_smooth", "lat", "lng", "activity_id", "isprocessed"])
    df.to_csv('Streams_{0}_to_{1}.csv'.format(start_date, end_date))
    status_text.set("Successfully exported Streams to a CSV")
    
def ExportLogs(start_date, end_date):
    status_text.set("Exporting Logs to a CSV")
    text = cs.ExportLogs(start_date, end_date)
    df = pd.DataFrame(text, columns = ["id", "timestamp", "who", "status", "source", "action_type", "db_table", "db_column", "db_value"])
    df.to_csv('Logs_{0}_to_{1}.csv'.format(start_date, end_date))
    status_text.set("Successfully exported Logs to a CSV")
    
def ExportProcessedActivities(start_date, end_date):
    status_text.set("Exporting ProcessedActivities to a CSV")
    text = cs.ExportProcessedActivities(start_date, end_date)
    df = pd.DataFrame(text, columns=["DbId", "ActivityName", "Type", "StartDate", "Hour", "DayOfWeek", "AthleteId", "ElapsedTime_sec", "MovingTime_sec", "Distance_mile", "TotalElevationGain_ft", "AvgSpeed_mph", "MaxSpeed_mph", "Kilojoules", "AvgWatts", "WeightedAvgWatts", "MaxWatts", "ElevationHigh_ft", "ElevationLow_ft", "Timezone", "Achievements", "Athletes", "Kudos", "Photos", "Comments", "hasKudoed", "isPrivate", "ProcessedTimestamp"])
    df.to_csv('ProcessedActivities_{0}_to_{1}.csv'.format(start_date, end_date))
    status_text.set("Successfully exported ProcessedActivities to a CSV")
    
def ChangeButtonColors(color):
    btn_api_check.bg

#############################################
#########################
## UI Variables to set ##
#########################

lbl_api_hdr = Label(window, text="Strava API", font= ('Arial 14 bold'))
lbl_api_hdr.grid(column=1, row=0, pady= 10)

per_mins = StringVar()
per_day = StringVar()
per_mins.set(0)
per_day.set(0)
btn_api_check = Button(window, text="Check API Calls", command=CheckApiCalls)
btn_api_check.grid(column=0, row=1)
lbl_api_15min = Label(window, text="15mins:")
lbl_api_15min.grid(column=1, row=1)
lbl_api_15min_val = Label(window, textvariable=per_mins)
lbl_api_15min_val.grid(column=2, row=1)
lbl_api_1day = Label(window, text="1day: ")
lbl_api_1day.grid(column=3, row=1)
lbl_api_1day_val = Label(window, textvariable=per_day)
lbl_api_1day_val.grid(column=4, row=1)

lbl_api_hdr = Label(window, text="Connection Settings", font= ('Arial 14 bold'))
lbl_api_hdr.grid(column=1, row=2, pady= 10)

lbl_access_token = Label(window, text="API Access Token")
lbl_access_token.grid(column=0, row=3)
txt_access_token = Entry(window,width=50)
txt_access_token.grid(column=1, row=3, columnspan=2)

lbl_db_user = Label(window, text="Postgres User")
lbl_db_user.grid(column=0, row=4)
txt_db_user = Entry(window,width=50)
txt_db_user.grid(column=1, row=4, columnspan=2)
txt_db_user.insert(0, os.getenv('POSTGRES_USER') or '')

lbl_db_pw = Label(window, text="Postgres Password")
lbl_db_pw.grid(column=0, row=5)
txt_db_pw = Entry(window,width=50,show="*")
txt_db_pw.grid(column=1, row=5, columnspan=2)
txt_db_pw.insert(0, os.getenv('POSTGRES_PASSWORD') or '')

lbl_db_host = Label(window, text="Postgres Host")
lbl_db_host.grid(column=0, row=6)
txt_db_host = Entry(window,width=50)
txt_db_host.grid(column=1, row=6, columnspan=2)
txt_db_host.insert(0, 'localhost')

lbl_db = Label(window, text="Postgres Database")
lbl_db.grid(column=0, row=7)
txt_db = Entry(window,width=50)
txt_db.grid(column=1, row=7, columnspan=2)
txt_db.insert(0, os.getenv('POSTGRES_DB') or '')

btn_connect = Button(window, text="Connect to DB", command=Connect)
btn_connect.grid(column=0, row=8)

btn_api_all = Button(window, text="Update Entire DB with API", command=PullAllDataFromApi)
btn_api_all.grid(column=1, row=8)

btn_process_acts = Button(window, text="Process Activities", command=ProcessActivities)
btn_process_acts.grid(column=2, row=8)

#############################################
#############
## Exports ##
#############
lbl_exports = Label(window, text="Export", font= ('Arial 14 bold'))
lbl_exports.grid(column=1, row=9, pady= 10)

# Date Range Filters
lbl_export_date_range = Label(window, text="Date Range")
lbl_export_date_range.grid(column=0, row=11)
txt_export_date_range_start = DateEntry(window,width=25)
txt_export_date_range_start.grid(column=1, row=11)
txt_export_date_range_end = DateEntry(window,width=25)
txt_export_date_range_end.grid(column=2, row=11)

lbl_raw = Label(window, text="Raw:")
lbl_raw.grid(column=0, row=13)

btn_export_acts = Button(window, text="Activities", command=lambda: ExportActivities(str(txt_export_date_range_start.get_date()), str(txt_export_date_range_end.get_date())))
btn_export_acts.grid(column=1, row=13)

btn_export_streams = Button(window, text="Activity Streams", command=lambda: ExportStreams(str(txt_export_date_range_start.get_date()), str(txt_export_date_range_end.get_date())))
btn_export_streams.grid(column=2, row=13)

btn_export_logs = Button(window, text="DB Logs", command=lambda: ExportLogs(str(txt_export_date_range_start.get_date()), str(txt_export_date_range_end.get_date())))
btn_export_logs.grid(column=3, row=13)

lbl_processed = Label(window, text="Processed:")
lbl_processed.grid(column=0, row=14)

btn_export_acts_processed = Button(window, text="Activities", command=lambda: ExportProcessedActivities(str(txt_export_date_range_start.get_date()), str(txt_export_date_range_end.get_date())))
btn_export_acts_processed.grid(column=1, row=14)

#############################################
#############
## Status  ##
#############
status_text = StringVar()
status_text.set("Not Connected")
lbl_status = Label(window, text="Status:")
lbl_status.grid(column=0, row=15)
lbl_status_status = Label(window, textvariable=status_text)
lbl_status_status.grid(column=1, row=15, columnspan=3)

cs = None

window.mainloop()