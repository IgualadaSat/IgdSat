import asyncio
import time
import json

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



#Activating bmp280...
print("Activating bmp280...")
i2c = busio.I2C(3, 2)
sensor = None
while sensor == None:
    try:
        sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c,118)
    except:
        print("ERROR bmp connection, retrying...")
        time.sleep(0.2)
        continue

#Activating sensirion...
print("Activating sensirion...")
i2c_transceiver = LinuxI2cTransceiver('/dev/i2c-1')
sensirion = None
while sensirion == None:
    try:
        channel = I2cChannel(I2cConnection(i2c_transceiver),slave_address=0x61,crc=CrcCalculator(8, 0x31, 0xff, 0x0))
        sensirion = Scd30Device(channel)
        sensirion.stop_periodic_measurement()
        sensirion.soft_reset()
        sensirion.start_periodic_measurement(0)
    except:
        print("ERROR sensirion connection, retrying...")
        time.sleep(0.5)
        continue

#Activating RadSens...
radSens = RadSens.CG_RadSens(RadSens.RS_DEFAULT_I2C_ADDRESS)
radSens.init()
time.sleep(1)
while not radSens.init():
    print("ERROR RadSens connection, retrying...")
    time.sleep(1)
radSens.set_sensitivity(105)
time.sleep(0.2)
radSens.set_hv_generator_state(False)
time.sleep(0.2)
radSens.set_led_state(True)

#Activating CommunicationModule
CM = CommunicationModule()



print("Sensors detected successfully!\n")

#DATA = [0,0,0,0,0,0,0,0,0,0] # 0 - co2, 1- temp1, 2- humidity, 3- temp2, 4 - altitude, 
#                        #  5 - rad_d, 6 - GpsLat, 7 - GpsLong, 8 - rad_s, 9 - rad_pulses
#                        #
DATA = {
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
async def SensorsReading(data, sensor, sensirion, CM, radSens, igdsat):
    ActiveIterator=0 # 2 Iterations at dv>1m/s # 20 iterations to make standby 
    
    PreviousAltitude=0
    Iterator=1 # 1 second for standby, 0.5 seconds for active
    with open("/home/igdsat/IgdSat-MPU/DATA.txt", "a") as DataFile:
        DataFile.write("\n\n\nNew session...")
        
        try:
            while True:

                await asyncio.sleep(Iterator)
                try:
                    (a,b,c) = sensirion.read_measurement_data()
                    if a==a: # Looks redundant but it's neccessary to check for nan values
                        #(co2_concentration, temperature, humidity) = a,b,c
                        data["C"][0] = a # co2
                        data["T"][1] = b # scd-30 temperature
                        data["H"][0] = c # humidity
                    #(temp2, altitude) = (sensor.temperature,sensor.altitude)
                        data["T"][0] = sensor.temperature
                        data["A"][0] = sensor.altitude
                        data["P"][0] = sensor.pressure

                    #Raspberry Pi Internal
                    data["T"][2] = gz.CPUTemperature().temperature
                    data["D"][0] = psutil.cpu_percent()
                    data["U"][0] = time.time()

                    #CM
                    data["G"] = [CM.GPS[0],CM.GPS[1]] # GPS coordinates
                    data["A"][1] = CM.GPS[2] # GPS altitude
                    data["S"] = CM.Signal
                    data["T"][3] = CM.CPUTemp

                    #RadSens
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

                    igdsat.apc.print(str([DATA["U"][0] ,DATA["C"][0], DATA["T"][0], DATA["A"][0], DATA["P"][0], DATA["R"][0], DATA["G"][0],DATA["G"][1] ]))

                    PreviousAltitude=data["A"][0]


                except KeyboardInterrupt:
                    raise
                except:
                    print("Comunication ERROR!")
                    pass

                #text = ""
                #text += f"\nCo2: {data[0]}\nTemperature-1: {data[1]}\nHumidity: {data[2]}"
                #text += "\nTemperature-2: " + str(round(data[3], 2))
                #text += "\nAltitude: " + str(round(data[4], 2))
                #text += "\nRadSens: " + str(data[5])
                #print(text)
                DataFile.write(json.dumps(data) + "\n")

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt!")
            print("Closing connections...")
            pass
