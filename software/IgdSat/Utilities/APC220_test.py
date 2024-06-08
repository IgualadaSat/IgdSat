import serial
import time
import random

ser = serial.Serial('/dev/ttyS0',9600)
ser.flushInput()

while True:
    ser.write( ("Test-%s\n\n" % str(random.randint(1,100)) ).encode() )
    time.sleep(1)
