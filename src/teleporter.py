#!/usr/bin/env python3

from plugins.Ranch.DB_Wrapper import RANCH_DB as RanchOld
from plugins.Ranch.MySQL_Wrapper import RANCH_DB as RanchNew
import time

"""
    HOW TO USE
    1. copy ranch.db into THIS folder
    2. enter your db credentials
"""


SQLITE_FILE = "./data/chat.f-list.net/chat2/ranch.db"

sqlite = RanchOld(SQLITE_FILE)
sqlite.connect()

MYSQL_USER = "root"
MYSQL_PASS = "example"
MYSQL_DB   = "Ranch"
MYSQL_HOST = "judy.local"

mysql = RanchNew(MYSQL_USER, MYSQL_PASS, MYSQL_DB, MYSQL_HOST)
mysql.connect()
mysql.setup()

tables = ["person", "cow", "worker", "milking", "level"]

start_teleport = time.time()
for table in tables:
    
    # get all data from one table and see how big it is
    data = sqlite.select_all_from(table)
    print(f"{table}: {len(data)}")
    print(data[0])
    print()
    
    tab_len = len(data)
    index = 0
    start_teleport_table = time.time()
    for d in data:
        index += 1
        mysql.insert(table, list(d))
        
        if index % 100 == 0:
            percent = index/tab_len *100 
            print(f"  {index} - {percent:.0f}%")
            
    end_teleport_table = time.time()
    print(f"done in {end_teleport_table-start_teleport_table}s") 
    print()   
    
end_teleport = time.time()
print(f"teleport finished in {end_teleport-start_teleport}s")    
    