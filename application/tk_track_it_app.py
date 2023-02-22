'''
    Defines the GUI classes instantiated in ../main.py 
    
    Dependencies: 
        tkinter 

    @author:    Liam Stubbington
                RT Physicist, Cambridge University Hospitals NHS Foundation Trust      

'''

import tkinter as tk
from tkinter import ttk 
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from os import path
from modules.track_it_sheet import TrackItSheet

# COLOURS 
PRIMARY = "#0D3B66"
SECONDARY = "#D9DBF1"
LIGHT_BACKGROUND = "#D0CDD7"
LIGHT_TEXT = "#ACB0BD"
DARK_TEXT = "#C44900"

# -- Frame (root) inherited class --
class TrackItApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #photo = tk.PhotoImage(file=path.normpath(r"\\GBCBGPPHFS001.net.addenbrookes.nhs.uk\Dosimetry\track-it\app\icon.ico"))
        #self.iconphoto = (False, photo)
        
        self.__version__ = "2.2"
        
        self.iconbitmap(path.normpath(r"\\MOSAIQAPP-20\mosaiq_app\TOOLS\TRACK-IT\ExportToDatabase\Track-it\TrackIt.ico"))

        self.title("MS Excel App --> PTW TRACK-IT v" + self.__version__)
        self.columnconfigure(0,weight = 1)
        self.rowconfigure(0,weight=1)

        self.geometry("800x300")
        self.resizable(True, True) 
        
        self.tk_frame = TrackItFrame(self)
        self.tk_frame.grid(row = 0,
                  column = 0,
                  sticky = "NSEW")

class TrackItFrame(ttk.Frame):
    '''tk.Frame class to hold widgets and launch filedialog'''
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # -- STYLING --
        style = ttk.Style(self) 
        style.theme_use("clam")
        
        
        style.configure('TButton', 
        background = LIGHT_BACKGROUND, 
        foreground = DARK_TEXT,
        font = ("Calibri", 12),
        )
        
        style.configure('TFrame', 
        background = PRIMARY,
        foreground = SECONDARY, 
        )
        
        style.configure('TLabel', 
        background = SECONDARY,
        foreground = PRIMARY, 
        font = ("Calibri", 12),
        )

        self.fd_label_text = tk.StringVar(value="No spreadsheet selected.")
        # label text 

        self.columnconfigure(0,weight = 1)
        self.columnconfigure(1,weight=1)
        self.rowconfigure((0,1), weight = 1)
        self.paddings = {"padx": 45, "pady":45}

        # -- File dialogue --
        self.fd_button = ttk.Button(self,
                                   text = "Open spreadsheet: ",
                                   command = self.select_file,
                                   
                                   )
        self.fd_button.grid(row=0, column = 0,
                            **self.paddings,
                            sticky = "NSEW")

        # -- File dialogue text --
        self.text_label = tk.Text(self, width=40, height=4, font = ("Calibri", 12))
        # height is in lines, width in chars 
        self.text_label.configure(foreground=PRIMARY,
                                  background=SECONDARY,
                                  borderwidth=2,
                                  relief="flat")
        self.text_label.grid(row = 0, column = 1,
                           **self.paddings,
                           sticky = "NSEW"
                           )

        # -- TRACK-IT button --
        self.ptw_button  = ttk.Button(self, text = "Export to TRACK-IT over HTTPS...",
                                command = self.export_xml)
        self.ptw_button.grid(row=1, column = 0,
                             columnspan = 2, 
                             **self.paddings,
                             sticky = "EW", 
                             )
                                     

    # -- INSTANCE METHODS -- 
    def select_file(self):
        file_types = (("All files", '*.*'),
                      ("Text files", '*.txt'),
                      ("csv files", '*.csv'),
                      ("xlsx files", '*.xlsx'),
                      ("xlsm files", '*.xlsm')
                      )

        try:               
            self.f_path = fd.askopenfilename(
                title = "Select spreadsheet",
                initialdir=r"\\GBCBGPPHFS001.net.addenbrookes.nhs.uk\Dosimetry\track-it\excel-templates",
                filetypes=file_types
                )
        except IOError as ie:
            self.f_path = None

        if self.f_path:
            self.ts = TrackItSheet(self.f_path)
            
            if self.ts._status:
                self.text_label.delete("1.0","end") 
                self.text_label.insert("1.0",f"Reading: {path.split(self.f_path)[-1]}")
            else:
                self.text_label.delete("1.0","end")             
                self.text_label.insert("1.0",f"Error reading: {path.split(self.f_path)[-1]}")
                mb.showerror(
                    title = "Error!",
                    message = self.ts._error_message 
                )
            
    
    def export_xml(self):
        # mw = mb.showinfo(title = "Information", 
                         # message = ("Close the PTW TRACK-IT Export Service Window \n"
                         # "When progress bar completes")
                         # )
        if self.ts._status:
            self.ts.ptw_xml.print_xml()
            self.ts.ptw_xml.export_xml() 
            self.ts.ptw_xml.build_xml_log()
            self.text_label.delete("1.0","end") 
            self.text_label.insert(
                "1.0",
                f"Sent {path.split(self.f_path)[-1]}"
                " to PTW TRACK-IT.\n\n"
                "Click open spreadsheet to start again."
            )

        else:
            warning = mb.showerror(
                title = "XML build error!",
                message = "Something went wrong\nPlease check the logs.",
                )

        
        
