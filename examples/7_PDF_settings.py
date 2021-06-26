from esc2pdf import ESC_Device, PDFWriter

"""
    A very brief demonstration on how to set particular properties
    for a PDF.
    You will find them most probably under "properties" when opening the pdf.
"""

# Create PDF handler
PDF = PDFWriter('out.pdf', scaling=0.85)

# Add desired properties
PDF.docProperties.Title = 'YourTitle'
PDF.docProperties.Subject = 'YourSubject'
PDF.docProperties.Author = 'You'
PDF.docProperties.Creator = 'You as well'
PDF.docProperties.Producer = 'Boss'

# Your text input (will be converted to bytearray)
Text = 'Hello World\r\n' # A line is only complete after LineFeed
bdata = Text.encode('ascii')

# Create 9-Pin ESC/P code handler
ESCdevice = ESC_Device() # Create device to interprete ESC code


# Process ESC-code and feed to PDF handler
Flowable = ESCdevice.process_bytearray(bdata)
PDF.addFlowable(Flowable)

# Print to PDF
PDF.printPDF()
