#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO

import serial
import time

ser = serial.Serial('/dev/ttyUSB2',115200)
ser.flushInput()

rec_buff = ''

def send_at(command,back,timeout):
        rec_buff = ''
        ser.write((command+'\r\n').encode())
        time.sleep(timeout)
        if ser.inWaiting():
                time.sleep(0.01 )
                rec_buff = ser.read(ser.inWaiting())
        if rec_buff != '':
                if back not in rec_buff.decode():
                        print(command + ' ERROR')
                        print(command + ' back:\t' + rec_buff.decode())
                        return None
                else:
                    if ",,,," in rec_buff.decode():
                            print("GPS not ready")
                            return None

                    global GPSDATA
                    GPSDATA = str(rec_buff.decode())
                    Cleaned = GPSDATA[13:]

                    Lat = Cleaned[:2]
                    SmallLat = Cleaned[2:11]
                    NorthOrSouth = Cleaned[12]

                    Long = Cleaned[14:17]
                    SmallLong = Cleaned[17:26]
                    try:
                            EastOrWest = Cleaned[27]
                    except:
                            EastOrWest = "W"

                    FinalLat = float(Lat) + (float(SmallLat)/60)
                    FinalLong = float(Long) + (float(SmallLong)/60)

                    if NorthOrSouth == 'S': FinalLat = -FinalLat
                    if EastOrWest == 'W': FinalLong = -FinalLong

                    print(FinalLat, FinalLong)

                    return 1
        else:
                print('GPS is not ready')
                return 0

def get_gps_position():
        rec_null = True
        answer = 0
        while rec_null:
                
                answer = send_at('AT+CGPSINFO','+CGPSINFO: ',1)
                if not answer:
                    print("Still searching for satellites...")
                time.sleep(1.5)



print('Starting GPS test session...')

ser.write(('AT+CGPS=1\r\n').encode())
time.sleep(2)
if ser.inWaiting():
        time.sleep(0.01 )
        print(ser.read(ser.inWaiting()))
while True:

        get_gps_position()