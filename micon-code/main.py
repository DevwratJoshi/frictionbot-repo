import time
import config
import friction_monitor as fm
from machine import Pin

HOST  = '192.168.11.56'
PORT = 9002
max_rec_bytes = 256
module_number = '3'
maxTime = 10
fric = fm.FrictionMonitor()
red_led = Pin(33, Pin.OUT)
green_led = Pin(32, Pin.OUT)
red_led.value(0)
green_led.value(0)
start_time = time.ticks_ms()

while time.ticks_diff(time.ticks_ms(), start_time) < maxTime*1000:
  if fric.query_friction_value():
    if(fric.high_friction):
      red_led.value(1)
      green_led.value(0)

    else:
      red_led.value(0)
      green_led.value(1)

  time.sleep(1.0)
  


