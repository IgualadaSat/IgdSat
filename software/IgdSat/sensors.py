import asyncio
import time
import json
import os

#bmp280
import board
import busio
import adafruit_bmp280

#sensirion
from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection, CrcCalculator
from sensirion_i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_scd30.device import Scd30Device

# Raspberry pi internal features
import psutil # CPU usage 
import gpiozero as gz # CPU temperature 

# Other IgdSat scripts...
#   CommunicationModule
from CommunicationModule import *
#   RadSens
import RadSens

async def InitializeSensors(igdsat):

    #Activating bmp280...
    print("Activating bmp280...")
    try:
        i2c = busio.I2C(3, 2)
        igdsat.bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c,118)
    except:
        print("ERROR: Couldn't connect to bmp280")
        print("Overriding temperature and pressure measurement...")
        igdsat.bmp = None

    #Activating sensirion...
    print("Activating sensirion...")
    i2c_transceiver = LinuxI2cTransceiver('/dev/i2c-1')
    tries=0
    while tries < 5:
        try:
            channel = I2cChannel(I2cConnection(i2c_transceiver),slave_address=0x61,crc=CrcCalculator(8, 0x31, 0xff, 0x0))
            
            igdsat.sensirion = Scd30Device(channel)
            sensirion = igdsat.sensirion
            sensirion.stop_periodic_measurement()
            sensirion.soft_reset()
            sensirion.start_periodic_measurement(0)
            break
        except:
            print("ERROR sensirion connection, retrying...")
            await asyncio.sleep(0.5)
            tries += 1
            continue
    if tries >= 5:
        print("ERROR: Couldn't connect to sensirion Scd30")
        print("Overriding C02 and humidity measurement...")
        igdsat.sensirion = None

    #Activating RadSens...
    igdsat.radSens = RadSens.CG_RadSens(RadSens.RS_DEFAULT_I2C_ADDRESS)
    radSens = igdsat.radSens
    radSens.init()
    tries=0
    while tries < 10 :
        if not radSens.init():
            tries += 1
            await asyncio.sleep(0.5)
            continue
        else:
            break
    if tries >= 10:
        print("ERROR: Couldn't connect to RadSens")
        print("Overriding radiation measurement...")
        igdsat.radSens = None
    else:
        radSens.set_sensitivity(105)
        await asyncio.sleep(0.5)
        radSens.set_hv_generator_state(False)
        await asyncio.sleep(0.5)
        radSens.set_led_state(True)


async def SensorsReading( igdsat):
    await InitializeSensors(igdsat)
    await igdsat.CM.initialize()
    data = igdsat.DATA

    ActiveIterator=0 # 2 Iterations at dv>1m/s # 20 iterations to make standby 
    
    PreviousAltitude=0
    Iterator=1 # 1 second for standby, 0.5 seconds for active
    with open(os.path.expanduser('~') + "/IgdSat-DATA/DATA.txt", "a") as DataFile:
        DataFile.write("\n\n\nNew session...")
        try:
            while True:

                await asyncio.sleep(Iterator)
                try:
                    sensirion = igdsat.sensirion
                    if sensirion:
                        (a,b,c) = sensirion.read_measurement_data()
                        if a==a: # Looks redundant but it's neccessary to check for nan values
                            #(co2_concentration, temperature, humidity) = a,b,c
                            data["C"][0] = a # co2
                            data["T"][1] = b # scd-30 temperature
                            data["H"][0] = c # humidity
                    bmp = igdsat.bmp
                    if bmp:
                    #(temp2, altitude) = (sensor.temperature,sensor.altitude)
                        data["T"][0] = bmp.temperature
                        data["A"][0] = bmp.altitude
                        data["P"][0] = bmp.pressure

                    #Raspberry Pi Internal
                    data["T"][2] = gz.CPUTemperature().temperature
                    data["D"][0] = psutil.cpu_percent()
                    data["U"][0] = time.time()

                    #CM
                    CM = igdsat.CM
                    if CM:
                        data["G"] = [CM.GPS[0],CM.GPS[1]] # GPS coordinates
                        data["A"][1] = CM.GPS[2] # GPS altitude
                        data["S"] = CM.Signal
                        data["T"][3] = CM.CPUTemp

                    #RadSens
                    radSens = igdsat.radSens
                    if radSens:
                        a = radSens.get_rad_intensy_dynamic()
                        b = radSens.get_rad_intensy_static()
                        c = radSens.get_number_of_pulses()
                        data["R"] = [a,b,c]

                    # Active calculation

                    if PreviousAltitude != 0:
                        altitude_difference = abs(data["A"][0] - PreviousAltitude)
                        if igdsat.Active == False:
                            if altitude_difference >= 1.0:
                                ActiveIterator += 1
                            else:
                                ActiveIterator = 0
                            if ActiveIterator >= 2:
                                igdsat.Active = True
                                Iterator = 0.5
                                ActiveIterator = 0
                                igdsat.outputs.notes = [4400,1100,4400,1100,4400,1100] # Activating
                        else:
                            if altitude_difference < 1.0:
                                ActiveIterator += 1
                            else:
                                ActiveIterator = 0
                            
                            if ActiveIterator >= 20: # Static for 20 iterations --> 10 seconds
                                igdsat.Active = False
                                Iterator = 1
                                ActiveIterator = 0
                                igdsat.outputs.notes = [1100,0,1100,0,1100,0,1100] # Deactivating

                    igdsat.apc.print(str([data["U"][0] ,data["C"][0], data["T"][0], data["A"][0], data["P"][0], data["R"][0], data["G"][0],data["G"][1] ]))

                    PreviousAltitude=data["A"][0]
                    DataFile.write(json.dumps(data) + "\n")


                except KeyboardInterrupt:
                    raise
                except:
                    print("ERROR: Sensor measurement error")
                    pass

                #text = ""
                #text += f"\nCo2: {data[0]}\nTemperature-1: {data[1]}\nHumidity: {data[2]}"
                #text += "\nTemperature-2: " + str(round(data[3], 2))
                #text += "\nAltitude: " + str(round(data[4], 2))
                #text += "\nRadSens: " + str(data[5])
                #print(text)
                

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt!")
            print("Closing connections...")
            pass
