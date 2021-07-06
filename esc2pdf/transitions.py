# A part of esc2pdf (https://github.com/szihlmann/esc2pdf)
# Copyright (C) 2021 Serge Zihlmann, Bern, Switzerland
# MIT license -- See LICENSE.txt for details

from .boxes import TextBox, GraphicsBox, PageBreakBox, LineFeedBox, CarriageReturnBox

def t_ReceiveText(byte, Boxes, properties):
    def addTextBox():
        Boxes.append( TextBox(properties.charCode, properties.FontSize, properties.boldFont, properties.italicFont) )

    if Boxes == []: # Empty list
        addTextBox()
    elif not isinstance(Boxes[-1], TextBox ): # Current box is not a TextBox
        addTextBox()
    elif (Boxes[-1].FontSize != properties.FontSize or
            Boxes[-1].boldFont != properties.boldFont or
            Boxes[-1].italicFont != properties.italicFont ): # Current box is of type TextBox - check for matching font properties
        addTextBox()
    else: # Current box is TextBox with equal properties
        pass
    
    # Finally, write data to TextBox
    Boxes[-1].add( byte )

def t_CarriageReturn(Boxes):
    Boxes.append( CarriageReturnBox() )
    
def t_LineFeed(Boxes, space):
    Boxes.append( LineFeedBox(space) )

def t_FormFeed(Boxes):
    Boxes.append( PageBreakBox() )

def t_create_GraphicBox(Boxes, res, data):
        newBox = GraphicsBox()
        newBox.H_resolution = res # dpi  
        newBox.graphicsData = data # bytearray
        Boxes.append( newBox )