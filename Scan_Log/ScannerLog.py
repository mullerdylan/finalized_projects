from operator import truediv
from sys import setswitchinterval
from tkinter import *
import sqlite3
import time
import sched
import datetime
import os
import tkinter
from xlsxwriter.workbook import Workbook
from tkinter import ttk
from win32com.client import Dispatch
import pathlib
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askyesno
import configparser
from os import close, path


root = Tk()
conn = sqlite3.connect('Scan_Log.db')
# root.geometry("960x540")
root.geometry("960x540")
root.title("USPS Scanner Checkout Application")
root.iconbitmap('usps-icon.ico')

###Color settings 
suc_col = "#61bd4f"

# sets background image template 
bg = PhotoImage(file = "uspslogo.png")
#defines canvas settings/removes border highlight
my_canvas = Canvas(root, width = 960, height =540, bd = 0, highlightthickness=0)
my_canvas.pack(fill = "both", expand = True)
#Creates input box
IB = Entry(root, font =("Helvetica", 24), width = 20, fg = "black", bd = 0)
#adds boxes to canvas
IBwindow = my_canvas.create_window(500,120,window= IB)

#set image in canvas 
my_canvas.create_image(0,0, image = bg, anchor = "nw")
#Creates static text
my_canvas.create_text(500,165, text= "Scan Employee Badge  & Scanner Barcode ", anchor = 'c',font = ("helvetica",15) ,fill= "white")
# my_canvas.create_text(10,520, text= "Tell Dylan he is bad at his job:  dylan.muller@usps.gov", anchor = "nw", font = ("helvetica",8) ,fill= "white")
vartext  = my_canvas.create_text(500,60, text= "", anchor = "c", font = ("helvetica",25) ,fill= "white")
EINLvartext  = my_canvas.create_text(25,351, text= "", anchor = "nw", font = ("helvetica",15) ,fill= "white")
SNLvartext  = my_canvas.create_text(25,391, text= "", anchor = "nw", font = ("helvetica",15) ,fill= "white")

#_________CONFIG FILE SETTINGS _________________________________
config = configparser.ConfigParser()
configfilename = 'config.ini'
configdur = os.path.dirname(os.path.abspath(__file__))
#checking to ensure config file exists, creates using below defaults
if path.exists(configfilename) == FALSE:
    config['DEFAULT'] = {'printset': 'Inactive',
                        'printer_name': 'DYMO LabelWriter 400',
                        'refresh_rate': '4000',
                        'output_path': '%s' %configdur,
                        'scanner_stringlength': '12'}
    with open(configfilename, 'w') as configfile:
        config.write(configfile)
#end config file check 

config.read(configfilename)
printset = config.get('DEFAULT','printset').upper()
printer_name = config.get('DEFAULT','printer_name')
refresh_rate = config.get('DEFAULT','refresh_rate')
output_path = config.get('DEFAULT','output_path')
if path.exists(output_path) == False:
    prompt = askyesno(title = 'Directory Error' ,message='Directory Specified in Config.ini does not exist Do you Want to fix the file path?')
    if prompt == True:
        #opens directory change dialog
        output_path = askdirectory(title='Select Folder')
        config.set('DEFAULT', 'output_path', output_path)
        with open(configfilename, 'w') as editpath:
            config.write(editpath)
    else:
        output_path = 'Invalid Path'
        exit
scanner_stringlength = int(config.get('DEFAULT','scanner_stringlength'))
#config files list [printset state,printer name, path for output file, scanner string length/condition, barcode timeout, ]

#conditional formatting for printer display. accomidates config file for printer
if printset == 'ACTIVE':
    my_canvas.create_text(2,20, text= "Printer Active", anchor = "nw", font = ("helvetica",10) ,fill= suc_col)
else:
    my_canvas.create_text(2,20, text= "Printer Inactive", anchor = "nw", font = ("helvetica",8) ,fill= 'gray')

