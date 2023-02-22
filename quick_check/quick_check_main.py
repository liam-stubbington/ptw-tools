# -*- cod"ing: utf-8 -*-
'''

@author:    Liam Stubbington, 
            RT Physicist, Cambridge University Hospitals NHS Foundation Trust

'''

from quick_check import PTWQuickCheckDBTool

my_db_tool = PTWQuickCheckDBTool(
    qcw_in = "Acer_2022.qcw",
    config_csv = "config.csv"
)

# APPLY A CONDITION  
condition = {
    "AdminValue": "Info",
    "Value":"6X Output. Energy. Flat and Symm."
}
path_to_output_qcw_file = "MODIFIED_QCW.qcw"

my_db_tool.change_all_analysis_params(
    condition = condition
)

# APPLY ANOTHER CONDITION  
condition = {
    "AdminValue": "FFF",
    "Value":"Yes"
}
my_db_tool.change_all_analysis_params(
    condition = condition
)

# WRITE NEW QCW FILE 
my_db_tool.write_new_qcw_file(
    f_out = "MODIFIED_QCW_Acer2022.qcw"
)





