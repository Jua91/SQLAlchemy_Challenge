import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask,jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine,reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask routes
@app.route("/")
def home():

    return(
        f"Available Routes <br/>"
        f"Precipitation for the last year: /api/v1.0/precipitation <br/>"
        f"List of stations: /api/v1.0/stations <br/>"
        f"Temperature Observations of the most active station for the last year: /api/v1.0/tobs <br/>"
        f"Temperature Statistics from start date: /api/v1.0/(yyyy-mm-dd) <br/>"
        f"Temperature Statistics from start date to end date: /api/v1.0/(yyyy-mm-dd)/(yyyy-mm-dd) <br/>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session from python to database
    session = Session(engine)

    # Get the latest date from the database
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # Convert the latest date into readable string
    latest_date_str = dt.datetime.strptime(latest_date,"%Y-%m-%d")
    # Get the date one year ago from the latest date
    one_year_ago = latest_date_str - dt.timedelta(days=365)
    # Convert the date into string format date
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")

    # Query all date and precipitation data
    date_prcp = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=one_year_ago_str).all()

    session.close()

    # Convert list of tuples into dictionary
    prcp_dict_list=[]
    for date,prcp in date_prcp:
        prcp_dict={}
        prcp_dict["date"]=date
        prcp_dict["prcp"]=prcp
        prcp_dict_list.append(prcp_dict)
    
    return jsonify(prcp_dict_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create a session from python to database
    session = Session(engine)
    # Query the list of stations
    stations = session.query(Station.station, Station.name).all()
    
    session.close()

    # Convert list of tuples into dictionary
    station_dict_list = []
    for station_id,station_name in stations:
        station_dict={}
        station_dict["ID"] = station_id
        station_dict["Name"] = station_name
        station_dict_list.append(station_dict)
    
    return jsonify(station_dict_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create a session from python to database
    session = Session(engine)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date_str = dt.datetime.strptime(latest_date,"%Y-%m-%d")
    one_year_ago = latest_date_str - dt.timedelta(days=365)
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")
    # Query the dates and temperature observations of the most active station for the last year of data
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    date_tobs = session.query(Measurement.date,Measurement.tobs).filter(func.strftime('%Y-%m-%d',Measurement.date)>=one_year_ago_str).filter(Measurement.station == most_active_station).all()
    
    session.close()

    # Convert list of tuples into dictionary
    tobs_dict_list = []
    for date,tobs in date_tobs:
        tobs_dict = {}
        tobs_dict["date"]=date
        tobs_dict["tobs"]=tobs
        tobs_dict_list.append(tobs_dict)
    
    return jsonify(tobs_dict_list)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    # Create a session from python to database
    session = Session(engine)
    # Query temperature statistics from the start date to the latest date
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    temp = session.query(*sel).filter(func.strftime("%Y-%m-%d",Measurement.date)>=start).all()
    
    session.close()

    # Convert list of tuple into dictionary
    for tmin,tavg,tmax in temp:
        temp_stat = {}
        temp_stat["Minimum Temperature"]=tmin
        temp_stat["Average Temperature"]=tavg
        temp_stat["Maximum Temperature"]=tmax

    return jsonify(temp_stat)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start,end):
    # Create a session from python to database
    session = Session(engine)
    # Query temperature statistics from the start date to the end date
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    temp = session.query(*sel).filter(func.strftime("%Y-%m-%d",Measurement.date)>=start).filter(func.strftime("%Y-%m-%d",Measurement.date)<=end).all()
    
    session.close()

    # Convert list of tuple into dictionary
    for tmin,tavg,tmax in temp:
        temp_stat = {}
        temp_stat["Minimum Temperature"]=tmin
        temp_stat["Average Temperature"]=tavg
        temp_stat["Maximum Temperature"]=tmax

    return jsonify(temp_stat)

if __name__ == '__main__':
    app.run(debug=True)