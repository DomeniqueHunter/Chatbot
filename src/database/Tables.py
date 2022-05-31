from database.Query import QUERY

class DB_TABLES():
    
    def __init__(self):
        self.tables = {}
        self.selects = {}
        
    def create_table(self, table):
        if not table in self.tables:
            self.tables[table] = DB_TABLE(table)
        return self.tables[table]
    
    def select(self, name, fields = []):
        if not name in self.selects:
            self.selects[name] = None
            self.selects[name] = QUERY()
            print (self.selects)
            
        self.selects[name].fields(fields)
        return self.selects[name]
    
class DB_TABLE():
    def __init__(self, name):
        self.name = name
        self.attributes = None
        self.columns = []
        self.column_names = []
        self.unique_columns = None
        
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
        
    def unique(self, columns = []):
        for column in columns:
            if not column in self.column_names:
                return False
        
        # if all columns are in column names
        self.unique_columns = columns
                     
    def to_string(self):
        statement = f"CREATE TABLE {self.name} ("
        statement += ",".join(self.columns)
        
        if self.unique_columns:
            statement += ",UNIQUE(" + ",".join(self.unique_columns) + ")"
        
        statement += ");"
        print ("XXX:", statement)
        return statement