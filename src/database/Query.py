
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
        
    def __expression(self, expr, a, b, operator, type):
        type = type.lower()
        if type == 'text' or type == 'date':
            self.statement += f"{expr} {a} {operator} '{b}' "
        elif type == 'int' or type == 'integer' or type == 'real':
            self.statement += f"{expr} {a} {operator} {b} "

    def WHERE (self, a, b, operator = "=", type = "text"):
        self.__expression("WHERE", a, b, operator, type)
        return self
    
    def AND(self, a, b, operator = "=", type = "text"):
        self.__expression("AND", a, b, operator, type)
        return self
    
    def OR(self, a, b, operator = "=", type = "text"):
        self.__expression("OR", a, b, operator, type)
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

    
    