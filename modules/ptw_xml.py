# -*- cod"ing: utf-8 -*-
"""
The PTWTrackItXML is the work horse class of the TrackItApp. 
The main methods are: 
    generate_xml - yattag Doc class, with PTW specific formatting 
    print_xml - commits the xml content to memory 

It is initialised with the following kwargs:
    comment:            TRACK-IT Comment 
    deviceID:           TRACK-IT MeasuringDevice
    machineID:          TRACK-IT RadiationID
    params:             TRACK-IT Parameters as list of python dicts
    dtypes:             TRACK-IT DataTypes as list of python dicts 
    meas:               TRACK-IT Measurements list of python dicts
    information:        python dict used to keep track of the TRACK-IT data origin
    measurement_date:   python datetime object 
    import_client_path: path to PTW ExportToDatabase.exe  
    
Dependencies: 
    yattag v1.14
    
    
@author:    Liam Stubbington, 
            RT Physicist, Cambridge University Hospitals NHS Foundation Trust

"""

## Import modules 
from yattag import Doc, indent # formatting xmls
from datetime import datetime,timezone # generating UID
from struct import pack # for packing floats and ints into 64-bit string 
from base64 import b64encode # raw data needs to be 64-bit encoded
import os
from subprocess import run

class PTWTrackItXML():
    def __init__(self, 
                 comment,
                 machineID,
                 params,
                 dtypes,
                 meas,
                 information,
                 measurement_date = None,
                 import_client_path = os.path.normpath("//mosaiqapp-20/MOSAIQ_APP/TOOLS/TRACK-IT/ExportToDatabase/TrackitExporter.exe"),
                 *args, **kwargs):
        self._xml_build_log = []
        self.comment = comment
        self.machineID = machineID
        self.meas_date = measurement_date
        
        # Before we build the xml, we apply the necessary boolean conversions 

        self.dtypes = self.add_comments_column(dtypes)
        self.dtypes = [
            self.string_boolean_conversion(row) for row in self.dtypes
        ]
        self.meas = [
            self.string_boolean_conversion(row) for row in meas
        ]
        self.params = [
            self.param_boolean_conversion(row) for row in params
        ]

        self.information = information
        self._line0 = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        self._track_it_ip = "http://10.252.166.69:8080"
        self.import_client_path = import_client_path
        self._author = "Liam Stubbington - Addenbrooke's TRACK-IT QA Exporter"
        self._ptw = "PTW"
        self._version = "1.3"
        self.f_root = os.getcwd()
        
        self._fname = "_".join([
            information["author"].replace(" ","_"),
            information["source"].replace(" ","_"),
            datetime.now().strftime('%Y_%m_%d_%H_%M_%S'),
            ])
        
    def check_init(self): 
        ''' Useful self check method that returns true if non-empty
            machineID and deviceIDs are defined'''
        if (self.machineID!="" and self.dtypes):
            return True 
        else:
            return False 
        
    def generate_xml(self):
        '''
            Generate the xml string using the yattag patterns. 
        '''
        self.track_it_xml, tag, text, line = Doc().ttl()  
        self.track_it_xml.asis(self._line0)
        with tag(self._ptw): # root
            line('Version',self._version)
            line('Author',self._author)
            
            with tag('Content'):
                with tag('DataTypes'):
                    self._xml_build_log.append('Processing DataTypes...')
                    for row in self.dtypes:
                        if row["values"] != '':
                            self._xml_build_log.append(f"Found DataType: {row['track-it']} with value {row['values']}")
                            with tag('DataType',id = row["track-it"]): 
                                line('Name',row["track-it"])
                                line('ValueType',row["valuetype"])
                                line('Definition',row["definition"])
                                if row["unit"]:
                                    line('Unit',row["unit"])
                        else:
                            self._xml_build_log.append(f"Skipping DataType: {row['track-it']} because "
                                  "value was blank")
                            
                # define RadiationUnits, we can only measure on 1 LINAC at a time 
                with tag('RadiationUnits'):
                    with tag('RadiationUnit',id='1'): 
                        line('Name',self.machineID)
                        
                # define MeasuringDevices
                # as of version 1.2, we can have more than one of these per measurement 
                set_of_measuring_devices = set (
                    [
                        row["measuringdevice"] for row in self.dtypes
                    ]
                )
                with tag('MeasuringDevices'):
                    for measuring_device in set_of_measuring_devices:
                        with tag('MeasuringDevice',id=measuring_device):
                            line('Name',measuring_device)
                        
                # define MeasuringSoftwares - this is a useful filter on import, again 1 per xml 
                # name of source spreadsheet comes across to TRACK-IT 
                with tag('MeasuringSoftwares'):
                    with tag('MeasuringSoftware',id='1'): 
                        line('Name',self.information["source"])

                # MEASUREMENTS 
                with tag('Measurements'):

                    # enter loop through measuring devices 
                    for measuring_device in set_of_measuring_devices:
                        self._xml_build_log.append('Looking at measurements with '+measuring_device)
                        _dtypes = [row for row in self.dtypes if row["measuringdevice"]==measuring_device]

                        with tag('Measurement',
                                ('guid',"_".join([self._fname, measuring_device])), 
                                ('radiation-unit-ref','1'), 
                                ('measuring-software-ref','1'),
                                ('measuring-device-ref',measuring_device)): 
                            # associate with 1 LINAC as a time 
                            
                            # Measurement admin
                            with tag('AdminData'):
                                if self.meas_date:
                                    line('Date', self.meas_date.replace(microsecond = 0, tzinfo=timezone.utc).isoformat())
                                else:
                                    line('Date', datetime.utcnow().replace(microsecond = 0, tzinfo=timezone.utc).isoformat()) 
                                if self.comment:
                                    line('Comment',self.comment) 
                                
                                # Measurement parameters
                                if self.params:
                                    self._xml_build_log.append('Processing Parameters...')
                                    with tag('Parameters'): 
                                        for row in self.params:
                                            if row["values"] != '':
                                                self._xml_build_log.append(f"Found Parameter: {row['track-it']} with value {row['values']}")
                                                if row["unit"]: 
                                                    with tag('Parameter', 
                                                            name=row["track-it"], 
                                                            valuetype=row["valuetype"],
                                                            unit=row["unit"]):
                                                        text(str(row["values"]))
                                                else:
                                                    with tag('Parameter', 
                                                            name=row["track-it"], 
                                                            valuetype=row["valuetype"]):
                                                        text(str(row["values"]))
                                        
                                            else:
                                                self._xml_build_log.append(f"Skipping Parameter: {row['track-it']} because "
                                                    "value was blank")
                                else:
                                    self._xml_build_log.append('No parameters provided - nothing to process.')  

                            # Analysis values - tracked longitudinally in TRACK-IT 
                            self._xml_build_log.append('Processing AnalysisValues...')
                    
                            with tag('AnalyzeData'):
                                for row in _dtypes:
                                    if row["values"] != '':
                                        self._xml_build_log.append(f'Found AnalysisValue: {row["track-it"]} with value: {row["values"]}')
                                        with tag('AnalyzeValue',('data-type-ref',row["track-it"])):
                                            if "long" in row["valuetype"].lower():
                                                line('Value',int(row["values"])) # Integer
                                            else:
                                                line('Value',row["values"]) # Any other data format
                                            if row["comment"]:
                                                line('Comment',row["comment"])
                                    else:
                                        self._xml_build_log.append(f"Skipping AnalysisValue: {row['track-it']} because "
                                        "value was blank")
                            
                            # Measurement specific values e.g. temperature, pressure, chamberID 
                            with tag('MeasData'):
                                if self.meas:
                                    self._xml_build_log.append('Processing MeasData...')
                                    for row in self.meas:
                                        if row["values"] != '': 
                                            self._xml_build_log.append(f'Found MeasData: {row["track-it"]} with value: {row["values"]}')
                                            with tag('MeasValues',
                                                    ('name',row["track-it"]),
                                                    ('type',row["valuetype"]),
                                                    ):
                                                if row["unit"]:
                                                    line('Values',
                                                        PTWTrackItXML.b64_method(
                                                            row["values"],
                                                            row["valuetype"]),
                                                            unit=row["unit"]
                                                        )
                                                else:
                                                    line('Values',
                                                        PTWTrackItXML.b64_method(
                                                            row["values"],
                                                            row["valuetype"]
                                                            )
                                                        )
                                        
                                        else:
                                            self._xml_build_log.append(f"Skipping Measurement: {row['track-it']} because "
                                            "value was blank")
                                else:
                                    self._xml_build_log.append('No Measurements to process.')
                                    
                                with tag('MeasValues',
                                        ('name',"Measured by"),
                                        ('type',"String"),
                                        ):
                                    line('Values',
                                        PTWTrackItXML.b64_method(self.information["author"], "String")
                                        )
    
    def print_xml(self, f_path = None):
        ''' 
            Commit the xml string to file. 
        '''
        if f_path is None:
            f_path = os.path.join(self.f_root,"xml")
        self._f_out = os.path.normpath(os.path.join(f_path,self._fname+".xml"))
        try: 
            with open(self._f_out, "w") as o:
                o.write(indent(self.track_it_xml.getvalue()))
            self._xml_build_log.append(f"xml file generated: {self._f_out}")
        except (IOError, AttributeError) as e:
            self._xml_build_log.append(f"Could not generate xml: {e}")
            
        
    def export_xml(self):
        '''
            Export the xml to TRACK-IT using the PTW Export tool. 
            Appends the command to the log file. 
        '''
        ptw_cmd = " ".join([
                            self.import_client_path,
                            "-i",
                            self._f_out,
                            "-o",
                            self._track_it_ip,
                            ])
        
        self._xml_build_log.append('Sending to TRACK-IT via HTTPS')
        
        run(ptw_cmd, capture_output =False, )
        
        self._xml_build_log.append(ptw_cmd)
                       
            
    def build_xml_log(self):
        ''' 
            Print the basic log file list to .log file. 
        '''
        f_path = os.path.normpath(os.path.join(
            self.f_root,
            "log",
            self._fname+".log"
            )
        )
        
        with open(f_path, 'w') as w:
            w.writelines([line+"\n" for line in self._xml_build_log])
    
    def add_comments_column(self, table):
        '''
            Some legacy spreadsheets AnalysisValues do not have a comment column. 
            This needs adding to ensure backward compatability. 
        '''
        for row in table:
            if not "comment" in row:
                row["comment"]= ""
        return table
            
         
    def string_boolean_conversion(self, row):
        ''' 
            Row wise Boolean conversion for dtypes and meas. 

            Ideally, booleans would be passed as 0, 1 or 2.
            However, they might come across as any of:
                Fail, Pass, Warning, Yes/No etc. 
            String converions assumes
                p, t or y gets converted to TRUE (1) for pass, true, yes
                f, n gets converted to false for FALSE (0), no 
                warn in string variable indicates WARNING (2)

            Note that this method assumes that the user will put 
            0, 1, or 2 correctly in the spreadsheet. 
        '''
        if isinstance(row["values"],str) and "bool" in row["valuetype"].lower():

            self._xml_build_log.append(
                f"Applying boolean conversion method to {row['track-it']} with value: {row['values']}"
                )

            if any(substring in row["values"].lower() for substring in ["p","t","y"]):
                row["values"] = 1 
            elif "warn" in row["values"].lower():
                row["values"] = 2
            elif any(substring in row["values"].lower() for substring in ["f","n"]):
                row["values"] = 0
            
                
        
        return row

    def param_boolean_conversion(self, row):
        ''' 
            Row wise Boolean conversion for params.
            
            Parameters have slightly different boolean presentations. 
            Need to end up as either True or False, rather than 1 or 0. 
                If p, t or y is found in the string --> True 
                Any non-zero value --> True 
                Otherwise False. 
        '''
        if "bool" in row["valuetype"].lower():
            if isinstance(row["values"],str):
                self._xml_build_log.append(
                    f"Applying boolean conversion method to {row['track-it']} with value: {row['values']}"
                    )
                if any(substring in row["values"].lower() for substring in ["p","t","y"]):
                    row["values"] = "True"
                else:
                    row["values"] = "False"
            elif row["values"]!= 0: 
                row["values"] = "True"
            else:
                row["values"] = "False"

        return row

    # -- static methods -- not dependent on object state 
    @staticmethod
    def convert_to_b64_alphabet(bytes_value):
        ''' 
            Takes bytes and does these 2 things:
                1.) applies base64 encoding to said bytes, returning b64 encoded bytes 
                2.) decodes the bytes to base64 alphabet string 

            Remember 
                - utf-8 helps translate text to bytes 
                - base64 helps translate bytes to text 
                
        '''
        b64 = b64encode(bytes_value)
        return b64.decode('ascii', errors = 'xmlcharrefreplace')
    
    @staticmethod
    def b64_method(val,val_type):
        '''determines the byte conversion requirements
        For strings - we can use the .encode() method to get the bytes
        For ints, floats, bools as required by TRACK-IT - 
        We have to convert python native datatypes to bytes string '''
        val_type = val_type.lower()
        if val_type=='string':
            val = val.encode(encoding = 'utf-8', errors = 'xmlcharrefreplace')
        elif val_type=='double' :
            # for floats we need to use struct.pack() with a <d argument
            val = pack('<d',val)
        elif val_type=='long' or val_type=='boolean' : 
            # for ints and bools we need to use integer C type 
            val = pack('<q',val)
        return PTWTrackItXML.convert_to_b64_alphabet(val)
