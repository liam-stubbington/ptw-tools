# -*- cod"ing: utf-8 -*-
'''

@author:    Liam Stubbington, 
            RT Physicist, Cambridge University Hospitals NHS Foundation Trust

'''


from os import path
import xmltodict as xmld
from csv import DictReader as dr

class PTWQuickCheckDBTool():
    '''
        Script object template for manipulating PTW QuickCheck [.qcw] 
        database files. 
    
        Attributes: 
            qcw_in 
                xmltodict instance of input qcw database file 
            config
                List of dicts.
                Used to change AnalyzeParams in qcw file 
        Methods: 
            change_all_analysis_params
                Change the Min, Max, Target and Norm for all 
                elements matching an AdminValue condition. 
            write_new_qcw_file
                Write the modified database to file. 

    '''

    def __init__(self, qcw_in: str, config_csv: str = "./config.csv"):
        '''
            Params:
                qcw_in 
                    Path to source .qcw database file 
                config_csv (optional)
                    Path to config.csv file 
                    Read as a list of dictionaries 

        '''
        try:
            with open(path.normpath(qcw_in), 'rb') as f:
                self.qcw_in = xmld.parse(f)
        except FileNotFoundError:
            print("ERROR: No database file found.")
            self.qcw_in = None
            raise FileNotFoundError
        


        try:
            with open(path.normpath(config_csv), 'r', encoding="utf-8") as f:
                self.config = list(dr(f))
        except FileNotFoundError:
            print("ERROR: Could not find config.csv file.")
            self.config = None
            raise FileNotFoundError

        for config in self.config:
            config["Min"] = "{:e}".format(float(config["Min"]))
            config["Max"] = "{:e}".format(float(config["Max"]))
            config["Norm"] = "{:e}".format(float(config["Norm"]))
            config["Target"] = "{:e}".format(float(config["Target"]))


    def change_all_analysis_params(self, condition: dict = None):
        '''
            Params:
                condition
                    dict: AdminValue, Value
                    You my not wish to modify all tags - so provide 
                    the name and value of an AdminValue e.g Energy, SDD, TreatmentUnit 
                    as a dict. Only elements matching this condition will be modified.  
        '''


        if self.config and self.qcw_in:

            td = self.qcw_in['PTW']['Content']['TrendData']

            for config in self.config:

                for element_record in td:

                    try: 
                        admin = element_record['Worklist']['AdminData']
                        if condition: 
                            if admin['AdminValues'][condition['AdminValue']] == condition['Value']: # CHANGE THIS 
                                admin['AnalyzeParams'][config['AnalysisParam']]['Min'] = config["Min"]
                                admin['AnalyzeParams'][config['AnalysisParam']]['Max'] = config ["Max"]
                                admin['AnalyzeParams'][config['AnalysisParam']]['Norm'] = config ["Norm"]
                                admin['AnalyzeParams'][config['AnalysisParam']]['Target'] = config ["Target"]
                        else:
                            admin['AnalyzeParams'][config['AnalysisParam']]['Min'] = config["Min"]
                            admin['AnalyzeParams'][config['AnalysisParam']]['Max'] = config ["Max"]
                            admin['AnalyzeParams'][config['AnalysisParam']]['Norm'] = config ["Norm"]
                            admin['AnalyzeParams'][config['AnalysisParam']]['Target'] = config ["Target"]
                    except  KeyError:
                        print("ERROR: Check all the keyword arguments again.")
                        raise KeyError
                        
        
    def write_new_qcw_file(self, f_out: str = "MODIFIED.qcw"):
        '''
            Params:
                f_out: str 
                    Path to output .qcw file. 
        '''

        try:
            with open(path.normpath(f_out), 'w', encoding='utf-8') as f_out:
                xmld.unparse(self.qcw_in, output = f_out, pretty="true")

        except IOError:
            print("Could not write new qcw file.")
            raise IOError


