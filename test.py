#!/usr/bin/env python2

import serial
import io

#SOH = "\x0H"
STX = "\x02"
CR  = "\x0D"
ESC = "\x1B"

# 191100001800020OpenLab Augsburg  
#  |||||||||||||||_ text
#  ||||||||||||||_ x coord
#  ||||||||||_ y coord
#  ||||||_ fixed
#  |||_ fixed
#  |_ font


kk = serial.Serial(
        bytesize=8,
        baudrate=9600,
        port="/dev/ttyUSB0",
        timeout=0,
        parity="N",
        stopbits=1,
        xonxoff=1,
        rtscts=1)

if __name__ == "__main__":
    kk.write(STX+"m"+CR) # metric
    kk.write(STX+"KX0025"+CR) # 25mm
    kk.write(STX+"L"+CR) # enter label formatting mode

    kk.write("1W1c55000002000202000000000http://dinge.openlab-augsburg.de/ding/0000000001"+CR)

    kk.write("191100001800020OpenLab Augsburg                 openlab-augsburg.de"+CR)
    kk.write("121100001100210ID: 0000000001"+CR)

    kk.write("111100000300210owner: hannes"+CR)
    kk.write("111100000300610maintainer: hannes"+CR)

    kk.write("E"+CR) # end label formatting mode

    kk.close()
