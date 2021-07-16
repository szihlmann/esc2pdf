# A part of esc2pdf (https://github.com/szihlmann/esc2pdf)
# Copyright (C) 2021 Serge Zihlmann, Bern, Switzerland
# MIT license -- See LICENSE.txt for details

defaultGraphicsResolutionH = 60 # DPI
defaultGraphicsResolutionV = 72 # DPI

# Blueprint for Box object
class Box(object):
    def __init__(self):
        self.CmdPromptOutput = False
        #pass

    def Type(self):
        return self.__class__.__name__

    def isType(self, typeName = 'None'):
        return self.Type() == typeName
    
    def PrintToCmd(self):
        pass

# Boxes for data storage
class TextBox(Box):
    def __init__(self, code = 'ibm437', fSize = 12, bold = False, italic = False):
        self.Text = ''
        self.charCode = code
        self.FontSize = fSize
        self.boldFont = bold # By default, font is not bold
        self.italicFont = italic # By default, font is not italic
        self.CmdPromptOutput = False # By default not printing to command line

    def add(self, byte):
        string = byte.decode(self.charCode, errors='replace') # Decode to text and save
        self.Text += string
        if self.CmdPromptOutput:
            print (string, end = '')

    def PrintToCmd(self):
        self.CmdPromptOutput = True


class GraphicsBox(Box):
    def __init__(self):
        self.graphicsData = bytearray()
        self.H_resolution = defaultGraphicsResolutionH # DPI, horizontal
        self.V_resolution = defaultGraphicsResolutionV # DPI, vertical
    
    def PrintToCmd(self):
        print ('{Graphics Data ' + str(len(self.graphicsData)) + ' bytes}', end = '')

class PageBreakBox(Box):
    def PrintToCmd(self):
        print ('{Page Break}', end = '\n')

class LineFeedBox(Box):
    def __init__(self, space):
        self.LineSpace = space

    def PrintToCmd(self):
        print ('{LF ' + str(self.LineSpace) + ' pts}', end = '\n')

class CarriageReturnBox(Box):
    def PrintToCmd(self):
        print ('{CR}', end = '')
