from esc2pdf import ESC_Device, PDFWriter
from readbin import readbindata

# Import data
folder = 'sample_binaries'
file = '07_Plot_Quench.esc'
bdata = readbindata(folder, file) # Convert to bytearray

# Create 9-Pin ESC/P code handler
ESCdevice = ESC_Device() # Create device to interprete ESC code

# Create PDF handler
filename = 'out.pdf'
PDF = PDFWriter(filename, scaling=0.85)

# Process ESC-code and feed to PDF handler
Flowable = ESCdevice.process_bytearray(bdata)
PDF.addFlowable(Flowable)

# Print to PDF
PDF.printPDF()