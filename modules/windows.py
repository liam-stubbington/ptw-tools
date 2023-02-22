# -*- cod"ing: utf-8 -*-
'''
@author: Liam Stubbington, RT Physicist, Cambridge University Hospitals NHS Foundation Trust
version: 1.0
datetime: 03/11/2022
'''

def set_dpi_awareness():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        print("Unix based OS.")
