import mysql.connector as mysql
import time

def value_string(values):
    value_list = []
    for value in values:
        if type(value) == int:
            value_list.append(str(value))
        else:
            value_list.append(f"'{value}'")
            
    return ",".join(value_list)

class DB_WRAPPER():
    
    def __init__(self, user, password, database, host, port=3306):
        self.user = user 
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        
        self.tables = {}    
        
        self.connection = None
        self.cursor = None
    
    def setup(self):
        pass
    
    def connect(self, try_counter=0):
        
        try:
            self.connection = mysql.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database
                )
            
            self.connection.autocommit = False
            self.cursor = self.connection.cursor()
            return True

        except Exception as e:
            if try_counter <= 10:
                print(f"could not connect.. ({try_counter})")
                time.sleep(30)
                try_counter += 1
                return self.connect(try_counter)
                
            return False
        
    def close(self):
        if self.connection:
            self.connection.close()
            return True
        else:
            return False
        
    def add_table(self, table, if_not_exists=False):
        """
        Adds a new Table in Memory, no commit yet!
        """
        if not table in self.tables:
            self.tables[table] = DB_TABLE(table, if_not_exists)
        return self.tables[table]    
    
    def execute(self, statement):
        success_execute = self._execute(statement)
        if success_execute:
            success_commit = self.commit()
        else:
            self.connection.rollback()
            success_commit = False
        
        return success_execute and success_commit

    def _execute(self, statement):
        try:
            self.cursor.execute(statement)
            return True
        except Exception as e:
            print (e)
            return False
    
    def insert(self, table, values):        
        if type(table) == str:
            table = self.tables[table]
            
        if type(table) != DB_TABLE:
            raise TypeError
        
        if len(table.column_names) == len(values):
            
            fields = ",".join(table.column_names)
            values = value_string(values)
            
            statement = f"INSERT INTO {table.name}({fields}) VALUES({values})"
            return self.execute(statement)
        else:
            print("number of columns and values does not match")
            raise ValueError
            
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
            
        return rows
            
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
        """
        Creates the table on the database.
        """
        if isinstance(table, DB_TABLE):
            return self._execute(table.to_string())
        
        elif isinstance(table, str):
            if table in self.tables:
                statement = self.tables[table].to_string()
                return self._execute(statement)           
                
        return False

class DB_TABLES():
    
    def __init__(self):
        self.tables = {}
        self.selects = {}
        
    def create_table(self, table, if_not_exists=False):
        if not table in self.tables:
            self.tables[table] = DB_TABLE(table, if_not_exists)
        return self.tables[table]
    
    def select(self, name, fields = []):
        if not name in self.selects:
            self.selects[name] = None
            self.selects[name] = QUERY()
            print (self.selects)
            
        self.selects[name].fields(fields)
        return self.selects[name]
    
class DB_TABLE():
    def __init__(self, name, if_not_exists=False):
        self.name = name
        self.attributes = None
        self.columns = []
        self.column_names = []
        self.unique_columns = None
        self.primary_columns = None
        self.index_string = None
        self.foreign_constrains = []
        self.if_not_exists = if_not_exists
        
    def add_column(self, name, type, attributes = None):
        if name not in self.column_names:
            self.column_names.append(name)
            if attributes:
                self.columns.append(f"{name} {type} {attributes}")
            else:
                self.columns.append(f"{name} {type}")
            return True
        else:
            return False
        
    def primary_key(self, columns = []):
        for column in columns:
            if not column in self.column_names:
                return False
        
        # if all columns are in column names
        self.primary_columns = columns
        
    def unique(self, columns = []):
        for column in columns:
            if not column in self.column_names:
                return False
        
        # if all columns are in column names
        self.unique_columns = columns
        
    def index(self, index_field):
        if index_field in self.column_names:
            self.index_string = f"INDEX `idx_{index_field}` ({index_field})"
        
    def foreign_key(self, from_fields:list, to_table, to_fields:list, on_update="RESTRICT", on_delete="RESTRICT"):
        if from_fields and to_table and to_fields:
            fields = ",".join(from_fields)
            ref_fields = ",".join(to_fields)
            
            const_name = "_".join(to_fields)
            statement = f"CONSTRAINT `fk_{self.name}_{to_table}_{const_name}` FOREIGN KEY ({fields}) REFERENCES {to_table} ({ref_fields}) ON UPDATE {on_update} ON DELETE {on_delete}"
                       
            self.foreign_constrains.append(statement)
             
                     
    def to_string(self):
        if self.if_not_exists:
            parameter = "IF NOT EXISTS "
        else:
            parameter = ""
        
        statement = f"CREATE TABLE {parameter}{self.name} ("
        statement += ",".join(self.columns)
        
        if self.unique_columns:
            statement += ",UNIQUE(" + ",".join(self.unique_columns) + ")"
        
        if self.primary_columns:
            statement += ",PRIMARY KEY (" + ",".join(self.primary_columns) + ")"
            
        if self.index_string:
            statement += f",{self.index_string}"
            
        if self.foreign_constrains:
            for constraint in self.foreign_constrains:
                statement += "," + constraint      
        
        statement += ");"
        return statement
    
    def parameter(self, if_not_exists=False):
        self.if_not_exists = if_not_exists

class QUERY():
    def __init__(self, name):
        self.name = name
        self.statement = ""
        self.br_open = 0
        self.br_close = 0

    def SELECT (self, fields = []):
        self.statement += f'SELECT {",".join(fields)} '
        return self
    
    def FROM (self, tables = []):
        try:
            self.statement += f'FROM {",".join(tables)} '
            return self
        except:
            return None
        
    def UPDATE (self, table):
        if table:
            self.statement = f"UPDATE {table} "
            return self
        else:
            return None
        
    def INSERT_INTO(self, table):
        if table:
            self.statement = f" INSERT INTO {table} "
            return self
        else:
            return None
        
    def __expression(self, expr, a, b, operator):
        self.statement += f"{expr} {a} {operator} {b} "

    def WHERE (self, a, b, operator = "="):
        self.__expression("WHERE", a, b, operator)
        return self
    
    def AND(self, a, b, operator = "="):
        self.__expression("AND", a, b, operator)
        return self
    
    def OR(self, a, b, operator = "="):
        self.__expression("OR", a, b, operator)
        return self
    
    def JOIN(self):
        pass
    
    def GROUP_BY(self):
        pass
    
    def ORDER_BY(self):
        pass
    
    def BRACKET_OPEN(self):
        self.br_open += 1
        return self.__brackets("(")
    
    def BRACKET_CLOSE(self):
        self.br_close += 1
        return self.__brackets(")")
    
    def __brackets(self, bracket):
        self.statement += f"{bracket}"
        return self
     
    def get(self):
        if not self.br_close == self.br_open:
            raise Exception(f"unequal brackets open: {self.br_open}, closed: {self.br_close}")
        return self.statement
    
    def __str__(self):
        return self.get()



if __name__ == "__main__":
    test = DB_TABLE("test", True)
    test.add_column("a", "Varchar(255)", "not null")
    test.add_column("b", "varchar(2)")
    test.unique(["a", "b"])
    
    print(test.to_string())
    
    
    
    
    
    
    
    
        
    