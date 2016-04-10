#!/usr/bin/env python3

from io import BytesIO
import serial

STX = '\x02'


class LayoutElem:
    """
    LayoutElem represents generally any element that can be rendered into a
    Label.
    """
    X = 0
    Y = 1

    orientation = 1
    coordinates = (0, 0)
    offset = (0, 0)
    stretch = (1, 1)

    def __init__(self, x, y, orientation = 1, mult_x = 1, mult_y = 1):
        self.set_orientation(orientation)
        self.set_coordinates(x, y)
        self.set_stretch(mult_x, mult_y)
        pass

    def _encode_coordinate(self, f_coord):
        s = str(float(f_coord)).split('.')
        return s[0].zfill(3)+s[1][:1]

    def _encode_base_24(self, value):
        if value < 10:
            return str(value)
        return chr(ord('A')+value-10)

    def set_stretch(self, x, y):
        if x not in range(0,25) or y not in range(0,25):
            raise ValueError("Bad stretch value: Valid range [0:24]")
        self.stretch = (int(x), int(y))

    def set_orientation(self, o):
        if o not in range(1,5):
            raise ValueError("Bad orientation value: Allowed values [1:4]")
        self.orientation = o

    def set_coordinates(self, x, y):
        if int(x) not in range(1000) or int(y) not in range(1000):
            raise ValueError("Bad coordinate value: Valid range [0.0:999.9]")
        self.coordinates = (float(x),float(y))
        return

    def set_offset(self, x, y):
        #TODO implement
        pass

    def encode_prerequisites(self):
        return b''

    def encode(self):
        return b''



class Text(LayoutElem):
    def __init__(self, font, text, x, y, font_subtype = 0, orientation = 1,
            mult_x = 1, mult_y = 1):
        super().__init__(x, y, orientation, mult_x, mult_y)
        self.font = font
        self.text = text
        self.font_subtype = font_subtype
        return

    def encode(self):
        return(
                bytes(
                    str(self.orientation) +
                    str(self.font) +
                    self._encode_base_24(self.stretch[self.X]) +
                    self._encode_base_24(self.stretch[self.Y]) +
                    str(self.font_subtype).zfill(3)+
                    self._encode_coordinate(self.coordinates[self.Y]) +
                    self._encode_coordinate(self.coordinates[self.X]) +
                    self.text+"\r",
                "CP437")
                )




class Barcode(LayoutElem):
    pass


class Bitmap(LayoutElem):
    pass



class Label():
    layout_elements = []

    def __init__(self, height): #TODO include more label specif. settings
        self.height = int(height)
        return

    def add(self, layout_elem):
        if not isinstance(layout_elem, LayoutElem):
            raise TypeError("Not a layout element.")
        self.layout_elements.append(layout_elem)

    def encode_prerequisites(self):
        out = bytes(STX + "KX" + str(int(self.height)).zfill(4) + '\r', "CP437")

        for l in self.layout_elements:
            out += l.encode_prerequisites()
        return out

    def encode(self):
        out = bytes(STX+"L\r", "CP437")

        for l in self.layout_elements:
            out += l.encode()

        out += bytes(STX+"E\r", "CP437")

        return out



class LabelPrinter(serial.Serial):

    def __init__(self, port, baudrate):
        """
        super().__init__(
                baudrate=baudrate,
                port=port,
                timeout=0,
                parity="N",
                stopbits=1,
                xonxoff=1,
                rtscts=1)
                """
        return

    def print_label(self, label, count=1):
        """
        if not self.isOpen():
            self.open()

        self.write(label.encode())

        if count > 1: # print copies
            self.write(STX+'E'+str(count).zfill(4)+'\r')
            self.write(STX+'G\r')

        self.close()
        """
        
        print(label.encode_prerequisites())
        print(label.encode())

        if count > 1: # print copies
            print(bytes(STX+'E'+str(count).zfill(4)+'\r', "CP437"))
            print(bytes(STX+'G\r', "CP437"))

        # send <STX>Q to clear memory after each job
        return

"""
class LabelLayout:

    cursor  = {'x':0.0, 'y':0.0}
    stretch = {'x':1, 'y':1}
    orientation = 1
    label_height = 0

    label_buffer = BytesIO()

    barcodes = {
        '3OF9':     'a',
        'UPC-A':    'b',
        'UPC-E':    'c',
        'ITF':      'd',
        'CODE128':  'e',
        'EAN-13':   'f',
        'EAN-8':    'g',
        'HBIC':     'h',
        'CODA BAR': 'i',
        'ITFmod10': 'j',
        'PLESSEY':  'k',
        }

    def __init__(self, label_height):
        if label_height > 9999 or label_height < 0:
            raise ValueError("Bad label_height: Valid range [0:9999]")
        self.label_height = label_height

        self._write_string_encoded(STX + "KX" + str(int(label_height)).zfill(4) + '\r')
        self._write_string_encoded(STX + "L\r") # enter label formatting mode
        return

    def _encode_coord(self, f_coord):
        s = str(float(f_coord)).split('.')
        return s[0].zfill(3)+s[1][:1]

    def _write_string_encoded(self, string):
        self.label_buffer.write(bytes(string, "CP437"))
        return

    def _encode_base_24(self, value):
        if value < 10:
            return str(value)
        return chr(ord('A')+value-10)

    def set_cursor(self, x, y):
        if int(x) > 999 or int(y) > 999 or x < 0 or y < 0:
            raise ValueError("Bad coordinate value: Valid range [0.0:999.9]")
        self.cursor = {
                'x': float(x),
                'y': float(y)
                }
        return

    def translate_cursor(self, dx, dy):
        self.set_cursor(self.cursor['x']+dx, self.cursor['y']+dy)
        return

    def set_stretch(self, x, y):
        if x < 0 or y < 0 or x > 24 or y > 24:
            raise ValueError("Bad stretch value: Valid range [0:24]")
        self.stretch['x'] = x
        self.stretch['y'] = y

    def draw_text(self, font, text, font_subtype = 0):
        self._write_string_encoded(
                str(self.orientation) +
                str(font) +
                self._encode_base_24(self.stretch['x']) +
                self._encode_base_24(self.stretch['y']) +
                str(font_subtype).zfill(3)+
                self._encode_coord(self.cursor['y']) +
                self._encode_coord(self.cursor['x']) +
                text+"\r")
        return

    def draw_barcode(self, barcode, value, with_string = False, bc_height = 0):
        if bc_height < 0 or bc_height > 999:
            raise ValueError('bc_height out of Range. Allowed [0:999]')

        try:
            btype = self.barcodes[barcode]
            if with_string:
                btype = btype.upper()

        except KeyError:
            raise ValueError('Invalid barcode identifier "'+barcode+'".')

        self._write_string_encoded(
                str(self.orientation) +
                str(btype) +
                '2' + # TODO wide bar width
                '1' + # TODO narrow bar width
                str(bc_height).zfill(3)+
                self._encode_coord(self.cursor['y']) +
                self._encode_coord(self.cursor['x']) +
                str(value)+"\r")
        return

    def get_label(self):
        self._write_string_encoded(STX + "E\r") # end label formatting mode
        self.label_buffer.seek(0)
        return self.label_buffer

"""
