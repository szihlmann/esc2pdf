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

* Version 0.1 is designed for Python 3.9, tested under Windows 10 and Ubuntu.
* In order to create PDF-files, it relies on the `reportlab`__ package (needs to be installed). Tested with reportlab "3.5.55".
* The package may convert a livestream of printer data but also complete files.
* Permissively licensed.
__ http://www.reportlab.org/


Limitations
~~~~~~~~~~~
Currently, the following limitations apply to esc2pdf:

* Only ESC/P code is supported (not ESC/P2).
* Only <PlainText>, <ESC 2>, <ESC 3>, <ESC 4>, <ESC 5>, <ESC E>, <ESC F> and <ESC K nl nh> commands are supported. Simply because those were sufficient to interprete text and graphics in the initial application. It should be simple enough to extend the library to other ESC/P commands.

Initial use
===========
This library was created 2021 when it became necessary for the author to digitize the output of a laboratory equipment. The physical devices only output was to a historical Epson dot-matrix printer on endless paper via the Centronics interface. The solution was as follows:

* Convert the centronics parallel data to serial data using a ATEN SXP-320A or `BLACKBOX`__ PI125A-R2.
* Read the serial data via a Serial-to-USB converter.
* Run Python on a PC.
* Process the data using `pyserial`__, `reportlab`__ and esc2pdf from ESC/P to PDF.
__ https://www.blackbox.com
__ https://github.com/pyserial/pyserial
__ http://www.reportlab.org/
In principal, a computer with parallel input could be used but is rather difficult to find nowadays.

Operation Principle
===================
**esc2pdf** is a reduced implementation of reverse <9-Pin ESC/P> code which is well documented in the `Epson ESC/P Reference Manual`__ (December 1997). A state-machine (esc_p.py) translates the code character-by-character into Python objects (*Boxes*). *Boxes* may represent Text, Linefeed, Pagebreak, Carriage-return and Graphics-data. *Boxes* are aggregated into *Flowables* (simple list of boxes) to indicate that those portions of data belong together and should not break over pages.
The PDF-module (pdfwriter.py) takes *Flowables* as input, putting those to pages and outputs a PDF using `reportlab`__.

__ http://files.support.epson.com/pdf/general/escp2ref.pdf
__ http://www.reportlab.org/

In more detail
~~~~~~~~~~~~~~
-  ESC_Device
   
   The device is a state machine, which interpretes the input byte per byte.
   It currently understands plain text, ESC 2, ESC 3, ESC K commands for 9 pin printers.
   It returns *Boxes* grouped to one *Flowable*. Incomplete *Boxes* remain in memory
   and will not be returned with *Flowable* until more data is fed to ESC_Device.

-  PDFWriter
   
   The writer accepts *Flowables* and tries to put as many of them as possible
   onto the current page.
   If space is not sufficent, one or several Flowables will be put onto the next page(s).
   A Flowable will only break over pages if it is larger then one page.

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

Including fonts
~~~~~~~~
The font is a property of *PDFWriter*. Set your True-Type font after initializing the *PDFWriter*::

	PDF = PDFWriter('out.pdf', scaling=0.85)

By registering and selecting the font::

	PDF.register_TTFont('SomeFontFile.ttf', 'UserFont')
	PDF.selectFont('UserFont', FontType='Standard')

Be reminded that different fonts must be used for standard, bold, italic and bold-italic styles. Use the *FontType* argument to specify which font to update. If not specified, *Standard* will be used. Options: *Standard*, *Bold*, *Italic*, *Bold_Italic*. If no font is specified, the native PDF fonts Courier, Courier-Bold, Courier-Oblique and Courier-BoldOblique are used by default.

PDF Settings
~~~~~~~~
You can set the PDF properties such as author using the following commands (after initializing PDFWriter)::

	PDF.docProperties.Title = 'YourTitle'
	PDF.docProperties.Subject = 'YourSubject'
	PDF.docProperties.Author = 'You'
	PDF.docProperties.Creator = 'You as well'
	PDF.docProperties.Producer = 'Boss'

Pagebreaks
~~~~~~~~~~
The FormFeed character sent to printers (hex 0x0c, decimal 12), will by default cause a Pagebreak while being interpreted by ESC_Device.
There might be situations where one needs to supppress this behavior. This can be achieved via the *setIgnoreFormFeed* function.
On the other hand, one might need to include an extra pagebreak upon certain (text based) keywords. The latter can be achieved via the
*setPageBreakKeywords* function.

After initializing the ESCdevice::

	ESCdevice = ESC_Device()

Include::

	ESCdevice.setIgnoreFormFeed( True )
	ESCdevice.setPageBreakKeywords(['SomeKeyWord'])
	
*setPageBreakKeywords* accepts a list as argument.

Print to command prompt
~~~~~~~~~~~~~~~~~~~~~~~
Use the following function to printout *live* as characters are converted::

	ESCdevice.setCmdPromptOutput( True )

Overlay and Headers	
~~~~~~~~
You might want to add a watermark, a header or pagenumbering to each page of the PDF? To accomplish that, you need to create a function with
arguments *canvas*, *pageNo*, which will then be passed to PDFWriter instance. When generating the PDF, the PDFWriter will call this function
with every page. Within this function you may write to the *canvas*, which ist actually a reportlab canvas object. You can use all commands you
can use in reportlab. Changes you make here (e.g. fonts) will not affect the rest of the PDF.
The second argument - pageNo - is the number of the current page.

First creat said function::

	def OverlayFunction(self, canvas, pageNo):
        	y0 = 285 * 72 / 25.4
        	x0 = 15 * 72 / 25.4
        	canvas.setFont('Helvetica', 15)
        	canvas.drawString(x0,     y0, "This is a header")
        	canvas.drawString(x0+400, y0, "Page " + str(pageNo))

Then, pass this function as argument to PDFWriter instance::

	PDF.overlay = OverlayFunction

Get number of pages
~~~~~~~~~~~~~~~~~~~
At any time, you can read the current number of pages of the PDF::

	NumberOfPages = PDF.getPageNumbers()

Examples
~~~~~~~~
`Examples`__ are included on github. These should outline almost all capabilities.

__ https://github.com/szihlmann/esc2pdf/tree/main/examples

Other libraries
===============
Key advantages of esc2pdf are:

* Platform independence.
* Ability to handle CONTINUOUS/incomplete streams of ESC/P-data (real case when listening to a port). Enables *live printing*.
* Setup in minutes with only Python and reportlab as prerequisites (pure Python).
* Generate PDF output with real text and not bitmap.

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
