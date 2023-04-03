# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///C:/Users/hasan/Data Analytics/Projects/Modules/week10/sqlalchemy-challenge/Surfsup/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station
# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    
    return (
        f"List of all available routes:<br/><br/>"
        f"<a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation<a><br/>"
        f"<a href=\"/api/v1.0/stations\">/api/v1.0/stations<a><br/>"
        f"<a href=\"/api/v1.0/tobs\">/api/v1.0/tobs<a><br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    
    start_date = '2016-01-01'
    sel = [measurement.date, 
        func.sum(measurement.prcp)]
    precipitation = session.query(*sel).\
            filter(measurement.date >= start_date).\
            group_by(measurement.date).\
            order_by(measurement.date).all()
   
    session.close()

 
    precipitation_dates = []
    precipitation_total = []

    for date, dailytotal in precipitation:
        precipitation_dates.append(date)
        precipitation_total.append(dailytotal)
    
    precipitation_dict = dict(zip(precipitation_dates, precipitation_total))

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
   
    session = Session(engine)

    sel = [measurement.station]
    active_stations = session.query(*sel).\
        group_by(measurement.station).all()
    session.close()


    list_of_stations = list(np.ravel(active_stations)) 
    return jsonify(list_of_stations)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    start_date = '2016-08-23'
    sel = [measurement.date, 
        measurement.tobs]
    station_temp = session.query(*sel).\
            filter(measurement.date >= start_date, measurement.station == 'USC00519281').\
            group_by(measurement.date).\
            order_by(measurement.date).all()

    session.close()

    observation_dates = []
    temperature_observations = []

    for date, observation in station_temp:
        observation_dates.append(date)
        temperature_observations.append(observation)
    
    most_active_tobs_dict = dict(zip(observation_dates, temperature_observations))

    return jsonify(most_active_tobs_dict)

@app.route("/api/v1.0/<start_date>")
def start_date(start_date):

    session = Session(engine)
    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    return jsonify(trip_stats)
      
@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_date(start_date, end_date):

    session = Session(engine)
    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    return jsonify(trip_stats)
     

    
if __name__ == '__main__':
    app.run(debug=True)