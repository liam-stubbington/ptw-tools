# PTW Tools 

This project describes a set of tools for interfacing with PTW software. 

External dependencies: 
- progress==1.6
- pylightxl==1.60
- xmltodict==0.13.0
- yattag==1.14.0

---

## Using the TRACK-IT Import Client 

PTW TRACK-IT is a proprietary SQL database for Radiotherapy QA data with a HTML front-end. 

Data can be entered manually, or can be imported from xml. 

PTW provide a client application and an informal description of the [xml format](Track-it%20XML%20Format%20Description.pdf) for transfer and subsequent import of QA data to TRACK-IT.  

A copy of the client application, which comes with most PTW software.

This project contains a collection of modules that facilitate the use of the TRACK-IT Import Client. 

The modules contained herein can be used to transfer data from:

- MS Excel Spreadsheets 
- Analysis of DICOM files using ImageJ or pylinac 
- MPC Results.csv files 
- TQA exports
- ... 

The possibilities are endless. 

---

### TRACK-IT XML Structure 

TRACK-IT expects data to arrive in a certain format. There are a few key elements of each measurement record. 

| Name | Description | ValueTypes | Example |
| ---  |  ---        | ---        | --- |
| Parameters |  Treatment delivery system settings required to produce the measurement. These must be the same to group measurements together into a single series when using the Trends utility. | String <br> Boolean <br>Long <br>Double<br>Area "XxY"<br>Modality | Depth 5.0cm (Double)
| Measurements  | Raw values associated with each derived analysis value. These cannot be trended and are largely ignored by TRACK-IT.| String <br> Boolean <br> Long <br> Double <br> Profile <br> PDD <br> UserDefined | Reading [nC] (Double) |
|AnalysisValues | Values derived from an analysis protocol. In general, these are the values you wish to track and trend across time. Analysis values can also be associated with Reports. | Boolean <br> Long <br> Double | Output [cGy/MU] 

#### Booleans
TRACK-IT accepts the following Boolean Arguments. 

| DataType | Boolean Arguments | Notes |
| --- | --- | --- |
| Parameters | True or False | Pass a string variable equal to "True" or "False"
| Measurements | Yes  or No  | 0 is No, all other integer arguments are Yes. 
| AnalysisValues | Pass, Fail or Warning | 0 is False, 1 is True, 2 is Warning. 

The general logic for booleans implemented in this project is that if the value passed contains a t, p or y the result will be True, an n or f, results in False and if warn is in the argument a Warning will be passed (AnalysisValues only).

#### A note on Measurements 
Ancillary data can be attached to TRACK-IT record via Measurements. This data must be given to TRACK-IT as 64-bit encoded. The PTWTrackItXML Class has helper methods to assist with this. 

---

### The PTWTrackItXML Class

