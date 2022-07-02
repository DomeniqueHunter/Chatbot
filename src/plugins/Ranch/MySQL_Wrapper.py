from database.MySqlDB import DB_WRAPPER, DB_TABLES, DB_TABLE, QUERY
import time

class RANCH_DB(DB_WRAPPER):
    
    def setup(self):
        # DB        
        self.add_table("person", True)
        self.tables["person"].add_column("id", "int unsigned", "PRIMARY KEY AUTO_INCREMENT")
        self.tables["person"].add_column("name", "varchar(22)", "NOT NULL UNIQUE")
        
        self.add_table("cow", True)
        self.tables["cow"].add_column("id", "int unsigned", "PRIMARY KEY AUTO_INCREMENT")
        self.tables["cow"].add_column("person_id", "int unsigned", "NOT NULL UNIQUE")
        self.tables["cow"].add_column("active", "int", "NOT NULL DEFAULT 1")
        self.tables["cow"].add_column("yield", "int", "NOT NULL")
        self.tables["cow"].foreign_key(["person_id"], "person", ["id"])
        
        self.add_table("worker", True)
        self.tables["worker"].add_column("id", "int unsigned", "PRIMARY KEY AUTO_INCREMENT")
        self.tables["worker"].add_column("person_id", "int unsigned", "NOT NULL UNIQUE")
        self.tables["worker"].add_column("active", "int", "NOT NULL DEFAULT 1")
        self.tables["worker"].foreign_key(["person_id"], "person", ["id"])
        
        self.add_table("bull", True)
        self.tables["bull"].add_column("id", "int unsigned", "PRIMARY KEY AUTO_INCREMENT")
        self.tables["bull"].add_column("person_id", "int unsigned", "NOT NULL UNIQUE")
        self.tables["bull"].add_column("active", "int", "NOT NULL DEFAULT 1")
        
        self.add_table("breeding", True)
        self.tables["breeding"].add_column("id", "int unsigned", "PRIMARY KEY AUTO_INCREMENT")
        self.tables["breeding"].add_column("breeder_id", "int unsigned", "NOT NUNLL")
        self.tables["breeding"].add_column("prey_id", "int unsigned", "NOT NULL")
        self.tables["breeding"].add_column("amount", "int", "NOT NULL")
        self.tables["breeding"].add_column("status", "varchar(22)", "NOT NULL") # pregnant, finished
        self.tables["breeding"].add_column("children", "int unsigned", "DEFAULT 0")
        self.tables["breeding"].add_column("date", "datetime", "NOT NULL")
                
        self.add_table("milking", True)
        #self.tables["milking"].add_column("id", "bigint unsigned", "PRIMARY KEY AUTO_INCREMENT")
        self.tables["milking"].add_column("worker_id", "int unsigned", "NOT NULL")
        self.tables["milking"].add_column("cow_id", "int unsigned", "NOT NULL")
        self.tables["milking"].add_column("amount", "int unsigned", "NOT NULL")
        self.tables["milking"].add_column("date", "datetime", "NOT NULL")
        self.tables["milking"].primary_key(["worker_id", "cow_id", "date"])
        self.tables["milking"].unique(["worker_id", "cow_id", "date"])
        self.tables["milking"].foreign_key(["cow_id"], "cow", ["id"])
        self.tables["milking"].foreign_key(["worker_id"], "worker", ["id"])
        
        self.add_table("level", True)
        self.tables["level"].add_column("id", "int unsigned", "PRIMARY KEY AUTO_INCREMENT")
        self.tables["level"].add_column("person_id", "int unsigned", "NOT NULL")
        self.tables["level"].add_column("job", "varchar(22)", "NOT NULL")
        self.tables["level"].add_column("level", "int unsigned", "NOT NULL DEFAULT 0")
        self.tables["level"].add_column("experience", "int", "NOT NULL DEFAULT 0")        
        self.tables["level"].unique(["person_id", "job"])   
        
        self.create_table(self.tables["person"])
        self.create_table(self.tables["cow"])
        self.create_table(self.tables["worker"])
        self.create_table(self.tables["milking"])
        self.create_table(self.tables["level"])
    
    def rename_person(self, old_name, new_name):
        statement = f"UPDATE person SET name='{new_name}' WHERE name='{old_name}'"   
        return self.execute(statement)
    
    def enable(self, table, name):
        return self.__activate(table, name)
    
    def disable (self, table, name):
        return self.__deactivate(table, name)
            
    def __deactivate(self, table, name):
        statement = f"UPDATE {table} SET active = 0 WHERE person_id = (SELECT id from person where lower(name) = lower('{name}'))"
        status = self.execute(statement)
        if not status:
            print (f"can't deactivate {table}.name = {name}")
            
        return status
    
    def __activate(self, table, name):
        statement = f"UPDATE {table} SET active = 1 WHERE person_id = (SELECT id from person where lower(name) = lower('{name}'))"
        status = self.execute(statement)
        if not status:
            print (f"can't activate {table}.name = {name}")
            
        return status
    
    def _add_person(self, name):
        if not self.get_person(name):
            statement = f"INSERT INTO person(name) VALUES('{name}')"
            return self.execute(statement)
        
        else:
            # person already exists
            return True
    
    def get_person(self, name):
        statement = f"""
                    select name
                    from person
                    where name = '{name}'
                    """
        try:
            return self.select(statement)[0]
        except:
            return None
    
    def add_cow(self, name, amount = 10):
        status = self._add_person(name)
        
        if status:
            print("new person", name)
        else:
            print("person already exists")
        
        statement = f"INSERT INTO cow(person_id, yield) VALUES((SELECT id from person where lower(name) = lower('{name}')),{amount})"        
        return self.execute(statement) and self.set_level(name, 'cow')
        
    def update_cow_milk(self, name, milk = 10):
        statement = f"UPDATE cow set yield={milk} WHERE lower(person_id)=(SELECT id from person where lower(name) = lower('{name}'))"
        return self.execute(statement)
    

    def add_worker(self, name):
        status = self._add_person(name)
        
        if status:
            print("new worker", name)
        else:
            print("person already exists")
        
        statement = f"""INSERT INTO worker(person_id) VALUES((SELECT id FROM person WHERE lower(name) = lower('{name}')))"""
        return self.execute(statement) and self.set_level(name, 'worker')
            
    def milk_cow(self, cow, worker_name, amount, date):
        statement = f"""INSERT INTO milking(worker_id, cow_id, amount, date) VALUES(
                           (SELECT id FROM worker WHERE person_id = (SELECT id FROM person WHERE lower(name) = lower('{worker_name}'))),
                           (SELECT id FROM cow WHERE person_id = (SELECT id FROM person WHERE lower(name) = lower('{cow}'))),
                           {amount},'{date}')"""
        return self.execute(statement)
        
    def get_cow_milkings(self, cow):
        """
        @return: top 10 milkings of cow
        """  
        statement = f"""
                    select person.name, SUM(milking.amount)
                    from milking
                    inner join worker on worker.id = milking.worker_id
                    inner join person on person.id = worker.person_id
                    inner join cow on cow.id = milking.cow_id
                    and worker.active = 1
                    and cow.id = (select id from cow where person_id = (select id from person where lower(name) = lower('{cow}') ) )
                    group by worker.id                    
                    order by SUM(milking.amount) DESC
                    LIMIT 10
                    ;
                    """        
        rows = self.select(statement)
        return rows
    
    def get_last_milking(self, worker, cow):
        """
        @return: date of last milking
        """
        
        statement = f"""
                    select m.date
                    from milking m, worker w, cow c
                    where m.cow_id = c.id
                    and m.worker_id = w.id
                    and c.person_id = (select id from person where lower(name) = lower('{cow}') )
                    and w.person_id = (select id from person where lower(name) = lower('{worker}') )
                    order by m.date desc
                    limit 1
                    """
        return self.select(statement)[0]
        
    def get_worker_jobs(self, worker):
        """
        @return: top 10 milkings of worker
        """        
        statement = f"""
                    select person.name, SUM(milking.amount)
                    from milking
                    inner join cow on cow.id = milking.cow_id
                    inner join person on person.id = cow.person_id
                    inner join worker on worker.id = milking.worker_id
                    and cow.active = 1
                    and worker.id = (select id from worker where person_id = (select id from person where lower(name) = lower('{worker}') ) )
                    group by cow.id                    
                    order by SUM(milking.amount) DESC
                    LIMIT 10        
                    """
        rows = self.select(statement)
        return rows
        
    def get_cow_stats_all(self):
        rows = self.select("""
                    select person.name, SUM(milking.amount)
                    from milking
                    inner join cow on cow.id = milking.cow_id
                    inner join person on person.id = cow.person_id
                    and cow.active = 1                    
                    group by cow.id                    
                    order by SUM(milking.amount) DESC
                    ;
                    """)
        return rows
       
    def get_cow_stats_this_month(self, page= 1):
        """
        @param page: page to be seen
        @return: (name, level, exp, milk)
        
        """
        if page > 1:
            offset = (page-1) * 10
        else:
            offset = 0
        
        start = time.time()
        rows = self.select(f"""
                    select person.name, lvl.level, lvl.experience, IFNULL((SELECT SUM(amount) 
                                        FROM milking,cow 
                                        where MONTH(milking.date) = MONTH(CURRENT_DATE())
                                        AND YEAR(milking.date) = YEAR(CURRENT_DATE())
                                        AND cow.id = c.id 
                                        AND milking.cow_id = c.id 
                                        GROUP BY milking.cow_id),0) as M
                    from cow c, person, level lvl
                    where c.person_id = person.id
                    and lvl.person_id = person.id
                    and lvl.job = 'cow'
                    and c.active = 1
                    order by M DESC
                    LIMIT 10 OFFSET {offset}
                    ;
                    """)
        stop = time.time()
        #print(f"get_cows: {stop - start}s")

        return rows
        
    def get_worker_stats_all(self):
        rows = self.select("""
                    select person.name, SUM(milking.amount)
                    from milking
                    inner join worker on worker.id = milking.worker_id
                    inner join person on person.id = worker.person_id
                    and worker.active = 1
                    group by worker.id                    
                    order by SUM(milking.amount) DESC
                    ;
                    """)
        return rows
    
    def get_worker_stats_this_month(self, page= 1):
        if page > 1:
            offset = (page-1) * 10
        else:
            offset = 0
        
        start = time.time()
        rows = self.select(f"""
                    select person.name, lvl.level, lvl.experience, IFNULL((SELECT SUM(amount) 
                                        FROM milking,worker 
                                        where MONTH(milking.date) = MONTH(CURRENT_DATE())
                                        AND YEAR(milking.date) = YEAR(CURRENT_DATE())
                                        AND worker.id = w.id 
                                        AND milking.worker_id = w.id 
                                        GROUP BY milking.worker_id),0) as M
                    from worker w, person, level lvl
                    where w.person_id = person.id
                    and lvl.person_id = person.id
                    and lvl.job = 'worker'
                    and w.active = 1
                    order by M DESC
                    LIMIT 10 OFFSET {offset}
                    ;
                    """)
        stop = time.time()
        #print(f"get_workers: {stop - start}s")
        
        return rows
 
    def get_cow_stats(self, name):
        statement = f"""
                    select person.name, level.level, level.experience, SUM(milking.amount)
                    from milking, cow, person, level
                    where milking.cow_id = cow.id
                    and cow.person_id = person.id
                    and level.person_id = person.id
                    and level.job = 'cow'
                    and cow.id = (select id from cow where person_id = (select id from person where lower(name) = lower('{name}') ) )
                    group by cow.id
                    ;
                    """  
                    
        try:
            answer = self.select(statement)
            return answer
            #return self.select(statement)
        except:
            return None
    
    def get_cow(self, name, respect = True):
        if respect:
            statement = f"""
                        select person.name, cow.yield, level.level, level.experience, cow.active
                        from person, cow, level
                        where person.id = cow.person_id
                        and person.id = level.person_id
                        and lower(person.name) = lower('{name}')
                        and level.job = 'cow'
                        and cow.active = 1;
                        """
        else:
            statement = f"""
                        select person.name, cow.yield, level.level, level.experience, cow.active
                        from person, cow, level
                        where person.id = cow.person_id
                        and person.id = level.person_id
                        and lower(person.name) = lower('{name}')
                        and level.job = 'cow'
                        """
        try:
            return self.select(statement)[0]
        except:
            return None
    
    def get_all_cows(self):
        statement = """
                    select person.name
                    from person, cow
                    where person.id = cow.person_id
                    """
        return self.select(statement)
    
    def get_all_workers(self):
        statement = """
                    select person.name
                    from person, worker
                    where person.id = worker.person_id
                    """
        return self.select(statement)
    
    def get_worker(self, name):
        statement = f"""
                    select worker.id, person.name
                    from worker, person
                    where worker.person_id = (SELECT id FROM person WHERE lower(name) = lower('{name}'))
                    and worker.person_id = person.id
                    and active = 1
                    ;
                    """
        return self.select(statement)
        
    def get_breeder(self, name):
        statement = f"""
                    select breeder.id, person.name
                    from breeder, person
                    where person.id = breeder.person_id
                    and worker.person_id = (SELECT id FROM person WHERE lower(name) = lower('{name}'))
                    ;
                    """
        return self.execute(statement)

    def update_experience(self, name, level, exp, job):
        statement = f"""
                    UPDATE level
                    SET level={level}, experience={exp}
                    WHERE person_id = (SELECT id FROM person WHERE lower(name) = lower('{name}'))
                    AND job = '{job}'
                    """
        return self.execute(statement)
    
    def set_level(self, name, job):
        statement = f"""INSERT INTO level(person_id, job) 
                        VALUES ( (SELECT id FROM person WHERE lower(name)=lower('{name}') ), '{job}')
                    """
        return self.execute(statement)
    
    
    
    
    
    
    
    