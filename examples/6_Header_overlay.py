from esc2pdf import ESC_Device, PDFWriter
from readbin import readbindata

"""
    Demonstrates how to put an overlay, e.g. header, over pages
    You have to create a generator function which is then passed to the PDFWriter instance.
    By design, the generator function will always take two arguments: The reportlab canvas & page numbers
    Within the generator function you can draw directly without restrictions onto the reportlab canvas.
"""

class Header(object):
    pages = 0
    def GeneratorFun(self, canvas, pageNo):
        y0 = 285 * 72 / 25.4
        x0 = 15 * 72 / 25.4
        canvas.setFont('Helvetica', 15)
        canvas.drawString(x0, y0,    "This is a header")
        canvas.drawString(x0+400, y0,    "Page " + str(pageNo) + ' of ' + str(self.pages))
    
# import data
folder = 'sample_binaries'
files = [
         '04_Spectrum_1.esc',
         '06_Quenchcurve.esc',
         '07_Plot_Quench.esc',
         '08_Single_Measurement.esc'
    ]

# Create 9-Pin ESC/P code handler
ESCdevice = ESC_Device() # Create device to interprete ESC code

# Create PDF handler
PDF = PDFWriter('out.pdf', scaling=0.85)

# Process ESC-code and feed to PDF handler
for index in [3,0,1,2]:
    bdata = readbindata(folder, files[index])
    Flowable = ESCdevice.process_bytearray(bdata)
    PDF.addFlowable(Flowable)

# Create PDF-overlay / header
Header.pages = PDF.getPageNumbers()
overlay = Header()
PDF.overlay = overlay.GeneratorFun # Pass header/overlay functio

# Print to PDF
PDF.printPDF()
