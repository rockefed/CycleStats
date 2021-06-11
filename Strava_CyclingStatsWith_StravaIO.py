# -*- coding: utf-8 -*-
"""
Created on Sat Jun  5 17:31:46 2021

@author: rocke
"""
from stravaio import strava_oauth2
from stravaio import StravaIO
import pandas as pd
import numpy as np
import psycopg2
import datetime
import random
import time

class CylcingStats:
    def __init__(self, host="localhost", db="CyclingStats", usr="postgres", pwd="soccer18"):
        self.moisture = []
        self.ts = []
        self.conn = None
        self.host = host,
        self.database = db,
        self.user = usr,
        self.password = pwd
        self.client = None
        self.insert_sql = 'INSERT INTO Activities(achievement_count, athlete, athlete_count, attribute_map, average_speed, average_watts, comment_count, commute, device_watts, discriminator, distance, elapsed_time, elev_high, elev_low, end_latlng, external_id, flagged, gear_id, has_kudoed, id, kilojoules, kudos_count, manual, map, max_speed, max_watts, moving_time, name, photo_count, private, start_date, start_date_local, start_latlng, swagger_types, timezone, total_elevation_gain, total_photo_count, trainer, type, upload_id, weighted_average_watts, workout_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
        
        self.cols = ['achievement_count', 'athlete', 'athlete_count', 'attribute_map', 'average_speed', 'average_watts', 'comment_count', 'commute', 'device_watts', 'discriminator', 'distance', 'elapsed_time', 'elev_high', 'elev_low', 'end_latlng', 'external_id', 'flagged', 'gear_id', 'has_kudoed', 'id', 'kilojoules',
 'kudos_count', 'manual', 'map', 'max_speed', 'max_watts', 'moving_time', 'name', 'photo_count', 'private', 'start_date', 'start_date_local', 'start_latlng',
 'swagger_types', 'timezone', 'total_elevation_gain', 'total_photo_count', 'trainer', 'type', 'upload_id', 'weighted_average_watts',  'workout_type']
        self.insert_params = (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        
        self.athlete = None #JSON for strava athlete
        self.activities = [] # List of JSON for strava athletes activities
        self.activities_df = None

    def ConnectStravaApi(self):
        self.client = StravaIO(access_token='ae43677c206a6e100d05df5fdb5098d5db0179cc')

    def ConnectDb(self):
        self.conn = psycopg2.connect(host=self.host, database=self.database,
                                      user=self.user, password=self.password)

    def CloseDb(self):
        self.conn.close()

    # 
    def InsertActivities(self):
        self.conn = psycopg2.connect(host = "localhost", database = 'sandbox',
                              user = 'hank', password = 'soccer18')
        with self.conn:
            with self.conn.cursor() as curs:
                for record in self.activities_df.itertuples():
                    self.insert_params = (record.achievement_count, record.athlete, record.athlete_count, record.attribute_map, record.average_speed, record.average_watts, record.comment_count, record.commute, record.device_watts, record.discriminator, record.distance, record.elapsed_time, record.elev_high, record.elev_low, record.end_latlng, record.external_id, record.flagged, record.gear_id, record.has_kudoed, record.id, record.kilojoules, record.kudos_count, record.manual, record.map, record.max_speed, record.max_watts, record.moving_time, record.name, record.photo_count, record.private, record.start_date, record.start_date_local, record.start_latlng, record.swagger_types, record.timezone, record.total_elevation_gain, record.total_photo_count, record.trainer, record.type, record.upload_id, record.weighted_average_watts, record.workout_type)
                    curs.execute(self.insert_sql, self.insert_params)
                    print('Log successful')
        self.CloseDb()
        
    def GetAthlete(self):
        self.athlete = self.client.get_logged_in_athlete()
        self.athlete = self.athlete.to_dict()
        
    def GetActivities(self):
        self.list_activities = self.client.get_logged_in_athlete_activities()
        
    def ParseActivities(self):
        # Parse out each activities and store each record in a list
        for obj in self.list_activities:
            record = [obj.achievement_count, obj.athlete, obj.athlete_count, obj.attribute_map, obj.average_speed, obj.average_watts, obj.comment_count, obj.commute, obj.device_watts, obj.discriminator, obj.distance, obj.elapsed_time, obj.elev_high, obj.elev_low, obj.end_latlng, obj.external_id, obj.flagged, obj.gear_id, obj.has_kudoed, obj.id, obj.kilojoules, obj.kudos_count, obj.manual, obj.map, obj.max_speed, obj.max_watts, obj.moving_time, obj.name, obj.photo_count, obj.private, obj.start_date, obj.start_date_local, obj.start_latlng, obj.swagger_types, obj.timezone, obj.total_elevation_gain, obj.total_photo_count, obj.trainer, obj.type, obj.upload_id, obj.weighted_average_watts, obj.workout_type]
            
            self.activities.append(record)
            
        # Build a dataframe from the activities
        self.activities_df = pd.DataFrame(self.activities, columns=self.cols)

# Create an instance for the soil sensor
cs = CylcingStats()

cs.GetActivities()
cs.InsertActivities()


# strava_oauth2(client_id=66752, 
#               client_secret='c465d46063a97a42d5ef7336da589b9669a82bd9')

# Need logic here to check if access token is still valid and if not use request token to get a new one


# If the token is stored as an environment varible it is not neccessary
# to pass it as an input parameters
client = StravaIO(access_token='ae43677c206a6e100d05df5fdb5098d5db0179cc')

# Get logged in athlete (e.g. the owner of the token)
# Returns a stravaio.Athlete object that wraps the
# [Strava DetailedAthlete](https://developers.strava.com/docs/reference/#api-models-DetailedAthlete)
# with few added data-handling methods
athlete = client.get_logged_in_athlete()

# Dump athlete into a JSON friendly dict (e.g. all datetimes are converted into iso8601)
athlete_dict = athlete.to_dict()

# Get list of athletes activities since a given date (after) given in a human friendly format.
# Kudos to [Maya: Datetimes for Humans(TM)](https://github.com/kennethreitz/maya)
# Returns a list of [Strava SummaryActivity](https://developers.strava.com/docs/reference/#api-models-SummaryActivity) objects
list_activities = client.get_logged_in_athlete_activities()


# Columns for the dataframe
cols = ['achievement_count', 'athlete', 'athlete_count', 'attribute_map', 'average_speed', 'average_watts', 'comment_count', 'commute', 'device_watts', 'discriminator', 'distance', 'elapsed_time', 'elev_high', 'elev_low', 'end_latlng', 'external_id', 'flagged', 'gear_id', 'has_kudoed', 'id', 'kilojoules',
 'kudos_count', 'manual', 'map', 'max_speed', 'max_watts', 'moving_time', 'name', 'photo_count', 'private', 'start_date', 'start_date_local', 'start_latlng',
 'swagger_types', 'timezone', 'total_elevation_gain', 'total_photo_count', 'trainer', 'type', 'upload_id', 'weighted_average_watts',  'workout_type']

# Empty list to store each workout
records = []

# Parse out each activities and store each record in a list
for obj in list_activities:
    record = [obj.achievement_count, obj.athlete, obj.athlete_count, obj.attribute_map, obj.average_speed, obj.average_watts, obj.comment_count, obj.commute, obj.device_watts, obj.discriminator, obj.distance, obj.elapsed_time, obj.elev_high, obj.elev_low, obj.end_latlng, obj.external_id, obj.flagged, obj.gear_id, obj.has_kudoed, obj.id, obj.kilojoules, obj.kudos_count, obj.manual, obj.map, obj.max_speed, obj.max_watts, obj.moving_time, obj.name, obj.photo_count, obj.private, obj.start_date, obj.start_date_local, obj.start_latlng, obj.swagger_types, obj.timezone, obj.total_elevation_gain, obj.total_photo_count, obj.trainer, obj.type, obj.upload_id, obj.weighted_average_watts, obj.workout_type]
    
    records.append(record)
    
# Build a dataframe from the activities
records_df = pd.DataFrame(records, columns=cols)

records_df
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    