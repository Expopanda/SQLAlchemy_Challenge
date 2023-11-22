# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
latest_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')
start_date = latest_date - dt.timedelta(days=365)
session.close()
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end"
    )
####################PRECIPITATION################
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
                                     
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= start_date).all()
    session.close()
    
    prcp_data = {result.date: result.prcp for result in results}
    return jsonify(prcp_data)



####################STATIONS#####################
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(station.station,station.name).all()
    session.close()

    all_stations = [{"station": result.station, "name": result.name} for result in results]
    return jsonify(all_stations)

#####################TOBS########################
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    results = session.query(measurement.date,measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= start_date).all()
    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps)
    
#####################START & END#################
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start=None, end=None):

#Min(TMIN), Max(TMAX), Avg(TAVG) for start date range of all stations
    if not end:
        session = Session(engine)
        start = dt.datetime.strptime(start, "%Y%m%d")
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start).all()
        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)

    start = dt.datetime.strptime(start, "%Y%m%d")
    end = dt.datetime.strptime(end, "%Y%m%d")

    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >=start).\
        filter(measurement.date <= end).all()
    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps=temps)
  

if __name__ == '__main__':
    app.run(debug=True)  