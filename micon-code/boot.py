# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

import network 
import config
import time 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

b = [code[0] for code in wlan.scan()]

if config.bunri_wifi["ssid"] in b :
	print("Found lab network")
	wlan.connect(config.bunri_wifi["ssid"], config.bunri_wifi["pass"]) 

time.sleep(2)
# import main



