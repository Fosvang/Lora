#!/usr/bin/env python3

import struct
from collections import OrderedDict
import json

"""
Example: 9e16411954000194897013130c0f
FLAGS
7 Presence of temperature information 0 or 1
6 Transmission triggered by the accelerometer 0 or 1
5 Transmission triggered by pressing pushbutton 1 0 or 1
4 Presence of GPS information 0 or 1
3 Presence of Uplink frame counter 0 or 1
2 Presence of Downlink frame counter 0 or 1
1 Presence of battery level information 0 or 1
0 Not used always is set to 0

"""

class Payload:
    def __init__(self, payload_string):
        payload = bytes.fromhex(payload_string)
        self.flags, self.data = payload[0], payload_string[2:]
        self._decode()
        
    @property
    def source(self):
        if self.flags & (1 << 6):
            return 'Accelerometer'
        elif self.flags & (1 << 5):
            return 'Button'
        else:
            return 'Periodic'
    
    def _decode(self):
        #See: https://www.adeunis.com/wp-content/uploads/2017/08/FTD_sigfox_RC1_UG_FR_GB_V1.1.3.pdf
        index = 0
        if self.flags & (1 << 7):
            self.temperature = int(self.data[:index+2], 16)
            index += 2
        if self.flags & (1 << 4):
            lat = self.data[index:index+8]
            deg  = int(lat[:2])
            min  = lat[2:4]
            frac = lat[4:7]
            dir  = 1 if (int(lat[7]) & 0x1) == 0 else -1
            deg  = dir * (deg + float(min+'.'+frac) / 60)
            self.latitude = '{0:.4f}'.format(deg)
            
            lng  = self.data[index+8:index+16]
            deg  = int(lng[:3])
            min  = lng[3:5]
            frac = lng[5:7]
            deg  = dir * (deg + float(min+'.'+frac) / 60)
            self.longitude = '{0:.4f}'.format(deg)
            
            self.quality = int(self.data[index+16: index+18], 16)
            index += 18
        else:
            self.latitude = ''
            self.longitude = ''
            self.quality = ''
        if self.flags & (1 << 3):
            self.uplink = int(self.data[index:index+2], 16)
            self.downlink = int(self.data[index+2:index+4], 16)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        data = sys.argv[1]
    else:
        data = sys.stdin.readline().strip()
    p = Payload(data)
    print(p.source)
    print(p.temperature)
    print(p.latitude)
    print(p.longitude)
    print(p.quality)
    print(p.uplink)
    print(p.downlink)