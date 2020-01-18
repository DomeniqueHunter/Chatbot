
import re

class BBCode():
    
    @staticmethod
    def get_name(string):
        if string.startswith("["):
            '''
                enable BBCode for this kind of userinteraction
            '''
            pattern = "\[.+\](.+)\[\/.+\]|(.+)"
            string = re.search(pattern, string)
            string = string.group(1).strip()
        
        return string.strip()