# -*- cod"ing: utf-8 -*-
'''

MS Excel --> PTW TRACK-IT App

Objective: simplify the transfer of data from in-house QA spreadsheet templates to TRACK-IT.
The "programme" consists of a python virtual environment:
//GBCBGPPHFS001.net.addenbrookes.nhs.uk/Dosimetry/track-it/venv 
And a collection of python modules found in:
//GBCBGPPHFS001.net.addenbrookes.nhs.uk/Dosimetry/track-it/

The user must have python v3.10.x 64 bit installed on their Windows machine. 
Site packages are detailed in venv/requirements.txt

Module versions are detailed in ./docs/.versions

@author:    Liam Stubbington 
            RT Physicist, Cambridge University Hospitals NHS Foundation Trust
            
version: 2.2


'''

from application.tk_track_it_app import TrackItApp
from modules.windows import set_dpi_awareness 
from modules.track_it_sheet import TrackItSheet
from modules.ptw_xml import PTWTrackItXML
set_dpi_awareness()


if __name__ == "__main__":

    root = TrackItApp()
    # instantiate an object of class TrackItWindow which inherits from tk.Tk() 

    root.mainloop()
    # call the mainloop() method of our Tk class object, root

