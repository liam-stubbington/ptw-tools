from datetime import datetime, date, time, timezone
from csv import DictReader as dr
from os import path
from modules.ptw_xml import PTWTrackItXML
import subprocess
from admin_mpc import USERNAME, PASSWORD

class MPCPTWXml():
    '''
        Workhorse of the Varian MPC - PTW TRACK-IT service. 

        Attributes: 
            f_name: str 
                Path to MPC Results.csv file. 
                Is broken down into constituent parts. 
            sn: LINAC serial number. 
                Used in look-up ../config/radiation_units.csv
                Assigns TRACK-IT RadiationUnit. 
            acquisition_date: 
                Datetime object.
                MPC acquisition date. 
            params:
                List of dicts. 
                Parameters passed to TRACK-IT per MPC record. 
            dtypes:
                List of dicts.
                DataTypes passed to TRACK-IT per MPC record. 
            meas: 
                List of dicts.
                Measurements passed to TRACK-IT per MPC record. 

        Methods: 
            check_acquisition_date_greater_than --> bool
            merge_config_and_data
            export_to_track_it -- > int (Process return code)


    '''
    def __init__(self, f_path):
        # parse the file name 
        self.f_name = path.normpath(f_path).split(path.sep)[-2].split("-")
        self.sn = self.f_name[2]
        self.acqusition_date = datetime.combine(
            date(
            int(self.f_name[3]), int(self.f_name[4]), int(self.f_name[5])
        ),
        time(
            int(self.f_name[6]), int(self.f_name[7]) , int(self.f_name[8])
        )
        )

        self.__version__ = "1.0"

        # load the config file 
        with open('mpc/config/config.csv', 'r', encoding='utf-8') as fcsv:
            config = [row for row in dr(fcsv, skipinitialspace=True)]

        # load the LINAC lookup file & find radiation_unit
        with open("mpc/config/radiation_units.csv",'r') as f:
            self.radiation_unit = next(
                row for 
                row in dr(f, skipinitialspace=True) 
                if row["SN"] in self.sn
            )['RADIATION-UNIT']

        # open .config/energies.csv & set params 
        with open("mpc/config/energies.csv", newline='') as csvfile:
            energy = next(
                row for row in dr(csvfile, skipinitialspace=True)
                if row["FLAG"] in self.f_name[-1]
            )
   
        self.params = [
            {
                "track-it": energy["track-it"],
                "valuetype":energy["valuetype"],
                "unit":energy["unit"],
                "values":energy["value"]
            },
            {
                "track-it":"*MPC - FFF",
                "valuetype":"Boolean",
                "unit":None,
                "values": "FFF" in self.f_name[-1]
            },
            {
                "track-it": "*MPC - Modality",
                "valuetype": "Modality",
                "unit": None, 
                "values":energy["modality"]
            }
        ]

        # read the Results.csv data 
        with open(f_path, newline='') as csvfile:
            self.data = [row for row in dr(csvfile, skipinitialspace=True)]

        # merge the two list of dictionary objects 
        self.merge_config_and_data(config)

    def check_acquisition_date_greater_than(self, dt: datetime) -> bool: 
        '''
            Check if the MPC acquisition date is greater than or equal to
            input datetime object. 
        '''
        return self.acqusition_date >= dt

    def merge_config_and_data(self, config):
        '''
            Merge the values from the Results.csv file into the template in the 
            config file. 
        '''
        for row in config:
            for line in self.data:
                if line["Name [Unit]"]==row["Name [Unit]"]:
                    row["values"] = line["Value"]

        self.dtypes = [row for row in config if row["type"]== "dtypes" and "values" in row]
        self.meas = [row for row in config if row["type"]=="meas"]
        for row in (row for row in config if row["type"]=="params"):
            self.params.append(row)

    def export_to_PTW(self):
        '''
            Override default export location in PTWTrackItXML class.
        '''
        ptw_xml = PTWTrackItXML(
            comment = None, deviceID = "Varian MPC",
            machineID = self.radiation_unit,
            params = self.params, meas = self.meas, 
            dtypes = self.dtypes,
            measurement_date=self.acqusition_date,
            information = {
                "author": "MPC",
                "source": " ".join(["MPCService v",self.__version__]) 
            }
        )
        ptw_xml._fname = "_".join(self.f_name)
        ptw_xml.generate_xml() 
        ptw_xml.print_xml()
        password = PASSWORD
        user_name = USERNAME
        ptw_cmd = [
            ptw_xml.import_client_path,
            "-i",
            ptw_xml._f_out,
            "-o",
            ptw_xml._track_it_ip,
            "-m",
            "1",
            "-u",
            user_name,
            "-p",
            password,
            ]

        pd = subprocess.run(
            args=ptw_cmd, 
            shell = True, 
            check = True,
            timeout=60,
            text=True
            )

        ptw_xml._xml_build_log.append(f"RadiationUnit: {self.radiation_unit}")
        ptw_xml._xml_build_log.append(" ".join([item for item in ptw_cmd]))
        ptw_xml._xml_build_log.append(f"TRACK-IT Export Process return code: {pd.returncode}") 

        ptw_xml.build_xml_log() 

        return pd.returncode


            
        
