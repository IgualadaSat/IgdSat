import serial
import time
import asyncio
import subprocess


# AT commands sheet
# AT+CPMUTEMP (Temperature)
# AT+CSQ   (Signal strength) --> 2 values
# AT+CGPSINFO  (GPS info)
# AT+CGPS=1  (Activate GPS)

class CommunicationModule():
    def __init__(self) -> None:
        self.Signal = [0,0]
        self.CPUTemp = 0
        self.GPS = [0,0,0] # [LAT,LONG,Altitude]
        self.gps = serial.Serial('/dev/ttyUSB2',115200)
        self.gps.flushInput()
        self.SendCommand("AT+CGPS=1")
        _gps=False
        while _gps==False:
            time.sleep(0.5)
            if self.gps.inWaiting():
                    self.gps.read(self.gps.inWaiting())
                    print("GPS detected")
                    _gps=True
            else:
                print("No response from CM, retrying...")
                self.gps.close()
                continue

    def SendCommand(self,command):
          self.gps.write(('%s\r\n' % command).encode())

    async def AsyncCommand(self,command):
        self.SendCommand(command)
        waiting=0
        while not self.gps.in_waiting:
            await asyncio.sleep(0.05)
            waiting +=0.05
            if waiting > 2:
                print("No response from CM, retrying...")
                self.gps.close()
                await asyncio.sleep(0.2) 
                self.gps = serial.Serial('/dev/ttyUSB2',115200)
                self.gps.flushInput() 
                self.SendCommand("AT+CGPS=1")
                await asyncio.sleep(0.5) 
                self.read(self.gps.inWaiting() )
                await asyncio.sleep(0.5) 
                return 0
        b = self.gps.read(self.gps.inWaiting()).decode()
        if b=="\r\nERROR\r\n":
            return "ERROR"
        
        b = b[b.find("+C"):]
        b = b[:b.find("\r")]
        b = b[b.find(": ")+2:]
        b = b.split(",")
        return b # Array of values returned by the command
        
    async def serve(self): # Non-blocking data gathering
        while True:
            try:
                self.CPUTemp = float((await self.AsyncCommand("AT+CPMUTEMP"))[0])
                await asyncio.sleep(0.1)
                Signal = await self.AsyncCommand("AT+CSQ")
                self.Signal[0] = int(Signal[0])
                self.Signal[1] = int(Signal[1])
                await asyncio.sleep(0.1)
                self.GPS = self.GpsGathering(await self.AsyncCommand("AT+CGPSINFO"))
            except:
                print("CM ERROR")
                pass
            await asyncio.sleep(0.3)
          
    def GpsGathering(self,data):
            if data[0] == "":
                  return [0,0,0]
        
            Lat = data[0][:2]
            SmallLat = data[0][2:]
            NorthOrSouth = data[1]

            Long = data[2][:3]
            SmallLong = data[2][3:]
            EastOrWest = data[3]

            FinalLat = float(Lat) + (float(SmallLat)/60)
            FinalLong = float(Long) + (float(SmallLong)/60)

            if NorthOrSouth == 'S': FinalLat = -FinalLat
            if EastOrWest == 'W': FinalLong = -FinalLong
            altitude = float(data[6])
            #print(FinalLat, FinalLong)

            return [FinalLat, FinalLong, altitude]