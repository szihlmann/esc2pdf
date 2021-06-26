import os

def readbindata(*args): # folders and file as individual arguments ('folder', 'file.esc')
    # open file in binary mode 'rb' and read data
    filepath = os.path.join(*args)
    f = open(filepath, "rb")
    rawdata = f.read()
    f.close()
    return rawdata