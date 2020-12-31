from flask import Flask
from flask import jsonify

import requests

app = Flask(__name__)

target = 0
target_till = 0


@app.route('/')
def home():
    return 'Here is the server for the heating controller.   See the site here...'


def getAllData():
    data_heatingcontroller = requests.get('http://heating.lan/cm?cmnd=status%2010').json()
    data_stairs = requests.get('http://sonoff-2286.lan/cm?cmnd=status%2010').json()
    data_setpoints = requests.get('http://heating.lan/cm?cmnd=mem1').json()

    global target
    return {
      'oceanRoom': data_heatingcontroller['StatusSNS']['DS18B20-3']['Temperature'],
      'hotWater': data_heatingcontroller['StatusSNS']['DS18B20-1']['Temperature'],
      'hallTemperature': data_stairs['StatusSNS']['DS18B20']['Temperature'],
      'setOceanRoomTemperature': data_setpoints['Mem1'],
      'targetHallTemperature': target,
    }

def setSetpoint(temp):
    requests.get('http://heating.lan/cm?cmnd=mem1%20'+str(temp))

    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p") + "temp target is now " + str(temp) )


@app.route('/temp')
def temp():
    return jsonify(getAllData())

def setTarget(offset):
    x = getAllData();

    # Set setpoint to 2 deg hotter than now for 3 hours.
    global target
    global target_till

    target = x['hallTemperature'] + offset;
    target_till = time.time()+(3*3600);


    update_setpoints();


@app.route('/hotter')
def hotter():
  setTarget(2);
  return "ok"


@app.route('/colder')
def colder():
  setTarget(-2);
  return "ok"


import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler


def update_setpoints():
    global target
    global target_till
    if time.time()>target_till:
        # No specific instruction.  Use default temp chart.
        hour = int(time.strftime('%H'))

        temps_each_hour = [0,0,0,0,0,0,16,16,16, 14, 14, 14, 14, 14, 14, 14, 14, 14, 17, 17, 17, 17, 0, 0, 0 ];

        target = temps_each_hour[hour]

    x = getAllData();

    if x['hallTemperature']<target:
        setSetpoint(x['oceanRoom']+1);
    else:
        setSetpoint(x['oceanRoom']-1);


update_setpoints()

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_setpoints, trigger="interval", seconds=300)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())




