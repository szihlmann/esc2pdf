from esc2pdf import ESC_Device, PDFWriter
from readbin import readbindata

"""
    Note: This dataset uses box drawing characters not supported by native PDF-fonts. You will see empty squares instead.
    Please install a monospaced true-type font which supports box-drawing-characters
    (e.g. FreeMono from https://www.gnu.org/software/freefont/ or direct ftp.gnu.org/gnu/freefont/freefont-ttf-20120503.zip)
"""

# Create PDF handler
PDF = PDFWriter('out.pdf', scaling=0.85)

#Uncomment this code to add a font
#PDF.register_TTFont('FreeMono.ttf', 'FreeMono')
#PDF.selectFont('FreeMono')

# Import data
folder = 'sample_binaries'
file = '01_Table1_status.esc'
bdata = readbindata(folder, file) # Convert to bytearray

# Create 9-Pin ESC/P code handler
ESCdevice = ESC_Device() # Create device to interprete ESC code

# Process ESC-code and feed to PDF handler
Flowable = ESCdevice.process_bytearray(bdata)
PDF.addFlowable(Flowable)

# Print to PDF
PDF.printPDF()
