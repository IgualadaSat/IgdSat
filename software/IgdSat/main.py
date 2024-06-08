#!/usr/bin/env python

import asyncio
import itertools
import json
import websockets
import subprocess

print("Initializing IgdSat...")
#IgdSat scripts...
from outputs import *

from sensors import *
from camera import *
from APC import APC

class IgdSat():
    def __init__(self) -> None:
        self.outputs = Outputs()
        self.bmp = None
        self.sensirion = None
        self.CM = CommunicationModule()
        self.RadSens = None
        #DATA = [0,0,0,0,0,0,0,0,0,0] # 0 - co2, 1- temp1, 2- humidity, 3- temp2, 4 - altitude, 
        #                        #  5 - rad_d, 6 - GpsLat, 7 - GpsLong, 8 - rad_s, 9 - rad_pulses
        #                        #
        DATA = { # The data packet structure
            "U": [0], # Unix time
            "C": [0], # Co2
            "T": [0,0,0,0], # Temperature [BME, SCD-30, MPU-temp, CM-temp]
            "H": [0], # Humidity
            "A":[0,0], # Altitude [Pressure-based, GPS-based]
            "P":[0], # Barometric pressure
            "R": [0,0,0], # Radiation [Dinamic-rad,Static-rad, Pulses]
            "G": [0,0], # GPS [LAT, LONG]
            "S": [0,0], # Signal for LTE [RSSI signal, bit error rate]
            "D": [0] # Debuging [CPU-usage]
        }
        self.DATA = DATA
        self.Active = False # Active mode means High-Speed data collection during parachute descent
        self.apc = None

igdsat = IgdSat()
encoder.igdsat = igdsat
igdsat.outputs.notes = [1100,2200,1100,2200]
igdsat.apc = APC(igdsat)
DATA=igdsat.DATA
# Websocket handler
async def handler(websocket):
    print("New connection")
    igdsat.outputs.notes = [1000,2000,3000,4000]
    igdsat.outputs.led = [1,0]
    try:
        while True:
            await websocket.send(json.dumps(DATA))
            Interval = 1
            if igdsat.Active:
                Interval = 0.5
            await asyncio.sleep(Interval)
    except Exception as e:
        igdsat.outputs.notes = [4000,3000,2000,1000]
        igdsat.outputs.led = [1,1,0,0]
        raise e

# Internet checker...
async def InternetCheck():
    failed=0
    while True:
        try:
            result = await asyncio.create_subprocess_shell("ping -c 2 -W 3 10.8.0.1", # To check that VPN works
                                                           stdout=subprocess.PIPE,
                                                           stderr=subprocess.PIPE)
            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                failed = 0
                continue
            else:
                failed += 1
                if failed == 2:
                    failed = 0
                    # In case it fails --> restart VPN
                    igdsat.outputs.notes = [4400,0,4400,0,2200,0,2200,0,4400,0,4400,0,2200,0,2200,0]
                    await asyncio.create_subprocess_shell("sudo service openvpn restart", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    await asyncio.sleep(3)

        except Exception as e:
            print("PING ERROR")
            continue

        await asyncio.sleep(2)

# Asyncio asyncronous execution
async def main():
    async with websockets.serve(handler, "", 8001):
        #await asyncio.Future()  # run forever
        await run_web_server()
        await asyncio.gather(  SensorsReading(igdsat), igdsat.CM.serve(), igdsat.outputs.serve(), InternetCheck() )


if __name__ == "__main__":
    asyncio.run(main())
