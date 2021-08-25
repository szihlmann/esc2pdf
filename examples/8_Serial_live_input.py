from esc2pdf import ESC_Device, PDFWriter
import serial
import time

"""
    This is untested PSEUDO-CODE which demonstrates how to convert real time serial ESC-data to PDF.
    
    The key to success is to concatenate data-packages which belong together.
    This way printed elements (e.g. a table / text  block / graphic / etc.) will not be split over pages.
    
    The concept is to collect incoming data until data reception is finished. This is done
    by resetting a certain timet AS LONG as data is received. After reception, the serial
    IDLE time will be reached and the collected data passed to ESC_Device to generate a Flowable,
    which is then passed to the PDFWriter and put to the current page.
"""

# Define variables
SerialTimeout = 5 # seconds
byteBuffer = bytearray([])
LastDataReceive = time.time()

# Initialize serial connection
connection = serial.Serial(
                            port = 'COM1' 
                            baudrate = 19200,
                            timeout = 1,
                            parity = 'E',
                            stopbits = 1,
                            bytesize = 8)
                            
# Create 9-Pin ESC/P code handler
ESCdevice = ESC_Device() # Create device to interprete ESC code

# Create PDF handler
filename = 'out.pdf'
PDF = PDFWriter(filename, scaling=0.85)

while True: # Repeat forever

    # Read serial data
    WaitingChars = connection.in_waiting
    if (WaitingChars):
        byteBuffer += connection.read(WaitingChars) # Read all data as bytearray and append to buffer
        LastDataReceive = time.time() # reset timeout

    # Process serial data after timeout
    if (byteBuffer and time.time() > (LastDataReceive + SerialTimeout) ): # bytBuffer not empty AND timeout
        Flowable = ESCdevice.process_bytearray(byteBuffer) # Generate flowable from received ESC Data
        byteBuffer.clear()
        PDF.addFlowable(Flowable) # Pass Flowable to PDFWriter
        PDF.printPDF() # Update PDF File

    # Reduce CPU usage
    time.sleep(0.01)

    