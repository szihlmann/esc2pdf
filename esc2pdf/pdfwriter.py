# A part of esc2pdf (https://github.com/szihlmann/esc2pdf)
# Copyright (C) 2021 Serge Zihlmann, Bern, Switzerland
# MIT license -- See LICENSE.txt for details

from os import path
from .pdfengine import pdfDoc, pagedef
from reportlab.pdfbase import pdfmetrics, _fontdata
from reportlab.pdfbase.ttfonts import TTFont

# Import a default fixed-pitch font supporting PC437 characters
PackagePath = path.dirname(__file__)
DFLT_FONT = 'Courier'
DFLT_FONT_Bold = 'Courier-Bold'
DFLT_FONT_Italic = 'Courier-Oblique'
DFLT_FONT_Bold_Italic = 'Courier-BoldOblique'

# Define page --> Global for all instances of PDFWriter()
PageDef = pagedef(210, 297) # A4 by default
PageDef.LeftMargin(15) # mm
PageDef.TopMargin(25) # mm
PageDef.BottomMargin(10) # mm

class PDFWriter(object):
    # Contains: finished and partial filled pages and unmatched flowables
    #           methods to process data and print pdf-pages.
    def __init__(self, filename, scaling=1):
        self._scaling = scaling      # Scaling factor
        self._Flowables = []         # Empty list of Flowables
        self._Pages = []             # Page list
        self._currentPage = None     # Points to the last page in Pages
        self._nextPage()             # Add first page
        self._PDFfilename = filename # Filename to save PDF output as
        self.docProperties = pdfDocProperties()
        self._Font = DFLT_FONT
        self._boldFont = DFLT_FONT_Bold
        self._italicFont = DFLT_FONT_Italic
        self._bold_italicFont = DFLT_FONT_Bold_Italic
 
    def addFlowable(self, Flowable):
        self._Flowables.append(Flowable) # Append incoming Flowable

    def printPDF(self):
        self._createPages() # Put flowables to pages
        self._pdfSetup()
        self._makePDF()

    def overlay(self, *args):
        pass # by default no overlay defined

    def register_TTFont(self, FontPath, Name):
        pdfmetrics.registerFont(TTFont(Name, FontPath))
    
    def selectFont(self, Font, FontType = 'Standard'):
        # get lists of native PDF-fonts and userdefined fonts
        nativeFonts = list( _fontdata.standardFonts )
        userFonts   = list( pdfmetrics._fonts.keys() )
        allFonts    = nativeFonts + userFonts
        if Font in allFonts:
            if FontType == 'Standard':
                self._Font = Font
            elif FontType == 'Bold':
                self._boldFont = Font
            elif FontType == 'Italic':
                self._italicFont = Font
            elif FontType == 'Bold_Italic':
                self._bold_italicFont = Font
        else:
            print('Font \'' + Font + '\' is not registered. Keeping current font.')

    def _pdfSetup(self):
        self._PDFdoc = pdfDoc(
                    fileName = self._PDFfilename,
                    PageDef = PageDef,
                    overlay = self.overlay,
                    Font = self._Font,
                    boldFont = self._boldFont,
                    italicFont = self._italicFont,
                    bold_italicFont = self._bold_italicFont,
                    docProperties = self.docProperties,
                    scaling = self._scaling
                    ) # Create PDF printer object

    def _makePDF(self):
        FirstPage = True
        for page in self._Pages:
            if FirstPage:
                FirstPage = False # no need to create a page in the first run
            else:
                self._PDFdoc.nextPage()
            for Box in page.Boxes:
                self._PDFdoc.printBox( Box )
        self._PDFdoc.save()
    
    def _nextPage(self):
         self._Pages.append( HighLevelPage(self._scaling) )
         self._currentPage = self._Pages[-1]

    def _createPages(self):

        for Flowable in self._Flowables:
            # Check spacing for flowable on page - try to put it on current
            if self._currentPage.isEmpty():
                pass # No need to add page, as it is empty
            elif not self._currentPage.hasSpace(Flowable): # If flowable larger than current page-space
                self._nextPage()
            
            # Put boxes of flowable onto page(s)
            for box in Flowable:
                # Ignore pagebreaks, CR, LF if page is still empty
                if self._currentPage.isEmpty():
                    if box.isType('PageBreakBox'):
                        continue # process next box
                    if box.isType('LineFeedBox'):                 
                        continue # process next box
                    if box.isType('CarriageReturnBox'):
                        continue # process next box

                if box.isType('PageBreakBox'):
                    self._nextPage() # Add page with PageBreakBox
                else: # Send all other boxes to HighLevelPage
                    self._currentPage.addBoxes( [box] )   
                    if ( not self._currentPage.hasSpace( [] ) ): # page full
                        self._nextPage()

        # Clear processed flowables from memory
        self._Flowables.clear()

    def getPageNumbers(self):
        self._createPages()
        return len( self._Pages )

class pdfDocProperties(object):
    def __init__(self):
        self.Title = 'esc2pdf output'
        self.Subject = 'Converting ESC/P data to PDF'
        self.Author = 'esc2pdf'
        self.Creator = 'esc2pdf - github.com'
        self.Producer = 'esc2pdf - github.com'

class HighLevelPage():
    # Page consists of Boxes
    def __init__(self, scaling = 1):
        self.Boxes = [] # Empty list of Boxes
        self._scaling = scaling

    def _size(self):
        return self._Fsize(self.Boxes)

    def addBoxes(self, Flowable):
        self.Boxes += Flowable
    
    def isEmpty(self):
        return self.Boxes == []

    def hasSpace(self, Flowable):
        return self._Fsize(Flowable) + self._size() <= PageDef.VerticalSpace

    def _Fsize(self, Flowable):
        # Determine vertical size of Flowable UNTIL NEXT PAGEBREAK in points (pts) by summing linespaces in LineFeedBoxes
        size = 0
        for box in Flowable:
            if box.isType('LineFeedBox'):
                size += box.LineSpace
            if box.isType('PageBreakBox'):
                break
        return size * self._scaling
