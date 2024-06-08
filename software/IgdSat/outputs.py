from gpiozero import  LED, PWMOutputDevice
import asyncio


class Outputs():
    def __init__(self) -> None:
        self.b = PWMOutputDevice(13,True,0.1, 4400)
        self.b.value = 0
        self.l=LED(26)
        self.notes = [1100,0,2200,0,2200,0] # bootup sound
        self.led = [1,1,0,0] # default led interval
        self._ledPos = 0
        self.alarm = False

    async def serve(self):
         while True:
            # Buzzer iterator
            if len(self.notes) != 0:
                if self.notes[0] == 0: # if freq is 0 then silence
                    self.value = 0
                else:
                    self.b.value = 0.1
                    self.b.frequency = self.notes[0]
                self.notes = self.notes[1:]
            elif self.alarm:
                if self.b.value == 0.1:
                    self.b.value = 0
                else:
                    self.b.value = 0.1
            else:
                self.b.value = 0
            
            # Led iterator
            if self._ledPos >= len(self.led):
                self._ledPos = 0
            
            if self.led[self._ledPos] == 1:
                self.l.on()
            else:
                self.l.off()
            self._ledPos += 1


            await asyncio.sleep(0.1)
                 