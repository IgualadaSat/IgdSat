import serial
import time

class APC():
    def __init__(self,igdsat) -> None:
        self.igdsat = igdsat
        self.ser = serial.Serial('/dev/ttyS0',9600)
    
    def print(self,text):
        self.ser.write(str(text).encode())