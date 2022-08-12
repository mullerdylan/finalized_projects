# query.py
import sqlite3
import datetime
import cx_Oracle
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\r17kc0\Downloads\instantclient_19_11")


###create SQLITE3 table if one doesn't exits
global conn, c
conn = sqlite3.connect('AGV_Stat.db')
c = conn.cursor()
c.execute(""" CREATE TABLE IF NOT EXISTS AGV_Stat (
                VEHICLE text,
                Status text,
                Entry_time text
            ) """)
conn.commit
conn.close

# Establish the database connection
connection = cx_Oracle.connect(user="AMSADMIN", password="Am$tcprod!admin",
                               dsn="56.72.27.24/TCPRODMGMT")
cursor = connection.cursor()


# QUERY For AGV names 
DBQUERY = """
    SELECT DISTINCT VEHICLE       
    FROM "AMSADMIN"."TBL_AGVVEHICLEHISTORYLOG"
    WHERE IP_ADDRESS = '56.229.1.79' AND trunc(status_change_end_date_time) BETWEEN TRUNC(SYSDATE-1) and trunc(SYSDATE)
    ORDER BY  VEHICLE
     """

#for each vehicle name returend, insert vehicle name to SQLite3 Db
cursor.execute(DBQUERY)
for row in cursor:
    Entry_time = datetime.datetime.now()
    VEHICLE_NAME = row[0]
    print(VEHICLE_NAME)
    STAT = 'ELIGIBLE'
    c.execute("INSERT INTO AGV_Stat VALUES (:VEHICLE, :Status, :Entry_time)   ",
            {
                'VEHICLE': VEHICLE_NAME,
                'Status': STAT,
                'Entry_time': Entry_time,    
            })
conn.commit()            
cursor.close()


