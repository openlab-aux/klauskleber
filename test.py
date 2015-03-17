#!/usr/bin/env python2

import serial
import io

#SOH = "\x0H"
STX = "\x02"
CR  = "\x0D"
ESC = "\x1B"


kk = serial.Serial(
        bytesize=8,
        baudrate=9600,
        port="/dev/ttyUSB1",
        timeout=0,
        parity="N",
        stopbits=1,
        xonxoff=1,
        rtscts=1)



if __name__ == "__main__":

    kk.write(STX+"KX0025"+CR) # set label length to 25mm
    #kk.write(STX+"K1503"+CR)  # set gap width

    kk.write(STX+"L"+CR) # enter label formatting mode

    kk.write(STX+"m") # metric
    kk.write(STX+"M0250"+CR) # 25mm

    kk.write("C0025") # vmargin 25mm
    kk.write("R0005") # hmargin 25mm

    kk.write("121100001000050OpenLab Augsburg"+CR)

    kk.write("E"+CR) # end label formatting mode


    kk.close()
