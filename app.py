###library###
from flask import Flask, request
import sqlite3
import requests
from tqdm import tqdm
import json 
import numpy as np
import pandas as pd

app = Flask(__name__) 

###function###
def make_connection():
    connection = sqlite3.connect('austin_bikeshare.db')
    return connection
    
def get_all_stations(conn):
    query = f"""SELECT * FROM stations"""
    result = pd.read_sql_query(query, conn)
    return result

def get_all_trips(conn):
    query = f"""SELECT * FROM trips"""
    result = pd.read_sql_query(query, conn)
    return result

def get_station_id(station_id, conn):
    query = f"""SELECT * FROM stations WHERE station_id = {station_id}"""
    result = pd.read_sql_query(query, conn)
    return result 

def get_trip_id(trip_id, conn):
    query = f"""SELECT * FROM trips WHERE id = {trip_id}"""
    result = pd.read_sql_query(query, conn)
    return result

def get_trips_by_start_station(station_id, conn):
    query = f"""SELECT *
    FROM trips
    WHERE start_station_id='{station_id}'"""
    result = pd.read_sql_query(query, conn)
    return result

def get_trips_by_end_station(station_id, conn):
    query = f"""SELECT *
    FROM trips
    WHERE end_station_id='{station_id}'"""
    result = pd.read_sql_query(query, conn)
    return result

def insert_into_stations(data, conn):
    query = f"""INSERT INTO stations values {data}"""
    try:
        conn.execute(query)
    except:
        return 'Error'
    conn.commit()
    return 'OK'

def insert_into_trips(data, conn):
    query = f"""INSERT INTO trips values {data}"""
    try:
        conn.execute(query)
    except:
        return 'Error'
    conn.commit()
    return 'OK'

def get_all_avg_duration(conn):
    query = f"""SELECT bikeid, AVG(duration_minutes) AS avg_duration
    FROM Trips
    GROUP BY bikeid"""
    result = pd.read_sql_query(query, conn)
    return result

def get_bike_id_avg_duration(bike_id, conn):
    query = f"""SELECT bikeid, AVG(duration_minutes) AS avg_duration
    FROM Trips
    WHERE bikeid = '{bike_id}'"""
    result = pd.read_sql_query(query, conn)
    return result

###route###
@app.route('/')
def home():
    return 'Connection Succesfully Created!'

@app.route('/stations/')
def route_all_stations():
    conn = make_connection()
    stations = get_all_stations(conn)
    return stations.to_json()

@app.route('/trips/')
def route_all_trips():
    conn = make_connection()
    trips = get_all_trips(conn)
    return trips.to_json()

@app.route('/trips/average_duration') 
def route_average_duration():
    conn = make_connection()
    average_duration=get_all_avg_duration(conn)
    return average_duration.to_json()

@app.route('/stations/<station_id>')
def route_stations_id(station_id):
    conn = make_connection()
    station = get_station_id(station_id, conn)
    return station.to_json()

@app.route('/trips/<trip_id>')
def route_trips_id(trip_id):
    conn = make_connection()
    trips = get_trip_id(trip_id, conn)
    return trips.to_json()

@app.route('/trips/average_duration/<bike_id>')
def route_average_duration_bike_id(bike_id):
    conn = make_connection()
    average_duration = get_bike_id_avg_duration(bike_id, conn)
    return average_duration.to_json()

@app.route('/json', methods=['POST']) 
def json_example():
    req = request.get_json(force=True)
    name = req['name']
    age = req['age']
    address = req['address']
    return (f'''Hello {name}, your age is {age}, and your address in {address}''')

@app.route('/trips/start_station/<station_id>')
def route_trip_start_station(station_id):
    conn = make_connection()
    trip_start_station = get_trips_by_start_station(station_id, conn)
    return trip_start_station.to_json()

@app.route('/trips/end_station/<station_id>')
def route_trip_end_station(station_id):
    conn = make_connection()
    trip_end_station = get_trips_by_end_station(station_id, conn)
    return trip_end_station.to_json()

@app.route('/stations/add', methods=['POST']) 
def route_add_station():
    data = pd.Series(eval(request.get_json(force=True)))
    data = tuple(data.fillna('').values)   
    conn = make_connection()
    result = insert_into_stations(data, conn)
    return result

@app.route('/trips/add', methods=['POST']) 
def route_add_trip():
    data = pd.Series(eval(request.get_json(force=True)))
    data = tuple(data.fillna('').values)   
    conn = make_connection()
    result = insert_into_trips(data, conn)
    return result

@app.route('/analyse/trips_start_time', methods=['POST'])
def analyse():  
    input_data = request.get_json() 
    specified_date = input_data['period'] 
    conn = make_connection()
    query = f"SELECT * FROM trips WHERE start_time LIKE '{specified_date}%'"
    selected_data = pd.read_sql_query(query, conn)
    result = selected_data.groupby('start_station_id').agg({
        'bikeid': 'count', 
        'duration_minutes': 'mean'
    })
    return result.to_json()

###app settings###
if __name__ == '__main__':
    app.run(debug=True, port=5000)
