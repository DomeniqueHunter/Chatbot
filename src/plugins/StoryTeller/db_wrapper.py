from database.Tables import DB_TABLE
from database.Wrapper import DB_WRAPPER


class StoryDBWrapper(DB_WRAPPER):
    
    def setup(self):
        t_person = DB_TABLE("person")
        t_person.add_column("id", "integer", "PRIMARY KEY")
        t_person.add_column("name", "text", "NOT NULL UNIQUE")
        t_person.add_column("nick", "text", "NOT NULL UNIQUE")
        
        # daily session
        t_session = DB_TABLE("session")
        t_session.add_column("person_id", "int", "NOT NULL")
        t_session.add_column("date", "text", "NOT NULL") # yyyy-dd
        t_session.add_column("finished", "int", "DEFAULT 0") # 1 when dead
        t_session.add_column("cum", "int", "DEFAULT 0")
        t_session.add_column("points", "int", "DEFAULT 0")
        t_person.unique(["person_id", "date"])
        
        self.create_table(t_person)
        self.create_table(t_session)
        
    def get_current_session(self, name:str, date:str) -> tuple:
        statement = f"""SELECT finished, cum, points 
                        FROM session, person
                        WHERE session.person_id = person.id
                        AND session.date='{date}'
                        AND lower(person.name) = lower('{name}') 
                    """
        self.select(statement)
        
    def get_person(self, name:str) -> tuple:
        statement = f"""SELECT nick, (SELECT SUM(cum) c, SUM(points) p, sum(finished) d
                                      FROM session
                                      WHERE person.id = session.person_id
                                      GROUP BY session.person_id) 
                    FROM person
                    WHERE lower(name) = lower('{name}')
                    """
        return self.select(statement)
    
    def rename_person(self, old_name, new_name):
        statement = f"UPDATE person SET name='{new_name}' WHERE name='{old_name}'"   
        return self.execute(statement)
    
    def set_nick_name(self, name:str, nick:str):
        statement = f"UPDATE person set nick='{nick}' WHERE name='{name}'"
        return self.execute(statement)