#conditioinal formatting for filepath Display
if output_path == 'Invalid Path':
    pathtxt = my_canvas.create_text(2,5, text='Output Path is Invalid, Please Restart ' + output_path, anchor = "nw", font = ("helvetica",8) ,fill= 'Red')
else:
    pathtxt = my_canvas.create_text(2,5, text='Output Directory is: ' + output_path, anchor = "nw", font = ("helvetica",8) ,fill= suc_col)

fpath = config.get('DEFAULT','output_path') + '/output.xlsx'

#sets focus for input
IB.focus_set()

def LabelPrint():
    #printer code set up
    barcode_path = pathlib.Path('./Scanner_label_Final.label')
    labelCom = Dispatch('Dymo.DymoAddIn')
    labelText = Dispatch('Dymo.DymoLabels')

    isOpen = labelCom.Open('scanner.label')
    selectPrinter = printer_name
    labelCom.SelectPrinter(selectPrinter)
    labelCom.Open(barcode_path)

    labelText.SetField('Barcode', SN)
    labelText.SetField('ADDRESS_1', IBT)
    labelText.SetField('ADDRESS', str('EIN: ' + EIN))

    #printing barcode
    labelCom.StartPrintJob()
    labelCom.Print(1,False)
    labelCom.EndPrintJob()
# ____________________________activates printer _______________________________

###create table if one doesn't exits
conn = sqlite3.connect('Scan_Log.db')
c = conn.cursor()
c.execute(""" CREATE TABLE IF NOT EXISTS Scan (
                EIN text,
                SN text,
                Checkout_time text,
                Checkin_time text,
                scanstat text
            ) """)
conn.commit
conn.close

