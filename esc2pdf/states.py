# A part of esc2pdf (https://github.com/szihlmann/esc2pdf)
# Copyright (C) 2021 Serge Zihlmann, Bern, Switzerland
# MIT license -- See LICENSE.txt for details

from .state_obj import State
from .transitions import (t_ReceiveText, t_CarriageReturn, t_LineFeed,
                          t_FormFeed, t_create_GraphicBox)

charCodeTbl = {
  "LF":  b'\x0a',
  "FF":  b'\x0c',
  "CR":  b'\x0d',
  "ESC": b'\x1b',
  "*":   b'\x2a',
  "0":   b'\x30',
  "1":   b'\x31',
  "2":   b'\x32',
  "3":   b'\x33',
  "4":   b'\x34',
  "5":   b'\x35',
  "E":   b'\x45',
  "F":   b'\x46',
  "K":   b'\x4b'
}

def baseCharacterDecision(byte, Boxes, properties):
    if byte == b'': # remain in this state
        return IDLE

    elif byte == charCodeTbl['ESC']:
        return ESC()

    elif byte == charCodeTbl['LF']:
        t_CarriageReturn(Boxes)
        t_LineFeed(Boxes, properties.LineSpace)
        return IDLE()
        
    elif byte == charCodeTbl['CR']:
        t_CarriageReturn(Boxes)
        return CarriageReturn()

    elif byte == charCodeTbl['FF']:
        t_FormFeed(Boxes)
        return IDLE()

    else:
        t_ReceiveText(byte, Boxes, properties)
        return IDLE()

# ================================= #
# ESC/POS translation engine states #
# ================================= #
class IDLE(State):
    """
    The state which indicates that we are IDLE and ready to receive next byte
    """
    def on_byte(self, byte, Boxes, properties):
        return baseCharacterDecision(byte, Boxes, properties)

class CarriageReturn(State):
    def on_byte(self, byte, Boxes, properties):
        if byte == charCodeTbl['LF']:
            t_LineFeed(Boxes, properties.LineSpace)
            return IDLE()
        else:
            # CR is not followed by LF: Process character as usual.
            return baseCharacterDecision(byte, Boxes, properties)

class ESC(State):

    def on_byte(self, byte, Boxes, properties):
        if byte == charCodeTbl['2']:
            properties.LineSpace = 1/6 * 72 # Set 1/6 inch linespace
            return IDLE()
        elif byte == charCodeTbl['3']:
            return ESC_3()
        elif byte == charCodeTbl['4']: # Select italic font
            properties.italicFont = True
            return IDLE()
        elif byte == charCodeTbl['5']: # Cancel italic font
            properties.italicFont = False
            return IDLE()
        elif byte == charCodeTbl['E']: # Select bold font
            properties.boldFont = True
            return IDLE()
        elif byte == charCodeTbl['F']: # Cancel bold font
            properties.boldFont = False
            return IDLE()
        elif byte == charCodeTbl['K']: # ESC K state for 60-dpi graphics
            return ESC_K()
        else:
            print('Received unknown ESC-sequence: ESC + ' + byte.decode(properties.charCode, errors='replace'))
            return IDLE()

class ESC_3(State):

    def on_byte(self, n, Boxes, properties):
        properties.LineSpace = n[0]/216 * 72 # Set 1/6 inch linespace
        return IDLE()

class ESC_K(State):
    # Select 60-dpi graphics 
    # Bit-image graphics in 8-dot columns, at a density of 60 horzontal by 60 vertical dpi
    # ESC K nL nH d1 .... dn
    def __init__(self):
        self._nL = None
        self._nH = None
        self._k = None
        self._receivedChars = 0
        self._graphicsData = bytearray()

    def on_byte(self, byte, Boxes, properties):
        if self._nL == None:
            self._nL = byte[0]
        elif self._nH == None:
            self._nH = byte[0]
            self._k = self._nL + self._nH * 256 # Determine number of expected graphic bytes
        elif self._k == 0: # no graphic data to receive
            return IDLE()
        else:
            self._graphicsData += byte # append current character to graphicsData
            self._receivedChars += 1 # increase count for received chars
            
            if self._receivedChars >= self._k:
                t_create_GraphicBox(Boxes, 60, self._graphicsData) # 60 dpi resolution
                return IDLE()

        return self