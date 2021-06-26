# A part of esc2pdf (https://github.com/szihlmann/esc2pdf)
# Copyright (C) 2021 Serge Zihlmann, Bern, Switzerland
# MIT license -- See LICENSE.txt for details

class State(object):
    # State object which provides utility functions for the individual state

    def __init__(self):
        pass

    def on_byte(self, byte, Flowable):
        # Handle events that are delegated to this State.
        return self
    
    def Name(self):
        # Returns the name of the State.
        return self.__class__.__name__
        
    def isState(self, stateName = 'None'):
        # Verifies that state corresponds to a given stateName (string)
        return self.__class__.__name__ == stateName
        
