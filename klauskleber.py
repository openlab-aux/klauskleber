#!/usr/bin/env python2

import serial
import qrcode
from StringIO import StringIO
import sys
import urlparse

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



class LabelPrinter(serial.Serial):
    def __init__(self, port):
        super(LabelPrinter, self).__init__(
                bytesize=8,
                baudrate=19200,
                port=port,
                timeout=0,
                parity="N",
                stopbits=1,
                xonxoff=1,
                rtscts=1)
        return

    def print_label(self, label, count=1):
        for line in label.build():
            self.write(line)

        if count > 1:
            self.write(STX+"E"+str(count).zfill(4)+CR)
            self.write(STX+"G"+CR)

        self.close()
        return


class Label:

    thing_base_url = "https://dinge.openlab-augsburg.de/ding/"

    def __init__(
            self,
            thing_id,
            thing_name,
            thing_maintainer,
            thing_owner = "OpenLab",
            thing_use_pol = "",
            thing_discard_pol = ""):

        if len(thing_id) > 12 or not thing_id.isdigit():
            raise ValueError("Not a valid thing_id: field must contain max "
                             "12 digits ranging from 0-9")
        self.thing_id = thing_id.zfill(12)

        if len(thing_name) > 18:
            self.thing_name = thing_name[:15] + "..."
        else:
            self.thing_name = thing_name

        if len(thing_owner) > 13:
            raise ValueError("Not a valid thing_owner: field must contain "
                             "less then 13 characters")
        self.thing_owner = thing_owner

        if len(thing_maintainer) > 13:
            raise ValueError("Not a valid thing_maintainer: field must "
                             "contain less then 13 characters")
        self.thing_maintainer = thing_maintainer

        if len(thing_use_pol) > 12:
            raise ValueError("Not a valid thing_use_pol: field must contain "
                             "less then 12 characters")
        self.thing_use_pol = thing_use_pol

        if len(thing_discard_pol) > 12:
            raise ValueError("Not a valid thing_discard_pol: field must "
                             "contain less then 12 characters")
        self.thing_discard_pol = thing_discard_pol

        return


    def _gen_qrcode(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=2,
            border=0)

        qr.add_data(urlparse.urljoin(self.thing_base_url,self.thing_id))
        qr.make()
        img = qr.make_image()

        bmp = StringIO()
        img.save(bmp, kind="BMP")
        bmp.seek(0)

        return bmp.read()

    def build(self):
        label = []
        ### GENERAL SETTINGS reseted after turn off ###
        label.append(STX+"m"+CR)     # use metric system
        label.append(STX+"KX0025"+CR)   # 25mm label[0] height
        label.append(STX+"f740"+CR)     # stop position for back feed

        ### QR-Code transmitting ###
        label.append(STX+"IAbqrcode"+CR) # write bmp into ram as "qrcode"
        label.append(self._gen_qrcode())


        label.append(STX+"L"+CR) # enter label[0] formatting mode

        label.append("1Y1100000070030qrcode"+CR) # qrcode

        label.append("191100001800030Inventar - OpenLab Augsburg e. V."+CR) # header

        label.append("121100001260225"+self.thing_name+CR)             # Name
        label.append("111100000850225ID: "+self.thing_id+CR)           # ID

        label.append("111100000380225OWN: "+self.thing_owner+CR)       # Owner
        label.append("111100000030225MNT: "+self.thing_maintainer+CR)  # Maintainer

        label.append("111100000380670USE: "+self.thing_use_pol+CR)     # Usage
        label.append("111100000030670DIS: "+self.thing_discard_pol+CR) # Discard

        label.append("1F3108000950790"+self.thing_id+CR)               # EAN

        label.append("E"+CR) # end label[0] formatting mode

        return label