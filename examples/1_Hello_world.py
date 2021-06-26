from esc2pdf import ESC_Device, PDFWriter

# Your text input (will be converted to bytearray)
Text = 'Hello World\r\n' # A line is only complete after LineFeed
bdata = Text.encode('ascii')

# Create 9-Pin ESC/P code handler
ESCdevice = ESC_Device() # Create device to interprete ESC code

# Create PDF handler
PDF = PDFWriter('out.pdf', scaling=0.85)

# Process ESC-code and feed to PDF handler
Flowable = ESCdevice.process_bytearray(bdata)
PDF.addFlowable(Flowable)

# Print to PDF
PDF.printPDF()
