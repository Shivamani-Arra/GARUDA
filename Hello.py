import argparse
import os
import socket
import sys
import time
import speedtest
from serial.tools.list_ports import comports

from dronekit import LocationGlobalRelative, VehicleMode
from dronekit import connect 
from flask import Flask, jsonify, render_template, request,redirect, url_for
from flask_socketio import SocketIO, emit
from pymavlink import mavutil
from socketio import Namespace
import logging
from port import ask_for_port


app=Flask(__name__,static_folder='static', static_url_path='/static')
with open('app_log.log', 'w'):
    pass
logging.basicConfig(filename='app_log.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
vehicle=None
app.config['SECRET_KEY']="Garuda"
socketio = SocketIO(app,cors_allowed_origins="*")
altitude = 0
yaw = 0
def get_parameters():
    global vehicle
    global altitude
    while(1):
        socketio.emit('alt', {'data': altitude})
    

def condition_yaw_at_current_location(heading, relative=False):
    global vehicle
    if relative:
        is_relative = 1  # yaw relative to the direction of travel
    else:
        is_relative = 0  # yaw is an absolute angle

    # create the CONDITION_YAW command using command_long_encode()
    msg = vehicle.message_factory.command_long_encode(
        0, 0,  # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW,  # command
        0,  # confirmation
        heading,  # param 1, yaw in degrees
        0,  # param 2, yaw speed deg/s
        1,  # param 3, direction -1 ccw, 1 cw
        is_relative,  # param 4, relative offset 1, absolute angle 0
        0, 0, 0)  # param 5 ~ 7 not used

    vehicle.send_mavlink(msg)

    timeout=10
    start_time = time.time()
    while time.time() - start_time < timeout:
        newyaw = vehicle.heading
        print("yaw : ",newyaw)
        socketio.emit('yaw',{'data': newyaw})
        time.sleep(1)


def send_message():
    socketio.emit('server_message', {'data': 'Hello from Flask!'}, room=request.sid)


def start_client():
   st = speedtest.Speedtest()
   st.get_best_server()
   download_speed=st.download()
   upload_speed=st.upload()
   print("Download Speed:", download_speed)
   print("Upload Speed:", upload_speed)
   print("Ping:", st.results.ping)
   download_speed_mbps = download_speed / (1024 * 1024)
   upload_speed_mbps = upload_speed/ (1024 * 1024)
   print("Download Speed (Mbps):", download_speed_mbps)
   print("Upload Speed (Mbps):", upload_speed_mbps)
   return download_speed_mbps,upload_speed_mbps
   
@app.route('/')
def start():
   return render_template("About_page.html")
@app.route("/main1",methods=['POST','GET'])
def goto_page():
   return render_template('Goto.html')
@socketio.on('connect')
def handle_connect():
    global vehicle
    print(f'Client connected: {request.sid}')
    socketio.emit('alt', {'data': altitude})
    socketio.emit('yaw', {'data': yaw})
@app.route("/connect",methods=['POST'])
def connect_vehicle():
   if request.method=='POST':
      s1=ask_for_port()
      print("s1: ",s1)
      if(s1==[]):
         # s1="udp:192.168.2.102:14553"
         s1="tcp:172.168.0.179:5760"
      else:
         
         print(len(s1))
         s1=s1[0]
      try:
         global vehicle 
         vehicle= connect1(s1)
         print(vehicle)
      except Exception as e:
         print(f"Failed to connect: {str(e)}")

      vehicle.wait_ready('autopilot_version')
      print(vehicle.location.global_relative_frame)
      while not vehicle.gps_0.fix_type > 2:
         print('Waiting for GPS fix...')
         time.sleep(1)

      # Get satellite information
      num_satellites = vehicle.gps_0.satellites_visible
      print(f'Number of satellites: {num_satellites}')
      if(int(vehicle.location.global_relative_frame.alt)<=0):
         return render_template('takeoff.html')
      else:
         return render_template('Goto.html')
def connect1(s):
   vehicle = connect(s, wait_ready=True,baud=56700)
   # vehicle = connect(s, wait_ready=True)
   print("\nConnecting to vehicle on: %s" % s)
   print(vehicle.battery.level)
   return vehicle
@app.route("/index")
def index():
    return render_template("index.html")
@app.route("/getData",methods=['POST'])
def getData():
   global vehicle
   altitude = vehicle.location.global_relative_frame.alt
   print(altitude,vehicle.heading)
   socketio.emit('alt', {'data': altitude})
   socketio.emit('yaw', {'data': vehicle.heading})
   return "hi"
@app.route('/main',methods=['POST'])
def arm_and_takeoff():
   global vehicle
   if(int(vehicle.location.global_relative_frame.alt)<=0):
      if request.method == 'POST':
         alt =int(request.json.get('altitude'))
         # x=dataTrans()
         x=10
         # connection_string = 'udp:127.0.0.1:14550'
         print(" Waiting for vehicle to initialise... %s "% vehicle)
         while not vehicle.is_armable:
            print(" Waiting for vehicle to initialise...")
            time.sleep(1)

         print("Arming motors")
      # Copter should arm in GUIDED mode
         vehicle.mode = VehicleMode("GUIDED")
         vehicle.armed = True

      # Confirm vehicle armed before attempting to take off
         while not vehicle.armed:
            print(" Waiting for arming...")
            time.sleep(1)

         print("Taking off!")
         vehicle.simple_takeoff(alt)
         while True:
            altitude = vehicle.location.global_relative_frame.alt
            print(" Altitude: ", vehicle.location.global_relative_frame.alt,vehicle.location.global_relative_frame)
            # Break and return from function just below target altitude.
            socketio.emit('alt', {'data': altitude})
            socketio.emit('yaw', {'data': vehicle.heading})
            if vehicle.location.global_relative_frame.alt >= alt * 0.95:
                  print("Reached target altitude")
                  socketio.emit('alt',{'data':alt})
                  break
            time.sleep(1)
         print(vehicle.battery)
         return render_template("index.html")
   else:
      alt =int(request.json.get('altitude'))
      point1 = LocationGlobalRelative(vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon,alt)
      if(vehicle.mode!="GUIDED"):
         vehicle.mode = VehicleMode("GUIDED")
      vehicle.armed = True
      while not vehicle.armed:
         print(" Waiting for arming...")
         time.sleep(1)
      print("goto!")
      vehicle.simple_goto(point1)
      while True:
         print(" Altitude: ", vehicle.location.global_relative_frame.alt,int(vehicle.location.global_relative_frame.lat*1000))
         currAlt = vehicle.location.global_relative_frame.alt
         print("Altitude: ", currAlt)
         socketio.emit('alt', {'data': currAlt})
         socketio.emit('yaw', {'data': vehicle.heading})
         if currAlt >= alt * 0.95 and currAlt <= alt * 1.05:
               print(f"Reached new target altitude: {currAlt}")
               time.sleep(1)
               socketio.emit('alt', {'data': alt})
               socketio.emit('yaw', {'data': vehicle.heading})
               break
         time.sleep(1)
      print("hi")
      # return render_template("index.html",alt=vehicle.location.global_relative_frame.alt,dir=vehicle.heading,speed=vehicle.airspeed,connectionSpeed=50)
@app.route('/return_to_home' ,methods=['POST'])
def return_to_home():
   global vehicle
   try:
      vehicle.mode = VehicleMode("RTL")
      while not vehicle.mode.name == 'RTL':
         pass
      while True:
         socketio.emit('alt', {'data': vehicle.location.global_relative_frame.alt})
         if(vehicle.location.global_relative_frame.alt<=0.3):
            socketio.emit('alt', {'data': 0})
            break
         time.sleep(1)
      return render_template("/")
   except Exception as e:
      if(vehicle.location.global_relative_frame.alt<=0.3):
         return render_template("/")
@app.route('/Land',methods=['POST','GET'])
def land():
   global vehicle
   try:
      vehicle.mode = VehicleMode("LAND")
      while True:
         socketio.emit('alt', {'data': vehicle.location.global_relative_frame.alt})
         if(vehicle.location.global_relative_frame.alt<=0.3):
            socketio.emit('alt', {'data': 0})
            break
         time.sleep(1)
      return render_template("takeoff.html")
   except Exception as e:
      return render_template("index.html")
@app.route("/change_yaw",methods=['GET','POST'])
def change_yaw():
   
   # yaw = int(request.json.get('yaw', 0))
   # while True:
   #    vehicle.channels.overrides['4'] = 1500
   #    if yaw - 1 <= int(vehicle.heading) <= yaw + 1:
   #       break
   #    desired_yaw = 1550
   #    vehicle.channels.overrides['4'] = int(desired_yaw)
   #    time.sleep (0.1)
   #    socketio.emit('yaw', {'data': vehicle.heading})
   #    print(vehicle.heading)
   #    vehicle.channels.overrides['4'] = 1500
   # # x=dataTrans()
   #    # x=50
   # time.sleep(1)
   yaw = int(request.json.get('yaw'))
   headingval=vehicle.heading
   socketio.emit('yaw', {'data':headingval})
   condition_yaw_at_current_location(yaw)
   time.sleep(5)
   response_data = {"message": "Done!"}
   return jsonify(response_data)
@app.route("/networkspeed", methods=['POST'])
def network_speedtest():
    print("Speed test started")
   #  speeds = start_client()
   #  download_speed, upload_speed = speeds
    download_speed,upload_speed=start_client()
    print("1, ",download_speed," 2",upload_speed)

    response_data = {
        "download_speed": download_speed,
        "upload_speed": upload_speed
    }
    return jsonify(response_data)
if __name__=='__main__':
   # Initialize the socket before running the Flask app
   socketio.run(app, debug=True,host='0.0.0.0', port=5500)