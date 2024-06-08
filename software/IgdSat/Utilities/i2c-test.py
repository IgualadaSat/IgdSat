import board
import busio
import adafruit_bmp280
import time
from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection, CrcCalculator
from sensirion_i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_scd30.device import Scd30Device


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

print("Sensors detected successfully!\n")

(co2_concentration, temperature, humidity, temp2, altitude) = (0,0,0,0,0)
with open("DATA.txt", "a") as DataFile:
    DataFile.write("\nNew session...")
    

    try:
        while True:
            time.sleep(0.5)
            try:
                (a,b,c) = sensirion.read_measurement_data()
                if a==a: # Looks redundant but it's neccessary to check for nan values
                    (co2_concentration, temperature, humidity) = a,b,c
                (temp2, altitude) = (sensor.temperature,sensor.altitude)
            except KeyboardInterrupt:
                raise
            except:
                print("Comunication ERROR!")
                pass

            text = ""
            text += f"\nCo2: {co2_concentration}\nTemperature-1: {temperature}\nHumidity: {humidity}"
            text += "\nTemperature-2: " + str(round(temp2, 2))
            text += "\nAltitude: " + str(round(altitude, 2))
            print(text)
            DataFile.write(text)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt!")
        print("Closing connections...")
        pass

i2c.deinit()
i2c_transceiver.close()

print("Bye!")
        #sensor.soft_reset()