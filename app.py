# Import dependencies

from flask import Flask, jsonify
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import os


######################
# Database Setup
######################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station



######################
# Flask Setup
######################

# Create an App
app = Flask(__name__)

# Define route to homepage

@app.route("/")
def home():
        return (f"Welcome to Jeff's Weather Home Page<br/><br/>"
                f"Available Routes:<br/>"
                f"/api/v1.0/precipitation<br/>"
                f"/api/v1.0/stations<br/>" 
                f"/api/v1.0/tobs")


# Define route to precipitaton page
@app.route("/api/v1.0/precipitation")
def precip():

# Perform a query to retrieve the date and precipitation scores for last year

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    date_1yrago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    precip = session.query(Measurement.date.label("Date"), 
                    Measurement.prcp.label("Precipitation")).filter(Measurement.date>=date_1yrago).order_by(Measurement.date)

    session.close()

# Create a dictionary with date as the key and precip as the value
    all_precip=[]              
    for p in precip:
        precip_dict={}
        precip_dict[p.Date] = p.Precipitation
        all_precip.append(precip_dict)

# Return a json representation of the data
    return jsonify(all_precip)

# Define route to stations page
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the station from the Station table
    stations = session.query(Station.station).all()
    session.close()
    
    # convert list of tuples to normal list
    station_list = list(np.ravel(stations))

    # return JSON list of stations
    return jsonify(station_list)

# Define route to Temperature Page
@app.route("/api/v1.0/tobs")
def temps():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query last year of temp data
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    date_1yrago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    temps = session.query(Measurement.date, Measurement.tobs). \
            filter(Measurement.date>=date_1yrago).all()
    session.close()
    # Unpack the list of tuples

    # The instruction said to just return the tobs, but I don't think that makes sense
    # so I am creating a dictionary with date as the key tobs as value and returning that

    all_temps=[]              
    for t in temps:
        temp_dict={}
        temp_dict[t.date] = t.tobs
        all_temps.append(temp_dict)


    return jsonify(all_temps)


# Define route to Temperature Start Range Analysis
@app.route("/api/v1.0/<start>")
def starttemp(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    starttemps=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), 
            func.max(Measurement.tobs)).filter(Measurement.date>start).all()
    session.close()
  
    return jsonify(starttemps)


# Define route to Temperature Start/End Range Analysis
@app.route("/api/v1.0/<start>/<end>")
def startendtemp(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    startendtemps=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), 
            func.max(Measurement.tobs)).filter(Measurement.date>=start) \
            .filter(Measurement.date<=end).all()
    session.close()
  
    return jsonify(startendtemps)



# Run in development mode
if __name__ == "__main__":
    app.run(debug=True)