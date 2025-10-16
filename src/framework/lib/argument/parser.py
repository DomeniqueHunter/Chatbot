

__allowed_types = (str, int, float, bool)


def parse(input_string:str, *types, seperator:str=","):
    if len(types) == 0: 
        return None  # ERROR
    
    splitted = input_string.split(seperator)
    if len(splitted) < len(types):
        return None  # ERROR
    
    returning_values = []
    for value, type_ in zip(splitted, types):
        if type_ not in __allowed_types:
            returning_values.append(None)
            continue
        
        try:
            clear_value = type_(value.strip())
                    
            returning_values.append(clear_value)
        
        except ValueError:
            print(f"Could not convert '{value}' to {type_}")
        
    return tuple(returning_values)

    
def test():
    test_strings = [
        "one, 2, three",
        "1,2,3",
        "one, 2, None",
        "a,2, c, d, eee, 9" 
        ]
    
    for test_string in test_strings:
        split = parse(test_string, str, int, str)
        
        print(split)


if __name__ == "__main__":
    test()
