import re


def get_field(string: str) -> tuple:
    '''
    Extracts the field (e.g. "user") and content (e.g. "Bob") from a string formatted as [field]content[/field].
    Returns a tuple (field, content).
    '''
    pattern = r"\[([^\]]+)\](.*?)\[/\1\]"
    match = re.search(pattern, string)
    if match:
        field = match.group(1)
        content = match.group(2).strip()
        return field, content
    return "", string


def get_name(string: str) -> str:
    _, name = get_field(string)
    return name.strip()


def user(user:str) -> str:
    return f"[user]{user}[/user]"


def icon(user:str) -> str:
    return f"[icon]{user}[/icon]"

def url(string:str, text:str = "") -> str:
    '''
    Wraps the input string in BBCode-style URL tags.
    If no text is provided, the domain is used as the text.
    If text is provided, the domain is the link, and text is the visible display text.
    '''
    if text:
        return f"[url={string}]{text}[/url]"
    return f"[url]{string}[/url]"


def bold(string:str) -> str:
    return f"[b]{string}[/b]"


def italic(string: str) -> str:
    return f"[i]{string}[/i]"


def test() -> None:
    '''
    Runs basic test cases.
    '''
    test_cases_names = [
        ("[username]John Doe[/username]", "John Doe"),
        ("PlainText", "PlainText"),
        ("[user]Alice[/user]", "Alice"),
        ("[name] Bob ", "[name] Bob"),
        ("[name]  Test Name[/name] ", "Test Name"),
        ("Alice", "Alice"),
        ("Bob", "Bob"),
        ("Admin", "Admin"),
    ]
    
    for idx, (input_str, expected) in enumerate(test_cases_names, start=1):
        result = get_name(input_str) if input_str.startswith("[") else input_str
        assert result == expected, f"Test case {idx} failed: {result} != {expected}"
        print(f"Name Test case {idx} passed!")
        
        
    test_cases_url = [
        ("https://example.com", "", "[url]https://example.com[/url]"),
        ("https://example.com", "Click Here", "[url=https://example.com]Click Here[/url]"),
    ]
    
    for idx, (input_str, parameter, expected) in enumerate(test_cases_url, start=1):
        result = url(input_str, parameter)
        assert result == expected, f"Test case {idx} failed: {result} != {expected}"
        print(f"Url Test case {idx} passed!")


if __name__ == "__main__":
    test()
