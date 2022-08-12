from re import sub
from tkinter import *
import datetime
import sched, time
import sys
import sqlite3
import pandas as pd
import cx_Oracle
import win32com.client
# external creds python script, not shared for security
import creds

##outlook set up files
outlook = win32com.client.Dispatch('outlook.application')

sys_user = creds.user
password = creds.password
dsn = creds.dsn

#ENSURE TO CHANGE THIS TO ABOLUTE PATH
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\r17kc0\Downloads\instantclient_19_11")
# Establish the database connection
connection = cx_Oracle.connect(user=sys_user, password=password,
                               dsn=dsn)
s = sched.scheduler(time.time, time.sleep)

#TKINTER set up files
root = Tk()
root.geometry("960x540")
root.title("USPS HONCHO")

# sets background image template 
bg = PhotoImage(file = "uspslogo.png")
#defines canvas settings/removes border highlight
my_canvas = Canvas(root, width = 960, height =540, bd = 0, highlightthickness=0)
my_canvas.pack(fill = "both", expand = True)

#set image in canvas 
my_canvas.create_image(0,0, image = bg, anchor = "nw")
#Creates static text
runstat ='Process started at   %s' %(datetime.datetime.now())

my_canvas.create_text(10,520, text= "dylan.muller@usps.gov", anchor = "nw", font = ("helvetica",8) ,fill= "white")
my_canvas.create_text(25,350, text= "AGVs Reported Will Appear Here:", anchor = "nw", font = ("helvetica",15) ,fill= "white")

#sets timeout counter to 0 on reset
a = 0
querycount = 0

#defines variable text values for timeout counter and last AGV reported 
vartext  = my_canvas.create_text(25,370, text= "", anchor = "nw", font = ("helvetica",15) ,fill= "red")
vartextcount  = my_canvas.create_text(650,50, text= 'Emails sent %s' %a, anchor = "nw", font = ("helvetica",15) ,fill= "red")
vartextquerycount  = my_canvas.create_text(800,50, text= 'Query Count  %s' %querycount, anchor = "nw", font = ("helvetica",15) ,fill= "green")
vartextquerytime = my_canvas.create_text(800,40, text= "", font = ("helvetica",10) ,fill= "gray")
vartextlog = my_canvas.create_text(150, 90, text= "", font = ("helvetica",7) ,fill= "gray")
vartextstart = my_canvas.create_text(800,20, text= "", font = ("helvetica",10) ,fill= "gray")
global vartextcurstat
vartextcurstat = my_canvas.create_text(600,360, text= "Process will restart in 30 Seconds " , font = ("helvetica",15) ,fill= "white")

print(runstat)

