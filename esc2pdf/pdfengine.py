# A part of esc2pdf (https://github.com/szihlmann/esc2pdf)
# Copyright (C) 2021 Serge Zihlmann, Bern, Switzerland
# MIT license -- See LICENSE.txt for details

from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics 

# Global variables
markerSize = 0.95 # 95% Marker-Fill for graphics

class pdfDoc(object):
    def __init__(self, fileName, PageDef, overlay, Font, boldFont, italicFont, bold_italicFont, docProperties, scaling=1):
        self._pdfCanvas = Canvas(fileName, pagesize=(PageDef.width, PageDef.height)) # Create PDF Object
        self._pdfCanvas.setAuthor   (docProperties.Author)
        self._pdfCanvas.setTitle    (docProperties.Title)
        self._pdfCanvas.setCreator  (docProperties.Creator)
        self._pdfCanvas.setProducer (docProperties.Producer)
        self._pdfCanvas.setSubject  (docProperties.Subject)
        
        self._scaling = scaling
        self._Cursor = cCursor(PageDef.xStart, PageDef.yStart, PageDef.width)
        self._PageCnt = 1
        self._LineSpacing = 0 # Will be defined with the first LineFeedBox
        self._Font = Font
        self._standardFont = Font
        self._italicFont = italicFont
        self._boldFont = boldFont
        self._bold_italicFont = bold_italicFont 
        self._FontSize = 0 # Will be defined with the first TextBox
        self._bold = False # Will be defined with the first TextBox
        self._italic = False # Will be defined with the first TextBox
        self._redefineFont() # Call this after setting font or fontsize
        self.overlay = overlay # overlay function
        self._prtOverlay()

    def printBox(self, Box):
        if Box.isType('TextBox'):
            BoxFontSize = Box.FontSize * self._scaling
            if BoxFontSize != self._FontSize: # Change FontSize if necessary
                self._FontSize = BoxFontSize
                self._redefineFont()
            if Box.boldFont != self._bold:
                self._bold = Box.boldFont
                self._redefineFont()
            if Box.italicFont != self._italic:
                self._italic = Box.italicFont
                self._redefineFont()
            self._pdfCanvas.drawString(self._Cursor.x, self._Cursor.y, Box.Text)
            self._moveTextWidth(Box.Text) # move cursor with typed text in x
        elif Box.isType('LineFeedBox'):
            self._LineSpacing = Box.LineSpace * self._scaling
            self._nextLine()
        elif Box.isType('CarriageReturnBox'):
            self._Cursor.CR() # Return to line start
        elif Box.isType('GraphicsBox'):
            self._printGraphics(Box)

    def _nextLine(self):
        self._Cursor.move(0, self._LineSpacing)
        if self._Cursor.y < 0:
            print('Warning: Page overflow. Extra page inserted.')
            self.nextPage()

    def nextPage(self):
        self._PageCnt += 1
        self._Cursor.reset()
        self._pdfCanvas.showPage() # End page and start new one
        self._redefineFont()
        self._prtOverlay()
        
    def _prtOverlay(self):
        self._pdfCanvas.saveState()
        self.overlay(self._pdfCanvas, self._PageCnt) # call overlay function and pass canvas & page number
        self._pdfCanvas.restoreState()
    
    def overlay(self, *args):
        pass # by default no overlay defined

    def _moveTextWidth(self, Text):
        textWidth = pdfmetrics.stringWidth(Text, self._Font, self._FontSize)
        self._Cursor.move(textWidth, 0)

    def _printGraphics(self, gBox):
        gData = gBox.graphicsData
        xStep = 72.0 / gBox.H_resolution * self._scaling
        yStep = 72.0 / gBox.V_resolution * self._scaling
        markerSizeX = markerSize * xStep / 2
        markerSizeY = markerSize * yStep
        self._pdfCanvas.setLineWidth(markerSizeY) # Stroke thickness of lines

        for j in range( len(gData) ):           # Loop through all bytes in graphic data
            for k in range(8):                  # For each pixel in byte
                if ( gData[j] & (0b1 << k ) ):  # Evaluate bit in byte
                    self._pdfCanvas.line(       # Draw dot (.line uses least disc space)
                        self._Cursor.x - markerSizeX, self._Cursor.y + k*yStep,
                        self._Cursor.x + markerSizeX, self._Cursor.y + k*yStep ) 
            self._Cursor.move(xStep, 0)         # Move 1 step in x
    
    def _redefineFont(self):
        if self._italic and self._bold:
            self._Font = self._bold_italicFont
        elif self._italic:
            self._Font = self._italicFont
        elif self._bold:
            self._Font = self._boldFont
        else:
            self._Font = self._standardFont

        self._pdfCanvas.setFont(self._Font, self._FontSize)

    def save(self):
        self._pdfCanvas.save()

class cCursor(object):
    def __init__(self, x0, y0, width):
        self.x0 = x0 # Starting value
        self.y0 = y0 # Starting value
        self.x_lim = width - x0
        self.x_limlim = width
        self.x = 0
        self.y = 0
        self.reset()

    def move(self, XD, YD):
        self.x += XD # move points in x
        self.y -= YD # move points in y
        self.checkLims()

    def reset(self):
        self.x = self.x0
        self.y = self.y0

    def CR(self):
        self.x = self.x0
    
    def checkLims(self):
        if (self.x > self.x_limlim):
            print('Error: Exceeding page width')
        elif (self.x > self.x_lim):
            print('Warning: Printing close to right border')

class pagedef(object):
    def __init__(self, width, height):
        self.setHeight(height)
        self.setWidth(width)
        #self.width = round( mmToPts(width) )
        #self.height = round( mmToPts(height) )
        self.xStart = 0
        self.yStart = 0
        self.VerticalSpace = 0
        self._LeftM = 0
        self._TopM = 0
        self._BottomM = 0
    
    def LeftMargin(self, margin):
        # Define space in mm to the left of page
        self._LeftM = round(mmToPts(margin))
        self._recalc()
    
    def TopMargin(self, margin):
        # Define space in mm to the top of page
        self._TopM = round(mmToPts(margin))
        self._recalc()
        
    def BottomMargin(self, margin):
        # Define space in mm to the bottom of page
        self._BottomM = round(mmToPts(margin))
        self._recalc()

    def _recalc(self):
        self.xStart = self._LeftM
        self.yStart = self.height - self._TopM
        self.VerticalSpace = self.height - self._TopM - self._BottomM
    
    def setWidth(self, width):
        self.width = round( mmToPts(width) )

    def setHeight(self, height):
        self.height = round( mmToPts(height) )

def mmToPts(x):
    # Convert mm to points
    return x * 72 / 25.4 # 72 pts per inch