# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

import network 
import config
import time 

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    b = [code[0] for code in wlan.scan()]

    if config.bunri_wifi["ssid"] in b :
      print("Found lab network")

    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(config.bunri_wifi["ssid"], config.bunri_wifi["pass"]) 
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    

do_connect() 




