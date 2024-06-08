
# Simple script to test IgdSat's outputs: a led and a buzzer 

# GPIO13 --> Buzzer (PWM)
# GPIO26 --> Yellow LED

from gpiozero import  LED, PWMOutputDevice
b = PWMOutputDevice(13,True,0.1, 4400) # Buzzer(13)
import time
#time.sleep(1000)
l=LED(26)
while True:
        l.on();b.value = 0.1;time.sleep(0.05);b.value = 0;l.off();b.frequency += 0;time.sleep(0.05)