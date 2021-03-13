# Dependencies and Setup
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#  Import Flask
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# Create an engine for the hawaii.sqlite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# Define what to do when a user hits the Home route
@app.route("/")
def welcome():
    return (
        f"Surf's Up!: Hawaii Climate API routes<br/>"
        f"===============================<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation  ------Precipitation Data<br/>"
        f"/api/v1.0/stations  ------Station List<br/>"
        f"/api/v1.0/tobs  -------Temperature Observation<br/>"
        f"/api/v1.0/2017-08-01  ------Start Day Temperature Observation<br/>"
        f"/api/v1.0/2017-08-01/2017-08-07  ------Start End Day Temperature Observation<br/>"
    )
# Define what to do when a user hits the Precipitation route
@app.route("/api/v1.0/precipitation")
def prcp():
    #Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Design a Query to Retrieve the Last 12 Months of Precipitation Data 
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= year_ago).\
            order_by(Measurement.date).all()

    session.close()
    #Convert list of Tuples into Dictionary
    all_prcp = []
    for date,prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    #Return the JSON representation of dictionary
    return jsonify(all_prcp)
    
# Define what to do when a user hits the Station route
@app.route("/api/v1.0/stations")
def stations():
    # List of stations from the dataset
    results= session.query(Station.name).all()

    session.close()

   # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    # Return JSON List of Stations from the Dataset
    return jsonify(all_stations)

# Define what to do when a user hits tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Query the dates and temperature observations of the most active station for the last year of data
    temp_data = session.query(Measurement.date,Measurement.tobs).\
         filter(Measurement.date >= year_ago).\
         filter(Measurement.station == 'USC00519281').\
    order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into normal list
    all_temps = []
    for date,temp in temp_data:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temp"] = temp
        all_temps.append(temp_dict)

    # Return a JSON list of temperature observations (TOBS) for the previous year
    return jsonify(all_temps)

# Define what to do when a user hits Start Day route
@app.route("/api/v1.0/<start>")
def start_day(start):
    temp_start = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
        all()

    session.close()

    # Convert list of tuples into normal list
    temp_start_list = []                       
    for result in temp_start:
        temp_dict = {}
        temp_dict["TMIN"] = result[0]
        temp_dict["TAVG"] = result[1]
        temp_dict["TMAX"] = result[2]
        temp_start_list.append(temp_dict)

    # Return a JSON list of temperature observations (TOBS) for the previous year
    return jsonify(temp_start_list)

# Define what to do when a user hits the Start-End Day route
@app.route("/api/v1.0/<start>/<end>")
def date_range(start,end):
    temp_range = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date)>= start).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).all()

    session.close()
    # Convert list of tuples into normal list
    temp_start_end_list = []                       
    for result in temp_range:
        temp_end_dict = {}
        temp_end_dict["TMIN"] = result[0]
        temp_end_dict["TAVG"] = result[1]
        temp_end_dict["TMAX"] = result[2]
        temp_start_end_list.append(temp_end_dict)

    # Return a JSON list of temperature observations (TOBS) for the previous year
    return jsonify(temp_start_end_list)

# Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