##show  all records query
def query():
    ##SQL query settings 
    conn = sqlite3.connect('Scan_Log.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Scan")
    recs = c.fetchall()
    ###TREE INTEGRATION 

    #table configuration settings 
    global top, tree, style
    top = Toplevel()
    tree= ttk.Treeview(top,  column=("column1", "column2", "column3","column4", "column5"), show='headings')
    top.geometry("600x200")
    top.title('ALL RECORDS')

    style = ttk.Style()
    style.theme_use("default")
    style.map('Treeview', background = [('selected','green')])
    style.configure("Treeview", background = "white",fieldbackground = "white", rowheight = 20)
    style.configure('Treeview.Heading', background = "white")
    tree.heading("#1", text="Employee ID" , anchor = 'c')
    tree.column("#1", minwidth=10, width=20, anchor = 'c', stretch=YES)
    tree.heading("#2", text="Scanner ID" , anchor = 'c')
    tree.column("#2", minwidth=15, width=35,anchor = 'c',  stretch=YES)
    tree.heading("#3", text="Check Out Time" , anchor = 'c')
    tree.column("#3", minwidth=10, width=100,anchor = 'c',  stretch=YES)
    tree.heading("#4", text="Check In Time" , anchor = 'c')
    tree.column("#4", minwidth=10, width=100,anchor = 'c',  stretch=YES)
    tree.heading("#5", text="Status" , anchor = 'c')
    tree.column("#5", minwidth=10, width=20, anchor = 'c', stretch=YES)

    # logic for table writing 
    for row in recs:
        tree.insert("", tkinter.END, values=row)
    tree.pack(expand=YES, fill=BOTH)

    conn.commit()
    conn.close()

##shows currently checkout scanners 
def checkout():
    conn = sqlite3.connect('Scan_Log.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Scan WHERE Scanstat = 'Out'")
    recs = c.fetchall()
    ####launching second window
    #table configuration settings 
    global top, tree, style
    top = Toplevel()
    tree= ttk.Treeview(top,  column=("column1", "column2", "column3","column4", "column5"), show='headings')
    top.geometry("600x200")
    top.title('ALL RECORDS')

    style = ttk.Style()
    style.theme_use("default")
    style.map('Treeview', background = [('selected','green')])
    style.configure("Treeview", background = "white",fieldbackground = "white", rowheight = 20)
    style.configure('Treeview.Heading', background = "white")
    tree.heading("#1", text="Employee ID" , anchor = 'c')
    tree.column("#1", minwidth=10, width=20, anchor = 'c', stretch=YES)
    tree.heading("#2", text="Scanner ID" , anchor = 'c')
    tree.column("#2", minwidth=15, width=35,anchor = 'c',  stretch=YES)
    tree.heading("#3", text="Check Out Time" , anchor = 'c')
    tree.column("#3", minwidth=10, width=100,anchor = 'c',  stretch=YES)
    tree.heading("#4", text="Check In Time" , anchor = 'c')
    tree.column("#4", minwidth=10, width=100,anchor = 'c',  stretch=YES)
    tree.heading("#5", text="Status" , anchor = 'c')
    tree.column("#5", minwidth=10, width=20, anchor = 'c', stretch=YES)

    # logic for table writing 
    for row in recs:
        tree.insert("", tkinter.END, values=row)
    tree.pack(expand=YES, fill=BOTH)
    
    conn.commit()
    conn.close()

def pathdef():
    config.read('config.ini')
    output_path = askdirectory(title='Select Folder')
    if output_path == '':
        my_canvas.itemconfig(pathtxt, text ='Output Path is Invalid ', fill = 'red')
    else:
        config.set('DEFAULT', 'output_path', output_path)
        with open('config.ini', 'w') as editpath:
            config.write(editpath)
        fpath = config.get('DEFAULT','output_path') + '/output.xlsx'
        my_canvas.itemconfig(pathtxt, text= fpath, fill = suc_col)

#button set up
query_btn = Button(root, text = "Show All Records", width=20, command = query)
query_window = my_canvas.create_window(860,520,window= query_btn)
checkout_btn = Button(root, text = "Show Checked Out Scanners", width=25, command = checkout)
query_window = my_canvas.create_window(670,520,window= checkout_btn)
path_btn = Button(root, width=25,text = "Change Output Path Directory",command = pathdef)
query_window = my_canvas.create_window(100,520, window= path_btn)

cond = 0
cond2 = 0

def submit():
    conn = sqlite3.connect('Scan_Log.db')
    IBL = IB.get()
    IBLength = len(IB.get()) 
    global EINL
    global EIN
    global SN
    global SNL
    global cond
    global cond2
    #Employee ID string Condition 
    if IBLength == 12 and IBL.isnumeric() == TRUE:
        #handles leading 000 in badge reader
        EIN = IBL[3:11]
        my_canvas.itemconfig(SNLvartext, text= 'EIN accepted as  %s' %(EIN), anchor = "nw", font = ("helvetica",15) ,fill= suc_col )
        my_canvas.itemconfig(vartext, text= 'EIN Accepted', fill= suc_col )
        cond = 1
    #Scanner Barcode Condition 
    elif IBLength == scanner_stringlength and IBL.isnumeric() == FALSE:
    # elif IBLength == 12 and IBL.isnumeric() == FALSE: 
        SN = IBL.upper()
        global Checkin_time
        Checkin_time = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        my_canvas.itemconfig(EINLvartext, text= 'SN accepted as  %s' %(SN), anchor = "nw", font = ("helvetica",15) ,fill= suc_col )
        my_canvas.itemconfig(vartext, text= 'SN Accepted',fill= suc_col)
        #used to check in scanner, doesn't require checkin condition to be true  
        conn = sqlite3.connect('Scan_Log.db')
        c = conn.cursor()
        c.execute("""UPDATE Scan 
                    SET Checkin_time = (?), scanstat = 'In'  
                    WHERE Checkout_time = (
                        SELECT Checkout_time FROM Scan 
                        WHERE scanstat = 'Out' AND SN =(?)  
                        ORDER BY Checkout_time  DESC limit 1
                        )""", [Checkin_time, SN] )
        # c.execute("UPDATE Scan SET scanstat = 'In' WHERE SN = (?)", [SN])
        # c.execute("UPDATE Scan SET Checkin_time = (?) WHERE SN = (?)", [checkintime,SN])
        workbook = Workbook(fpath)
        worksheet = workbook.add_worksheet()
        worksheet.write('A1', 'EIN')
        worksheet.write('B1', 'SN')
        worksheet.write('C1', 'Check Out Time')
        worksheet.write('D1', 'Check In Time')
        worksheet.write('E1', 'Status')
        

        mysel=c.execute("SELECT * FROM Scan")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i+1, j, row[j])
        workbook.close()
        conn.commit()
        conn.close()
        cond2 = 1
    else:
        if IBL == "checkin" and cond2 == 1:
            my_canvas.itemconfig(SNLvartext, text= '', anchor = "nw", font = ("helvetica",15) ,fill= "white" )
            my_canvas.itemconfig(EINLvartext, text= '', anchor = "nw", font = ("helvetica",15) ,fill= suc_col )
            my_canvas.itemconfig(vartext, text= "Scanner Checked In Successfully ",fill= suc_col)

            ##writes to excel
            conn = sqlite3.connect('Scan_Log.db')
            c = conn.cursor()
            workbook = Workbook(fpath)
            worksheet = workbook.add_worksheet()
            worksheet.write('A1', 'EIN')
            worksheet.write('B1', 'SN')
            worksheet.write('C1', 'Check Out Time')
            worksheet.write('D1', 'Check In Time')
            worksheet.write('E1', 'Status')
            

            mysel=c.execute("SELECT * FROM Scan")
            for i, row in enumerate(mysel):
                for j, value in enumerate(row):
                    worksheet.write(i+1, j, row[j])
            workbook.close()
            conn.close()
            cond = 0
            cond2 = 0
        elif IBLength>=1:
            my_canvas.itemconfig(SNLvartext, text= '', anchor = "nw", font = ("helvetica",15) ,fill= "white" )
            my_canvas.itemconfig(EINLvartext, text= '', anchor = "nw", font = ("helvetica",15) ,fill= "white" )
            my_canvas.itemconfig(vartext, text= 'Invalid input', fill= "red" )    
            cond = 0
            cond2 = 0
 
    IB.delete(0,END)
    root.after(refresh_rate,submit)
    if cond == 1 & cond2 == 1:
        my_canvas.itemconfig(SNLvartext, text= '', anchor = "nw", font = ("helvetica",15) ,fill= "white" )
        my_canvas.itemconfig(EINLvartext, text= '', anchor = "nw", font = ("helvetica",15) ,fill= "white" )
        rec = str(" SN " + SN + " EIN " + EIN)
        scanstat = "Out" 
        global IBT
        IBT = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        placeholder = '-'
        conn = sqlite3.connect('Scan_Log.db')
        c = conn.cursor()

        #_______________________________triggers label print____________________________________________________________ 
        if printset == 'ACTIVE':
            LabelPrint()
        
        c.execute("INSERT INTO Scan VALUES (:EIN, :SN, :Checkout_time, :Checkin_time, :scanstat) ", 
            {
                'EIN': EIN,
                'SN': SN,
                'Checkout_time': IBT,
                'Checkin_time': placeholder,
                'scanstat': scanstat, ##new code
            })
        
        ####writes value to excel sheet
        workbook = Workbook(fpath)
        worksheet = workbook.add_worksheet()

        worksheet.write('A1', 'EIN')
        worksheet.write('B1', 'SN')
        worksheet.write('C1', 'Check Out Time')
        worksheet.write('D1', 'Check In Time')
        worksheet.write('E1', 'Status')

        mysel=c.execute("SELECT * FROM Scan")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i+1, j, row[j])
        workbook.close()
        conn.commit()
        conn.close()
        cond = 0
        cond2 = 0
        my_canvas.itemconfig(vartext, text= "Last Succesful Record " + rec, fill= suc_col )
        
root.after(0,submit)
SubmitB = Button(root, text = "submit", command = submit)
root.mainloop()