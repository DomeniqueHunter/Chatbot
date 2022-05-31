import sqlite3
import os
from pathlib import Path

from database.Tables import DB_TABLE, DB_TABLES

class DB_WRAPPER():
    
    def __init__(self, database):
        self.database = database
        self.connection = None
        self.cursor = None
    
    def setup(self):
        pass
    
    def connect(self, timeout = 5):
        try:
            path = os.path.dirname(self.database)
            Path(path).mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(self.database, timeout = timeout)
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            print(e)
            return False
        
    def close(self):
        if self.connection:
            self.connection.close()
            return True
        else:
            return False
        
    def execute(self, statement):
        # with commit
        x = self._execute(statement)
        if x:
            y = self.commit()
        else:
            self.connection.rollback()
            y = False
        
        #print ("{} : {}".format(x,y))
        return x and y

    def _execute(self, statement):
        try:
            #self.cursor.execute(statement)
            cursor = self.connection.cursor()
            cursor.execute(statement)   
            return True
        except Exception as e:
            print (e)
            return False
            
    def select_all_from(self, table):
        """
        Query all rows in the tasks table
        :param conn: the Connection object
        :return:
        """
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {table}")     
        rows = cursor.fetchall()     
        for row in rows:
            print(row)
            
    def select(self, statement):
        cursor = self.connection.cursor()
        cursor.execute(statement)     
        return cursor.fetchall()     
            
    def commit(self):
        try:
            #self.cursor.execute("commit")
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False
    
    def create_table(self, table):
        if isinstance(table, DB_TABLE):
            return self._execute(table.to_string())            
        else:
            return False