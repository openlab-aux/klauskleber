#!/usr/bin/env python2

import serial
import qrcode
from StringIO import StringIO
import sys
from argparse import ArgumentParser

#SOH = "\x0H"
STX = "\x02"
CR  = "\x0D"
ESC = "\x1B"

#ID = "135792468228"
ID =  "000000000001"

# 191100001800020OpenLab Augsburg
#  |||||||||||||||_ text
#  ||||||||||||||_ x coord
#  ||||||||||_ y coord
#  ||||||_ fixed
#  |||_ fixed
#  |_ font


kk = serial.Serial(
        bytesize=8,
        baudrate=19200,
        port="/dev/ttyUSB1",
        timeout=0,
        parity="N",
        stopbits=1,
        xonxoff=1,
        rtscts=1)


qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_Q,
    box_size=2,
    border=0,
)



if __name__ == "__main__":

    argparser = ArgumentParser(description="controls klauskleber")
    argparser.add_argument("--id", help="12 digits thing ID", required=True)
    argparser.add_argument("--name", help="thing name (18 chars max)", required=True)
    argparser.add_argument("--own", help="thing owner",default="OpenLab", required=False)
    argparser.add_argument("--mnt", help="thing maintainer", default="", required=False)
    argparser.add_argument("--use", help="usecase", default="", required=False)
    argparser.add_argument("--dis", help="discard", default="", required=False)

    args = argparser.parse_args()

    qr.add_data("https://dinge.openlab-augsburg.de/ding/"+args.id)
    qr.make()
    img = qr.make_image()

    bmp = StringIO()
    img.save(bmp, kind="BMP")
    bmp.seek(0)


    ### GENERAL SETTINGS (reseted after turn off) ###
    kk.write(STX+"m"+CR)        # use metric system
    kk.write(STX+"KX0025"+CR)   # 25mm label height
    kk.write(STX+"f700"+CR)     # stop position for back feed

    ### QR-Code transmitting ###
    kk.write(STX+"IAbqrcode"+CR) # write bmp into ram as "qrcode"
    kk.write(bmp.read())


    kk.write(STX+"L"+CR) # enter label formatting mode

    kk.write("1Y1100000070030qrcode"+CR) # qrcode

    kk.write("191100001800030Inventar - OpenLab Augsburg e. V."+CR) # header

    kk.write("121100001260225"+args.name+CR)        # Name
    kk.write("111100000850225ID: "+args.id+CR)      # ID

    kk.write("111100000380225OWN: "+args.own+CR)    # Owner
    kk.write("111100000030225MNT: "+args.mnt+CR)    # Maintainer

    kk.write("111100000380625USE: "+args.use+CR)    # Usage
    kk.write("111100000030625DIS: "+args.dis+CR)    # Discard

    kk.write("1F3108000950790"+args.id+CR)          # EAN

    kk.write("E"+CR) # end label formatting mode


    kk.close()