def submit():
    my_canvas.itemconfig(vartextstart, text= runstat,  font = ("helvetica",10) ,fill= "gray" )
    global a, querycount
    global conn, c, entry_time
    entry_time = datetime.datetime.now()
    querycount = querycount + 1
    my_canvas.itemconfig(vartextquerycount, text= 'Query Count  %s' %querycount, anchor = "nw", font = ("helvetica",15) ,fill= "green" )
    my_canvas.itemconfig(vartextquerytime, text= 'Last Query Started At %s' %entry_time,  font = ("helvetica",10) ,fill= "green" )
    
    conn = sqlite3.connect('AGV_Stat.db')
    c = conn.cursor()
    cursor = connection.cursor()
    # QUERY For AGV names, way more complicatd than it should be  
    AGMV_LAST_STAT = """
        SELECT * FROM(
            SELECT "VEHICLE",
            "BATTERYLEVEL",
            "STATUS_CHANGE_START_DATE_TIME",
            "STATUS_CHANGE_END_DATE_TIME",
            "IP_ADDRESS",
            
        TRUNC("STATUS_CHANGE_START_DATE_TIME") AS DAYVAL,
        RANK() OVER ( PARTITION BY VEHICLE ORDER BY STATUS_CHANGE_END_DATE_TIME DESC ) AS CAT
        FROM "AMSADMIN"."TBL_AGVVEHICLEHISTORYLOG"
        where trunc(status_change_end_date_time) BETWEEN TRUNC(SYSDATE-1) and trunc(SYSDATE)
            AND IP_ADDRESS = '56.229.1.79'
            AND BATTERYLEVEL > 0 )
        WHERE CAT = 1
            
        ORDER BY "VEHICLE" 
        """

    #QUERY THE LAST STATUS OF ALL AGVS
    print('######query started########')
    cursor.execute(AGMV_LAST_STAT)
    print('#####QUERY EXECUTED########')
    dfdb = pd.read_sql_query(AGMV_LAST_STAT, connection)
    dfdb_table = dfdb[['VEHICLE', 'BATTERYLEVEL','STATUS_CHANGE_END_DATE_TIME']].set_index('VEHICLE')
    my_canvas.itemconfig(vartextlog, text= '%s' %dfdb_table,  font = ("helvetica",7) ,fill= "gray" )

    print('######query evaluated########')
    for row in cursor:
        VEHICLE = row[0]
        Battery_level = int(row[1])
        Last_reported = row[3]
        #IF BATTERY LEVEL IS BELOW 25% FIND THAT VEHICLE IN STATUS TABLE
        if Battery_level < 25:
            c.execute("SELECT VEHICLE, Status FROM AGV_Stat WHERE VEHICLE = (?)", [VEHICLE])
            for row in c: 
                status2 = row[1]
                VEHICLE2 = row[0]
                #IF STATUS IS ELIGIBLE, SEND EMAIL 
                if status2 == 'ELIGIBLE':
                    lowbattime = datetime.datetime.now()
                    my_canvas.itemconfig(vartext, text= '%s at %s' %(VEHICLE2 ,lowbattime), anchor = "nw", font = ("helvetica",15) ,fill= "red" )
                    my_canvas.itemconfig(vartextcount, text= 'Emails sent %s' %a, anchor = "nw", font = ("helvetica",15) ,fill= "red" )
                    mail = outlook.CreateItem(0)
                    mail.To = 'dylan.muller@usps.gov'
                    mail.Subject = 'Low Battery Alert for %s' %(VEHICLE2)
                    # mail.HTMLBody = '<h3>This is HTML Body</h3>'
                    mail.Body = "%s Reported a battery Percentage of %s at %s. The last reported status was from %s" %(VEHICLE2, Battery_level,lowbattime, Last_reported)
                    mail.Send()
                    print(status2 + ' Email sent ' )
                    a = a +1
                    if a ==10:
                        sys.exit(' Event counter has reached max value ')
                #UPDATES DATA TABLE ELIGIBILITY, NEEDS TO BE LAST
                    c.execute("UPDATE AGV_Stat SET Status = 'INELIGIBLE' , Entry_time = (?) WHERE VEHICLE = (?)", [entry_time, VEHICLE])
                    conn.commit()
        #UPDATES RESULTS OUTSIDE OF THRESHOLD TO ELIGIBLE TO HANDLE WHEN AGV RETURNS TO 100%            
        else: 
            c.execute("UPDATE AGV_Stat SET Status = 'ELIGIBLE' , Entry_time = (?) WHERE VEHICLE = (?)", [entry_time, VEHICLE]) 
            conn.commit()
            # print('AGVDBupdated')
        
        conn.commit()
    cursor.close()  
    c.close()
    root.after(30000,submit)

#SHOW records of eligibilty table
def eligible_query():
    conn = sqlite3.connect('AGV_Stat.db')
    df = pd.read_sql_query("SELECT * from AGV_Stat", conn)
    df.set_index('VEHICLE')
    df2 = df['VEHICLE']
    top = Toplevel()
    top.title('AGV Eligibility')
    Label(top,text= df).pack()
    conn.commit()
    conn.close()

def end_loop():
    sys.exit(' Event counter has reached max value ')

query_btn = Button(root, text = "Start Query", width=20, command= submit)
my_canvas.create_window(860,520,window= query_btn)

Show_eligible = Button(root, text = "Show Eligible AGVs", width=25, command = eligible_query)
my_canvas.create_window(470,520,window= Show_eligible)

checkout_btn = Button(root, text = "End Program", width=25, command= end_loop)
my_canvas.create_window(670,520,window= checkout_btn)

root.mainloop()