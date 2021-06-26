==================
esc2pdf 0.1
==================

:Author: Serge Zihlmann

.. contents::
    :backlinks: none

.. sectnum::

Introduction
============

**esc2pdf** is a pure Python library that interpretes 9-Pin ESC/P code and converts it into PDF:

* Version 0.1 is designed for Python 3.9, tested under Windows 10 and Ubuntu
* In order to create PDF-files, it relies on the `reportlab`__ package (needs to be installed). Tested with reportlab "3.5.55".
* The package may convert a livestream of printer data but also complete files.
* Permissively licensed.
__ http://www.reportlab.org/


Limitations
~~~~~~~~~~~
Currently, the following limitations apply to esc2pdf:

* Only ESC/P code is supported (not ESC/P2)
* Only <PlainText>, <ESC 2>, <ESC 3> and <ESC K nl nh> commands are supported. Simply because those were sufficient to interprete text and graphics in the initial application. It should be simple enough to extend the library to other ESC/P commands.

Initial use
===========
This library was created 2021 when it became necessary for the author to digitize the output of a laboratory equipment. The physical devices only output was to a historical Epson dot-matrix printer on endless paper via the Centronics interface. The solution was as follows:

* Convert the centronics parallel data to serial data using a ATEN SXP-320A or `BLACKBOX`__ PI125A-R2
* Read the serial data via a Serial-to-USB converter
* Run Python on a PC
* Process the data using esc2pdf from ESC/P to PDF
__ https://www.blackbox.com
In principal, a computer with parallel input could be used but is rather difficult to find nowadays.

Operation Principle
===================
**esc2pdf** is a reduced implementation of reverse <9-Pin ESC/P> code which is well documented in the `Epson ESC/P Reference Manual`__ (December 1997). A state-machine (esc_p.py) translates the code character-by-character into Python objects (*Boxes*). *Boxes* may represent Text, Linefeed, Pagebreak, Carriage-return and Graphics-data. *Boxes* are aggregated into *Flowables* (simple list of boxes) to indicate that those portions of data belong together and should not break over pages. The PDF-module (pdfwriter.py) takes *Flowables* as input, putting those to pages and output a PDF using *reportlab*.

__ http://files.support.epson.com/pdf/general/escp2ref.pdf

In more detail
~~~~~~~~~~~~~~
-  ESC_Device
   
   The device is a state machine, which interpretes the input byte per byte.
   It currently understands plain text, ESC 2, ESC 3, ESC K commands for 9 pin printers.
   It returns *Boxes* grouped to one *Flowable*. Incomplete *Boxes* remain in memory
   and will not be returned with *Flowable* until more data is fed to ESC_Device

-  PDFWriter
   
   The writer accepts *Flowables* and tries to put as many of them as possible
   onto the first page.
   If space is not sufficent, one or several Flowables will be put onto the next page(s).
   One flowable will always stick together, except if it's larger than one page,
   which would always trigger an additional Pagebreak.


Usage
=====
With many old devices outputing `box drawing characters`__ not supported by ascii or native PDF-fonts, you need to install an additional monospaced (fixed-pitch) font such as `GNU FreeFont`__.

__ https://en.wikipedia.org/wiki/Box-drawing_character
__ https://www.gnu.org/software/freefont/

Primary usage
~~~~~~~~~~~~~~
First step is to import esc2pdf::

	from esc2pdf import ESC_Device, PDFWriter

Create device to interprete ESC/P and PDF-engine::

	ESCdevice = ESC_Device()
	PDF = PDFWriter('out.pdf', scaling=0.85)

Read your  data. E.g. from file or from computer-port. bdata must be bytearray()::
	bdata = ....

Process ESC-code and convert to Flowable::

	Flowable = ESCdevice.process_bytearray(bdata)

Add generated Flowable(s) to PDF::

	PDF.addFlowable(Flowable)

Make PDF::

	PDF.printPDF()

Examples
~~~~~~~~
Examples are included on github. These should outline almost all capabilities.

Other libraries
===============
Key advantages of esc2pdf are

* Platform independence
* Ability to handle CONTINUOUS/incomplete streams of ESC/P-data (real case when listening to a port). Enables *live printing*
* Setup in minutes with only Python and reportlab as prerequisites (pure Python)
* Generate PDF output with real text and not bitmap

Although I have not tested any of those in detail, here is a list of other tools intending to do similar operations:

-  `PrinterToPDF`__

    Seems to be a complete tool written in C. Output is a PDF-file with all data as bitmap.
    Runs only under Linux and requires libpng, ImageMagick, SDL libHARU installed.
    Will only handle complete captured files.

-  `node-escprinter`__

    JavaScript implementation with SVG output. Requires complete data-file.
    From what I understood text will be dot matrix image.

-  `ESCParser`__

    C++ implementation with PostScript, SVG and PDF output. Requires complete data-file.

-  `dotprint`__

    Outputs to PDF. Target platform Linux. Requires complete data-file.

-  `printfileprinter.html`__

    Outputs to PDF. Not open source. Requires complete data-file.

__ https://github.com/RWAP/PrinterToPDF/
__ https://github.com/shokre/node-escprinter
__ https://github.com/nzeemin/ukncbtl-utils/wiki/ESCParser
__ https://github.com/zub2/dotprint
__ http://www.columbia.edu/~em36/printfileprinter.html