[.//modules/ptw_xml.py](../modules/ptw_xml.py)

This is the workhorse of the xml transfer. 
Once you have initialised an object of class PTWTrackItXML, the rest is easy.  

#### Attributes 
| Attribute | Notes | Example |
| --- | --- | --- |
| comment | TRACK-IT Comment | `"Test Comment"` |
| machineID | TRACK-IT RadiationUnit | `"DummyLINAC"` |
| params | TRACK-IT Parameters as list of python dicts. The following keywords should be defined in each dictionary: <br><ul><li> track-it</li><li>unit (optional)</li><li>values</li><li>valuetype</li></ul> | ```params = [{"track-it":"*Gantry Angle", "values":90.0, "unit":"Deg", "valuetype":"Double"}] ```|
|dtypes| TRACK-IT AnalysisValues as list of python dicts. The following keywords should be defined in each dictionary: <br><ul><li> track-it</li><li>unit (optional)</li><li>values</li><li>valuetype</li><li>definition</li><li>comment (optional)</li><li>measuringdevice</li></ul> | ```dtypes = [{"track-it":"*Output", "values":1.003, "unit":"cGy/MU", "valuetype":"Double", "definition": "QA", "measuringdevice": "F18"} ] ```|
| meas | TRACK-IT Measurements list of python dicts. The following keywords should be defined in each dictionary: <br><ul><li> track-it</li><li>unit (optional)</li><li>values</li><li>valuetype</li></ul> | ```meas = [{"track-it":"Mean Reading", "values":3.1459, "unit":"nC", "valuetype":"Double"}] ```|
| information | dict with the following kwargs: <br><ul><li>author</li><li>source</li></ul>| ```info = {"author":"ANON","source":"MS Excel"}```
| measurement_date |   python datetime object, corresponding to the date of measurement. <br><br> If blank, defaults to `datetime.utcnow()`| `measurement_date = datetime(year=2023,month=2,day=14)`
| import_client_path | path to PTW ExportToDatabase.exe (default) | `"\\MOSAIQAPP-20\mosaiq_app\TOOLS\TRACK-IT\ExportToDatabase\TrackItExporter.exe"`

**WARNING:** The TRACK-IT kwarg controls your variables label in TRACK-IT. Prefix Parameters and AnalysisValues with a * to avoid corrupting exiting proprietary DataTypes or Parameters. 

#### Methods 
- generate_xml -> None 
    - Generates the xml doc string using the yattag library patterns. 
- print_xml(f_path = None) -> None
    - prints the xml string to file 
    - optional f_path argument (default `./xml`)
- export_xml -> None 
    - calls the PTW ExportToDatabase.exe as a subprocess 
- build_xml_log -> None
    - Writes an xml build log string to file 
    - `./log`

The PTW ExportToDatabase.exe tool can be called from the command line. The following will bring up a help menu. 

```
<path-to-ExportToDatabase.exe> -h
```

#### Example Usage
```
from pylightxl import readxl
from modules.ptw_xml import PTWTrackItXML
from re import sub
from datetime import datetime 

ptw = PTWTrackItXML(
    comment = "",
    machineID = "DummyLinac", 

    params = [{
        "track-it":"*Gantry Angle",
        "values":90.0, 
        "unit":"Deg", 
        "valuetype":"Double"
    }],

    dtypes = [{
        "track-it":"*Output",
        "values":1.003, 
        "unit":"cGy/MU", 
        "valuetype":"Double", 
        "definition": "QA", 
        "measuringdevice": "F18"
    }],
                
    meas = [{
        "track-it":"Mean Reading", 
        "values":3.1459, 
        "unit":"nC", 
        "valuetype":"Double"
    }],

    information = {
        "author" : "Marty McFly",
        "source" : "MS Excel Spreadsheet 1.0"
    },

    measurement_date = datetime(
        year = 2023,
        month = 10,
        day = 21
    ),

    import_client_path = 
    "C:/Program Files (x86)/PTW/Tools/ExportToDatabase/TrackItExporter.exe",
)

ptw.generate_xml() 
ptw.print_xml(f_path = "C:/Users")
ptw.export_xml() 
   
```


---

### The TrackItSheet Class
[.//modules/track_it_sheet.py](../modules/track_it_sheet.py)

This is a convenience class for reading well formatted MS Excel spreadsheets. <br>
It is supposed to facilitate the creation of a PTWTrackItXML object. 

#### Attributes 
- comment: Named range called Comment 
- machineID: Named range called RadiationID
- params: TRACK-IT Parameters as python dict
- dtypes: TRACK-IT DataTypes as python dict 
- meas: TRACK-IT Measurements as python dict 
- information: python dict containing author and source fields
- ptw_xml: instance of the ptw_xml class based on the information above 

For more information, see the [PTWTrackItXML Class notes.](#the-ptwtrackitxml-class)

#### Formatting the spreadsheet 

The TrackItSheet class is looking for a tab called **TRACK_IT**. 

In this tab, several named ranges of cells should be defined.
Order is not important, but all must be present in the spreadsheet. 
The column headings need to be included in the named range. 

Empty cells are ignored.

| Named Range | Column Headings |
| --- | --- | 
AnalysisValues | TRACK-IT, Values, Unit, Definition, ValueType, Comment, MeasuringDevice |
| Measurements | TRACK-IT, Values, Unit, ValueType |
| Parameters | TRACK-IT, Values, Unit, ValueType |  

Some single cell references must also be defined: 
- RadiationUnit 
- Author
- Title (spreadsheet name and version number)
- Comment 

Your goal is then to design a spreadsheet front-end for the end-user and then map the values in this front-end into the TRACK_IT tab. 

You can design the front-end however you wish, however it is advisable to use sheet protection, data-validation and other MS Excel tools to control and validate user input before transfer to TRACK-IT. 

**WARNING:** The TRACK-IT column controls your variables label in TRACK-IT. Prefix Parameters and AnalysisValues with a * to avoid corrupting exiting proprietary DataTypes or Parameters. 

#### Example Usage 
```
from os import path     
from modules.track_it_sheet import TrackItSheet
f_root = "//GBCBGPPHFS001.net.addenbrookes.nhs.uk/Dosimetry/track-it/excel-templates"
f_name = "boilerplate-spreadsheet.xlsx"

f_path = path.join(f_root, f_name)
print(f_path)

dat = TrackItSheet(f_path)
print(dat.params)
print(dat.dtypes)
print(dat.comment)
print("Etc.")
```

---

### The MPC Service
[.//modules.ptw_mpc.py](.//modules.ptw_mpc.py)

The TrueBeams store MPC data in Results.csv folders, on a per MPC run basis, on the va_transfer drive.

This is another convenience class for reading MPC Results.csv output files and generating a PTWTrackItXML object.

The MPCChecks directory has a carefully formatted filename that contains the LINAC S/N, energy and datetime of the measurement. 

`NDS-WKS-SN2795-2022-11-16-07-46-30-0004-BeamCheckTemplate10x`

All of these are used in the construction of a TRACK-IT record. The conversion from S/N to RadiationUnit is controlled by [radiation_units.csv](./mpc/config/radiation_units.csv), the energy identifier is controlled by [energies.csv](./mpc/config/energies.csv) and the presentation of the data in TRACK-IT (Measurements vs AnalysisValues) is controlled by [config.csv](./mpc/config/config.csv). 

#### Attributes 

- f_name: str 
    - Path to MPC Results.csv file. 
    - Is broken down into constituent parts. 
- sn: LINAC serial number. 
    - Used in look-up ../config/radiation_units.csv
    - Assigns TRACK-IT RadiationUnit. 
- acquisition_date: 
    - Datetime object.
    - MPC acquisition date. 
- params:
    - List of dicts. 
    - Parameters passed to TRACK-IT per MPC record. 
- dtypes:
    - List of dicts.
    - DataTypes passed to TRACK-IT per MPC record. 
- meas:     
    - List of dicts.
    - Measurements passed to TRACK-IT per MPC record.

For more information, see the [PTWTrackItXML Class notes.](#the-ptwtrackitxml-class)

#### Methods 

| Method | Returns | Notes| 
| --- | --- | --- |
| check_acquisition_date_greater_than | bool | Only send MPC records after a certain date. <br>Nightly service, this may be midnight yesterday. |
|merge_config_and_data | None | combines the config.csv and Results.csv files |
| export_to_track_it | int | Process return code for confirmation of successful export.   

*You will need to configure an admin account in your instance of TRACK-IT.*

Define USERNAME and PASSWORD in the [admin_mpc.py](/mpc/admin_mpc.py) file.

#### Example Usage 
```
import os
from glob import glob
from modules.ptw_mpc import MPCPTWXml
from datetime import datetime
import time

PATH = "./data/"
EXT = "*.csv"
    
all_csv_files = [f
                 for path, subdir, files in os.walk(PATH)
                 for f in glob(os.path.normpath(
                     os.path.join(path, EXT)))
                     ]

# datetime(year, month, day, hour, minute, second, microsecond)
dt = datetime(
    year=2022,
    month=11,
    day=16,
)

files_to_process = [
    MPCPTWXml(mpc_csv).export_to_PTW() 
    for mpc_csv in all_csv_files
    if MPCPTWXml(mpc_csv).check_acquisition_date_greater_than(dt)
]
```

---

### QuickCheck XMLs 

PTW QuickCheck writes database files in .qcw format - which is just a lightweight version of xml.

The data is organised into AnalysisValues and Measurements. AnalysisValues are available for trending and Measurements are ancillary - similar to TRACK-IT. 

Each AnalysisValue has an aossciated set of Parameters: Min, Max, Norm, Target. 

Occasionally, QA requires that you rebaseline these values across the entire database. 

The PTWQuickCheckDBTool class provides a script object for easy manipulation of these AnalysisParameter values. 

Simply provide a config.csv with the name of your analysis parameter and the values of Min, Max, Target and Norm. 

For example:

![Example config.csv file for working with QuickCheck .qcw database files.](/quick_check/config.png)

#### Attributes
- qcw_in 
    - xmltodict instance of input qcw database file 
- config
    - List of dicts.
        - Used to change AnalyzeParams in qcw file 

#### Methods 
- change_all_analysis_params
    - Change the Min, Max, Target and Norm for all 
    elements matching an AdminValue condition. 
- write_new_qcw_file
    - Write the modified database to file. 

#### Example Usage 

```
from quick_check.quick_check import PTWQuickCheckDBTool

my_db_tool = PTWQuickCheckDBTool(
    qcw_in = "LA1.qcw",
    config_csv = "./quick_check/config.csv"
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
    f_out = "MODIFIED_QCW2.qcw"
)

```

