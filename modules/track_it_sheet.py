'''
    Defines the TrackItSheet class which is based on the readxl class from 
    the pylightxl 3rd party library. 
    TrackItSheet could be a custom class of readxl.
    https://pylightxl.readthedocs.io/en/latest/quickstart.html#
    
    credit: https://stackoverflow.com/questions/35763593/convert-list-of-lists-to-list-of-dictionaries
    29/07/2022
    https://realpython.com/python-zip-function/
    
    Dependencies: 
        pylightxl v1.60

    @author:    Liam Stubbington
                RT Physicist, Cambridge University Hospitals NHS Foundation Trust       

    Example usage:
    
    from os import path     
    from track_it_sheet import TrackItSheet
    f_root = "//GBCBGPPHFS001.net.addenbrookes.nhs.uk/Dosimetry/track-it"
    f_name = "a-spreadsheet.xlsx"
  
    f_path = path.join(f_root, f_name)
    print(f_path)
    
    dat = TrackItSheet(f_path)



'''

from pylightxl import readxl
from modules.ptw_xml import PTWTrackItXML
from re import sub

class TrackItSheet():
    '''
        The TrackItSheet class tries to read the user's xlsx file.
        If successful, the object will have the following attributes:
            comment - Named range called Comment 
            machineID - Named range called RadiationID
            params - TRACK-IT Parameters as python dict
            dtypes - TRACK-IT DataTypes as python dict 
            meas - TRACK-IT Measurements as python dict 
            information - python dict used to keep track of the things like author & software 
            ptw_xml - instance of the ptw_xml class based on the information above 
            _status - used for debugging 
        
    ''' 
    def __init__(self, f_path, *args, **kwargs):
        self._status = True
        self._version = "2.2"
        
        
        with open(f_path, 'rb') as f:
            try: 
                self.db = readxl(f, ws=("TRACK_IT"))
            except UserWarning as uw:
                self.db = None
                self._status = False 
                self._error_message = (
                    "Did not find a worksheet tab called TRACK_IT.\n"
                    "Check the underscore and capitalisation and try again."
                )

                
        if self.db:
            try: 
                self.machineID = self.db.nr(name="RadiationUnit")[0][0].strip()
                self.dtypes = TrackItSheet.dict_from_xltable(self.db.nr(name="AnalysisValues"))
            except:
                self._status = False
                self._error_message = (
                    "Error! \n"
                    "Please check named ranges in spreadsheet:\n"
                    f"{f_path}\n\n"
                    "RadiationUnit (exists and is not blank)\n"
                    "AnalysisValues (exists)\n"
                    )

            try:
                author = sub(r'[^\w\s]', '_', self.db.nr(name="Author")[0][0].strip())
                # All non-alphanumeric characters should be replaced in author field 
            except:
                author = "No Name"

            try: 
                source = self.db.nr(name="Title")[0][0].strip()
            except:
                source = "MS Excel"
            
            self.information = {"author":author,"source": source}
                
            try: 
                self.comment = sub(r'[^\w\s]', '_', self.db.nr(name="Comment")[0][0].strip())
                # if this is empty, a [[]] object is returned, which results in an indexing error 
                # not clean 
                # All non-alphanumeric characters should be replaced in author field 
            except:
                self.comment = ''
                
            try:
                self.params = TrackItSheet.dict_from_xltable(self.db.nr(name="Parameters"))
            except:
                self.params = None

            try:
                self.meas = TrackItSheet.dict_from_xltable(self.db.nr(name="Measurements"))
            except:
                self.meas = None 
            
            if self._status:

                if self.machineID=="":
                    self._status = False
                    self._error_message = (
                        "RadiationUnit cell is blank.\n"
                        "You have not defined a LINAC, HDR or kV unit.\n"
                        "Please adjust and try sending data again. "
                    )

                if not any("measuringdevice" in row for row in self.dtypes):
                    self._status = False 
                    self._error_message = (
                        "Check that you have a MeasuringDevice defined for each "
                        "Analysis Value."
                    )

            if self._status:
                
                self.ptw_xml = PTWTrackItXML(comment=self.comment,
                 machineID= self.machineID,
                 params=self.params,
                 dtypes=self.dtypes,
                 meas=self.meas,
                 information=self.information)
            
                # check the PTWTrackItXML build 
                if self.ptw_xml.check_init():
                    self.ptw_xml.generate_xml() 
                else:
                    self._status = False
                
    @staticmethod     
    def dict_from_xltable(xltable):
        heads = [item.strip().lower() for item in xltable[0]]
        body = xltable[1:]
        #body = [list(sublist) for sublist in list(zip(*body))]
        return [{k:TrackItSheet.strip_white_space(v) 
                 for k,v in zip(heads, row)} for row in body]
    
    @staticmethod
    def strip_white_space(arg):
        if isinstance(arg, str):
            return arg.strip()
        else:
            return arg 



