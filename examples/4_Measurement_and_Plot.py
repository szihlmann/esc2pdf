from esc2pdf import ESC_Device, PDFWriter
from readbin import readbindata

"""
    The outline the concept of the "flowable" we will open two files.
    File1: Measurement as Text
    File2: Spectrum graphics
    1) First, we merge both of them into the same Flowable (Flowable1).
       The graphic will break over pages.
    2) Secondly, we put both files to individual flowables (Flowable 2 / 3).
       Flowables will both appear on an individual page such as not to break them.
"""

# import data
folder = 'sample_binaries'
file1 = '08_Single_Measurement.esc'
file2 = '04_Spectrum_1.esc'

# Create 9-Pin ESC/P code handler
ESCdevice = ESC_Device() # Create device to interprete ESC code

# Create PDF handler
PDF = PDFWriter('out.pdf', scaling=0.85)

# Process ESC-code and feed to PDF handler
Flowable1 = ESCdevice.process_bytearray(
                    readbindata(folder, file1)
                    )

Flowable1 += ESCdevice.process_bytearray(
                    readbindata(folder, file2)
                    )

Flowable2 = ESCdevice.process_bytearray(
                    readbindata(folder, file1)
                    )

Flowable3 = ESCdevice.process_bytearray(
                    readbindata(folder, file2)
                    )

PDF.addFlowable(Flowable1)
PDF.addFlowable(Flowable2)
PDF.addFlowable(Flowable3)

# Print to PDF
PDF.printPDF()
