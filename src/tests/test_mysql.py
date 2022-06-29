
import sys
sys.path.append('..')
sys.path.append('../database')


from database.MySqlDB import DB_WRAPPER, DB_TABLES, DB_TABLE, QUERY


class DB(DB_WRAPPER):
    
    def __init__(self, user, password, database, host, port=3306):
        super().__init__(user, password, database, host, port=3306)
    
    def setup(self):
        # create first table
               
        self.add_table("test", True)
        self.tables["test"].add_column("id", "int", "not null auto_increment")
        self.tables["test"].add_column("name", "varchar(255)", "not null")
        self.tables["test"].primary_key(["id"])
        self.tables["test"].unique(["name"])
        
        print(self.tables["test"].to_string())
        
        self.create_table(self.tables["test"])
        #self.create_table("test")
        
    def add_person(self, name):
        statement = f"INSERT INTO test(name) VALUES('{name}')"
        return self.execute(statement)
        
        
def main(db:DB):
    db.connect()
    db.setup()
    
def insert_person(db:DB):
    test = db.add_person("Gudrun")
    print(test)
    
    
    table_1 = DB_TABLE("test", True)
    table_1.add_column("id", "int", "not null auto_increment")
    table_1.add_column("name", "varchar(255)", "not null")
    table_1.primary_key(["id"])
    table_1.unique(["name"])
    
    db.insert(table_1, 2, "Badrun")
    db.insert(table_1, 5, "Schwelf")
    db.insert(table_1, 7, "Hannelore")
    db.insert(table_1, 9, "Berta")
    
    
    test = db.add_person("Bomann")
    print(test)
    test = db.add_person("Priemel")
    print(test)
 
def insert_more():
    test = db.add_person("AAAAA")
    print(test)
    test = db.add_person("AAAAA")
    print(test)
    test = db.add_person("BBBBB")
    print(test)
       
    
if __name__ == "__main__":
    db = DB("root", "example", "Ranch", "judy.local")
    main(db)
    
    insert_person(db)
    
    insert_more()
    
    
    
    
    
    
    
    
    
    
    