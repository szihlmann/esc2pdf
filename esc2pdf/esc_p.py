# A part of esc2pdf (https://github.com/szihlmann/esc2pdf)
# Copyright (C) 2021 Serge Zihlmann, Bern, Switzerland
# MIT license -- See LICENSE.txt for details

# Implementation of a state machine to process ESC code data
from .states import IDLE
from .boxes import PageBreakBox

class deviceProperties(object):
    def __init__(self):
        # Initialize with default values
        self.LineSpace = 12 # Default linespace in pts (equals 1/6 inch) (72 points per inch)
        self.FontSize = 12 # Default fontsize is 12 pts
        self.boldFont = False # Default font is not boldFont
        self.italicFont = False # Default font is not italic
        self.charCode = 'ibm437' # IBM Code Page PC437 
        self.IgnoreFormFeed = False # By default, FormFeedBoxes are accepted
        self.PageBreakKeywords = [] # None per default, can be multiple
        self.KeywordPagebreakeInsert = 'Before'  # 'Before' or type anything for after

class BoxList (list):
    # A simple copy of the List object with an add-on, which allows debug printing when a new entry is added.
    def __init__(self, *args):
        super().__init__(*args) # inherit __init__ from list object
        self.CmdPromptOutput = False # By default, do not print interpreted ESC to command prompt

    def append(self, *args):
        # rewrite the append function. Runs the native append() plus printing new element 
        super().append(*args)
        if self.CmdPromptOutput:
            self[-1].PrintToCmd()

class ESC_Device(object):
    """ 
        A simple state machine that mimics the functionality of a device from a high level.
    """

    def __init__(self):
        # Initialize the components.
        self.state = IDLE() # Start with IDLE state
        self.Flowable = []  # Returnable Flowable. Empty list of boxes.
        self.Boxes = BoxList() # Working Flowable. Empty list of boxes (Textbox, LineFeedBox, PageBreakBox or GraphicsBox).
        self.devProperties = deviceProperties() # Initialize device properties

    def process_bytearray(self, array): # array is bytearray()
        self.Flowable = [] # Clear returnable flowable
        # self.Boxes is persistent
        for byte in array:
            a_byte = byte.to_bytes(1, 'big') # convert back to byte
            self.process_byte(a_byte)
        
        return self.Flowable # return the flowable

    def process_byte(self, byte):
        """
            This is the core of the state machine. On a incoming event, 
            the new state is assigned through the current state based
            on the event. All events are handled by the states.
        """

        # The next state will be the result of the on_byte function of the current state.
        self.state = self.state.on_byte(byte, self.Boxes, self.devProperties)
        
        # Handle special cases on boxes
        if self.Boxes != []: # if not empty
            
            # Check for line termination and move boxes to returnable Flowable
            if self.Boxes[-1].isType('LineFeedBox'):
                self.handlePageBreakKeywords()
                self.boxesToFlowable()
            
            # Remove PageBreak if user advises to ignore
            elif self.Boxes[-1].isType('PageBreakBox') and self.devProperties.IgnoreFormFeed:
                del self.Boxes[-1] # remove Pagebreak

    def handlePageBreakKeywords(self):
        if self.devProperties.PageBreakKeywords != []:
            i = 0
            for Box in self.Boxes:
                if Box.isType('TextBox'):
                    for Keyword in self.devProperties.PageBreakKeywords:
                        if Keyword in Box.Text:
                            if self.devProperties.KeywordPagebreakeInsert == 'Before':
                                self.Boxes.insert(i, PageBreakBox() )
                                return
                            else: # Add after
                                self.Boxes.insert(i+1, PageBreakBox() )
                                return
                i += 1

    def boxesToFlowable(self):
        # Move all boxes to returnable flowable. Clear Boxes.
        self.Flowable += self.Boxes.copy()
        self.Boxes.clear()
    
    # Setter functions
    def setDefaultLinespace(self, space):
        self.devProperties.LineSpace = space
    
    def setCharcode(self, code):
        self.devProperties.charCode = code

    def setIgnoreFormFeed(self, choice):
        self.devProperties.IgnoreFormFeed = choice

    def setPageBreakKeywords(self, keywords):
        self.devProperties.PageBreakKeywords = keywords

    def setKeywordPagebreakeInsert(self, position):
        self.devProperties.KeywordPagebreakeInsert = position
    
    def setCmdPromptOutput(self, state):
        # Print to command prompt "live" as data is received. Will make everything slow.
        self.Boxes.CmdPromptOutput = state
