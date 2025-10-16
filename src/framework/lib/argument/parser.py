from typing import Union 

__allowed_types: tuple = (str, int, float, bool)

__default_values: dict = {
    str: "",
    int: 0,
    float: 0.0,
    bool: False
}


def parse(input_string:str, *types:type, separator:str=",") -> Union[tuple, None]:
    """
    Parses a string into multiple values of specified types, separated by a given separator.
    Missing values are replaced with the default value of the expected type.

    :param input_string: The string to be parsed.
    :param types: A variable number of types (e.g., str, int, float, bool).
    :param separator: The character used to separate values in the input string (default is comma).
    :return: A tuple of parsed values or None if no types were provided.
    """
    if len(types) == 0:
        return None  # No types provided

    parts = input_string.split(separator)
    parsed_values = []

    for i, type_ in enumerate(types):
        value = parts[i].strip() if i < len(parts) else None

        if type_ not in __allowed_types:
            parsed_values.append(None)
            continue

        # Handle missing values
        if value is None or value == "":
            parsed_values.append(__default_values[type_])
            continue

        try:
            # Handle boolean parsing manually
            if type_ is bool:
                normalized = value.lower()
                if normalized in ("true", "1", "yes", "y"):
                    parsed_values.append(True)
                elif normalized in ("false", "0", "no", "n"):
                    parsed_values.append(False)
                else:
                    print(f"Invalid boolean literal: '{value}'")
                    parsed_values.append(__default_values[bool])
                continue

            parsed_values.append(type_(value))

        except ValueError:
            print(f"Could not convert '{value}' to {type_.__name__} using default value")
            parsed_values.append(__default_values[type_])

    return tuple(parsed_values)

    
def test():
    test_strings = [
        "one, 2, three",
        "1,2,3",
        "one, 2, None",
        "a,2, c, d, eee, 9",
        "one, 2"
        ]
    
    for test_string in test_strings:
        split = parse(test_string, str, int, str, float)
        
        print(split)


if __name__ == "__main__":
    test()
